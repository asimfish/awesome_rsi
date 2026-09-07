# Reef 深度解读：把"服务、反馈、更新、版本发布"做成一个可复用的循环

> **Reef: Continual learning infra for self-improving agents**
> Human-Agent-Society，2026-08-31 建库，Apache-2.0，PyPI 包 `reef-infra` · GitHub：github.com/Human-Agent-Society/reef · 文档：reefinfra.ai/docs · 读取时间 2026-09-08（689 star，47 fork，50 个开放 issue，234 个 Python 文件）
> 团队：Wenhao Chai、Paul Liang、Ao Qu、Zhenting Qi、Bo Liu、Jiacheng Zhu 等 25 人（按 README 列表）
> 依赖：SGLang（推理）、slime（权重训练）、cordis（harness 进化）；配套项目 reef-eval、reef-client、Harbor 任务标准

---

## 1. 一句话定位

Reef 是一个开源基础设施，把自改进 agent 需要的四件事接成一个循环：**Serve**（代理模型请求并记录每次交互，返回一个 receipt）→ **Observe**（外部反馈按 receipt 匹配到交互记录）→ **Grow**（recipe 从合格记录里产出候选更新）→ **Commit**（候选经评估器和选择策略判定后发布为新版本，旧版本继续服务直到切换）。它支持两条学习面：用 slime + SGLang 更新模型权重，或修改 harness 的 prompt、规则、技能和代码；两条面共用同一套记录、版本链和候选评估机制。仓库内置六个 recipe（SAO、OpenClaw-RL、TTT-Discover、Guidance-TTT、SkillClaw、GEPA）和一个 Meta-Harness 实现，每个都附复现结果：SAO 在 48 个 rollout 的预算下 0.479 高于基线 0.458 和 GRPO 0.417；GEPA 在 AIME 2025 上 26.67% → 46.67%（种子 0）；TTT-Discover 在 Erdős 最小重叠、26 圆和 32 圆装填上复现到与原论文相差不超过 8e-7。它没有解决锚从哪来的问题——候选评估器由使用者提供——但把本仓库反复讨论的"评估门 + 版本化回滚"从每篇论文各自实现变成了一个通用组件。

## 2. 要解决的问题

本仓库收录的自进化系统几乎每一个都自己搭了一套基础设施：DGM 有档案和沙箱，MOSS 有失败重放和批准队列，AutoSaddler 有 EvoDAG，Self-Harness 有双 split 回归门，Prime Agent 有 daemon 和版本化 refinement。这些系统的核心机制彼此不同，但外围的工程需求高度重复：记录每次模型调用、把事后反馈对应到具体调用、决定一个候选更新是否上线、保留版本以便回滚、更新时不中断服务。

Reef 的 README 用一张表说明它填的位置：推理引擎（vLLM、SGLang）能服务流量但不训练；RL 框架（slime、veRL、AReaL）能训练但不服务；两者都不管版本、不保证更新期间在线、不支持权重以外的进化对象。Reef 声称同时覆盖这五项。

第二个问题是**反馈与调用的对应**。生产环境里反馈往往是事后的、稀疏的、可能重试或迟到的；Reef 用 receipt（每次推理记录的 id，同时标识产生它的版本）解决对应问题，报告只引用 receipt，每份报告最多消费一次。

## 3. 与已有工具的关系

| 工具 | 服务流量 | 训练权重 | 版本管理 | 更新不中断 | 进化 harness | 评估门 |
|---|---|---|---|---|---|---|
| vLLM / SGLang | 是 | 否 | 否 | 否 | 否 | 否 |
| slime / veRL / AReaL | 否 | 是 | 否 | 否 | 否 | 否 |
| Proteus（报告 29） | 否 | 否 | 是（快照） | 否 | 是（声明区域） | 是（产物验证） |
| Prime Agent（报告 18） | 是（daemon） | 否 | 是（refinement 版本） | 是 | 是 | 弱（无独立锚） |
| MOSS（报告 08） | 是（生产 agent） | 否 | 是（镜像） | 是（换装探测） | 是（源码） | 是（失败重放 + 人工批准） |
| **Reef** | 是 | 是 | 是（release chain） | 是 | 是（harness tree） | 是（CandidateEvaluator + Selector） |

Reef 与 MOSS、Prime Agent 的差别在于它不是一个 agent，而是 agent 外面的一层：任何通过 OpenAI 或 Anthropic 兼容接口调用模型的 harness 都可以接进来，训练与推理后端可以替换。与 Proteus 的差别是 Reef 同时覆盖权重训练，Proteus 只做 harness。

## 4. 机制拆解

### 4.1 核心对象（据 glossary）

- **Scenario**：一个工作负载，独立拥有记录、训练状态和版本链；第一个带新 `x-reef-scenario` 头的请求创建它并永久绑定一个 recipe。
- **Agent record / Receipt**：每次推理或报告存为一条记录；推理的 receipt 在响应头 `x-reef-agent-record-id` 返回，同时记录服务它的版本。
- **Report**：`POST /reef/report`，带数值 `score` 和文本或结构化 `feedback`，引用一个或多个 receipt；核心只存不解释，由 recipe 决定含义。
- **Recipe**：绑定处理器（判定每条记录 TRAIN / WAIT / NEVER 并组批）、step preparer（把批次变成损失族和优势）、损失族（`sao`、`tttd`、`openclawrl`）、运行时和 surface。
- **Artifact / Release / Content ID**：artifact 是被选中的内容（检查点、在线权重或 harness tree）；release 是一次发布决定，带父 release；content_id 标识内容本身。回滚是创建一个指向旧 content_id 的新 release，历史只追加不回退。
- **Candidate selection**：`CandidateEvaluator` 测量候选，`CandidateSelector` 决定选或拒，二者合为 `CandidateEvaluationPlugin`，每个 recipe 都必须带。文档称之为 gate。
- **Harness tree**：harness 中可变文件的版本化表示——配置、规则、prompt 模板、技能、扩展代码，native 适配器下还包括工具、hook 和控制流图；通过 `GET /reef/harness` 下发。
- **Mutation**：对 harness tree 一个根级节点的 create / update / remove；一个序列作为一个复合提案、一个判定。
- **Staleness**：训练样本所用权重与当前服务权重之间允许的滞后，`max_staleness=0` 要求样本对着生成它的权重训练。

### 4.2 权重训练面

以 SAO recipe 为例：harness 把模型调用发到 Reef，拿到 receipt；任务结束后评估器算出奖励，harness 报告分数并引用该 receipt；处理器把合格记录送入训练步；slime 更新权重后同步到 SGLang 服务运行时，后续请求使用新版本而不重启。SAO（arXiv 2607.07508）的特点是一条打分的 rollout 驱动一次训练步，没有比较组，也没有等最慢样本的屏障。

### 4.3 harness 进化面

以 harness-evolve 快速入门为例：harness 配置是一棵节点树，提案是一次门控的树变更，通过的变更发布为版本化产物供客户端拉取。提案者是被服务的模型本身：读当前技能节点和自己失败的请求，输出一个 JSON 格式的技能变更。评估在固定的小任务集上跑真实的无头 episode，按最终答案精确匹配打分，**每个任务当前树和候选树各跑一次**（paired gate），只有让原来失败的任务通过的提案才发布。

快速入门的记录表（2026-08-17 至 09-06，13 次运行）说明了这个机制的实际行为：Qwen3-8B 在三个任务上 1.0 / 0.0 / 1.0，提案"create direct-answer"技能，候选树 1.0 / 1.0 / 1.0，胜负平 1 / 0 / 2，发布；qwen2.5:7b 的多次运行中，提案在 gate 上 0 胜 1 负 2 平或 0 / 0 / 3 时被拒绝。作者标明每行是单次运行，没有重复，gate episode 本身有随机性（同一种子树在 sieve 任务上记录时 1.0、gate 里五次中四次 0.0）。

### 4.4 内置 recipe 与复现结果

| Recipe | 更新对象 | 来源论文 | Reef 上的复现结果 |
|---|---|---|---|
| SAO | 权重 | arXiv 2607.07508 | Qwen3-30B-A3B、IMOAnswerBench 三题、每臂 48 个 rollout：SAO 0.479 > 基线 0.458 > GRPO(+DIS) 0.417；GRPO 48 个 rollout 只填满 12 组且多数组内全对或全错、无梯度。作者说明这是预算受限的对比，只回答"论文的排序在此预算下是否成立" |
| TTT-Discover | 权重（LoRA r=32） | arXiv 2601.16175 | Qwen3-8B、两块 B200、每步 8 组 × 64 rollout：Erdős 最小重叠 25 步 0.38094（论文 0.38093，目标 0.38080，越低越好）；26 圆装填 50 步 2.635983（与论文相同）；32 圆装填 2.939573（与论文差 < 8e-7）。每个任务一条轨迹，无种子方差 |
| Guidance-TTT | 引导模型权重 | 同上 | 训练只输出摘要的 Qwen 引导策略，冻结的外部执行模型写程序 |
| OpenClaw-RL | 权重 | arXiv 2603.10165 | 72 个 GSM8K 作业会话的模拟学生流，next-state 二值奖励、无外部评分器；一次记录的运行在第 14 个会话达到"连续三次通过"的适应标准；作者标明这是单人格单任务族的适应结果 |
| SkillClaw | harness 技能池 | arXiv 2608.08377 | 白天跑冻结的 60 任务 WildClawBench，晚上每组技能一个决定合成一次复合变更；`selection: always`，即按原论文的无门控方式每晚都发布，探针 episode 的分数只记录不决定 |
| GEPA | harness（prompt） | arXiv 2507.19457 | AIME 2025 150 题测试集：种子 0 上游 GEPA 31.33% → 42.67%（+11.33），Reef 实现 26.67% → 46.67%（+20.00）；种子 1 上游 +14.00，Reef +12.00；两种子均值上游 +12.67、Reef +16.00。作者说明 GEPA 是随机优化，单次运行没有稳定数字 |
| Meta-Harness | harness 组合 | arXiv 2603.28052 | 每个候选是完整的 Reef 组合，proposer 看全部保留候选及分数；选择标准为验证集均分严格高于在位者入选时的分；Reef 的 paired gate 让它每次迭代花两倍评估。Terminal-Bench 结果另见 RESULTS.md |

recipe 不随 `reef-infra` 的 wheel 发布，放在仓库 `recipes/` 目录按 dotted 路径选择；Reef 没有全局的 recipe 注册表。

### 4.5 代码结构

234 个 Python 文件：`train/` 90 个（处理器、评估、更新任务）、`harness/` 47 个（适配器、树、变更）、`service/` 24 个（请求与记录）、`runtime/` 23 个（推理与产物更新）、其余为 `artifact/`、`scenario/`、`surface/`、`core/`、`recipe/`、`observability/`。产物和检查点依赖 git-lfs。

## 5. 与本仓库主线的对照

**评估门是一等公民，但门里放什么由用户决定。** 每个 recipe 必须带 `candidate_evaluation` 插件，这与本仓库"每个能运行的系统都有一个不参与进化的检查环节"的观察一致。但 Reef 只提供接口：harness-evolve 用固定任务集的精确匹配，GEPA 用验证集均分，SkillClaw 干脆 `selection: always`。锚是否独立于训练循环、是否会被优化压力带偏，由使用者的 evaluator 决定。本仓库报告 05 和 16 的结论在这里表现为一个配置问题：把 `selection` 设成 always 就是无锚运行。

**receipt 机制解决了本仓库多篇论文各自处理的归因问题。** Self-Harness 的失败签名、AutoSaddler 的反思会话、HarnessFix 的轨迹 IR 都需要先把失败对应到具体的执行记录；Reef 在服务层就把每次调用和产生它的版本绑定，报告只能引用 receipt。这是基础设施层的解法，不替代方法层的归因，但让归因有了稳定的原始数据。

**版本链的设计与 MOSS、OLE 一致。** 回滚不是回退历史而是追加一个指向旧内容的新 release；content_id 与 release_id 分离，使"同样的内容被重新发布"可以被识别。这和 OLE（报告 27）的"策略资产带版本和血统"、MOSS 的 last-known-good 镜像是同一思路，Reef 把它做成了默认行为。

**staleness 参数对应本仓库的"优化期间尺子必须冻结"。** `max_staleness=0` 要求训练样本对着生成它的权重训练，这是在线权重更新里保持 on-policy 的工程手段，与 RQGM 的 epoch 内冻结（报告 04）解决的是同一类不一致问题，只是对象从评估器换成了策略。

**Meta-Harness 的 Reef 实现给出了一个可核对的细节**：Reef 的 paired gate 每次迭代评估候选和在位者各一次，原论文只评估候选，所以按 episode 计的预算与原论文的迭代数不可直接比较。这类实现差异正是复现工作的价值所在。

**能力地板在 Reef 的记录里再次出现。** harness-evolve 快速入门里，qwen2.5:7b 作为提案者的多次运行大多被 gate 拒绝或打平，Qwen3-8B 和 DeepSeek-V4-Flash 的运行才有发布；这与 Continual Harness（报告 11）"弱模型自建脚手架反而更差"和 Self-Harness（报告 14）"回归门保护地板"的观察一致——Reef 的 gate 在这里起的正是保护作用。

## 6. 局限

1. **锚由用户提供，Reef 不保证其独立性。** `selection: always` 是合法配置；文档没有讨论 evaluator 被优化压力带偏的风险。
2. **复现结果规模小、多为单次运行。** SAO 每臂 48 个 rollout；TTT-Discover 每任务一条轨迹；harness-evolve 每行一次运行；作者在每处都标明了这一点，但这意味着结果只能说明"机制能跑通、排序与论文一致"，不能说明效果大小。
3. **SFT 复现失败被如实记录**：SAO 示例里两种 SFT 变体（3.5k TIR、30k 混合）都低于基座（44.69 → 9.75 / 5.44），未能复现论文的 SFT 结果。
4. **项目很新。** 2026-08-31 建库，读取时 50 个开放 issue，接口（如 `episode_workers` 等字段）在文档中已标为弃用并替换，API 稳定性未知。
5. **部署门槛。** 权重面需要 slime + SGLang + GPU 集群（SAO 示例用两台 8 卡节点）；harness 面可以只用模型 API，但 native 适配器和沙箱（bubblewrap、E2B）有平台限制（Linux、Python 3.12+）。
6. **与 iCoder 式多阶段研究流水线的适配未验证。** Reef 的 recipe 是"一种方法绑定一个 scenario"，iCoder 的 Data → SFT → OPSD → RLVR 是多阶段、可回退的流程，能否表示为 recipe 序列需要实际尝试。
7. **无独立的安全层。** 没有 Falsifiable Release Gates（报告 27）式的常驻不变量或"收紧自动、放松人审"规则；人工批准需要用户在 selector 里自己实现。

## 7. 意义与位置

**对报告 10 insight 7 的实证**：本仓库说进入生产的系统都有版本、审计、预测、回滚四项机制，Reef 把其中版本和回滚做成了默认行为，审计有记录层支撑，预测（提议者预测自己改动的效果）没有。它是第一个把这些机制从单篇论文的实现变成通用组件的开源项目。

**对 §10 路线图的意义**：本仓库计划以 iCoder 为研究流水线基座，Reef 可以承担运行时的服务、记录、候选评估和版本发布层。两者的接缝在 recipe：iCoder 的阶段控制器是否能表示为 Reef 的一组 recipe 与 scenario，是下一步要核实的事。另一个要核实的是 Reef 的 `CandidateEvaluator` 能否接入独立于训练循环的锚集（本仓库的不可妥协项）。

**对报告 13、16、21 三种 harness 修改哲学的意义**：Reef 已经实现了 Meta-Harness 风格的全历史搜索；AutoSaddler 的 mini-batch 诊断和 Co-Harness 的双环在它上面都可以表示为 recipe，这使三种哲学的对照实验第一次可以在同一套基础设施上做。

**对报告 18 Prime Agent 的对照**：两者都在做"免重置、版本化 refinement"，Prime Agent 是一个完整的 agent 产品，Reef 是 agent 外面的一层；Prime Agent 的 RCON 作弊事故在 Reef 里对应的是 `selection` 配置——如果 evaluator 只看被测目标，同样的事会发生。

**对报告 29、30 的关系**：Prism-Shadow 的清单收录 Proteus 而未收 Reef（Reef 建库晚于其数据快照）；按其九维标签，Reef 应为 Parametric + Non-parametric、Online、Sequential、验收标准由 recipe 决定、更新者 Self 或 Teacher 均可。
