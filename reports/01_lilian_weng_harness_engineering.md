# Lilian Weng《Harness Engineering for Self-Improvement》深度解读：一旦 harness 成为可执行搜索空间，强编码 agent 就能用人类工程师的同一设计空间优化它

> **Harness Engineering for Self-Improvement**
> lilianweng.github.io/posts/2026-07-04-harness/（2026-07-04，约 31 分钟阅读量级长文）· Lilian Weng（Thinking Machines 联创，前 OpenAI 安全副总裁，Lil'Log 博主）
> 性质：领域综述 + 个人判断——把 2023–2026 年 auto-research、自改进 agent、进化式程序搜索三条线统一组织到"harness 工程 → RSI"这一问题之下
> 归档：`assets/fulltext/` 无 PDF（网页长文）；本仓库的**总纲**：其余全部材料都能在这篇的分类框架里找到坐标

---

## 1. 一句话定位

RSI 的近期现实路径不是模型直接改写自己的权重，而是**改进围绕模型的 harness**——即编排执行、决定模型如何思考规划、调用工具、感知与管理上下文、存储工件、评估结果的那一层系统；一旦 harness 设计成为**可执行的搜索空间**（代码），强编码 agent 就能利用与人类工程师相同的设计空间来优化它，这构成"模型改进部署系统→部署系统产出更强后继模型"的反馈环。

## 2. 要解决的问题：RSI 的近期现实路径在哪一层

- RSI 概念谱系：I. J. Good (1965) 的"超智能机器"（能设计更好的机器来改进自己）→ Yudkowsky (2008) 的"递归自改进"（AI 用当前智能改进产生其智能的认知机器）。
- 现代版本的两种形态：模型直接改权重（远期）；模型改进**训练管线与部署系统**，从而产出更强后继模型（近期，前沿实验室已在发生——文中直接引用 Anthropic 与 OpenAI 的加速证据）。
- **Harness 定义**（原文）：围绕基础模型的系统，编排执行，决定模型如何思考与规划、如何调用工具与行动、如何感知与管理上下文、存储工件、评估结果。Claude Code / Codex 等编码 agent 产品的成功证明这一层与模型原始智能同等重要。
- 划界：self-play、合成数据、test-time training、持续学习也属 RSI 愿景，但不在本文范围。

## 3. 为什么此前做不通：从 agent 四件套到 harness 工程

早期"agent = LLM + 记忆 + 工具 + 规划"的框架缺了四样——工作流设计（loop engineering）、评估、权限控制、持久状态管理——这四样正是 2026 年 harness 工程的主体。以下三模式 + 一案例是 Weng 归纳的现状。

### 3.1 Harness 设计模式（三模式 + 一案例）

相比早期"agent = LLM + 记忆 + 工具 + 规划"，harness 工程额外包含**工作流设计（loop engineering）、评估、权限控制、持久状态管理**——已经不是 prompt 模板，而是运行时与软件系统设计。Weng 给出 OS 类比：harness 应像操作系统一样封装复杂逻辑、保持接口简单；配置、工具接口等协议会逐步全行业标准化。

**模式 1 · 工作流自动化**：目标导向循环（计划→执行→观察/测试→改进→再执行，直到达标），可主动向用户请求澄清。Karpathy 的 autoresearch 仓库是干净范例；Codex agent loop 是产品化范例。关键在于模型分析**自己的轨迹与失败案例**并通过"agent 运行时"迭代，而非静态 prompt 模板。

**模式 2 · 文件系统作为持久记忆**：长时程 agent 的工件（实验日志、代码 diff、论文摘要、错误痕迹、历史轨迹）远超上下文窗口；harness 不应把一切塞进 context，而应把持久状态放进文件。读写文件（bash）是 LLM 的基础能力，因此文件式记忆天然随核心模型能力提升而受益——这是把记忆问题外包给"模型能力增长"的杠杆设计。

**模式 3 · 子 agent 与后台任务**：并行搜索多假设、并发跑实验、隔离子任务防止污染主上下文；父 agent 需要小型进程管理器（启动任务、查日志、取消失败运行、合并结果）。关键设计：**并行必须显式且可检视**——子 agent 输出若只活在瞬态聊天上下文里会迅速失效，存成文件/日志/状态记录才能在中断后恢复、对自己的执行历史推理。

**案例 · 编码 agent harness**：主流编码 agent（Claude Code、Codex、OpenCode、Cursor 系）的核心接口已趋同——文件系统工具（glob/grep/read/edit/apply_patch）、shell、git、MCP/Skills、web 搜索、后台进程（cron）、agent 委托（spawn/resume/wait/interrupt）。

**Harness 层 vs 核心智能**：Weng 的预测——(1) harness 工程走向元方法论（改进"获得更好答案的机器"而非答案本身），harness 系统自身成为优化目标，启发式规则减少、通用机制增多；(2) 成熟 harness 使能 auto-research 闭环，更聪明的模型反过来防止 harness 过度工程化。最终许多 harness 改进会被**内化**进模型行为，但与外部上下文和工具的接口会保留——类比 prompt 工程：手工技巧随指令微调而边缘化，但"指定目标、约束、上下文、评估"的需求从未消失。

## 4. 方法机制：Harness 优化的递进线

Weng 给出核心递进线：**指令 prompt → 结构化上下文 → 工作流 → harness 代码 → 优化器代码**——模型越强，优化对象越复杂、方法越通用。

### 4.1 上下文工程
- **ACE**（Agentic Context Engineering，Zhang et al. 2025）：把上下文当作演化中的 playbook 而非越写越长的 prompt。三组件：Generator 产轨迹、Reflector 从成败轨迹蒸馏洞见、Curator 增量更新条目化上下文。防塌缩关键：Curator 不重写整段 prompt，只输出（标识符，描述）结构化条目，用确定性逻辑合并、周期性去重——避免迭代重写导致的 context collapse 与简洁偏置。局限：更新规则与工作流仍是手工设计。
- **MCE**（Meta Context Engineering，Ye et al. 2026）：把**机制**（怎么管上下文）与**内容**（上下文里有什么）分离，双层优化——内层给定 skill 优化上下文，外层在 skill 空间搜索最优机制；skill 数据库记录历史（skill、上下文函数、训练/验证分数），元级 agent 对既往 skill 做 agentic crossover 产生新 skill。上下文函数落地为专用目录中的文件集合（静态 skill.md + 动态 rollout），全部在带标准工具集（Read/Write/Edit/Bash/Glob/Grep/TodoWrite）的 agentic 编码环境中执行。
- **Meta-Harness**（Lee et al. 2026）：再深一层——优化对象是"决定信息如何存储、检索、呈现给模型"的**代码**；提案者本身是编码 agent，输出 Pareto 前沿上的 harness 候选集合。执行历史全部可经文件系统访问（grep/cat 按需读，不塞满 prompt）；每个候选 harness 是文件系统里含源码、分数、轨迹、状态更新的字典。TerminalBench-2 实验从 Terminus-KIRA/Terminus-2 两个很强的人工 harness 初始化仍能继续提升。Weng 的总结："一旦 harness 设计成为可执行搜索空间，强编码 agent 就能利用人类工程师使用的同一设计空间。"

### 4.2 工作流设计
- 手工设计路线：AI Scientist（Lu et al. 2026，Nature——提想法/写代码/跑实验/分析/写稿/同行评审全管线）；ScientistOne（Meng et al. 2026，以可验证性为中心约束：每条声明——引用/数值/方法/结论——必须回溯到证据源并过 Chain-of-Evidence 审计）；Autodata（Kulikov et al. 2026，challenger/弱 solver/强 solver/verifier 四角色合成"恰好难度"的数据——强 solver 能解而弱 solver 不能；Weng 点出局限：合成任务只微调弱 solver 不动强 solver，更像对生成 prompt 分布的间接蒸馏，RSI 味道不足）。
- 搜索路线：ADAS（Hu et al. 2025，meta-agent 用代码编程新 agent 工作流，档案累积，两步自精炼查新颖性）；AFlow（Zhang et al. 2025，工作流表示为图——节点是 LLM 调用、边是代码逻辑——MCTS 搜索，QA/代码/数学上超过手工工作流与 ADAS）。

### 4.3 自改进 Harness（本文核心节）
- 立论：上下文工程或工作流设计都只是 harness 的一部分；**代码是定义程序与系统的通用语言**——harness 就是编排 prompt、工具调用、子 agent、控制流、记忆、工作流逻辑的代码；LLM 能优化执行 agent 的代码，就能访问远大于手写 prompt 的设计空间。
- **STOP**（Zelikman et al. 2023）：递归脚手架改进的早期范例。种子改进器 I 接（效用函数 u，解 s，黑箱模型 M）返回改进解；目标不是改进 s 而是**改进改进器本身**——用元效用（改进器在下游任务集上的平均效用）递归更新 I。发现的策略包括遗传算法、分解改进、多臂 prompt bandit、模拟退火、束/树搜索。**警示性结果**：GPT-4 上跨迭代改善、GPT-3.5/Mixtral 上退化——递归结构本身不够，基础模型必须足够强才能改进机制；harness 改进使模型部署更好，但智能仍是核心。
- **Lin et al. 2026（能力解耦）**：拆开两个轴——harness-updating（产出有用 harness 编辑的能力）与 harness-benefit（利用更新后 harness 的能力）。惊人发现：从 Qwen3.5-9B 到 Claude Opus 4.6，**更新能力几乎持平**（9B 写出的 skill 与 Opus 程序同构）；受益能力非单调，**中档模型受益最大**。要用好 harness，模型需要正确及时地调用 skill/工具、擅长长时程指令遵循。
- **Self-Harness**（Zhang et al. 2026）：propose-evaluate-accept 循环——弱点挖掘（把失败聚类成 verifier 锚定的失败模式；同一表面错误可能有不同因果机制，需含 verifier 级原因+因果状态+抽象机制的富失败记录）；有界 harness 提案（提案上下文含可编辑面、失败模式、需保留的通过行为、既往编辑摘要；偏好可由窄改动解决的复发模式；候选需彼此互异）；提案验证（held-in 测弱点是否解决 + held-out 测是否引入新问题，**双侧零回归才接受**）。三个模型在 Terminal-Bench-2 上学到各自弱点定制的 harness 指令。Weng 的安全担忧：允许程序编辑 OS 系统就打破了抽象边界——可编辑面要精心设计，**权限控制与安全层必须住在循环之外**。
- **AHE**（Agentic Harness Engineering，Lin et al. 2026）：把瓶颈定位在**可观测性**——rollout 失败时必须知道哪个组件负责，每次编辑必须证据接地。三支柱：组件可观测（harness 拆成 7 组件——系统提示/工具描述/工具实现/中间件/skill/子 agent 配置/长期记忆——每个失败模式映射到一个组件）；经验可观测（Agent debugger 逐轨迹写根因报告，聚合成基准总览，分层访问省 token）；决策可观测（Evolve agent 的每次编辑配下一轮可证伪的预测，且**runs 目录/tracer/verifier/LLM 配置只读**——物理禁掉关 verifier、换模型、加推理预算这类 reward hacking，保证每笔收益可归因到 harness 编辑）。Terminal-Bench-2 上超过 OpenCode/Terminus-2/Codex（Hard 档除外）；冻结后的 harness 零样本迁移到 SWE-bench-verified 仍有效——进化的是工程经验而非基准特定优化。

### 4.4 进化搜索
- 适用条件：搜索空间巨大或形状怪异 + 梯度难做但解易评估——harness 搜索恰好匹配。
- 谱系：Promptbreeder（mutation prompt 也被进化）→ GEPA（反思式进化）→ **AlphaEvolve**（Novikov et al. 2025：候选程序池 + 冻结 LLM 生成 diff；EVOLVE-BLOCK 标注可改区域；meta-prompt 与解程序共同进化；消融证明进化过程/上下文/元提示/全文件进化/强 LLM 各有贡献）→ ThetaEvolve（进化+RL+ICL）、DemoEvolve（人类示范增广档案）、ShinkaEvolve（三件套提升采样效率：父代采样平衡性能排名与子代数、嵌入相似度的代码新颖性拒绝采样、meta-scratchpad 记录成功模式）。
- **DGM**（Zhang et al. 2025）：与上述"解改进"不同，显式针对**可编辑 harness 代码仓库**的进化——agent 被允许修改自己的 harness；后续 Hyperagents（Zhang et al. 2026）加 meta-agent 控制如何修改任务 agent。Weng 强调：DGM 是**固定模型下的 harness 进化**，SWE-bench 20%→50%、Polyglot 14.2%→30.7%。
- 适用边界判断（重要）：这族方法在**候选解可自动评估、适应度易量化**的域有效（矩阵乘法、GPU kernel、算法竞赛、数据中心调度），在评估慢、模糊、启发式为主的域挣扎；算力效率也是现实约束。

### 4.5 与模型权重的联合优化
- SIA（Hebbar et al. 2026）：Meta-Agent 提 harness、任务 agent 执行、Feedback-Agent 决定本轮改 harness 还是改权重。Weng 的评价直接：实验混淆严重（任务 agent 用 gpt-oss-120b 而 Meta/Feedback 用 Claude Sonnet 4.6，基线太弱），"方向有趣、证据临时"（provisional）。训练稳定性与 Goodhart 效应开放。
- Continual Harness（Karten et al. 2026）：长时程游戏设定，harness 更新 + 用强教师在低奖励轨迹上蒸馏标签共学 policy。

## 5. 实验证据与七条挑战（每条都是后续论文的题眼）

先给了一个冷静的实证参照——Trehan & Chopra (2026)：最小脚手架下测试 LLM 从想法到论文，三领域 45-50 篇种子文档，只有 4 个想法过人类专家筛选、**只有 1 个完整执行成论文**。六个复发失败模式：训练数据默认偏置（旧库/陈旧命令/未接地假设）、执行压力下的实现漂移（复杂时滑向常见简单方案）、记忆与上下文退化、过度乐观（噪声里宣布胜利，即 Bubeck et al. 的"p-hacking and eureka-ing"、"numerical duct tape"）、领域智能不足（判断实现复杂度/结果合理性/哪些基线重要的隐性手艺）、科学品味弱（实验可执行但没回答对的问题）。

1. **弱而模糊的评估器**：多数研究声明没有快速精确 verifier；自改进循环只在可测量客观指标的任务上好用（同 RL）；研究品味、新颖性、长期科学价值难测。
2. **上下文与记忆生命周期**：记忆随自治性增长；Weng 的判断——上下文工程将且应当成为**智能的核心部分**而非停留在软件层（类比人类终身记忆维护）。
3. **负结果**：文献偏向成功案例，LLM 可能不擅长放弃假设、报告负结果、承认失败；研究 harness 应让失败尝试易于保存——从失败学习是修剪搜索空间的最好方式。
4. **多样性塌缩**：进化与 RL 循环倾向利用已知高奖励模式；开放式研究里最好的路径初期在当前评估器下可能更差。
5. **Reward hacking**：奖励来自单测就过拟合单测、来自 judge 就学 judge 特定把戏、来自基准就利用基准伪影；**评估器与权限控制应住在进化循环之外**，配 held-out 测试、轨迹审计、关键决策点人类评审——监督能自动化到什么程度是开放问题。
6. **长期成功**：优化目标多为短期（完成手头任务），沙箱 RLVR 很难捕捉可维护性、所有权边界、迁移成本、向后兼容、未来调试负担。
7. **人类角色**：人类应**沿栈上移而非被移出循环**——在正确的时间、正确的抽象层级提供监督；"我们是在为人类更好的未来造技术，不是反过来。"

附录给出 6 个基准速查：PaperBench（复现 20 篇 ICML 2024 论文，8316 条 rubric，当时最佳 Claude 3.5 Sonnet 约 21% 不敌 ML PhD）、CORE-Bench、ScienceAgentBench、RE-Bench（AI 在 2 小时预算 4 倍于人类、8/32 小时被人类反超）、MLE-bench、KernelBench。

## 6. 局限与批判性评价

**框架价值**：这是目前唯一把 auto-research / 自改进 agent / 进化搜索三条文献统一到单一优化对象递进线（prompt→上下文→工作流→harness 代码→优化器代码）上的综述，"harness 是可执行搜索空间"一句话给了整个领域操作性定义。七条挑战清单在 2026 下半年被逐条回应（见趋势调研）：弱评估器→EvalCEGAR/SCORE，负结果→SkillProx 的删除一等公民，多样性塌缩→Metan 进化档案，reward hacking→BenchJack/HVTB，人类角色→Falsifiable Release Gates。

**判断的可检验性**：Weng 的三个预测——harness 改进最终内化进模型、评估器必须在循环外、中档模型从 harness 受益最大（引 Lin et al.）——都是可证伪命题；其中"评估器在循环外"与六篇论文的评估器共进化方向存在**建设性张力**：六篇证明评估器不动会成为瓶颈，Weng 强调评估器乱动会被 hack，两者的合题正是"锚定纪律"（锚在循环外、metric 在循环内进化）。

**盲区**：全文以编码/研究域为中心，对多模态、具身、物理实验域的 harness 几乎未触及；对经济学约束（算力-认知劳动替代弹性）只字未提——这两块恰是 Anthropic 文章与 2026 下半年宏观争论的主战场。"52× 加速"这类内部数据引用自实验室自述，缺第三方口径（METR 试点后来补上了这一角）。

## 7. 意义与位置

- 六篇论文全部可放进她的分类：DGM/MOSS→3.3-3.4 节（自改 harness+进化搜索）、EvoLM/ECHO→3.5 节（联合权重优化）、RQGM/WGtG→挑战 1+5（评估器与 reward hacking）、WikiSkill→模式 2+3.1 节（文件记忆+上下文工程）。
- Anthropic 文章是她"前沿实验室加速"一句引用的展开版；她的挑战 7（人类沿栈上移）与 Anthropic 的"方向与批准权留在人手"完全同构。
- 阅读顺序建议：先读本文建立坐标系，再读六篇看坐标系里每个格子的最新进展，最后读趋势调研看格子之间的连线。

**七条挑战在本仓库的回应表**（2026 年 7 月后）：

| Weng 的挑战 | 回应工作 | 报告 |
|---|---|---|
| 1 弱评估器 | EvalCEGAR 碰撞对驱动评估器进化；RHO 完全无锚 | 24, 25 |
| 2 上下文与记忆生命周期 | WikiSkill 三层；技能红海五篇的生命周期管理 | 09, 26 |
| 3 负结果 | SkillProx 删除一等公民；WikiSkill 被拒提案存 wiki | 26, 09 |
| 4 多样性塌缩 | Metan 进化档案 archive-best vs best chain；DGM 踏脚石 | 20, 07 |
| 5 Reward hacking | HVTB 蜜罐测量；Prime Agent RCON 事故；AHE 只读 verifier | 27, 18 |
| 6 长期成功 | AutoSaddler durable updates（回归率减半）；Falsifiable Gates 常驻不变量 | 16, 27 |
| 7 人类角色 | iCoder 五层 prior 边界；Gates"收紧自动/放松人审" | 19, 27 |

**Weng 预言的 meta-harness 层**在 Meta-Harness（报告 13）被正式论文化——连名字都一样；她提的"更聪明的模型反过来防止 harness 过度工程化"在 Prime Agent（报告 18）"模型没被训练来操作 harness"的观察里得到反向印证：当前是 harness 等模型，不是模型等 harness。

**Weng 的"评估器在循环外"与评估侧四篇的合题**：六篇证明评估器不动会成为瓶颈（ECHO 冻结 critic 低于裸 GRPO），Weng 强调评估器乱动会被 hack——两者的合题正是 WGtG 的"锚定纪律"：锚在循环外、metric 在循环内进化。这条线是本仓库的主轴。
