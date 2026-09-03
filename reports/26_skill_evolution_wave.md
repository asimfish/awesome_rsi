# 解读报告 26 · 技能进化红海五篇合评：WikiSkill 同月的平行答案

| 论文 | arXiv | 机构 | 归档 |
|---|---|---|---|
| SkillCommit: Evolving Agent Skills through Behaviorally Validated Scope Expansion | 2608.15165 | Yu He, Weikai Yang 等 | `papers/en/2608.15165_SkillCommit.pdf` |
| HyperSkill: Self-Evolving LLM Agents via Hypergraph-Structured Skill Memory | 2608.16114 | Ruiyao Xu, Tiankai Yang, Wei-Chieh Huang 等 | `papers/en/2608.16114_HyperSkill.pdf` |
| ERSkill: Evolving for Skill-Guided Adaptive Memory Retrieval | 2608.12720 | Haolong Chen, Liang Zhang, Guangxu Zhu 等 | `papers/en/2608.12720_ERSkill.pdf` |
| SkillProx: Self-Evolving Agent Skills via Proximal Textual Gradient Descent | 2608.07449 | Mingxuan Zheng, Yujin Zhou, Chuxue Cao 等 | `papers/en/2608.07449_SkillProx.pdf` |
| Evo-Harness: Context-to-Harness Skill Compilation for Self-Evolving Agents | 2608.15071 | Tianxin Wei, Zhan Shi, Minhua Lin, Bing He 等（Amazon 系） | `papers/en/2608.15071_EvoHarness.pdf` |
| 在调研中的位置 | 2026 年 8 月 WikiSkill（报告 09）发布前后两周内密集出现的五篇平行工作——知识侧从"一个方法"变成"一个方向"的证据；本报告不逐篇精读，按**共同问题 → 五种分歧 → 共识与反面数据**组织 | | |

## 一句话核心主张

五篇论文回答同一个问题——**冻结模型的 agent 如何把交互经验变成不占权重的可复用能力**——并在两件事上达成共识：(1) 存原始轨迹是错的，必须抽象成技能；(2) 技能库需要生命周期管理（验证门禁、效用审计、合并与退役）。分歧全在**抽象的结构**上：行为验证的层级（SkillCommit）、超图（HyperSkill）、可执行检索原语（ERSkill）、近端梯度形式化（SkillProx）、单次执行编译为 harness（Evo-Harness）。

## 五种分歧

**SkillCommit · 反对按语义相似度合并。** 核心批评：现有方法按 embedding 相似度或 LLM 判断合并经验，会把表面相似但**行为不兼容**的策略合并坏。它的流水线：每条新经验先保留为实例级补丁（保住在局部上下文里验证过的行为）→ embedding 检索候选相关技能 → **跨实例重放**（技能在彼此的案例上是否仍然有效）+ LLM 机制检查（是否共享同一底层机制）→ 双检通过才抽象为高层技能，且只有在保持全部成员技能已验证行为的前提下才提交（commit）。RuleArena / OpenExempt / KOR-Bench 上持续提升，学到的技能可跨模型规模与家族迁移。它对 WikiSkill 的意义：直接点中"经验 → wiki → skill"三层里最脆弱的抽象一步。

**HyperSkill · 记忆与技能合成一张超图。** 两类节点（子任务步骤、可复用技能），每条超边 = 一条轨迹里的子任务与技能的 n 元关联，从而保留了扁平存储丢掉的**组合关系**。双路检索（子任务级 + 轨迹级）按跨检索轨迹的共现排名技能；周期性结构感知维护——按质量加权传播修剪低效用节点、合并冗余技能。xBench / GAIA / WebWalkerQA 上超过十个记忆基线，GAIA **+11.51**、WebWalkerQA **+11.18**（GPT-4o 与 Qwen3-30B-A3B）。它把 WikiSkill 的三层分离改造成图结构上的连续谱。

**ERSkill · 把"检索行为"本身技能化。** 长期记忆的检索机制很少被当作可进化组件，但异构查询需要不同的证据构造策略。ERSkill 把检索行为表示为由基本原语组合成的可执行技能，训练一个路由器把查询匹配到最优技能；技能集与路由器共进化，用**经验 trie** 记录已探索的检索路径，用**双 frontier** 把"新技能扩张"与"面向路由器的稳定部署"安全解耦。F1 / BLEU-1 / LLM-judge 平均提升 **31.3%**（Qwen3-Next-80B-A3B）与 **28.1%**（GPT-5.4-nano）。双 frontier 与 RQGM（报告 04）的 epoch 冻结同构——都是用"冻结一侧"换稳定性。

**SkillProx · 近端梯度下降搬进文本技能空间。** 批评现有框架缺少显式的"诊断-结果"反馈，且把删除当作普通编辑而非专门的知识固化机制。目标函数 = 任务损失 + 技能复杂度；**前向阶段**在同批任务上重放诊断驱动的编辑、回滚回归、把测量到的结果喂回后续诊断；**后向阶段**把技能分解为可审计知识单元，用冻结的留一（leave-one-out）效用审计估计每个单元的贡献，做验证门控的固化 / 降级 / 删除。多骨干、ID 与 OOD 基准上比最强文本梯度基线 **+3.0 pp**。"删除作为一等公民"回应 Weng（报告 01）的负结果处理挑战。

**Evo-Harness · 单次执行编译成结构化 harness。** 提出"在线 harness 学习"形式化：冻结 agent 在顺序任务流上持续更新一个结构化 harness，而真实环境里每个新任务往往只给**一次**改进机会，执行上下文噪声极大。核心机制"context-to-harness skill compilation"把单次执行蒸馏为通用技能 + 主题技能。Claude Opus 4.6 为求解器时五基准全胜（Table 1）：CL-Bench 29.54→**34.02**、TerminalBench-2 62.92→**73.03**、SWE-bench Lite 63.67→67.00、τ-bench 72.73→76.97、WebArena-Infinity 72.50→76.25，超过 AWM / Dynamic Cheatsheet / Evo-Memory / ACE / XSkill 全部基线。它的方法论贡献大于分数：系统性隔离 evolver 设计、反馈类型、迁移设置各自的贡献，明确把 skill harness 当作"研究自改进机制的可解释介质"。

## 共识、反面数据与批评

**三条共识**：抽象优于存储（五篇一致）；生命周期管理是必需品（SkillCommit 的提交门、HyperSkill 的修剪合并、SkillProx 的审计删除、ERSkill 的双 frontier）；技能可迁移（SkillCommit 跨规模家族、Evo-Harness 跨域）。

**一条重要的反面数据来自谱系之外**：Metan（报告 20）实测代码/技能转移只贡献 15% 的增益，72% 来自层间条件化字符串——至少在那个设置里，**好的条件化比好的技能库值钱得多**。五篇论文都没有做"技能库 vs 等量上下文提示"的对照，这是整个方向的共同盲点。

**两条批评**：(1) 五篇几乎全部用任务成功率做效用信号，技能库的"锚"就是基准分——Who Grades the Grader（报告 05）的观测等价问题原样存在，只有 SkillProx 的冻结留一审计和 SkillCommit 的跨实例重放算是在效用估计上多加了一层纪律；(2) 分歧点（层级 / 超图 / 检索原语 / 近端形式化）缺少横向对比——五篇互不引用（发布间隔太短），谁的结构更好目前无法判断，Evo-Harness 的隔离变量方法论是唯一可以拿来做裁决的框架。

## 与本调研的连线

1. **对报告 09 WikiSkill 的定位修正**：WikiSkill 不是孤立方法，而是一波浪潮中"经验先编译为知识再蒸馏为技能"这一支；SkillCommit 的行为验证、HyperSkill 的组合关系保留，都可以看作对 WikiSkill 三层分离的两种替代实现。
2. **与报告 10 insight 6（经验必须先编译成知识才能复利）的关系**：五篇全部支持"编译"这一步，但对"编译成什么结构"给出五个答案——insight 6 应细化为"编译是必要的，结构是开放的"。
3. **与报告 04 RQGM / 报告 14 Self-Harness 的机制同构**：ERSkill 双 frontier、SkillCommit 提交门、SkillProx 验证门控与 RQGM epoch 冻结、Self-Harness 回归门是同一防御哲学在技能层的投影——**改坏即拒，是所有能跑的自进化系统的公共部件**。
4. **对报告 20 Metan 的悬而未决**：技能资产化叙事（报告 10 insight 5）与 Metan 的 15% 数据直接冲突，需要一个"技能库 vs 条件化提示"的受控实验来裁决——这是本方向最值得做的下一个实验。

