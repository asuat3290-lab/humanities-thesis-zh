#!/usr/bin/env python3
"""Read-only audit for Chinese humanities theses in Markdown or plain text."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from difflib import SequenceMatcher
from pathlib import Path

STYLE_PHRASES = [
    "这意味着", "由此可见", "正是在这一意义上", "从这个意义上看", "换言之",
    "可以说", "进一步说", "需要指出的是", "真正需要把握的是", "这一点表明",
    "这也说明", "随后将", "下面将", "本章将", "本节将",
]
PROCESS_TRACES = [
    "根据你的要求", "本轮修改", "当前版本", "工作稿", "已有材料", "吸收进论文",
    "恢复引文", "本地 OCR", "据本地 OCR", "正式目录页核对", "后续人工核对",
    "待核验脚注清单",
]
STRONG_WORDS = [
    "根本性", "绝对", "必然导致", "彻底消除", "完全取代", "无可争议",
    "毫无疑问", "极为重要", "至关重要",
]
TEMPLATES = {
    "不是A而是B": re.compile(r"不是[^。！？；\n]{0,45}而是"),
    "并非A而是B": re.compile(r"并非[^。！？；\n]{0,45}而是"),
    "如果说A那么B": re.compile(r"如果说[^。！？；\n]{0,80}那么"),
}
DEFAULT_TERMS: list[tuple[str, str, list[str]]] = []


@dataclass
class Finding:
    category: str
    severity: str
    line: int
    message: str
    excerpt: str = ""


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-16", "gb18030"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            pass
    raise UnicodeError("无法识别文件编码：" + str(path))


def line_no(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def clip(value: str, size: int = 120) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    return value if len(value) <= size else value[:size - 1] + "…"


def style_body(text: str) -> str:
    match = re.search(r"^#{1,3}\s*(参考文献|References)\s*$", text, re.MULTILINE | re.IGNORECASE)
    return text[:match.start()] if match else text


def paragraphs(text: str):
    result, cursor = [], 0
    for block in re.split(r"\n\s*\n", text):
        start = text.find(block, cursor)
        cursor = start + len(block)
        value = block.strip()
        if not value or value.startswith(("#", "[^")):
            continue
        plain = re.sub(r"\s+", "", value)
        result.append({"line": line_no(text, start), "text": value, "plain": plain})
    return result


def scan_terms(text: str, terms, category: str, severity: str, prefix: str):
    counts, findings = {}, []
    for term in terms:
        matches = list(re.finditer(re.escape(term), text, re.IGNORECASE))
        counts[term] = len(matches)
        for match in matches[:8]:
            findings.append(Finding(category, severity, line_no(text, match.start()),
                                    prefix + "“" + term + "”。",
                                    clip(text[max(0, match.start() - 30):match.end() + 50])))
    return counts, findings


def language_audit(text: str):
    counts: Counter[str] = Counter()
    findings = []
    for phrase in STYLE_PHRASES:
        matches = list(re.finditer(re.escape(phrase), text))
        counts[phrase] = len(matches)
        for match in matches[:5]:
            findings.append(Finding("language", "review", line_no(text, match.start()),
                                    "检查模板化过渡是否承担真实论证功能。", phrase))
    for label, pattern in TEMPLATES.items():
        matches = list(pattern.finditer(text))
        counts[label] = len(matches)
        for match in matches[:5]:
            findings.append(Finding("language", "review", line_no(text, match.start()),
                                    "检查“" + label + "”式转折是否连续重复。", clip(match.group(0))))
    return dict(counts), findings


def repetition_audit(items):
    findings = []
    exact: dict[str, list[int]] = {}
    for item in items:
        normalized = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", item["plain"])
        if len(normalized) >= 55:
            exact.setdefault(normalized, []).append(item["line"])
    for value, lines in exact.items():
        if len(lines) > 1:
            findings.append(Finding("repetition", "review", lines[0],
                                    "相同段落出现于第 " + "、".join(map(str, lines)) + " 行。", clip(value)))
    long_items = [item for item in items if len(item["plain"]) >= 110]
    for i, left in enumerate(long_items):
        for right in long_items[i + 1:]:
            if abs(left["line"] - right["line"]) < 8:
                continue
            ratio = SequenceMatcher(None, left["plain"], right["plain"]).ratio()
            if ratio >= 0.78:
                findings.append(Finding("repetition", "review", left["line"],
                                        f"第 {left['line']} 与第 {right['line']} 行段落高度相似（{ratio:.2f}）。",
                                        clip(left["text"])))
                if len(findings) >= 30:
                    return findings
    return findings


def footnote_audit(text: str):
    refs = re.findall(r"\[\^([^\]\s]+)\](?!:)", text)
    defs = re.findall(r"^\[\^([^\]\s]+)\]:", text, re.MULTILINE)
    ref_set, def_set = set(refs), set(defs)
    numeric = sorted(int(x) for x in def_set if x.isdigit())
    gaps = sorted(set(range(numeric[0], numeric[-1] + 1)) - set(numeric)) if numeric else []
    return {
        "reference_count": len(refs),
        "definition_count": len(defs),
        "missing_definitions": sorted(ref_set - def_set),
        "unused_definitions": sorted(def_set - ref_set),
        "duplicate_definitions": sorted(x for x, count in Counter(defs).items() if count > 1),
        "numeric_definition_gaps": gaps,
        "most_reused_notes": [{"id": x, "references": count}
                              for x, count in Counter(refs).most_common(10) if count > 1],
    }


def paragraph_at(text: str, position: int):
    start = text.rfind("\n\n", 0, position)
    end = text.find("\n\n", position)
    start = 0 if start < 0 else start + 2
    end = len(text) if end < 0 else end
    return line_no(text, position), text[start:end].strip()


def terminology_audit(text: str, specs):
    chapter = re.search(r"^#{1,3}\s*第[一二三四五六七八九十百\d]+章", text, re.MULTILINE)
    offset = chapter.start() if chapter else 0
    body, results = text[offset:], []
    for label, pattern, originals in specs:
        matches = list(re.finditer(pattern, body))
        if not matches:
            continue
        first = offset + matches[0].start()
        first_line, first_para = paragraph_at(text, first)
        annotated_line, found_originals = None, []
        for match in matches[:8]:
            position = offset + match.start()
            line, para = paragraph_at(text, position)
            found = [original for original in originals if original in para]
            if found:
                annotated_line, found_originals = line, found
                break
        results.append({
            "label": label,
            "first_line": first_line,
            "annotated_line": annotated_line,
            "status": "ok" if annotated_line else "review",
            "found_originals": found_originals,
            "first_excerpt": clip(first_para),
            "note": "前八次实质出现中已括注原词。" if annotated_line else "请人工判断首次实质界定处是否需括注原词。",
        })
    return results


def run(path: Path, check_terms: bool, config: Path | None):
    text = read_text(path)
    body = style_body(text)
    paras = paragraphs(body)
    findings: list[Finding] = []

    phrase_counts, found = language_audit(body)
    findings.extend(found)
    process_counts, found = scan_terms(text, PROCESS_TRACES, "process-trace", "error", "删除加工痕迹")
    findings.extend(found)
    strong_counts, found = scan_terms(body, STRONG_WORDS, "claim-strength", "review", "核对强断言")
    findings.extend(found)
    findings.extend(repetition_audit(paras))
    for para in paras:
        count = para["text"].count("：")
        if count >= 3:
            findings.append(Finding("language", "review", para["line"],
                                    f"本段含有 {count} 个中文冒号，检查讲解式表达。", clip(para["text"])))

    notes = footnote_audit(text)
    for item in notes["missing_definitions"]:
        findings.append(Finding("footnote", "error", 0, f"脚注引用 [^{item}] 缺少定义。"))
    for item in notes["duplicate_definitions"]:
        findings.append(Finding("footnote", "error", 0, f"脚注 [^{item}] 存在重复定义。"))
    for item in notes["unused_definitions"][:20]:
        findings.append(Finding("footnote", "review", 0, f"脚注定义 [^{item}] 未被正文引用。"))

    specs = DEFAULT_TERMS
    if config:
        data = json.loads(read_text(config))
        specs = [(x["label"], x["pattern"], x["originals"]) for x in data.get("term_specs", [])]
    term_results = terminology_audit(text, specs) if check_terms and specs else []
    for item in term_results:
        if item["status"] == "review":
            findings.append(Finding("terminology", "review", item["first_line"],
                                    item["label"] + "在前八次实质出现中未检出原词括注。",
                                    item["first_excerpt"]))

    heads = [{"line": line_no(text, m.start()), "level": len(m.group(1)), "title": m.group(2)}
             for m in re.finditer(r"^(#{1,6})\s+(.+?)\s*$", text, re.MULTILINE)]
    chapters = [x for x in heads if x["level"] <= 2 and re.match(r"第.+章", x["title"])]
    sections = [x for x in heads if re.match(r"第.+节", x["title"])]
    return {
        "file": str(path.resolve()),
        "summary": {
            "chinese_characters": len(re.findall(r"[\u4e00-\u9fff]", text)),
            "paragraphs": len(paras),
            "average_paragraph_characters": round(sum(len(x["plain"]) for x in paras) / len(paras), 1) if paras else 0,
            "headings": len(heads),
            "chapters": chapters,
            "sections": sections,
        },
        "style_phrase_counts": phrase_counts,
        "process_trace_counts": {k: v for k, v in process_counts.items() if v},
        "strong_word_counts": {k: v for k, v in strong_counts.items() if v},
        "footnotes": notes,
        "term_checks": term_results,
        "findings": [asdict(x) for x in sorted(findings, key=lambda x: (x.line, x.category, x.message))],
    }


def print_report(report):
    summary = report["summary"]
    print("文件：" + report["file"])
    print(f"规模：{summary['chinese_characters']} 个汉字，{summary['paragraphs']} 个正文段，"
          f"{len(summary['chapters'])} 章，{len(summary['sections'])} 节")
    notes = report["footnotes"]
    print(f"Markdown 脚注：{notes['reference_count']} 次引用，{notes['definition_count']} 条定义")
    frequent = [f"{k}={v}" for k, v in sorted(report["style_phrase_counts"].items(),
                                                key=lambda x: (-x[1], x[0])) if v]
    if frequent:
        print("语言观察：" + "；".join(frequent[:20]))
    for item in report["term_checks"]:
        print(f"术语 {item['label']}：{item['status']}（首次 {item['first_line']}；括注 "
              f"{item['annotated_line'] or '未检出'}）")
    findings = report["findings"]
    print(f"发现：{len(findings)} 项（error={sum(x['severity'] == 'error' for x in findings)}）")
    for item in findings[:80]:
        location = f"第 {item['line']} 行" if item["line"] else "全篇"
        print(f"[{item['severity']}] {location} {item['category']}：{item['message']}")
        if item["excerpt"]:
            print("    " + item["excerpt"])
    if len(findings) > 80:
        print(f"其余 {len(findings) - 80} 项请使用 --json 查看。")


def main():
    parser = argparse.ArgumentParser(description="只读审查中文人文社科论文的结构、脚注、概念和语言风险。")
    parser.add_argument("path", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--term-config", "--config", dest="config", type=Path,
                        help="可选 JSON 术语配置；未指定时不执行领域术语检查")
    parser.add_argument("--marx-terms", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if not args.path.is_file():
        parser.error("文件不存在：" + str(args.path))
    config = args.config
    if args.marx_terms and config is None:
        config = Path(__file__).resolve().parent.parent / "profiles" / "marx-mega" / "terms.json"
    if config and not config.is_file():
        parser.error("配置文件不存在：" + str(config))
    report = run(args.path, bool(config), config)
    print(json.dumps(report, ensure_ascii=False, indent=2)) if args.json else print_report(report)
    errors = [x for x in report["findings"] if x["severity"] == "error"]
    return 2 if args.strict and errors else 0


if __name__ == "__main__":
    sys.exit(main())

