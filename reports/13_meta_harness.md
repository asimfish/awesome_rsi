# 解读报告 13 · Meta-Harness: End-to-End Optimization of Model Harnesses

| 项目 | 内容 |
|---|---|
| arXiv | 2603.28052 v1（2026-03-30） |
| 作者 | Yoonho Lee、Roshen Nair、Qizheng Zhang（Stanford）、Kangwook Lee（KRAFTON）、Omar Khattab（MIT）、Chelsea Finn（Stanford） |
| 代码 | github.com/stanford-iris-lab/meta-harness-tbench2-artifact；项目页 yoonholee.com/meta-harness（含交互 demo） |
| 在调研中的位置 | Weng 总纲（报告 01）中 meta-harness 概念的首个正式论文化：harness 工程本身被一个外层 coding agent 自动化，即"优化 harness 的 harness" |

## 一句话核心主张

同一模型换 harness 可产生 6 倍性能差，但 harness 工程至今靠人手迭代；已有文本优化器（GEPA、AlphaEvolve、TextGrad 等）把反馈压缩成分数、模板或摘要，每步只消费 0.002 至 0.026 MTok，远低于 harness 搜索的诊断足迹。Meta-Harness 的解法是把全部历史——每个候选的源码、分数、原始执行轨迹——放进文件系统，让一个 coding agent proposer（Claude Code + Opus-4.6）用 grep/cat 自主决定读什么（每轮中位 82 个文件、约 10 MTok），自己做失败归因、自己决定改哪里；外环刻意极简，不设父代选择规则，不设变异算子。

## 方法拆解：极简外环 + 满血反馈通道

- 目标形式化：H* = argmax E[r(τ,x)]，harness 是包裹冻结模型 M 的有状态程序（单文件 Python，100 至 1000 行），多目标时按 Pareto 支配维护前沿。
- 循环：proposer 查文件系统 → 提出 k 个新 harness → 接口校验后评估 → 全部日志写回文件系统新目录。典型一次跑 20 轮、评约 60 个 harness，数小时墙钟完成。
- 关键选择是"coding agent 而非裸 LLM"：经验量远超上下文窗口，proposer 必须决定看什么、并通过直接操作代码库验证编辑。作者自注：这一工作流直到 2026 年初 coding agent 能力跃升后才变得可行。
- proposer 全程只见搜索集，测试集留到最终评估（TerminalBench-2 是刻意破例，见局限）。

## 关键数字

- 在线文本分类（GPT-OSS-120B，LawBench / Symptom2Disease / USPTO-50k）：48.6% 对 ACE 40.9（+7.7 分）、MCE 40.0，且上下文只用 11.4K token 对 ACE 的 50.8K（省 4 倍余）。搜索集上 50.0 中位 / 56.7 最佳，对 GEPA 32.6/40.2、OpenEvolve 39.1/43.3、TTT-Discover 34.1/45.6——4 次评估就追平对手跑满预算的终点，终点再高 10 分以上。
- 决定性消融（表 3）：只给分数 34.6/41.3；分数加 LLM 摘要 34.9/38.7；全轨迹 50.0/56.7。中位候选都胜过两个消融的最佳候选——摘要补不回信号，甚至压掉诊断细节。原始执行轨迹是唯一关键成分。
- OOD 泛化：9 个搜索期未见数据集平均 73.1% 对 ACE 70.2%，6/9 最佳；而少样本例子加过 32 个后在 7/9 任务上反而变差。
- 检索增强数学推理：535K 题去重去污语料，40 轮搜出 109 个候选，选出的单个四路 BM25 词法路由 harness（组合/几何/数论/默认，各配不同的去重-重排-取例策略）在 200 道 IMO 级题上对 5 个 held-out 模型平均 +4.7 分（对无检索基线），胜稠密检索与裸 BM25，且无一模型回退。
- TerminalBench-2：Opus 4.6 上 76.4%（超手工 Terminus-KIRA 的 74.7%，全榜第 2，第 1 名 ForgeCode 结果无法从公开代码复现）；Haiku 4.5 上 37.6%（全榜第 1，超 Goose 35.5）。发现的改动小得惊人：在 Terminus-KIRA 上加约 80 行"环境快照 bootstrap"——agent 循环开始前跑一条复合 shell 命令收集语言/包管理器/目录清单注入首个 prompt，省掉开头 2 至 4 个探索回合；89 任务净赢 7 个，全是"环境不可先验假设"的任务。
- 定性轨迹（附录 A）：前两轮把结构修复与 prompt 改写捆绑提交、双双回退；第 3 轮 proposer 明确写出混淆变量诊断（共享的 prompt 干预才是祸首）并做隔离实验；连续 6 轮回退后第 7 轮转向"纯加性修改"拿下最佳。这种跨候选因果推理是压缩反馈优化器在构造上做不到的。

## 局限与批评

- TerminalBench-2 搜索集等于测试集（论文自称 discovery problem，援引该榜惯例并做了字符串泄漏 regex 审计），但这正是本调研反复警惕的评估器塌缩温床：regex 挡得住硬编码答案，挡不住对 89 个任务分布的软过拟合。
- 单一 proposer：全部结果建立在 Claude Code + Opus-4.6 上，跨 proposer 的稳健性未验证；且 proposer 本身冻结不进化——严格说这是自动化 harness 工程而非递归自改进，改进者与被改进物完全分离。
- 每轮 10 MTok 的反馈消费是对既有方法三个数量级的成本跃升，论文未报告搜索总开销。
- 被优化的 harness 在任务间重置（与记忆进化线明确切割），它优化的是"程序"而非"经验"，跨任务累积收益让渡给了 ACE/MCE 一系。

## 与本调研的连线

- **对报告 01（Weng 总纲）**：Weng 把 harness 定义为可执行搜索空间并预言 meta-harness 层，本文是该预言的直接论文化——连名字都叫 Meta-Harness，并给出这一层的第一性设计原则：外环最小结构 + 全历史文件系统，把搜索智能全部让渡给 proposer，随 coding agent 变强自动变强（Bitter Lesson 的 harness 版）。
- **对报告 07（DGM）**：DGM 用档案与父代采样的进化结构管理历史，Meta-Harness 刻意删掉这些结构，用"proposer 自由 grep 全历史"替代，消融证明结构化压缩反而有害。但 DGM 改的是自身（改进者=被改进物），Meta-Harness 的 proposer 永远站在进化之外——这既是锚（proposer 不被 game），也是天花板（proposer 不会变强）。
- **对报告 11（CH）**：正交轴上的两极。CH 免重置、在故障现场改，harness 状态跨 episode 累积；Meta-Harness 重置式、离线搜索，产物是可读可迁移的静态程序。CH 的能力地板在这里被绕开：搜索智能外包给前沿 proposer，目标模型再弱（Haiku 4.5）也吃到 harness 红利——恰好补上 CH"弱模型自举失败"的缺口。
- **对报告 05（WGtG 锚定纪律）**：搜索集分数与官方 verifier 是不参与进化的锚，测试集全程对 proposer 隔离——除 TB2 一处破例；破例处用人工检查加 regex 审计打补丁，是 WGtG 意义上"锚变薄后用外部审计增厚"的实操样本。
- **对报告 10（harness 资产化）**：数学检索 harness 对 5 个未见模型平均 +4.7 分、文本分类 harness 在 9 个 OOD 数据集 6 胜——harness 是可跨模型迁移、可人工审读的资产；代码空间的过拟合肉眼可见（脆弱 if 链、硬编码映射），这是权重空间不具备的可审计性。
