# Awesome Recursive Self-Improvement (RSI) Resources

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
![papers](https://img.shields.io/badge/papers-32%2B3_classics-blue)
![reports](https://img.shields.io/badge/reports-20-red)
![zh-PDF](https://img.shields.io/badge/zh--PDF-19-green)
![slides](https://img.shields.io/badge/slides-26p-orange)

围绕 **Recursive Self-Improvement（递归自改进）** 的论文与资源列表 + 系统性调研仓库（2026-08-31 完成）。与一般 awesome 列表不同，本仓库同时提供：

- **20 份中文精读报告**（`reports/`，逐篇拆方法、数字、局限与谱系定位，含 00 起源前史）
- **32 篇论文英文原版 PDF + 3 篇起源经典（1965-2003）+ 保版式中文翻译 PDF**（`papers/`，由 [super_translate](https://github.com/asimfish/super_translate) 生成）
- **26 页汇总报告**（`awesome_rsi_slides.html` 方向键翻页 / `awesome_rsi_slides.pdf`）

一句话结论：**执行已经自动化，品味正在被编译，锚是最后的手工业**——所有能跑的自进化系统都保留一个不参与进化的 ground-truth 锚；谁能工业化地生产不可 game 的锚，谁就握住了 RSI 的节流阀。

核心材料（本调研的十份精读对象）以 ⭐ 标记。

## Content

| [1. Start Here](#1-start-here)                          |                                                              |
| ------------------------------------------------------- | ------------------------------------------------------------ |
| [2. Core Readings](#2-core-readings)                    | [2.5 Origins (1965-2014)](#25-origins-1965-2014)              |
| [3. Papers](#3-papers)                                  |                                                              |
| [3.0 Surveys](#30-surveys)                              | [3.1 Framework Side](#31-framework-side)                      |
| [3.2 Evaluator Side](#32-evaluator-side)                | [3.3 Model Side](#33-model-side)                              |
| [3.4 Knowledge Side](#34-knowledge-side)                | [3.5 Online Side](#35-online-side)                            |
| [3.6 Harness & Self-Evolving Agent Lineage](#36-harness--self-evolving-agent-lineage) | [4. Frontier Tracking (2026 H2)](#4-frontier-tracking-2026-h2) |
| [5. Ten Insights](#5-ten-insights)                      | [6. Reading Routes](#6-reading-routes)                        |
| [7. Repository Layout](#7-repository-layout)            | [8. Translation Pipeline](#8-translation-pipeline)            |
| [9. Disclaimer & Credits](#9-disclaimer--credits)       |                                                              |

## 1. Start Here

| 时间预算 | 路线 |
|---|---|
| 15 分钟 | 打开 [`awesome_rsi_slides.html`](awesome_rsi_slides.html)（浏览器方向键翻页，P 键打印）或 [`awesome_rsi_slides.pdf`](awesome_rsi_slides.pdf) |
| 2 小时 | [汇总报告](reports/10_synthesis_insights.md) → [总纲解读](reports/01_lilian_weng_harness_engineering.md) → [Who Grades the Grader 解读](reports/05_who_grades_the_grader.md)（全谱系最重要的否定性结论） |
| 系统研读 | `reports/` 按 00→01→02→07→03→04→05→06→08→11→09→10 顺序（谱系扩编 12-18 与 iCoder 19 按需精读），配 `papers/zh/` 中文 PDF 对照原文 |

## 2. Core Readings

总纲与工业证据（非论文类核心材料）：

1. ⭐ **Harness Engineering for Self-Improvement.** Lil'Log, 2026\. [blog](https://lilianweng.github.io/posts/2026-07-04-harness/), [解读](reports/01_lilian_weng_harness_engineering.md)
_Lilian Weng_
2. ⭐ **When AI Builds Itself: Anthropic's Progress toward Recursive Self-Improvement.** Anthropic Institute, 2026\. [article](https://www.anthropic.com/institute/recursive-self-improvement), [解读](reports/02_anthropic_when_ai_builds_itself.md)
_Anthropic_
3. **RSI 六篇论文导读帖**（本调研 3.1-3.3 节六篇论文的最初信息源）. 小红书, 2026\. [post](https://www.xiaohongshu.com/explore/6a93e8a3000000001f000d72)
4. **Continual Harness 中文解读.** 微信公众号「X0后的回忆」, 2026\. [article](https://mp.weixin.qq.com/s/xMuLJvX3kwRUUw5WQ7R3ww)
5. **Harness 自进化全景：三种范式与六个系统的实现思路**（Self-Harness / Meta-Harness / AutoSaddler / EnvHarness / Prime Agent / MetaCaster 六系统导读）. 微信公众号, 2026\. [article](https://mp.weixin.qq.com/s/Lm_hmnkeeWlN6zVGlBBphw)
6. **Agentic RL 系列（上）：环境、轨迹、Reward 与训练闭环.** 微信公众号, 2026\. [article](https://mp.weixin.qq.com/s/Ly2BvP3y2bFB9czGqRguWQ)
7. **Agentic RL 系列（中）：SkillRL，如何把一次失败变成可复用的 Skill.** 微信公众号, 2026\. [article](https://mp.weixin.qq.com/s/wqMM1D4NZQmRtWOcebuhTA)
8. **Agentic RL 系列（下）：Evolving-RL，用 Reward 训练 Agent 总结经验.** 微信公众号, 2026\. [article](https://mp.weixin.qq.com/s/bu3-RyqaYPdA1mH79oF39g)
9. **AI到底能不能自己造AI？别吵了，有人做出来了**（iCoder 中文解读）. 微信公众号, 2026\. [article](https://mp.weixin.qq.com/s/28q7O59IzEXl_tiWulYbDA)

## 2.5 Origins (1965-2014)

RSI 概念的思想起源四篇（逐篇拆解见[解读报告 00](reports/00_origins_1965_2014.md)）：Good 给正反馈直觉，Yudkowsky 给能力构造与持续条件，Schmidhuber 给自指完备的形式化极限，Bostrom 给进入强 RSI 的动力学判据（crossover）。

1. ⭐ **Speculations Concerning the First Ultraintelligent Machine.** Advances in Computers Vol. 6, 1965\. [paper](http://incompleteideas.net/papers/Good65ultraintelligent.pdf), [PDF](papers/classics/1965_Good_UltraintelligentMachine.pdf)（扫描影印版，无文本层）, [解读](reports/00_origins_1965_2014.md)
_Irving John Good_ — 提出 intelligence explosion："设计机器本身也是一种智力活动，超智能机器可以设计出更好的机器"，智能提升提高产生进一步提升的能力，形成正反馈。
2. ⭐ **General Intelligence and Seed AI 2.3.** Singularity Institute, 2000-2001\. [web archive](https://web.archive.org/web/20120805130100/singularity.org/files/GISAI.html), [PDF](papers/classics/2001_Yudkowsky_GISAI.pdf), [PDF-zh](papers/classics/2001_Yudkowsky_GISAI_zh.pdf), [解读](reports/00_origins_1965_2014.md)
_Eliezer Yudkowsky_ — 描述具备 self-understanding / self-modification / recursive self-improvement 的 Seed AI；指出让固定优化器跑得更快不能维持递归改进，每一级提升必须让系统看到或实现新的改进机会。
3. ⭐ **Gödel Machines: Self-Referential Universal Problem Solvers Making Provably Optimal Self-Improvements.** arXiv, 2003\. [paper](https://arxiv.org/abs/cs/0309048), [PDF](papers/classics/2003_Schmidhuber_GoedelMachines.pdf), [PDF-zh](papers/classics/2003_Schmidhuber_GoedelMachines_zh.pdf), [解读](reports/00_origins_1965_2014.md)
_Juergen Schmidhuber_ — 寻找 improvement 的机制本身也在可修改集合里；proof searcher 找到"自改写收益可证明更高"的证明才执行改写。
4. ⭐ **Superintelligence: Paths, Dangers, Strategies.** Oxford University Press, 2014\. [book](https://global.oup.com/academic/product/superintelligence-9780199678112), [解读](reports/00_origins_1965_2014.md)
_Nick Bostrom_ — 把 RSI 放入 optimization power / recalcitrance 动力学；crossover point：系统自身贡献开始主导后续改进即进入 strong RSI。判据："When the AI improves itself, it improves the thing that does the improving"——一次改进是否同时提升发现、验证、实现下一次改进的能力。

## 3. Papers

> 分类沿用本调研的五侧地图：**框架侧**（改 harness 源码）、**评估侧**（评估器共进化）、**模型侧**（critic 与权重）、**知识侧**（经验编译为技能）、**在线侧**（免重置在线适应）。每条提供 arXiv 链接、仓库内英文/中文 PDF 与精读报告的相对链接。

### 3.0 Surveys

1. **A Survey of Self-Evolving Agents: What, When, How, and Where to Evolve on the Path to Artificial Super Intelligence.** TMLR, 2026\. [paper](https://arxiv.org/abs/2507.21046), [PDF-en](papers/en/2507.21046_SelfEvolvingAgentsSurvey.pdf), [PDF-zh](papers/zh/2507.21046_SelfEvolvingAgentsSurvey_zh.pdf), [解读](reports/12_self_evolving_agents_survey.md)
_Huan-ang Gao, Jiayi Geng, Wenyue Hua, Mengkang Hu, Xinzhe Juan, Hongzhang Liu, Shilong Liu, Jiahao Qiu, et al._

另见 4 节趋势中以共进化为中心轴的综述 [Co-Evolution in Agentic Systems](https://arxiv.org/abs/2608.10299)。

### 3.1 Framework Side

> 自改进的工程化基线与生产部署：agent 直接改写自己的 harness 代码库。

1. ⭐ **Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents.** ICLR, 2026\. [paper](https://arxiv.org/abs/2505.22954), [code](https://github.com/jennyzzt/dgm), [PDF-en](papers/en/2505.22954_DGM.pdf), [PDF-zh](papers/zh/2505.22954_DGM_zh.pdf), [解读](reports/07_darwin_godel_machine.md)
_Jenny Zhang, Shengran Hu, Cong Lu, Robert Lange, Jeff Clune_
2. ⭐ **MOSS: Self-Evolution through Source-Level Rewriting in Autonomous Agent Systems.** arXiv, 2026\. [paper](https://arxiv.org/abs/2605.22794), [PDF-en](papers/en/2605.22794_MOSS.pdf), [PDF-zh](papers/zh/2605.22794_MOSS_zh.pdf), [解读](reports/08_moss.md)
_Qianshu Cai, Yonggang Zhang, Xianzhang Jia, Huajiang Zheng, Wei Xue, Jun Song, Xinmei Tian, Yike Guo_

### 3.2 Evaluator Side

> 评估器不再是固定裁判：rubric 共进化、受控效用进化、锚定纪律——以及"评估器塌缩与真进化观测等价"的否定性结论。

1. ⭐ **EvoLM: Self-Evolving Language Models through Co-Evolved Discriminative Rubrics.** arXiv, 2026\. [paper](https://arxiv.org/abs/2605.03871), [code](https://github.com/stellalisy/EvoLM), [PDF-en](papers/en/2605.03871_EvoLM.pdf), [PDF-zh](papers/zh/2605.03871_EvoLM_zh.pdf), [解读](reports/03_evolm.md)
_Shuyue Stella Li, Rui Xin, Teng Xiao, Yike Wang, Rulin Shao, Zoey Hao, Melanie Sclar, Sewoong Oh, Faeze Brahman, Pang Wei Koh, Yulia Tsvetkov_
2. ⭐ **The Red Queen Gödel Machine: Co-Evolving Agents and Their Evaluators.** arXiv, 2026\. [paper](https://arxiv.org/abs/2606.26294), [PDF-en](papers/en/2606.26294_RQGM.pdf), [PDF-zh](papers/zh/2606.26294_RQGM_zh.pdf), [解读](reports/04_red_queen_godel_machine.md)
_Alex Iacob, Andrej Jovanović, William F. Shen, Daniel Burkhardt, Meghdad Kurmanji, et al._
3. ⭐ **Who Grades the Grader? Co-Evolving Evaluation Metrics and Skills for Self-Improving LLM Agents.** arXiv, 2026\. [paper](https://arxiv.org/abs/2607.12790), [PDF-en](papers/en/2607.12790_WhoGradesTheGrader.pdf), [PDF-zh](papers/zh/2607.12790_WhoGradesTheGrader_zh.pdf), [解读](reports/05_who_grades_the_grader.md)
_Xing Zhang, Guanghui Wang, Yanwei Cui, Ziyuan Li, Wei Qiu, Bing Zhu, Peiyang He_

### 3.3 Model Side

> 把共进化推进到权重层：critic 与 policy 双路同步更新，解决 critic 滞后于 policy 分布偏移。

1. ⭐ **No More Stale Feedback: Co-Evolving Critics for Open-World Agent Learning (ECHO).** arXiv, 2026\. [paper](https://arxiv.org/abs/2601.06794), [PDF-en](papers/en/2601.06794_ECHO.pdf), [PDF-zh](papers/zh/2601.06794_ECHO_zh.pdf), [解读](reports/06_echo.md)
_Zhicong Li, Lingjie Jiang, Yulan Hu, Xingchen Zeng, Yixia Li, Xiangwen Zhang, Guanhua Chen, Zheng Pan, Xin Li, Yong Liu_

### 3.4 Knowledge Side

> 经验必须先编译成结构化知识（wiki）再蒸馏为技能，才能跨任务复利。

1. ⭐ **WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution.** arXiv, 2026\. [paper](https://arxiv.org/abs/2608.27454), [PDF-en](papers/en/2608.27454_WikiSkill.pdf), [PDF-zh](papers/zh/2608.27454_WikiSkill_zh.pdf), [解读](reports/09_wikiskill.md)
_Liyan Tang, Cyrus Rashtchian, Chun-Sung Ferng, Andrew Tomkins, Da-Cheng Juan, Tu Vu_

### 3.5 Online Side

> 免重置（reset-free）在线自改进：在故障现场修 harness 而非回起点重来，并首次闭环模型-harness 共学习。

1. ⭐ **Continual Harness: Online Adaptation for Self-Improving Foundation Agents.** arXiv, 2026\. [paper](https://arxiv.org/abs/2605.09998), [project](https://sethkarten.ai/continual-harness), [PDF-en](papers/en/2605.09998_ContinualHarness.pdf), [PDF-zh](papers/zh/2605.09998_ContinualHarness_zh.pdf), [解读](reports/11_continual_harness.md)
_Seth Karten, Joel Zhang, Tersoo Upaa Jr, Ruirong Feng, Wenzhe Li, Chengshuai Shi, Chi Jin, Kiran Vodrahalli_

### 3.6 Harness & Self-Evolving Agent Lineage

> Weng 博文谱系与本调研扩展收录的自进化 agent 前置/平行工作，按时间排序。其中 Self-Harness / Meta-Harness / AutoSaddler / EnvHarness / Prime Agent / MetaCaster 六个系统的中文导读见 [Harness 自进化全景](https://mp.weixin.qq.com/s/Lm_hmnkeeWlN6zVGlBBphw)。

1. **Self-Taught Optimizer (STOP): Recursively Self-Improving Code Generation.** COLM, 2024\. [paper](https://arxiv.org/abs/2310.02304), [PDF-en](papers/en/2310.02304_STOP.pdf), [PDF-zh](papers/zh/2310.02304_STOP_zh.pdf)
_Eric Zelikman, Eliana Lorch, Lester Mackey, Adam Tauman Kalai_
2. **Automated Design of Agentic Systems (ADAS).** ICLR, 2025\. [paper](https://arxiv.org/abs/2408.08435), [code](https://github.com/ShengranHu/ADAS), [PDF-en](papers/en/2408.08435_ADAS.pdf)
_Shengran Hu, Cong Lu, Jeff Clune_
3. **AFlow: Automating Agentic Workflow Generation.** ICLR, 2025\. [paper](https://arxiv.org/abs/2410.10762), [code](https://github.com/FoundationAgents/AFlow), [PDF-en](papers/en/2410.10762_AFlow.pdf)
_Jiayi Zhang, Jinyu Xiang, Zhaoyang Yu, Fengwei Teng, Xiong-Hui Chen, et al._
4. **AlphaEvolve: A Coding Agent for Scientific and Algorithmic Discovery.** arXiv, 2025\. [paper](https://arxiv.org/abs/2506.13131), [PDF-en](papers/en/2506.13131_AlphaEvolve.pdf)
_Alexander Novikov, Ngân Vũ, Marvin Eisenberger, Emilien Dupont, Po-Sen Huang, et al. (Google DeepMind)_
5. **GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning.** ICLR (Oral), 2026\. [paper](https://arxiv.org/abs/2507.19457), [code](https://github.com/gepa-ai/gepa), [PDF-en](papers/en/2507.19457_GEPA.pdf)
_Lakshya A Agrawal, Shangyin Tan, Dilara Soylu, Noah Ziems, et al._
6. **ShinkaEvolve: Towards Open-Ended and Sample-Efficient Program Evolution.** arXiv, 2025\. [paper](https://arxiv.org/abs/2509.19349), [code](https://github.com/SakanaAI/ShinkaEvolve), [PDF-en](papers/en/2509.19349_ShinkaEvolve.pdf)
_Robert Tjarko Lange, Yuki Imajuku, Edoardo Cetin (Sakana AI)_
7. **Agentic Context Engineering (ACE): Evolving Contexts for Self-Improving Language Models.** ICLR, 2026\. [paper](https://arxiv.org/abs/2510.04618), [PDF-en](papers/en/2510.04618_ACE.pdf), [PDF-zh](papers/zh/2510.04618_ACE_zh.pdf)
_Qizheng Zhang, Changran Hu, Shubhangi Upasani, Boyuan Ma, et al._
8. **Why LLMs Aren't Scientists Yet: Lessons from Four Autonomous Research Attempts.** arXiv, 2026\. [paper](https://arxiv.org/abs/2601.03315), [PDF-en](papers/en/2601.03315_WhyLLMsArentScientistsYet.pdf)
_Dhruv Trehan, Paras Chopra_
9. **Meta Context Engineering via Agentic Skill Evolution (MCE).** arXiv, 2026\. [paper](https://arxiv.org/abs/2601.21557), [PDF-en](papers/en/2601.21557_MCE.pdf), [PDF-zh](papers/zh/2601.21557_MCE_zh.pdf)
_Haoran Ye, Xuning He, Vincent Arak, Haonan Dong, Guojie Song_
10. **HyperAgents.** arXiv, 2026\. [paper](https://arxiv.org/abs/2603.19461), [PDF-en](papers/en/2603.19461_Hyperagents.pdf)
_Jenny Zhang, Bingchen Zhao, Wannan Yang, Jakob Foerster, Jeff Clune, Minqi Jiang, Sam Devlin, Tatiana Shavrina_
11. **Meta-Harness: End-to-End Optimization of Model Harnesses.** arXiv, 2026\. [paper](https://arxiv.org/abs/2603.28052), [code](https://github.com/stanford-iris-lab/meta-harness-tbench2-artifact), [PDF-en](papers/en/2603.28052_MetaHarness.pdf), [PDF-zh](papers/zh/2603.28052_MetaHarness_zh.pdf), [解读](reports/13_meta_harness.md)
_Yoonho Lee, Roshen Nair, Qizheng Zhang, Kangwook Lee, et al._
12. **Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses (AHE).** arXiv, 2026\. [paper](https://arxiv.org/abs/2604.25850), [code](https://github.com/china-qijizhifeng/agentic-harness-engineering), [PDF-en](papers/en/2604.25850_AHE.pdf), [PDF-zh](papers/zh/2604.25850_AHE_zh.pdf)
_Jiahang Lin, Shichun Liu, Chengjun Pan, Lizhi Lin, Shihan Dou, et al._
13. **DemoEvolve: Overcoming Sparse Feedback in Agentic Harness Evolution with Demonstrations.** arXiv, 2026\. [paper](https://arxiv.org/abs/2605.24539), [PDF-en](papers/en/2605.24539_DemoEvolve.pdf)
_Lirong Che, Yuzhe Yang, Peiwen Lin, Chuang Wang, Xueqian Wang, Jian Su_
14. **ScientistOne: Towards Human-Level Autonomous Research via Chain-of-Evidence.** arXiv, 2026\. [paper](https://arxiv.org/abs/2605.26340), [PDF-en](papers/en/2605.26340_ScientistOne.pdf)
_Rui Meng, Bhavana Dalvi Mishra, Jiefeng Chen, Chun-Liang Li, et al. (Google Cloud AI Research)_
15. **SIA: Self Improving AI with Harness & Weight Updates.** arXiv, 2026\. [paper](https://arxiv.org/abs/2605.27276), [PDF-en](papers/en/2605.27276_SIA.pdf)
_Prannay Hebbar, Yogendra Manawat, Samuel Verboomen, et al. (Hexo Labs)_
16. **Harness Updating Is Not Harness Benefit: Disentangling Evolution Capabilities in Self-Evolving LLM Agents.** arXiv, 2026\. [paper](https://arxiv.org/abs/2605.30621), [PDF-en](papers/en/2605.30621_HarnessUpdatingNotBenefit.pdf)
_Minhua Lin, Juncheng Wu, Zijun Wang, Zhan Shi, Yisi Sang, et al._
17. **Self-Harness: Harnesses That Improve Themselves.** arXiv, 2026\. [paper](https://arxiv.org/abs/2606.09498), [PDF-en](papers/en/2606.09498_SelfHarness.pdf), [PDF-zh](papers/zh/2606.09498_SelfHarness_zh.pdf), [解读](reports/14_self_harness.md)
_Hangfan Zhang, Shao Zhang, Kangcong Li, Chen Zhang, Yang Chen, Yiqun Zhang, Lei Bai, Shuyue Hu_
18. **Autodata: An Agentic Data Scientist to Create High Quality Synthetic Data.** arXiv, 2026\. [paper](https://arxiv.org/abs/2606.25996), [PDF-en](papers/en/2606.25996_Autodata.pdf)
_Ilia Kulikov, Chenxi Whitehouse, Tianhao Wu, Yixin Nie, et al. (FAIR at Meta)_
23. ⭐ **iCoder: Recursive AI-Led Development of Frontier Industrial Coding Model.** Tech Report, 2026\. [report](https://huggingface.co/i-Coder/iCoder-27B/blob/main/Coder_Tech_Report.pdf), [code](https://github.com/bingreeky/iCoder), [model](https://huggingface.co/i-Coder/iCoder-27B), [PDF-en](papers/en/iCoder27B_TechReport.pdf), [PDF-zh](papers/zh/iCoder27B_TechReport_zh.pdf), [解读](reports/19_icoder.md)
_Cheng Yang, Jiayang Lyu, Shangyuan Liu, Guibin Zhang, et al. (SJTU, NUS, DP Technology)_ — AI 主导交付 release-ready 27B 工业编码模型（RTLLM 68.0 超 GPT-5.5/Opus 4.8），人类介入压缩为"高密度 prior、低频门控"五层接口。**本仓库计划以其代码库为后续开发基础。**
19. **EnvHarness: Awakening Static Worlds for Agent Learning.** arXiv, 2026\. [paper](https://arxiv.org/abs/2608.19880), [PDF-en](papers/en/2608.19880_EnvHarness.pdf), [PDF-zh](papers/zh/2608.19880_EnvHarness_zh.pdf), [解读](reports/15_envharness.md)
_Chengsong Huang, Zifeng Wang, Rujun Han, Jun Yan, Yanfei Chen, et al. (Google Cloud AI Research)_
20. **AutoSaddler: Automatic Harness Optimization with Durable Updates from Agent Execution Traces.** arXiv, 2026\. [paper](https://arxiv.org/abs/2608.23041), [PDF-en](papers/en/2608.23041_AutoSaddler.pdf), [PDF-zh](papers/zh/2608.23041_AutoSaddler_zh.pdf), [解读](reports/16_autosaddler.md)
_Sungho Park, Wonjoong Kim, Rongyuan Tan, Jue Zhang, Wook-Shin Han, et al. (POSTECH, KAIST, SUSTech, Microsoft)_
21. **MetaCaster: Meta-Harness-Optimized Agent for End-to-End Few-Shot Learning of Lightweight Time Series Forecasters.** arXiv, 2026\. [paper](https://arxiv.org/abs/2608.23473), [code](https://github.com/D2I-Group/metacaster), [PDF-en](papers/en/2608.23473_MetaCaster.pdf), [PDF-zh](papers/zh/2608.23473_MetaCaster_zh.pdf), [解读](reports/17_metacaster.md)
_ChengAo Shen, Wenchao Yu, Fangyu Wu, Dongjin Song, Hanghang Tong, et al. (UH, NEC Labs)_
22. **Prime Agent: A Self-Improving RLM Harness.** arXiv, 2026\. [paper](https://arxiv.org/abs/2608.23552), [code](https://github.com/PrimeIntellect-ai/prime-agent), [PDF-en](papers/en/2608.23552_PrimeAgent.pdf), [PDF-zh](papers/zh/2608.23552_PrimeAgent_zh.pdf), [解读](reports/18_prime_agent.md)
_Seth Karten, Alex L. Zhang, Kevin Thomas, Sebastian Müller, et al. (Princeton, Prime Intellect, MIT)_

## 4. Frontier Tracking (2026 H2)

2026 年 6-8 月扫描结果（完整笔记见 [`assets/trends_research_raw.md`](assets/trends_research_raw.md)：19 篇新论文 + 9 项工业动态 + 7 项基准动态 + 8 项安全治理）。

**评估器军备赛**

1. **EvalCEGAR: Metrics That Write Themselves.** [arXiv:2608.18744](https://arxiv.org/abs/2608.18744) — 用反例（而非 prompt）驱动评估器算子进化，延续 Who Grades the Grader 路线。
2. **SCORE: Self-Evolving Deep Research via Joint Generation and Evaluation.** [arXiv:2606.04507](https://arxiv.org/abs/2606.04507) — 评估器与求解器共享参数联合训练，推进到权重层。
3. **Co-Evolution in Agentic Systems (Survey).** [arXiv:2608.10299](https://arxiv.org/abs/2608.10299) — 首个以共进化为中心轴的综述：Agent-Agent / Agent-Environment / Meta 三层。

**技能进化红海（WikiSkill 同月平行工作）**

4. **SkillCommit.** [arXiv:2608.15165](https://arxiv.org/abs/2608.15165) — 反对语义相似度合并，用行为验证的层级抽象提交。
5. **HyperSkill.** [arXiv:2608.16114](https://arxiv.org/abs/2608.16114) — 超图结构技能记忆，GAIA +11.5。
6. **ERSkill.** [arXiv:2608.12720](https://arxiv.org/abs/2608.12720) — 检索行为本身技能化，双 frontier 解耦扩张与部署。
7. **SkillProx.** [arXiv:2608.07449](https://arxiv.org/abs/2608.07449) — 近端梯度下降形式化搬到文本技能空间，删除是一等公民。
8. **Evo-Harness.** [arXiv:2608.15071](https://arxiv.org/abs/2608.15071) — 反思编译为技能 harness，五基准系统性隔离变量。

**Harness 工程化与共学习**

9. **Co-Harness: Co-Evolving Harnesses and Model Weights.** [arXiv:2607.22688](https://arxiv.org/abs/2607.22688) — harness 优化产生轨迹再蒸馏进权重，双环交替。
10. **RHO: Retrospective Harness Optimization via Self-Preference.** [arXiv:2606.05922](https://arxiv.org/abs/2606.05922) — 完全无标签自优化，SWE-Bench Pro 59%→78%。
11. **Adaptive Auto-Harness.** [arXiv:2606.01770](https://arxiv.org/abs/2606.01770) — 密集自改进在开放任务流上早峰后衰减的负结果实证。
12. **HarnessFix.** [arXiv:2606.06324](https://arxiv.org/abs/2606.06324) — 轨迹+harness 编译为 IR，失败归因到 ETCLOVG 七层。
13. **Metan (Meta^n): RSI through Emergent Depth.** [arXiv:2608.24735](https://arxiv.org/abs/2608.24735) — 论证自改写 meta 深度上限约 2.5，改输入不改机器绕开权衡。
14. **HSI: Hierarchical Self-Improvement.** [arXiv:2608.08466](https://arxiv.org/abs/2608.08466) — 三层作用域进化，冻结 meta-evolver 为外层锚。

**安全、治理与基准**

15. **SESG: A Self-Evolving Safety Guardrail in Production.** [arXiv:2608.08471](https://arxiv.org/abs/2608.08471) — 深信服生产系统，16-24h 自动闭环新威胁（原 40-90h）。
16. **OpenLoopEvolve (OLE).** [arXiv:2608.09380](https://arxiv.org/abs/2608.09380) — 策略资产版本化+血统追踪+劣化自动回滚，补 MOSS 的部署纪律。
17. **Falsifiable Release Gates for Self-Improving Systems.** [arXiv:2607.13070](https://arxiv.org/abs/2607.13070) — 七道可证伪发布门：收紧类自动应用、放松类必须人类合并。
18. **HVTB: Hack-Verifiable Terminal Bench.** [arXiv:2608.22103](https://arxiv.org/abs/2608.22103) — 蜜罐嵌入真实编码任务，测前沿模型 reward hacking 率下界。
19. **ASG-SI / ARA（安全谱系背景）.** [arXiv:2512.23760](https://arxiv.org/abs/2512.23760), [arXiv:2602.01750](https://arxiv.org/abs/2602.01750) — verifier-auditor 密码学溯源与对抗性奖励审计。

## 5. Ten Insights

完整论证见 [`reports/10_synthesis_insights.md`](reports/10_synthesis_insights.md)：

1. 评估器是双重瓶颈：既是能力上限，又是攻击靶点
2. "无锚不进化"成为共识设计原则
3. 评估器与策略的相对速度决定系统命运
4. 自改写深度存在结构性上限，绕行方案已出现
5. 发现与执行是两种能力，技能是可交易资产
6. 经验必须先编译成知识，才能复利
7. 生产落地的分水岭是"自改进资产化"
8. 微观加速与宏观节奏之间存在实证鸿沟
9. 算力-认知劳动替代弹性 σ 是宏观争论的单一关键参数
10. 测量基础设施本身正在成为一级瓶颈

## 6. Reading Routes

按目的选路线（materials 均在本仓库内）：

- **想快速建立全景**：slides 26 页（15 分钟）→ [报告 10](reports/10_synthesis_insights.md)（叙事弧线 + 两轴地图 + 十条 insight）
- **想理解 harness 工程**：[报告 01](reports/01_lilian_weng_harness_engineering.md)（Weng 总纲）→ [报告 07](reports/07_darwin_godel_machine.md)（DGM 基线）→ [报告 11](reports/11_continual_harness.md)（免重置 + 共学习）
- **想理解评估器战争**：[报告 03](reports/03_evolm.md)（reward overoptimization 悖论）→ [报告 04](reports/04_red_queen_godel_machine.md)（epoch 冻结）→ [报告 05](reports/05_who_grades_the_grader.md)（观测等价 + 锚定纪律）→ [报告 06](reports/06_echo.md)（权重层双路 GRPO）
- **想看生产落地**：[报告 02](reports/02_anthropic_when_ai_builds_itself.md)（Anthropic 内部证据）→ [报告 08](reports/08_moss.md)（MOSS 门控回滚）→ 4 节的 SESG / OLE / HarnessFix

## 7. Repository Layout

```
awesome_rsi/
├── README.md                        # 本文件
├── awesome_rsi_slides.html          # 26 页汇总 HTML PPT（方向键翻页，P 键打印）
├── awesome_rsi_slides.pdf           # 同内容 26 页 PDF 版（1280x720 逐页）
├── reports/                         # 20 份精读报告（Markdown，中文）
│   ├── 00_origins_1965_2014.md                 # 前史：Good → Yudkowsky → Schmidhuber → Bostrom
│   ├── 01_lilian_weng_harness_engineering.md   # 总纲：harness 工程 → RSI
│   ├── 02_anthropic_when_ai_builds_itself.md   # 工业证据：>80% 代码由 Claude 写
│   ├── 03_evolm.md                             # 评估侧：rubric 共进化
│   ├── 04_red_queen_godel_machine.md           # 评估侧：受控效用进化
│   ├── 05_who_grades_the_grader.md             # 评估侧：锚定纪律 + 否定性结论
│   ├── 06_echo.md                              # 模型侧：critic-policy 双轨 GRPO
│   ├── 07_darwin_godel_machine.md              # 框架侧：RSI 工程化基线
│   ├── 08_moss.md                              # 框架侧：生产部署 + 门控回滚
│   ├── 09_wikiskill.md                         # 知识侧：经验→wiki→技能
│   ├── 10_synthesis_insights.md                # 汇总：两轴地图 + 十条 insight
│   ├── 11_continual_harness.md                 # 在线侧：免重置精炼 + 模型-harness 共学习
│   ├── 12_self_evolving_agents_survey.md       # 综述：What/When/How/Where 四维坐标
│   ├── 13_meta_harness.md                      # 谱系：harness 端到端优化（Stanford）
│   ├── 14_self_harness.md                      # 谱系：harness 自我改进（上海 AI Lab）
│   ├── 15_envharness.md                        # 谱系：环境侧进化（Google Cloud AI）
│   ├── 16_autosaddler.md                       # 谱系：轨迹归因 + 持久化更新（Microsoft 等）
│   ├── 17_metacaster.md                        # 谱系：meta-harness 垂直落地（时序预测）
│   ├── 18_prime_agent.md                       # 谱系：自改进 RLM harness（Prime Intellect）
│   └── 19_icoder.md                            # 工业实证：AI 主导开发 27B 前沿模型（后续开发基座）
├── papers/
│   ├── classics/                    # 起源经典（1965 Good / 2001 GISAI / 2003 Gödel Machine，含中译）
│   ├── en/                          # 32 篇英文原版 PDF（arXiv + iCoder 技术报告）
│   └── zh/                          # 20 篇中文翻译 PDF（super_translate，保版式）
└── assets/
    ├── fulltext/                    # 核心论文提取全文（报告撰写底稿）
    └── trends_research_raw.md       # 2026H2 趋势扫描原始笔记
```

## 8. Translation Pipeline

中文 PDF 由 [super_translate](https://github.com/asimfish/super_translate) 生成：冻结公式/图表等结构对象 → 术语注入 → 按原坐标替换文本 → QA 审计 + 确定性修复环。后端为 DeepSeek API，逐篇带翻译缓存。翻译保留原版式与页码，适合与英文版对照精读；技术术语与公式排版以英文原版为准。

## 9. Disclaimer & Credits

- 论文 PDF 版权归原作者与 arXiv 所有，本仓库仅作研究备份与学习用途；中文翻译为机器翻译，引用请以英文原文为准。
- 精读报告与 slides 为本仓库原创内容（CC BY 4.0），转载注明出处。
- 编目规范参考 [Thinklab-SJTU/awesome-ml4co](https://github.com/Thinklab-SJTU/awesome-ml4co)。
- 欢迎 PR 补充新论文：条目格式为 `**标题.** 来源, 年份. [paper](链接)` + 斜体作者行。
