# RHO 深度解读：在黑暗中进化——无任何外部评分的 harness 优化，单轮 SWE-Bench Pro 59%→78%

> **RHO: Retrospective Harness Optimization from Unlabeled Trajectories**
> arXiv 2606.05922 v3（2026-06 首发，v3 2026-08-29）· 香港城市大学 + 微软亚洲研究院（Wenbo Pan、Shujie Liu、Chin-Yew Lin、Jingying Zeng、Xianfeng Tang、Xiangyang Zhou、Yan Lu、Xiaohua Jia）
> 代码 / 项目页：github.com/wbopan/retro-harness · paper-rho.wenbo.io
> 归档：`papers/en/2606.05922_RHO.pdf`

---

## 1. 一句话定位

harness 优化方法几乎都需要带 ground truth 的验证集（Meta-Harness、AutoSaddler、Self-Harness 全部如此），而部署场景里这种标注数据很难拿到——你有的只是过去的轨迹。RHO（Retrospective Harness Optimization）只用历史：用行列式点过程（DPP）从历史里选一个**困难且多样**的任务 coreset，并行重解 G 次，让 agent 用**自验证**（轨迹内能否确认自己的结果）与**自一致性**（G 条轨迹间是否分歧）诊断失败并写改进指令，best-of-N 生成候选 harness（Skills + Tools），再用 agent 自己的**成对自偏好**选最优者。单轮把 **SWE-Bench Pro 从 59% 提到 78%**（Terminal-Bench 2 71→76、GAIA-2 29→37），全程没有任何外部评分；与需要标签的 Meta-Harness 对比：匹配算力单轮 Meta-Harness 只有 0.62，十轮 0.80 但花 **3.1×** 算力且仍需标签。它是对"评估器瓶颈"最激进的回答——**不要外部评估器**，用组内相对信号替代——与 Who Grades the Grader（报告 05）的锚定路线、EvalCEGAR（报告 24）的锚驱动路线形成对极。但作者自列的局限 (4) 是全文最关键的一句：**只评估了单轮**，不声称多轮增益会累积甚至保持单调——WGtG 的塌缩结论是关于多轮动态的，RHO 的多轮实验将是对锚定纪律最直接的检验。

## 2. 要解决的问题

论文的中心问题一句话："**只有过去的轨迹、没有标签时，能不能改进 harness 以提升未来表现？**"

三个现实约束：
1. **标签稀缺**：部署系统有海量轨迹（用户会话、任务日志），但几乎没有 ground truth——没人给每次会话打对错；
2. **验证集会漂移**：即使有验证集，部署分布随时间变，验证集过时；
3. **既有方法全部依赖验证反馈**：Meta-Harness 读全历史但选候选靠搜索集分数；AutoSaddler 靠 dev 门；Self-Harness 靠双 split 通过率——去掉标签，这些方法的选择机制全部失效。

RHO 的假设：**agent 自己知道自己什么时候做得不好**——轨迹内它能验证（跑测试、检查输出），轨迹间它能对比（同一任务 G 次解法分歧说明不稳定）。这两个信号不需要标签，且能定位"harness 该改哪里"。

## 3. 为什么此前做不通：三条线各差一块

| 已有路线 | 有什么 | 缺什么 |
|---|---|---|
| Meta-Harness（报告 13） | 全历史 + 前沿 proposer | **搜索集分数**选候选；需标签；多轮烧算力 |
| AutoSaddler（报告 16） | mini-batch + dev 门 | **dev 集**是泛化门；消融显示无 dev 门为负收益 |
| Self-Harness（报告 14） | 双 split 回归门 | **held-in/held-out 通过率**；需 verifier |
| Dynamic Cheatsheet / ReasoningBank / Sleep-time Compute | 从轨迹积累记忆/技能，无标签 | 只**积累**不**优化**——把经验存下来，不选哪个 harness 更好；增益 ≤ +0.05 |
| 自一致性（Wang et al.）| 多次采样投票 | 用于**推理时**选答案，不用于选 harness |
| WGtG（报告 05） | 证明无锚不可验证 | 规范性结论，不给无锚场景的可行方案 |

关键缺口：**没有人用 agent 的自偏好做 harness 选择器**。记忆类方法有"无标签"但没有"选择"——它们把所有经验都存，RHO 在 N 个候选 harness 里挑。

## 4. 方法机制（Algorithm 1，单轮）

### 4.1 阶段 1 · Coreset 选择（DPP）

历史轨迹里大多是平凡任务，直接重放浪费预算。RHO 要求 coreset **同时困难且多样**：用 DPP 核 L 对轨迹排序——难度项（此前失败或低置信）与多样性项（覆盖不同失败模式的嵌入距离）按 θ 加权；DPP-Greedy 选 k 条。消融（§6.2）：只按难度（θ=1）、只按覆盖（θ=0）、随机采样都劣于 DPP 混合。

### 4.2 阶段 2 · 组 rollout 与自诊断

对 coreset 每个任务并行重解 G 次。两路信号：
- **自验证**（self-validation）：单条轨迹内部 agent 能否确认自己的结果——跑了测试没有、输出是否被检查；
- **自一致性**（self-consistency）：G 条轨迹之间是否分歧——低一致性通常意味着任务对当前 harness 而言不稳定。

agent 据此写出改进指令 I_t，跨任务合并为诊断摘要。

### 4.3 阶段 3 · Best-of-N 提案 + 自偏好选择

harness 优化本身是随机的，即便输入信号有效也可能不涨。RHO 并行生成 N 个候选 harness，每个都在 coreset 上重跑得到新轨迹，然后对每个任务让 agent 把"新轨迹 vs 原 harness 的旧轨迹"做**成对排序**，跨任务聚合出偏好分，取最高者。整个过程不读任何 ground-truth 标签。

### 4.4 harness 表面

编辑对象是 **Skills + Tools**：Skills 记录此前导致失败的 grader / 环境特异性（例如某个基准的验收习惯）；Tools 是可执行的辅助程序（例如修复-验证工具）。

## 5. 实验结果全景

### 5.1 主结果（Table 1，held-out 通过率，Codex 风格 CLI agent + GPT-5.5）

| 方法 | 编辑表面 | 需标签 | SWE-Bench Pro | Terminal-Bench 2 | GAIA-2 |
|---|---|---|---|---|---|
| Vanilla Codex | 无 | – | 0.59 | 0.71 | 0.29 |
| Dynamic Cheatsheet | Skills | 否 | 0.62 | 0.73 | 0.30 |
| ReasoningBank | Memory | 否 | 0.61 | 0.73 | 0.28 |
| Sleep-time Compute | Memory | 否 | 0.64 | 0.73 | 0.32 |
| **RHO** | Skills + Tools | **否** | **0.78（+0.19）** | **0.76（+0.05）** | **0.37（+0.08）** |

三个记忆/技能类基线的增益都在 +0.05 以内，RHO 在 SWE-Bench Pro 上一轮 +0.19。

### 5.2 vs Meta-Harness（Table 2，SWE-Bench Pro）

| 方法 | 验证标签 | Agent 调用（相对 RHO） | 通过率 |
|---|---|---|---|
| **RHO** | **无** | 103（1.0×） | **0.78** |
| Meta-Harness（1 轮） | 需要 | 41（0.4×） | 0.62 |
| Meta-Harness（10 轮） | 需要 | 320（3.1×） | 0.80 |

Meta-Harness 十轮才超过 RHO 单轮 2 个点，且花 3.1× 算力、仍依赖 held-out 标签。

### 5.3 诊断消融（Table 4）

| 变体 | SWE Pro | TB 2 | GAIA-2 |
|---|---|---|---|
| **完整诊断** | **0.78** | **0.76** | **0.37** |
| − 自一致性 | **0.56** | 0.75 | 0.27 |
| − 自验证 | 0.70 | 0.73 | 0.30 |
| 原始轨迹（跳过诊断） | 0.60 | 0.75 | 0.29 |

**去自一致性在 SWE-Bench Pro 上跌到 0.56——低于未优化基线 0.59**。跨轨迹分歧是最关键的诊断信号；只给原始轨迹不做诊断几乎没有收益（0.60）。TB2 对诊断不敏感——它的增益来自程序化 playbook 而非工具。

### 5.4 Best-of-N 的价值（Table 3，N=3）

| 数据集 | 均值（随机选） | RHO 选中 | 最低 |
|---|---|---|---|
| SWE-Bench Pro | 0.79 | 0.78 | 0.73 |
| TB2 | 0.74 | 0.76 | 0.71 |
| GAIA-2 | 0.34 | 0.37 | 0.32 |

自偏好选择在 TB2/GAIA-2 上选到了高于均值的候选，SWE-Bench Pro 上略低于均值（0.78 vs 0.79）——**自偏好是弱选择器**，主要价值是避开最差候选（0.73）。

### 5.5 行为分析（§6.1）

增益主要来自**长时程任务**——短任务本来就能做对。SWE-Bench Pro 上优化后 agent **验证行为大幅增加**（主动跑测试）；GAIA-2 上新环境 helper 每任务运行约 20 次；**TB2 是例外**——生成的脚本从未被执行，增益来自写进指令的程序化 playbook——RHO 按环境调整 harness 表面，不总是加可执行工具。

## 6. 局限

**作者自列五条**：
1. 组 rollout 要求环境可干净重置、容忍重复尝试——一次性或不可逆任务不在覆盖范围；
2. 预设 agent 能力的相当部分由可编辑 harness 中介；
3. 单一骨干与框架（GPT-5.5 Codex CLI），迁移性未验证；
4. **只评估了单轮**，不声称多轮增益会累积甚至保持单调；
5. 优化后的 harness 适应了各自的基准环境（例如针对某基准的修复-验证工具）。

**本调研补充**：
6. **自偏好是已知偏差源**：LLM judge 的自偏好、位置、冗长偏差在文献里被反复记录（EvalCEGAR 报告 24 开篇即引），RHO 把这个偏差源当作唯一选择信号——单轮有效不等于它不会在多轮里放大成系统性漂移。Table 3 已显示自偏好在 SWE-Bench Pro 上选到了略低于均值的候选。作者自己的局限 (4) 恰好把最关键的问题留给了未来。
7. **"无外部评分"的边界值得追问**：Skills 里记录的是"grader 特异性"——harness 学到的部分内容是**关于评估器的知识**。这在部署上合理，在方法论上意味着增益里混有"更懂考官"的成分；held-out split 能隔离任务泄漏，隔离不了 grader 泄漏。
8. **N=3 太小**：best-of-N 的收益上限没有探索。

## 7. 意义与位置

**对报告 05 锚定纪律的最强反例候选**：Who Grades the Grader 说无锚则塌缩与进化不可区分，RHO 说单轮 +0.19 不需要锚。两者并不矛盾——WGtG 的结论是关于**多轮**动态的，RHO 只测了单轮；且 RHO 的"验证"仍是 held-out 通过率（作者用了标签来**报告**结果，只是不用标签来**选择**）。RHO 的多轮实验将是对锚定纪律最直接的检验：如果多轮保持单调，insight 2 需要修正为"无锚不**可验证地**进化"；如果不保持，它就是 insight 2 最干净的实证。

**与 AutoSaddler（报告 16）的关键对照**：AutoSaddler 的消融显示去掉 dev 集泛化门后自动优化跌破未优化基线（50.6 vs 53.0），RHO 则宣称完全不用 dev 集也能 +0.19——差异可能在 RHO 的 best-of-N 自偏好选择起了"软泛化门"的作用（Table 3 显示它至少避开了最差候选），也可能在单轮与多轮的区别。**这是当前谱系里最需要被复现裁决的分歧。**

**与 EvalCEGAR（报告 24）的对极**：同一时期、同一问题（评估器稀缺），两种答案——最大化利用稀缺的锚 vs 完全不用锚。就实用性而言 RHO 的部署门槛更低；就可审计性而言 EvalCEGAR 的每个算子都能被读和证伪，RHO 的自偏好判断则是黑箱。

**与 Meta-Harness（报告 13）**：RHO 用 1/3 算力、无标签达到 Meta-Harness 十轮的 97%——但 Meta-Harness 的优势在多轮持续爬升，RHO 只证明了单轮。两者的 harness 表面也不同：Meta-Harness 改整个 Python 程序，RHO 只改 Skills + Tools。

**与 ECHO（报告 06）**：ECHO 的 critic 靠外部 R 冻结锚定；RHO 的诊断靠自一致性——都是"policy 自己的分歧"作信号，但 ECHO 有 R 兜底，RHO 没有。去自一致性后 RHO 跌破基线（0.56 < 0.59），说明这个信号是承重的。

**对报告 10 insight 2（无锚不进化）的压力测试**：RHO 是目前唯一声称完全无标签的 harness 优化，其多轮结果将决定 insight 2 的表述。
