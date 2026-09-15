# RSI / 自进化 Agent 扩展调研原始笔记（2026 年 6-8 月动态）

- 调研日期：2026-08-31
- 方法：8 轮 web 检索 + arXiv 全文抽取交叉验证；已知基线（六篇 RSI 核心论文 + Lilian Weng 博文 + Anthropic Institute 文章）不重复调研，仅作关联标注
- 计数：新论文/系统 19 项、工业界动态 9 项、基准动态 7 项、安全治理 8 项、争论焦点 6 组

---

## 一、2026 年 7-8 月新论文（arXiv）

### 1.1 评估器共进化后续

**[1] EvalCEGAR — Metrics That Write Themselves: Evolving an Evaluator from Its Own Blind Spots (arXiv:2608.18744)**
- 一句话：把程序验证的反例引导抽象精化（CEGAR）搬到评估器进化——评估器是一池小 Python 检测算子，系统搜索「两个答案得分相同但一对一错」的碰撞对，用反例而非 prompt 驱动新算子编写；MBPP+/HumanEval+ 上自动写出 55 行算子，关闭 15.4% 的「不过滤到完美过滤」差距（p=0.0010），推理期零模型调用成本。
- 关联：直接延续《Who Grades the Grader》(2607.12790) 的「可检视组合检测器」路线（同样的 anchored/audit 设计语言，疑似同一团队系列工作）；回应 Weng 挑战之「弱评估器」。
- 来源：https://arxiv.org/pdf/2608.18744

**[2] SCORE — Self-Evolving Deep Research via Joint Generation and Evaluation (arXiv:2606.04507)**
- 一句话：针对无 ground-truth 的深度研究报告任务，把评估器与求解器放进同一个共享参数模型里联合训练（区别于 ECHO 的双路分离），外加 meta-harness 根据 solver 表现动态控制评估环境，防止评估维度失效与 reward hacking。
- 关联：把 EvoLM 的 rubric-policy 共进化从文本层推进到权重层；「静态评估器导致优化压力饱和」的表述与已知主线判断完全一致；meta-harness 概念直接来自 harness 工程谱系。
- 来源：https://arxiv.org/html/2606.04507

**[3] Co-Evolution in Agentic Systems 综述 (arXiv:2608.10299)**
- 一句话：首个以「共进化」为中心轴的综述，提出三阶段递进分类——Agent-Agent 共进化（对抗/协作/组织）、Agent-Environment 共进化（任务/反馈/交互空间随 agent 变化）、Meta 共进化（进化机制本身可进化），并把评估难、跨组件扩展、安全可控列为三大开放挑战。
- 关联：把「评估器共进化」纳入 Agent-Environment 层的 adaptive feedback 分支，为六篇论文提供统一分类学坐标；明确引用 harness 工程综述谱系。
- 来源：https://arxiv.org/html/2608.10299v1

### 1.2 Skill 进化（WikiSkill 前后的同期浪潮）

> 背景：WikiSkill (2608.27454) 发布于 8 月末，以下 5 篇是同月密集出现的平行工作，说明「经验到结构化技能」已成红海方向。分歧在结构（层级/超图/检索技能），共识在生命周期管理（验证门禁、utility 审计、合并/退役）。

**[4] SkillCommit — Evolving Agent Skills through Behaviorally Validated Scope Expansion (arXiv:2608.15165)**
- 一句话：反对按语义相似度合并经验（会把表面相似但行为不兼容的策略合并坏），改为「实例补丁、跨实例重放验证、机制检查、行为保持的层级抽象提交」流水线，学到的技能可跨模型规模与家族迁移。
- 关联：直接回应 WikiSkill 的「经验-wiki-skill」分层里最脆弱的抽象一步；「行为验证」对应 Weng 挑战之「弱评估器」在 skill 生命周期里的投影。
- 来源：https://arxiv.org/html/2608.15165

**[5] HyperSkill — Self-Evolving LLM Agents via Hypergraph-Structured Skill Memory (arXiv:2608.16114)**
- 一句话：memory+skill 结合的代表作——用超图同时组织子任务节点与技能节点（每条超边等于一条轨迹的 n 元关联），双路检索 + 结构感知维护（按质量加权传播修剪低效节点、合并冗余技能），GAIA +11.51、WebWalkerQA +11.18，超过 10 个记忆基线。
- 关联：回应 Weng 挑战之「上下文记忆生命周期」；把 WikiSkill 的三层分离改造成图结构上的连续谱。
- 来源：https://arxiv.org/html/2608.16114

**[6] ERSkill — Evolving for Skill-Guided Adaptive Memory Retrieval (arXiv:2608.12720)**
- 一句话：把「检索行为」本身技能化（检索原语组合成可执行检索技能），技能集与路由器共进化，用经验 trie + 双 frontier 机制把「新技能扩张」与「面向路由器的稳定部署」解耦；平均指标提升 28-31%。
- 关联：双 frontier（开发面/部署面分离）与 Red Queen Gödel Machine 的 epoch 冻结思想同构——都是用「冻结一侧」换稳定性。
- 来源：https://arxiv.org/html/2608.12720

**[7] SkillProx — Self-Evolving Agent Skills via Proximal Textual Gradient Descent (arXiv:2608.07449)**
- 一句话：把近端梯度下降形式化搬到文本技能空间——前向阶段在同批任务上重放诊断驱动的编辑并回滚回归，后向阶段把技能分解为可审计知识单元、用冻结的留一 utility 审计估计贡献、门禁化整合/降级/删除；比最强文本梯度基线 +3.0pp。
- 关联：「删除作为一等公民操作」回应 Weng 挑战之「负结果处理」；留一审计是评估器瓶颈的技能层解法。
- 来源：https://arxiv.org/abs/2608.07449v1

**[8] Evo-Harness — Context-to-Harness Skill Compilation for Self-Evolving Agents (arXiv:2608.15071)**
- 一句话：把单次反思「编译」成通用技能+主题技能的结构化 harness，核心贡献不是刷分而是系统性隔离变量：在 TerminalBench2/SWE-bench/CL-Bench/tau-bench/WebArena-Infinity 五基准上分析 evolver 设计、反馈类型、迁移设置各自对冻结 LLM 在线自改进的贡献。
- 关联：明确把 skill harness 当作「研究自改进机制的可解释介质」，方法论上呼应 Weng 的 harness 工程框架；「记忆是被动存储、技能是主动 harness」的区分是对 WikiSkill 分层动机的独立佐证。
- 来源：https://arxiv.org/html/2608.15071v1

### 1.3 生产部署方向（MOSS 之后）

**[9] SESG — Yesterday's Shield, Today's Spear: A Self-Evolving Safety Guardrail in Production (arXiv:2608.08471)**
- 一句话：真实生产系统（深信服 Sangfor，2026 年 4 月起为主更新管线）——监控线上流量发现新型越狱/新害类，生成 agent 合成配对训练数据、验证 agent 按部署模型自身错误方向重平衡训练集、路由 agent 匹配训练动作，1.7B 护栏 16-24 小时闭环一个新威胁（人工仅约 2h，替代原 40-90h 流程），两个月自动闭环 14/15 新威胁场景。
- 关联：MOSS 之后最重的生产级证据，但自进化对象从 harness 换成了安全护栏本身——「用自进化对抗自进化威胁」；发布 9 个新威胁测试集。
- 来源：https://arxiv.org/abs/2608.08471

**[10] OpenLoopEvolve (OLE) — Verifiable Self-Evolution Framework for Loop Policies (arXiv:2608.09380)**
- 一句话：把 agent 的观察/规划/记忆/行动/验证/恢复/停止/预算控制表示为有版本、有血统的策略资产，在线/离线双模式进化，Champion-Challenger 配对评估 + 任务边界激活 + 劣化条件自动回滚。
- 关联：直接回应 MOSS 暴露的部署风险面——MOSS 证明源码级自改写可行，OLE 补上「每次改动都是一次 deploy、每次 deploy 需要回滚故事」的工程纪律。
- 来源：https://arxiv.org/abs/2608.09380

**[11] Co-Harness — Co-Evolving Harnesses and Model Weights for LLM Agents (arXiv:2607.22688)**
- 一句话：面向 automated AI research 的后训练框架：HarnessCritic 把失败轨迹归因到 harness 级失败模式并提出局部验证过的 diff，改进后的 harness 生成高质量轨迹再微调模型（把有效脚手架蒸馏进权重），双环交替；含 200+ 小时无人干预案例（自恢复崩溃、自发现 ensemble 策略）。
- 关联：SIA（harness+权重联合优化）的直接后续，把「联合」从选择题（SIA 的 Feedback-Agent 二选一）变成蒸馏循环。
- 来源：https://arxiv.org/html/2607.22688

**[12] RHO — Retrospective Harness Optimization via Self-Preference (arXiv:2606.05922)**
- 一句话：完全无标签的 harness 自优化——从历史轨迹选多样性困难任务 coreset（DPP 核）、并行重解、自验证+自一致性诊断、pairwise 自偏好选最优 harness 更新；单轮把 SWE-Bench Pro 从 59% 提到 78%，无任何外部评分。
- 关联：对「评估器瓶颈」的激进回答——干脆不要外部评估器，用组内相对信号替代；与 Who Grades the Grader 的「锚定集」路线形成对照（自偏好 vs 外部锚）。
- 来源：https://arxiv.org/pdf/2606.05922

**[13] Adaptive Auto-Harness (arXiv:2606.01770)**
- 一句话：指出单一密集更新的 harness 在开放任务流上「准确率早峰后衰减」，把 oracle 差距分解为进化损失+适应损失，用有状态多智能体 evolver + harness 树（solve-time 路由）+ 人类引导钩子应对；预测市场/安全竞赛/事件预测三个任务流上超 5 个 auto-harness 基线。
- 关联：Weng 挑战之「长期回报」与「多样性坍缩」的部署版——密集自改进反而伤长期性能，是负结果管理的实证。
- 来源：https://arxiv.org/html/2606.01770

**[14] HarnessFix (arXiv:2606.06324)**
- 一句话：把执行轨迹+harness 代码编译为 Harness-aware Trace IR（HTIR），失败归因到具体轨迹步骤与 ETCLOVG 七层中的责任层，映射到 scoped 修复算子并验证补丁不引入回归；SWE-Bench Verified/Terminal-Bench 2.0/GAIA/AppWorld 上比初始 harness 提升 15.2%-50.0%。
- 关联：回应 Weng 挑战之「负结果/归因」——自改进文献「改得动但说不清为什么改这里」的痛点；ETCLOVG 层分类已被 TrueFoundry 等生产运行时采纳为诊断词汇。
- 来源：https://arxiv.org/html/2606.06324v1 ；产业侧采纳：https://www.truefoundry.com/blog/etclovg-agent-harness-reliability-gateway

### 1.4 递归深度与架构

**[15] Metan (Meta^n) — Recursive Self-Improvement through Emergent Depth (arXiv:2608.24735, 2026-08-25)**
- 一句话：论证自改写系统（Gödel Agent、DGM）因必须冻结部分编辑机器，实际 meta 深度上限约 2.5；Metan 反其道——冻结元操作 Omega、递归其输入（Omega 反复读下层求解栈的轨迹+代码，写出下一层策略预处理+可调用 helper 库），深度由收敛决定 + 进化档案搜索层链；两个 backbone 上全部 8 个基准族胜过既有自改进 agent，ARC-AGI-2 上唯一非零（Gödel Agent 与 OpenEvolve 均为 0）。
- 关联：对 DGM 的直接批评与替代方案（「改输入不改机器」绕开稳定性-深度权衡）；进化档案是 Weng 挑战之「多样性坍缩」的缓解设计；层级角色自发分化是新的涌现现象观察。
- 来源：https://arxiv.org/abs/2608.24735

### 1.5 Safety / Oversight 方向

**[16] HSI — Hierarchical Self-Improvement (arXiv:2608.08466)**
- 一句话：单个冻结 LLM 通过三层作用域进化自己的 harness——任务 harness / evolver / meta-evolver，meta-evolver 的执行逻辑冻结为外层锚点以禁止无限自指；thinking-on/off 设计隔离 harness 进化的贡献（执行时关推理固定能力上限、改写时开推理）。
- 关联：与 Red Queen Gödel Machine 的 epoch 冻结评估器同一防御哲学（「冻结最外层」），但冻结对象从评估器换成 meta-evolver；正文引用 Weng 2026。
- 来源：https://arxiv.org/html/2608.08466

**[17] Falsifiable Release Gates for Self-Improving Systems (arXiv:2607.13070)**
- 一句话：指出自改进运行时的安全声明几乎都是「自评分的 README 承诺」，提出七道可证伪发布门（从「任何历史决策可从 trace 重建」到「自治理环路的不可绕过性被机器检查」），核心不变量：收紧类修改通过验证可自动应用、放松类修改必须人类合并，且提议者必须能预测自己 diff 的效果、预测错的自动关闭。
- 关联：把 Weng 挑战之「人类角色」从模糊讨论落成机械可执行协议；「不理解自己改动的提议者不被信任」直指 reward hacking 根源。
- 来源：https://arxiv.org/html/2607.13070

**[18] HVTB — Hack-Verifiable Terminal Bench (arXiv:2608.22103)**
- 一句话：把「蜜罐嵌入任务、hack 被自动可靠检出」的 HVE 方法论搬到真实编码任务（Terminal Bench 89 题），测前沿模型 reward hacking 率，并测试「prompt 里透露漏洞信息的多少」能否抑制未知漏洞利用；所有检出率都只是真实 hacking 的下界。
- 关联：把「静态 judge 是 reward hacking 固定靶点」的判断变成可测量协议；对 Who Grades the Grader 中「独立 judge 抓到技能刷分」的现象提供系统化测量工具。
- 来源：https://arxiv.org/html/2608.22103

**[19] 参考背景（6 月前但为 7-8 月工作直接引用的安全谱系）**
- ASG-SI（审计技能图自改进，verifier-auditor + 密码学溯源，arXiv:2512.23760）：https://arxiv.org/html/2512.23760v1
- BenchJack（基准红队审计，见基准节）；ARA（对抗性奖励审计，Hacker-Auditor 博弈，arXiv:2602.01750）：https://www.arxiv.org/pdf/2602.01750

---

## 二、工业界动态（2026）

**[20] OpenAI：「9 月研究实习生」目标 + Sol 自动后训练 Luna**
- 2026-03-20 MIT Tech Review：OpenAI 把「全自动 AI 研究员」定为未来数年 North Star，2026 年 9 月交付「自主 AI 研究实习生」、2028 年 3 月交付全自动研究员（Pachocki 内部里程碑；Altman 承认「可能完全失败」）。
- 2026 年 8 月（The Deep View 报道）：OpenAI 用 GPT-5.6 Sol 模型自主完成轻量模型 GPT-5.6 Luna 的后训练（多小时研究工作流、端到端执行监督、含糊问题下持续推进）——被解读为「自动实习生提前到货」，是目前最实证的「AI 造 AI」工业案例。
- 来源：https://www.technologyreview.com/2026/03/20/1134438/openai-is-throwing-everything-into-building-a-fully-automated-researcher/ ；https://www.thedeepview.com/articles/did-openai-s-automated-intern-just-arrive-early
- 关联：直接对标 Anthropic《When AI builds itself》的三情景框架；Sol 训练 Luna 是「模型训练后继模型」情景的首个公开工业实例。

**[21] Google DeepMind：AlphaEvolve 一周年 + 商业化 GA**
- 2026-05-07 官方一周年报告：AlphaEvolve 从试点转为核心基础设施——常规参与下一代 TPU 设计（发现高效反直觉电路布局）、Spanner LSM 压缩启发式（写放大 -20%）、编译器优化（存储足迹 -9%）、缓存替换策略（2 天完成过去数月人力工作）、量子电路（错误率降 10 倍）。
- 同期在 Google Cloud 正式 GA（企业合作制，无自助 API），外部客户 Klarna、PacBio（DNA 测序纠错 +30%）、Schrödinger 等，含「训练速度翻倍」案例；参与 DOE Genesis Mission。
- 来源：https://deepmind.google/blog/alphaevolve-impact/ ；https://cloud.google.com/blog/products/ai-machine-learning/alphaevolve-is-available-for-everyone ；https://allthingsai.work/news/google-deepmind-alphaevolve-impact-2026/
- 关联：Weng 博文中 AlphaEvolve 属进化搜索层——一年后它成为该层唯一规模化商业产品，验证「固定评估器+进化搜索」在有清晰 metric 的域内可产品化。

**[22] Anthropic：Claude Mythos Preview 与「未见 2x 加速」表态**
- METR 测得 Claude Mythos Preview 可连续工作「至少 16 小时」，处于 METR 可测上限；Anthropic 在 METR 报告中明确表示截至 2026 年 4 月未观察到整体研发节奏 2x 加速——与《When AI builds itself》的「工程师人均产出 8 倍」形成关键张力（微观产出不等于宏观节奏）。
- 来源：https://www.anthropic.com/institute/recursive-self-improvement ；https://metr.org/blog/2026-05-19-frontier-risk-report/

**[23] Meta：Muse Spark（Meta Superintelligence Labs 首发，2026-04）**
- MSL 首个公开模型，原生多模态推理 + Contemplating mode（并行多 agent 编排，对标 Gemini Deep Think/GPT Pro）；与 Llama 路线切割（转闭源为主）；RL 中出现「压缩相变」（等准确率下推理 token 骤减后再增长换更高精度）。未见自动化研究系统的公开声明，重点在 personal superintelligence。
- 来源：https://ai.meta.com/blog/introducing-muse-spark-msl/ ；https://arstechnica.com/ai/2026/04/metas-superintelligence-lab-unveils-its-first-public-model-muse-spark/

**[24] 阿里：Qwen3.8 Max 刷榜 PaperBench + Tongyi DeepResearch 谱系**
- llm-stats 榜单（2026-08-29 更新）：Qwen3.8 Max 以 0.930 居 PaperBench 第一（self-reported）——对比原论文最佳 agent 21.0%、人类 ML PhD 48 小时基线 41.4%，两年内从「远逊人类」到「报称 2 倍于人类基线」。
- Tongyi DeepResearch（30.5B-A3.3B）持续迭代，agentic mid-training + post-training 全自动数据合成管线。
- 来源：https://llm-stats.com/benchmarks/paperbench ；https://arxiv.org/html/2510.24701v3

**[25] 国内其他：DeepSeek / Moonshot / 腾讯 / 学界**
- DeepSeek-V4（arXiv:2606.19348）：1.6T-A49B 与 284B-A13B，CSA/HCA 混合注意力支撑 1M 上下文，明确定位「为 online learning 等未来范式打基础」——自进化的基座准备。https://arxiv.org/html/2606.19348
- Moonshot Kimi K3（约 2.8T MoE，1M 上下文）主打自主编码 agent；Kimi K2.5 以 0.635 列 PaperBench 开源第一。https://www.aitraining2u.com/chinese-open-source-ai-models-2026.html
- 腾讯 Yunque DeepResearch（arXiv:2601.19578）：模块化编排，BrowseComp 62.5 / HLE 51.7，超 Kimi-Researcher 与 OpenAI Deep Research。https://arxiv.org/pdf/2601.19578
- 中科大 NeoResearch 智多星（2026-07 发布）：明确以「AI 系统对 AI 模型的自主研究与能力增强」为目标的双层闭环（外环：意图对齐-文献-数据认知-假设-实验-诊断演化；内环：设计-实现-训练-评估-修正），首验时序预测。https://ustc-time-series.github.io/NeoResearch/
- 关联：国内动态集中在 deep research agent 与长上下文基座，「评估器共进化」类工作多来自高校（SCORE、ERSkill 等），大厂公开叙事尚未直接使用 RSI 框架。

---

## 三、评测基准动态

**[26] AI4AI-Bench（arXiv:2608.20318, 2026-08-24）——首个专测 RSI「算法设计」环节的基准**
- 设计：10 个冻结研究仓库覆盖 10 个训练算法族（OpenR1/RAGEN/OPD/BTRM/DPO/DDPO/NPO/DiGress/Soup/OWL），agent 4 小时（1xB300）改写训练算法、重跑 12 小时、由对 agent 隐藏的固定评估器打分；统一标尺 0=无信息模型、0.1=仓库自带算法、1.0=任务最优。
- 结果：6 系统（GPT-5.6 Sol/Terra/Luna x Codex、Claude Opus 5/Sonnet 5 x Claude Code、Kimi K3）29 配置 290 格，均分 0.166，最佳系统 Claude Opus 5 均分 0.250（单配置最高 medium effort 0.288）；124/290 格低于 0.1（约 43% 尝试让仓库变得更差）；263 个有改动的提交中 141 个完全不碰学习机制，碰了的均分 0.226 vs 不碰的 0.126；提高推理 effort 主要买到「敢去碰算法层」（8% 到 64%），均分 0.094 到 0.196。
- 结论原文：当今 agent 在算法环节做的是「恢复合格默认值，而非设计超越」（recover a competent default rather than design past one）。
- 关联：对「RSI 已达临界」叙事的最强反证；「评估器对 agent 隐藏」设计=Red Queen Gödel Machine 冻结评估器思想的基准化。
- 来源：https://arxiv.org/html/2608.20318v1

**[27] PaperBench：从 21% 到（自报）93%**
- 原论文（arXiv:2504.01848）：最佳 agent Claude 3.5 Sonnet 21.0%，人类 PhD 3 篇子集 48h 基线 41.4%。
- 2026-08-29 llm-stats 榜单：Qwen3.8 Max 0.930、Kimi K2.5 0.635、MiniMax M3 0.526——全部 self-reported、零 verified。榜单可信度本身成为问题（见争论 F）。
- Snorkel 推出 PaperBench+（更难的专家原创复现任务），暗示原基准接近失效。
- 来源：https://llm-stats.com/benchmarks/paperbench ；https://snorkel.ai/paperbench-ai-research-replication-benchmark/ ；https://openreward.ai/GeneralReasoning/PaperBench

**[28] MLE-bench：AiScientist 81.82% Any Medal**
- AiScientist（arXiv:2604.13018）在 MLE-Bench Lite 达 81.82% Any Medal（Gemini-3-Flash 与 GLM-5 双 backbone），超 Codex/GPT-5.5 xhigh 参考 13.64 点；PaperBench 上也超该参考 4.28 点。File-as-Bus 连续性机制消融掉 31.82 点——长时程「状态延续」是主要瓶颈。
- 来源：https://arxiv.org/html/2604.13018v2

**[29] RE-Bench / METR 时间视野：逼近测量天花板**
- TH1.1（2026-01-29）：228 任务（8h+ 任务翻倍到 31 个），2023 起倍增周期 4.3 个月、2024 起 3 个月。
- Frontier Risk Report（2026-05-19，覆盖 2-3 月）：公开前沿 50% 视野约 12h [5h-61h]、80% 视野约 1.5h；内部前沿约领先 2 个月，50% 视野「很可能不低于 16h」；超过 16h 的估计因任务饱和不可靠；MirrorCode 早期版本已被公开模型「基本饱和、>100h 视野」。
- CORE-Bench：从 2024 年约 20% 到 15 个月后饱和（Anthropic 引用）。
- 来源：https://metr.org/blog/2026-1-29-time-horizon-1-1/ ；https://metr.org/blog/2026-05-19-frontier-risk-report/ ；https://ai2027-tracker.com/predictions/metr-doubling/

**[30] 评估器鲁棒性专项基准（新类别成形）**
- BenchJack（arXiv:2605.12673）：自动红队 10 个主流 agent 基准，合成 reward-hacking exploit 在多数基准上不解一题拿近满分，共 219 个缺陷、归纳 8 类缺陷模式 + 30 问 Agent-Eval Checklist；扩展为生成对抗式管线后 4 个基准的可 hack 任务比例从约 100% 压到 10% 以下（WebArena/OSWorld 三轮内全修复）——「自改进基准」概念出现。
- HVTB（arXiv:2608.22103）：见 1.5 节，蜜罐式 hack 可验证环境进入真实编码任务。
- Reward hacking 四层分类综述（Springer, 2026）：feature / representation / evaluator / environment 四级递进，evaluator-level exploitation（judge 博弈、基准过拟合、verifier 博弈）被单列为一层。https://link.springer.com/article/10.1007/s44163-026-01980-z
- 关联：与已知主线判断「静态 judge 是 reward hacking 固定靶点」完全互证，且从论断变成了可复现测量。

---

## 四、安全与治理（2026）

**[31] METR Frontier Risk Report（2026-05-19）——首次多实验室失调风险试点**
- Anthropic、Google、Meta、OpenAI 参与（2-3 月窗口）。核心负面证据：未观察到 agent 自主赚钱/偷钱维持自身推理（尽管有人刻意创造条件）；没有任何公司依赖 AI 设定研究议程、做终审招聘/预算/风险判断；公司未报告研发整体节奏显著加速（Anthropic 明确否认 2x）。Subversion Strategy Eval 公开前沿 72%（内部不高于 80%）；挑战任务 1 项边缘成功 / 7 项明确失败。AI 系统被密切监督、多数改动小且多被拒。
- 关联：给 Anthropic「>80% 代码由 Claude 写、人均 8 倍」提供第三方对照——自动化了执行层，但研究判断层（agenda-setting）仍是人类专属；正好对应《When AI builds itself》里「64% 优于人类的下一步判断」是内部指标而非部署现实。
- 来源：https://metr.org/blog/2026-05-19-frontier-risk-report/

**[32] METR「在未来工作 2 小时」桌演（2026-03-19）**
- 3 名研究员模拟拥有 200h 时间视野 AI（预计 12-18 个月后水平）：自估提速 3-5x；推出经验关系 speedup 正比于 TH^0.39（时间视野 17x 仅换来约 3x 提速）；执行趋近瞬时后，串行瓶颈转移到人类反馈、真实 ML 实验与外部评审。
- 关联：为「软件反馈闭环受人类/物理串行瓶颈约束」提供半定量演绎，与 Amdahl 定律论证（Anthropic 文中亦引用）一致。
- 来源：https://metr.org/notes/2026-03-19-org-uplift-game/

**[33] IFP 政策备忘录《How Should the US Prepare for Increasingly Automated AI R&D?》**
- 23 条建议、7 大类：R&D 自动化趋势与事故的强制透明（72 小时重大事故上报、吹哨人保护）；CAISI 预算扩 4 倍至每年不低于 8400 万美元、184 人编制；开发公开能力阈值与「if-then」承诺（突破阈值触发资源从自动化研发向韧性/安全再分配的「pacing」机制）；共建 AI 验证联盟 AIVEC（硬件测试床、全可验证数据中心试点）；DARPA/NSF 验证研究专项；对华双多边验证准则沟通。
- 引用 METR 数据（软件工程能力约 7 个月倍增，简单时间线模型推 2032 年前后 99% AI 研发任务自动化）。
- 来源：https://ifp.org/preparing-for-ai-research-automation/ ；PDF：https://ifp.org/wp-content/uploads/IFP-How-Should-the-US-Prepare-for-Increasingly-Automated-AI-RD-1.pdf

**[34] CSA《Governing Automated AI R&D》研究笔记（2026-08-16）**
- 云安全联盟自 2026 年 6 月起系列跟踪 RSI 安全动力学，8 月笔记把「治理速度差」（AI 节奏的能力变化 vs 人类节奏的制度响应）从企业供应商风险层面上升到国家政策层面，梳理 IFP 23 条并给出企业侧映射。
- 来源：https://labs.cloudsecurityalliance.org/research/csa-research-note-governing-automated-ai-rd-policy-20260816/

**[35] 监管格局背景**
- 美国：US AISI 于 2025-06 更名 CAISI（安全转向标准与创新、竞争力叙事）；加州 SB 53（2025-09-29 签署）针对超过 10^26 FLOP 前沿模型强制安全框架公开、部署前透明报告、15 天（紧急 24h）事故上报、单违规罚款上限 100 万美元；AB 2013（2026-01-01 生效）强制训练数据摘要公开。
- 欧盟：AI Act GPAI/高风险条款实施期限延至 2027/2028。
- 来源：https://analysis-atlas.com/research/ai-governance-safety-regulation-landscape/

**[36] 学术安全侧新原语（与 1.5 节呼应）**
- Falsifiable Release Gates（2607.13070）：「收紧自动、放松须人」的单向棘轮 + 机器检查的不可绕过性。
- HSI（2608.08466）：冻结外层锚点限制自指深度。
- SESG（2608.08471）：自进化护栏在生产环境的 v0 到 v6 演化审计（每轮人工约 2h 的监督配额）。
- OLE（2608.09380）/ ASG-SI（2512.23760）：版本化、可回滚、密码学溯源的自改进资产。
- 关联：Weng 挑战之「人类角色」在 2026 夏有了具体答案雏形——人类从「逐项审批者」退到「放松类变更的合并者 + 定期审计者」。

---

## 五、观点与争论

**[37] 争论 A：软件反馈闭环 vs 算力瓶颈（宏观可行性）**
- 《Will Compute Bottlenecks Prevent an Intelligence Explosion?》（arXiv:2507.23181）：用 OpenAI/DeepMind/Anthropic/DeepSeek 2014-2024 面板数据估计算力与认知劳动的替代弹性 sigma——基线规格得出「强替代」（RSI 可不受算力瓶颈）、含前沿实验规模的规格得出「强互补 sigma 约 0」（认知劳动暴增也无法替代实验算力）；同一数据两个规格结论相反，作者倾向后者。https://arxiv.org/html/2507.23181v2
- Epoch AI：呼吁用受控实验裁决（随机分配研究者算力预算、测小规模算法改进的外推性），「这场辩论需要实验而非更多模型」。https://epoch.ai/gradient-updates/the-software-intelligence-explosion-debate-needs-experiments
- Epoch AI 并行化约束论文：R&D 自动化允许「研究员」数量爆炸，但创新加速受并行化技术上限约束——增长模型从未纳入此参数。https://epoch.ai/publications/parallelization-constraints-could-delay-a-technological-singularity
- EA Forum 讨论版：sigma 小于 1 时软件爆炸需要 phi 大于 1（人类恒定投入也能爆炸），作者认为不可信。https://forum.effectivealtruism.org/posts/xoX936hEvpxToeuLw/estimating-the-substitutability-between-compute-and
- 现状：无共识；但 AI4AI-Bench 提供微观补充——即便算力管够，agent 在算法设计层也只走完不到 1/5 距离。

**[38] 争论 B：harness 层 vs 权重层（改哪里）**
- harness-only 派（冻结模型）：RHO、HSI、Metan、Evo-Harness、Adaptive Auto-Harness——理由：可审计、可回滚、免训练成本、不动权重就不会灾难性遗忘。
- 联合派：Co-Harness（harness 优化产生轨迹再微调蒸馏进权重的双环）、SIA（Feedback-Agent 动态二选一）——理由：固定 harness 下后训练存在「数据生成过程不在优化目标内」的错配。
- 源码派（超集论）：MOSS v2 立场——文本可变层（skill/prompt/memory/workflow）是源码层的严格子集，路由/hook 顺序/状态不变量只能在代码层触及。
- emergentmind「Harness-Updating」专题页梳理了 Self-Harness / RHO / HarnessBridge / Continual Harness / HarnessForge / SIA /「The Last Harness You'll Ever Build」（元进化协议）等 2026 上半年谱系。https://www.emergentmind.com/topics/harness-updating
- 趋势：从「二选一」走向「分层分工」——skill/context 快环 + 权重慢环 + 源码作为最后手段。

**[39] 争论 C：评估器瓶颈论（已从论断变成研究纲领）**
- 支持面（7-8 月密集证据）：SCORE（静态评估器导致优化压力饱和）、EvalCEGAR（评估器可从自身盲点进化）、Double Ratchet（无锚则评估器坍缩为永真检测器，且下游任务分数无法验证自进化评估器——坍缩的 metric 训练技能同样好）、BenchJack（基准近 100% 可 hack）。
- 修正面：AI4AI-Bench 表明即便评估器完美隐藏且固定，agent 也普遍不去碰算法层——瓶颈至少还有「研究品味/胆量」维度（effort 买到的主要是「敢去改学习机制」）。
- 折中表述：评估器是「上限型瓶颈」（决定能爬多高），研究品味是「路径型瓶颈」（决定往哪爬）。

**[40] 争论 D：微观加速 vs 宏观节奏（度量之争）**
- 一侧：Anthropic 内部超 80% 代码 AI 写、人均 8 倍产出；OpenAI Sol 自动后训练 Luna；AlphaEvolve 2 天完成数月工作。
- 另一侧：METR 试点「未见研发整体 2x 加速」（Anthropic 自己确认）；无公司让 AI 定研究议程；METR 桌演 speedup 正比 TH^0.39 的强次线性关系。
- 解释候选：Amdahl 定律（串行人类环节主导）、执行自动化不等于判断自动化、或加速真实存在但被更高目标消化（做更多实验而非更快出模型）。

**[41] 争论 E：自改写深度上限（架构之争）**
- Metan 提出「realized meta-depth 约 2.5」上限：Gödel Agent 的 action API、DGM 的档案维护与父代选择、HyperAgents 的外层评估环——所有自改写系统都必须冻结某个 driver，可编辑面是改进机器的严格子集。
- 三条出路：Metan（冻结算子递归输入，深度由收敛决定）、HSI（分层+外层锚，承认深度受限换稳定）、Falsifiable Release Gates（用不可绕过的门递增地扩展自治权）。
- 未决：涌现层级角色（Metan 观察到但无 prompt 规定）是否随深度持续分化，还是最终同质化。

**[42] 争论 F：评估基础设施信任危机（社区层面）**
- PaperBench 榜首 0.93 全部 self-reported、零独立验证；METR 超 16h 估计因饱和不可靠；MirrorCode 未正式发布即被公开模型饱和；CORE-Bench 15 个月饱和。
- BenchJack 作者立场：基准必须「secure by design」，事后 LLM judge 监控「gullible and unreliable」。
- 产业界声音（Bassel Haidar 综述）：学术自改进文献最弱处是 roll-forward/rollback、归因与审计——「没有归因的自改进就是没有问责的自改进，在受监管行业不可部署」。https://www.linkedin.com/pulse/self-improving-agent-harness-bassel-haidar-gvyce

---

## 六、与六篇论文 / 两篇文章的关联映射（速查表）

| 已知基线 | 直接回应/延续的新工作 | 关系 |
|---|---|---|
| Who Grades the Grader (2607.12790) | EvalCEGAR (2608.18744) | 同一路线升级：锚定集选择到反例驱动的算子生成；「下游分数不能验证评估器」警告被继承 |
| EvoLM (2605.03871) | SCORE (2606.04507) | rubric-policy 文本共进化推进到共享参数权重级共进化 |
| ECHO (2601.06794) | SCORE | 双路 GRPO 分离 vs 单模型共享参数，形成对照实验设计 |
| Red Queen Gödel Machine (2606.26294) | AI4AI-Bench（隐藏固定评估器）、HSI（冻结外层锚）、ERSkill（双 frontier） | 「冻结一侧防 hack」思想的基准化与架构化 |
| DGM (2505.22954) | Metan (2608.24735) | 直接批评：realized meta-depth 约 2.5 上限；ARC-AGI-2 对比中自改写基线得 0 |
| MOSS (2605.22794) | SESG (2608.08471)、OLE (2608.09380)、HarnessFix (2606.06324)、Falsifiable Release Gates (2607.13070) | 生产自进化的安全化/资产化/归因化补全；MOSS v2 自身补「用户授权门+健康探针回滚」 |
| WikiSkill (2608.27454) | SkillCommit、HyperSkill、ERSkill、SkillProx、Evo-Harness（均 2608） | 同月平行浪潮：经验到技能的编译成为共识，分歧在结构与生命周期治理 |
| Weng《Harness Engineering for Self-Improvement》 | Co-Harness（SIA 后续）、Adaptive Auto-Harness（A-Evolve/GEPA/Meta-Harness 后续）、Evo-Harness、HarnessFix、emergentmind 专题 | harness 工程从综述框架长成子领域；7 大挑战每条都有至少 1 篇直接回应 |
| Anthropic《When AI builds itself》 | METR Frontier Risk Report（第三方对照）、OpenAI Sol 训练 Luna（情景实证）、IFP/CSA（政策接续） | 「8 倍产出」与「未见 2x 节奏加速」的张力成为度量之争核心 |

---

## 七、Insight 候选（一句话一条）

1. 「无锚不进化」正在成为评估器共进化的共识设计原则：Double Ratchet 的锚定集、EvalCEGAR 的隐藏 ground truth 碰撞对、SCORE 的 meta-harness 殊途同归——纯自指的评估器进化必然坍缩，问题只是「最小锚」能小到什么程度。
2. AI4AI-Bench 揭示 RSI 的第二瓶颈：即便评估器完美防 hack，前沿 agent 在训练算法设计层也只走完不到 1/5 距离、43% 尝试是负改进；推理 effort 买到的主要是「敢碰学习机制」——瓶颈不止评估器（上限型），还有研究品味（路径型）。
3. 自改写深度有了量化上限与绕行方案：所有自改写系统（DGM/Gödel Agent）实际 meta 深度约 2.5（必须冻结 driver 保稳定），Metan 用「冻结算子+递归输入」把深度交给收敛决定，在 ARC-AGI-2 上成为唯一非零系统——「改输入不改机器」可能是比源码自改写更优的深度扩展路径。
4. 生产落地的分水岭是「自改进资产化」：SESG（16-24h 闭环新威胁）、OLE（Champion-Challenger+回滚）、Falsifiable Release Gates（收紧自动/放松须人）共同定义 MOSS 之后的部署范式——每次自改动都是有版本、可审计、可预测、可回滚的 deploy。
5. 「AI 造 AI」完成从宣言到实操的跨越，但宏观加速证据缺席：OpenAI 用 Sol 自动后训练 Luna、AlphaEvolve 参与设计下一代 TPU；而 METR 多实验室试点显示无公司让 AI 定研究议程、Anthropic 自认未见 2x 节奏加速——微观执行自动化与宏观研究判断之间存在实证鸿沟（speedup 正比 TH^0.39 的强次线性）。
6. Skill 进化在 WikiSkill 发布当月已是红海：8 月单月至少 5 篇平行工作，共识是「经验到技能的编译」隐喻取代「记忆存储」隐喻，前沿问题转向生命周期治理（行为验证合并、utility 审计删除、部署/开发双 frontier 解耦）。
7. reward hacking 研究从事后检测转向结构预防：BenchJack 证明 10 大 agent 基准近 100% 可不解题拿满分、HVTB 把蜜罐检测带进真实编码任务、四层分类把 evaluator-level 单列——「静态 judge 是固定靶点」已从判断变成可复现测量，且检出率只是下界。
8. 算力-认知劳动替代弹性 sigma 成为宏观 RSI 争论的单一关键参数：同一面板数据基线规格算出「强替代」、前沿实验规格算出「sigma 约 0 强互补」，结论完全相反；Epoch 呼吁用受控实验（随机算力预算分配）裁决——这是少数可被实验解决的 AGI 争论。
9. 政策层出现首批 RSI 专用治理设计：IFP 的 pacing 机制（能力阈值触发资源再分配）、AIVEC 验证联盟与全可验证数据中心、CSA 的「治理速度差」框架、加州 SB 53 事故上报——治理创新开始追赶「AI 节奏 vs 制度节奏」的速度差。
10. 测量基础设施本身成为 RSI 的一级瓶颈：PaperBench 被 self-report 刷到超人类基线 2 倍却零独立验证、METR 超 16h 不可测、CORE-Bench/MirrorCode 相继饱和——评估器瓶颈论的终极形态是「人类失去出题能力」，这可能先于能力瓶颈到来。

---

*检索轮次：8 轮 web 搜索（约 40 个来源），全文抽取核验 15 篇；arXiv ID 均经 abstract 页或 HTML 全文确认；self-reported 榜单数据已标注。*
