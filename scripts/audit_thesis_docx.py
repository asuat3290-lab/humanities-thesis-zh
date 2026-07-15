#!/usr/bin/env python3
"""Read-only structural audit for DOCX thesis files using OOXML."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
PROCESS_TRACES = [
    "根据你的要求", "本轮修改", "当前版本", "工作稿", "已有材料", "吸收进论文",
    "恢复引文", "本地 OCR", "据本地 OCR", "正式目录页核对", "后续人工核对",
    "待核验脚注清单",
]
LEFTOVER_PATTERNS = {
    "Markdown 脚注引用": re.compile(r"\[\^[^\]]+\]"),
    "Markdown 标题": re.compile(r"(?m)^#{1,6}\s+"),
    "未完成标记": re.compile(r"\b(?:TODO|FIXME)\b", re.IGNORECASE),
    "目录占位语": re.compile(r"目录将在\s*Microsoft Word\s*中自动更新", re.IGNORECASE),
    "Codex 内部引用": re.compile(r"turn\d+(?:search|fetch|view)\d+", re.IGNORECASE),
}


@dataclass
class Finding:
    category: str
    severity: str
    paragraph: int
    message: str
    excerpt: str = ""


def qname(local: str) -> str:
    return "{" + W + "}" + local


def clip(value: str, size: int = 130) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    return value if len(value) <= size else value[:size - 1] + "…"


def xml_from_zip(archive: zipfile.ZipFile, name: str):
    try:
        return ET.fromstring(archive.read(name))
    except KeyError:
        return None


def styles_map(root):
    result = {}
    if root is None:
        return result
    for style in root.findall("w:style", NS):
        style_id = style.get(qname("styleId"), "")
        name_node = style.find("w:name", NS)
        name = name_node.get(qname("val"), "") if name_node is not None else ""
        result[style_id] = name
    return result


def paragraph_text(paragraph) -> str:
    parts = []
    for node in paragraph.iter():
        if node.tag == qname("t"):
            parts.append(node.text or "")
        elif node.tag == qname("tab"):
            parts.append("\t")
        elif node.tag == qname("br"):
            parts.append("\n")
    return "".join(parts)


def paragraph_style(paragraph) -> str:
    node = paragraph.find("w:pPr/w:pStyle", NS)
    return node.get(qname("val"), "") if node is not None else ""


def document_paragraphs(root, style_names):
    result = []
    if root is None:
        return result
    for index, paragraph in enumerate(root.findall(".//w:body/w:p", NS), start=1):
        style_id = paragraph_style(paragraph)
        result.append({
            "index": index,
            "text": paragraph_text(paragraph),
            "style_id": style_id,
            "style_name": style_names.get(style_id, style_id),
        })
    return result


def footnote_data(document_root, footnotes_root):
    refs = []
    if document_root is not None:
        for node in document_root.findall(".//w:footnoteReference", NS):
            value = node.get(qname("id"))
            if value is not None:
                refs.append(value)
    definitions = {}
    if footnotes_root is not None:
        for note in footnotes_root.findall("w:footnote", NS):
            note_id = note.get(qname("id"))
            if note_id in (None, "-1", "0"):
                continue
            definitions[note_id] = "".join(paragraph_text(p) for p in note.findall(".//w:p", NS)).strip()
    return {
        "reference_count": len(refs),
        "definition_count": len(definitions),
        "missing_definitions": sorted(set(refs) - set(definitions)),
        "unused_definitions": sorted(set(definitions) - set(refs)),
        "reused_ids": [{"id": item, "references": count}
                       for item, count in Counter(refs).items() if count > 1],
    }


def toc_data(root, paragraphs):
    instructions = []
    if root is not None:
        for node in root.findall(".//w:instrText", NS):
            if node.text and "TOC" in node.text.upper():
                instructions.append(node.text.strip())
        for node in root.findall(".//w:fldSimple", NS):
            value = node.get(qname("instr"), "")
            if "TOC" in value.upper():
                instructions.append(value.strip())
    entries = [
        p for p in paragraphs
        if p["style_id"].upper().startswith("TOC") or p["style_name"].upper().startswith("TOC")
        or p["style_name"].startswith("目录")
    ]
    return {
        "field_present": bool(instructions),
        "field_instructions": instructions,
        "entry_count": len(entries),
        "entry_preview": [clip(p["text"]) for p in entries[:20] if p["text"].strip()],
    }


def run(path: Path):
    findings: list[Finding] = []
    with zipfile.ZipFile(path) as archive:
        document_root = xml_from_zip(archive, "word/document.xml")
        if document_root is None:
            raise ValueError("DOCX 缺少 word/document.xml")
        styles_root = xml_from_zip(archive, "word/styles.xml")
        footnotes_root = xml_from_zip(archive, "word/footnotes.xml")
        style_names = styles_map(styles_root)
        paras = document_paragraphs(document_root, style_names)
        footnotes = footnote_data(document_root, footnotes_root)
        toc = toc_data(document_root, paras)

        section_count = len(document_root.findall(".//w:sectPr", NS))
        page_breaks = len(document_root.findall(".//w:br[@w:type='page']", NS))
        headings = [
            p for p in paras
            if p["style_id"].lower().startswith("heading")
            or p["style_name"].lower().startswith("heading")
            or p["style_name"].startswith("标题")
        ]

        full_text = "\n".join(p["text"] for p in paras)
        for phrase in PROCESS_TRACES:
            for p in paras:
                if phrase.lower() in p["text"].lower():
                    findings.append(Finding("process-trace", "error", p["index"],
                                            "删除加工痕迹“" + phrase + "”。", clip(p["text"])))
        for label, pattern in LEFTOVER_PATTERNS.items():
            for p in paras:
                if pattern.search(p["text"]):
                    findings.append(Finding("leftover", "error", p["index"],
                                            "清理 " + label + "。", clip(p["text"])))

        for item in footnotes["missing_definitions"]:
            findings.append(Finding("footnote", "error", 0, "脚注引用 " + item + " 缺少定义。"))
        for item in footnotes["unused_definitions"][:20]:
            findings.append(Finding("footnote", "review", 0, "脚注定义 " + item + " 未被正文引用。"))

        required = ["摘要", "Abstract", "目录", "绪论", "结论", "参考文献"]
        required_sections = {}
        for label in required:
            matches = [p["index"] for p in paras if label.lower() in p["text"].strip().lower()]
            required_sections[label] = matches[:10]
            if not matches:
                findings.append(Finding("structure", "review", 0, "未检出章节标识：“" + label + "”。"))

        cover_preview = [clip(p["text"]) for p in paras[:40] if p["text"].strip()][:15]
        title_break_risk = []
        for i, p in enumerate(paras[:50]):
            text = p["text"].strip()
            if text.endswith(("《资", "《资本", "《资本论》时")):
                title_break_risk.append(p["index"])
                findings.append(Finding("layout", "review", p["index"],
                                        "封面题名可能在书名内部断行，请渲染核对。", clip(text)))

        if toc["field_present"] and not toc["entry_count"]:
            findings.append(Finding("toc", "review", 0, "检测到目录域但未检出目录条目，需在 Word 中更新目录并渲染核对。"))
        if not toc["field_present"]:
            findings.append(Finding("toc", "review", 0, "未检出 Word 自动目录域。"))

        heading_counts = Counter(p["style_name"] or p["style_id"] or "(none)" for p in headings)
        package_parts = sorted(archive.namelist())

    return {
        "file": str(path.resolve()),
        "package": {"part_count": len(package_parts), "has_footnotes_xml": "word/footnotes.xml" in package_parts},
        "summary": {
            "paragraphs": len(paras),
            "nonempty_paragraphs": sum(bool(p["text"].strip()) for p in paras),
            "sections": section_count,
            "page_breaks": page_breaks,
            "headings": len(headings),
            "heading_styles": dict(heading_counts),
        },
        "cover_preview": cover_preview,
        "required_sections": required_sections,
        "toc": toc,
        "footnotes": footnotes,
        "findings": [asdict(item) for item in sorted(findings, key=lambda x: (x.paragraph, x.category, x.message))],
    }


def print_report(report):
    summary = report["summary"]
    print("文件：" + report["file"])
    print(f"结构：{summary['paragraphs']} 段，{summary['sections']} 个节属性，"
          f"{summary['headings']} 个标题段，{summary['page_breaks']} 个显式分页")
    toc = report["toc"]
    print(f"目录：域={'有' if toc['field_present'] else '无'}，条目={toc['entry_count']}")
    notes = report["footnotes"]
    print(f"Word 脚注：{notes['reference_count']} 次引用，{notes['definition_count']} 条定义")
    print("封面预览：" + " | ".join(report["cover_preview"][:8]))
    findings = report["findings"]
    print(f"发现：{len(findings)} 项（error={sum(x['severity'] == 'error' for x in findings)}）")
    for item in findings[:80]:
        location = f"第 {item['paragraph']} 段" if item["paragraph"] else "全篇"
        print(f"[{item['severity']}] {location} {item['category']}：{item['message']}")
        if item["excerpt"]:
            print("    " + item["excerpt"])


def main():
    parser = argparse.ArgumentParser(description="只读检查 DOCX 学位论文的结构、目录、脚注和加工痕迹。")
    parser.add_argument("path", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.path.is_file():
        parser.error("文件不存在：" + str(args.path))
    try:
        report = run(args.path)
    except (zipfile.BadZipFile, ET.ParseError, ValueError) as error:
        print("无法审查：" + str(error), file=sys.stderr)
        return 3
    print(json.dumps(report, ensure_ascii=False, indent=2)) if args.json else print_report(report)
    errors = [item for item in report["findings"] if item["severity"] == "error"]
    return 2 if args.strict and errors else 0


if __name__ == "__main__":
    sys.exit(main())

