# RHO 深度解读：从未标注轨迹优化 harness，单轮 SWE-Bench Pro 59%→78%

> **RHO: Retrospective Harness Optimization from Unlabeled Trajectories**
> arXiv 2606.05922 v3（2026-06 首发，v3 2026-08-29）· 香港城市大学 + 微软亚洲研究院（Wenbo Pan、Shujie Liu、Chin-Yew Lin、Jingying Zeng、Xianfeng Tang、Xiangyang Zhou、Yan Lu、Xiaohua Jia）
> 代码 / 项目页：github.com/wbopan/retro-harness · paper-rho.wenbo.io
> 归档：`papers/en/2606.05922_RHO.pdf`

---

## 1. 一句话定位

harness 优化方法几乎都需要带 ground truth 的验证集，包括 Meta-Harness、AutoSaddler、Self-Harness。部署场景很难获得这些标注数据，通常只有历史轨迹。RHO（Retrospective Harness Optimization）用行列式点过程（DPP）从历史中选出困难且多样的任务 coreset，并行重解 G 次。agent 检查单条轨迹内能否确认自己的结果，也比较 G 条轨迹间是否存在分歧。这两类信号分别称为自验证和自一致性，用于诊断失败、编写改进指令。系统再通过 best-of-N 生成候选 harness（Skills + Tools），用 agent 自己的成对自偏好选择候选。

优化过程不使用外部评分。单轮优化把 SWE-Bench Pro 从 59% 提到 78%（Terminal-Bench 2 71→76、GAIA-2 29→37）。作为对照，Meta-Harness 需要标签。在匹配算力的单轮设置下，Meta-Harness 通过率为 0.62；十轮达到 0.80，使用了 3.1× 算力，且仍需标签。

RHO 用组内相对信号替代外部评估器，Who Grades the Grader（报告 05）和 EvalCEGAR（报告 24）则依赖锚。作者在局限 (4) 中指出，只评估了单轮，不声称多轮增益会累积或保持单调。WGtG 的塌缩结论涉及多轮动态，因此仍需多轮实验检验 RHO 能否持续改进。

## 2. 要解决的问题

论文研究如何在只有历史轨迹、没有标签的情况下，改进 harness 并提升未来任务的表现。

三个现实约束：

1. **标签稀缺**：部署系统积累了大量用户会话和任务日志，但几乎没有 ground truth，通常无人逐次标注会话结果的对错；
2. **验证集会过时**：部署分布会随时间变化，已有验证集可能无法反映新的任务分布；
3. **既有方法全部依赖验证反馈**：Meta-Harness 读取完整历史，依靠搜索集分数选择候选；AutoSaddler 用 dev 集筛选；Self-Harness 用双 split 通过率判定。没有标签，这些方法的选择机制就无法运行。

RHO 假设 agent 能通过自身行为识别失败。它可以在单条轨迹内运行测试、检查输出，也可以比较同一任务 G 次解法的分歧，判断表现是否稳定。这两个信号无需标签，可用于定位 harness 需要修改的部分。

## 3. 为什么此前做不通：三条线各差一块

| 已有路线 | 有什么 | 缺什么 |
|---|---|---|
| Meta-Harness（报告 13） | 全历史 + 前沿 proposer | 用**搜索集分数**选候选，需要标签；多轮运行消耗较多算力 |
| AutoSaddler（报告 16） | mini-batch + dev 门 | 用 **dev 集**检验泛化；消融显示不经 dev 门筛选时收益为负 |
| Self-Harness（报告 14） | 双 split 回归门 | **held-in/held-out 通过率**；需 verifier |
| Dynamic Cheatsheet / ReasoningBank / Sleep-time Compute | 从轨迹积累记忆/技能，无标签 | 保存经验，但不比较和选择 harness；增益 ≤ +0.05 |
| 自一致性（Wang et al.）| 多次采样投票 | 用于**推理时**选答案，不用于选 harness |
| WGtG（报告 05） | 证明无锚不可验证 | 规范性结论，不给无锚场景的可行方案 |

这些方法尚未用 agent 的自偏好选择 harness。记忆类方法无需标签，会保存所有经验，但不筛选候选。RHO 从 N 个候选 harness 中选择一个。

## 4. 方法机制（Algorithm 1，单轮）

### 4.1 阶段 1 · Coreset 选择（DPP）

历史轨迹中大多是简单任务，直接重放会把预算花在已能完成的任务上。RHO 用 DPP 核 L 对轨迹排序，使 coreset 包含困难任务，并覆盖不同失败模式。难度项衡量此前失败或置信度低的情况，多样性项用嵌入距离衡量覆盖了哪些失败模式。两项按 θ 加权，再由 DPP-Greedy 选出 k 条。消融（§6.2）显示，只按难度（θ=1）、只按覆盖（θ=0）和随机采样都不如 DPP 混合。

### 4.2 阶段 2 · 组 rollout 与自诊断

对 coreset 中的每个任务并行重解 G 次，提取两类信号：

- **自验证**（self-validation）：检查单条轨迹内部 agent 能否确认自己的结果，包括是否运行测试、检查输出；
- **自一致性**（self-consistency）：比较 G 条轨迹之间是否存在分歧。一致性低通常意味着当前 harness 在该任务上表现不稳定。

agent 据此写出改进指令 I_t，再合并各任务的指令，形成诊断摘要。

### 4.3 阶段 3 · Best-of-N 提案 + 自偏好选择

harness 优化具有随机性，即使输入信号有效，性能也可能不提升。RHO 并行生成 N 个候选 harness，分别在 coreset 上重跑，得到新轨迹。agent 逐个任务比较"新轨迹 vs 原 harness 的旧轨迹"，给出偏好分。系统汇总各任务的偏好分，选择得分最高的候选。整个过程不读取 ground-truth 标签。

### 4.4 harness 表面

系统编辑 Skills + Tools。Skills 记录 grader 或环境中此前导致失败的特定要求，例如某个基准的验收方式。Tools 提供可执行的辅助程序，例如修复-验证工具。

## 5. 实验结果全景

### 5.1 主结果（Table 1，held-out 通过率，Codex 风格 CLI agent + GPT-5.5）

| 方法 | 编辑表面 | 需标签 | SWE-Bench Pro | Terminal-Bench 2 | GAIA-2 |
|---|---|---|---|---|---|
| Vanilla Codex | 无 | – | 0.59 | 0.71 | 0.29 |
| Dynamic Cheatsheet | Skills | 否 | 0.62 | 0.73 | 0.30 |
| ReasoningBank | Memory | 否 | 0.61 | 0.73 | 0.28 |
| Sleep-time Compute | Memory | 否 | 0.64 | 0.73 | 0.32 |
| **RHO** | Skills + Tools | **否** | **0.78（+0.19）** | **0.76（+0.05）** | **0.37（+0.08）** |

三个记忆/技能类基线的增益都在 +0.05 以内。RHO 在 SWE-Bench Pro 上单轮提升 +0.19。

### 5.2 vs Meta-Harness（Table 2，SWE-Bench Pro）

| 方法 | 验证标签 | Agent 调用（相对 RHO） | 通过率 |
|---|---|---|---|
| **RHO** | **无** | 103（1.0×） | **0.78** |
| Meta-Harness（1 轮） | 需要 | 41（0.4×） | 0.62 |
| Meta-Harness（10 轮） | 需要 | 320（3.1×） | 0.80 |

Meta-Harness 十轮的通过率比 RHO 单轮高 2 个点，使用了 3.1× 算力，仍依赖 held-out 标签。

### 5.3 诊断消融（Table 4）

| 变体 | SWE Pro | TB 2 | GAIA-2 |
|---|---|---|---|
| **完整诊断** | **0.78** | **0.76** | **0.37** |
| − 自一致性 | **0.56** | 0.75 | 0.27 |
| − 自验证 | 0.70 | 0.73 | 0.30 |
| 原始轨迹（跳过诊断） | 0.60 | 0.75 | 0.29 |

去掉自一致性后，SWE-Bench Pro 通过率降到 0.56，低于未优化基线 0.59。这是上述消融中降幅最大的一项。只给原始轨迹、不做诊断时，收益也很小（0.60）。TB2 对诊断不敏感，增益来自程序化 playbook，工具没有贡献。

### 5.4 Best-of-N 的价值（Table 3，N=3）

| 数据集 | 均值（随机选） | RHO 选中 | 最低 |
|---|---|---|---|
| SWE-Bench Pro | 0.79 | 0.78 | 0.73 |
| TB2 | 0.74 | 0.76 | 0.71 |
| GAIA-2 | 0.34 | 0.37 | 0.32 |

自偏好选择在 TB2/GAIA-2 上选到了高于均值的候选。SWE-Bench Pro 上选中的候选略低于均值（0.78 vs 0.79），该机制主要起到避开最差候选（0.73）的作用。

### 5.5 行为分析（§6.1）

增益主要来自长时程任务，短任务在优化前就已能做对。SWE-Bench Pro 上，优化后的 agent 更频繁地主动运行测试等验证操作。GAIA-2 上，新增的环境 helper 每个任务运行约 20 次。TB2 中生成的脚本从未执行，增益来自写入指令的程序化 playbook。RHO 在不同环境中改动的 harness 部分不同，可执行工具只在部分环境中发挥作用。

## 6. 局限

**作者自列五条**：

1. 组 rollout 要求环境能重置到初始状态，并允许重复尝试，因此不适用于一次性或不可逆任务；
2. 方法假设 agent 有相当一部分能力受可编辑 harness 影响；
3. 单一骨干与框架（GPT-5.5 Codex CLI），迁移性未验证；
4. **只评估了单轮**，不声称多轮增益会累积甚至保持单调；
5. 优化后的 harness 适应了各自的基准环境（例如针对某基准的修复-验证工具）。

**本调研补充**：

6. **自偏好是已知偏差源**：文献多次记录了 LLM judge 的自偏好、位置和冗长偏差，EvalCEGAR 报告 24 开篇也引用了这些结果。RHO 将自偏好作为唯一选择信号。单轮有效尚不能排除偏差在多轮中累积、造成系统性漂移的可能。Table 3 已显示，RHO 在 SWE-Bench Pro 上选到了略低于均值的候选。作者在局限 (4) 中也承认，尚未验证多轮效果。
7. **"无外部评分"的边界仍需澄清**：Skills 记录了 grader 的具体要求，harness 学到的部分内容因此与评估器有关。这在部署中合理，但部分增益来自对评估器的适应。held-out split 能隔离任务泄漏，无法隔离 grader 泄漏。
8. **N=3 太小**：实验尚未探索 best-of-N 的收益上限。

## 7. 意义与位置

**对报告 05 锚定纪律的最强反例候选**：Who Grades the Grader 认为，无锚时无法区分塌缩与进化。RHO 报告了不依赖锚的单轮 +0.19 增益。WGtG 讨论多轮动态，RHO 只测了单轮，两者尚不矛盾。RHO 选择候选时不使用标签，报告效果时仍用带标签的 held-out 通过率验证结果。多轮实验可以检验锚是否必要。如果多轮保持单调，insight 2 需要修正为"无锚不可验证地进化"；如果无法保持，则为 insight 2 提供实证。

**与 AutoSaddler（报告 16）的关键对照**：AutoSaddler 的消融显示，去掉 dev 集泛化门后，自动优化的结果低于未优化基线（50.6 vs 53.0）。RHO 报告完全不用 dev 集也能提升 +0.19。best-of-N 自偏好选择可能起到了部分筛选作用，Table 3 显示它至少避开了最差候选。差异也可能来自单轮与多轮设置，需要通过复现判断具体原因。

**与 EvalCEGAR（报告 24）的对极**：两篇论文在同一时期讨论评估器稀缺问题，分别采用充分利用稀缺锚 vs 完全不用锚的方案。RHO 无需锚，部署门槛更低。EvalCEGAR 的每个算子都能阅读和证伪，便于审计。RHO 的自偏好判断无法用同样的方式审计。

**与 Meta-Harness（报告 13）**：RHO 无需标签，使用 1/3 算力，通过率达到 Meta-Harness 十轮的 97%。Meta-Harness 已展示多轮持续提升，RHO 只验证了单轮效果。两者修改的 harness 范围也不同。Meta-Harness 修改整个 Python 程序，RHO 只改 Skills + Tools。

**与 ECHO（报告 06）**：ECHO 的 critic 由冻结的外部 R 锚定；RHO 通过自一致性诊断失败。两者都使用 policy 自身的分歧作信号，但只有 ECHO 用 R 提供外部约束。去掉自一致性后，RHO 低于基线（0.56 < 0.59），表明当前方法依赖这一信号。

**对报告 10 insight 2（无锚不进化）的压力测试**：目前只有 RHO 声称可以完全不用标签优化 harness。是否需要调整 insight 2 的表述，仍取决于 RHO 的多轮实验结果。
