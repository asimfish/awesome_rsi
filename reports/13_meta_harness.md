# Meta-Harness 深度解读：让 coding agent 根据完整执行轨迹修改 harness

> **Meta-Harness: End-to-End Optimization of Model Harnesses**
> arXiv 2603.28052 v1（2026-03-30）· Stanford IRIS Lab（Yoonho Lee、Roshen Nair、Qizheng Zhang、Chelsea Finn）+ KRAFTON（Kangwook Lee）+ MIT（Omar Khattab）
> 代码：github.com/stanford-iris-lab/meta-harness-tbench2-artifact · 项目页 yoonholee.com/meta-harness
> 归档：`papers/en/2603.28052_MetaHarness.pdf` · 中译 `papers/zh/2603.28052_MetaHarness_zh.pdf`

---

## 1. 一句话定位

同一模型更换 harness 后，性能可相差 **6×**，但 harness 仍主要由工程师观察失败、调整启发式并反复修改。已有文本优化器（OPRO、TextGrad、GEPA、AlphaEvolve、TTT-Discover）将反馈压缩为分数、模板或 LLM 摘要，每步只读取 **0.002–0.026 MTok**，可能丢失追溯上游 harness 决策所需的信息。harness 对存储、检索和呈现方式的选择，会影响许多步之后的行为。

Meta-Harness 将每个候选的源码、分数和原始执行轨迹全部存入文件系统，由 **coding agent proposer**（Claude Code + Opus-4.6）通过 grep/cat 自主选择材料，分析失败并决定修改位置，每轮中位读取 **82 个文件**、约 **10 MTok**。外环不预设父代选择规则或变异算子。

三个领域的结果为：在线文本分类 **48.6% vs ACE 40.9（+7.7）**，上下文节省 **4×**；IMO 级数学检索 harness 在 5 个 held-out 模型上平均 **+4.7 分**；TerminalBench-2 上，Opus 4.6 达到 **76.4%**，高于手工 Terminus-KIRA 的 74.7%，全榜第 2，Haiku 4.5 达到 **37.6%**，全榜第 1。消融中，只给分数时为 34.6/41.3，加入摘要后为 34.9/38.7，使用全轨迹为 **50.0/56.7**，其中位候选也高于两个消融的最佳候选。本文首次在正式论文中实现了 Weng 总纲提出的 meta-harness 概念。

## 2. 要解决的问题

Table 1 比较了各方法每轮读取的历史信息量：

| 方法 | 历史 | 日志内容 | MTok/轮 |
|---|---|---|---|
| OPRO | 窗口 | 过去 (solution, score) 对 | 0.002 |
| TextGrad | 最近 | 当前工件的文本反馈 | 0.015 |
| AlphaEvolve | 窗口 | 程序库 + 评估分 | 0.022 |
| GEPA | 摘要 | rollout 轨迹的反思反馈 | 0.008 |
| Feedback Descent | 摘要 | 对比 + 文本反馈 | 0.012 |
| TTT-Discover | 窗口 | 前一解的片段 | 0.026 |
| **Meta-Harness** | **全部** | **全部日志与分数** | **10.0** |

三个数量级的差距与任务结构有关。harness 在**代码空间**中优化，检索、记忆和 prompt 构造逻辑的小改动，可能经过许多推理步才显现效果，局部搜索启发式难以处理这种依赖。作者认为，既有优化器压缩反馈是为了控制成本和扩展规模，不能据此判断长程依赖没有信息价值。

另一个问题是**如何读取这些信息**。10 MTok 远超单个上下文窗口，proposer 需要由 **coding agent** 担任，自主选择材料，并直接操作代码库验证编辑，单次 LLM 调用无法完成。作者说明，这一工作流直到 2026 年初 coding agent 能力提高后才变得可行。

## 3. 为什么此前做不通：三条线各差一块

| 已有路线 | 有什么 | 缺什么 |
|---|---|---|
| 文本优化器（GEPA、OPRO、TextGrad） | 迭代修改 prompt / 文本工件 | 反馈压缩到 <0.03 MTok；只见当前候选或摘要；**无法跨候选做因果归因** |
| 程序进化（AlphaEvolve、OpenEvolve、ADAS、AFlow） | 在代码空间搜索，由 LLM 生成变异 | 在固定 scaffold 中进化指定函数，或搜索工作流图；空间预先定义，档案和父代选择由人工设计 |
| 记忆设计搜索（ACE、MCE） | 跨任务累积上下文 | 更新经验，程序保持固定；上下文随时间增加（ACE 50.8K token） |
| DGM（报告 07） | 修改自身源码、搜索档案 | 按结构化规则采样父代，每步只见自身失败；**改进者 = 被改进物**，proposer 会被 game |
| 人工 harness 工程 | 目前 SOTA（Terminus-KIRA、ForgeCode） | 不可扩展；每换一个模型都要重来 |

反馈需要与读取者的能力匹配。LLM 无法一次处理全部历史，因此需要压缩；coding agent 能通过 grep 自主检索全历史，继续压缩反而会丢失信息。Meta-Harness 据此减少预设搜索规则，将材料选择、诊断和编辑交给系统完成。

## 4. 方法机制

### 4.1 目标形式化

harness 是运行在冻结模型 M 外围的有状态程序。给定任务 x ∼ X，执行 rollout τ ∼ p_M(H, x)：harness 构造 prompt，模型生成响应，harness 再更新状态。任务奖励 r(τ, x) 用于打分，目标为：

H* = argmax_H E_{x∼X, τ∼p_M(H,x)} r(τ, x)

同时优化准确率和上下文成本时，按 Pareto 支配关系维护前沿。实践中，每个 harness 是 **100–1000 行的单文件 Python 程序**，修改范围包括任务特定的 prompting、检索、记忆和编排逻辑。

### 4.2 极简外环（Algorithm 1）

1. 初始化种群 H，基线 harness 包括 zero-shot、few-shot、ACE、MCE，评估后写入文件系统 D；
2. 每轮由 proposer 查询 D，提出 k 个新 harness。通过接口校验的候选进入评估，全部日志（源码、推理轨迹、分数、执行轨迹）写入 D 的新目录；
3. 运行固定轮数后返回 Pareto 前沿，在测试集上做最终评估。

**外环不预设搜索结构**：proposer 可以读取任意先前 harness，无固定父代选择规则；proposer 自行决定局部编辑或整体重写，无固定变异算子；也不预设档案结构。作者认为，将诊断和编辑决策交给 proposer，可以让 Meta-Harness 随 coding agent 能力提高而改善。这是将 Bitter Lesson 用于 harness 搜索的做法。

**数据隔离**：proposer 全程只访问搜索集（search set），测试集用于最终评估。TerminalBench-2 未遵循这一设置，详见局限部分。

### 4.3 proposer 的实际行为（Appendix A）

**文件访问统计**（TB2 搜索，10 轮）：中位 **82 文件/轮**（69–99），其中 41% 为先前 harness 源码，40% 为执行轨迹，6% 为分数摘要，13% 为其他文件。访问模式是**非马尔可夫**的，通常检查大部分历史，超出了最近父代的范围。

**跨候选归因过程**（以下转述 TB2 搜索日志中 proposer 的分析）：
- **轮 1–2**：两个候选都同时修改结构和 prompt 模板。结构修复包括标记剥离、循环打断，以及移除双重确认完成机制。两者均低于 64.4% 的基线，分别为 58.9%、57.8%。
- **轮 3 · 识别混淆变量**：系统判断，prompt 模板中的清理指令导致 agent 在任务完成前删除必要状态，使结构修复与有害的 prompt 变更混在一起。evo_strip_only 单独保留两个已验证的结构修复，结果为 63.3%（−1.1pp）。下降幅度远小于前两版，支持了混淆变量的诊断。
- **轮 4–6**：继续修复完成流状态机 bug，参考 configure-git-webserver 任务中反复验证 30–60 步的轨迹，同时放宽清理措辞、加入智能等待，结果全部下降。proposer 据此认为，即使局部假设合理，修改 prompt 和完成流仍有较高风险。
- **轮 7 · 胜出候选**：系统将此前 6 轮下降归因于完成流、prompt 模板或观察处理的修改。evo_env_bootstrap 只新增一项功能：在首次 LLM 调用前，用一条 shell 命令收集环境快照，附到初始 prompt，其余方法保持不变。
- **轮 8 · 组合**：合并环境快照与标记剥离两个相互独立的修复，保持 prompt 和确认流不变，因为这些修改在 7 轮中有 5 轮导致下降。
- **轮 10 · 跨运行迁移**：引用另一次独立搜索的结果：保留服务产物、不执行清理，带来 +18pp。

这段过程展示了如何跨候选追溯失败原因。压缩反馈的优化器缺少此类信息，GEPA 的反思摘要不会保留两个失败候选共享同一项 prompt 修改的细节。

## 5. 实验结果全景

### 5.1 在线文本分类（GPT-OSS-120B）

**设置**：LawBench（215 类罪名）、Symptom2Disease（22 类）、USPTO-50k（180 类反应物）；20 轮 × 2 候选 = 40 harness。

**vs 手工 harness（Table 2）**：

| Harness | USPTO | S2D | Law | Avg Acc | Ctx (K tok) |
|---|---|---|---|---|---|
| Zero-shot | 12.0 | 63.2 | 7.0 | 27.4 | 0 |
| Few-shot (all) | 15.0 | 78.3 | 29.0 | 40.8 | 12.3 |
| MCE | 14.0 | 83.0 | 23.0 | 40.0 | 28.5 |
| ACE | 16.0 | 77.8 | 29.0 | 40.9 | 50.8 |
| **Meta-Harness** | 14.0 | **86.8** | **45.0** | **48.6** | **11.4** |

相对 ACE 提高 +7.7 分，相对 MCE 提高 +8.6，上下文仅为 ACE 的 22%。Law 从 29→45，是单个数据集上的最大提升。

**vs 文本优化器（Table 4，搜索集）**：GEPA 32.6/40.2、Best-of-N 34.0/44.2、OpenEvolve 39.1/43.3、TTT-Discover 34.1/45.6、**Meta-Harness 50.0/56.7**（中位/最佳）。仅用 **4 次评估**就达到对手耗尽预算后的分数，评估效率高 10×；最终分数还高出 10 分以上。

**反馈内容消融（Table 3）**：

| 条件 | 分数 | 代码 | 摘要 | 轨迹 | 中位 | 最佳 | >ZS |
|---|---|---|---|---|---|---|---|
| 只给分数 | ✓ | ✓ | × | × | 34.6 | 41.3 | 26 |
| 分数 + 摘要 | ✓ | ✓ | ✓ | × | 34.9 | 38.7 | 23 |
| **全接口** | ✓ | ✓ | – | ✓ | **50.0** | **56.7** | **39** |

加入摘要后的最佳分数仍低于只给分数（38.7 < 41.3），说明摘要未能补回反馈信息，可能遗漏了诊断细节。这组消融的增益来自原始执行轨迹。

**OOD 泛化（Table 5）**：9 个搜索期未见数据集的平均分为 **73.1% vs ACE 70.2%**，在 6/9 上最佳；few-shot 示例超过 32 个后，在 7/9 任务上表现下降。

**Pareto 前沿（Fig. 3）**：给 proposer 当前指标与期望权衡后，它能沿整条准确率-上下文曲线搜索 harness，覆盖多个取舍点。

### 5.2 检索增强数学推理

**设置**：≥500K 已解题语料（8 个开源数据集，去重去污，人工检查 held-out 的 BM25 top 检索）；250 题搜索集（OlympiadBench + Omni-MATH hard）；40 轮 109 候选；GPT-OSS-20B 上选出单个 harness；200 道 IMO 级 held-out 题（IMO-AnswerBench、IMO-ProofBench、ArXivMath）。

**Table 6（pass@1，3 样本均值）**：

| 方法 | GPT-5.4n | GPT-5.4m | Gem-3.1FL | Gem-3F | GPT-20B | Avg |
|---|---|---|---|---|---|---|
| 无检索 | 23.0 | 28.8 | 28.6 | 42.6 | 47.6 | 34.1 |
| Dense (k=5) | 31.1 | 28.3 | 37.1 | 47.2 | 46.7 | 38.1 |
| BM25 | 30.2 | 29.2 | 32.8 | 46.6 | 48.9 | 37.5 |
| **Meta-Harness** | **31.7** | **30.4** | 34.9 | 46.3 | **50.6** | **38.8 (+4.7)** |

5 个 held-out 模型均未退化；相比之下，dense 在 GPT-5.4m 上 −0.5，随机 few-shot 平均 −1.9。得到的 harness 使用**四路 BM25 词法路由**（组合/几何/数论/默认），每路配置不同的去重、重排和取例策略。修改全部发生在同一 BM25 栈的代码中，未引入稠密编码器。

### 5.3 TerminalBench-2（89 任务）

| 模型 | Harness | Pass |
|---|---|---|
| Opus 4.6 | Terminus-KIRA（手工） | 74.7 |
| Opus 4.6 | ForgeCode | 81.8（公开代码无法复现） |
| Opus 4.6 | **Meta-Harness** | **76.4**（全榜 #2） |
| Haiku 4.5 | Goose | 35.5 |
| Haiku 4.5 | **Meta-Harness** | **37.6**（全榜 #1） |

最终改动是在 Terminus-KIRA 上添加约 **80 行**环境快照 bootstrap。agent 循环开始前，系统运行一条复合 shell 命令，收集 pwd、/app 清单、语言版本（Python/GCC/Node/Java/Rust/Go）、包管理器和内存信息，注入首个 prompt。命令设为 15 秒超时，失败时不报错。这省去了开头 **2–4 个探索回合**。89 个任务中净赢 7 个，protein-assembly、path-tracing 的提升最大。受益任务都需要先了解环境，包括生信库、渲染管线、棋引擎、密码学工具和 CoreWars 模拟器。

## 6. 局限

1. **TB2 搜索集 = 测试集**。论文将任务称为 discovery problem，援引该榜惯例，公开 writeup 已描述在 TB 上反复迭代 harness，并使用 regex 审计。但反复优化同一评估分布仍可能使评估失效：regex 能排查硬编码答案，无法排除对 89 个任务分布的**软过拟合**。解释 76.4% 时需要保留这一限制。
2. **单一 proposer**：全部结果来自 Claude Code + Opus-4.6，尚未验证跨 proposer 的稳健性，作者将其列为 future work。
3. **proposer 冻结不进化**：改进者与被改进对象完全分离，严格说属于**自动化 harness 工程**，尚不构成递归自改进。隔离使 proposer 不被 game，但 proposer 自身不会变强，也限制了后续改进。
4. **成本未报告**：每轮 10 MTok 意味着成本增加三个数量级。论文仅称耗时数小时，未给出搜索总开销，也未与基线比较 token 用量。
5. **harness 在任务间重置**：与记忆进化方法 ACE/MCE 不同，这里更新程序，不保留跨任务经验，因此未获得后者的跨任务累积收益。
6. **文本分类中 USPTO 没有提升**（14.0 vs ACE 16.0），收益集中在 Law 与 S2D。

## 7. 意义与位置

**对报告 01（Weng 总纲）**：Weng 将 harness 定义为可执行搜索空间，并提出 meta-harness 层。本文以 Meta-Harness 为名实现了这一设想：外环只保留必要结构，文件系统保存全部历史，具体搜索决策由 proposer 作出。

**对报告 07（DGM）**：DGM 通过档案与父代采样管理历史，Meta-Harness 删去这些预设结构，让 proposer 自由 grep 全历史。消融中，压缩反馈降低了表现。两者的修改对象也不同：DGM 修改自身，Meta-Harness 的 proposer 始终在进化循环之外。

**对报告 14（Self-Harness）**：两者可用于比较"外部强 proposer vs 自我 proposer"。Meta-Harness 由前沿 proposer 读取完整反馈，追求更高表现；Self-Harness 压缩证据并设置回归检查，让 35B 级模型能够完成循环。Self-Harness 的证据包摘要属于 Meta-Harness 消融中会丢失信号的压缩方式。前者的上限取决于外部 proposer，后者则受弱模型处理上下文的能力限制。

**对报告 11（Continual Harness）**：CH 不重置环境，在故障现场修改，状态跨 episode 累积；Meta-Harness 重置环境后离线搜索，得到可读、可迁移的静态程序。CH 所遇到的最低能力要求在这里得到缓解：由前沿 proposer 负责搜索，较弱的目标模型 Haiku 4.5 也能从 harness 改进中受益。

**对报告 05（WGtG 锚定纪律）**：搜索集分数与官方 verifier 提供不参与进化的评估依据，测试集全程与 proposer 隔离。唯一例外是 TB2，这里用人工检查和 regex 审计作补充，尝试弥补测试独立性不足。

**对报告 10（harness 资产化）**：数学检索 harness 在 5 个未见模型上 +4.7，文本分类 harness 在 9 个 OOD 数据集上取得 6 胜，说明 harness 可以跨模型迁移，也便于人工审读。代码中的过拟合可以通过脆弱的 if 链、硬编码映射等形式识别，权重空间缺少这种直接审计方式。

**Discussion 提出的后续方向**：共同进化 harness 与模型权重，使策略影响模型学习的内容，模型再影响策略。Co-Harness（报告 21）与 Continual Harness 的 co-learning loop 正在研究这一过程。
