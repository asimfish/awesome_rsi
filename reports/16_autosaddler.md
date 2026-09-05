# AutoSaddler 深度解读：把 harness 优化做成 mini-batch 学习——没有泛化门时自改进是负收益

> **AutoSaddler: Automatic Harness Optimization with Durable Updates from Agent Execution Traces**
> arXiv 2608.23041 v1（2026-08-24）· POSTECH + KAIST + 南方科技大学 + Microsoft（Sungho Park*、Wonjoong Kim*、Rongyuan Tan* 共同一作，均为 Microsoft 实习；Jue Zhang†、Wook-Shin Han†）
> 项目页：aka.ms/AutoSaddler-website
> 归档：`papers/en/2608.23041_AutoSaddler.pdf` · 中译 `papers/zh/2608.23041_AutoSaddler_zh.pdf`

---

## 1. 一句话定位

手工调 harness 贵且慢，本文把 harness 优化形式化为对 **θ = (prompt, tool, middleware)** 的预算受限**离线学习问题**，逐步映射到标准 mini-batch 训练：每轮在训练 mini-batch 上跑当前 harness（forward）、Diagnosis-Patch Agent 深挖失败轨迹与 harness 代码库产出结构化补丁（textual backprop）、同批验证过关后再上 dev 集测泛化（generalization gate）、反思会话把 fixed/regressed/still-failing/still-passing 四象限证据存进 **EvoDAG**（optimizer state）、进化会话据此合成下一代候选。目标是产出 **durable updates**——修复率与 hot fix 相当（55% vs 58%）但回归率减半（8% vs 17%）。三基准：GAIA2 **53.0→62.0（+9.0）**、SWE-Bench Pro **37.3→46.9（+9.6，跨语言迁移）**、Terminal-Bench 2.0 **40.0→50.0（+10.0，超人类手调 Terminus KIRA 2.5）**；用的学习轨迹只有 Meta-Harness 的 1/10。最重要的贡献是一条消融：**去掉泛化感知选择后 62.0→50.6，跌破未优化基线 53.0**——这是全调研关于"无锚自改进为负收益"的最干净证据。

## 2. 要解决的问题

harness 工程的成本结构与模型训练相反：模型训练的昂贵部分是梯度计算，harness 优化的昂贵部分是**rollout**——单条任务轨迹平均 55 万输入 token，一次全量评估动辄数百次 rollout。已有自动方法在这个成本结构下各有问题：

- **prompt 优化器**（GEPA、OPRO）：只改 prompt，碰不到工具与中间件——而 harness 失败的大头往往在可执行层（工具缺参数、循环逻辑不打断、没有预检钩子）。
- **Meta-Harness**：外部 coding agent 读全历史，每轮 10 MTok，全量评估 60 个候选——对 GAIA2 这种任务轨迹超长的基准，1400 条学习轨迹烧到饱和只到 61.5%。
- **单轨迹 hot fix**：看一条失败轨迹、打一个补丁——修好这条、打坏一片。论文把这类更新与 durable 更新对立。

三个设计要求由此推出：**in-depth diagnosis**（深挖长轨迹与代码库，不是浅反思）、**structured intervention**（限定在 prompt/tool/middleware 三层九子型，不是自由编辑）、**generalization-aware selection**（mini-batch 验证 + dev 门 + 历史记忆，不是单条轨迹通过就接受）。

## 3. 为什么此前做不通：三条线各差一块

| 已有路线 | 有什么 | 缺什么 |
|---|---|---|
| GEPA / OPRO（prompt 优化） | 反思式文本梯度 | 只碰 prompt；无 dev 门；GAIA2 上 54.6 |
| Meta-Harness（报告 13） | 全历史文件系统 + 前沿 proposer | 每候选全量评估，rollout 预算烧得快；无结构化补丁空间 |
| Self-Harness（报告 14） | 有界编辑 + 双 split 回归门 | 无历史记忆 DAG；线性 lineage 无法 rebase/cherry-pick |
| DGM（报告 07） | 种群档案 + 自指 | 自指动力学在有限 rollout 预算下不可控；作者明确放弃 |
| Continual Harness（报告 11） | 在线免重置 | 出厂后场景；不解决开发期批量调优 |

关键缺口：**没有人把 harness 优化的七步（采样→前向→反传→验证→泛化→记忆→更新）与 mini-batch 学习一一对齐**，并把"文本梯度需要验证"这个与数值梯度的根本差异做成机制。Appendix A Table 4 给出的映射表是这篇论文的思想骨架。

## 4. 方法机制

### 4.1 七步循环（Figure 2）

任务集 X 切成 D_train / D_dev / D_test。每轮 n：
1. 在 mini-batch B_n ⊂ D_train 上评估当前 harness H_n（forward）；
2. **Diagnosis-Patch Session** 分析失败轨迹产出结构化补丁 Δθ_n，H'_n = H_n + Δθ_n；
3. H'_n 在**同一 mini-batch** 上验证，Ĵ_Bn(H'_n) > Ĵ_Bn(H_n) 才算 mini-batch 改进；
4. 通过则上 D_dev 估泛化；
5. **Reflection Session** 比较前后轨迹，记录 fixed / regressed / still-failing / still-passing 四象限；
6. 教训与分数存进 **EvoDAG**；
7. **Evolution Session** 查 EvoDAG 合成 H_{n+1}。

预算 K 耗尽后返回 dev 上最高分的候选，在测试集上评估一次、不再修改。

**文本梯度需要验证**：数值梯度由固定算子推出，文本"梯度"是推断的、语义的、会错的——所以每个补丁先当作"检验根因假设的干预"，同批重跑分数严格上升才有资格进 dev 门。

### 4.2 Diagnosis-Patch Session

**不分离诊断与补丁生成**——让 agent 充分利用诊断期收集的上下文。输入：失败轨迹 + harness 代码库 θ_n + 结构化引导（渐进检索轨迹细节以缓解长上下文）。只暴露实现 harness 功能逻辑的源文件，**禁止访问评估与基准数据相关代码**。

**补丁空间三层九子型（Table 1）**：

| 层 | 子型 | 类型 |
|---|---|---|
| Prompt | 规则增加 / 规则修改 | 引导 (S) |
| Tool | 新工具 / 参数修改 / 实现修复 | 能力 (C) |
| Tool | 描述修正 | 引导 (S) |
| Middleware | PreToolUse 钩子 | 引导 (S) |
| Middleware | 基建变更 / 循环逻辑变更 | 能力 (C) |

**能力补丁**改可执行代码或编排逻辑；**引导补丁**只改文本。**两相调度**模拟学习率调度：先能力后引导，能力期 1 个 epoch。

### 4.3 Reflection + EvoDAG + Evolution

**反思强制做随机性甄别**——每个 PASS↔FAIL 翻转必须对照代码 diff 与轨迹分歧点，区分真因果与 LLM 非确定性的假信号，防止把运气污染进经验库。若触发 dev 评估，额外反思"是否及如何泛化到 mini-batch 之外"。

**EvoDAG** G = (V, E)：节点 = 候选 harness + 教训 + 分数，边 = diff Δθ。Evolution Agent 查全图，可从**任意子集**组合元素——不只是从 H'_n 继续，类似进化搜索的 merge，逃出局部最优。经 evo-dag CLI 支持 rebase、cherry-pick、回滚。

搜索轨迹（GAIA2）：Iter20 一个高频工具上的过宽钩子造成 dev 33.8% 的灾难性回归，系统 **rebase 回 Iter13** 并摘取已证实修复，Iter27 冲上峰值 72.3%；Iter46 又因累积 8 个钩子跌 12.3 点，Iter47 剪到 4 个保守补丁恢复 69.2%。**自动优化器学会了 git 工作流。**

## 5. 实验结果全景

### 5.1 主结果（训练/dev/测试按任务组严格分离）

| 基准 | 分离方式 | 基线 | AutoSaddler | 最强对比 |
|---|---|---|---|---|
| GAIA2 | 按 Universe | 53.0 | **62.0 (+9.0)** | GEPA 54.6 |
| SWE-Bench Pro | 按仓库 + 跨语言 | 37.3 | **46.9 (+9.6)** | qutebrowser/Python 训练，Ansible/Flipt/Element-web 三语言测 |
| Terminal-Bench 2.0 | – | 40.0 | **50.0 (+10.0)** | 人类手调 Terminus KIRA 47.5 |

### 5.2 效率

- GAIA2 dev 72.3% 只花约 **1000 次**任务执行；GEPA / Meta-Harness 烧 2800 次饱和在 64.6% / 61.5%。
- 真正用于学习的轨迹：**147 条 vs Meta-Harness 1400 条**（约 10×）；TB2 上 12 条 vs 98 条（8×）。
- 391 次 rollout 达 dev 67.7%，已超 Meta-Harness 1400 次的峰值。
- 单补丁 $14.56（比 Meta-Harness 贵 $1.91 但墙钟省 39.6%）。

### 5.3 消融即证据链（GAIA2）

| 消融 | 测试分 | 关键现象 |
|---|---|---|
| 完整 | 62.0 | 接受补丁 20 |
| 去 in-depth 诊断（浅反思单次 LLM 调用） | 57.8 | 接受补丁 20→15 |
| 去结构化干预 | 56.9 | 补丁分布塌缩到 **91.5% 引导型**、能力型只剩 4%——而新工具/循环变更/基建变更的接受率恰是最高的 83%/71%/67% |
| **去泛化感知选择** | **50.6** | **跌破未优化基线 53.0** |
| 仅去两相调度 | −5.9pp | 人类结构先验的贡献 |

细粒度版（Universe 22）：去 dev 过滤 60.7→50.0，再去反思+EvoDAG →44.9。

### 5.4 durable 的操作化定义

能力补丁与引导补丁修复率相当（**55% vs 58%**），但回归率减半（**8% vs 17%**）；dev 回归率斜率 −0.24pp/iter vs 消融 +0.16pp/iter——完整系统随迭代越来越稳，消融系统越来越脆。

### 5.5 可迁移与稳健

- Opus 4.6 优化出的 harness 换 **Haiku 4.5** 跑仍 **+5.6pp（30.0→35.6）**；
- 换训练 Universe（29→24）仍 +5.9pp；
- 独立重跑 58.6% vs 60.7%。

### 5.6 教训的抽象阶梯

同一问题（邮件回复质量）的教训从原子诊断（Iter 3："回复缺少收件人上下文"）→ 跨场景模式（Iter 19："所有需要引用历史的任务都漏检索"）→ 场景无关原则（Iter 27："在生成前先检索相关上下文"）——经验编译的抽象阶梯在 meta 层重演。

## 6. 局限

1. **dev 集是新的可磨损锚**：最终选择规则是在 dev 上取 argmax——65 个 dev 场景上比较 21 个候选是教科书式自适应选择，dev 峰值 72.3% 与测试 62.0% 之间约 10 点落差里有多少是 dev 过拟合，论文没有分解。锚定纪律要求锚不参与进化：dev 集虽不被"改"，但被反复"选"，选择压力同样磨损锚的信息量。
2. **锚的硬度不均**：SBP/TB2 用单元测试和检查脚本（硬验证器），GAIA2 却用 Llama-3.3-70B 当 judge——最大增益之一恰落在最软的锚上，而针对 judge 的 game 行为（引导补丁教 agent 用 judge 偏好的答案格式，Rule 1 "respond with ONLY the direct answer" 就在边缘）与真实能力提升在此观测等价。
3. **stateless 假设切掉了记忆**：θ 明确不含 memory 与 skill curation，任务假设无状态独立——这既是与 WikiSkill/CH 的分工边界，也意味着"durable"只在任务分布固定的离线意义上成立，分布漂移下的持久性没有测。
4. **统计力薄**：优化太贵，主实验每方法只跑一次进化轨迹，稳健性检查也只有两条；TB2 测试仅 40 题且三次重跑标准差 0.0。
5. **结构先验的反 Bitter-Lesson 一面**：人类设计的九子型分类加两相调度贡献了 5.9pp——当前能力档位上约束胜过自由，但该结论会随优化器模型变强而过期，届时结构化干预可能反成枷锁。Meta-Harness 的"无结构"与 AutoSaddler 的"强结构"在同一个 TB2 上都赢了手调 harness，说明当前证据不足以裁决。

## 7. 意义与位置

**对报告 01（Weng 总纲）**：把"harness 是可执行搜索空间"推到最工程化形态——搜索空间显式参数化为 θ 三元组，优化过程逐行映射到 mini-batch 学习七步；Opus 调、Haiku 用仍 +5.6pp 的跨模型迁移，是 **harness 资产化**最直接的实证之一。

**对报告 05（Who Grades the Grader）**：w/o 泛化感知选择的消融是全调研关于"无锚自改进"最干净的负结果——去掉 dev 门控与反思后，自动优化产出的 harness（50.6）**比不优化（53.0）更差**。这不是收益递减而是负收益：没有不参与进化的锚，harness 空间的爬山会爬向 mini-batch 噪声而非任务分布信号。reward overoptimization 在 harness 层的形态就是"过宽钩子修好一处、打坏一片"（消融组回归率 8%→22% 的尖峰）。

**对报告 13（Meta-Harness）**：同一个 TB2 上两种哲学都赢了手调——Meta-Harness 无结构 + 全历史，AutoSaddler 强结构 + 压缩教训。但效率差 10×：AutoSaddler 的 mini-batch + dev 门用更少 rollout 达更高 dev 分。这提示 Meta-Harness 的全量评估可能是浪费——不是信息不够，是验证太贵。

**对报告 14（Self-Harness）**：两者都是"有界编辑 + 门控"，Self-Harness 的双 split 回归门与 AutoSaddler 的 dev 门同构；AutoSaddler 的消融给 Self-Harness 的门控必要性提供了反面证据。

**对报告 09（WikiSkill）**：两种经验沉淀的镜像——WikiSkill 把轨迹编译成给 **agent 消费**的技能，AutoSaddler 的反思把轨迹编译成给**优化器消费**的教训；三级抽象阶梯（原子诊断→跨场景模式→场景无关原则）是同一个编译过程在 meta 层的重演。

**对报告 07（DGM）/ 08（MOSS）**：作者明确放弃自指（引用 DGM 与 Gödel agent 后声明不建模自指动力学、meta-agent 不必等于 task agent），换来有限 rollout 预算下更可控的搜索；EvoDAG 的 rebase/cherry-pick/回滚是 MOSS"改坏怎么办"门控故事的进化版——MOSS 用失败重放加批准门，AutoSaddler 用同批验证、dev 门与 DAG 回溯，安全机制从"防改坏"转向"可撤销"。

**对报告 11（Continual Harness）**：离线/重置式 vs 在线/免重置的正对照——AutoSaddler 管出厂前，CH 管出厂后，谁也替代不了谁。
