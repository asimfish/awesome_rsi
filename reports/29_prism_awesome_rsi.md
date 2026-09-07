# Prism-Shadow/awesome-rsi 深度解读：用九个维度的元数据整理 RSI 基准与方法

> **Awesome RSI: A Curated Collection of Recursive Self-Improvement Benchmarks and Methods**
> GitHub：github.com/Prism-Shadow/awesome-rsi · 网站：prism-shadow.github.io/awesome-rsi · 中英双语，2026（网站数据快照取自 2026-08-13 的 Semantic Scholar 引用数）
> 内容：27 个基准、31 个方法、1 个开源系统（Proteus）、3 本书与若干课程、1 篇长文（另见报告 30）
> 本报告依据：仓库 README、网站数据文件（`papers.js`、`methods.js`、`paperTaxonomy.js`、`methodTaxonomy.js`、`systems.js`、`resources.js`），读取时间 2026-09-08

---

## 1. 一句话定位

Prism-Shadow/awesome-rsi 是目前公开的 RSI 资源里唯一把**基准**和**方法**分开编目、并给每条都打上多维度元数据的清单：27 个基准按来源、模式、进化对象、构造标准、指标、创建方式、评分方式七个维度标注，31 个方法按进化对象、模式、拓扑、验收标准、更新者、反馈来源、反馈类型、更新频率、经验范围九个维度标注。网站把同一批数据做成筛选面板、按日期或引用数排序的列表、引用图和"书籍与课程"页。它与本仓库的重叠只有 12 篇方法论文；它收录了 19 篇本仓库没有的方法（以记忆和技能类为主，如 SEAL、ReasoningBank、A-MEM、SkillSmith、Mendel Gödel Machine、Recuris、TRACE），本仓库有 48 篇它没有收录的论文（评估器共进化、harness 工业化、安全治理和思想史几乎全部）。两个仓库对 RSI 的组织方式不同：它按"改了什么、何时改、谁改、凭什么留下"给每篇论文贴标签，本仓库按"进化循环外的固定评估依据在哪"排一条主线。它的"验收标准"维度是两者最接近的地方。

## 2. 这个资源要解决的问题

RSI 领域没有统一的技术范式：有的工作改模型参数，有的改上下文、记忆、技能，有的改工具和 harness 代码；评测方式也各不相同，有的用固定基准，有的用任务流，有的只看单题结果。读者面对一篇新论文，很难快速判断它和已有工作的关系。

已有的 awesome 列表（包括本仓库 §4.3 的三份综述配套清单）大多是按主题分节的链接列表，条目没有结构化标签，无法按"只看在线模式、改技能、用可执行验证器验收的方法"这类条件筛选。Prism-Shadow 的做法是把每条论文的分类判断写成数据文件，再由网站渲染成可筛选的视图。

它同时把**基准**单独列为一类。RSI 方法论文通常在自己选的任务上报告提升，而"怎样测量自改进是否真的发生"是另一个问题：需要任务流、需要区分训练与测试、需要有对照组。截至 2026 年 9 月，该清单收录了 27 个专门为此设计的基准，本仓库在这一块基本空白（只有 METR 的任务时长测量）。

## 3. 与已有资源的关系

| 资源 | 组织方式 | 规模 | 与 Prism-Shadow 的差别 |
|---|---|---|---|
| Prism-Shadow/awesome-rsi | 基准 + 方法两张表，每条带多维标签，网站可筛选 | 27 基准 + 31 方法 + 1 系统 | — |
| 本仓库 asimfish/awesome_rsi | 按"锚在哪"排主线，13 个小节，每篇有深度解读和中译 | 61 篇论文 + 6 篇经典 + 29 份解读 | 重叠 12 篇方法；本仓库没有基准表，它没有评估器共进化、安全治理、思想史 |
| iSEngLab/Awesome-Self-Evolving-Coding-Agents | 按进化对象六类，限编码域 | 综述配套 | 只有编码域；无基准表、无元数据 |
| CharlesQ9/Self-Evolving-Agents | TMLR 综述配套 | 上百篇 | 按 What/When/How/Where 分节，无筛选 |
| Lil'Log Harness Engineering 博文 | 叙述式综述 | 约 30 篇引用 | 有观点无编目 |

Prism-Shadow 的增量是**元数据**：它把综述里的分类维度变成每条论文上的标签，让分类可以被检索和统计。代价是只做标签不做解读——每条只有一句"是什么、为什么重要"。

## 4. 内容与机制拆解

### 4.1 方法表的九个维度（methodTaxonomy.js）

| 维度 | 取值 | 与本仓库概念的对应 |
|---|---|---|
| artifact（进化对象） | Parametric；Non-parametric 下分 Harness code / Context / Memory / Skill | 本仓库的"改哪层"（权重 / 源码 / 文本），它把文本层再拆成上下文、记忆、技能三类 |
| mode（模式） | Online / Offline / Offline → Online | 本仓库的重置式 / 免重置之分近似但不相同；它按"更新发生在最终评测之前还是之中"划分 |
| topology（拓扑） | Sequential / Tree / Graph | 本仓库没有单列此维度；DGM 是 Tree，Metan 的档案是 Tree，Mendel GM 是 Graph |
| selection（验收标准） | Artifact validation / Instance result / Benchmark score / Combined metrics / No validation | **最接近本仓库的"锚"**：它记录留下更新的证据是什么；"No validation"对应本仓库说的无锚 |
| updater（更新者） | Self / Teacher / Joint | 本仓库的 Self-Harness（Self）与 Meta-Harness（Teacher）之分 |
| source（反馈来源） | Benchmark / Train-dev set / Environment / Executable verifier / LLM feedback / Human | 本仓库的锚形态：人工标注集（Human）、冻结验证器（Executable verifier）、dev 集（Train/dev set） |
| feedback（反馈类型） | Score（Binary / Non-binary）/ Non-score（Ground truth / LLM-as-a-judge / Other） | 本仓库未单列 |
| frequency（更新频率） | Step / Event / Trajectory / Batch | 本仓库的"快环 / 慢环"近似 |
| scope（经验范围） | General / Specialized | 本仓库未单列 |

维度设计有几处值得注意的规则：多个取值用"或"，多个维度用"与"；Offline → Online 只给"先离线建立再在线更新"的单一流水线，同时有离线和在线变体的方法给两个标签；反馈类型只记录用于更新学生的反馈，只用于进化教师的反馈不计；LLM 给出的标量算分数，只有文字判断才算 LLM-as-a-judge。

### 4.2 基准表的七个维度（paperTaxonomy.js）

| 维度 | 取值 |
|---|---|
| origin（来源） | Composite（由已有基准拼装）/ Original（自建任务） |
| mode（模式） | Online 下分 Random order / Curriculum / Streaming / Repeated-iterative；Offline；Offline → Online |
| artifact（进化对象） | Parametric / Non-parametric（Skill / Memory / Harness code）/ Other |
| construction（构造标准） | Headroom（留有提升空间）/ Diversity / Generalization / Other |
| metric（指标） | Accuracy / Gain（提升量）/ Cost / Latency |
| creation（创建方式） | Fully automated / Human-in-the-loop / Manual |
| evaluation（评分方式） | Rule-based / LLM-as-a-judge |

其中 **Gain** 作为独立指标值得单独说：一个 RSI 基准应该报告的是"更新前后的差"而不只是最终准确率，否则测的是模型能力而不是自改进能力。FinEvo-Bench（见报告 30）用状态重置的对照组算这个差，是这一维度的典型实现。

### 4.3 收录内容

**31 个方法**（按首版日期）：Cradle 2024-03、AWM 2024-09、Gödel Agent 2024-10、A-MEM 2025-02、DGM 2025-05、SEAL 2025-06、Memp 2025-08、ReasoningBank 2025-09、Meta-Harness 2026-03、Mem²Evolve 2026-04、HeLa-Mem 2026-04、Escher-Loop 2026-04、AHE 2026-04、Continual Harness 2026-05、DemoEvolve 2026-05、SkillSmith 2026-05、SePO 2026-06、HarnessFix 2026-06、Self-Harness 2026-06、HarnessX 2026-06、When Rules Learn 2026-06、RQGM 2026-06、HarnessBank 2026-07、RHI 2026-07、Mendel Gödel Machine 2026-08、Evo-Harness 2026-08、HyperSkill 2026-08、TRACE 2026-08、MediSkill-Evo 2026-08、Prime Agent 2026-08、Recuris 2026-08。

与本仓库的重叠 12 篇：DemoEvolve、Gödel Agent、DGM、Meta-Harness、AHE、Continual Harness、HarnessFix、Self-Harness、RQGM、Evo-Harness、HyperSkill、Prime Agent。

它有本仓库没有的 19 篇，可以分三组：
- 记忆类：AWM、A-MEM、Cradle、ReasoningBank、Mem²Evolve、HeLa-Mem、Memp、Recuris——本仓库把记忆归入知识侧，只收了 WikiSkill 和五篇技能进化论文，没有单独追记忆进化这条线。
- 参数类：SEAL（模型自己生成训练数据和超参的 self-edit，用 RL 学什么样的 self-edit 有效）——本仓库权重侧只有 ECHO、Co-Harness、SkillRL、Evolving-RL、SIA。
- harness 与技能类：HarnessX、HarnessBank、RHI、Escher-Loop、SkillSmith、SePO、Mendel Gödel Machine、TRACE、MediSkill-Evo、When Rules Learn。其中 Mendel Gödel Machine 是 DGM 的直接后续（用跨任务、跨分支的轨迹对照决定怎么改，Polyglot 50.8% → 93.2%，单轨迹树形基线 77.9%），本仓库的框架侧应该补上。

本仓库有它没有的 48 篇，集中在四块：评估器共进化（EvoLM、WGtG、ECHO、EvalCEGAR、RHO、SCORE）、harness 工业化的另一半（AutoSaddler、EnvHarness、MetaCaster、Co-Harness、Metan、HSI、Adaptive Auto-Harness、Harness Updating≠Benefit）、安全治理（SESG、OLE、Falsifiable Gates、HVTB、ASG-SI、ARA）、思想史与程序进化谱系（Good 到 Bostrom、STOP、ADAS、AFlow、AlphaEvolve、GEPA、ShinkaEvolve）。MOSS 和 WikiSkill 也不在它的表里。

**27 个基准**（2025-05 至 2026-09）：LifelongAgentBench、MemoryAgentBench、StuLife、MemoryBench、Evo-Memory、PostTrainBench、Agent² RL-Bench、SkillFlow、SkillLearnBench、EvoMemBench、Curation-Bench、Meta-Agent Challenge、AutoLab、CL-Bench、EdgeBench、EvoAgentBench、RSIBench-Data、AgentStream、PATH-Bench、ContinualSkillBench、PAST-Bench、GDPevo、HarnessOpt-Bench、FinEvo-Bench、Evo-Bench、HarnessDev、VeRO。其中 2026 年 8 月一个月发布了 9 个。这些基准回答的是本仓库报告 10 insight 10（测量基础设施是瓶颈）提出的问题，但本仓库一篇都没收。

**1 个开源系统**：Proteus v0.3.0（2026-08-24），与具体 harness 解耦的自进化框架，每个 episode 用新的模型上下文，agent 只能修改预先声明的 harness 区域，代码改动通过验证后才启用，版本化快照保留历史。标签：Non-parametric（Harness code / Context / Memory / Skill）、Offline、Sequential、验收为 Artifact validation + Instance result。

**书与课程**：李博杰《AI Agents in Depth》（开源技术书）、Lanham《AI Agents in Action, 2nd ed.》、Alesso《AI Builds Itself: Recursive Self-Improvement in 2026》，以及几门课程。

### 4.4 网站功能

同一份数据渲染成四个视图：基准列表（多维筛选面板，可按日期或引用数排序）、引用图、方法与系统列表、书籍与课程页。中英文切换和明暗主题由本地存储记住。贡献指南要求新条目必须带全部维度的标签，否则不能进入筛选视图。

## 5. 与本仓库对照的几个具体差别

**对同一篇论文的分类可以互相校验。** 以 Continual Harness 为例，本仓库的判断是"文本四组件 + 权重共学习，免重置，锚为冻结 PRM 和教师模型"；Prism-Shadow 的标签应为 Parametric + Non-parametric、Online、Sequential、更新者 Joint、反馈来源 Environment + LLM feedback。两套标签描述的是同一件事的不同侧面：本仓库回答"什么部件不参与进化"，它回答"参与进化的部件是哪些、按什么节奏改"。

**"验收标准"维度里的 No validation 是本仓库最关心的一格。** 本仓库的结论是去掉锚以后评估器会偏离而任务分数看不出来（报告 05、16）；Prism-Shadow 把"生成后直接写入、不设验收"作为一个正常取值列出，没有给出这类方法的风险判断。两边合起来读，可以把该清单里标为 No validation 的方法作为检验"无锚是否退化"的候选样本。

**基准表填补了本仓库的空白，但基准本身也需要被审视。** 27 个基准里以 LLM-as-a-judge 评分的那部分，会遇到本仓库报告 03、05 讨论的问题：评估器可以被优化压力带偏。Prism-Shadow 的 evaluation 维度区分了 Rule-based 和 LLM-as-a-judge，这已经是必要的第一步，但没有进一步标注 judge 是否冻结、是否有人工锚定样本。

**引用数排序的局限。** 数据快照取自 2026-08-13 的 Semantic Scholar，收录的多数论文发表不到三个月，引用数接近零，按引用排序在当前阶段没有区分度。

## 6. 局限

1. **只有标签，没有解读。** 每条一句话，读者无法从清单本身判断一篇论文的证据强度、消融是否充分、局限在哪。这是它与本仓库的根本分工。
2. **标签是人工判断，无出处。** 数据文件里的分类没有标注依据论文的哪一节，读者无法核对；本仓库解读中的数字则要求标注到表号。
3. **方法覆盖偏向记忆与技能，缺评估器一侧。** 31 个方法里没有任何一篇以评估器共进化为主题，而这是 2026 年 RSI 研究里增长最快的方向之一。
4. **基准表未评估基准质量。** 收录标准是"专门为 RSI 设计"，没有区分哪些基准有状态重置对照组、哪些只报告最终准确率。
5. **网站是 JS 单页应用，数据不易被机器读取。** 论文列表存在 `site/src/data/*.js` 里，不是 CSV 或 JSON，二次使用需要自己解析。
6. **收录截止约 2026-09-01**（HarnessDev），更新频率未知。

## 7. 意义与位置

**对本仓库的直接补充**：三件事可以照着做——(1) 增加基准一节，至少收录 GDPevo、FinEvo-Bench、SkillFlow、VeRO、HarnessOpt-Bench 这几个与本仓库主题直接相关的；(2) 框架侧补 Mendel Gödel Machine，知识侧补 ReasoningBank 和 SEAL；(3) 在 §7.3 对照矩阵里为每个系统加"验收标准"和"更新者"两列，与它的元数据对齐，方便两个仓库互相引用。

**对报告 10 insight 10 的实证**：本仓库说测量基础设施是下一个瓶颈，Prism-Shadow 的基准表显示 2026 年 8 月一个月出了 9 个 RSI 基准，说明这个判断已经被社区行动验证，但这些基准彼此的任务流设计、对照组设置和评分方式尚无统一标准。

**对报告 12、22、28 三份综述的补充**：三份综述都给了分类框架但没有把框架应用到每篇论文上；Prism-Shadow 做了这一步。它的九个维度与 TMLR 综述的 What / When / How 高度对应，多出的 selection、updater、frequency、scope 四个维度正是 TMLR 缺少的操作层面。

**与报告 30（Prism-Shadow 长文）的关系**：长文是对这套元数据的叙述式解释，每个维度配一篇代表论文；本报告看数据，报告 30 看论述。
