# Awesome Recursive Self-Improvement (RSI)

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
![papers](https://img.shields.io/badge/papers-61%2B6_classics-blue)
![reports](https://img.shields.io/badge/deep--dives-29-red)
![zh-PDF](https://img.shields.io/badge/zh--PDF-66-green)
![slides](https://img.shields.io/badge/slides-34p-orange)
![full report](https://img.shields.io/badge/full_report-149p-8a2be2)

围绕 **Recursive Self-Improvement（递归自改进）** 的论文列表 + 系统性调研仓库：从 Good 1965 的智能爆炸猜想，到 2026 年的评估器共进化与 harness 工业化。与一般 awesome 列表不同，本仓库对每篇核心论文都附**中文深度解读**与**保版式中文 PDF**，并给出一条贯穿全部材料的主线：

> **执行已经自动化，品味正在被编译，锚是最后的手工业。** 所有能跑的自进化系统都保留一个不参与进化的 ground-truth 锚；谁能工业化地生产不可 game 的锚，谁就握住了 RSI 的节流阀。

![Figure 1 · Timeline](assets/fig1_timeline.svg)

*图 1 · 71 项工作的时间线：十个家族分泳道，按 arXiv 首版年月定位，★ 为十份核心精读材料；1965–2014 思想史与 2023–2026 工程爆发之间断轴，2026-08 一个月集中了 21 项。*

**仓库内容一览**

| 类型 | 数量 | 位置 |
|---|---|---|
| 中文深度解读（统一七节结构，约 8.3 万字） | 29 份 | [`reports/`](reports/) · 索引见 [§5](#5-deep-dive-reports) |
| 英文论文 PDF | 61 篇 + 6 篇起源经典 | [`papers/en/`](papers/en/) · [`papers/classics/`](papers/classics/) |
| 保版式中文翻译 PDF（[super_translate](https://github.com/asimfish/super_translate)） | 66 篇——**全部英文 PDF 均有中译** | [`papers/zh/`](papers/zh/) |
| 汇总 PPT | 34 页 HTML / PDF | [`report/awesome_rsi_slides.html`](report/awesome_rsi_slides.html) · [PDF](report/awesome_rsi_slides.pdf) |
| 全文合订报告（29 份解读 + 两张纵览图） | 149 页 | [`report/awesome_rsi_full_report.pdf`](report/awesome_rsi_full_report.pdf) · [HTML](report/awesome_rsi_full_report.html) |

## Contents

- [1. Start Here](#1-start-here)
- [2. Core Readings](#2-core-readings)
- [3. Overview: Taxonomy](#3-overview-taxonomy)
- [4. Papers](#4-papers)
  - [4.1 Origins (1965–2014)](#41-origins-19652014) · [4.2 Bridge (2023–2025)](#42-bridge-20232025) · [4.3 Surveys](#43-surveys)
  - [4.4 Framework Side](#44-framework-side) · [4.5 Evaluator Side](#45-evaluator-side) · [4.6 Model Side](#46-model-side) · [4.7 Knowledge Side](#47-knowledge-side) · [4.8 Online Side](#48-online-side)
  - [4.9 Harness Engineering (2026)](#49-harness-engineering-2026) · [4.10 Autonomous Research & Industrial Evidence](#410-autonomous-research--industrial-evidence)
  - [4.11 Safety & Governance](#411-safety--governance) · [4.12 Program Evolution Lineage](#412-program-evolution-lineage) · [4.13 Macro Debate & Measurement](#413-macro-debate--measurement)
- [5. Deep-Dive Reports](#5-deep-dive-reports)
- [6. Insights & Open Problems](#6-insights--open-problems)
- [7. Reference](#7-reference) — [Glossary](#71-glossary) · [Timeline](#72-timeline) · [System Comparison Matrix](#73-system-comparison-matrix)
- [8. Secondary Sources (中文导读)](#8-secondary-sources-中文导读)
- [9. Repository Layout & Build](#9-repository-layout--build)
- [10. Roadmap](#10-roadmap)
- [11. Related Resources](#11-related-resources)
- [12. Disclaimer & Credits](#12-disclaimer--credits)

**标记约定**：⭐ = 调研发起时的十份核心精读对象；`[解读]` = 有专门的中文深度解读报告；每条论文均附 `[paper]` 原文链接与仓库内 `[PDF-en]` / `[PDF-zh]`。

## 1. Start Here

**按时间预算**

| 预算 | 路线 |
|---|---|
| 15 分钟 | [汇总 PPT](report/awesome_rsi_slides.html)（浏览器方向键翻页，P 键打印）或 [PDF 版](report/awesome_rsi_slides.pdf) |
| 2 小时 | [报告 10 汇总洞察](reports/10_synthesis_insights.md) → [报告 01 Weng 总纲](reports/01_lilian_weng_harness_engineering.md) → [报告 05 Who Grades the Grader](reports/05_who_grades_the_grader.md)（全谱系最重要的否定性结论） |
| 通读 | [全文合订报告](report/awesome_rsi_full_report.pdf)（149 页，29 份解读按编号排列） |
| 系统研读 | `reports/` 按 00 → 23 → 01 → 02 → 07 → 03 → 04 → 05 → 06 → 08 → 11 → 09 → 10 的顺序，其余按需；配 `papers/zh/` 中文 PDF 对照原文 |

**按目的**

| 目的 | 路线 |
|---|---|
| 建立全景 | [10](reports/10_synthesis_insights.md) → 三份综述 [12](reports/12_self_evolving_agents_survey.md) / [22](reports/22_coevolution_survey.md) / [28](reports/28_self_evolving_coding_agents_survey.md) |
| 理解 harness 工程 | [01](reports/01_lilian_weng_harness_engineering.md) Weng 总纲 → [07](reports/07_darwin_godel_machine.md) DGM → [13](reports/13_meta_harness.md) Meta-Harness vs [14](reports/14_self_harness.md) Self-Harness → [16](reports/16_autosaddler.md) AutoSaddler → [11](reports/11_continual_harness.md) Continual Harness |
| 理解评估器战争 | [03](reports/03_evolm.md) EvoLM → [04](reports/04_red_queen_godel_machine.md) RQGM → [05](reports/05_who_grades_the_grader.md) WGtG → [06](reports/06_echo.md) ECHO → [24](reports/24_evalcegar.md) EvalCEGAR vs [25](reports/25_rho.md) RHO（锚的最大化利用 vs 完全无锚） |
| 看生产落地 | [02](reports/02_anthropic_when_ai_builds_itself.md) Anthropic → [08](reports/08_moss.md) MOSS → [19](reports/19_icoder.md) iCoder → [18](reports/18_prime_agent.md) Prime Agent → [27](reports/27_safety_governance.md) 安全治理五篇 |
| 思想史与递归深度 | [00](reports/00_origins_1965_2014.md) Good → Bostrom → [23](reports/23_godel_agent_to_sica.md) Gödel Agent → SICA → [07](reports/07_darwin_godel_machine.md) DGM → [20](reports/20_metan.md) Metan |
| 知识侧 / 技能库 | [09](reports/09_wikiskill.md) WikiSkill → [26](reports/26_skill_evolution_wave.md) 技能红海五篇 → [15](reports/15_envharness.md) EnvHarness（练什么决定技能上限） |
| 二次开发 | [19](reports/19_icoder.md) iCoder 基座评估 → [13](reports/13_meta_harness.md) / [16](reports/16_autosaddler.md) 两种 harness 改写哲学 → [21](reports/21_co_harness.md) Co-Harness 双环 → [22](reports/22_coevolution_survey.md) 过程级测试清单 → [27](reports/27_safety_governance.md) 部署纪律清单 |

## 2. Core Readings

本调研的两份总纲性材料（非论文），其余八份 ⭐ 核心论文分布在 §4 各侧。

1. ⭐ **Harness Engineering for Self-Improvement.** Lil'Log, 2026\. [blog](https://lilianweng.github.io/posts/2026-07-04-harness/), [解读](reports/01_lilian_weng_harness_engineering.md)
_Lilian Weng_ — 把 auto-research / 自改进 agent / 进化式程序搜索三条线统一到"harness 是可执行搜索空间"之下；优化对象递进线 prompt → 上下文 → 工作流 → harness 代码 → 优化器代码；七条挑战成为 2026 下半年论文的题眼。
2. ⭐ **When AI Builds Itself: Anthropic's Progress toward Recursive Self-Improvement.** Anthropic Institute, 2026\. [article](https://www.anthropic.com/institute/recursive-self-improvement), [解读](reports/02_anthropic_when_ai_builds_itself.md)
_Marina Favaro, Jack Clark_ — 首次披露的内部数据：>80% 合入代码由 Claude 写、人均产出 8×、训练加速测试 3×→52×、研究方向判断胜人类 64%；执行已自动化，品味是人类保留的最后一环。

## 3. Overview: Taxonomy

![Figure 2 · Taxonomy](assets/fig2_taxonomy.svg)

*图 2 · 递归自改进的分类体系：七个一级维度（思想史与判据 / 改哪层 / 锚在哪 / 时间模式 / 知识侧 / 安全治理 / 测量与宏观）、37 个子类。"锚在哪"是本仓库独有的主轴——三份公开综述都没有这一列。两图由 `scripts/make_figures.py` 生成，深色版用于 PPT。*

§4 的论文分类沿用本调研的**五侧地图**（框架侧 / 评估侧 / 模型侧 / 知识侧 / 在线侧）加上 2026 年的三个新家族（harness 工程、自动研究与工业实证、安全治理），再以思想史、桥接、综述、程序进化谱系、宏观测量五节补全上下文。

## 4. Papers

### 4.1 Origins (1965–2014)

> RSI 的定义链：Good 给正反馈直觉，Yudkowsky 给能力构造与持续条件，Schmidhuber 给自指完备的形式化极限，Bostrom 给进入强 RSI 的动力学判据（crossover）。逐篇拆解见[报告 00](reports/00_origins_1965_2014.md)。

1. **Speculations Concerning the First Ultraintelligent Machine.** Advances in Computers Vol. 6, 1965\. [paper](http://incompleteideas.net/papers/Good65ultraintelligent.pdf), [PDF-en](papers/classics/1965_Good_UltraintelligentMachine.pdf)（扫描件，无文本层）, [解读](reports/00_origins_1965_2014.md)
_Irving John Good_ — "设计机器本身也是一种智力活动"，超智能机器可以设计更好的机器 → intelligence explosion。
2. **General Intelligence and Seed AI 2.3.** Singularity Institute, 2000–2001\. [web archive](https://web.archive.org/web/20120805130100/singularity.org/files/GISAI.html), [PDF-en](papers/classics/2001_Yudkowsky_GISAI.pdf), [PDF-zh](papers/classics/2001_Yudkowsky_GISAI_zh.pdf), [解读](reports/00_origins_1965_2014.md)
_Eliezer Yudkowsky_ — Seed AI 三能力（self-understanding / self-modification / recursive self-enhancement）；让固定优化器跑得更快不能维持递归改进，每一级提升必须开出新的改进机会。
3. **Gödel Machines: Self-Referential Universal Problem Solvers Making Provably Optimal Self-Improvements.** arXiv, 2003\. [paper](https://arxiv.org/abs/cs/0309048), [PDF-en](papers/classics/2003_Schmidhuber_GoedelMachines.pdf), [PDF-zh](papers/classics/2003_Schmidhuber_GoedelMachines_zh.pdf), [解读](reports/00_origins_1965_2014.md)
_Jürgen Schmidhuber_ — 寻找 improvement 的机制本身也在可修改集合里；只有 proof searcher 证明"自改写收益更高"才执行改写——理论自洽、工程不可行的极点。
4. **Superintelligence: Paths, Dangers, Strategies.** Oxford University Press, 2014\. [book](https://global.oup.com/academic/product/superintelligence-9780199678112), [解读](reports/00_origins_1965_2014.md)
_Nick Bostrom_ — 增长率 = optimization power ÷ recalcitrance；crossover point：系统自身贡献主导后续改进即进入 strong RSI。"When the AI improves itself, it improves the thing that does the improving."
5. **The Coming Technological Singularity: How to Survive in the Post-Human Era.** VISION-21 Symposium, 1993\. [essay](https://edoras.sdsu.edu/~vinge/misc/singularity.html)
_Vernor Vinge_ — 把 Good 的智能爆炸命名为"奇点"，列出四条路径。
6. **The Basic AI Drives.** AGI-08, 2008\. [paper](https://selfawaresystems.com/wp-content/uploads/2008/01/ai_drives_final.pdf), [PDF-en](papers/classics/2008_Omohundro_BasicAIDrives.pdf), [PDF-zh](papers/classics/2008_Omohundro_BasicAIDrives_zh.pdf)
_Stephen M. Omohundro_ — 任何足够强的目标驱动系统都会自发产生自改进、自保护、资源获取等工具性驱力——RSI 安全讨论的起点。
7. **The Singularity: A Philosophical Analysis.** Journal of Consciousness Studies, 2010\. [paper](http://consc.net/papers/singularity.pdf), [PDF-en](papers/classics/2010_Chalmers_Singularity.pdf), [PDF-zh](papers/classics/2010_Chalmers_Singularity_zh.pdf)
_David J. Chalmers_ — 把爆炸论证形式化为"比例论题 + 扩展论题"，系统列举结构性 / 相关性 / 动机性 / 情境性 defeaters。
8. **Intelligence Explosion Microeconomics.** MIRI Technical Report, 2013\. [paper](https://intelligence.org/files/IEM.pdf), [PDF-en](papers/classics/2013_Yudkowsky_IEM.pdf), [PDF-zh](papers/classics/2013_Yudkowsky_IEM_zh.pdf)
_Eliezer Yudkowsky_ — "认知再投资回报率"作为核心变量；Bostrom 2014 动力学框架的直接前身，也是 §4.13 宏观争论的源头。

### 4.2 Bridge (2023–2025)

> 从思想史到 2025 年工程爆发之间的踏脚石：证明门 → LLM 判断 → 效用函数 → 基准，三步松弛越来越可测、也越来越依赖外部评估器。逐篇拆解见[报告 23](reports/23_godel_agent_to_sica.md)。

1. **Voyager: An Open-Ended Embodied Agent with Large Language Models.** arXiv, 2023\. [paper](https://arxiv.org/abs/2305.16291), [code](https://github.com/MineDojo/Voyager), [PDF-en](papers/en/2305.16291_Voyager.pdf), [PDF-zh](papers/zh/2305.16291_Voyager_zh.pdf)
_Guanzhi Wang, Yuqi Xie, Yunfan Jiang, Ajay Mandlekar, et al. (NVIDIA / Caltech / Stanford)_ — 第一个"可执行技能库随交互增长"的 LLM agent，知识侧工作的共同祖先。
2. **Gödel Agent: A Self-Referential Agent Framework for Recursively Self-Improvement.** arXiv, 2024\. [paper](https://arxiv.org/abs/2410.04444), [code](https://github.com/Arvid-pku/Godel_Agent), [PDF-en](papers/en/2410.04444_GodelAgent.pdf), [PDF-zh](papers/zh/2410.04444_GodelAgent_zh.pdf), [解读](reports/23_godel_agent_to_sica.md)
_Xunjian Yin, Xinyi Wang, Liangming Pan, Li Lin, Xiaojun Wan, William Yang Wang (PKU / UCSB)_ — Gödel Machine 的第一个 LLM 实现：monkey patching 运行时改写自身逻辑；GPT-3.5 系 DROP / MGSM / MMLU / GPQA 80.9 / 64.2 / 70.9 / 34.9 超 Meta Agent Search。
3. **A Self-Improving Coding Agent (SICA).** arXiv, 2025\. [paper](https://arxiv.org/abs/2504.15228), [code](https://github.com/MaximeRobeyns/self_improving_coding_agent), [PDF-en](papers/en/2504.15228_SICA.pdf), [PDF-zh](papers/zh/2504.15228_SICA_zh.pdf), [解读](reports/23_godel_agent_to_sica.md)
_Maxime Robeyns, Martin Szummer, Laurence Aitchison (Bristol / iGent AI)_ — SWE-Bench Verified 子集 17% → 53%；显式多目标效用函数 + 版本档案 + **异步监督者**——自改写系统安全部件的起点。

### 4.3 Surveys

> 三份综述的分工：TMLR 给单体自进化的四维坐标，Co-Evolution 给多组件互相施压的三阶段，Coding 给编码域的对象–时间–证据三维。三份都没有把"必须存在不参与进化的锚"写成必要条件——这是本仓库 §7.3 对照矩阵把"锚在哪"设为主轴的原因。

1. **A Survey of Self-Evolving Agents: What, When, How, and Where to Evolve on the Path to Artificial Super Intelligence.** TMLR, 2026\. [paper](https://arxiv.org/abs/2507.21046), [code](https://github.com/CharlesQ9/Self-Evolving-Agents), [PDF-en](papers/en/2507.21046_SelfEvolvingAgentsSurvey.pdf), [PDF-zh](papers/zh/2507.21046_SelfEvolvingAgentsSurvey_zh.pdf), [解读](reports/12_self_evolving_agents_survey.md)
_Huan-ang Gao, Jiayi Geng, Wenyue Hua, Mengkang Hu, et al. (Princeton / 清华 / CMU 等 17 家机构)_ — What / When / How / Where 四维；评估节指出 Retention 是最缺服务的维度；图书馆学而非力学。
2. **Co-Evolution in Agentic Systems: Toward Self-Directed Evolution Beyond Human Design.** arXiv, 2026\. [paper](https://arxiv.org/abs/2608.10299), [PDF-en](papers/en/2608.10299_CoEvolutionSurvey.pdf), [PDF-zh](papers/zh/2608.10299_CoEvolutionSurvey_zh.pdf), [解读](reports/22_coevolution_survey.md)
_Qing Zong, Jiayu Liu, Junhao Shen, Zecong Tang, Linsi Wu, et al., Yangqiu Song (HKUST / UIUC / CUHK / HKU / PKU)_ — Agent-Agent → Agent-Environment → Meta 三阶段；按其判据只有 RQGM 越过 Meta 线；提出过程级测试三件套。
3. **Self-Evolving Coding Agents.** arXiv, 2026\. [paper](https://arxiv.org/abs/2608.03392), [awesome list](https://github.com/iSEngLab/Awesome-Self-Evolving-Coding-Agents), [PDF-en](papers/en/2608.03392_SelfEvolvingCodingAgentsSurvey.pdf), [PDF-zh](papers/zh/2608.03392_SelfEvolvingCodingAgentsSurvey_zh.pdf), [解读](reports/28_self_evolving_coding_agents_survey.md)
_Hao Zhou, Haichuan Hu, Ye Shang, Quanjun Zhang (NJUST / NJU, iSEngLab)_ — 进化对象六类 × 时间三类 × 证据三类；核心警告：不可靠的测试或基准捷径会被存进记忆、蒸馏成技能、更新进模型——**错误被持久化**。

### 4.4 Framework Side

> 自改写源码：agent 直接修改自己的 harness 代码库。共同约束是必须留一部分不可改（DGM 的探索循环、MOSS 的进化引擎），Metan 把这个约束量化为 meta 深度 ≈ 2.5 并给出绕行。

1. ⭐ **Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents.** ICLR, 2026\. [paper](https://arxiv.org/abs/2505.22954), [code](https://github.com/jennyzzt/dgm), [PDF-en](papers/en/2505.22954_DGM.pdf), [PDF-zh](papers/zh/2505.22954_DGM_zh.pdf), [解读](reports/07_darwin_godel_machine.md)
_Jenny Zhang, Shengran Hu, Cong Lu, Robert Lange, Jeff Clune_ — 证明门松弛为基准门 + 开放式档案保留踏脚石；SWE-bench 20.0% → 50.0%、Polyglot 14.2% → 30.7%；出现伪造日志等 objective hacking。
2. ⭐ **MOSS: Self-Evolution through Source-Level Rewriting in Autonomous Agent Systems.** arXiv, 2026\. [paper](https://arxiv.org/abs/2605.22794), [code](https://github.com/hkgai-official/Moss), [PDF-en](papers/en/2605.22794_MOSS.pdf), [PDF-zh](papers/zh/2605.22794_MOSS_zh.pdf), [解读](reports/08_moss.md)
_Qianshu Cai, Yonggang Zhang, Xianzhang Jia, Huajiang Zheng, Wei Xue, Jun Song, Xinmei Tian, Yike Guo (USTC / HKGAI / HKUST / HKBU)_ — 唯一覆盖生产部署的源码级自改写：失败批次重放 + 用户批准门 + 健康探测回滚；单轮 0.25 → 0.61。
3. **HyperAgents.** arXiv, 2026\. [paper](https://arxiv.org/abs/2603.19461), [PDF-en](papers/en/2603.19461_Hyperagents.pdf), [PDF-zh](papers/zh/2603.19461_Hyperagents_zh.pdf)
_Jenny Zhang, Bingchen Zhao, Wannan Yang, Jakob Foerster, Jeff Clune, Minqi Jiang, Sam Devlin, Tatiana Shavrina (UBC / Vector / Edinburgh / NYU)_ — DGM 后继：加 meta-agent 控制如何修改任务 agent，从编码推广到任意域。
4. **Metaⁿ: Recursive Self-Improvement through Emergent Depth.** arXiv, 2026\. [paper](https://arxiv.org/abs/2608.24735), [code](https://github.com/minnesotanlp/meta-n), [PDF-en](papers/en/2608.24735_Metan.pdf), [PDF-zh](papers/zh/2608.24735_Metan_zh.pdf), [解读](reports/20_metan.md)
_Zae Myung Kim, Young-Jun Lee, Seungyeon Jwa, Dongyeop Kang (UMN / SNU)_ — 冻结元操作 Ω、递归其输入：深度由收敛决定（3–6）；ARC-AGI-2 0.331 唯一非零；消融显示 72% 增益来自层间条件化字符串、代码复用仅 15%。

### 4.5 Evaluator Side

> 评估器不再是固定裁判：rubric 共进化、受控效用进化、锚定纪律、碰撞对驱动进化——以及"评估器塌缩与真进化观测等价"的否定性结论。

1. ⭐ **EvoLM: Self-Evolving Language Models through Co-Evolved Discriminative Rubrics.** arXiv, 2026\. [paper](https://arxiv.org/abs/2605.03871), [code](https://github.com/stellalisy/EvoLM), [PDF-en](papers/en/2605.03871_EvoLM.pdf), [PDF-zh](papers/zh/2605.03871_EvoLM_zh.pdf), [解读](reports/03_evolm.md)
_Shuyue Stella Li, Rui Xin, Teng Xiao, Yike Wang, Rulin Shao, et al., Yulia Tsvetkov (UW / AI2)_ — rubric 生成器与 policy 交替训练；反直觉发现：静态 RM 判分精度越高、训出的 policy 反而越差（reward overoptimization 悖论）。
2. ⭐ **The Red Queen Gödel Machine: Co-Evolving Agents and Their Evaluators.** arXiv, 2026\. [paper](https://arxiv.org/abs/2606.26294), [PDF-en](papers/en/2606.26294_RQGM.pdf), [PDF-zh](papers/zh/2606.26294_RQGM_zh.pdf), [解读](reports/04_red_queen_godel_machine.md)
_Alex Iacob, Andrej Jovanović, William F. Shen, et al., Nicholas D. Lane (Cambridge / NVIDIA / Flower Labs)_ — epoch 内冻结评估器、边界处在人类锚数据集上晋升 + 选择性擦除；Polyglot 71.7% vs 69.9% 且省 1.35–1.72× token；论文写作接受率 1.86×。
3. ⭐ **Who Grades the Grader? Co-Evolving Evaluation Metrics and Skills for Self-Improving LLM Agents.** arXiv, 2026\. [paper](https://arxiv.org/abs/2607.12790), [code](https://github.com/amazon-science/Self-Evolving-Agents-Double-Ratchet), [PDF-en](papers/en/2607.12790_WhoGradesTheGrader.pdf), [PDF-zh](papers/zh/2607.12790_WhoGradesTheGrader_zh.pdf), [解读](reports/05_who_grades_the_grader.md)
_Xing Zhang, Guanghui Wang, Yanwei Cui, Ziyuan Li, Wei Qiu, Bing Zhu, Peiyang He (AWS / HSBC)_ — 十条锚定样本下进化评估指标（MBPP+ 一致性 +0.21）；否定性结论：去掉锚定守卫，塌缩的指标训出的技能任务分与正常一样好——**下游任务分不能验证自进化评估器**。
4. **Metrics That Write Themselves: Evolving an Evaluator from Its Own Blind Spots (EvalCEGAR).** arXiv, 2026\. [paper](https://arxiv.org/abs/2608.18744), [PDF-en](papers/en/2608.18744_EvalCEGAR.pdf), [PDF-zh](papers/zh/2608.18744_EvalCEGAR_zh.pdf), [解读](reports/24_evalcegar.md)
_Xing Zhang, Yanwei Cui, Guanghui Wang, Zhihao Lin, Peiyang He (AWS)_ — WGtG 续作：借程序验证的 CEGAR，把锚上的碰撞对（签名相同、一对一错）当作评估算子的编写规格；55 行算子关闭 15.4% 可达差距（p = 0.001）。
5. **Self-Evolving Deep Research via Joint Generation and Evaluation (SCORE).** arXiv, 2026\. [paper](https://arxiv.org/abs/2606.04507), [PDF-en](papers/en/2606.04507_SCORE.pdf), [PDF-zh](papers/zh/2606.04507_SCORE_zh.pdf)
_Han Zhu, Chengkun Cai, Yuanfeng Song, Xing Chen, Sirui Han, Yike Guo (HKUST / ByteDance / UCL)_ — 评估器与求解器共享参数联合训练，把评估器共进化推进到权重层；用 meta-harness 监控评估维度失效。

### 4.6 Model Side

> 共进化推进到权重层：critic 与 policy 同步更新、harness 收益蒸馏进权重、技能库随 RL 共进化。

1. ⭐ **No More Stale Feedback: Co-Evolving Critics for Open-World Agent Learning (ECHO).** arXiv, 2026\. [paper](https://arxiv.org/abs/2601.06794), [PDF-en](papers/en/2601.06794_ECHO.pdf), [PDF-zh](papers/zh/2601.06794_ECHO_zh.pdf), [解读](reports/06_echo.md)
_Zhicong Li, Lingjie Jiang, Yulan Hu, et al., Yong Liu (人大 / 阿里高德 / 北大)_ — critic 与 policy 双轨 GRPO 锁步更新 + 饱和感知增益；Qwen3-4B 四环境 77.85 vs GRPO 70.57；冻结 critic 在 ALFWorld/SciWorld 上**低于不用 critic**——陈旧反馈不是无用，是有害。
2. **Co-Harness: Co-Evolving Harnesses and Model Weights for LLM Agents.** arXiv, 2026\. [paper](https://arxiv.org/abs/2607.22688), [PDF-en](papers/en/2607.22688_CoHarness.pdf), [PDF-zh](papers/zh/2607.22688_CoHarness_zh.pdf), [解读](reports/21_co_harness.md)
_Zhengyu Chen, Teng Xiao, Huaisheng Zhu, Yige Yuan, Luan Zhang, Jingang Wang (美团 / AI2)_ — HarnessCritic 按归因分类法改 harness、再用改进后的轨迹 SFT 权重；Qwen3-8B/32B × AIME/HMMT 平均 +20.4 pp，超人工 harness +24.7；200+ 小时无人干预 22 版 harness。
3. **SkillRL: Evolving Agents via Recursive Skill-Augmented Reinforcement Learning.** arXiv, 2026\. [paper](https://arxiv.org/abs/2602.08234), [code](https://github.com/aiming-lab/SkillRL), [PDF-en](papers/en/2602.08234_SkillRL.pdf), [PDF-zh](papers/zh/2602.08234_SkillRL_zh.pdf)
_Peng Xia, Jianwen Chen, Hanyang Wang, Jiaqi Liu, et al. (UNC / aiming-lab)_ — 轨迹蒸馏为分层 SkillBank，技能库在 RL 中按验证失败递归进化；ALFWorld / WebShop 超基线 15.3%。
4. **Evolving-RL: End-to-End Optimization of Experience-Driven Self-Evolving Capability within Agents.** arXiv, 2026\. [paper](https://arxiv.org/abs/2605.10663), [code](https://github.com/Fanzy27/Evolving-RL), [PDF-en](papers/en/2605.10663_EvolvingRL.pdf), [PDF-zh](papers/zh/2605.10663_EvolvingRL_zh.pdf)
_小红书 + 北京大学_ — 同一策略同时当 extractor 与 solver，用下游迁移收益做 GRPO 奖励；ALFWorld 未见任务相对 GRPO +98.7%。
5. **SIA: Self Improving AI with Harness & Weight Updates.** arXiv, 2026\. [paper](https://arxiv.org/abs/2605.27276), [PDF-en](papers/en/2605.27276_SIA.pdf), [PDF-zh](papers/zh/2605.27276_SIA_zh.pdf)
_Prannay Hebbar, Yogendra Manawat, Samuel Verboomen, et al. (Hexo Labs)_ — Feedback-Agent 决定本轮改 harness 还是改权重；Weng 评价"方向有趣、证据临时"（任务 agent 与 meta agent 用不同模型，基线偏弱）。

### 4.7 Knowledge Side

> 经验必须先编译成结构化知识再蒸馏为技能，才能跨任务复利；共识是"抽象优于存储 + 生命周期管理"，分歧在编译成什么结构。合评见[报告 26](reports/26_skill_evolution_wave.md)。

1. ⭐ **WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution.** arXiv, 2026\. [paper](https://arxiv.org/abs/2608.27454), [PDF-en](papers/en/2608.27454_WikiSkill.pdf), [PDF-zh](papers/zh/2608.27454_WikiSkill_zh.pdf), [解读](reports/09_wikiskill.md)
_Liyan Tang, Cyrus Rashtchian, Chun-Sung Ferng, Andrew Tomkins, Da-Cheng Juan, Tu Vu (Google Research / Virginia Tech)_ — raw 不可变 / wiki 永不回滚 / skill 门控可回滚的三层不对称；五基准五模型全部第一；Proposer 有 wiki +15.0、Inference 读 wiki −2.8；9B+技能 > 27B 无技能。
2. **SkillCommit: Evolving Agent Skills through Behaviorally Validated Scope Expansion.** arXiv, 2026\. [paper](https://arxiv.org/abs/2608.15165), [PDF-en](papers/en/2608.15165_SkillCommit.pdf), [PDF-zh](papers/zh/2608.15165_SkillCommit_zh.pdf), [合评](reports/26_skill_evolution_wave.md)
_Yu He, Weikai Yang (NJU / HKUST-GZ)_ — 反对按语义相似度合并：跨实例重放 + 机制检查双检通过才提交为高层技能。
3. **HyperSkill: Self-Evolving LLM Agents via Hypergraph-Structured Skill Memory.** arXiv, 2026\. [paper](https://arxiv.org/abs/2608.16114), [PDF-en](papers/en/2608.16114_HyperSkill.pdf), [PDF-zh](papers/zh/2608.16114_HyperSkill_zh.pdf), [合评](reports/26_skill_evolution_wave.md)
_Ruiyao Xu, Tiankai Yang, Wei-Chieh Huang (Northwestern / USC / UIC)_ — 超边保留子任务与技能的 n 元组合关系；GAIA +11.51、WebWalkerQA +11.18。
4. **ERSkill: Evolving for Skill-Guided Adaptive Memory Retrieval.** arXiv, 2026\. [paper](https://arxiv.org/abs/2608.12720), [PDF-en](papers/en/2608.12720_ERSkill.pdf), [PDF-zh](papers/zh/2608.12720_ERSkill_zh.pdf), [合评](reports/26_skill_evolution_wave.md)
_Haolong Chen, Liang Zhang, Zhuo Li, Lei Xue, Guangxu Zhu (CUHK-SZ / SYSU)_ — 把检索行为本身技能化，技能集与路由器共进化，双 frontier 解耦扩张与部署；平均 +31.3%。
5. **SkillProx: Self-Evolving Agent Skills via Proximal Textual Gradient Descent.** arXiv, 2026\. [paper](https://arxiv.org/abs/2608.07449), [PDF-en](papers/en/2608.07449_SkillProx.pdf), [PDF-zh](papers/zh/2608.07449_SkillProx_zh.pdf), [合评](reports/26_skill_evolution_wave.md)
_Mingxuan Zheng, Yujin Zhou, Chuxue Cao, et al., Sirui Han, Yike Guo (HKUST)_ — 近端梯度下降搬到文本技能空间，冻结留一效用审计，删除是一等公民；+3.0 pp。
6. **Evo-Harness: Context-to-Harness Skill Compilation for Self-Evolving Agents.** arXiv, 2026\. [paper](https://arxiv.org/abs/2608.15071), [PDF-en](papers/en/2608.15071_EvoHarness.pdf), [PDF-zh](papers/zh/2608.15071_EvoHarness_zh.pdf), [合评](reports/26_skill_evolution_wave.md)
_Tianxin Wei, Zhan Shi, Minhua Lin, Bing He, et al., Hanqing Lu (UIUC / Amazon)_ — 单次执行编译为通用 + 主题技能；Opus 4.6 五基准全胜（TerminalBench-2 62.92 → 73.03）；系统性隔离 evolver / 反馈 / 迁移各自贡献。
7. **Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models (ACE).** ICLR, 2026\. [paper](https://arxiv.org/abs/2510.04618), [PDF-en](papers/en/2510.04618_ACE.pdf), [PDF-zh](papers/zh/2510.04618_ACE_zh.pdf)
_Qizheng Zhang, Changran Hu, Shubhangi Upasani, et al., Kunle Olukotun (Stanford / SambaNova)_ — 上下文当作演化中的 playbook：Generator / Reflector / Curator 三组件增量更新，防 context collapse。
8. **Meta Context Engineering via Agentic Skill Evolution (MCE).** arXiv, 2026\. [paper](https://arxiv.org/abs/2601.21557), [PDF-en](papers/en/2601.21557_MCE.pdf), [PDF-zh](papers/zh/2601.21557_MCE_zh.pdf)
_Haoran Ye, Xuning He, Vincent Arak, Haonan Dong, Guojie Song (PKU)_ — 把上下文管理的机制与内容分离，在 skill 空间做元级搜索。

### 4.8 Online Side

> 免重置（reset-free）自改进：在故障现场修 harness 而非回起点重来；率先闭环模型–harness 共学习；并落成开源基础设施。

1. ⭐ **Continual Harness: Online Adaptation for Self-Improving Foundation Agents.** arXiv, 2026\. [paper](https://arxiv.org/abs/2605.09998), [project](https://sethkarten.ai/continual-harness), [PDF-en](papers/en/2605.09998_ContinualHarness.pdf), [PDF-zh](papers/zh/2605.09998_ContinualHarness_zh.pdf), [解读](reports/11_continual_harness.md)
_Seth Karten, Joel Zhang, Tersoo Upaa Jr, Ruirong Feng, Wenzhe Li, Chengshuai Shi, Chi Jin, Kiran Vodrahalli (Princeton)_ — 单场连续 episode 内精炼 harness 四组件，同一轨迹同时喂 Refiner 与权重训练器；发现**能力地板**（Flash-Lite 之下自改进全线更差）。
2. **Prime Agent: A Self-Improving RLM Harness.** arXiv, 2026\. [paper](https://arxiv.org/abs/2608.23552), [code](https://github.com/PrimeIntellect-ai/prime-agent), [PDF-en](papers/en/2608.23552_PrimeAgent.pdf), [PDF-zh](papers/zh/2608.23552_PrimeAgent_zh.pdf), [解读](reports/18_prime_agent.md)
_Seth Karten, Alex L. Zhang, Kevin Thomas, Sebastian Müller, et al. (Princeton / Prime Intellect / MIT)_ — CH 续作：持久 REPL + daemon 恢复分叉 + 版本化 refinement；ARC-AGI-3 官方壳 30.2% → 95.5%；Factorio agent 把 RCON 作弊固化成技能——无独立锚的 refinement 会保存 spec-gaming。

### 4.9 Harness Engineering (2026)

> 2026 年 3–8 月的 harness 工业化浪潮：外部 proposer 优化、模型自改、离线 mini-batch 学习、环境侧进化、垂直落地。共同发现——harness 是可跨模型迁移的资产，且每个能跑的系统都有一个不参与进化的门。六系统中文导读见[§8](#8-secondary-sources-中文导读)。

1. **Meta-Harness: End-to-End Optimization of Model Harnesses.** arXiv, 2026\. [paper](https://arxiv.org/abs/2603.28052), [code](https://github.com/stanford-iris-lab/meta-harness-tbench2-artifact), [PDF-en](papers/en/2603.28052_MetaHarness.pdf), [PDF-zh](papers/zh/2603.28052_MetaHarness_zh.pdf), [解读](reports/13_meta_harness.md)
_Yoonho Lee, Roshen Nair, Qizheng Zhang, Kangwook Lee, Omar Khattab, Chelsea Finn (Stanford / KRAFTON / MIT)_ — coding agent proposer 读全历史文件系统（每轮 82 文件 / 10 MTok）；决定性消融：只给分数 34.6、加摘要 34.9、全轨迹 50.0；TerminalBench-2 Opus 4.6 76.4%（超手工 74.7%）、Haiku 4.5 榜首。
2. **Self-Harness: Harnesses That Improve Themselves.** arXiv, 2026\. [paper](https://arxiv.org/abs/2606.09498), [PDF-en](papers/en/2606.09498_SelfHarness.pdf), [PDF-zh](papers/zh/2606.09498_SelfHarness_zh.pdf), [解读](reports/14_self_harness.md)
_Hangfan Zhang, Shao Zhang, Kangcong Li, et al., Lei Bai, Shuyue Hu (上海 AI Lab)_ — 同一冻结模型给自己的 harness 提有界编辑，双 split 回归门"改坏即拒"；3 模型 × 3 基准 9/9 双升，最大 +132%——锚定纪律本身就是地板保护。
3. **AutoSaddler: Automatic Harness Optimization with Durable Updates from Agent Execution Traces.** arXiv, 2026\. [paper](https://arxiv.org/abs/2608.23041), [project](https://aka.ms/AutoSaddler-website), [PDF-en](papers/en/2608.23041_AutoSaddler.pdf), [PDF-zh](papers/zh/2608.23041_AutoSaddler_zh.pdf), [解读](reports/16_autosaddler.md)
_Sungho Park, Wonjoong Kim, Rongyuan Tan, Jue Zhang, Wook-Shin Han, et al. (POSTECH / KAIST / SUSTech / Microsoft)_ — harness 优化 = 离线 mini-batch 学习（诊断-补丁当反传、dev 集当泛化门、EvoDAG 当优化器状态）；GAIA2 +9.0、TB2 +10.0 超人类手调；**去掉泛化门 50.6 跌破未优化 53.0**。
4. **EnvHarness: Awakening Static Worlds for Agent Learning.** arXiv, 2026\. [paper](https://arxiv.org/abs/2608.19880), [code](https://github.com/google-research/envharness), [PDF-en](papers/en/2608.19880_EnvHarness.pdf), [PDF-zh](papers/zh/2608.19880_EnvHarness_zh.pdf), [解读](reports/15_envharness.md)
_Chengsong Huang, Zifeng Wang, Rujun Han, Jun Yan, et al., Chen-Yu Lee (WashU / Google Cloud AI)_ — 进化对象换成环境（Stage / Contract / Chain 三类接口插件），验证器一根手指不许碰；ALFWorld OOD +9.0；从静态环境抽的技能可为负资产。
5. **MetaCaster: Meta-Harness-Optimized Agent for End-to-End Few-Shot Learning of Lightweight Time Series Forecasters.** arXiv, 2026\. [paper](https://arxiv.org/abs/2608.23473), [code](https://github.com/D2I-Group/metacaster), [PDF-en](papers/en/2608.23473_MetaCaster.pdf), [PDF-zh](papers/zh/2608.23473_MetaCaster_zh.pdf), [解读](reports/17_metacaster.md)
_ChengAo Shen, Wenchao Yu, Fangyu Wu, Dongjin Song, Hanghang Tong, et al., Jingchao Ni (UH / NEC Labs)_ — Agent-as-Engineer：优化信号是 hinge(MSE)——数字当裁判；30 格 19 格第一；同一 harness 换四个 LLM 骨干波动 < 0.1。
6. **Evolving Agents in the Dark: Retrospective Harness Optimization via Self-Preference (RHO).** arXiv, 2026\. [paper](https://arxiv.org/abs/2606.05922), [code](https://github.com/wbopan/retro-harness), [PDF-en](papers/en/2606.05922_RHO.pdf), [PDF-zh](papers/zh/2606.05922_RHO_zh.pdf), [解读](reports/25_rho.md)
_Wenbo Pan, Shujie Liu, Chin-Yew Lin, et al., Xiaohua Jia (CityU HK / MSRA)_ — 只用历史轨迹、零外部评分：DPP coreset → 自验证 + 自一致性诊断 → best-of-N 自偏好选择；单轮 SWE-Bench Pro 59% → 78%；只测单轮，与 AutoSaddler 的"无锚负收益"是当前最需裁决的分歧。
7. **From Failed Trajectories to Reliable LLM Agents: Diagnosing and Repairing Harness Flaws (HarnessFix).** arXiv, 2026\. [paper](https://arxiv.org/abs/2606.06324), [PDF-en](papers/en/2606.06324_HarnessFix.pdf), [PDF-zh](papers/zh/2606.06324_HarnessFix_zh.pdf), [合评](reports/27_safety_governance.md)
_Mengzhuo Chen, Junjie Wang, Zhe Liu, Yawen Wang, Haiming Zheng, Qing Wang (中科院软件所)_ — 轨迹 + harness 制品编译为 HTIR，失败归因到 ETCLOVG 七层后作用域受限修复；四基准 +6.3%–18.4%。
8. **Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses (AHE).** arXiv, 2026\. [paper](https://arxiv.org/abs/2604.25850), [code](https://github.com/china-qijizhifeng/agentic-harness-engineering), [PDF-en](papers/en/2604.25850_AHE.pdf), [PDF-zh](papers/zh/2604.25850_AHE_zh.pdf)
_Jiahang Lin, Shichun Liu, Chengjun Pan, et al., Tao Gui, Yu-Gang Jiang (复旦 / 北大 / 奇绩智峰)_ — 组件 / 经验 / 决策三重可观测；runs 目录、verifier、LLM 配置只读，物理禁掉 reward hacking。
9. **DemoEvolve: Overcoming Sparse Feedback in Agentic Harness Evolution with Demonstrations.** arXiv, 2026\. [paper](https://arxiv.org/abs/2605.24539), [PDF-en](papers/en/2605.24539_DemoEvolve.pdf), [PDF-zh](papers/zh/2605.24539_DemoEvolve_zh.pdf)
_Lirong Che, Yuzhe Yang, Peiwen Lin, Chuang Wang, Xueqian Wang, Jian Su (清华 / AgiBot)_ — 人类示范增广进化档案，缓解稀疏反馈。
10. **Adaptive Auto-Harness: Sustained Self-Improvement for Agentic System Deployment on Open-Ended Task Streams.** arXiv, 2026\. [paper](https://arxiv.org/abs/2606.01770), [PDF-en](papers/en/2606.01770_AdaptiveAutoHarness.pdf), [PDF-zh](papers/zh/2606.01770_AdaptiveAutoHarness_zh.pdf)
_Zewen Liu, Zhan Shi, Yisi Sang, Bing He, Minhua Lin, Tianxin Wei, et al. (Emory / Amazon)_ — 密集自改进在开放任务流上早峰后衰减的负结果实证。
11. **Hierarchical Self-Improvement: A Framework for Task-Specific Evolvable Agent Harnesses (HSI).** arXiv, 2026\. [paper](https://arxiv.org/abs/2608.08466), [PDF-en](papers/en/2608.08466_HSI.pdf), [PDF-zh](papers/zh/2608.08466_HSI_zh.pdf)
_Tailin Zhou (HKUST)_ — 每个任务族维护自己的 harness，经固定注入接口热替换；冻结 meta-evolver 为外层锚。
12. **Harness Updating Is Not Harness Benefit: Disentangling Evolution Capabilities in Self-Evolving LLM Agents.** arXiv, 2026\. [paper](https://arxiv.org/abs/2605.30621), [PDF-en](papers/en/2605.30621_HarnessUpdatingNotBenefit.pdf), [PDF-zh](papers/zh/2605.30621_HarnessUpdatingNotBenefit_zh.pdf)
_Minhua Lin, Juncheng Wu, Zijun Wang, Zhan Shi, Yisi Sang, Bing He, et al._ — 拆开"产出有用编辑"与"利用编辑"两种能力：从 9B 到 Opus 更新能力几乎持平，受益能力非单调、中档模型受益最大。

### 4.10 Autonomous Research & Industrial Evidence

> "AI 造 AI"的实证线：从端到端自动写论文，到 agent 主导交付 release-ready 前沿模型。Anthropic 的一手工业证据见 [§2](#2-core-readings)。

1. **iCoder: Recursive AI-Led Development of Frontier Industrial Coding Model.** Tech Report, 2026\. [report](https://huggingface.co/i-Coder/iCoder-27B/blob/main/Coder_Tech_Report.pdf), [code](https://github.com/bingreeky/iCoder), [model](https://huggingface.co/i-Coder/iCoder-27B), [PDF-en](papers/en/iCoder27B_TechReport.pdf), [PDF-zh](papers/zh/iCoder27B_TechReport_zh.pdf), [解读](reports/19_icoder.md)
_Cheng Yang, Jiayang Lyu, Shangyuan Liu, Guibin Zhang, et al. (SJTU / NUS / DP Technology)_ — 人类介入压缩为"高密度 prior、低频门控"五层接口，agent 主导 Data → SFT → OPSD → RLVR 全部运行时决策；RTLLM 68.0 超 GPT-5.5 / Opus 4.8，KernelBench L1 61 近两倍于 DeepSeek-V4-Pro。**本仓库计划以其代码库为后续开发基础。**
2. **The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery.** arXiv, 2024\. [paper](https://arxiv.org/abs/2408.06292), [code](https://github.com/SakanaAI/AI-Scientist), [PDF-en](papers/en/2408.06292_AIScientist.pdf), [PDF-zh](papers/zh/2408.06292_AIScientist_zh.pdf)
_Chris Lu, Cong Lu, Robert Tjarko Lange, Jakob Foerster, Jeff Clune, David Ha (Sakana AI)_ — auto-research 线的起点：端到端自动生成 ML 论文。
3. **ScientistOne: Towards Human-Level Autonomous Research via Chain-of-Evidence.** arXiv, 2026\. [paper](https://arxiv.org/abs/2605.26340), [PDF-en](papers/en/2605.26340_ScientistOne.pdf), [PDF-zh](papers/zh/2605.26340_ScientistOne_zh.pdf)
_Rui Meng, Bhavana Dalvi Mishra, Jiefeng Chen, Chun-Liang Li, et al. (Google Cloud AI Research)_ — 每条声明（引用 / 数值 / 方法 / 结论）必须回溯到证据源并过 Chain-of-Evidence 审计。
4. **Autodata: An Agentic Data Scientist to Create High Quality Synthetic Data.** arXiv, 2026\. [paper](https://arxiv.org/abs/2606.25996), [PDF-en](papers/en/2606.25996_Autodata.pdf), [PDF-zh](papers/zh/2606.25996_Autodata_zh.pdf)
_Ilia Kulikov, Chenxi Whitehouse, Tianhao Wu, Yixin Nie, et al. (FAIR at Meta)_ — challenger / 弱 solver / 强 solver / verifier 四角色合成"恰好难度"的数据。
5. **Why LLMs Aren't Scientists Yet: Lessons from Four Autonomous Research Attempts.** arXiv, 2026\. [paper](https://arxiv.org/abs/2601.03315), [PDF-en](papers/en/2601.03315_WhyLLMsArentScientistsYet.pdf), [PDF-zh](papers/zh/2601.03315_WhyLLMsArentScientistsYet_zh.pdf)
_Dhruv Trehan, Paras Chopra_ — 最小脚手架下 45–50 篇种子文档只有 1 个想法完整执行成论文；六个复发失败模式（训练数据默认偏置、实现漂移、过度乐观、科学品味弱……）。

### 4.11 Safety & Governance

> 把安全从"自评分的 README 承诺"变成机械可检查的东西：生产闭环、策略资产版本化、可证伪发布门、reward hacking 测量。合评见[报告 27](reports/27_safety_governance.md)。

1. **Yesterday's Shield, Today's Spear: A Self-Evolving Safety Guardrail in Production (SESG).** arXiv, 2026\. [paper](https://arxiv.org/abs/2608.08471), [PDF-en](papers/en/2608.08471_SESG.pdf), [PDF-zh](papers/zh/2608.08471_SESG_zh.pdf), [合评](reports/27_safety_governance.md)
_Cong Ming, Jingyi Chen, Bin Liu, Qi Chu, Tao Gong, Nenghai Yu, Yingfei Xiang, Ronghai Yang (中科大 / 深信服)_ — 1.7B 护栏 16–24 小时闭环新威胁（原 40–90h）；深信服产品主管线两个月自动闭合 14/15 新威胁。
2. **OpenLoopEvolve: A Verifiable Self-Evolution Framework for Loop Policies in Long-Horizon Complex Tasks (OLE).** arXiv, 2026\. [paper](https://arxiv.org/abs/2608.09380), [PDF-en](papers/en/2608.09380_OpenLoopEvolve.pdf), [PDF-zh](papers/zh/2608.09380_OpenLoopEvolve_zh.pdf), [合评](reports/27_safety_governance.md)
_Siqi Wang, Xinlin Li, Zhenglin Li, Li Li_ — 观察 / 规划 / 恢复 / 停止等控制行为做成有版本有血统的策略资产；Champion-Challenger 配对评估 + 劣化自动回滚到父版本。
3. **Falsifiable Release Gates for Self-Improving Systems: Standing Invariants at Scale.** arXiv, 2026\. [paper](https://arxiv.org/abs/2607.13070), [PDF-en](papers/en/2607.13070_FalsifiableReleaseGates.pdf), [PDF-zh](papers/zh/2607.13070_FalsifiableReleaseGates_zh.pdf), [合评](reports/27_safety_governance.md)
_Deepak Soni_ — 预声明的机器可检查验收套件 + 常驻不变量（六版本零修改，测试 122 → 563）；**收紧类修改自动应用、放松类必须人类合并、预测错自己 diff 效果的提议者自动关闭**。
4. **Hack-Verifiable Terminal Bench: Evaluating Reward Hacking in Terminal Tasks (HVTB).** arXiv, 2026\. [paper](https://arxiv.org/abs/2608.22103), [PDF-en](papers/en/2608.22103_HVTB.pdf), [PDF-zh](papers/zh/2608.22103_HVTB_zh.pdf), [合评](reports/27_safety_governance.md)
_Amit Roth, Ivan Bercovich, Yonathan Efroni (TAU / UCSB)_ — 蜜罐嵌入 89 个真实终端任务、2,225 条轨迹；gemini-3.1-pro 明令禁止下仍 16.3% 作弊，加警告反而从 47.7% 升到 59.8%；所有检出率只是下界。
5. **Audited Skill-Graph Self-Improvement for Agentic LLMs via Verifiable Rewards, Experience Synthesis, and Continual Memory (ASG-SI).** arXiv, 2025\. [paper](https://arxiv.org/abs/2512.23760), [PDF-en](papers/en/2512.23760_ASG-SI.pdf), [PDF-zh](papers/zh/2512.23760_ASG-SI_zh.pdf)
_Ken Huang, Jerry Huang_ — verifier-auditor 分离与密码学溯源的技能图自改进。
6. **Adversarial Reward Auditing for Active Detection and Mitigation of Reward Hacking (ARA).** arXiv, 2026\. [paper](https://arxiv.org/abs/2602.01750), [PDF-en](papers/en/2602.01750_ARA.pdf), [PDF-zh](papers/zh/2602.01750_ARA_zh.pdf)
_Mohammad Beigi, Ming Jin, Junshan Zhang, Qifan Wang, Lifu Huang_ — 把 reward hacking 建模为 Hacker 与 Auditor 的动态博弈，主动发现奖励模型漏洞。

### 4.12 Program Evolution Lineage

> Weng 博文 §3.3–3.4 的谱系：递归脚手架改进、自动 agent 设计、进化式程序搜索——2026 年 harness 工程的直接前身。

1. **Self-Taught Optimizer (STOP): Recursively Self-Improving Code Generation.** COLM, 2024\. [paper](https://arxiv.org/abs/2310.02304), [PDF-en](papers/en/2310.02304_STOP.pdf), [PDF-zh](papers/zh/2310.02304_STOP_zh.pdf)
_Eric Zelikman, Eliana Lorch, Lester Mackey, Adam Tauman Kalai (Stanford / MSR / OpenAI)_ — 用元效用递归改进"改进器"本身；GPT-4 上跨迭代改善、GPT-3.5 上退化——基础模型必须够强才能改进机制。
2. **Automated Design of Agentic Systems (ADAS).** ICLR, 2025\. [paper](https://arxiv.org/abs/2408.08435), [code](https://github.com/ShengranHu/ADAS), [PDF-en](papers/en/2408.08435_ADAS.pdf), [PDF-zh](papers/zh/2408.08435_ADAS_zh.pdf)
_Shengran Hu, Cong Lu, Jeff Clune_ — meta-agent 用代码编程新 agent 工作流，档案累积。
3. **AFlow: Automating Agentic Workflow Generation.** ICLR, 2025\. [paper](https://arxiv.org/abs/2410.10762), [code](https://github.com/FoundationAgents/AFlow), [PDF-en](papers/en/2410.10762_AFlow.pdf), [PDF-zh](papers/zh/2410.10762_AFlow_zh.pdf)
_Jiayi Zhang, Jinyu Xiang, Zhaoyang Yu, Fengwei Teng, Xiong-Hui Chen, et al._ — 工作流表示为图（节点 LLM 调用、边代码逻辑），MCTS 搜索。
4. **AlphaEvolve: A Coding Agent for Scientific and Algorithmic Discovery.** arXiv, 2025\. [paper](https://arxiv.org/abs/2506.13131), [PDF-en](papers/en/2506.13131_AlphaEvolve.pdf), [PDF-zh](papers/zh/2506.13131_AlphaEvolve_zh.pdf)
_Alexander Novikov, Ngân Vũ, Marvin Eisenberger, Emilien Dupont, Po-Sen Huang, et al. (Google DeepMind)_ — 候选程序池 + 冻结 LLM 生成 diff；EVOLVE-BLOCK 标注可改区域；适用于候选可自动评估的域。
5. **GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning.** ICLR (Oral), 2026\. [paper](https://arxiv.org/abs/2507.19457), [code](https://github.com/gepa-ai/gepa), [PDF-en](papers/en/2507.19457_GEPA.pdf), [PDF-zh](papers/zh/2507.19457_GEPA_zh.pdf)
_Lakshya A Agrawal, Shangyin Tan, Dilara Soylu, Noah Ziems, et al._ — 反思式提示进化超过 GRPO；Meta-Harness / AutoSaddler 的主要对照基线。
6. **ShinkaEvolve: Towards Open-Ended and Sample-Efficient Program Evolution.** arXiv, 2025\. [paper](https://arxiv.org/abs/2509.19349), [code](https://github.com/SakanaAI/ShinkaEvolve), [PDF-en](papers/en/2509.19349_ShinkaEvolve.pdf), [PDF-zh](papers/zh/2509.19349_ShinkaEvolve_zh.pdf)
_Robert Tjarko Lange, Yuki Imajuku, Edoardo Cetin (Sakana AI)_ — 父代采样平衡 + 代码新颖性拒绝采样 + meta-scratchpad 三件套提升采样效率。

### 4.13 Macro Debate & Measurement

> 微观加速 vs 宏观节奏的实证鸿沟（insight 8）与算力–认知劳动替代弹性 σ 之争（insight 9）的证据源。

1. **Explosive Growth from AI Automation: A Review of the Arguments.** arXiv, 2023\. [paper](https://arxiv.org/abs/2309.11690), [PDF-en](papers/en/2309.11690_ExplosiveGrowthReview.pdf), [PDF-zh](papers/zh/2309.11690_ExplosiveGrowthReview_zh.pdf)
_Ege Erdil, Tamay Besiroglu (Epoch AI)_ — 系统梳理"AI 自动化能否导致 >30%/年经济增长"的正反论证；σ > 1 是否成立被识别为关键参数。
2. **Will AI R&D Automation Cause a Software Intelligence Explosion?** Forethought Research, 2025\. [report](https://www.forethought.org/research/will-ai-r-and-d-automation-cause-a-software-intelligence-explosion)
_Daniel Eth, Tom Davidson_ — 把 Bostrom 的 recalcitrance 具体化为软件研发回报率 r，论证 r > 1 时算力不增也可爆炸。
3. **Measuring AI Ability to Complete Long Software Tasks.** arXiv, 2025\. [paper](https://arxiv.org/abs/2503.14499), [PDF-en](papers/en/2503.14499_METR_LongTasks.pdf), [PDF-zh](papers/zh/2503.14499_METR_LongTasks_zh.pdf)
_Thomas Kwa, Ben West, Joel Becker, et al. (METR)_ — 50% 任务时长地平线约每 7 个月翻倍：宏观节奏唯一的公开连续测量。

## 5. Deep-Dive Reports

29 份中文深度解读（[`reports/`](reports/)），统一七节结构：一句话定位 → 要解决的问题 → 为什么此前做不通 → 方法机制 → 实验结果全景 → 局限 → 意义与位置；每篇 2000–5200 字，数字可回溯到论文表号，末节与其他报告交叉引用。全部合订为 [149 页 PDF](report/awesome_rsi_full_report.pdf)。

| # | 报告 | 对象 | 一句话 |
|---|---|---|---|
| 00 | [起源 1965–2014](reports/00_origins_1965_2014.md) | Good / Yudkowsky / Schmidhuber / Bostrom + 四位中间人 | 四个坐标轴，以及前史没预见的评估器问题 |
| 01 | [Weng 总纲](reports/01_lilian_weng_harness_engineering.md) | Harness Engineering for Self-Improvement | harness 是可执行搜索空间；七条挑战的回应表 |
| 02 | [Anthropic 进度报告](reports/02_anthropic_when_ai_builds_itself.md) | When AI builds itself | 执行已自动化、品味是最后一环；按 crossover 判据仍是弱 RSI |
| 03 | [EvoLM](reports/03_evolm.md) | rubric 共进化 | 静态 RM 越准、policy 越差的 reward overoptimization 悖论 |
| 04 | [RQGM](reports/04_red_queen_godel_machine.md) | 受控效用进化 | 评估器可以进循环，但锚必须留在外面 |
| 05 | [Who Grades the Grader](reports/05_who_grades_the_grader.md) | 锚定纪律 | 任务分永远证明不了评估器没塌——全谱系最重要的否定性结论 |
| 06 | [ECHO](reports/06_echo.md) | critic–policy 双轨 GRPO | 冻结 critic 低于裸 GRPO：陈旧反馈有害 |
| 07 | [DGM](reports/07_darwin_godel_machine.md) | 开放式档案自改写 | 证明门 → 基准门的松弛与代价 |
| 08 | [MOSS](reports/08_moss.md) | 生产级源码自改写 | 文本层物理够不着 harness 故障；批准 / 回滚门控 |
| 09 | [WikiSkill](reports/09_wikiskill.md) | 经验 → wiki → 技能 | 知识永不回滚、技能严格门控的不对称 |
| 10 | [汇总洞察](reports/10_synthesis_insights.md) | 全部材料 | 两轴地图 + 十条 insight + 18 系统冻结锚表 + 九个开放问题 |
| 11 | [Continual Harness](reports/11_continual_harness.md) | 免重置 + 模型–harness 共学习 | 能力地板；第一个共学习闭环 |
| 12 | [TMLR 综述](reports/12_self_evolving_agents_survey.md) | What / When / How / Where | 图书馆学而非力学 |
| 13 | [Meta-Harness](reports/13_meta_harness.md) | 外部 proposer 读全历史 | 原始执行轨迹是唯一关键成分 |
| 14 | [Self-Harness](reports/14_self_harness.md) | 模型改自己的 harness | 回归门让 35B 走通循环——地板 = 模型 × 接受机制 |
| 15 | [EnvHarness](reports/15_envharness.md) | 环境侧进化 | 让出题人进化、裁判钉死 |
| 16 | [AutoSaddler](reports/16_autosaddler.md) | mini-batch harness 学习 | 无泛化门时自改进是负收益 |
| 17 | [MetaCaster](reports/17_metacaster.md) | 时序预测垂直落地 | 数字当裁判；harness 比骨干重要 |
| 18 | [Prime Agent](reports/18_prime_agent.md) | 免重置产品化 | 评测测的是模型还是壳；RCON 作弊被固化 |
| 19 | [iCoder](reports/19_icoder.md) | AI 主导开发 27B 模型 | 人类到底还握着什么：五层 prior 边界表 |
| 20 | [Metan](reports/20_metan.md) | 冻结 Ω、递归输入 | 不改机器也能拿到深度；72% 增益来自条件化 |
| 21 | [Co-Harness](reports/21_co_harness.md) | harness–权重双环 | 把有效脚手架蒸馏进权重；Harness Debt 为负 |
| 22 | [Co-Evolution 综述](reports/22_coevolution_survey.md) | 三阶段递进 | 只有 RQGM 越过 Meta 线；Red Queen 是警告不是承诺 |
| 23 | [Gödel Agent → SICA](reports/23_godel_agent_to_sica.md) | 2024–2025 桥接 | 证明门换成效用门，监督者第一次进场 |
| 24 | [EvalCEGAR](reports/24_evalcegar.md) | 碰撞对驱动评估器进化 | 锚利用效率最高的设计 |
| 25 | [RHO](reports/25_rho.md) | 完全无锚自偏好 | 单轮 59 → 78；多轮是对锚定纪律最直接的检验 |
| 26 | [技能进化红海](reports/26_skill_evolution_wave.md) | SkillCommit / HyperSkill / ERSkill / SkillProx / Evo-Harness | 抽象优于存储是共识，编译成什么结构是开放的 |
| 27 | [安全与治理](reports/27_safety_governance.md) | SESG / OLE / HarnessFix / Gates / HVTB | 锚在安全域的三种形态：不变量、蜜罐、红队集 |
| 28 | [Coding Agents 综述](reports/28_self_evolving_coding_agents_survey.md) | 对象 × 时间 × 证据 | 可执行反馈是红利也是风险——错误会被持久化 |

## 6. Insights & Open Problems

**十条核心 insight**（完整论证见[报告 10](reports/10_synthesis_insights.md)）

1. 评估器是双重瓶颈：既是能力上限，又是攻击靶点
2. "无锚不进化"成为共识设计原则——AutoSaddler 去门负收益 vs RHO 单轮无锚 +0.19 是当前最需裁决的分歧
3. 评估器与策略的相对速度决定系统命运：优化期间尺子必须冻结
4. 自改写深度存在结构性上限（≈ 2.5），Metan"改输入不改机器"绕行
5. 发现与执行是两种能力，技能是可交易资产——但 Metan 的 72/15 提示条件化可能比技能库更值钱
6. 经验必须先编译成知识才能复利；编译是必要的，结构是开放的
7. 生产落地的分水岭是"自改进资产化"：版本化、可审计、可预测、可回滚
8. 微观加速与宏观节奏之间存在实证鸿沟（METR：无公司报告 2× 节奏）
9. 算力–认知劳动替代弹性 σ 是宏观争论的单一关键参数
10. 测量基础设施本身正在成为一级瓶颈

**开放问题**（按可检验性排序）

1. **最小锚问题**：维持评估器不塌缩所需的人工锚定量下界？（WGtG 十条、EvalCEGAR 十个碰撞对是两个数据点）
2. **无锚自偏好能否多轮单调**：RHO 只测一轮；若单调，insight 2 改为"无锚不**可验证地**进化"
3. **技能库 vs 条件化**：Metan 的 72/15 比例在技能进化场景是否成立？需要"技能作为 prompt 前缀 vs 作为可执行程序"的受控实验
4. **harness 收益曲线能否预测**：地板之下为负、中段最大、天花板附近饱和——能否从基座能力事先预测收益符号？
5. **评测测的是模型还是壳**：基准报告是否应强制附带 harness 规格与 harness-normalized 分数？
6. **crossover 的可操作测量**：iCoder 的"逐步降低 prior 密度看性能何时崩"能否成为标准协议？
7. **品味可否被编译**：wiki / 技能层能否沉淀"方向判断"而不只是"流程知识"？
8. **跨代锚漂移**：RQGM 的 epoch 边界换尺、SESG 的 v0 → v6——锚本身的更新由谁验证？
9. **宏观加速何时显形**：若 2027 年 METR 仍测不到 2× 节奏，是 Amdahl 串行瓶颈成立，还是加速被"做更多实验"消化？
10. **σ 之争的实验裁决**：随机分配算力预算的受控实验何时有人做？

## 7. Reference

### 7.1 Glossary

| 术语 | 含义 | 出处 |
|---|---|---|
| **RSI（递归自改进）** | 不是"系统反复改进自身"，而是"一次改进提升了系统发现、验证、实现下一次改进的能力"——改进能力本身进入优化闭环 | Bostrom 2014 · 报告 00 |
| **crossover point / recalcitrance** | 系统自身贡献开始主导后续改进的时刻 / 系统对改进的阻力；增长率 = optimization power ÷ recalcitrance | Bostrom 2014 · 报告 00 |
| **Harness** | 基座模型之外决定信息流的一切：编排、规划、工具调用、上下文管理、评估；Weng 论点——harness 是可执行的搜索空间 | 报告 01 |
| **三层改进面** | 文本层（prompt / 技能，快环）、权重层（微调，慢环）、源码层（改 harness 代码，最后手段）；2026 共识是分层分工而非三选一 | 报告 10 |
| **锚定纪律（anchor discipline）** | 所有能跑的自进化系统都保留一个不参与进化的 ground-truth 部件（人工标注集 / 冻结 PRM / 原始验证器 / 冻结 proposer / dev 门） | 报告 05 · 11 · 15 · 16 |
| **评估器塌缩 / 观测等价** | 评估器被 game 与真进化在任务分数上不可区分，必须引入进化外的锚才能分辨 | 报告 05 |
| **reward overoptimization** | 静态奖励模型判分精度越高、训出的策略反而越差——策略利用了固定判据 | 报告 03 |
| **critic staleness** | 静态 critic 跟不上 policy 的分布偏移，反馈效用递减甚至转负；解法是 critic 与 policy 同步更新 | 报告 06 |
| **免重置 vs 重置式** | 重置式（DGM / RQGM / GEPA）的效用信号来自完整评测；免重置（Continual Harness / Prime Agent）在故障现场修 harness，可达 episode 深处的失败模式 | 报告 11 · 18 |
| **能力地板（capability floor）** | 基座能力低于阈值时更强的脚手架只会让它更迷茫（CH）；但 Self-Harness 显示回归门"改坏即拒"能保护地板——地板是"模型 × 接受机制"的联合属性 | 报告 11 · 14 |
| **Harness Debt** | 在补偿模型弱点的脚手架下训练，模型可能依赖脚手架而裸测退步；Co-Harness 实测每轮裸测精度上升，债务为负 | 报告 21 |
| **realized meta-depth** | 系统中行为真正发生变化的最高 meta 层级；自改写系统因需冻结驱动层卡在约 2.5，Metan 以"冻结 Ω、递归输入"绕行，停在 3–6 | 报告 20 |
| **harness 资产化** | 优化后的 harness 可跨模型迁移（Meta-Harness 5 模型 +4.7；AutoSaddler Opus 调 Haiku 用 +5.6；MetaCaster 四骨干波动 < 0.1） | 报告 13 · 16 · 17 |
| **高密度低频接口** | 把专家经验一次性编码为 prior（目标 / 脚手架 / 权限 / 验证 / 证据纪律），运行期只在权限变更时介入——iCoder 对"人类还握什么"的工程答案 | 报告 19 |
| **过程级测试** | 评估共进化系统不能只看任务分：历史交叉对弈、组件消融、held-out 评估器三件套 | 报告 22 |
| **错误持久化** | 自进化特有风险：不可靠的测试结果、噪声轨迹或基准捷径会被存进记忆、蒸馏成技能、更新进模型——单次推理错一次，自进化错了会复利 | 报告 28 |

### 7.2 Timeline

| 时间 | 事件 | 报告 |
|---|---|---|
| 1965 | Good 提出 intelligence explosion | 00 |
| 1993 | Vinge 命名"奇点"，列出四条路径 | 00 |
| 2000–01 | Yudkowsky GISAI：Seed AI 三能力 + "每级须开新机会" | 00 |
| 2003 | Schmidhuber Gödel Machine：自指完备的形式化极限 | 00 |
| 2008–13 | Omohundro 工具性驱力 → Chalmers 形式化论证 → Yudkowsky IEM 认知再投资回报率 | 00 |
| 2014 | Bostrom《Superintelligence》：crossover / recalcitrance 动力学 | 00 |
| 2023 | Voyager 可增长技能库；STOP 递归自改进代码生成；Erdil & Besiroglu 爆炸增长综述 | 23 |
| 2024 | ADAS / AFlow 自动 agent 设计；AI Scientist 端到端自动研究；**Gödel Agent** 首个 LLM 版 Gödel Machine | 23 |
| 2025 H1 | METR 任务地平线 7 个月翻倍；**SICA** 17 → 53% 并引入异步监督者；**DGM** 开放式档案自改写 | 23 · 07 |
| 2025 H2 | AlphaEvolve / ShinkaEvolve 程序进化；GEPA 反思提示进化超 RL；TMLR 自进化综述；ACE 上下文进化 | 12 |
| 2026 Q1 | **ECHO** critic 共进化；MCE；SkillRL；HyperAgents；**Meta-Harness** | 06 · 13 |
| 2026 Q2 | AHE；**EvoLM**；**Continual Harness**；**MOSS**；Evolving-RL；SIA；**Self-Harness**；**RQGM**；RHO / HarnessFix / Adaptive Auto-Harness / SCORE | 03 · 04 · 08 · 11 · 14 · 25 |
| 2026 Q3 | Weng 总纲；Anthropic 进度报告；**Who Grades the Grader**；**Co-Harness**；Falsifiable Gates；技能红海五篇；**EnvHarness** / **AutoSaddler** / **MetaCaster** / **Prime Agent**；**Metan**；**WikiSkill**；EvalCEGAR；SESG / OLE / HVTB；两份综述；**iCoder** | 01 · 02 · 05 · 09 · 15–22 · 24 · 26–28 |

### 7.3 System Comparison Matrix

20 个核心系统在本调研四条主轴上的坐标（数字均可在对应报告中找到出处）：

| 系统 | 改哪层 | 锚在哪（不参与进化的部件） | 重置式 / 免重置 | 生产部署 | 一个关键数字 | 报告 |
|---|---|---|---|---|---|---|
| DGM | 源码（harness 代码库） | 固定基准 + 沙箱人审 | 重置式 | 否 | SWE-bench Verified 20.0 → 50.0% | 07 |
| MOSS | 源码（生产 agent） | 失败重放 + 批准 / 回滚门 | 重置式 | 是 | 单轮 0.25 → 0.61；代码门 100% 生效 | 08 |
| EvoLM | 权重（policy + rubric 生成器） | 训练环内的 rubric 共进化 | 重置式 | 否 | 静态 RM 越准、policy 越差 | 03 |
| RQGM | harness + 评估器 | epoch 内冻结评估器 + 人类锚数据集 | 重置式 | 否 | 论文写作接受率 40.5% vs 21.8%（1.86×） | 04 |
| Who Grades the Grader | 文本技能 + 评估指标 | 人工锚定集（十条） | 重置式 | 否 | 评估器塌缩与真进化观测等价 | 05 |
| ECHO | 权重（critic + policy 双路 GRPO） | 环境结果奖励 | 重置式 | 否 | 77.85 vs GRPO 70.57；冻结 critic 68.58 < GRPO | 06 |
| WikiSkill | 文本（经验 → wiki → 技能） | 验证集 + skill-impact 审计 | 重置式 | 否 | Proposer 有 wiki +15.0；9B+技能 > 27B | 09 |
| Continual Harness | 文本四组件 + 权重共学习 | 冻结 PRM + 前沿教师 | **免重置** | 否 | Pro 100%/$130 vs 98%/$215；Flash-Lite 能力地板 | 11 |
| Meta-Harness | 源码（harness 代码） | 冻结外层 proposer + 搜索集 | 重置式 | 否 | TB2 76.4% vs 手工 74.7%；轨迹是唯一关键成分 | 13 |
| Self-Harness | harness 配置面 | 回归门（held-in / held-out 双 split） | 重置式 | 否 | 9/9 双升，最大 +132% | 14 |
| EnvHarness | **环境**（Stage / Contract / Chain） | 原任务与人写验证器不动 | 重置式 | 否 | ALFWorld OOD +9.0；静态环境技能可为负资产 | 15 |
| AutoSaddler | prompt + 工具 + 中间件 | dev 集泛化门 + EvoDAG 回滚 | 重置式 | 否 | 去掉 dev 门 50.6 跌破未优化 53.0 | 16 |
| MetaCaster | 文本（系统提示 + 技能库） | 真实测试集数字裁判（仅元训练期） | 重置式 | 否 | 四骨干互换波动 0.267–0.366 | 17 |
| Prime Agent | 文本 harness + 持久 REPL | 环境奖励（无独立锚 → 作弊被固化为技能） | **免重置** | 是（开源 harness） | ARC-AGI-3 官方壳 30.2% → 95.5% | 18 |
| iCoder | **权重**（27B 前沿模型） | 官方 verifier 锁死 + 人类权限门 | 重置式 | 是（release-ready） | RTLLM 68.0 超 GPT-5.5 / Opus 4.8 | 19 |
| Metan | 文本预处理 + helper 代码库 | 基准验证分 + 进化档案（Ω 自身冻结） | 重置式 | 否 | ARC-AGI-2 0.331 唯一非零；72% 增益来自条件化 | 20 |
| Co-Harness | harness diff + 权重 | 验证集 + 归因分类法 + 版本化回滚 | 重置式（离线批次） | 否 | 平均 +20.4 pp，超人工 harness +24.7 | 21 |
| EvalCEGAR | **评估器**（算子池） | 训练 split 的 oracle 碰撞对 | — | 否 | 55 行算子关闭 15.4% 差距（p = 0.001） | 24 |
| RHO | Skills + Tools | **无**（成对自偏好） | 重置式（需重放） | 否 | SWE-Bench Pro 0.59 → 0.78（单轮） | 25 |
| SESG | 权重（1.7B 护栏） | 红队测试集 + 人工约 2h/威胁 | — | 是（深信服主管线） | 两个月自动闭合 14/15 新威胁 | 27 |

读法：**"锚在哪"一列没有空白**——除 RHO 明确选择无锚（且只测单轮）外，所有能跑的系统都保留了一个不参与进化的部件；**"生产部署"一列只有五个"是"**，且其中 MOSS / iCoder / SESG 的锚都是最保守的形态（门控、锁死、人工标注）。

## 8. Secondary Sources (中文导读)

本调研的信息源与配套中文解读，按被引用的仓库分节排列：

- 小红书 · **RSI 六篇论文导读帖**（§4.4–4.6 六篇 ⭐ 论文的最初信息源）— [post](https://www.xiaohongshu.com/explore/6a93e8a3000000001f000d72)
- 微信 · **Continual Harness 中文解读**（§4.8）— [article](https://mp.weixin.qq.com/s/xMuLJvX3kwRUUw5WQ7R3ww)
- 微信 · **Harness 自进化全景：三种范式与六个系统**（§4.9 Self-Harness / Meta-Harness / AutoSaddler / EnvHarness / Prime Agent / MetaCaster 导读）— [article](https://mp.weixin.qq.com/s/Lm_hmnkeeWlN6zVGlBBphw)
- 微信 · **Agentic RL 系列**（上：环境、轨迹、Reward 与训练闭环 — [article](https://mp.weixin.qq.com/s/Ly2BvP3y2bFB9czGqRguWQ)；中：SkillRL — [article](https://mp.weixin.qq.com/s/wqMM1D4NZQmRtWOcebuhTA)；下：Evolving-RL — [article](https://mp.weixin.qq.com/s/bu3-RyqaYPdA1mH79oF39g)）（§4.6）
- 微信 · **AI 到底能不能自己造 AI？别吵了，有人做出来了**（iCoder，§4.10）— [article](https://mp.weixin.qq.com/s/28q7O59IzEXl_tiWulYbDA)
- 微信 · **一篇 Self-Evolving Coding Agents 最新综述**（§4.3）— [article](https://mp.weixin.qq.com/s/hSrJLcZN3j7J7X02N2HIMg)
- 2026 年 6–8 月趋势扫描原始笔记（19 篇新论文 + 9 项工业动态 + 7 项基准动态 + 8 项安全治理）— [`assets/trends_research_raw.md`](assets/trends_research_raw.md)

## 9. Repository Layout & Build

```
awesome_rsi/
├── README.md · CONTRIBUTING.md
├── report/
│   ├── awesome_rsi_slides.html / .pdf        # 34 页汇总 PPT（方向键翻页，P 键打印）
│   └── awesome_rsi_full_report.html / .pdf   # 149 页全文合订（29 份解读 + 封面 + 目录 + 两图）
├── reports/                                  # 29 份深度解读 00–28（索引见 §5）
├── papers/
│   ├── en/                                   # 61 篇英文原版 PDF（arXiv + iCoder 技术报告）
│   ├── zh/                                   # 61 篇中文翻译 PDF，与 en/ 一一对应
│   └── classics/                             # 6 篇起源经典（Good 1965 扫描件无文本层，其余 5 篇含中译）
├── assets/
│   ├── fig1_timeline.svg · fig2_taxonomy.svg # 纵览图（+ _dark 变体供 PPT）
│   ├── fulltext/                             # 论文提取全文（解读撰写底稿）
│   └── trends_research_raw.md                # 2026H2 趋势扫描笔记
├── scripts/
│   ├── make_figures.py                       # 生成两张纵览图
│   ├── build_full_report.py                  # pandoc 合订 reports/*.md → HTML → Chrome PDF
│   └── translate_batch5.sh                   # 批量中译（三条可并行队列）
└── logs/                                     # 翻译日志
```

**重建产物**：`python3 scripts/make_figures.py` 重出两图；`python3 scripts/build_full_report.py --pdf` 重建全文报告；slides PDF 用 Chrome headless `--print-to-pdf` 生成。

**翻译管线**：中文 PDF 由 [super_translate](https://github.com/asimfish/super_translate) 生成——冻结公式 / 图表等结构对象 → 术语注入 → 按原坐标替换文本 → QA 审计 + 确定性修复环；后端 DeepSeek API，逐篇带翻译缓存。翻译保留原版式与页码，适合与英文版对照精读；术语与公式以英文原版为准。批量脚本见 `scripts/translate_batch5.sh`。

## 10. Roadmap

- **基座**：以 [iCoder](https://github.com/bingreeky/iCoder) 代码库为后续开发基础，复用其 Research Skills 表示、治理四件套（任务队列 / 实验日志 / 决策记录 / 审批门）与 Data → SFT → OPSD → RLVR 可回退状态机（评估见[报告 19](reports/19_icoder.md)）。
- **待验证的设计选择**：harness 改写走 Meta-Harness 式全轨迹自由改写（[13](reports/13_meta_harness.md)）还是 AutoSaddler 式归因约束局部 diff（[16](reports/16_autosaddler.md)）；权重环走 Co-Harness 离线批次（[21](reports/21_co_harness.md)）还是 Continual Harness 在线共学习（[11](reports/11_continual_harness.md)）。
- **不可妥协项**：进化外的独立锚（[05](reports/05_who_grades_the_grader.md)）、回归门（[14](reports/14_self_harness.md)）、版本化回滚（[08](reports/08_moss.md) / [21](reports/21_co_harness.md)）、过程级测试三件套（[22](reports/22_coevolution_survey.md)）。
- **持续维护**：新论文按 §4 格式追加并入库 PDF-en / PDF-zh；重点论文补深度解读（模板见 [CONTRIBUTING](CONTRIBUTING.md)）；之后重建全文报告、按需更新两图，并同步 slides 与本 README 的计数。

## 11. Related Resources

- [iSEngLab/Awesome-Self-Evolving-Coding-Agents](https://github.com/iSEngLab/Awesome-Self-Evolving-Coding-Agents) — arXiv 2608.03392 综述的配套清单，按进化对象六类组织，编码域最全；与本仓库互补、已互相收录（解读见[报告 28](reports/28_self_evolving_coding_agents_survey.md)）
- [CharlesQ9/Self-Evolving-Agents](https://github.com/CharlesQ9/Self-Evolving-Agents) — TMLR 综述配套清单
- [Thinklab-SJTU/awesome-ml4co](https://github.com/Thinklab-SJTU/awesome-ml4co) — 本仓库编目格式的参考规范
- [asimfish/super_translate](https://github.com/asimfish/super_translate) — 本仓库全部中文 PDF 的翻译工具
- [Lil'Log · Harness Engineering for Self-Improvement](https://lilianweng.github.io/posts/2026-07-04-harness/) — 本调研的总纲，其参考文献是 §4.9 / §4.12 的种子

## 12. Disclaimer & Credits

- 论文 PDF 版权归原作者与 arXiv 所有，本仓库仅作研究备份与学习用途；中文翻译为机器翻译，引用请以英文原文为准。
- 深度解读、slides 与两张纵览图为本仓库原创内容（CC BY 4.0），转载注明出处。
- 欢迎 PR 补充新论文，条目格式与解读模板见 [CONTRIBUTING.md](CONTRIBUTING.md)。
