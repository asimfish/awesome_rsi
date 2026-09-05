# ECHO 深度解读：让 critic 与 policy 同步更新，适应变化的失败模式

> **ECHO: No More Stale Feedback — Co-Evolving Critics for Open-World Agent Learning**
> arXiv 2601.06794 v2（2026-04-14）· 人大高瓴 + **阿里高德（Amap）** + 北大 + 港科广 + 南科大
> 归档：`papers/en/2601.06794_ECHO.pdf`

---

## 1. 一句话定位

critique 引导的 RL 用自然语言反馈补充稀疏结果奖励，但现有 critic 多为静态或离线模型。on-policy RL 中，policy 的错误模式随训练变化：早期需要纠正粗略错误，后期则需定位细微缺陷；冻结 critic 的反馈逐渐失去作用，在 ALFWorld/SciWorld 上的效果低于不用 critic 的 GRPO。ECHO 将 critic 纳入共进化，以诊断让 policy 精炼后获得的饱和感知增益奖励 critic，policy 与 critic 各用一路 GRPO 同步更新。Qwen3-4B 在四个环境中的总均分为 77.85 vs GRPO 70.57（+7.28），DeepSearch 的相对收益最大，为 +42%。

实验依次考察了失败模式变化、冻结反馈失效和同步更新的修复效果。外部奖励模型 R 始终冻结，因此 WGtG 对评估依据的质疑在此仍然适用。

## 2. 要解决的问题

scalar outcome reward 只反映最终结果，无法指出具体应如何修正。critique-guided RL 用自然语言 critic 提供诊断，已有两类做法：

1. **模板 critic**（HINT、LUFFY 等）：成本低，但无法适应 agent 的具体动作；
2. **独立微调的 critic 模型**（McAleese 等）：诊断更有针对性（targeted），但训练后冻结，隐含假设最优 critique 策略始终是 stationary 的。

这一假设在 on-policy RL 中不成立。policy 持续更新，会改变轨迹分布和失败模式。早期 rollout 多为未调用工具之类的明显错误，后期则可能只差第三步检索 query 中的一个词。critic 若在旧分布上训练后冻结，就可能给出 redundant、粒度不合适或误导性的反馈。这种 critic staleness 会降低样本效率，使长时程 refinement 难以持续改进。

ECHO 用共进化的 critic 替代 stationary supervisor，并按 policy 精炼后的实际得分增益衡量 critic 的效果。

## 3. 为什么此前做不通：三条线各差一块

| 已有路线 | 有什么 | 缺什么 |
|---|---|---|
| 模板 / 离线 critic | 零训练成本 | **不跟踪 policy 漂移** |
| 独立微调 frozen critic | 比模板更 targeted | 训练后冻结；分布变化后 feedback 边际效用衰减 |
| Self-reward / 自评 LLM | 不需要外部 critic | critic 与 policy 同源，可能产生一致错误；缺少诊断、精炼、增益之间的反馈循环 |
| EvoLM 共进化 rubric | rubric 文本可读可迁移 | judge 在 K 步内冻结；权重层 vs 文本层 |
| RQGM 共进化 evaluator | epoch 内冻结，按锚定结果替换评估器，修改源码 | 适应较慢；需要 ground-truth 锚 |

已有工作尚未完整检验 critic 陈旧的原因和后果，也未将这些证据与修复方案联系起来。本文考察失败分布变化是否使冻结 critic 降低表现，再测试同步共进化与饱和感知奖励能否解决问题。多数工作只报告加入 critic 后的增益，没有报告冻结 critic 后得分下降、甚至低于无 critic 的情况。

## 4. 方法机制

### 4.1 级联进化 rollout（组结构的来源）

- **阶段一·多视角诊断**：policy 生成初始轨迹 τ_o，外部奖励模型 R 给出基线分 s_o。critic 以 (q, τ_o, s_o) 为条件，独立采样 N 份不同诊断 c_o。分数写入 prompt，使诊断能结合当前得分，指出哪些缺陷阻碍了进一步提升。
- **阶段二·条件精炼**：policy 以 (q, c_o) 为增强输入，为每份诊断生成一条精炼轨迹 τ_r，再由 R 给出 s_r。

一次级联得到基线分 s_o、诊断组 G_C（N 份对缺陷的不同假设）和精炼组 G_P（N 条对应的修正行动）。两个组相互依赖，分别用于 GRPO 的组内相对优势估计。

### 4.2 饱和感知增益塑形（对"等距谬误"的修正）

线性改进 Δs = s_r − s_o 将 0.9→0.95 与 0.1→0.15 视为相同增益，但接近上限时，取得相同提升要困难得多。线性奖励因此较少鼓励 critic 诊断高质量方案中的细微缺陷，优化容易停滞。

ECHO 用软障碍函数 ω(s)=1/(1−s+η)，定义内在增益：

g(s_o, s_r) = ln[(1−s_o+η)/(1−s_r+η)]

该增益具有三项性质：饱和感知，即相同 Δs 在高分区对应更大增益；可加/路径一致，即 g(a,b)+g(b,c)=g(a,c)；反对称，即 g(a,b)=−g(b,a)。增益直接作为 critic 的奖励 r_c。

### 4.3 双轨同步 GRPO

policy 的优势在精炼组 G_P 内归一化，用于比较不同诊断对应的修正效果。critic 的优势在诊断组的饱和感知奖励上归一化。两者采用相同的 GRPO 目标，包含 clip 与 KL 约束，每一步同时更新 critic 和 policy。

## 5. 实验结果全景

**设置**：实验使用 WebShop、ALFWorld、SciWorld、DeepSearch 四个环境，基础模型为 Qwen3-4B 与 Qwen2.5-7B。critic 默认与 policy 使用相同基础模型，R 取环境自带的程序化奖励。

### 主结果（Qwen3-4B）

| 方法 | WebShop | ALFWorld | SciWorld | DeepSearch | 总均 |
|---|---|---|---|---|---|
| 原始 Qwen3-4B | 6.12 | 0.32 | 4.50 | 20.25 | 7.80 |
| + GRPO | 82.37 | 87.50 | 79.14 | 33.25 | 70.57 |
| + **ECHO** | **90.03** | **91.25** | **82.88** | **47.25** | **77.85** |

相对 GRPO，平均提高 +7.28 分；DeepSearch 相对提高 +42%，WebShop 相对提高 +9%。需要跨多步诊断并修复具体失败原因的任务受益最大。除 DeepSearch 外，4B + ECHO 在全部环境中超过 GPT-5、Claude-Sonnet-4.5、Gemini-2.5-pro 等专有模型，以及 Qwen3-235B、DeepSeek-R1 等大型开源模型。Qwen2.5-7B 也有提升，为 79.03 vs GRPO 74.14。

### RQ2 · 失败模式漂移 + 冻结 critic 消融（论文经验根基）

训练轨迹分为早、中、晚三期，由 Gemini-2.5-pro 生成诊断，再用 Qwen3-8B-Embedding 嵌入和 t-SNE 可视化。四个环境均出现分布漂移。WebShop/DeepSearch 各期的失败形成紧凑簇，高密度中心明显移动；ALFWorld/SciWorld 的分布更分散，密度质心也持续变化。

**冻结 critic 消融**（仅冻结 critic，其余设置相同）：

| | WebShop | ALFWorld | SciWorld | DeepSearch |
|---|---|---|---|---|
| ECHO | 90.03 | 91.25 | 82.88 | 47.25 |
| Frozen critic | ↓ | **68.58** | ↓ | ↓ |

ALFWorld/SciWorld 的下降最明显，得分低于不使用反馈的 GRPO。复杂环境中，陈旧 critic 给出冗余或偏离问题的诊断，policy 在精炼时过度依赖这些噪声，放大了长时程错误。

效果随训练阶段变化。WebShop 上，冻结 critic 早期表现较好，后期被反超；ALFWorld/SciWorld 上，ECHO 前期与 GRPO 接近，中后期差距逐渐扩大。

### RQ3 · 饱和感知塑形的价值

去掉 SA 塑形、改用线性 Δs 后，WebShop/SciWorld 均下降。WebShop 更常进入接近得分上限的区域，因此下降更多。(s_o, s_r) 联合密度图显示，使用 SA 塑形后，改进区（s_r>s_o）的概率质量明显增加，尤其集中在高分区域。这与 SA 奖励鼓励高分方案继续精炼的设计一致。

### 附录 C · 三组补充证据（Qwen3-4B）

**vs 其他 critique-guided 基线（Table 4）**：

| 方法 | WebShop | ALFWorld | SciWorld | DeepSearch | 总均 |
|---|---|---|---|---|---|
| RCO（训练型 critic，policy 不更新） | 35.64 | 3.00 | 16.50 | 25.75 | 20.22 |
| LUFFY（教师答案提示） | 80.34 | 80.92 | 70.44 | 31.00 | 65.18 |
| **ECHO** | **90.03** | **91.25** | **82.88** | **47.25** | **77.85** |

LUFFY 使用 ground-truth 教师提示，ECHO 没有这类监督，得分仍更高。这说明自适应诊断可以带来收益，无须依靠更强的外部指导。RCO 不更新 policy，在长时程交互环境中几乎失效。

**critic 引导 vs 纯重采样（Table 5，N=8 同预算）**：

| 环境 | 阶段 | 无 critic 重采样 | critic 引导精炼 | 净增益 |
|---|---|---|---|---|
| WebShop | 早 | +0.81 | +6.54 | +5.73 |
| WebShop | 中 | +0.59 | +5.42 | +4.83 |
| WebShop | **晚** | +0.23 | **+7.54** | **+7.31** |
| SciWorld | 早 | +0.32 | +2.82 | +2.50 |
| SciWorld | 晚 | +0.34 | +3.78 | +3.44 |

同样生成 8 条第二轮轨迹时，有 critic 的增益是无 critic 的 8–30 倍，因此额外采样无法单独解释提升。晚期净增益最大，说明 critic 随共进化逐渐发挥更大作用。这与冻结 critic 在晚期降低表现的结果相符。

**critique 粒度随训练迁移（Table 6，Gemini-2.5-pro 固定评估）**：

| 环境 | 阶段 | 问题被解决率 | 粗粒度 | 中粒度 | 细粒度 |
|---|---|---|---|---|---|
| WebShop | 早 | 74.56% | 62.42 | 24.12 | 13.46 |
| WebShop | 晚 | **95.30%** | 8.61 | 49.34 | **42.05** |
| SciWorld | 早 | 75.15% | 68.90 | 20.66 | 10.44 |
| SciWorld | 晚 | 90.02% | 11.78 | 41.50 | **46.72** |

早期 critique 主要给出粗粒度的流程指导，例如指出没有调用工具；晚期近半用于定位细粒度错误。critic 的诊断分布随 policy 的失败分布变化，提供了共进化过程的直接观测。policy 也更能利用 critic 的反馈，问题被解决率从 75%→95%。

**训练成本（Table 7，附录 C.4）**：critic rollout 与更新本身带来的额外开销较小。主要成本来自精炼阶段，因为需要解码更长的上下文。总墙钟时间比 GRPO 平均多约 15%。

## 6. 局限

1. **外部奖励模型 R 仍被冻结**：critic 的全部机制依赖 R(q,τ)。R 保持不变，因此 ECHO 虽然解决了 critic 陈旧的问题，同样的风险仍可能出现在 R 上。按 WGtG 的分析，policy 学会 game R 后，共进化循环会放大 hack。
2. **四个基准的 R 都是环境自带的程序化奖励**，包括购物匹配度和任务完成检查，相对难以 game。换用学习型 RM 后能否保持稳定，尚无证据。
3. **静态 critic 反馈可能降低表现**：critic 既可能有害，也可能有用。部署静态 LLM-as-a-judge 反馈循环时，不能假定增加反馈就一定提高分数。
4. **成本核算仅见附录**：Table 7 报告墙钟时间多约 15%，没有报告 token 数。N=8 份诊断 + 8 条精炼意味着每步至少额外生成 16 条，墙钟 15% 是并行运行后的结果，token 成本的增幅可能更大。实验使用 16 × H20，额外开销"15%"能否在小集群复现仍不清楚。
5. **粒度分析由 Gemini-2.5-pro 外部评估**：用冻结 LLM 判断另一个 LLM 的 critique 是否细粒度、问题是否被解决，仍可能存在 judge 偏差。Table 6 的趋势有参考价值，绝对数字需谨慎解释。
6. **WGtG 对验证方式的质疑仍适用**：共进化 judge 与 policy，再报告 policy 得分提高，正是 WGtG 证明无法验证评估器有效性的实验设计。ECHO 的 critic 是否有效，取决于 R 是否可信，但 R 尚未经过审计。

## 7. 意义与位置

**实验将失败分布变化与冻结反馈失效联系起来**。嵌入可视化显示失败分布非平稳，冻结消融表明静态 critic 会降低表现，同步共进化则改善了结果。这些实验分别检验了问题是否存在、会产生什么影响，以及更新反馈是否有效。

**Table 6 直接记录了诊断粒度的变化**。除 policy 得分外，表中还测量了 critic 的输出内容，显示 critic 输出分布随 policy 的失败分布变化。RQGM 的 RQ3 课程效应（报告 04）也涉及评估器变化，但 RQGM 只观察档案排序的 Spearman ρ，ECHO 则对 critique 内容作了分类。

**与 EvoLM（报告 03）**：两者都处理评估反馈陈旧的问题。EvoLM 更新可读的 rubric 文本，judge 保持冻结；ECHO 更新 critic 权重，与 policy 连续同步。

**与 RQGM（报告 04）**：RQGM 在 harness/代码层更新评估器，epoch 内冻结，替换时用锚验证；ECHO 直接同步更新权重。RQGM 有跨 epoch 统计保证，但适应较慢；ECHO 适应较快，但缺少验证 critic 改进的外部锚。

**与 Weng / Anthropic**：ECHO 通过更新权重提高反馈质量。Anthropic 认为执行已加快，判断能力仍限制进展；ECHO 则展示了诊断能力可以通过训练改进，前提是任务范围较窄，且 R 可信。
