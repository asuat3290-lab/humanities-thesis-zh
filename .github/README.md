# humanities-thesis-zh

[中文](#中文) | [English](#english)

## 中文

### 简介

`humanities-thesis-zh` 是面向中文人文社会科学论文的 Codex skill，适用于哲学、思想史、社会理论和马克思主义研究等领域。它将论文写作与修订拆分为论证、概念、证据、结构、语言和文档交付六个相互衔接的层面，尤其适合逐章打磨、全文统稿、原始文本细读、脚注核验以及中文学术表达自然化。

该 skill 不以自动扩写或表面润色替代理论判断。它优先服从用户限定的修改范围，保留已经成立的论证主线，并要求所有新增引文和文献能够得到核验。

### 核心能力

- 明确全文主线、章节功能及相邻章节的论证接口。
- 识别概念滑移、首次界定缺失、对象泛化和术语不一致。
- 区分原始文本、二手研究与现实材料，检查判断与证据的对应关系。
- 支持马克思文本、MEGA² 卷册页码、德文术语和版本关系的审慎处理。
- 处理局部精修、章节写作、跨章去重、全文合并和结论收束。
- 在逻辑与引文稳定后清理模板化转折、讲解腔、机械排比和其他 AI 写作痕迹。
- 配合 Documents 工作流生成并检查 Markdown、DOCX、目录和真实 Word 脚注。

### 工作原则

1. 用户要求“只诊断”“先给方案”或“不要重写”时，不提前改写正文。
2. 先修复论证、概念和证据，再处理语言自然化。
3. 不编造原文、页码、卷期、DOI、出版社信息或现实材料。
4. 不把研究顺序或叙述顺序写成现实历史由概念自动生成。
5. 概念首次实质界定时可括注原词；外国学者首次出现时可括注原名，后文保持连续使用。
6. 审查脚本只报告风险，不自动改写论文。

### 安装

在 Codex 中向 `$skill-installer` 提交以下请求：

```text
请使用 $skill-installer 从 https://github.com/asuat3290-lab/humanities-thesis-zh 安装 humanities-thesis-zh skill。
```

安装完成后，在下一轮任务中调用：

```text
请使用 $humanities-thesis-zh 审查这一章的论证、概念、引文和语言，但不要直接重写正文。
```

### 审查脚本

```powershell
python scripts/audit_thesis_text.py thesis.md --marx-terms
python scripts/audit_thesis_docx.py thesis.docx
```

`audit_thesis_text.py` 检查 Markdown 或纯文本中的章节结构、Markdown 脚注、重复段落、模板句、加工痕迹及关键概念原词括注。`audit_thesis_docx.py` 直接读取 OOXML，检查 Word 目录、标题样式、真实脚注和残留标记。两者均只读运行。

### 文件结构

```text
SKILL.md
agents/openai.yaml
references/
  argument-and-concepts.md
  document-delivery.md
  evidence-and-citations.md
  language-style-zh.md
  marx-mega-workflow.md
  revision-workflow.md
scripts/
  audit_thesis_text.py
  audit_thesis_docx.py
```

### 隐私与学术诚信

仓库不包含任何论文正文、个人路径或未公开材料。使用过程中不得把无法核验的文献伪装为可靠来源，也不得利用语言润色掩盖论证缺口。涉及未公开论文、私人语料库或受版权保护的资料时，应遵守用户授权范围和相关使用规范。

## English

### Overview

`humanities-thesis-zh` is a Codex skill for writing, revising, auditing, and finalizing Chinese humanities and social-science theses, especially in philosophy, intellectual history, social theory, and Marxist studies. It treats argument, concepts, evidence, structure, language, and document delivery as connected but distinct layers of academic work.

The skill is designed for chapter-by-chapter revision, full-manuscript integration, close reading of primary texts, footnote verification, and natural Chinese academic prose. It does not use automatic expansion or stylistic polishing as a substitute for theoretical judgment.

### Core Capabilities

- Define the thesis spine, chapter functions, and interfaces between adjacent chapters.
- Detect conceptual drift, missing first definitions, overextended objects of analysis, and inconsistent terminology.
- Separate primary texts, secondary scholarship, and empirical materials while checking claim-evidence alignment.
- Support cautious work with Marx, MEGA² volume and page references, German terminology, and textual versions.
- Revise locally, draft chapters, remove cross-chapter repetition, merge manuscripts, and tighten conclusions.
- Remove formulaic transitions, lecture-like phrasing, mechanical parallelism, and other signs of AI-generated prose only after the logic and citations are stable.
- Coordinate with a document workflow for Markdown, DOCX, tables of contents, and genuine Word footnotes.

### Operating Principles

1. Honor scope constraints such as “diagnose only,” “plan first,” and “do not rewrite.”
2. Repair argument, concepts, and evidence before naturalizing the language.
3. Never invent quotations, pages, issues, DOIs, publishers, or empirical evidence.
4. Do not present the order of exposition as if concepts automatically generated historical reality.
5. Add original terms and foreign names at their first substantive definition when academically useful, then use them consistently.
6. Audit scripts report risks and never rewrite the manuscript automatically.

### Installation

Ask `$skill-installer` in Codex to install the repository:

```text
Use $skill-installer to install the humanities-thesis-zh skill from https://github.com/asuat3290-lab/humanities-thesis-zh.
```

Invoke it in a later turn with a request such as:

```text
Use $humanities-thesis-zh to audit this chapter's argument, concepts, citations, and language without rewriting it yet.
```

### Audit Scripts

```powershell
python scripts/audit_thesis_text.py thesis.md --marx-terms
python scripts/audit_thesis_docx.py thesis.docx
```

`audit_thesis_text.py` checks Markdown or plain text for heading structure, footnotes, repeated passages, formulaic phrasing, editing traces, and original-language annotations of key concepts. `audit_thesis_docx.py` reads OOXML directly to inspect Word tables of contents, heading styles, genuine footnotes, and leftover markers. Both scripts are read-only.

### Privacy and Academic Integrity

This repository contains no thesis manuscript, personal path, or unpublished research material. Unverified references must not be presented as established sources, and language polishing must never conceal gaps in reasoning. Private corpora, unpublished manuscripts, and copyrighted materials should only be used within the user's authorization and applicable legal or institutional rules.
