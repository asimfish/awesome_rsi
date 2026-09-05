# Red Queen Gödel Machine 深度解读：按阶段更新评估器，用固定锚数据验证改进

> **The Red Queen Gödel Machine: Co-Evolving Agents and Their Evaluators**
> arXiv 2606.26294 v2（2026-06-29，preliminary preprint）· 剑桥 CaMLSys + NVIDIA + Flower Labs + MBZUAI + Inria（Nicholas Lane 组）
> 命名：来自 Van Valen 的红皇后假说，即物种必须不断适应才能维持相对于共进化竞争者的适存度
> 归档：`papers/en/2606.26294_RedQueenGodelMachine.pdf`

---

## 1. 一句话定位

DGM / HGM / HyperAgents 在整个搜索过程中固定使用 SWE-bench、单元测试或人工标注集作为外部评估依据。RQGM 将评估器纳入搜索循环，任务 agent 与评估器共享可进化的代码库，meta-agent 可以同时修改两者。搜索按 epoch 进行，epoch 内冻结评估器；每个 epoch 因此都是固定准则的搜索问题，HGM 的收敛保证可逐 epoch 适用。只有在 epoch 边界，候选评估器在固定 ground-truth 锚数据集上的 ε-best-belief 统计优于当前评估器，才允许替换；随后只删除依赖旧评估器的效用记录。

Polyglot 编码的 held-out 通过率为 71.7% vs HGM-H 69.9%，token 用量少 1.35×–1.72×。论文写作的四评审 panel 平均接受率为 40.5% vs 21.8%（1.86×）；证明 grading 精度比静态基线高 9%，搜索成本比 HGM-H 低 3×。这些跨 epoch 保证仍依赖人工构造的固定锚数据集，锚不参与进化，也不放在共享代码库中。WGtG 同样要求在进化循环外保留锚。

## 2. 要解决的问题

固定评估器从三个方面限制 harness 自改进：

1. **缺少客观基准的领域**：论文写作和证明写作没有 ground truth，只有 reviewing / grading 有锚。静态基准难以覆盖可维护性、论证完整性等评估信号。
2. **评估缓慢或信息不足**：通过多轮 agent 执行来验证结果，成本较高。单次 agent-as-a-judge 调用便宜得多，但 judge 若保持不变，反馈就会 stale。
3. **静态基准饱和与 reward hacking**：DGM 在 SWE-bench 上出现过伪造日志、绕过检测的行为。原因之一是评估器不变，policy 可以专门学习如何骗过固定检查。

RQGM 研究的是效用变化后，如何保留自改进的保证。它只允许在 epoch 边界更新评估器，同时固定锚数据集。评估器可以在 epoch 之间提高标准、降低成本或增加对抗目标，但 epoch 内必须保持 stationary。

## 3. 为什么此前做不通：三条线各差一块

| 已有路线 | 有什么 | 缺什么 |
|---|---|---|
| DGM / HGM / HyperAgents | 源码级自改写 + 档案搜索 + ε-best-belief 选优 | **效用函数整场搜索不变**；评估器在循环外、人类设计 |
| EvoLM | rubric generator 与 policy 共进化 | judge **K=50 步内冻结**；rubric 文本层，非 harness 代码 |
| ECHO | critic 权重与 policy 同步 GRPO | **无跨 epoch 统计保证**；锚是冻结的环境奖励 R |
| WGtG | 用锚约束更新；证明任务分不能验证 judge | 不修改 harness 源码；只使用十条锚 |
| MOSS | 生产失败批次替代全局基准 | 不做种群搜索；批次即局部评估器 |

这些方法尚未同时解决评估器更新与收敛保证的问题。HGM 有收敛保证，但评估器固定；ECHO 的评估器随 policy 更新，却缺少证明评估器改善的外部证据。RQGM 在 epoch 内冻结评估器，并用锚验证替换条件，以结合两者；这仍要求在 epoch 边界之外保留人工锚。

## 4. 方法机制

### 4.1 谱系与四点修改

方法沿用 HGM 树搜索：保存档案节点，按 clade 元生产力 CMP 做 Thompson 采样，用 ε-best-belief 选择最终 agent。在此基础上作四点修改：

1. 每个档案节点由单 agent 扩展为多个角色共享的工作区，任务 agent 与评估器使用同一个可进化代码库；
2. 用可学习的 agentic 过程实现评估器，替代固定脚本；
3. 效用函数可在指定的进化 epoch 变化；
4. 评估器可在 epoch 边界被替换。

数据隔离比 DGM 更严格。meta-agent 根据训练结果修改自身，节点选择只依据验证集评估，最终结果使用独立测试集，以避免靠记忆测试内容获得提升。

### 4.2 受控效用进化（理论承重件）

**Epoch 内有效性（Prop. 3）**：epoch 内冻结评估器、产物生成协议和二值评分规则。每个 epoch 因此都属于固定准则搜索问题，可以直接使用 HGM 的 per-epoch 收敛保证。

**锚定改进（Prop. 4, Rem. 3）**：候选评估器必须在独立于评估器的 ground-truth 锚上取得更高的 ε-best-belief 分数（Beta 后验的 ε 分位数），才允许替换当前评估器。锚包括 CRAVE PR 接受/拒绝、APReS 人类决定和 IMO-GradingBench 人类评分。平局时保留当前评估器，避免不必要的擦除。这样既能保证 epoch 内的改进，也能约束跨 epoch 的更新。

**选择性擦除 + 摊销转换成本（Prop. 6, Rem. 7）**：替换评估器后，等搜索再次访问旧节点时才重新打分，无需立即重排全部档案。保留旧分数，或缩放旧分数以适配新评估器，都会混合不同效用函数下的证据，破坏 epoch 内平稳性。no-erasure control 显示，不擦除旧记录时，搜索持续沿用旧评估器的排序，新准则无法重排档案。采用指数间隔 checkpoint 后，需要擦除或重评的记录数随预算线性增长，为 O(B)；若每步都允许转换，则为 O(B²)。

### 4.3 三域锚定设计

- **编码（Polyglot）**：结合测试执行与共进化 code reviewer，以 CRAVE 真实 PR 数据集约束 reviewer。reviewer 只需单次调用，成本低于多轮执行。
- **论文写作/评审**：writer 没有锚，只能确定 epoch-local 赢家；reviewer 使用 APReS 作为锚。最强 baseline reviewer 对 AI 生成论文的接受率是人类论文的 1.42×–1.91×。RQGM 在 epoch 边界引入对抗目标：将旧评审员接受过的 AI 论文加入对抗池，在下一 epoch 额外奖励拒绝这些论文的行为。
- **证明写作/grading**：prover 没有锚；grader 使用 IMO-GradingBench 作为锚；7/7 满分视为通过。

## 5. 实验结果全景

**设置**：使用 GPT-5.5 low 作为 meta-agent，在三个领域研究四个 RQ。作者将结果标为 preliminary。proof 领域使用 88M token，SWE-bench 因运行时间过长未纳入实验。

### RQ1 · 有 ground truth 的域，学习型评估器依然有用（Polyglot）

共进化的 agent-as-a-judge code reviewer 为测试执行提供补充信号。held-out 通过率为 71.7% vs HGM-H 69.9%，token 用量少 1.35×–1.72×。被接受的补丁中，90% 修改了 coder 和 reviewer 共享的基础设施代码，一次编辑可以同时改善两个角色。这让共进化在同一搜索预算内找到更多改进机会。Fig. 1 右图显示，每次 evaluator replacement 后，效用先因 selective erasure 下降，再随新 epoch 的搜索逐步提高。

### RQ2 · 无客观基准的域

**论文写作（Tab. 1）**：四评审 panel 的平均接受率分别为 HGM-H writer 21.8%、RQGM generalist 38.8%（1.78×）、RQGM specialist 40.5%（1.86×）。Panel 包含 Sakana、DGM-H、HGM-H、RQGM adversarial 四个评审员。接受率最高的 writer 使用对抗评审员训练。

**证明写作（Tab. 2）**：RQGM specialist 均分为 4.33 vs 静态 IMO25 4.07 vs HGM-H 3.73，Pass@6 为 61.7%，居各方法最高。Pass@7 为 48.3%，低于 IMO25 的 55.0%。RQGM 产生了更多得分为 6/7 的接近完整证明，因此均分更高，但严格全对率仍较低，作者将此归因于搜索预算。HGM-H 在较长时间的搜索后停滞，因为冻结的 grader 不再提供有效信息。

**效率**：搜索期间，将任务 agent 的调用模型换成 Nemotron 3 Ultra，meta-agent 仍用 GPT-5.5，价格等效 token 可节省 ~13×，最终评估精度相近。

### RQ3 · 评估器替换对搜索施加课程效应

Fig. 3 显示，每次 replacement 后，Spearman ρ 保持在擦除后的新水平，没有恢复旧排序，后继评估器采用了更严格的准则。档案证据主要集中在少数谱系。转换后，部分按旧准则得分较低的谱系重新参与竞争，原先的最优谱系仍能保持优势。评估器更新因此改变了种群的搜索方向，同时保留了已有的有效谱系。

### RQ4 · 共进化改善评估器本身（论文最有信息量的部分）

**证明 grader**：有参考解时，自偏好空间较小。仅用共进化、不加对抗目标，IMO-GradingBench 精度就达到最高（+9%），搜索成本比 HGM-H 低 3×。

**论文 reviewer**：缺少参考答案时，LLM 存在自偏好偏差。HGM-H 过多接受 AI 论文，APReS 的接受/拒绝比例也会奖励宽松评审，因此更高的静态精度可能伴随更大的偏差。RQGM 引入对抗修正后，原始 APReS 精度按设计下降，但校准得到改善：对 AI 与人类论文的接受率相近，同时保留 80% ground-truth 精度。对抗池由旧评估器接受过的 AI 产物构成，来自共进化过程；单独训练评估器时，无法直接获得这些样本。

## 6. 局限

1. **保证依赖固定锚**：跨 epoch 保证要求 ground-truth 锚保持不变、不受污染，并代表真实目标。长时间搜索会削弱这些假设：锚可能饱和，档案可能间接过拟合，APReS 本身也偏向宽松评审。
2. **结果仍属 "preliminary"**：搜索时间较短，未纳入 SWE-bench，v2 与 v1 仅相隔数周。RQ3 的课程效应主要依据图形证据，样本量不足以支持较强结论。
3. **对抗修正的适用范围**：该方法依赖旧评估器接受过的 AI 产物。只有生成器与评估器共同参与搜索时，过程本身才会产生这些样本。
4. **需结合 WGtG 判断结果**：RQGM 展示了用锚约束评估器进化的收益，WGtG 则证明，去掉锚后，仅凭任务分数无法区分评估器塌缩与有效进化。两篇分别讨论了有锚和无锚的情况。
5. **仍未解决如何评估评估器的问题**：方法最终依赖规模更小、更新更慢的人工数据集，尚未解释如何验证这层评估依据。

## 7. 意义与位置

**论文为评估器更新给出了理论约束**：它用三条机制限制评估器的修改范围，将 Gödel Machine 要求确认修改有益后才执行的思路用于评估器。

**与 EvoLM 的对照**：EvoLM 连续交替训练并冻结 judge；RQGM 按离散 epoch 更新，judge 可以替换，但锚固定。两者都保留了不参与进化的最终评估依据。2026 年的相关工作允许更多层级参与共进化，同时也需要在更外层保留固定的评估依据。

**与其他材料的关系**：

- 延续 **DGM**（报告 07）：DGM 固定使用 SWE-bench，RQGM 指出评估器固定是 hack 行为的原因之一。
- 与 **ECHO**（报告 06）采用相同原理，但实现层级不同：RQGM 修改 harness/代码，ECHO 更新权重。RQGM 适应较慢，但有跨 epoch 统计保证；ECHO 适应较快，以冻结的 R 作为锚。
- **Weng** 的挑战 4 讨论评估瓶颈，**Anthropic** 强调研究方向判断仍限制改进。RQGM 中对应的问题是，怎样构造能代表目标的锚数据集。
