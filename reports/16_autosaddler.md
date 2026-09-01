# 解读报告 16 · AutoSaddler: Automatic Harness Optimization with Durable Updates from Agent Execution Traces

| 项目 | 内容 |
|---|---|
| arXiv | 2608.23041 v1（2026-08-24） |
| 作者 | Sungho Park*、Wonjoong Kim*、Rongyuan Tan*（共同一作，均为 Microsoft 实习）、Jue Zhang†、Wook-Shin Han† 等 |
| 机构 | POSTECH + KAIST + 南方科技大学 + Microsoft |
| 项目页 | aka.ms/AutoSaddler-website |
| 在调研中的位置 | harness 谱系里把"改 harness"最彻底工程化为**离线 mini-batch 学习**的一篇：诊断-补丁充当反传、dev 集充当泛化门、EvoDAG 充当优化器状态；同时提供了"无锚自改进为负收益"的最强消融证据 |

## 一句话核心主张

手工调 harness 贵且慢，本文把 harness 优化形式化为对 θ=(prompt, tool, middleware) 的预算受限离线学习问题：每轮在训练 mini-batch 上跑当前 harness，由 Diagnosis-Patch Agent 深挖失败轨迹与 harness 代码库产出结构化补丁，同批验证过关后再上 dev 集测泛化，反思会话把 fixed/regressed/still-failing/still-passing 四象限证据存进 EvoDAG，进化会话据此合成下一代候选——目标是产出 **durable updates（持久性更新）**而非只修单条轨迹的 hot fix。

## 机制逐层拆

- **文本梯度需要验证**：数值梯度由固定算子推出，文本"梯度"是推断的、语义的、会错的——所以每个补丁先当作"检验根因假设的干预"，同批重跑分数严格上升才有资格进 dev 门。这个"诊断→干预→同批校验"三段式是全文对反传最认真的类比。
- **结构化干预**：补丁空间按 Prompt/Tool/Middleware 三层九子型划分（规则增改、新工具、参数修改、实现修复、描述修正、PreToolUse 钩子、基建变更、循环逻辑变更），再按是否改可执行代码分为**能力补丁**与**引导补丁**，用两相调度模拟学习率调度：先能力后引导，能力期 1 个 epoch。
- **泛化感知选择**：dev 集过滤 + 反思会话。反思强制做**随机性甄别**——每个 PASS↔FAIL 翻转必须对照代码 diff 与轨迹分歧点，区分真因果与 LLM 非确定性的假信号，防止把运气污染进经验库。
- **EvoDAG**：进化历史存成 DAG（节点=候选 harness+教训+分数，边=diff），经 evo-dag CLI 按需查询；进化会话可 rebase、cherry-pick、回滚。搜索轨迹显示：Iter20 一个高频工具上的过宽钩子造成 dev 33.8% 的灾难性回归，系统 rebase 回 Iter13 并摘取已证实修复，Iter27 冲上峰值 72.3%；Iter46 又因累积 8 个钩子跌 12.3 点，Iter47 剪到 4 个保守补丁恢复 69.2%。**自动优化器学会了 git 工作流**。

## 关键数字

- **主结果**（训练/dev/测试按任务组严格分离——GAIA2 按 Universe、SWE-Bench Pro 按仓库且跨编程语言）：GAIA2 53.0→62.0（+9.0pp，超最强自动基线 GEPA 7.4）；SBP 37.3→46.9（+9.6pp，在 qutebrowser/Python 上训练，Ansible/Flipt/Element-web 三语言仓库上测）；Terminal-Bench 2.0 40.0→50.0（+10.0pp），并超过人类专家手调的 Terminus KIRA（47.5）2.5 点。
- **效率**：GAIA2 dev 72.3% 只花约 1000 次任务执行，GEPA/Meta-Harness 烧 2800 次饱和在 64.6%/61.5%；按真正用于学习的轨迹算是 147 条 vs Meta-Harness 1400 条（约 10×）；TB2 上 12 条 vs 98 条（8×）。
- **消融即证据链**：去 in-depth 诊断 62.0→57.8（浅反思单次 LLM 调用替代，接受补丁数 20→15）；去结构化干预 →56.9，补丁分布塌缩到 91.5% 引导型、高价值能力型只剩 4%——而新工具/循环变更/基建变更的接受率恰是最高的 83%/71%/67%；去泛化感知选择 →50.6，**跌破未优化基线 53.0**。细粒度版（Universe 22）：去 dev 过滤 60.7→50.0，再去反思+EvoDAG →44.9。
- **durable 的操作化定义**：能力补丁与引导补丁修复率相当（55% vs 58%），但回归率减半（8% vs 17%）；dev 回归率斜率 −0.24pp/iter vs 消融 +0.16pp/iter。
- **可迁移**：Opus 4.6 优化出的 harness 换 Haiku 4.5 跑仍 +5.6pp（30.0→35.6）；换训练 Universe（29→24）仍 +5.9pp；独立重跑 58.6% vs 60.7%。
- **成本**：单补丁 $14.56（比 Meta-Harness 贵 $1.91 但墙钟省 39.6%）；真正贵的是任务 rollout（单条平均 55 万输入 token），AutoSaddler 391 次 rollout 达 dev 67.7%，已超 Meta-Harness 1400 次的峰值。

## 局限与批评

- **dev 集是新的可磨损锚**：最终选择规则是在 dev 上取 argmax——65 个 dev 场景上比较 21 个候选是教科书式自适应选择，dev 峰值 72.3% 与测试 62.0% 之间约 10 点落差里有多少是 dev 过拟合，论文没有分解。锚定纪律要求锚不参与进化：dev 集虽不被"改"，但被反复"选"，选择压力同样磨损锚的信息量。
- **锚的硬度不均**：SBP/TB2 用单元测试和检查脚本（硬验证器），GAIA2 却用 Llama-3.3-70B 当 judge——最大增益之一恰落在最软的锚上，而针对 judge 的 game 行为（引导补丁教 agent 用 judge 偏好的答案格式，Rule 1 "respond with ONLY the direct answer" 就在边缘）与真实能力提升在此观测等价。
- **stateless 假设切掉了记忆**：θ 明确不含 memory 与 skill curation，任务假设无状态独立——这既是与 WikiSkill/CH 的分工边界，也意味着"durable"只在任务分布固定的离线意义上成立，分布漂移下的持久性没有测。
- **统计力薄**：优化太贵，主实验每方法只跑一次进化轨迹，稳健性检查也只有两条；TB2 测试仅 40 题且三次重跑标准差 0.0。
- **结构先验的反 Bitter-Lesson 一面**：人类设计的九子型分类加两相调度贡献了 5.9pp（仅去调度）——当前能力档位上约束胜过自由，但该结论会随优化器模型变强而过期，届时结构化干预可能反成枷锁。

## 与本调研的连线

- **对报告 01（Weng 总纲）**：把"harness 是可执行搜索空间"推到最工程化形态——搜索空间显式参数化为 θ 三元组，优化过程逐行映射到 mini-batch 学习七步；Opus 调、Haiku 用仍 +5.6pp 的跨模型迁移，是 **harness 资产化**最直接的实证之一：harness 是独立于模型的可转让资产。
- **对报告 05（Who Grades the Grader）**：w/o 泛化感知选择的消融是全调研关于"无锚自改进"最干净的负结果——去掉 dev 门控与反思后，自动优化产出的 harness（50.6）**比不优化（53.0）更差**。这不是收益递减而是负收益：没有不参与进化的锚，harness 空间的爬山会爬向 mini-batch 噪声而非任务分布信号。reward overoptimization 在 harness 层的形态就是"过宽钩子修好一处、打坏一片"（消融组回归率 8%→22% 的尖峰）。
- **对报告 09（WikiSkill）**：两种经验沉淀的镜像——WikiSkill 把轨迹编译成给 **agent 消费**的技能，AutoSaddler 的反思把轨迹编译成给**优化器消费**的教训；且展示了同一问题（邮件回复质量）的教训从原子诊断→跨场景模式→场景无关原则的三级成熟（Iter 3→19→27），正是经验编译的抽象阶梯在 meta 层的重演。
- **对报告 07（DGM）/ 08（MOSS）**：作者明确放弃自指（引用 DGM 与 Gödel agent 后声明不建模自指动力学、meta-agent 不必等于 task agent），换来有限 rollout 预算下更可控的搜索；EvoDAG 的 rebase/cherry-pick/回滚是 MOSS"改坏怎么办"门控故事的进化版——MOSS 用失败重放加批准门，AutoSaddler 用同批验证、dev 门与 DAG 回溯，安全机制从"防改坏"转向"可撤销"。
- **对报告 11（Continual Harness）**：离线/重置式 vs 在线/免重置的正对照——CH 主张失败特征在单场连续 episode 内复利累积，AutoSaddler 主张开发期离线调好再部署；两者覆盖生命周期的两段：AutoSaddler 管出厂前，CH 管出厂后，谁也替代不了谁。
