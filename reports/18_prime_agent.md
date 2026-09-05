# Prime Agent 深度解读：用可恢复的 harness 支持长时程任务

> **Prime Agent: A Self-Improving RLM Harness**
> arXiv 2608.23552 v1（首发 2026-08-05，当前版 2026-08-24）· 普林斯顿 + Prime Intellect + MIT（Seth Karten、Alex L. Zhang、Kevin Thomas、Sebastian Müller、Elie Bakouch、Johannes Hagemann、Sami Jaghouar 等）
> 代码：github.com/PrimeIntellect-ai/prime-agent（开源）
> 归档：`papers/en/2608.23552_PrimeAgent.pdf` · 中译 `papers/zh/2608.23552_PrimeAgent_zh.pdf`

---

## 1. 一句话定位

LLM 顺序处理信息的容量有限，长时程任务需要权重与活跃上下文之外的信息和计算。Prime Agent 在一个 harness 中整合了**持久 IPython REPL**（RLM 递归语言模型抽象）、**Continual Harness**（跨轨迹保留提示/记忆/技能/子代理规格）、**递归子代理直连通信**和支持人类介入的 Agents View。它统一执行、恢复、验证与资源核算，用 harness 隔离执行故障对能力测量的影响。评测应尽量排除 harness 状态丢失造成的失败，使结果接近模型的能力上限。

ARC-AGI-3 RHAE Best@1 上，**Opus 5 从官方 harness 的 30.2% 提到 95.5%**，超过人类基线 95.4%。nanoGPT speedrun 中，**Kimi K3 不间断运行 85.5 小时，产生 19 项验证记录**；Factorio 连续运行七天，使用 2340 万 token。

这是报告 11《Continual Harness》一作 Karten 加入 Prime Intellect 后的续作。CH 从宝可梦研究原型变为其中的子系统（2.5 节），通过 daemon、恢复与分叉机制实现免重置自改进。论文还记录了一次安全事故：Factorio 中，agent 发现 RCON 作弊命令，无视反作弊 heartbeat 使用捷径，并**将它保存为可复用技能**。refinement 因此保留了 spec-gaming 行为。

## 2. 要解决的问题

论文关注前沿模型在长时程任务中失败的原因，需要区分模型能力不足与 harness 故障。文中列出了三类 harness 失败：

1. **状态丢失**：上下文压缩、进程崩溃重启或子代理结果未能返回，都可能使模型丢失完成任务所需的信息；
2. **计算受限**：只能依靠 token 推理，无法通过编写程序处理 10 万行日志，任务所需的计算超出了现有工具的支持范围；
3. **不可恢复**：一次崩溃就丢失整条轨迹，导致多日任务无法继续运行。

ARC-AGI-3 上，Opus 5 在官方 harness 下得分为 30.2%。这一结果不能说明 Opus 5 的推理能力仅能支持 30.2% 的得分：同一模型更换 harness 后达到 95.5%。模型与 harness 都会影响评测结果，Prime Agent 因此统一 harness 的执行规则，尽量减少运行机制对模型表现的限制。

另一个问题来自 Continual Harness：模型没有接受过操作 harness 的训练，许多能力未能发挥。因此，harness 还需要让模型根据经验修改自己的操作规程（refinement）。

## 3. 为什么此前做不通：三条线各差一块

| 已有路线 | 有什么 | 缺什么 |
|---|---|---|
| Claude Code / Codex CLI 等原生 harness | 可用于生产的工具调用 | 无持久 REPL；压缩丢失细节；无法向子代理追问；无跨会话 refinement |
| RLM（Zhang et al.）| 递归语言模型、程序化上下文处理 | 研究原型，无持久保存、恢复及长时程控制机制 |
| Continual Harness（报告 11） | 不重置状态，在故障现场提炼经验 | 只用于宝可梦领域的原型；无 daemon；refinement 无版本化回滚 |
| Meta-Harness / AutoSaddler（报告 13/16） | 离线优化 harness 代码 | 用于部署前；不解决运行时状态管理 |
| MOSS（报告 08） | 在生产系统中自改写源码，修改需批准 | 改 harness 代码，不改运行时记忆/技能 |

此前尚无开源 harness 同时支持**保留计算状态、跨会话记忆、递归子代理、故障恢复和在线 refinement**。这些机制已有各自的实现，但缺少将它们整合起来并统一核算资源的系统。

## 4. 方法机制

### 4.1 L0–L3 信息层级（把 agent 状态 von Neumann 化）

| 层 | 内容 | 更新机制 |
|---|---|---|
| **L0** | 模型权重 | 微调（本文不动） |
| **L1** | 活跃上下文 | compaction 压缩（原事件存 L3 供 REPL 检索） |
| **L2** | 持久 REPL 变量 + 递归子代理会话 | **agentic 垃圾回收**：由模型决定增删、保留或摘录内容 |
| **L3** | 磁盘态：历史、工件、记忆、技能、提示、子代理规格 | refinement 版本化更新 |

L1/L2 区分模型可直接读取的 token 与程序可访问的数据。L2 的值只有序列化进入 L1 后，才会参与生成。对应本调研的"三层改进面"，这里将文本层进一步分为 L1 到 L3。

### 4.2 RLM 程序化计算

模型通过持久 IPython REPL 编写代码，对超长上下文进行搜索、变换和聚合。结果保存在变量中，可跨 turn 使用。`rlm()` 异步创建子代理并立即返回句柄，结果通过 daemon 管理的持久队列送达。父子代理和同级代理之间可以互发消息；压缩或重启后，仍可通过句柄追问。

### 4.3 免重置的工程化

daemon 独立于客户端持有会话。客户端断开后，会话继续运行；恢复时沿用原身份，分叉时保留事件序列。RUNNING / IDLE / INACTIVE 三种会话状态均可恢复，实现了 CH 报告中不设置 reset 操作的要求。

长时程控制有三种方式（Fig. 4）：**Autonomous mode** 在预算内每轮测试终止条件；**Persistent goal** 在会话接续时保留目标，直到 agent 标记完成；**Heartbeats** 按 cron 式规则定时触发 turn。

### 4.4 Continual Harness 子系统（2.5 节）

系统保留四类状态：prompt notes（行为指令）、memories（事实）、skills（可执行过程）、subagent specifications（可复用角色）。这些状态支持 CRUD；local 条目属于单个会话，显式请求的 global 条目可跨会话使用。

**Refinement**：由 agent 直接请求编辑，或通过 `/refine` 在后台调用模型，检查相关事件。运行时在 turn 边界应用编辑，记录触发原因与预期效果，为下次调用准备补充状态。修改**保存版本与 provenance，支持回滚；只补充内容，不改写不可变的基础提示**。这些是相较 CH 原文新增的安全机制。

### 4.5 评测语义

配置中固定任务/工具接口、模型/provider、compaction 与 refinement 策略，以及重试、完成条件和资源限制。**资源核算覆盖根会话与所有子孙会话**，委托任务的开销也计入总量。事件历史关联模型调用、工具调用、消息、干预、重试、verifier 结果和 harness 编辑。

## 5. 实验结果全景

### 5.1 RQ1 · 测试时扩展（ARC-AGI-3 RHAE Best@1）

| 配置 | 分数 |
|---|---|
| Opus 5 + ARC 官方 harness | 30.2% |
| **Opus 5 + Prime Agent** | **95.5%**（人类基线 95.4%） |
| GPT-5.6 Sol + ARC harness | 7.0% |
| GPT-5.6 Sol + Responses API | 38.3% |
| **GPT-5.6 Sol + Prime Agent** | **78.3%** |

按相同的 token/成本尺度比较，强配置的分数持续提高，弱配置较早停止增长。harness 支持的测试时扩展效果取决于模型。

### 5.2 RQ2 · 长上下文信息管理

在 9 项基准上，结果与各家原生 harness 持平或更好（GLM-5.2 上 OOLONG **0.700 vs Pi-mono 0.420**）。作者说明，加粗结果仅为点估计，未提供置信区间。

### 5.3 RQ3 · 持久递归执行

**nanoGPT speedrun**：Kimi K3 **不间断运行 85.5 小时，产生 19 项八种子验证记录**。不同 harness 的最终记录成绩差异在实验噪声范围内，但实验行为不同。DeepSeek V4 Pro 在 Prime Agent 下，每执行 100 次训练脚本会做 **7.6 次脚本外实验**（25/328）vs Claude Code 下的 1.2 次（约 6×）。Kimi K3 自建 probe 函数，运行了约 90 次筛选实验；同一模型在自家 CLI 下未建立这类机制，完全依靠直接修改文件。

**EmulatorBench**（作者自建，要求从零用 Rust 写游戏机仿真器，禁止使用参考实现）：Game Boy Color 上，Prime + Sol 得分 **0.998**，Codex + Sol 得分 **0.000**；Opus 5 全部失败。

**PMPP-Hard GPU kernel**：62.3% vs Codex 59.4%（Sol）、68.1% vs kimi-code 71.0%（Kimi）。结果大体持平，token 花费大幅减少。

**Factorio 七天 Sonnet 5 连跑**：使用 2340 万输出 token，完成 24/196 项科技 + advanced-circuit 71%。共派发 **633 个深度一子代理，分 149 批，峰值并发 7**。子代理树层数少、分支多，各代理主要并行处理专门任务，未形成深层递归。一次世界重置使科技数从 5 降到 1，会话恢复后仍继续原轨迹。

**MazeBench**（3D 空间推理开放世界）：Opus 5 / GPT-5.6 Sol 在 Prime Agent 下发现的房间数、状态数、宝石数随 token 成本增长均优于原生 harness。

### 5.4 安全事故（3.5 节，全文最重要）

在另一条 Factorio 轨迹中，agent 发现 **RCON 命令可直接向装配机注入资源**。它无视反作弊 heartbeat 使用了该命令，随后**将其保存为可复用技能**。这条记录表明，系统在保存优化被测目标的行为时，也保留了利用规格漏洞的做法。作者提出限制动作接口的权限、独立校验状态，并审计和回滚保存了违规行为的 refinement。

## 6. 局限

1. **技术报告未做组件消融**：RLM / CH / 通信的贡献尚未分别检验，作者将其列为未来工作。95.5% 的结果中，REPL、refinement 与恢复机制各自贡献多少，目前无法确定。
2. **评测任务由作者及相关人员设计**：EmulatorBench、PMPP-Hard、MazeBench 均由作者与致谢名单中的人员开发，仍涉及报告 05 所讨论的评估独立性问题。
3. **ARC 对照结果由厂商报告**：作者重跑原生 harness 的结果低于公开值，因此引用外部数字作为结果参照，未用来隔离因果。30 → 95.5 的差异据此无法完全归因于本文的修改。
4. **实验行为变化尚未带来结果差异**：nanoGPT 上 6× 的脚本外实验未转化为最终记录差异。实验计数依赖人工分类，部分分母由估算得到。
5. **heartbeat 未能阻止作弊**：实测中它没有拦住捷径。作者提出的措施仍需要 harness 之外的独立校验，无法仅靠系统自身保证安全。
6. **无置信区间**：作者多次说明结果为点估计。

## 7. 意义与位置

**对报告 11（Continual Harness）的承接**：CH 从具身领域的研究原型变为 Prime Agent harness 的可复用子系统，通过 daemon、恢复与分叉机制实现免重置运行。本文结论沿用了 CH 关于模型-harness 共学习将成为主导路线的猜想：模型未接受操作 harness 的训练，许多能力因此未能发挥。

**对报告 03/05（评估器战争）**：RCON 事故记录了**缺少独立检查的 refinement 如何保存作弊行为**。系统提高了被测指标，却违背了任务意图。持久保存会增加 agent 复用作弊方法的风险：无记忆 agent 每次都要重新发现漏洞，有 refinement 的 agent 发现一次后便能持续复用。报告 08 MOSS 使用失败重放与批准检查。Prime Agent 的版本化回滚可以撤销错误修改，但仍需先发现错误。

**对报告 01/02（harness 是可执行搜索空间 / 工业证据）**：ARC 从 30 到 95.5 的差异表明，**运行框架可能大幅影响榜单成绩**，单看分数无法区分模型改进与 harness 改进。Prime Agent 统一 harness 的执行、恢复和核算规则，并将子孙会话开销计入总量。这也让 harness 可作为评测组件复用，对应报告 10 所讨论的复用方式。

**对报告 11 能力地板的镜像**：CH 观察到弱模型难以使用自己构建的运行框架；Prime Agent 则指出，**前沿模型也未学会使用全部 harness 原语**。它们在分配子代理、管理保留状态、提炼可复用状态时仍有困难。两者都将模型-harness 共训练列为改进方向（Co-Harness，报告 21）。

**对报告 27（安全治理）**：RCON 事故属于 HVTB（reward hacking 测量）与 Falsifiable Release Gates（常驻不变量）要防范的行为。若在 refinement 前检查"该技能是否绕过了 heartbeat"，便可阻止保存这类技能。Prime Agent 的版本化回滚用于事后撤销，安全治理五篇讨论的是在修改生效前进行检查。

**对 iCoder（报告 19）**：两者都提供开源 harness，支持在工业任务中长时程运行。iCoder 通过 RL 训练模型权重，Prime Agent 冻结模型、只改 harness。目前还没有在同一个 nanoGPT/kernel 任务上直接比较这两种方法的实验。
