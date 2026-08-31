# 解读报告 03 · EvoLM: Self-Evolving Language Models through Co-Evolved Discriminative Rubrics

| 项目 | 内容 |
|---|---|
| arXiv | 2605.03871（2026-05-05，Under review） |
| 作者 | Shuyue Stella Li, Rui Xin 等（华盛顿大学 + Allen AI + UPenn；Pang Wei Koh、Yulia Tsvetkov 组） |
| 代码/模型 | github.com/stellalisy/EvoLM · huggingface.co/stellalisy/EvoLM-8B |
| 在六篇中的位置 | 评估侧第一篇：把 rubric 生成器纳入训练循环，与 policy 交替更新——共进化谱系中"权重内共进化"的代表 |

## 一句话核心主张

模型预训练里已经编码了大量评估知识，却没有被现有后训练方法当作奖励来源；EvoLM 把这份潜在能力结构化成**逐实例的判别性 rubric**，让同一个模型交替训练"出题打分"和"答题"两种能力——rubric 生成器的奖励是**让一个冻结的小 judge 更能分出好坏回答**（判别效用），policy 的奖励是 rubric 条件下的 judge 打分；全程不需要人类标注、专有 API 或领域验证器，偏好对完全由 policy 自己的输出通过**时间对比**（现在的回答 vs 早期 checkpoint 的回答）构造。

## 1. 方法

### 1.1 分解：rubric 生成 + judge 打分
标准做法是标量奖励模型 R(q,a)，评估标准隐在权重里不可检查。EvoLM 把奖励计算拆成两段自然语言接口：rubric 生成器 ρ_ϕ(q) 产出逐题评估标准 r，judge J(q,r,a)∈[0,1] 按标准打分。好处三个：**可解释**（标准可检查）、**模块化**（换 judge 不用重训）、**小 judge 可用**（给了具体标准，1.7B 的 judge 也能可靠打分——这是论文的核心赌注之一，实验证实）。

### 1.2 rubric 是隐变量：变分推断形式化
好 rubric 的定义只有一条：judge 用了它之后能把偏好回答排在前面。论文把 rubric 处理成解释观察到偏好的**隐变量**：p(a+≻a−|q,r)=σ(J(q,r,a+)−J(q,r,a−))，这是 Bradley-Terry 模型的推广（把隐标量奖励换成隐自然语言 rubric）。后验不可解，用摊销变分推断最大化 ELBO：重构偏好排序的对数似然 − KL(ρ_ϕ‖ρ_ref)。rubric 是离散文本，用策略梯度优化——rubric 生成器变成一个 agent，奖励是偏好重构对数似然。实际实现换成 margin 奖励 + 格式奖励：R = 0.7·(J(a+)−J(a−)) + 0.3·R_format（JSON schema 校验）。

### 1.3 交替训练（共进化的具体机制）
两个角色共享同一份 Qwen3-8B 权重（不同 prompt 切换），用 GRPO 训练。K=50 步交替：Phase 1 冻结 rubric 生成器训 policy（rubric 条件 judge 分做奖励）；Phase 2 冻结 policy 训 rubric 生成器（判别 margin 做奖励）。judge 全程冻结——**把改进信号的唯一来源隔离在 rubric 生成器上**。交替产生涌现课程：policy 变强 → rubric 必须更细才能分出好坏 → 更细的 rubric 给出更锐的奖励 → policy 再变强。

### 1.4 偏好对的三种自构造（无人类标注的关键）
1. **时间对比**：当前 policy 回答为 a+，t′<t 的早期 checkpoint 回答为 a−。步距 [20,100] 控制难度——距离大则对比容易，距离小则需要更细粒度 rubric，天然形成课程。
2. **推断问题（IQ）**：给 a+ 让 policy 反推它像在回答什么问题 q̂，再用 q̂ 生成 a−——训练 rubric 检查"回答是否切题"。
3. **rubric 条件（RC）**：a+ 由 (q,r) 条件生成、a− 只由 q 生成——直接测 rubric 是否包含可执行的改进指令。

## 2. 关键实验结果

设置：271K 提示（Tulu 3 混合，通用对话/指令遵循/数学/代码/科学理解），12 个基准（OLMo3-Adapt 套件），全部方法统一 500 步 policy 更新。

### 2.1 主结果（论文最重要的一张表）
| 奖励来源 | RewardBench-2（静态判别精度） | 下游 policy（OLMo3-Adapt 均分） |
|---|---|---|
| **Skywork-RM-V2 标量 RM** | **86.4%（最高）** | **59.7%（最低）** |
| GPT-4.1 提示 rubric | 36.6% | 66.7% |
| Qwen3-8B 提示 rubric | 26.2% | 67.5% |
| 四个 rubric-RL 基线（RAR/RRD/RLCER/Rubric-ARM） | — | 66.7–67.6% |
| 顺序训练（先 rubric 后 policy） | 47.2% | 68.3% |
| **EvoLM（共进化）** | 46.0% | **69.3%** |

两个反直觉结论：
1. **静态判分精度与下游质量脱钩甚至反挂**：标量 RM 在 RewardBench-2 上碾压所有 rubric 方法 40 个百分点，训出的 policy 却垫底（差 EvoLM 9.6 分）——policy 会针对固定评分面找捷径，这是 Gao et al. (2023) reward overoptimization 的又一实证。**评估器的价值不在静态精度，在能否跟着 policy 分布移动。**
2. **顺序训练的 rubric 静态精度更高（47.2 vs 46.0），下游却更差（68.3 vs 69.3）**——共进化的收益恰恰来自 rubric 对当前 policy 分布的适应性，静态基准测不出这个。

最大单项收益在代码生成：HumanEval+ 86.2% vs 次优 80.5%。

### 2.2 机制分析：rubric 从抽象标签进化为可验证检查
定性+统计分析（100 个评估提示）：纯标签式标准从 21.9% 降到 0.3%，嵌入具体期望值的标准从 6.9% 升到 19.3%，约束型标准从 7.7% 升到 20.3%；标准平均长度 59→112 字符而条数稳定在 3-4 条。数学域的 rubric 学会把 80% 权重压在一条嵌入期望答案的标准上（"正确的最大面积 144，由周长 48 导出"），**把证明验证变成答案核对**；受限写作域把格式/关键词要求合并成可数的显式检查。共同效应：把小 judge 做不可靠的整体语义判断，转换成小 judge 做得可靠的**具体模式匹配**——这是 margin 目标的直接后果（任何拉大分差的标准都被奖励，具体可验证的标准天然占优）。

### 2.3 泛化（rubric 生成器的真正价值检验）
- **OOD 域**：训练分布里完全没有的深度研究任务上，与专家人工 rubric 的成对排序一致性——HealthBench 58.4% vs GPT-4.1 的 52.5%，ResearchQA 59.3% vs 51.0%。8B 模型训出的 rubric 生成器在陌生领域比 GPT-4.1 更贴近专家判断。
- **跨 policy 迁移**：冻结 rubric 生成器训全新 policy——Qwen3-4B（65.2 vs GPT-4.1 rubric 的 64.4）、Llama-3.1-8B（46.9 vs 45.7），跨家族也成立。
- **跨 judge 迁移**：用 Qwen3-1.7B judge 训出的 rubric，换 Qwen3-8B judge 用时 RewardBench-2 +22.7 分——训练出的 rubric 编码了更强 judge 也提取不出的评估结构。
- **多 judge 训练**：五个小 judge 投票 + Fleiss's kappa 一致性奖励，进一步改善开箱即用的跨 judge 泛化。

## 3. 批判性评价

**真正的贡献是把"什么是好 rubric"变成了可优化的目标**。此前 rubric-RL 工作要么用 GPT-4.1 生成 rubric（RAR/RRD——专有依赖）、要么需要任务验证器（RLCER——只能做有 ground truth 的域）、要么需要偏好标签（Rubric-ARM）。EvoLM 是设计空间表里唯一五项全勾的（训练 rubric 生成器 / 无专有 API / 无外部标签 / 不限可验证域 / 与 policy 共进化）。

**但"无外部监督"有一个隐藏前提：时间对比假设后期回答优于早期回答**。这在训练早中期成立（policy 确实在涨），但如果训练进入退化阶段（reward hacking 开始），时间对比会把退化方向当成改进方向——**自监督信号与被监督对象共享同一个故障模式**。论文没有讨论这个循环性，Who Grades the Grader 的"评估器塌缩与进化观测等价"结论正打在这里：EvoLM 的 rubric 判别精度是对自己构造的偏好对测的，没有外部锚。

**judge 冻结是稳定性的来源，也是天花板**。EvoLM 把三元组（rubric 生成器、policy、judge）里只放开两个，judge 冻结避免了 RQGM 要处理的"尺子自己在动"问题——代价是 judge 能力上限最终约束整个循环（judge 分不出的差异，再好的 rubric 也无法表达）。论文用"具体化 rubric 降低 judge 负担"部分绕开了这个约束，但 rubric 能具体化的前提是任务有可具体化的正确性结构——开放域写作/研究判断这类任务上，把评估压成模式匹配本身就是失真。

**与安全的接口**：rubric 是自然语言、可检查，这比标量 RM 的黑盒评分对齐友好得多——人可以直接审计"policy 正在被什么标准优化"。但 2.2 节的机制分析同时暴露了风险：rubric 进化的方向是**评估收窄**（80% 权重压到单条标准），判别效用最大化与评估全面性之间存在未被讨论的张力。

## 4. 与其他材料的关系

- 与 **RQGM** 是共进化的两种时间结构：EvoLM 连续交替（K=50 步），RQGM epoch 内冻结评估器、边界处才换尺——RQGM 用可测性换适应速度，EvoLM 反之。
- 与 **WGtG** 互补且被其警示：EvoLM 展示评估器进化的收益，WGtG 证明没有外部锚时收益与塌缩不可区分。EvoLM 的专家 rubric 对齐实验（HealthBench/ResearchQA）实际上就是一种事后锚定——但它是评估阶段做的，不在训练循环里。
- 与 **ECHO** 同攻"评估侧滞后"：EvoLM 的武器是显式 rubric（结构化、可迁移），ECHO 是 critic 模型直接 GRPO 共训（连续、无结构）；EvoLM 在通用后训练场景，ECHO 在开放世界 agent 场景。
- 印证 **Weng** 挑战 4（评估瓶颈）与 Anthropic 文中固定加速测试的隐忧：任何静态评估器下的长期自改进都会撞上 overoptimization，EvoLM 的 59.7% vs 69.3% 是这一点最干净的量化。
