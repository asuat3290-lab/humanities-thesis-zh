---
name: humanities-thesis-zh
description: Write, revise, audit, and finalize Chinese humanities and social-science theses, especially philosophy, intellectual history, social theory, and Marxist studies. Use for 论文提纲、章节写作、局部精修、全文统稿、概念边界、论证衔接、原始文本细读、脚注与参考文献核验、中文学术语言自然化、去除 AI 写作痕迹、Markdown/DOCX 合并与交付，以及涉及 Marx/MEGA² 的文本考证。Honor requests such as “只诊断”“先给方案”“不要重写”“只处理指定章节” and preserve the thesis's established argument unless the user explicitly authorizes restructuring.
---

# 中文人文社科论文写作与统稿

## 核心原则

1. 先服从任务边界，再追求完整性。用户要求诊断、方案或局部修改时，不提前重写正文，不顺手修改其他章节。
2. 先解决论证、概念和证据，再处理语言。不得用流畅表达掩盖逻辑空缺。
3. 保留已经成立的主线、章节功能和可靠引文。除非明确授权，不以“更完整”为由另起炉灶。
4. 不编造文献、页码、卷期、DOI、出版社信息或原文。无法核验的内容删除、降格表述或标为待核验。
5. 区分历史过程、研究方法和叙述次序。不得把范畴的讲述顺序写成现实历史由概念自动生成。
6. 保留可追踪版本。编辑现有文件时另存修订版，不覆盖用户要求保留的源文件。

## 任务路由

- 用户只要诊断：说明章节功能、问题、证据缺口和风险，不改正文。
- 用户只要方案：给出保留、删除、合并、移动、补证和改写的位置，等待确认。
- 用户要求局部精修：仅在指定范围内修改，优先做小替换、段落缝合和脚注调整。
- 用户要求章节写作：先确认该章在全文中的输入、任务、输出和篇幅，再展开正文。
- 用户要求全文统稿：先冻结各章正式版本，再处理跨章重复、术语一致、首尾呼应和结论集中度。
- 用户要求 Word 交付：调用 Documents 工作流，生成真实脚注、目录和可继续编辑的 DOCX，并完成渲染核验。

## 标准工作流

### 1. 冻结约束

记录题目、核心问题、中心判断、章节范围、允许的改动级别、篇幅、引用格式、输出格式和禁用事项。将用户的明确限制视为硬约束。存在非显而易见的结构选择时先确认；其余细节自行解决。

### 2. 建立论证骨架

为全文或当前章节写出一句功能定义，并识别：

- 从上文继承的前提；
- 当前必须证明的判断；
- 支撑判断所需的文本或材料；
- 留给下文继续完成的问题。

涉及章节重组、概念边界或重复判断时，读取 [references/argument-and-concepts.md](references/argument-and-concepts.md)。

### 3. 建立概念登记表

记录核心概念的工作定义、相邻概念、首次界定位置、允许的同义表达和禁止的替换。概念第一次实质出现时解释，后续保持名称和含义连续。外国学者首次出现时采用“中文译名（原名）”；关键外语概念按学科需要标注原词，之后不反复括注。

### 4. 建立证据台账

把材料分为原始文本、二手研究和现实材料。逐项记录每条材料能够支持的具体判断，避免一个脚注笼统支撑整段综合论述。新增或调整引文时核对版本、卷册、页码和上下文。

涉及引文、脚注或参考文献时，读取 [references/evidence-and-citations.md](references/evidence-and-citations.md)。涉及马克思、MEGA² 或德文术语时，另读 [references/marx-mega-workflow.md](references/marx-mega-workflow.md)。

### 5. 按段落推进论证

让每个实质段落完成一个有限动作：提出问题、说明文本、解释概念、比较观点、限定结论或完成过渡。通常按“判断—证据—解释—与当前问题的关系”组织，但不要机械复制四段式模板。引用之后必须说明其论证作用。

### 6. 执行局部修订

优先处理概念滑移、论证跳跃、段落重复、章节越界和脚注错位。保留有用原句，通过补足中介句、调整句序、合并重复段和降低过强断言改善文本。只有原段无法修复时才整段重写。

涉及版本管理、逐章修改或全文合并时，读取 [references/revision-workflow.md](references/revision-workflow.md)。

### 7. 执行语言修整

在逻辑和引文稳定后再自然化语言。保持中文学术语体，允许为连贯性保留必要说明，不把文字压缩成跳跃的判断串。检查主语与指代、句间中介、术语连续、长短句变化、冒号密度、机械排比和模板化转折。

涉及语言润色或“去 AI 腔”时，读取 [references/language-style-zh.md](references/language-style-zh.md)。humanizer-zh 只能用于最后语言层，不能替代论证修复。

### 8. 完成质量门槛

依次通过以下检查：

1. 论证：问题是否得到推进，结论是否超出证据。
2. 概念：对象是否滑移，首次定义与后文是否一致。
3. 证据：引文是否准确，脚注是否紧跟具体判断。
4. 结构：章节是否越界，前后章是否重复或断裂。
5. 语言：是否存在讲解腔、模板句、跳跃、过强断言或加工痕迹。
6. 文档：目录、标题层级、脚注、页码、封面和换行是否正常。

可先运行：

~~~powershell
python scripts/audit_thesis_text.py thesis.md --marx-terms
python scripts/audit_thesis_docx.py thesis.docx
~~~

脚本只报告问题，不自动改文。查看 [references/document-delivery.md](references/document-delivery.md) 完成 Markdown、DOCX 与视觉核验。

## 与其他技能协作

- 用 PaperSpine 检查论文主线、章节功能和接口；不要让它越过用户授权直接重写。
- 用 academic-research-suite 核验原始文本、研究文献和引文支撑关系。
- 用 academic-reference-matcher 检查条目真实性、元数据和正文主张是否匹配。
- 用 humanizer-zh 做最后语言自然化，保持论点、引文和脚注不变。
- 用 Documents 编辑、合并和渲染 DOCX。用户禁止 LibreOffice 时不得暗中使用。

## 输出约定

- 诊断以问题和证据位置为主，先列高风险问题。
- 方案明确指出保留、合并、删除、移动、补证或重写的位置。
- 正文输出不含“根据要求”“当前版本”“工作稿”“恢复引文”等加工痕迹。
- 完成文件任务后报告文件链接、验证结果和仍待人工核验事项，不粘贴整篇正文。
- 不把用户论文正文、个人路径、未公开材料或受版权保护的大段资料打包进本 skill。