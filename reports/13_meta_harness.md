# Meta-Harness 深度解读：把 harness 工程交给 coding agent——原始执行轨迹是唯一关键成分

> **Meta-Harness: End-to-End Optimization of Model Harnesses**
> arXiv 2603.28052 v1（2026-03-30）· Stanford IRIS Lab（Yoonho Lee、Roshen Nair、Qizheng Zhang、Chelsea Finn）+ KRAFTON（Kangwook Lee）+ MIT（Omar Khattab）
> 代码：github.com/stanford-iris-lab/meta-harness-tbench2-artifact · 项目页 yoonholee.com/meta-harness
> 归档：`papers/en/2603.28052_MetaHarness.pdf` · 中译 `papers/zh/2603.28052_MetaHarness_zh.pdf`

---

## 1. 一句话定位

同一模型换 harness 可产生 **6×** 性能差，但 harness 工程至今靠人手迭代——工程师看失败、调启发式、改几版。已有文本优化器（OPRO、TextGrad、GEPA、AlphaEvolve、TTT-Discover）把反馈压缩成分数、模板或 LLM 摘要，每步只消费 **0.002–0.026 MTok**；而 harness 是长时程程序，一个"存什么、何时取、怎么呈现"的决定会影响许多步之后的行为，压缩掉的正是把下游失败追溯到上游 harness 决策所需的信息。Meta-Harness 的解法极简：把全部历史——每个候选的源码、分数、原始执行轨迹——放进文件系统，让一个 **coding agent proposer**（Claude Code + Opus-4.6）用 grep/cat 自主决定读什么（每轮中位 **82 个文件**、约 **10 MTok**），自己做失败归因、自己决定改哪里；外环不设父代选择规则、不设变异算子。三域结果：在线文本分类 **48.6% vs ACE 40.9（+7.7）** 且上下文省 **4×**；IMO 级数学检索 harness 跨 5 个 held-out 模型平均 **+4.7 分**；TerminalBench-2 Opus 4.6 上 **76.4%**（超手工 Terminus-KIRA 74.7%，全榜第 2）、Haiku 4.5 上 **37.6%**（全榜第 1）。决定性消融：只给分数 34.6/41.3，分数加摘要 34.9/38.7，全轨迹 **50.0/56.7**——**中位候选都胜过两个消融的最佳候选**。这是 Weng 总纲中 meta-harness 概念的首个正式论文化。

## 2. 要解决的问题

论文用一张表（Table 1）把问题定量化：

| 方法 | 历史 | 日志内容 | MTok/轮 |
|---|---|---|---|
| OPRO | 窗口 | 过去 (solution, score) 对 | 0.002 |
| TextGrad | 最近 | 当前工件的文本反馈 | 0.015 |
| AlphaEvolve | 窗口 | 程序库 + 评估分 | 0.022 |
| GEPA | 摘要 | rollout 轨迹的反思反馈 | 0.008 |
| Feedback Descent | 摘要 | 对比 + 文本反馈 | 0.012 |
| TTT-Discover | 窗口 | 前一解的片段 | 0.026 |
| **Meta-Harness** | **全部** | **全部日志与分数** | **10.0** |

三个数量级的差距不是"更多就更好"的粗暴主张，而是任务结构决定的：harness 优化发生在**代码空间**，检索、记忆、prompt 构造逻辑的小改动会在许多推理步之后才显形，局部搜索启发式与问题错配。既有优化器的压缩是"务实的可扩展性选择，不是长程依赖无信息的证据"。

第二个问题是**谁来消费这么多信息**。10 MTok 远超任何上下文窗口，所以 proposer 必须是 **coding agent 而非裸 LLM**——它得决定看什么、通过直接操作代码库验证编辑。作者自注：这一工作流直到 2026 年初 coding agent 能力跃升后才变得可行。

## 3. 为什么此前做不通：三条线各差一块

| 已有路线 | 有什么 | 缺什么 |
|---|---|---|
| 文本优化器（GEPA、OPRO、TextGrad） | 迭代改 prompt / 文本工件 | 反馈压缩到 <0.03 MTok；只见当前候选或摘要；**无法跨候选做因果归因** |
| 程序进化（AlphaEvolve、OpenEvolve、ADAS、AFlow） | 代码空间搜索、LLM 做变异算子 | 固定 scaffold 内进化指定函数、或搜索工作流图——**预定义空间**；档案/父代选择是人工结构 |
| 记忆设计搜索（ACE、MCE） | 跨任务累积上下文 | 优化的是"经验"不是"程序"；上下文随时间膨胀（ACE 50.8K token） |
| DGM（报告 07） | 改自身源码、档案搜索 | 有结构化父代采样、每步只见自身失败；**改进者 = 被改进物**，proposer 会被 game |
| 人工 harness 工程 | 目前 SOTA（Terminus-KIRA、ForgeCode） | 不可扩展；每换一个模型都要重来 |

关键缺口是**反馈带宽与消费者能力的匹配**：压缩反馈是因为 LLM 消化不了全历史；coding agent 能自主 grep 全历史，于是压缩变成纯损失。Meta-Harness 的贡献不是发明新搜索算法，而是发现"当消费者变强，最好的搜索结构就是没有结构"。

## 4. 方法机制

### 4.1 目标形式化

harness 是包裹冻结模型 M 的有状态程序：给定任务 x ∼ X，执行 rollout τ ∼ p_M(H, x)，harness 构造 prompt、模型响应、harness 更新状态；任务奖励 r(τ, x) 打分。目标：

H* = argmax_H E_{x∼X, τ∼p_M(H,x)} r(τ, x)

多目标（准确率 + 上下文成本）时按 Pareto 支配维护前沿。实践中每个 harness 是**单文件 Python 程序**（100–1000 行），修改任务特定的 prompting、检索、记忆、编排逻辑。

### 4.2 极简外环（Algorithm 1）

1. 初始化种群 H（基线 harness：zero-shot、few-shot、ACE、MCE），评估后写入文件系统 D；
2. 每轮：proposer 查询 D → 提出 k 个新 harness → 通过接口校验的进入评估 → 全部日志（源码、推理轨迹、分数、执行轨迹）写回 D 新目录；
3. 固定轮数后返回 Pareto 前沿，在测试集上做最终评估。

**刻意没有的东西**：父代选择规则（proposer 可以看任意先前 harness）、变异算子（proposer 自己决定局部编辑还是整体重写）、档案结构。作者的理由："把诊断与编辑决策留给 proposer 而非硬编码搜索启发式，Meta-Harness 随 coding agent 变强自动变强"——Bitter Lesson 的 harness 版。

**数据隔离**：proposer 全程只见搜索集（search set），测试集留到最终评估。TerminalBench-2 是刻意破例（见局限）。

### 4.3 proposer 的实际行为（Appendix A）

**文件访问统计**（TB2 搜索，10 轮）：中位 **82 文件/轮**（69–99），41% 先前 harness 源码、40% 执行轨迹、6% 分数摘要、13% 其他——访问模式**非马尔可夫**，例行检查大部分历史而非只看最近父代。

**因果推理叙事**（TB2 搜索日志，proposer 原话）：
- **轮 1–2**：两个候选都把结构修复（标记剥离 + 循环打断；移除双重确认完成机制）与 prompt 模板重写捆绑，双双从 64.4% 基线回退（58.9%、57.8%）。
- **轮 3 · 识别混淆变量**："回退的根因是 prompt 模板变更（清理指令）让 agent 在任务完成前删掉了必要状态。结构性修复与有害的 prompt 变更混淆了。evo_strip_only 隔离出两个已证明的结构修复。"结果 63.3%（−1.1pp）——损失远小于前两版，支持混淆诊断。
- **轮 4–6**：继续直接修诊断出的完成流状态机 bug（引用 configure-git-webserver 任务中 30–60 步验证螺旋的具体轨迹证据）、软化清理语言、智能等待——全部回退。proposer 学到经验教训："prompt 与完成流的修改高风险，即使局部假设听起来合理。"
- **轮 7 · 胜出候选**："全部 6 轮回退都因为修改了完成流、prompt 模板或观察处理。evo_env_bootstrap 采取不同路线——**纯加性**。在首次 LLM 调用前用一条 shell 命令收集环境快照、附到初始 prompt。不改其他任何方法。"
- **轮 8 · 组合**：把环境快照与标记剥离组合（"两个正交修复，不碰 prompt 或确认流——那些在 7 轮中 5 轮造成回退"）。
- **轮 10 · 跨运行迁移**：引用另一次独立搜索的结果（"'不要清理服务产物'值 +18pp"）。

这条叙事是论文的方法论核心：**跨候选的因果推理是压缩反馈优化器在构造上做不到的**——GEPA 的反思摘要不会告诉你"两个失败候选共享一个 prompt 干预"。

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

+7.7 分对 ACE、+8.6 对 MCE，上下文只有 ACE 的 22%。Law 上 29→45 是最大单点。

**vs 文本优化器（Table 4，搜索集）**：GEPA 32.6/40.2、Best-of-N 34.0/44.2、OpenEvolve 39.1/43.3、TTT-Discover 34.1/45.6、**Meta-Harness 50.0/56.7**（中位/最佳）。**4 次评估就追平对手跑满预算的终点**（10× 更快），终点再高 10 分以上。

**决定性消融（Table 3）**：

| 条件 | 分数 | 代码 | 摘要 | 轨迹 | 中位 | 最佳 | >ZS |
|---|---|---|---|---|---|---|---|
| 只给分数 | ✓ | ✓ | × | × | 34.6 | 41.3 | 26 |
| 分数 + 摘要 | ✓ | ✓ | ✓ | × | 34.9 | 38.7 | 23 |
| **全接口** | ✓ | ✓ | – | ✓ | **50.0** | **56.7** | **39** |

加摘要甚至比只给分数的最佳还低（38.7 < 41.3）——**摘要补不回信号，可能压掉诊断细节**。原始执行轨迹是唯一关键成分。

**OOD 泛化（Table 5）**：9 个搜索期未见数据集平均 **73.1% vs ACE 70.2%**，6/9 最佳；few-shot 例子加过 32 个后在 7/9 任务上反而变差。

**Pareto 前沿（Fig. 3）**：给 proposer 当前指标和期望权衡，它能在整条准确率-上下文曲线上发现 harness，而不是绑定单一人工操作点。

### 5.2 检索增强数学推理

**设置**：≥500K 已解题语料（8 个开源数据集，去重去污，人工检查 held-out 的 BM25 top 检索）；250 题搜索集（OlympiadBench + Omni-MATH hard）；40 轮 109 候选；GPT-OSS-20B 上选出单个 harness；200 道 IMO 级 held-out 题（IMO-AnswerBench、IMO-ProofBench、ArXivMath）。

**Table 6（pass@1，3 样本均值）**：

| 方法 | GPT-5.4n | GPT-5.4m | Gem-3.1FL | Gem-3F | GPT-20B | Avg |
|---|---|---|---|---|---|---|
| 无检索 | 23.0 | 28.8 | 28.6 | 42.6 | 47.6 | 34.1 |
| Dense (k=5) | 31.1 | 28.3 | 37.1 | 47.2 | 46.7 | 38.1 |
| BM25 | 30.2 | 29.2 | 32.8 | 46.6 | 48.9 | 37.5 |
| **Meta-Harness** | **31.7** | **30.4** | 34.9 | 46.3 | **50.6** | **38.8 (+4.7)** |

5 个 held-out 模型**无一回退**（dense 在 GPT-5.4m 上 −0.5、随机 few-shot 平均 −1.9）。发现的 harness 是**四路 BM25 词法路由**（组合/几何/数论/默认），各配不同的去重-重排-取例策略——在同一 BM25 栈上纯代码空间优化，不引入稠密编码器。

### 5.3 TerminalBench-2（89 任务）

| 模型 | Harness | Pass |
|---|---|---|
| Opus 4.6 | Terminus-KIRA（手工） | 74.7 |
| Opus 4.6 | ForgeCode | 81.8（公开代码无法复现） |
| Opus 4.6 | **Meta-Harness** | **76.4**（全榜 #2） |
| Haiku 4.5 | Goose | 35.5 |
| Haiku 4.5 | **Meta-Harness** | **37.6**（全榜 #1） |

发现的改动小得惊人：在 Terminus-KIRA 上加约 **80 行**"环境快照 bootstrap"——agent 循环开始前跑一条复合 shell 命令收集 pwd、/app 清单、语言版本（Python/GCC/Node/Java/Rust/Go）、包管理器、内存，注入首个 prompt；15 秒超时、静默失败。省掉开头 **2–4 个探索回合**。89 任务净赢 7 个（protein-assembly、path-tracing 最大），全是"环境不可先验假设"的任务（生信库、渲染管线、棋引擎、密码学工具、CoreWars 模拟器）。

## 6. 局限

1. **TB2 搜索集 = 测试集**。论文自称 discovery problem，援引该榜惯例（公开 writeup 已描述在 TB 上反复迭代 harness）并做 regex 审计——但这正是本调研反复警惕的评估器塌缩温床：regex 挡得住硬编码答案，挡不住对 89 个任务分布的**软过拟合**。76.4% 应打折读。
2. **单一 proposer**：全部结果建立在 Claude Code + Opus-4.6 上；跨 proposer 稳健性未验证，作者列为 future work。
3. **proposer 冻结不进化**：严格说这是**自动化 harness 工程**而非递归自改进——改进者与被改进物完全分离。这既是锚（proposer 不被 game），也是天花板（proposer 不会变强）。
4. **成本未报告**：每轮 10 MTok 是三个数量级的成本跃升，论文只说"数小时墙钟"，未给搜索总开销或与基线的 token 对比。
5. **harness 在任务间重置**：与记忆进化线（ACE/MCE）明确切割，优化的是"程序"不是"经验"——跨任务累积收益让渡给了那一系。
6. **文本分类的 USPTO 没涨**（14.0 vs ACE 16.0）——收益集中在 Law 与 S2D。

## 7. 意义与位置

**对报告 01（Weng 总纲）**：Weng 把 harness 定义为可执行搜索空间并预言 meta-harness 层，本文是该预言的直接论文化——连名字都叫 Meta-Harness。它给出这一层的第一性设计原则：**外环最小结构 + 全历史文件系统 + 搜索智能全部让渡给 proposer**。

**对报告 07（DGM）**：DGM 用档案与父代采样管理历史，Meta-Harness 刻意删掉这些结构，用"proposer 自由 grep 全历史"替代，消融证明结构化压缩反而有害。但 DGM 改的是自身，Meta-Harness 的 proposer 永远站在进化之外。

**对报告 14（Self-Harness）**：正好构成"外部强 proposer vs 自我 proposer"对照组。Meta-Harness 靠前沿 proposer 满血反馈拿绝对上限，Self-Harness 靠证据压缩 + 回归门让 35B 级模型走通循环——Self-Harness 的证据包压缩恰是 Meta-Harness 消融证明会丢信号的那类摘要。两者的天花板互为镜像：前者系于外部 proposer，后者系于弱模型的上下文消化能力。

**对报告 11（Continual Harness）**：正交轴两极。CH 免重置、故障现场改、状态跨 episode 累积；Meta-Harness 重置式、离线搜索、产物是可读可迁移的静态程序。CH 的能力地板在这里被绕开：搜索智能外包给前沿 proposer，目标模型再弱（Haiku 4.5）也吃到 harness 红利。

**对报告 05（WGtG 锚定纪律）**：搜索集分数与官方 verifier 是不参与进化的锚，测试集全程对 proposer 隔离——除 TB2 一处破例，破例处用人工检查加 regex 审计打补丁，是"锚变薄后用外部审计增厚"的实操样本。

**对报告 10（harness 资产化）**：数学检索 harness 对 5 个未见模型 +4.7、文本分类 harness 在 9 个 OOD 数据集 6 胜——harness 是可跨模型迁移、可人工审读的资产。代码空间的过拟合肉眼可见（脆弱 if 链、硬编码映射），这是权重空间不具备的可审计性。

**Discussion 里的一句话值得单独记**："自然的下一步是共进化 harness 与模型权重，让策略塑造模型学什么、反之亦然"——这正是 Co-Harness（报告 21）与 Continual Harness 的 co-learning loop 在做的事。
