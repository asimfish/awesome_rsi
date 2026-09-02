# 解读报告 21 · Co-Harness：harness 与模型权重的共进化

| 项目 | 内容 |
|---|---|
| arXiv | 2607.22688 v1（2026-07-17） |
| 作者 | Zhengyu Chen†, Teng Xiao†, Huaisheng Zhu, Yige Yuan, Luan Zhang, Jingang Wang（美团 + Allen Institute for AI；†同等贡献） |
| 归档 | `papers/en/2607.22688_CoHarness.pdf` · `papers/zh/2607.22688_CoHarness_zh.pdf` |
| 在调研中的位置 | "分层分工"（文本层快环 + 权重层慢环，报告 10 §2）在通用 LLM agent 后训练上的实现；与 Continual Harness（报告 11）的具身域共学习并列为 2026 年两个模型-harness 共进化闭环，但二者对"谁先"有争议（见批评 1） |

## 一句话核心主张

后训练 agent 时，现有流水线只更新模型参数、把 harness（prompt / 工具 / 技能 / 中间件 / 重试逻辑 / 上下文管理 / 记忆）当作手工设计的固定物——但 harness 决定了训练轨迹的质量，却从不从训练中观察到的失败里学习。Co-Harness 把两者放进同一个交替优化：**HarnessCritic** 分析失败轨迹、归因到 harness 级失败模式、提出经局部验证的 diff；然后用改进后 harness 生成的高质量轨迹微调模型，**把有效的脚手架蒸馏进权重**。两轮双环在 Qwen3-8B/32B × AIME24/25/HMMT25 上平均 +20.4 pp，且超过人工精心设计的静态 harness +24.7 pp。

## 方法拆解

**双环结构**。Co-Harness Loop：agent 在任务集上 rollout → 收集错误轨迹 → HarnessCritic 按失败归因分类法（Table 4：前五类为可操作的 harness 缺陷——工具 schema 错误、中间件/重试钩子缺失、上下文/记忆溢出、超时预算、prompt 欠规格；其余归为模型内部错误）定位责任组件 → 生成局部 diff → 在验证集上确认无回归后进入版本化 harness 注册表。Model Alignment Loop：用当前最优 harness 生成轨迹，筛选高质量样本做 SFT。两环交替：更好的 harness 产生更干净的轨迹训出更强的模型，更强的模型又解锁此前不可达的 harness 改进。

**失败归因是整个方法的关键部件**。论文用人工标注（三位专家、第三人仲裁）校验 HarnessCritic 的归因准确性——这一步把"改 harness"从盲目试错变成有语义依据的定向修复，也是它与 GEPA 式纯 prompt 进化的本质区别。

**200+ 小时无人干预案例（Figure 7）**。Qwen3-8B × AIME24 上 22 个 harness 版本的完整轨迹：初始配置 32 秒内因 vllm KV cache 错误崩溃；Phase 1（init–v7）工程修复——ThreadPool 换 ProcessPool + SIGKILL 清理、开启 thinking，v3 首次跑完 90 题得 59.6%（3.78 h）；Phase 2 效率优化 8.7× 加速（v9 达 61.5% / 1.11 h）；Phase 3 发现并验证 ensemble 策略，v15+v19 投票达 **63.3% / 2.29 h**（最高精度且在 3.33 h 时间预算内）；v20–v22 引入的领域专用 prompt 与 Qwen3 内部推理冲突导致回归，被自动检测并回滚。

## 关键数字

| 模型 | 基准 | 人工静态 harness | R0（仅进化 harness） | R2（两轮双环） | Δ vs 人工 |
|---|---|---|---|---|---|
| Qwen3-8B | AIME24 / AIME25 / HMMT25 | 59.3 / 51.3 / 34.7 | 63.3 / 56.9 / 39.6 | **84.7 / 78.3 / 59.7** | +25.4 / +27.0 / +25.0 |
| Qwen3-32B | AIME24 / AIME25 / HMMT25 | 72.0 / 61.3 / 46.7 | 76.7 / 64.9 / 49.8 | **87.3 / 86.3 / 77.0** | +15.3 / +25.0 / +30.3 |
| 平均 | | 54.2 | 58.5 | **78.9** | +24.7 |

- **越难的基准收益越大**：HMMT25 上 8B +20.1 pp、32B +27.2 pp；AIME24（基线已高）收益最小——脚手架缺陷在多步复杂推理上更容易成为失败原因
- **更大模型在难题上受益更多**：32B 的 HMMT25 增益（+27.2）远超其 AIME24 增益（+10.6）——更强模型有更多可被 harness 解锁的潜在能力
- **8B 饱和**：AIME24 上 R2（84.7）对 R1（84.0）几乎无提升——模型推理容量逼近该基准上限，剩余错误多为模型内部而非 harness 可归因
- **Harness Debt 反向证据**：担心"在补偿模型弱点的脚手架下训练会让模型依赖脚手架"，但每轮测试时绝对精度都在上升（8B AIME25 56.9→78.3），说明学到的是可迁移推理技能而非对 harness 的依赖

## 局限与批评

1. **"首个共进化框架"的自称不成立**：结论声称 Co-Harness 是"first framework to co-evolve both"，但 Continual Harness（arXiv 2605.09998，2026-05-11，报告 11）早两个月已在具身域完成模型-harness 共学习闭环（Refiner 改 harness + PRM/教师重标注/soft SFT 改权重）。更准确的定位是：CH 首发于具身域、Co-Harness 首次推广到通用 LLM agent 后训练——报告 10 已按此修正。
2. **实验域比叙事窄**：摘要以"automated AI research 的后训练"开题，实验全部是工具集成数学推理（AIME/HMMT）——数学有干净的可验证奖励，harness 归因也相对容易；能否迁移到 verifier 弱的研究任务未证明。
3. **归因能力有硬边界**：作者承认需要反事实控制流推理的失败模式归因精度下降，且**结构性 harness 重设计仍是人的责任**——HarnessCritic 做的是局部 diff，不是架构搜索。
4. **依赖强 critic 与冷启动失败量**：需要有能力的 critic LLM、最小体量的失败轨迹、多轮 SFT 算力——三个前提都指向"这是大厂后训练管线的增强件，不是小团队工具"。
5. **锚仍是固定基准**：验证集分数是 diff 接受的唯一判据，评估器共进化（报告 03-06）的问题原样保留；但版本化注册表 + 回归回滚（v20–v22 案例）是对 MOSS（报告 08）门控纪律的又一次独立确认。

## 与本调研的连线

1. **对报告 10 分层分工的实现**：文本层快环（HarnessCritic diff，小时级）+ 权重层慢环（每轮 SFT）在通用 agent 上的第一个完整版本；与 CH 的差别在触发方式——CH 是 episode 内免重置在线精炼，Co-Harness 是离线批次交替。
2. **对报告 11 能力地板的补充数据**："更强模型在难题上受益更多"与 CH 的"弱模型给更强脚手架反而更差"是同一曲线的两端——harness 收益随基座能力单调上升，地板之下为负、天花板附近饱和（8B AIME24 案例）。
3. **对报告 13 Meta-Harness 的分工**：Meta-Harness 让外层 coding agent 读全部历史轨迹自由改写 harness 代码（proposer 冻结），Co-Harness 用归因分类法约束改动为局部 diff 并把收益蒸馏进权重——前者搜索空间大、后者可控性高，且只有后者让能力脱离 harness 持续存在。
4. **对报告 02 Anthropic 叙事的微观印证**：200+ 小时无人干预、从崩溃配置自恢复、自发现 ensemble——这是"AI 改进 AI 训练基础设施"在单一实验尺度上的可复现样本，也是 Bostrom crossover（报告 00）意义上"系统自身贡献"的可量化案例（22 版全部由 agent 产出）。

