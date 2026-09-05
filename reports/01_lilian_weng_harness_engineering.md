# Lilian Weng《Harness Engineering for Self-Improvement》深度解读：编码 agent 可以搜索和优化 harness 代码

> **Harness Engineering for Self-Improvement**
> lilianweng.github.io/posts/2026-07-04-harness/（2026-07-04，约 31 分钟阅读量级长文）· Lilian Weng（Thinking Machines 联创，前 OpenAI 安全副总裁，Lil'Log 博主）
> 性质：领域综述 + 个人判断。把 2023–2026 年 auto-research、自改进 agent、进化式程序搜索三条线统一组织到"harness 工程 → RSI"这一问题之下
> 归档：`assets/fulltext/` 无 PDF（网页长文）；本仓库的**总纲**：其余全部材料都能在这篇的分类框架里找到坐标

---

## 1. 一句话定位

RSI 在近期可行的路径是改进围绕模型的 harness，直接改写模型权重仍是更远期的目标。这层系统负责编排执行，决定模型如何思考和规划、调用工具、感知与管理上下文、存储工件、评估结果。harness 用代码定义设计空间，能力足够强的编码 agent 就能在与人类工程师相同的空间中搜索和优化。由此可以形成"模型改进部署系统→部署系统产出更强后继模型"的反馈环。

## 2. 要解决的问题：RSI 的近期现实路径在哪一层

- RSI 概念谱系：I. J. Good (1965) 的"超智能机器"（能设计更好的机器来改进自己）→ Yudkowsky (2008) 的"递归自改进"（AI 用当前智能改进产生其智能的认知机器）。
- 现代版本有两种形态：模型直接修改权重是远期目标；近期则通过改进训练管线与部署系统，产出更强的后继模型。前沿实验室已在采用后一种方式，文中引用了 Anthropic 与 OpenAI 的加速证据。
- **Harness 定义**（原文）：围绕基础模型的系统，编排执行，决定模型如何思考与规划、如何调用工具与行动、如何感知与管理上下文、存储工件、评估结果。Claude Code / Codex 等编码 agent 产品的成功证明这一层与模型原始智能同等重要。
- 划界：self-play、合成数据、test-time training、持续学习也属 RSI 愿景，但不在本文范围。

## 3. 为什么此前做不通：从 agent 四件套到 harness 工程

早期"agent = LLM + 记忆 + 工具 + 规划"的框架未涵盖工作流设计（loop engineering）、评估、权限控制和持久状态管理。这四项构成了 2026 年 harness 工程的主要内容。Weng 将现有做法归纳为以下三种模式，并介绍了一个案例。

### 3.1 Harness 设计模式（三模式 + 一案例）

相比早期"agent = LLM + 记忆 + 工具 + 规划"，harness 工程还包含工作流设计（loop engineering）、评估、权限控制和持久状态管理。它从 prompt 模板扩展到了运行时与软件系统设计。Weng 用 OS 作类比：harness 应像操作系统一样封装复杂逻辑、保持接口简单。她预计，配置和工具接口等协议会逐步形成行业标准。

**模式 1 · 工作流自动化**：围绕目标循环执行（计划→执行→观察/测试→改进→再执行，直到达标），也可主动向用户请求澄清。Karpathy 的 autoresearch 仓库展示了这种做法，Codex agent loop 则将其用于产品。模型分析自己的轨迹与失败案例，通过"agent 运行时"迭代，超出了静态 prompt 模板能处理的范围。

**模式 2 · 文件系统作为持久记忆**：长时程 agent 产生的工件（实验日志、代码 diff、论文摘要、错误痕迹、历史轨迹）远超上下文窗口。harness 可将持久状态写入文件，按需读取，减少 context 的负担。读写文件（bash）是 LLM 的基础能力；模型能力提高后，也能更好地使用文件中保存的记忆。

**模式 3 · 子 agent 与后台任务**：并行搜索多个假设、并发运行实验，并隔离子任务，避免干扰主上下文。父 agent 需要小型进程管理器来启动任务、查看日志、取消失败运行和合并结果。并行任务的状态必须明确且可检查。子 agent 的输出若只保存在临时聊天上下文里，很快就会失效；写入文件、日志或状态记录后，系统才能在中断后恢复，并分析自身的执行历史。

**案例 · 编码 agent harness**：主流编码 agent（Claude Code、Codex、OpenCode、Cursor 系）的核心接口已趋同，包括文件系统工具（glob/grep/read/edit/apply_patch）、shell、git、MCP/Skills、web 搜索、后台进程（cron）和 agent 委托（spawn/resume/wait/interrupt）。

**Harness 层 vs 核心智能**：Weng 提出两个预测。(1) harness 工程会逐渐优化产生答案的机制，harness 系统自身成为优化目标，减少启发式规则，增加通用机制。(2) 成熟的 harness 能支持 auto-research 循环，能力更强的模型也会减少 harness 中不必要的复杂设计。最终，模型会学会许多原本依靠 harness 实现的行为，但仍需要与外部上下文和工具连接。prompt 工程有类似的变化：指令微调减少了对手工技巧的依赖，指定目标、约束、上下文和评估标准的需求仍然存在。

## 4. 方法机制：Harness 优化的递进线

Weng 按优化对象排列这些方法：**指令 prompt → 结构化上下文 → 工作流 → harness 代码 → 优化器代码**。随着模型能力增强，它能优化更复杂的对象，也能采用更通用的方法。

### 4.1 上下文工程
- **ACE**（Agentic Context Engineering，Zhang et al. 2025）：把上下文组织成持续更新的 playbook，避免 prompt 不断增长。系统分为三个组件：Generator 生成轨迹，Reflector 从成败轨迹中提取经验，Curator 按条目增量更新上下文。Curator 只输出（标识符，描述）结构化条目，不重写整段 prompt。系统用确定性逻辑合并条目并定期去重，避免反复重写造成 context collapse 与简洁偏置。更新规则与工作流仍由人工设计。
- **MCE**（Meta Context Engineering，Ye et al. 2026）：分别优化管理上下文的机制和上下文中的内容。内层按给定 skill 优化上下文，外层在 skill 空间中搜索最优机制。skill 数据库记录历史 skill、上下文函数以及训练/验证分数；元级 agent 对已有 skill 执行 agentic crossover，产生新 skill。上下文函数通过专用目录中的文件集合实现（静态 skill.md + 动态 rollout）。这些操作全部在配有标准工具集（Read/Write/Edit/Bash/Glob/Grep/TodoWrite）的 agentic 编码环境中执行。
- **Meta-Harness**（Lee et al. 2026）：优化决定信息如何存储、检索和呈现给模型的代码。提案者本身是编码 agent，输出 Pareto 前沿上的 harness 候选集合。执行历史全部可通过文件系统访问，使用 grep/cat 按需读取，减少 prompt 占用。每个候选 harness 在文件系统中表示为一个字典，包含源码、分数、轨迹和状态更新。TerminalBench-2 实验以 Terminus-KIRA/Terminus-2 两个表现较强的人工 harness 初始化后，仍能继续提升。Weng 据此认为，harness 设计用代码表达后，能力足够强的编码 agent 就能在与人类工程师相同的空间中搜索。

### 4.2 工作流设计
- 手工设计路线：AI Scientist（Lu et al. 2026，Nature）覆盖提出想法、写代码、跑实验、分析、写稿和同行评审的完整流程。ScientistOne（Meng et al. 2026）要求引用、数值、方法和结论中的每条声明都能追溯到证据源，并通过 Chain-of-Evidence 审计。Autodata（Kulikov et al. 2026）用 challenger、弱 solver、强 solver、verifier 四个角色合成数据，要求强 solver 能解而弱 solver 不能。Weng 指出，合成任务只用于微调弱 solver，强 solver 保持不变。这更接近对生成 prompt 分布的间接蒸馏，还不足以支持 RSI 的判断。
- 搜索路线：ADAS（Hu et al. 2025）的 meta-agent 用代码编写新的 agent 工作流，持续积累档案，并通过两步自精炼检查新颖性。AFlow（Zhang et al. 2025）把工作流表示为图，以 LLM 调用为节点、代码逻辑为边，再用 MCTS 搜索。在 QA/代码/数学任务上，它超过了手工工作流与 ADAS。

### 4.3 自改进 Harness（本文核心节）
- 上下文工程和工作流设计都属于 harness 的一部分。代码可以通用地定义程序与系统；harness 就是编排 prompt、工具调用、子 agent、控制流、记忆和工作流逻辑的代码。LLM 若能优化执行 agent 的代码，就能搜索比手写 prompt 广得多的设计空间。
- **STOP**（Zelikman et al. 2023）：早期尝试递归改进脚手架。种子改进器 I 接收效用函数 u、解 s 和黑箱模型 M，返回改进后的解。优化目标是改进器本身，通过元效用（改进器在下游任务集上的平均效用）递归更新 I，使其更有能力改进 s。系统发现的策略包括遗传算法、分解改进、多臂 prompt bandit、模拟退火和束/树搜索。实验中，GPT-4 随迭代改善，GPT-3.5/Mixtral 则退化。递归结构能否改进机制，仍取决于基础模型是否有足够能力；harness 改进可以改善部署效果，无法替代模型能力。
- **Lin et al. 2026（能力解耦）**：分别测量 harness-updating（产出有用 harness 编辑的能力）与 harness-benefit（利用更新后 harness 的能力）。从 Qwen3.5-9B 到 Claude Opus 4.6，更新能力几乎持平，9B 写出的 skill 与 Opus 程序同构。受益能力不随模型规模单调变化，中档模型受益最大。模型要用好 harness，需要及时、正确地调用 skill/工具，并在长时程任务中持续遵循指令。
- **Self-Harness**（Zhang et al. 2026）：采用 propose-evaluate-accept 循环。首先把失败聚类为经 verifier 确认的失败模式。同一种表面错误可能由不同机制导致，因此记录需包含 verifier 级原因、因果状态和抽象机制。随后提出限定修改范围的 harness 候选；提案上下文包含可编辑部分、失败模式、需要保留的通过行为及既往编辑摘要，优先处理能用小范围改动解决的反复失败，并要求候选彼此不同。最后用 held-in 检查弱点是否解决，用 held-out 检查是否引入新问题；两侧都没有回归才接受。三个模型在 Terminal-Bench-2 上学到了针对各自弱点的 harness 指令。Weng 担心，允许程序编辑 OS 系统会打破抽象边界。因此，需要明确可编辑范围，将权限控制与安全层放在循环之外。
- **AHE**（Agentic Harness Engineering，Lin et al. 2026）：要求 rollout 失败后能定位负责的组件，每次编辑都有证据支持。它从三个方面提供可观测性：将 harness 拆成 7 个组件（系统提示/工具描述/工具实现/中间件/skill/子 agent 配置/长期记忆），把每个失败模式对应到一个组件；由 Agent debugger 逐条轨迹撰写根因报告，再汇总为基准总览，分层访问以节省 token；要求 Evolve agent 为每次编辑提出下一轮可证伪的预测。runs 目录/tracer/verifier/LLM 配置只读，禁止关闭 verifier、更换模型或增加推理预算等 reward hacking 行为，确保收益能归因于 harness 编辑。Terminal-Bench-2 上，它超过 OpenCode/Terminus-2/Codex（Hard 档除外）。冻结后的 harness 零样本迁移到 SWE-bench-verified 仍有效，说明学到的工程经验可以用于其他基准。

### 4.4 进化搜索
- 适用条件：搜索空间很大或不规则，梯度难以计算，但候选解容易评估。harness 搜索符合这些条件。
- 相关方法：Promptbreeder 同时进化 mutation prompt；GEPA 采用反思式进化；**AlphaEvolve**（Novikov et al. 2025）维护候选程序池，用冻结的 LLM 生成 diff，并用 EVOLVE-BLOCK 标注可修改区域。它让 meta-prompt 与解程序共同进化，消融表明进化过程、上下文、元提示、全文件进化和强 LLM 各有贡献。后续的 ThetaEvolve 结合进化+RL+ICL，DemoEvolve 用人类示范扩充档案。ShinkaEvolve 通过三项设计提高采样效率：父代采样兼顾性能排名与子代数，按嵌入相似度对代码进行新颖性拒绝采样，用 meta-scratchpad 记录成功模式。
- **DGM**（Zhang et al. 2025）：将可编辑的 harness 代码仓库作为进化对象，允许 agent 修改自己的 harness。后续 Hyperagents（Zhang et al. 2026）增加了 meta-agent，控制如何修改任务 agent。Weng 强调，DGM 在固定模型的条件下进化 harness，结果为 SWE-bench 20%→50%、Polyglot 14.2%→30.7%。
- 适用范围：这类方法适用于候选解可自动评估、适应度易量化的领域，包括矩阵乘法、GPU kernel、算法竞赛和数据中心调度。在评估缓慢、标准模糊或主要依赖启发式判断的领域，方法效果受限；算力效率也会限制应用。

### 4.5 与模型权重的联合优化
- SIA（Hebbar et al. 2026）：Meta-Agent 提出 harness，任务 agent 执行，Feedback-Agent 决定本轮修改 harness 还是更新权重。Weng 指出实验存在严重混淆：任务 agent 用 gpt-oss-120b，Meta/Feedback 用 Claude Sonnet 4.6，且基线较弱。她认为方向值得研究，但证据仍属初步（provisional）。训练稳定性与 Goodhart 效应尚待解决。
- Continual Harness（Karten et al. 2026）：在长时程游戏中同时更新 harness 和 policy，后者使用强教师为低奖励轨迹提供的蒸馏标签学习。

## 5. 实验证据与七条挑战（每条都是后续论文的题眼）

Trehan & Chopra (2026) 在最小脚手架下测试了 LLM 从提出想法到完成论文的能力。实验使用三个领域的 45-50 篇种子文档，只有 4 个想法通过人类专家筛选，只有 1 个完整执行并形成论文。反复出现的失败模式有六种：沿用训练数据中的默认做法（旧库/陈旧命令/缺少依据的假设），在执行压力下偏离实现方案（任务复杂时转向常见的简单方案），记忆与上下文退化，过度乐观（把噪声误判为成功，即 Bubeck et al. 的"p-hacking and eureka-ing"、"numerical duct tape"），领域判断能力不足（难以判断实现复杂度、结果是否合理、哪些基线重要），以及科学品味弱（实验可以执行，却没有回答合适的问题）。

1. **弱而模糊的评估器**：多数研究声明缺少快速、精确的 verifier。自改进循环与 RL 一样，主要在能客观测量指标的任务上有效。研究品味、新颖性和长期科学价值仍难以测量。
2. **上下文与记忆生命周期**：系统越自主，需要保存和管理的记忆就越多。Weng 认为，上下文管理应逐步成为模型的核心智能能力，不能只依靠外围软件；人类对终身记忆的维护可作为参照。
3. **负结果**：文献偏向成功案例，LLM 可能不擅长放弃假设、报告负结果和承认失败。研究 harness 应便于保存失败尝试，让系统据此排除无效方向、缩小搜索空间。
4. **多样性塌缩**：进化与 RL 循环倾向复用已知的高奖励模式。在开放式研究中，最终表现最好的路径，早期可能被当前评估器打出较低分数。
5. **Reward hacking**：模型可能过拟合单测，利用 judge 的特定偏好骗过 judge，或利用基准中的伪影。评估器与权限控制应放在进化循环之外，并配合 held-out 测试、轨迹审计和关键决策点的人类评审。监督能自动化到什么程度仍待研究。
6. **长期成功**：现有优化目标多是完成手头任务。沙箱 RLVR 很难衡量可维护性、所有权边界、迁移成本、向后兼容性和未来的调试负担。
7. **人类角色**：人类需要继续参与循环，并随着系统能力提高，调整监督的时机和抽象层级。她强调，开发技术应服务于人类的未来。

附录汇总了 6 个基准：PaperBench（复现 20 篇 ICML 2024 论文，8316 条 rubric，当时最佳 Claude 3.5 Sonnet 约 21%，低于 ML PhD）、CORE-Bench、ScienceAgentBench、RE-Bench（AI 在 2 小时预算下表现为人类的 4 倍，8/32 小时预算下低于人类）、MLE-bench、KernelBench。

## 6. 局限与批判性评价

**分类框架**：这是目前唯一按优化对象的递进关系（prompt→上下文→工作流→harness 代码→优化器代码）组织 auto-research / 自改进 agent / 进化搜索三类文献的综述。将 harness 定义为可执行搜索空间，明确了这些方法具体优化什么。2026 下半年的工作逐条回应了七个挑战（见趋势调研）：EvalCEGAR/SCORE 改进弱评估器，SkillProx 将删除纳入常规操作，Metan 用进化档案应对多样性塌缩，BenchJack/HVTB 研究 reward hacking，Falsifiable Release Gates 讨论人类角色。

**判断的可检验性**：Weng 的三个预测都可以检验：模型最终会学会 harness 改进带来的行为，评估器必须在循环外，中档模型从 harness 中受益最大（引 Lin et al.）。其中，"评估器在循环外"与六篇论文研究的评估器共进化有所分歧。六篇论文证明，固定评估器会限制改进；Weng 则强调，任意修改评估器会使它被 hack。把锚保留在循环外，让 metric 在循环内进化，可以同时满足这两方面的要求。

**未覆盖的问题**：全文主要讨论编码与研究领域，几乎没有涉及多模态、具身和物理实验中的 harness，也没有讨论经济学约束（算力-认知劳动替代弹性）。Anthropic 文章与 2026 下半年的宏观讨论集中涉及这两方面。文中"52× 加速"等内部数据来自实验室自述，缺少第三方测量；METR 试点后来补充了部分证据。

## 7. 意义与位置

- 六篇论文都能对应到她的分类：DGM/MOSS→3.3-3.4 节（自改 harness+进化搜索）、EvoLM/ECHO→3.5 节（联合权重优化）、RQGM/WGtG→挑战 1+5（评估器与 reward hacking）、WikiSkill→模式 2+3.1 节（文件记忆+上下文工程）。
- Anthropic 文章详细介绍了她引用的前沿实验室加速现象。挑战 7 提出人类应转向更高层级的监督，这与 Anthropic 保留人类对方向和批准权的控制相符。
- 阅读顺序建议：先读本文了解分类，再读六篇论文了解各类方法的进展，最后读趋势调研，比较不同方法之间的关系。

**七条挑战在本仓库的回应表**（2026 年 7 月后）：

| Weng 的挑战 | 回应工作 | 报告 |
|---|---|---|
| 1 弱评估器 | EvalCEGAR 碰撞对驱动评估器进化；RHO 完全无锚 | 24, 25 |
| 2 上下文与记忆生命周期 | WikiSkill 分三层管理；技能进化五篇管理技能的整个生命周期 | 09, 26 |
| 3 负结果 | SkillProx 将删除纳入常规操作；WikiSkill 将被拒提案存入 wiki | 26, 09 |
| 4 多样性塌缩 | Metan 进化档案 archive-best vs best chain；DGM 保留可能支持后续改进的中间版本 | 20, 07 |
| 5 Reward hacking | HVTB 蜜罐测量；Prime Agent RCON 事故；AHE 只读 verifier | 27, 18 |
| 6 长期成功 | AutoSaddler durable updates（回归率减半）；Falsifiable Gates 持续检查不变量 | 16, 27 |
| 7 人类角色 | iCoder 限定五层 prior 的修改范围；Gates 允许自动收紧、放松须经人审 | 19, 27 |

**Weng 讨论的 meta-harness 层**由 Meta-Harness（报告 13）作为同名论文的研究对象。她认为，更强的模型可以减少 harness 中不必要的复杂设计。Prime Agent（报告 18）观察到，模型尚未受训以操作 harness，说明当前 harness 的使用仍受模型能力限制；harness 增加功能后，模型未必能充分利用。

**Weng 的"评估器在循环外"与评估侧四篇的关系**：六篇论文证明，固定评估器会限制改进，例如 ECHO 冻结 critic 后，效果低于不使用它的 GRPO。Weng 强调，任意修改评估器会使它被 hack。WGtG 将锚放在循环外，同时允许 metric 在循环内进化，以约束评估器的更新。本仓库据此组织对评估器问题的讨论。
