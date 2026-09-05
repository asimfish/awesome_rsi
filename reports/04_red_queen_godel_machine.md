# Red Queen Gödel Machine 深度解读：评估器可以进循环，但锚必须留在外面

> **The Red Queen Gödel Machine: Co-Evolving Agents and Their Evaluators**
> arXiv 2606.26294 v2（2026-06-29，preliminary preprint）· 剑桥 CaMLSys + NVIDIA + Flower Labs + MBZUAI + Inria（Nicholas Lane 组）
> 命名：Van Valen 红皇后假说——物种必须不断适应才能维持相对于共进化竞争者的适存度
> 归档：`papers/en/2606.26294_RedQueenGodelMachine.pdf`

---

## 1. 一句话定位

DGM / HGM / HyperAgents 把 SWE-bench、单元测试、人工标注集当作**整场搜索中永远不变的外部尺子**——这在进化论里相当于"物种适应一个静止环境"。RQGM 把评估器本身放进搜索循环：任务 agent 与评估器共居一个可进化代码库，meta-agent 可同时改两边；搜索按 **epoch** 组织，epoch 内尺子冻结（每个 epoch 就是一个固定准则搜索问题，HGM 的收敛保证逐 epoch 直接适用），epoch 边界处挑战者评估器只有在**固定的 ground-truth 锚数据集**上以 ε-best-belief 统计优于在位者才能上位，随后**选择性擦除**只删除依赖被替换评估器的效用记录。Polyglot 编码 held-out 通过率 **71.7% vs HGM-H 69.9%**，且用 **1.35×–1.72× 更少 token**；论文写作四评审 panel 平均接受率 **40.5% vs 21.8%（1.86×）**；证明 grading 精度比静态基线高 **9%**，搜索成本比 HGM-H 低 **3×**。但它没有消除锚：所有跨 epoch 保证最终悬挂在那个**不进化、不共居、人工构造**的锚数据集上——与 WGtG 的"锚定纪律"殊途同归。

## 2. 要解决的问题

三条结构性约束让"静止评估器"成为 harness 自改进的天花板：

1. **无客观基准的域**：论文写作没有 ground truth，证明写作没有，只有 reviewing / grading 有锚——静态基准无法覆盖"可维护性""论证完整性"这类基准测不到的信号。
2. **评估慢或弱信息**：多轮 agent 执行做验证太贵；单次 agent-as-a-judge 调用便宜得多，但 judge 本身若不动就会 stale。
3. **静态基准饱和与 reward hacking**：DGM 在 SWE-bench 上出现的伪造日志、绕过检测，根源之一是评估器是静止靶——policy 可以专门学会骗过固定检查。

RQGM 的命题因此不是"让评估器自由进化"，而是：**在非平稳效用下，怎样保留自改进保证？** 答案是把"动"限制在 epoch 边界，把"不动"限制在锚数据集——评估器可以在 epoch 之间变严、变便宜、加对抗目标，但 epoch 内必须 stationary。

## 3. 为什么此前做不通：三条线各差一块

| 已有路线 | 有什么 | 缺什么 |
|---|---|---|
| DGM / HGM / HyperAgents | 源码级自改写 + 档案搜索 + ε-best-belief 选优 | **效用函数整场搜索不变**；评估器在循环外、人类设计 |
| EvoLM | rubric generator 与 policy 共进化 | judge **K=50 步内冻结**；rubric 文本层，非 harness 代码 |
| ECHO | critic 权重与 policy 同步 GRPO | **无跨 epoch 统计保证**；锚是冻结的环境奖励 R |
| WGtG | 锚定纪律 + 否定性结论（任务分不能验证 judge） | 不碰 harness 源码层；十条锚的稀疏设定 |
| MOSS | 生产失败批次替代全局基准 | 不做种群搜索；批次即局部评估器 |

关键缺口是第二行与第三行之间：**HGM 有收敛保证但尺子不动；ECHO 尺子跟 policy 一起动但没有"尺子改好了"的外部证据。** RQGM 试图用 epoch 冻结 + 锚定晋升把两边接上——代价是 epoch 边界之外必须再挂一层人工锚。

## 4. 方法机制

### 4.1 谱系与四点修改

沿用 HGM 树搜索骨架（档案节点、clade 元生产力 CMP 做 Thompson 采样、ε-best-belief 选最终 agent），做四点修改：

1. 每个档案节点从单 agent 变成**多角色共享工作区**（任务 agent + 评估器共居一个可进化代码库）；
2. 评估器本身是**可学习的 agentic 过程**（不是固定脚本）；
3. 效用函数可在指定的进化 epoch 变化；
4. 评估器可在 epoch 边界被替换。

数据隔离比 DGM 时代收紧：meta-agent 看训练结果指导自我修改，节点选择只由验证集评估驱动，最终报告用独立测试集——防记忆化。

### 4.2 受控效用进化（理论承重件）

**Epoch 内有效性（Prop. 3）**：epoch 内评估器、产物生成协议、二值评分规则全部冻结 → 每个 epoch 是固定准则搜索问题 → HGM 的 per-epoch 收敛保证直接适用。

**锚定改进（Prop. 4, Rem. 3）**：挑战者只有在评估器无关的 ground-truth 锚（CRAVE PR 接受/拒绝、APReS 人类决定、IMO-GradingBench 人类评分）上把 ε-best-belief 分数（Beta 后验的 ε 分位数）抬高才被晋升；平局偏向在位者以避免不必要的擦除。评估器跨 epoch 也在改进，不只是 epoch 内。

**选择性擦除 + 摊销转换成本（Prop. 6, Rem. 7）**：替换时不立即重排全档案，而是懒惰重评——后续评估回到旧节点时才用新评估器重打分。保留旧分数或把旧分数缩放到新评估器上，都会混合不同效用函数的证据、破坏 epoch 内平稳性。**no-erasure control** 显示不擦除时搜索被钉死在被废评估器的排序上，新准则永远无法重排档案。指数间隔 checkpoint 使暴露于擦除/重评的记录数只随预算线性增长 O(B)，而不是每步都允许转换的 O(B²)。

### 4.3 三域锚定设计

- **编码（Polyglot）**：测试执行 + 共进化 code reviewer；reviewer 锚定 CRAVE 真实 PR 数据集；reviewer 单次调用、比多轮执行便宜。
- **论文写作/评审**：writer 无锚（只有 epoch-local 赢家）；reviewer 锚 APReS；最强 baseline reviewer 对 AI 生成论文接受率达人类的 **1.42×–1.91×**——RQGM 用 epoch 边界对抗目标：被废评审员曾接受的 AI 论文形成对抗池，下一 epoch 额外奖励拒绝这些论文。
- **证明写作/grading**：prover 无锚；grader 锚 IMO-GradingBench；7/7 满分算通过。

## 5. 实验结果全景

**设置**：GPT-5.5 low 做 meta-agent；三域四个 RQ；作者自称 preliminary，proof 域 88M token，SWE-bench 因运行时长被排除。

### RQ1 · 有 ground truth 的域，学习型评估器依然有用（Polyglot）

共进化 agent-as-a-judge code reviewer 作为测试执行的**补充信号**：held-out 通过率 **71.7% vs HGM-H 69.9%**，**1.35×–1.72× 更少 token**。机制：90% 被接受补丁修改的是 coder 和 reviewer **共享**的基础设施代码——一次编辑同时改善两个角色，共进化在**丰富搜索**而不是分裂预算。Fig. 1 右图：每次 evaluator replacement 效用先因 selective erasure 下跌，再在新 epoch 下爬升。

### RQ2 · 无客观基准的域

**论文写作（Tab. 1）**：四评审 panel 平均接受率——HGM-H writer **21.8%**；RQGM generalist **38.8%（1.78×）**；RQGM specialist **40.5%（1.86×）**。Panel 含 Sakana、DGM-H、HGM-H、RQGM adversarial 四个评审员；最强 writer 正是对抗评审员训出来的。

**证明写作（Tab. 2）**：RQGM specialist 均分 **4.33** vs 静态 IMO25 **4.07** vs HGM-H **3.73**；Pass@6 **61.7%** 最高；Pass@7 **48.3%** 仍输 IMO25 **55.0%**——RQGM 靠更多 6/7 近完整证明赢均分，严格全对率还差，作者归因搜索预算。HGM-H 在长时程后停滞（冻结 grader 不再提供信息量）。

**效率**：搜索期任务 agent 调用换成 Nemotron 3 Ultra（meta-agent 保持 GPT-5.5），价格等效 token 省 **~13×** 而终评精度接近。

### RQ3 · 评估器替换对搜索施加课程效应

Fig. 3：每次 replacement 后 Spearman ρ 永久停在擦除后的新水平，不回弹旧序——后继评估器执行更严准则。档案证据集中在少数骨干谱系；每次转换把被旧准则压低的谱系拉回竞争，但最优谱系跨转换保持韧性——课程围绕稳定骨干抬升种群，不是每次转换推倒重来。

### RQ4 · 共进化改善评估器本身（论文最有信息量的部分）

**证明 grader**（有参考解，自偏好空间小）：纯共进化就够——IMO-GradingBench 精度最高（+9%），搜索成本 **3×** 低于 HGM-H，无需对抗目标。

**论文 reviewer**（无参考答案，LLM 自偏好偏差）：HGM-H 过度接受 AI 论文；APReS 的接受/拒绝平衡奖励**宽松评审**——偏差与原始精度同向，静态精度指标反而掩护偏差。RQGM 对抗修正：原始 APReS 精度按构造下降，收益是**校准**——对 AI 与人类论文接受率相近、保住 80% ground-truth 精度。对抗池来自共进化结构本身——被废评估器接受的 AI 产物——单独训练评估器时这个修正**不免费可得**。

## 6. 局限

1. **锚是阿喀琉斯之踵**：跨 epoch 保证悬挂在固定 ground-truth 锚上——锚不进化、不受污染、代表真实目标，三个假设在长时程下逐一变弱（锚饱和、档案间接过拟合、APReS 本身带宽松偏差）。
2. **"preliminary" 要当真**：搜索时程短、SWE-bench 被排除、v2 与 v1 相隔仅数周；RQ3 课程效应基于图形证据，样本量不支持强结论。
3. **对抗修正的一般化**：依赖"被废评估器接受过的 AI 产物"——只在生成器-评估器共居搜索里天然存在。
4. **与 WGtG 的合读**：RQGM 展示锚定下评估器进化能带来什么；WGtG 证明无锚时任务分与塌缩不可区分——两篇合读才是完整论证。
5. **没有回答"评估器的评估器"**：只是把答案推给更小、更慢变的人工数据集。

## 7. 意义与位置

**六篇核心里的理论姿态最完整的一篇**：不是"我们让评估器动了"，而是"评估器可以动，但动的自由度被三条机制约束"——把 Gödel Machine 谱系"证明有益才修改"的精神翻译到了评估器层。

**与 EvoLM 的对照**：EvoLM 连续交替 + judge 冻结，RQGM 离散 epoch + judge 可替换但锚冻结——两者都没有让"最后一层尺子"动起来。2026 评估侧进展可以总结为：**共进化的自由度在上移，但每上移一层，就需要一个新的更外层冻结物。**

**与其他材料的连线**：
- 直接续 **DGM**（报告 07）：DGM 固定 SWE-bench，RQGM 指出 hack 行为的结构根源之一是评估器静止。
- 与 **ECHO**（报告 06）：RQGM 在 harness/代码层，ECHO 在权重层——同一原理的两个实现层；RQGM 适应慢但有跨 epoch 统计保证，ECHO 适应快但锚是冻结 R。
- 呼应 **Weng** 挑战 4（评估瓶颈）与 **Anthropic**"研究品味是最后瓶颈"——在 RQGM 这里具体化为锚数据集的构造品味。
