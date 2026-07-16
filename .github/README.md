# humanities-thesis-zh

[中文](#中文) | [English](#english)

## 中文

### 简介

`humanities-thesis-zh` 是面向中文人文社会科学论文的 Codex skill，适用于哲学、思想史、政治理论、社会学、文学、教育、法学及相关领域。它将论文写作与修订拆分为论证、概念、证据、结构、语言和文档交付六个相互衔接的层面，尤其适合逐章打磨、全文统稿、原始文本细读、脚注核验以及中文学术表达自然化。

该 skill 不以自动扩写或表面润色替代理论判断。它优先服从用户限定的修改范围，保留已经成立的论证主线，并要求所有新增引文和文献能够得到核验。

### 核心能力

- 明确全文主线、章节功能及相邻章节的论证接口。
- 识别概念滑移、首次界定缺失、对象泛化和术语不一致。
- 区分原始文本、二手研究与现实材料，检查判断与证据的对应关系。
- 支持原始文本版本、外语术语、译本差异和思想史语境的审慎处理。
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
python scripts/audit_thesis_text.py thesis.md
python scripts/audit_thesis_docx.py thesis.docx
```

`audit_thesis_text.py` 检查 Markdown 或纯文本中的章节结构、Markdown 脚注、重复段落、模板句、加工痕迹及关键概念原词括注。`audit_thesis_docx.py` 直接读取 OOXML，检查 Word 目录、标题样式、真实脚注和残留标记。两者均只读运行。

### 可选领域配置

默认工作流不加载任何特定思想家或理论传统。`profiles/marx-mega/` 是可选领域示例，仅在任务明确涉及马克思或 MEGA² 时使用：

```powershell
python scripts/audit_thesis_text.py thesis.md --term-config profiles/marx-mega/terms.json
```

其他研究领域可以用同一配置格式维护自己的术语表，而不改变通用核心。

### 文件结构

```text
SKILL.md
agents/openai.yaml
references/
  argument-and-concepts.md
  document-delivery.md
  evidence-and-citations.md
  language-style-zh.md
  revision-workflow.md
profiles/
  marx-mega/
    workflow.md
    terms.json
scripts/
  audit_thesis_text.py
  audit_thesis_docx.py
```

### 隐私与学术诚信

仓库不包含任何论文正文、个人路径或未公开材料。使用过程中不得把无法核验的文献伪装为可靠来源，也不得利用语言润色掩盖论证缺口。涉及未公开论文、私人语料库或受版权保护的资料时，应遵守用户授权范围和相关使用规范。

## English

### Overview

`humanities-thesis-zh` is a Codex skill for writing, revising, auditing, and finalizing Chinese humanities and social-science theses across philosophy, intellectual history, political theory, sociology, literature, education, law, and related fields. It treats argument, concepts, evidence, structure, language, and document delivery as connected but distinct layers of academic work.

The skill is designed for chapter-by-chapter revision, full-manuscript integration, close reading of primary texts, footnote verification, and natural Chinese academic prose. It does not use automatic expansion or stylistic polishing as a substitute for theoretical judgment.

### Core Capabilities

- Define the thesis spine, chapter functions, and interfaces between adjacent chapters.
- Detect conceptual drift, missing first definitions, overextended objects of analysis, and inconsistent terminology.
- Separate primary texts, secondary scholarship, and empirical materials while checking claim-evidence alignment.
- Support cautious work with primary-text versions, foreign-language terminology, translation differences, and intellectual-historical contexts.
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
python scripts/audit_thesis_text.py thesis.md
python scripts/audit_thesis_docx.py thesis.docx
```

`audit_thesis_text.py` checks Markdown or plain text for heading structure, footnotes, repeated passages, formulaic phrasing, editing traces, and original-language annotations of key concepts. `audit_thesis_docx.py` reads OOXML directly to inspect Word tables of contents, heading styles, genuine footnotes, and leftover markers. Both scripts are read-only.

### Optional Domain Profiles

The default workflow does not load rules for any particular thinker or theoretical tradition. `profiles/marx-mega/` is an optional example and should only be used when the task explicitly concerns Marx or MEGA²:

```powershell
python scripts/audit_thesis_text.py thesis.md --term-config profiles/marx-mega/terms.json
```

Other fields can supply their own terminology configuration without changing the generic core.

### Privacy and Academic Integrity

This repository contains no thesis manuscript, personal path, or unpublished research material. Unverified references must not be presented as established sources, and language polishing must never conceal gaps in reasoning. Private corpora, unpublished manuscripts, and copyrighted materials should only be used within the user's authorization and applicable legal or institutional rules.
