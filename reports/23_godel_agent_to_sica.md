# 解读报告 23 · 2024-2025 桥接：从 Gödel Agent 到 SICA

| 文献 | 时间 | 作者 / 机构 | 归档 |
|---|---|---|---|
| Gödel Agent: A Self-Referential Agent Framework for Recursively Self-Improvement | arXiv 2410.04444（2024-10，v4 2025-05） | Xunjian Yin, Xinyi Wang, Liangming Pan, Li Lin, Xiaojun Wan, William Yang Wang（北大 + UCSB + Arizona） | `papers/en/2410.04444_GodelAgent.pdf` + 中译 |
| A Self-Improving Coding Agent (SICA) | arXiv 2504.15228（2025-04） | Maxime Robeyns, Martin Szummer, Laurence Aitchison（Bristol + iGent AI） | `papers/en/2504.15228_SICA.pdf` + 中译 |
| 在调研中的位置 | 填补报告 00（1965-2014 思想史）与报告 07（DGM 2025-05）之间的空档：Gödel Agent 是 Schmidhuber Gödel Machine 的第一个 LLM 实现，SICA 是"agent 改自己代码"在真实编码基准上的第一个正结果；DGM 同时继承两者（名字来自前者、编码域与安全约束来自后者） |

## 一句话核心主张

2024-2025 年间，"agent 修改自身源码"从思想实验变成可运行系统，但代价是**把 Schmidhuber 的形式证明门换成经验效用门**：Gödel Agent 用 monkey patching 让 LLM 在运行时直接读写自身的内存与逻辑，只靠高层目标提示驱动；SICA 把这套机制放到 SWE-Bench Verified 上，用显式效用函数（分数 0.5 + 成本 0.25 + 时间 0.25）选最优版本，并第一次把**异步监督者**（asynchronous overseer）做成自改写系统的标配安全部件。

## Gödel Agent（2024-10）

**机制**：受 Gödel Machine 启发，agent 通过 monkey patching 直接读取和修改运行时内存中的自身逻辑，不依赖预定义例程或固定优化算法；整个搜索空间只受高层目标的提示约束。与 Meta Agent Search（ADAS）这类"meta 层固定、只搜 agent 设计"的方法不同，Gödel Agent 声称可以搜索整个 agent 设计空间。

**关键数字（Table 1，GPT-3.5 系）**：受约束版 Gödel-base 在 DROP / MGSM / MMLU / GPQA 上 80.9 / 64.2 / 70.9 / 34.9，全面超过 Meta Agent Search（79.4 / 53.4 / 69.6 / 34.6）和所有手工 agent（CoT、Self-Refine、LLM Debate 等）；无约束版 Gödel-free 达 90.5 / 90.6 / 87.9 / 55.7——但作者用斜体标注，因为"无约束"意味着它可以调用更强模型或外部资源，不是公平对比。

**历史意义与局限**：它证明了"自指 + LLM"在工程上可运行，但也暴露了后来 Metan（报告 20）量化的问题——action API 必须冻结，realized meta-depth 约 2.5；Metan 实测 Gödel Agent 在 ARC-AGI-2 上得分 0.054，CO-Bench 上 0.451（远低于 OpenEvolve 0.814），说明无档案、单链自改写在难任务上容易陷入平台。

## SICA（2025-04）

**机制**：一个带基本编码工具的 agent 系统自主编辑自身代码。核心设计三件：(1) **显式效用函数** U = 0.5·score + 0.25·(1 − cost/$10) + 0.25·(1 − time/300s)，超时按比例罚——第一次把"更好"定义成多目标而非单一基准分；(2) **版本档案**：每次自改写产出新版本，在基准上评估后选最优者作为下一轮的改写者与被改写者；(3) **异步监督者**：一个独立 LLM 线程每 30 秒（或关键事件）读取系统状态的完整文本表示，判断 agent 是否偏离或卡死并可干预——工具、子 agent 与监督机制本身也在可自改范围内。

**关键数字**：SWE-Bench Verified 随机子集从 **17% 提升到 53%**；LiveCodeBench 与合成 agent 基准（文件编辑、符号定位）亦有提升；全程考虑安全约束与资源预算。作者定位其为"数据高效、非梯度、由 LLM 反思与代码更新驱动的学习机制"。

**局限**：随机子集而非全量 SWE-Bench Verified；效用函数的权重是手设的；监督者与被监督者同源（同一 LLM 家族），属于自评。

## 桥接：两篇如何通向 DGM

| 要素 | Gödel Machine 2003 | Gödel Agent 2024 | SICA 2025 | DGM 2025-05（报告 07） |
|---|---|---|---|---|
| 改写触发 | 形式证明"改后更优" | LLM 判断 + 目标提示 | 效用函数 + 基准评估 | 基准评估 + 档案选择 |
| 搜索结构 | 单链 | 单链 | 版本档案（选最优） | 开放式档案（多父代、保留次优） |
| 安全部件 | 无（证明即安全） | 无 | 异步监督者 + 资源约束 | 沙箱 + 人工审查 + 档案回溯 |
| 域 | 通用 | QA/数学（DROP/MGSM/MMLU/GPQA） | 编码（SWE-Bench/LCB） | 编码（SWE-bench/Polyglot） |

DGM 从 Gödel Agent 继承了名字与"改自身代码"的野心，从 SICA 继承了编码域、效用/基准驱动与安全约束，再加上自己的贡献——**开放式档案**（保留表现差但可能是踏脚石的版本）。这条线上最重要的转折点不在 DGM 而在 SICA：**监督者的引入**承认了自改写系统需要一个不参与改写的观察者——这是锚定纪律（报告 05）在安全侧的第一个工程雏形，虽然 SICA 自己没有这样命名。

## 与本调研的连线

1. **对报告 00 的接续**：Schmidhuber 的证明门在 Gödel Agent 里被替换为"LLM 觉得更好"，在 SICA 里被替换为"效用函数说更好"，在 DGM 里被替换为"基准说更好"——三步松弛越来越可测，也越来越依赖外部评估器，直接导向报告 05 的评估器塌缩问题。
2. **对报告 07 DGM 的溯源**：DGM 论文的两项核心主张（自改写可行、档案多样性重要）分别在 Gödel Agent 与 SICA 里有原型；DGM 的增量是把两者合并并加大规模。
3. **对报告 20 Metan 的对照**：Metan 把 Gödel Agent 作为 baseline 系统性击败，并归因于"驱动层冻结导致 meta 深度 2.5"——本报告的两篇正是 Metan 批评的靶子，读完可以判断这一批评是否公允：Gödel Agent 的确单链无档案，SICA 有档案但仍是单 meta 层。
4. **对报告 08 MOSS 的前史**：SICA 的异步监督者 → DGM 的沙箱人审 → MOSS 的批准/回滚门控，是"自改写系统的安全部件"三年三级跳；SICA 是这条线的起点。

