# 解读报告 15 · EnvHarness: Awakening Static Worlds for Agent Learning

| 项目 | 内容 |
|---|---|
| arXiv | 2608.19880 v1（2026-08-20） |
| 作者 | Chengsong Huang（WashU，Google Cloud AI Research 实习期间完成）、Zifeng Wang、Rujun Han、Jun Yan、Chen-Yu Lee 等 |
| 机构 | 华盛顿大学圣路易斯 + Google Cloud AI Research（+ UNC 教堂山） |
| 代码 | github.com/google-research/envharness |
| 在调研中的位置 | 全谱系唯一把进化对象从 agent 翻转到**环境**的工作：文本/权重/源码三层改进面之外的"第四面"，同时是锚定纪律在环境侧的教科书式落地——环境随便改，验证器一根手指不许碰 |

## 一句话核心主张

Agent harness 用插件组件把冻结 LLM 变成 agent（Agent = Model + Harness），本文把同一等式对偶到交互回路的另一端：**Customized Env = Static Env + EnvHarness**——用一层可编程接口包装器把静态基准环境改造成会针对特定策略弱点出题的动态环境，全程不碰环境内部一行代码，因此每个改造环境**无条件继承原环境的人写验证器**；再用 EnvRigger 把定制过程自动化，实现策略与环境的定向共进化。

## 机制：三类组件 + 一个装配工

环境形式化为 E=(S,A,O,T,R,s0)，EnvHarness 组件是严格作用于接口层的变换 w: E→E'，三类实现全走标准 reset/step：

- **Stage（改初始状态）**：给定动作序列 δ，reset 后先替 agent 走几步再交还控制权——把马克杯藏进抽屉逼策略学搜索，或提前完成清洗子目标缩短时程。初始状态永远是可达状态，用环境自己的动作词汇表达。
- **Contract（改交互规则）**：三个纯函数钩子 (f_A, f_T, f_O) 分别重写动作、转移响应、观测——截断房间描述考察部分可观测、封掉 teleport 逼逐步导航、拦截未跑测试的代码提交。
- **Chain（拼接环境）**：把两个环境串成一个长时程 episode，复合裁决 R' = R_A ∧ R_B，两半各由自己的验证器判分，链条继承双亲的可信验证。

**R 轴刻意不暴露**。设计者提示词原文："success is the benchmark's own verdict, so reshaping reward cannot move the eval metric"——改环境无法移动评测指标。这一句就是本调研反复强调的锚定纪律。

**EnvRigger** 四阶段循环：Observe（基线 5 次 rollout）→ Diagnose（找行动循环、长观测解析失败等系统性根因；全对的任务被诊断为"环境太宽容"，转向加难）→ Write（合成组件候选集）→ Validate（新鲜 5 次 rollout，按成功率与失败分布接受/拒绝/修订，修订预算 5 轮）。设计者与策略共用同一模型 backbone，排除"从更强模型蒸馏"的解释。提示词里另一句值得抄录：**"SR=0 from impossibility is exactly as useless as SR=1 from triviality"**——难度必须落在能学到东西的带内。

## 关键数字

- **技能学习主结果**（ReasoningBank 抽技能，评测严格用原环境 held-out）：ALFWorld OOD 61.4→70.4（**+9.0**）；WebArena 均值 +3.1；SWE-bench Verified 49.9→52.6（+2.7）且平均步数 53.6→49.6——而从未改造环境抽的技能反把步数拉长到 55.0（相对之少 9.8%），SpreadsheetBench 上甚至跌破无技能基线（45.9 vs 46.4）：**静态环境只让 agent 练它已经会的动作**。
- **对领域专用生成管线**：ALFWorld 超 GenEnv 均值 5.7 / OOD 8.5 点；SWE-bench 超专门造的 SWE-smith 2.46 点且每回合少 5.11 步。
- **RL 兼容性**（GRPO + Qwen3-8B-base）：ALFWorld in-dist 81.4→87.9（+6.5），WebShop 分数 75.6→79.2；代价是 ALFWorld OOD 微跌 89.6→88.8。
- **环境规模化**：同预算 300 个环境，EnvHarness 47.7→54.8 仍在上行；真实环境 52.1、SWE-smith 生成 50.4 双双走平——每批环境都针对"装备了此前技能的策略"合成，环境与策略真正共进化。
- **跨模型**：从 Gemini Flash-Lite（裸 30.7）到 Claude Sonnet 4.6（裸 67.2）四个 backbone，对原环境技能的增益稳定在 +2.7~+3.7 绝对点，**增益大小与策略强弱基本无关**。
- **按指标定制**：把任务成功率校准进 [0.4,0.6] 目标带，命中率 6%→80%（均值 SR 0.74→0.48）；平均步数带 [25,35] 命中 18%→53%。
- **成本**：设计 token 1.46M 远超 GenEnv 的 38K，但总开销与同为真实执行的 VeriEnv 打平（137.3M vs 137.8M）——多花的是"接地"的钱，GenEnv 便宜 3.5× 的代价是幻觉转移与漂移的成功信号。

## 局限与批评

- **重置依赖是硬边界**：Stage 的动作重放与 Chain 的换环境都以确定性 reset 为前提，论文自认排除真实用户账户、实体机器人等不可重置域——与报告 11 Continual Harness 的免重置主张恰成正交：CH 解决"环境不能重置怎么办"，EnvHarness 依赖"环境必须能重置"。
- **环境会说谎**：附录展示的组件里有伪造的 "pytest: command not found"、假 OOM kill（exit 137）、sed 静默注入缩进损坏——课程难度与虚假世界观之间只隔一层纸。从被欺骗的轨迹里蒸馏的技能碰巧通用（如 pytest.main 兜底），但没有任何机制保证欺骗式扰动不会教出对真实世界错误的信念。
- **技能是唯一媒介**（SL 设定下）：改造环境的收益必须经"轨迹→技能文本→检索"三跳才抵达测试，最强模型上相对增益已缩到 +4.6%；leave-one-out 里 heat 类回归 −8.7 提示技能迁移并非无代价。
- **诊断者=被诊断者**：EnvRigger 与策略同模型，弱模型给自己诊断的盲区（不知道自己不知道什么）未被单独度量——跨模型实验只说明"循环不崩"，没给出诊断质量的下界。

## 与本调研的连线

- **对报告 01（Weng 总纲）**：Weng 把 harness 定义为模型外的可执行搜索空间，本文证明该等式两侧对称——环境侧也存在同构的可执行搜索空间，三层改进面之外真正新增了第四面：**环境面**。
- **对报告 04（RQGM）**：RQGM 的红皇后动力学里评估器与被评者共进化、塌缩风险来自裁判可被腐蚀；EnvHarness 给出干净的分工——**让出题人进化、裁判钉死**（R 轴不暴露），共进化的全部压力被引导到锚之外。这是"评估器塌缩与真进化观测等价"命题的一个建设性回避：不去解决观测等价，而是让观测者根本不参与进化。
- **对报告 05（Who Grades the Grader）**：验证器无条件继承 = 锚定纪律的环境侧实例；与 GenEnv 的对比（LLM 模拟转移+自造成功信号 → 幻觉与评估漂移）正是 WGtG 警告的实证——放弃人写锚省下 3.5× token，买到的是漂移的成功信号。
- **对报告 11（Continual Harness）**：两篇构成 harness 谱系的对偶极——CH 免重置、在故障现场改 agent 侧；EnvHarness 重置式、离线改环境侧。CH 有能力地板（弱模型自建组件自己用不利索），EnvHarness 跨模型增益平坦——因为**消费改造环境不需要生产能力**，这给资产市场叙事补上另一半：环境资产的消费门槛低于技能资产。
- **对报告 09（WikiSkill）**：EnvHarness 是技能生产管线的上游供给侧改革——WikiSkill 关心经验如何编译成可迁移技能，本文回答"什么样的经验值得编译"：从针对弱点定制的环境里来的轨迹，比从静态环境来的轨迹编译出的技能系统性更好（后者甚至可为负资产）。
