# Co-Harness 深度解读：把有效的脚手架蒸馏进权重——harness 与模型的双环共进化

> **Co-Harness: Co-Evolving Harness and Model for Self-Improving LLM Agents**
> arXiv 2607.22688 v1（2026-07-17）· 美团 + Allen Institute for AI（Zhengyu Chen†、Teng Xiao†、Huaisheng Zhu、Yige Yuan、Luan Zhang、Jingang Wang；†同等贡献）
> 归档：`papers/en/2607.22688_CoHarness.pdf` · 中译 `papers/zh/2607.22688_CoHarness_zh.pdf`

---

## 1. 一句话定位

后训练 agent 时，现有流水线只更新模型参数、把 harness（prompt / 工具 / 技能 / 中间件 / 记忆）当作手工设计的固定物——但 harness 决定了训练轨迹的质量，却从不从训练中观察到的失败里学习。Co-Harness 把两者放进同一个交替优化：**HarnessCritic** 分析失败轨迹、按五类归因分类法定位到 harness 级失败模式、提出经局部验证的 diff 进入版本化注册表；然后用改进后 harness 生成的高质量轨迹 SFT 模型，**把有效的脚手架蒸馏进权重**。两轮双环在 Qwen3-8B/32B × AIME24/25/HMMT25 上平均 **+20.4 pp**（58.5→78.9），且超过人工精心设计的静态 harness **+24.7 pp**。200+ 小时无人干预案例：从 32 秒崩溃的配置到 22 个 harness 版本、自发现 ensemble 策略、自动回滚回归。它是"分层分工"（文本层快环 + 权重层慢环，报告 10）在通用 LLM agent 后训练上的实现；与 Continual Harness（报告 11）的具身域共学习并列为 2026 年两个模型-harness 共进化闭环——但论文自称"首个共进化框架"不成立，CH 早两个月。

## 2. 要解决的问题

论文提出 **Harness Debt** 概念：agent 训练时 harness 是固定的、人工设计的，于是——

1. **harness 缺陷污染训练数据**：工具 schema 错、重试逻辑缺失、上下文溢出——这些导致的失败轨迹被当作模型失败，模型在噪声上训练；
2. **harness 从不学习**：训练中观察到的失败里有大量可归因到 harness 的模式，但没有机制把它们反馈回 harness；
3. **模型可能学会依赖脚手架**：如果 harness 补偿了模型弱点，模型可能永远学不会独立做那件事——这是 Harness Debt 的另一面。

Co-Harness 的假设：**harness 与模型应该交替优化，且 harness 改进要被蒸馏进权重**——这样模型变强后不再需要那些脚手架（还债），同时更强的模型暴露新的失败模式，给 harness 提供新的优化目标。

§3.6 给出三个复利条件：harness 更新必须提升**轨迹质量**（不只是表面格式）；模型更新必须**内化**改进（真正变强而非依赖脚手架）；更强的模型必须**解锁新 harness 机会**。任一条件失败，双环退化为单环。

## 3. 为什么此前做不通：三条线各差一块

| 已有路线 | 有什么 | 缺什么 |
|---|---|---|
| 标准 RL / SFT 后训练 | 更新权重 | harness 固定，缺陷污染数据 |
| GEPA / prompt 优化 | 进化 prompt | 只碰 prompt；无归因；不蒸馏进权重 |
| Meta-Harness（报告 13） | 外部 coding agent 自由改 harness | proposer 冻结；能力留在 harness 不进模型 |
| Self-Harness（报告 14） | 模型改自己的 harness | 权重不动；能力留在 harness |
| Continual Harness（报告 11） | 模型-harness 共学习（具身域） | 单域原型；在线免重置形态 |
| iCoder（报告 19） | agent 主导训练管线 | 改的是训练配方，不是运行时 harness |

关键缺口：**没有人在通用 LLM agent 后训练上把"harness 从失败学习"与"模型从 harness 学习"接成闭环**。GEPA 改 prompt 不训模型；标准 RL 训模型不改 harness；Meta-Harness 改 harness 但能力不进权重。

## 4. 方法机制

### 4.1 双环结构（Algorithm 3）

**Co-Harness Loop**（每轮 K 次）：
1. 在 (θ_t, φ_t) 下收集失败轨迹 F⁻_t；
2. HarnessCritic C 产出归因集 A_t = C(F⁻_t, φ_t)；
3. 聚合 diff：ΔΦ_t = AggregateDiffs(A_t)；
4. 应用得候选 φ̃_t；
5. **Validate**：目标失败模式改善（δ_in > 0）且 held-out 无回归（δ_out ≥ 0）→ 提交注册表；否则拒绝。

**Model Alignment Loop**：用最优 harness φ*_t 收集轨迹 D_t，保留通过 verifier 的，SFT：θ_{t+1} = argmax Σ log p_θ(τ|x)。

### 4.2 HarnessCritic 与失败归因分类法（Table 4）

| 根因 | 主要位点 | 典型症状 |
|---|---|---|
| prompt ambiguity | P | 指令欠规格或目标冲突 |
| tool schema error | T | 无效工具调用、参数 schema 错、后端不匹配 |
| skill missing | S | 缺可复用例程或分解原语 |
| middleware mismatch | Mid | 循环协议、hook 行为、上下文管理有缺陷 |
| memory overflow | M | 持久状态溢出、记忆过期、检索失败 |
| **agent error** | – | harness 检查后仍是模型侧问题（**弃权标签**，排除出补丁生成） |

每条失败产出结构化记录 {root cause, harness dim, severity, evidence, diff suggestion}——evidence 锚定到具体轨迹事件，diff 指定局部补丁目标（工具 schema 字段、中间件 hook 插入点、编排策略）。**聚合**：按复现率、严重度、字段路径一致性排序，合并兼容建议为单个 diff。diff **刻意局部**——只记录变化的字段及新旧值，为可解释性与回滚服务。

**人工校验**：三位专家标注 + 第三人仲裁校验归因准确性——这一步把"改 harness"从盲目试错变成有语义依据的定向修复，是它与 GEPA 式纯 prompt 进化的本质区别。

### 4.3 版本化注册表

接受的补丁写入版本化 harness 注册表——审计线索 + 完整回滚。v20–v22 案例即由此自动回滚。

## 5. 实验结果全景

### 5.1 设置

Tool-Integrated Reasoning（TIR）：agent 交替链式推理与 Python 工具调用解数学竞赛题。模型 Qwen3-8B / Qwen3-32B；基准 AIME24 / AIME25 / HMMT25；人工静态 harness 作对照。

### 5.2 主结果（Table 6）

| 模型 | 基准 | 人工静态 | R0（仅进化 harness） | R1 | R2（两轮双环） | Δ vs R0 | Δ vs 人工 |
|---|---|---|---|---|---|---|---|
| Qwen3-8B | AIME24 | 59.3 | 63.3 | 84.0 | **84.7** | +21.4 | +25.4 |
| Qwen3-8B | AIME25 | 51.3 | 56.9 | 66.7 | **78.3** | +21.4 | +27.0 |
| Qwen3-8B | HMMT25 | 34.7 | 39.6 | 52.3 | **59.7** | +20.1 | +25.0 |
| Qwen3-32B | AIME24 | 72.0 | 76.7 | 85.3 | **87.3** | +10.6 | +15.3 |
| Qwen3-32B | AIME25 | 61.3 | 64.9 | 83.9 | **86.3** | +21.4 | +25.0 |
| Qwen3-32B | HMMT25 | 46.7 | 49.8 | 68.7 | **77.0** | +27.2 | +30.3 |
| **平均** | | 54.2 | 58.5 | 73.5 | **78.9** | **+20.4** | **+24.7** |

三条观察：
- **越难的基准收益越大**：HMMT25 上 8B +20.1、32B +27.2；AIME24（基线已高）收益最小——脚手架缺陷在多步复杂推理上更容易成为失败原因。
- **更大模型在难题上受益更多**：32B 的 HMMT25 增益（+27.2）远超其 AIME24 增益（+10.6）——更强模型有更多可被 harness 解锁的潜在能力。
- **8B 饱和**：AIME24 上 R2（84.7）对 R1（84.0）几乎无提升——模型推理容量逼近该基准上限，剩余错误多为模型内部而非 harness 可归因。

### 5.3 Harness Debt 反向证据

担心"在补偿模型弱点的脚手架下训练会让模型依赖脚手架"，但每轮**测试时绝对精度都在上升**（8B AIME25 56.9→66.7→78.3），说明学到的是可迁移推理技能而非对 harness 的依赖。

### 5.4 200+ 小时无人干预案例（Figure 7，Qwen3-8B × AIME24，22 个 harness 版本）

- **初始配置**：32 秒内因 vllm KV cache 错误崩溃。
- **Phase 1（init–v7）工程修复**：ThreadPool 换 ProcessPool + SIGKILL 清理、开启 thinking；v3 首次跑完 90 题得 **59.6%**（3.78 h）。
- **Phase 2（v12–v15）效率优化**：全局批推理 **8.7× 加速**，v9 达 61.5% / 1.11 h。
- **Phase 3 发现并验证 ensemble 策略**：v15 + v19 投票达 **63.3% / 2.29 h**——最高精度且在 3.33 h 时间预算内。
- **v20–v22 回归**：引入的领域专用 prompt 与 Qwen3 内部推理冲突导致回归，**被自动检测并回滚**。

0% 崩溃、覆盖三个优化阶段、全部 22 版由 agent 产出。

## 6. 局限

1. **"首个共进化框架"的自称不成立**：结论声称 Co-Harness 是"first framework to co-evolve both"，但 Continual Harness（arXiv 2605.09998，2026-05-11）早两个月已在具身域完成模型-harness 共学习闭环（Refiner 改 harness + PRM/教师重标注/soft SFT 改权重）。更准确的定位：CH 首发于具身域、Co-Harness 首次推广到通用 LLM agent 后训练。
2. **实验域比叙事窄**：摘要以"automated AI research 的后训练"开题，实验全部是工具集成数学推理——数学有干净的可验证奖励，harness 归因也相对容易；能否迁移到 verifier 弱的研究任务未证明。
3. **归因能力有硬边界**：作者承认需要反事实控制流推理的失败模式归因精度下降，且**结构性 harness 重设计仍是人的责任**——HarnessCritic 做的是局部 diff，不是架构搜索。
4. **依赖强 critic 与冷启动失败量**：需要有能力的 critic LLM、最小体量的失败轨迹、多轮 SFT 算力——三个前提都指向"这是大厂后训练管线的增强件，不是小团队工具"。
5. **锚仍是固定基准**：验证集分数是 diff 接受的唯一判据，评估器共进化（报告 03-06）的问题原样保留。
6. **只有两轮**：R2 在 8B AIME24 上已饱和，更多轮是否继续复利、还是进入 Harness Debt 的另一种形态（harness 越来越针对特定模型版本），没有数据。

## 7. 意义与位置

**对报告 10 分层分工的实现**：文本层快环（HarnessCritic diff，小时级）+ 权重层慢环（每轮 SFT）在通用 agent 上的第一个完整版本；与 CH 的差别在触发方式——CH 是 episode 内免重置在线精炼，Co-Harness 是离线批次交替。

**对报告 11 能力地板的补充数据**："更强模型在难题上受益更多"与 CH 的"弱模型给更强脚手架反而更差"是同一曲线的两端——harness 收益随基座能力单调上升，地板之下为负、天花板附近饱和（8B AIME24 案例）。

**对报告 13 Meta-Harness 的分工**：Meta-Harness 让外层 coding agent 读全部历史轨迹自由改写 harness 代码（proposer 冻结），Co-Harness 用归因分类法约束改动为局部 diff 并把收益蒸馏进权重——前者搜索空间大、后者可控性高，且**只有后者让能力脱离 harness 持续存在**。Meta-Harness Discussion 里"下一步共进化 harness 与权重"的展望，Co-Harness 是第一个通用域实现。

**对报告 14 Self-Harness**：两者的接受门同构（δ_in > 0 且 δ_out ≥ 0 vs Δ_in ≥ 0 且 Δ_ho ≥ 0 且 max > 0）；Self-Harness 不训模型，Co-Harness 训——Self-Harness 的 harness 是终点，Co-Harness 的 harness 是中间件。

**对报告 02 Anthropic 叙事的微观印证**：200+ 小时无人干预、从崩溃配置自恢复、自发现 ensemble——这是"AI 改进 AI 训练基础设施"在单一实验尺度上的可复现样本，也是 Bostrom crossover（报告 00）意义上"系统自身贡献"的可量化案例（22 版全部由 agent 产出）。

**对报告 08 MOSS**：版本化注册表 + 回归回滚（v20–v22 案例）是对 MOSS 门控纪律的又一次独立确认——文本/配置层自改进的安全基础设施已趋同。

**对报告 18 Prime Agent**：Prime Agent 结论"模型没被训练来操作 harness"——Co-Harness 正是训练模型内化 harness 行为的方法；两者合起来是 CH 所预言"模型-harness 共学习将成主导路线"的两个半边。
