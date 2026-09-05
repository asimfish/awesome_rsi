# AutoSaddler 深度解读：用 mini-batch 学习优化 harness，并检查补丁的泛化效果

> **AutoSaddler: Automatic Harness Optimization with Durable Updates from Agent Execution Traces**
> arXiv 2608.23041 v1（2026-08-24）· POSTECH + KAIST + 南方科技大学 + Microsoft（Sungho Park*、Wonjoong Kim*、Rongyuan Tan* 共同一作，均为 Microsoft 实习；Jue Zhang†、Wook-Shin Han†）
> 项目页：aka.ms/AutoSaddler-website
> 归档：`papers/en/2608.23041_AutoSaddler.pdf` · 中译 `papers/zh/2608.23041_AutoSaddler_zh.pdf`

---

## 1. 一句话定位

手工调 harness 成本高、耗时长。本文将 harness 优化写成对 **θ = (prompt, tool, middleware)** 的预算受限**离线学习问题**，让优化步骤对应标准 mini-batch 训练。每轮先在训练 mini-batch 上运行当前 harness（forward），再由 Diagnosis-Patch Agent 分析失败轨迹与 harness 代码库，生成结构化补丁（textual backprop）。补丁通过同批验证后，在 dev 集上测泛化（generalization gate）；反思会话将 fixed/regressed/still-failing/still-passing 四类证据存入 **EvoDAG**（optimizer state），进化会话据此合成下一代候选。

系统要生成的 **durable updates** 与 hot fix 修复率相当（55% vs 58%），回归率减半（8% vs 17%）。三个基准的结果为 GAIA2 **53.0→62.0（+9.0）**、SWE-Bench Pro **37.3→46.9（+9.6，跨语言迁移）**、Terminal-Bench 2.0 **40.0→50.0（+10.0，超过人类手调 Terminus KIRA 2.5）**，使用的学习轨迹只有 Meta-Harness 的 1/10。消融中，**去掉泛化感知选择后 62.0→50.6，低于未优化基线 53.0**，表明这套设置下缺少泛化检查的自改进会降低测试表现。

## 2. 要解决的问题

模型训练的主要成本来自梯度计算，harness 工程的成本则主要来自评估时的 **rollout**。优化 harness 时，单条任务轨迹平均需要 55 万输入 token，一次全量评估需要数百次 rollout。已有自动方法各有局限：

- **prompt 优化器**（GEPA、OPRO）：只能改 prompt，无法修改工具与中间件。harness 失败往往发生在可执行层，例如工具缺少参数、循环逻辑未及时中断、缺少预检钩子。
- **Meta-Harness**：外部 coding agent 读取全部历史，每轮使用 10 MTok，并对 60 个候选做全量评估。在 GAIA2 这类任务轨迹很长的基准上，使用 1400 条学习轨迹后分数达到 61.5%，随后不再提高。
- **单轨迹 hot fix**：根据一条失败轨迹生成补丁，可能修复该任务却使其他任务回归。论文据此区分这类更新与 durable 更新。

论文提出三个设计要求。**in-depth diagnosis** 要求详细检查长轨迹与代码库，避免只做简单反思。**structured intervention** 将修改限定在 prompt/tool/middleware 三层九子型。**generalization-aware selection** 结合 mini-batch 验证、dev 检查与历史记忆，避免仅凭单条轨迹通过就接受补丁。

## 3. 为什么此前做不通：三条线各差一块

| 已有路线 | 有什么 | 缺什么 |
|---|---|---|
| GEPA / OPRO（prompt 优化） | 反思式文本梯度 | 只改 prompt；无 dev 检查；GAIA2 上 54.6 |
| Meta-Harness（报告 13） | 保存全部历史的文件系统 + 前沿 proposer | 对每个候选做全量评估，消耗较多 rollout 预算；无结构化补丁空间 |
| Self-Harness（报告 14） | 限制编辑范围 + 双 split 回归检查 | 无历史记忆 DAG；线性 lineage 无法 rebase/cherry-pick |
| DGM（报告 07） | 种群档案 + 自指 | 自指动力学在有限 rollout 预算下不可控；作者明确放弃 |
| Continual Harness（报告 11） | 在线运行，不重置状态 | 面向部署后场景；不解决开发期批量调优 |

此前工作尚未把 **harness 优化的七步（采样→前向→反传→验证→泛化→记忆→更新）与 mini-batch 学习逐一对应**，也未据此专门验证文本梯度。文本梯度与数值梯度的差异在于，前者需要额外检验。Appendix A Table 4 列出了这些步骤之间的对应关系。

## 4. 方法机制

### 4.1 七步循环（Figure 2）

任务集 X 分为 D_train / D_dev / D_test。每轮 n 执行以下步骤：
1. 在 mini-batch B_n ⊂ D_train 上评估当前 harness H_n（forward）；
2. **Diagnosis-Patch Session** 分析失败轨迹，生成结构化补丁 Δθ_n，H'_n = H_n + Δθ_n；
3. H'_n 在**同一 mini-batch** 上验证，Ĵ_Bn(H'_n) > Ĵ_Bn(H_n) 才算 mini-batch 改进；
4. 通过验证后，在 D_dev 上估计泛化表现；
5. **Reflection Session** 比较前后轨迹，按 fixed / regressed / still-failing / still-passing 四类记录结果；
6. 将教训与分数存入 **EvoDAG**；
7. **Evolution Session** 查询 EvoDAG，合成 H_{n+1}。

预算 K 耗尽后，返回 dev 上得分最高的候选。该候选只在测试集上评估一次，此后不再修改。

**文本梯度需要验证**：数值梯度由固定算子计算，文本"梯度"则依赖语义推断，可能出错。因此，每个补丁都要用于检验对失败原因的假设。只有在同批任务上重跑后分数严格上升，补丁才进入 dev 评估。

### 4.2 Diagnosis-Patch Session

**诊断与补丁生成在同一会话中完成**，agent 可以继续使用诊断时收集的上下文。输入包括失败轨迹、harness 代码库 θ_n 和结构化引导。系统逐步检索轨迹细节，以缓解长上下文带来的负担。它只提供实现 harness 功能逻辑的源文件，**禁止访问评估与基准数据相关代码**。

**补丁空间三层九子型（Table 1）**：

| 层 | 子型 | 类型 |
|---|---|---|
| Prompt | 规则增加 / 规则修改 | 引导 (S) |
| Tool | 新工具 / 参数修改 / 实现修复 | 能力 (C) |
| Tool | 描述修正 | 引导 (S) |
| Middleware | PreToolUse 钩子 | 引导 (S) |
| Middleware | 基建变更 / 循环逻辑变更 | 能力 (C) |

**能力补丁**修改可执行代码或编排逻辑，**引导补丁**只修改文本。**两相调度**参照学习率调度，先生成能力补丁，再生成引导补丁；能力阶段持续 1 个 epoch。

### 4.3 Reflection + EvoDAG + Evolution

**反思时必须检查结果是否来自随机波动**。每次 PASS↔FAIL 翻转都要对照代码 diff 与轨迹分歧点，区分代码修改的影响和 LLM 的非确定性，避免将偶然结果记为经验。若触发 dev 评估，还要分析"是否及如何泛化到 mini-batch 之外"。

**EvoDAG** G = (V, E)：节点 = 候选 harness + 教训 + 分数，边 = diff Δθ。Evolution Agent 查询全图，可从**任意子集**组合元素，无须始终从 H'_n 继续修改。这类似进化搜索中的 merge，可用于跳出局部最优。evo-dag CLI 支持 rebase、cherry-pick 和回滚。

GAIA2 的搜索轨迹记录了通过 git 操作恢复候选的过程。Iter20 在一个高频工具上设置了适用范围过宽的钩子，造成 dev 33.8% 的回归。系统 **rebase 回 Iter13**，并选取已验证的修复，在 Iter27 达到峰值 72.3%。Iter46 又因累积 8 个钩子下降 12.3 点；Iter47 将修改缩减为 4 个保守补丁，恢复到 69.2%。

## 5. 实验结果全景

### 5.1 主结果（训练/dev/测试按任务组严格分离）

| 基准 | 分离方式 | 基线 | AutoSaddler | 最强对比 |
|---|---|---|---|---|
| GAIA2 | 按 Universe | 53.0 | **62.0 (+9.0)** | GEPA 54.6 |
| SWE-Bench Pro | 按仓库 + 跨语言 | 37.3 | **46.9 (+9.6)** | 用 qutebrowser/Python 训练，在 Ansible/Flipt/Element-web 三种语言上测试 |
| Terminal-Bench 2.0 | – | 40.0 | **50.0 (+10.0)** | 人类手调 Terminus KIRA 47.5 |

### 5.2 效率

- GAIA2 dev 达到 72.3% 时，约执行了 **1000 次**任务；GEPA / Meta-Harness 执行 2800 次后分别停在 64.6% / 61.5%。
- 用于学习的轨迹为 **147 条 vs Meta-Harness 1400 条**（约 10×）；TB2 上为 12 条 vs 98 条（8×）。
- 执行 391 次 rollout 后，dev 达到 67.7%，超过 Meta-Harness 执行 1400 次的峰值。
- 每个补丁花费 $14.56，比 Meta-Harness 贵 $1.91，但实际耗时减少 39.6%。

### 5.3 消融即证据链（GAIA2）

| 消融 | 测试分 | 关键现象 |
|---|---|---|
| 完整 | 62.0 | 接受补丁 20 |
| 去 in-depth 诊断（浅反思单次 LLM 调用） | 57.8 | 接受补丁 20→15 |
| 去结构化干预 | 56.9 | **91.5% 的补丁为引导型**，能力型仅占 4%；新工具/循环变更/基建变更的接受率最高，分别为 83%/71%/67% |
| **去泛化感知选择** | **50.6** | **低于未优化基线 53.0** |
| 仅去两相调度 | −5.9pp | 人工设计的调度规则对结果有影响 |

进一步消融（Universe 22）：去掉 dev 过滤后 60.7→50.0，再去掉反思+EvoDAG 后 →44.9。

### 5.4 durable 的操作化定义

能力补丁与引导补丁的修复率相当（**55% vs 58%**），回归率约为后者的一半（**8% vs 17%**）。dev 回归率斜率为 −0.24pp/iter vs 消融 +0.16pp/iter：完整系统的回归率随迭代下降，消融系统则上升。

### 5.5 可迁移与稳健

- Opus 4.6 优化出的 harness 改用 **Haiku 4.5** 运行，仍提高 **+5.6pp（30.0→35.6）**；
- 更换训练 Universe（29→24）后，仍提高 +5.9pp；
- 独立重跑的结果为 58.6% vs 60.7%。

### 5.6 教训的抽象阶梯

对邮件回复质量这一问题，系统在 Iter 3 记录具体诊断："回复缺少收件人上下文"。到 Iter 19，它归纳出多个场景的共同问题："所有需要引用历史的任务都漏检索"。到 Iter 27，教训被改写为不依赖具体场景的规则："在生成前先检索相关上下文"。这些记录供 meta 层继续优化时使用。

## 6. 局限

1. **反复用 dev 集选择候选可能过拟合**：最终选择规则是在 dev 上取 argmax，即在 65 个 dev 场景上比较 21 个候选。dev 峰值 72.3% 与测试 62.0% 相差约 10 点，论文没有分析其中多少来自 dev 过拟合。作为独立评估依据的数据应避免参与进化；即使 dev 集内容不变，反复据此选择候选，也会降低它估计泛化表现的可靠性。
2. **评估依据的可靠性不同**：SBP/TB2 用单元测试和检查脚本验证，GAIA2 用 Llama-3.3-70B 当 judge。较大增益之一出现在依赖模型判断的基准上。针对 judge 的 game 行为也可能提高分数，例如引导补丁教 agent 使用 judge 偏好的答案格式；Rule 1 "respond with ONLY the direct answer" 就有这种可能。现有观测无法将它与真实能力提升区分开。
3. **stateless 假设未涵盖记忆**：θ 明确不含 memory 与 skill curation，并假设任务无状态、相互独立。本文与 WikiSkill/CH 因此处理不同的问题。这里的 "durable" 仅指任务分布固定时的离线效果，论文没有测试分布漂移下的持久性。
4. **重复实验较少**：由于优化成本高，主实验中每种方法只运行一次进化轨迹，稳健性检查也只有两条。TB2 测试仅 40 题，三次重跑的标准差为 0.0。
5. **结构先验与 Bitter-Lesson 的关系仍待检验**：人工设计的九子型分类与两相调度贡献了 5.9pp，表明当前模型在这些约束下表现更好。优化器模型增强后，这些约束可能限制搜索。Meta-Harness 的"无结构"与 AutoSaddler 的"强结构"在同一个 TB2 上都超过手调 harness，当前证据还不足以判断哪种做法更好。

## 7. 意义与位置

**对报告 01（Weng 总纲）**：本文将 harness 的搜索空间显式参数化为 θ 三元组，并将优化过程对应到 mini-batch 学习的七个步骤。用 Opus 优化、改由 Haiku 运行后，仍提高 +5.6pp，说明 **harness 可以跨模型复用**。

**对报告 05（Who Grades the Grader）**：w/o 泛化感知选择的消融中，去掉 dev 检查与反思后，自动优化得到的 harness（50.6）**比不优化（53.0）更差**。在这套设置下，缺少独立评估依据会使 harness 优化过度适应 mini-batch 噪声，偏离任务分布。harness 层的 reward overoptimization 表现为钩子适用范围过宽：它修复部分任务，却使其他任务回归，消融组回归率一度从 8%→22%。

**对报告 13（Meta-Harness）**：在同一个 TB2 上，两种方法都超过手调结果。Meta-Harness 不限定修改结构，读取全部历史；AutoSaddler 限定修改结构，将历史压缩为教训。两者效率相差 10×，AutoSaddler 结合 mini-batch 验证与 dev 检查，用更少的 rollout 达到更高 dev 分数。这一比较提示，Meta-Harness 的全量评估可能消耗了过多预算，问题在验证成本，而非历史信息不足。

**对报告 14（Self-Harness）**：两者都限制编辑范围，并在接受修改前检查结果。Self-Harness 的双 split 回归检查与 AutoSaddler 的 dev 检查结构相同。AutoSaddler 去掉检查后表现下降，为 Self-Harness 保留这一步提供了证据。

**对报告 09（WikiSkill）**：WikiSkill 将轨迹整理为供 **agent 使用**的技能，AutoSaddler 则通过反思将轨迹整理为供**优化器使用**的教训。后者从具体诊断归纳出跨场景模式，再改写为不依赖场景的原则，将相同的经验整理过程用于 meta 层。

**对报告 07（DGM）/ 08（MOSS）**：作者引用 DGM 与 Gödel agent 后，明确声明不建模自指动力学，meta-agent 不必等于 task agent，以便在有限 rollout 预算下控制搜索。MOSS 通过失败重放和批准检查来预防修改失败；AutoSaddler 使用同批验证、dev 检查与 DAG 回溯，并通过 EvoDAG 的 rebase/cherry-pick/回滚撤销修改，扩展了 MOSS 对修改失败的处理方式。

**对报告 11（Continual Harness）**：两者分别采用离线/重置式 vs 在线/免重置方式。AutoSaddler 优化部署前的系统，CH 处理部署后的持续适应，适用阶段不同，无法相互替代。
