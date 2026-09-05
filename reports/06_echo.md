# ECHO 深度解读：critic 必须跟 policy 一起动——冻结反馈不是无用，是有害

> **ECHO: No More Stale Feedback — Co-Evolving Critics for Open-World Agent Learning**
> arXiv 2601.06794 v2（2026-04-14）· 人大高瓴 + **阿里高德（Amap）** + 北大 + 港科广 + 南科大
> 归档：`papers/en/2601.06794_ECHO.pdf`

---

## 1. 一句话定位

critique 引导的 RL 用自然语言反馈补充稀疏结果奖励，但现有方法的 critic 是静态或离线的——on-policy RL 中 policy 的错误模式随训练漂移（早期粗错误需要高层提示，后期瓶颈是细微难定位的缺陷），冻结 critic 会**变陈旧**，边际效用持续衰减，在 ALFWorld/SciWorld 上**甚至低于不用 critic 的裸 GRPO**。ECHO 把 critic 当作共进化模块：critic 的奖励不是"听起来有道理"，而是它的诊断在 policy 精炼后实际带来的**饱和感知增益**；policy 与 critic 各跑一路 GRPO **同步更新**。Qwen3-4B 四环境总均 **77.85 vs GRPO 70.57（+7.28）**；最大相对收益 DeepSearch **+42%**。证据链最完整的是"漂移→冻结失效→同步修复"——但外部奖励模型 R 全程冻结，WGtG 的批判在此完全适用。

## 2. 要解决的问题

scalar outcome reward 只反映最终结果、不提供可操作的诊断——critique-guided RL 试图用自然语言 critic 补这个缺口。已有两条线：

1. **模板 critic**（HINT、LUFFY 等）：便宜但不可适应 agent 的具体动作；
2. **独立微调的 critic 模型**（McAleese 等）：更 targeted，但训练后**冻结**，隐含假设最优 critique 策略是 stationary 的。

在 on-policy RL 里这个假设不成立：policy 连续进化 → 轨迹分布漂移 → 失败模式漂移。早期 rollout 被粗错误主导（"你根本没调用工具"），后期被细粒度缺陷卡住（"第三步检索 query 偏了 一个词"）。critic 在旧分布上训练并冻结，产出 redundant、粒度失准、甚至误导的反馈——**critic staleness** 限制样本效率，阻止长时程 refinement 持续改进。

ECHO 的核心命题：**critic 应该是共进化模块，而不是 stationary supervisor**——且 critic 的好坏不由自评，而由"精炼后 policy 实际涨了多少分"来定义。

## 3. 为什么此前做不通：三条线各差一块

| 已有路线 | 有什么 | 缺什么 |
|---|---|---|
| 模板 / 离线 critic | 零训练成本 | **不跟踪 policy 漂移** |
| 独立微调 frozen critic | 比模板 targeted | **训练后静止**；漂移后 feedback 边际效用衰减 |
| Self-reward / 自评 LLM | 不需要外部 critic | critic 与 policy 同源，合谋风险；无"诊断→精炼→增益"闭环 |
| EvoLM 共进化 rubric | rubric 文本可读可迁移 | judge 在 K 步内冻结；权重层 vs 文本层 |
| RQGM 共进化 evaluator | epoch 冻结 + 锚定晋升 + 源码层 | 适应慢；需要 ground-truth 锚 |

关键缺口：**没有人把"critic 陈旧"从现象（失败分布漂移）到后果（冻结 critic 变害）到方案（同步共进化 + 饱和感知奖励）串成完整因果链。** 大多数工作只报告"加了 critic 涨分"，不报告"critic 冻住后掉分且低于无 critic"。

## 4. 方法机制

### 4.1 级联进化 rollout（组结构的来源）

- **阶段一·多视角诊断**：policy 生成初始轨迹 τ_o，外部奖励模型 R 给基线分 s_o；critic 以 (q, τ_o, s_o) 为条件独立采样 **N 份**不同诊断 c_o——分数放进 prompt 做"分数感知"解释（指出是什么缺口拦住了更高分）。
- **阶段二·条件精炼**：policy 以 (q, c_o) 为增强输入，对每份诊断各生成一条精炼轨迹 τ_r，R 打出 s_r。

一次级联产生：基线分 s_o、诊断组 G_C（N 份对缺陷的不同假设）、精炼组 G_P（N 条对应修正行动）——两个互相依赖的组结构喂 GRPO 的组内相对优势估计。

### 4.2 饱和感知增益塑形（对"等距谬误"的修正）

线性改进 Δs = s_r − s_o 的缺陷：0.9→0.95 与 0.1→0.15 被等价看待，但接近上限时每一分提升所需努力激增——线性奖励让 critic 不愿诊断高质量方案里细微但关键的缺陷，导致优化平台期。

ECHO 用软障碍函数 ω(s)=1/(1−s+η)，定义内在增益：

g(s_o, s_r) = ln[(1−s_o+η)/(1−s_r+η)]

三条性质：**饱和感知**（同样 Δs 在高分区增益更大）；**可加/路径一致**（g(a,b)+g(b,c)=g(a,c)）；**反对称**（g(a,b)=−g(b,a)）。这个增益直接做 critic 的奖励 r_c。

### 4.3 双轨同步 GRPO

policy 的优势在精炼组 G_P 内归一化（从多样化诊断中识别最有效的修正路径）；critic 的优势在诊断组的饱和感知奖励上归一化。两者用同一个 GRPO 目标（含 clip 与 KL 约束）**同步更新**——不是"先训 critic 再训 policy"的两阶段，而是每步锁步。

## 5. 实验结果全景

**设置**：WebShop、ALFWorld、SciWorld、DeepSearch 四环境；骨干 Qwen3-4B 与 Qwen2.5-7B；critic 默认与 policy 同骨干；R 是环境自带的程序化奖励。

### 主结果（Qwen3-4B）

| 方法 | WebShop | ALFWorld | SciWorld | DeepSearch | 总均 |
|---|---|---|---|---|---|
| 裸 Qwen3-4B | 6.12 | 0.32 | 4.50 | 20.25 | 7.80 |
| + GRPO | 82.37 | 87.50 | 79.14 | 33.25 | 70.57 |
| + **ECHO** | **90.03** | **91.25** | **82.88** | **47.25** | **77.85** |

对 GRPO 平均 **+7.28** 分；DeepSearch **+42%** 相对、WebShop **+9%** 相对——跨多步诊断并修复特定失败原因的任务受益最大。4B + ECHO 除 DeepSearch 外全面超过 GPT-5、Claude-Sonnet-4.5、Gemini-2.5-pro 等专有模型和 Qwen3-235B、DeepSeek-R1 等大开源模型。Qwen2.5-7B 上同样成立（**79.03 vs GRPO 74.14**）。

### RQ2 · 失败模式漂移 + 冻结 critic 消融（论文经验根基）

训练轨迹分早/中/晚三期，Gemini-2.5-pro 生成诊断、Qwen3-8B-Embedding 嵌入、t-SNE 可视化：四环境全部出现**分布漂移**——WebShop/DeepSearch 各期失败形成紧凑簇且高密度中心大幅移动；ALFWorld/SciWorld 分布更分散但密度质心仍在迁移。

**冻结 critic 消融**（其余不动只冻 critic）：

| | WebShop | ALFWorld | SciWorld | DeepSearch |
|---|---|---|---|---|
| ECHO | 90.03 | 91.25 | 82.88 | 47.25 |
| Frozen critic | ↓ | **68.58** | ↓ | ↓ |

ALFWorld/SciWorld 最严重，**甚至低于裸 GRPO**——复杂环境里陈旧 critic 产出冗余/偏靶诊断，policy 在精炼时过度依赖噪声，反而放大长时程错误。**陈旧的反馈不是无用，是有害。**

训练曲线相位依赖：WebShop 上冻结 critic 早期看着强、后期被反超；ALFWorld/SciWorld 上 ECHO 前期与 GRPO 接近、中后期拉开。

### RQ3 · 饱和感知塑形的价值

去掉 SA 塑形（换线性 Δs）在 WebShop/SciWorld 一致掉分，WebShop 掉得更多——它更常进入近上限区。(s_o, s_r) 联合密度图：SA 塑形在改进区（s_r>s_o）尤其高分方格内集中了明显更多概率质量——**最后一公里的精炼是被 SA 奖励专门买来的**。

### 附录 C · 三组补充证据（Qwen3-4B）

**vs 其他 critique-guided 基线（Table 4）**：

| 方法 | WebShop | ALFWorld | SciWorld | DeepSearch | 总均 |
|---|---|---|---|---|---|
| RCO（训练型 critic，policy 不更新） | 35.64 | 3.00 | 16.50 | 25.75 | 20.22 |
| LUFFY（教师答案提示） | 80.34 | 80.92 | 70.44 | 31.00 | 65.18 |
| **ECHO** | **90.03** | **91.25** | **82.88** | **47.25** | **77.85** |

LUFFY 有 ground-truth 教师提示这一特权监督，ECHO 没有却更高——增益来自**自适应诊断**而非更强的外部指导。RCO 因不更新 policy 在长时程交互环境里几乎失效。

**critic 引导 vs 纯重采样（Table 5，N=8 同预算）**：

| 环境 | 阶段 | 无 critic 重采样 | critic 引导精炼 | 净增益 |
|---|---|---|---|---|
| WebShop | 早 | +0.81 | +6.54 | +5.73 |
| WebShop | 中 | +0.59 | +5.42 | +4.83 |
| WebShop | **晚** | +0.23 | **+7.54** | **+7.31** |
| SciWorld | 早 | +0.32 | +2.82 | +2.50 |
| SciWorld | 晚 | +0.34 | +3.78 | +3.44 |

排除"额外采样"的解释：同样 8 条第二轮轨迹，有 critic 的增益是无 critic 的 8–30 倍；**晚期净增益最大**——critic 随共进化越来越有用，与"冻结 critic 晚期变害"互为镜像。

**critique 粒度随训练迁移（Table 6，Gemini-2.5-pro 固定评估）**：

| 环境 | 阶段 | 问题被解决率 | 粗粒度 | 中粒度 | 细粒度 |
|---|---|---|---|---|---|
| WebShop | 早 | 74.56% | 62.42 | 24.12 | 13.46 |
| WebShop | 晚 | **95.30%** | 8.61 | 49.34 | **42.05** |
| SciWorld | 早 | 75.15% | 68.90 | 20.66 | 10.44 |
| SciWorld | 晚 | 90.02% | 11.78 | 41.50 | **46.72** |

早期 critique 以粗粒度程序性指导为主（"你没调用工具"），晚期细粒度错误定位占近半——**critic 的诊断分布跟着 policy 的失败分布走**，这是"共进化"的直接观测，也是 policy"学会听 critic"（问题被解决率 75%→95%）的原因。

**训练成本（Table 7，附录 C.4）**：共进化机制本身（critic rollout + 更新）开销边际；主要额外成本来自精炼阶段（更长上下文解码）；总墙钟比 GRPO 平均多约 **15%**。

## 6. 局限

1. **外部奖励模型 R 是房间里的大象**：critic 的全部机制建立在 R(q,τ) 上——R 冻结，ECHO 解决了 critic 陈旧，却把同样问题留给 R。WGtG 批判完全适用：policy 学会 game R 时，共进化循环会放大 hack。
2. **四个基准的 R 恰好是环境自带程序化奖励**（购物匹配度、任务完成检查），相对难 game——换到学习型 RM 场景，稳定性无证据。
3. **"critic 有害"比"critic 有用"更重要**：对所有部署静态 LLM-as-a-judge 反馈循环的系统都是警告——反馈通道不是免费加分项。
4. **成本核算只在附录**：Table 7 报告墙钟多约 15%，但没报 token 数——N=8 份诊断 + 8 条精炼意味着每步至少 16 条额外生成，墙钟 15% 是并行化后的数字，token 成本可能远高于此；且 16 × H20 的硬件配置下"15%"能否在小集群上复现未知。
5. **粒度分析依赖 Gemini-2.5-pro 做外部评估**——用一个冻结 LLM 判断另一个 LLM 的 critique 是否"细粒度"、是否"被解决"，本身有 judge 偏差；Table 6 的趋势可信，绝对数字应打折。
6. **WGtG 方法论警告**："共进化 judge 与 policy、报告 policy 涨分"正是 WGtG 证明无法验证评估器有效性的实验设计——ECHO 的 critic 有效性依赖 R 的可信度，而 R 未被审计。

## 7. 意义与位置

**证据结构最完整的部分是"漂移→冻结失效"因果链**——先用嵌入可视化证明失败分布非平稳，再用冻结消融证明非平稳让静态 critic 变害，最后用同步共进化修复。比标准"我们的方法涨了分"叙事强一档。

**Table 6 的粒度迁移是全谱系最直接的"共进化在发生"证据**：它不是"policy 涨分所以 critic 有用"的间接推断，而是 critic 输出分布本身在随 policy 失败分布移动——RQGM 的 RQ3 课程效应（报告 04）与此同构，但 RQGM 只有档案排序的 Spearman ρ，ECHO 有 critique 内容的分类。

**与 EvoLM（报告 03）**：同攻评估侧陈旧，实现层互补——EvoLM 进化显式 rubric 文本（可读、judge 冻结），ECHO 进化 critic 权重（连续、与 policy 锁步）。

**与 RQGM（报告 04）**：RQGM 在 harness/代码层管理评估器演化（epoch 冻结 + 锚定晋升），ECHO 在权重层直接同步——RQGM 有跨 epoch 统计保证但适应慢，ECHO 适应快但无 critic 改进的外部锚。

**与 Weng / Anthropic**：ECHO 是"反馈质量"在权重层的极端实现；Anthropic"执行已快、判断是瓶颈"的对照里，ECHO 展示判断能力（诊断）本身也能被训练——在窄域、R 可信的前提下。
