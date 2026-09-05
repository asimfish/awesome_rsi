# Co-Harness 深度解读：交替改进 harness，并用生成的轨迹训练模型

> **Co-Harness: Co-Evolving Harness and Model for Self-Improving LLM Agents**
> arXiv 2607.22688 v1（2026-07-17）· 美团 + Allen Institute for AI（Zhengyu Chen†、Teng Xiao†、Huaisheng Zhu、Yige Yuan、Luan Zhang、Jingang Wang；†同等贡献）
> 归档：`papers/en/2607.22688_CoHarness.pdf` · 中译 `papers/zh/2607.22688_CoHarness_zh.pdf`

---

## 1. 一句话定位

现有 agent 后训练流程只更新模型参数，将人工设计的 harness（prompt / 工具 / 技能 / 中间件 / 记忆）保持固定。harness 影响训练轨迹的质量，却未根据训练中观察到的失败更新。Co-Harness 交替优化两者：**HarnessCritic** 分析失败轨迹，按五类归因定位 harness 级失败模式，提出 diff，经局部验证后写入版本化注册表。再用改进后 harness 生成的高质量轨迹对模型进行 SFT，**将有效的操作方法蒸馏进权重**。

两轮双环在 Qwen3-8B/32B × AIME24/25/HMMT25 上平均提高 **+20.4 pp**（58.5→78.9），比人工设计的静态 harness 高 **+24.7 pp**。一个 200+ 小时的无人干预案例从 32 秒就崩溃的配置开始，生成了 22 个 harness 版本，自行发现 ensemble 策略，并在检测到回归后自动回滚。

本文实现了报告 10 所讨论的分层分工，在通用 LLM agent 后训练中结合文本层快环与权重层慢环。它与 Continual Harness（报告 11）的具身域共学习同为 2026 年的模型-harness 共进化系统。但论文自称"首个共进化框架"不成立，CH 早两个月已完成相应工作。

## 2. 要解决的问题

论文用 **Harness Debt** 描述 agent 训练时保持人工设计的 harness 不变所带来的问题：

1. **harness 缺陷影响训练数据**：工具 schema 错误、缺少重试逻辑或上下文溢出造成的失败，被当作模型失败用于训练，因而引入噪声；
2. **训练失败未用于更新 harness**：训练轨迹中有大量可归因到 harness 的失败，但没有机制将这些发现用于修改 harness；
3. **模型可能依赖外部辅助**：如果 harness 持续补偿模型的弱点，模型可能始终无法独立完成相应任务。这也属于 Harness Debt。

Co-Harness 假设，**harness 与模型应交替优化，并将 harness 改进蒸馏进权重**。模型通过训练掌握相应能力后，就不再需要原有的辅助。同时，模型能力增强会暴露新的失败模式，为 harness 提供新的优化目标。

§3.6 列出持续改进的三个条件。harness 更新必须改善**轨迹的实质质量**。模型更新必须让模型**掌握改进后的能力**，减少对外部辅助的依赖。模型增强后，还必须出现**新的 harness 改进机会**。任一条件不成立，双环就会退化为单环。

## 3. 为什么此前做不通：三条线各差一块

| 已有路线 | 有什么 | 缺什么 |
|---|---|---|
| 标准 RL / SFT 后训练 | 更新权重 | harness 固定，其缺陷影响训练数据 |
| GEPA / prompt 优化 | 进化 prompt | 只改 prompt；无归因；不蒸馏进权重 |
| Meta-Harness（报告 13） | 外部 coding agent 自由改 harness | proposer 冻结；改进保留在 harness 中，未用于训练模型 |
| Self-Harness（报告 14） | 模型改自己的 harness | 权重不变；改进保留在 harness 中 |
| Continual Harness（报告 11） | 模型-harness 共学习（具身域） | 单域原型；在线运行，不重置状态 |
| iCoder（报告 19） | agent 主导训练流程 | 修改训练方案，未修改运行时 harness |

此前尚未在通用 LLM agent 后训练中，**根据失败改进 harness，再用改进后的 harness 训练模型**。GEPA 修改 prompt，未训练模型；标准 RL 训练模型，但保持 harness 不变；Meta-Harness 修改 harness，未将改进蒸馏进权重。

## 4. 方法机制

### 4.1 双环结构（Algorithm 3）

**Co-Harness Loop**（每轮 K 次）：
1. 在 (θ_t, φ_t) 下收集失败轨迹 F⁻_t；
2. HarnessCritic C 生成归因集 A_t = C(F⁻_t, φ_t)；
3. 聚合 diff：ΔΦ_t = AggregateDiffs(A_t)；
4. 应用修改，得到候选 φ̃_t；
5. **Validate**：目标失败模式改善（δ_in > 0）且 held-out 无回归（δ_out ≥ 0）→ 提交注册表；否则拒绝修改。

**Model Alignment Loop**：用最优 harness φ*_t 收集轨迹 D_t，保留通过 verifier 的轨迹，用于 SFT：θ_{t+1} = argmax Σ log p_θ(τ|x)。

### 4.2 HarnessCritic 与失败归因分类法（Table 4）

| 根因 | 主要位点 | 典型症状 |
|---|---|---|
| prompt ambiguity | P | 指令规定不充分或目标冲突 |
| tool schema error | T | 无效工具调用、参数 schema 错误、后端不匹配 |
| skill missing | S | 缺少可复用例程或分解原语 |
| middleware mismatch | Mid | 循环协议、hook 行为、上下文管理有缺陷 |
| memory overflow | M | 持久状态溢出、记忆过期、检索失败 |
| **agent error** | – | 检查 harness 后，仍判为模型侧问题（**弃权标签**，不为此生成补丁） |

每条失败生成一条结构化记录 {root cause, harness dim, severity, evidence, diff suggestion}。evidence 对应具体轨迹事件，diff 指定局部补丁目标，包括工具 schema 字段、中间件 hook 插入点或编排策略。**聚合**时，按复现率、严重度、字段路径一致性排序，将兼容的建议合并为单个 diff。diff **只记录局部修改**，列出变化的字段及新旧值，便于检查与回滚。

**人工校验**：三位专家参与标注，并由第三人仲裁，检查归因是否准确。归因为 harness 的定向修复提供语义依据；GEPA 式进化则只优化 prompt。

### 4.3 版本化注册表

接受的补丁写入版本化 harness 注册表，保留审计记录并支持完整回滚。v20–v22 案例通过这一机制自动回滚。

## 5. 实验结果全景

### 5.1 设置

实验采用 Tool-Integrated Reasoning（TIR），agent 交替进行链式推理与 Python 工具调用，求解数学竞赛题。模型为 Qwen3-8B / Qwen3-32B，基准为 AIME24 / AIME25 / HMMT25，以人工设计的静态 harness 作对照。

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

实验中观察到以下现象：
- **较难基准上的收益更大**：HMMT25 上 8B +20.1、32B +27.2；AIME24 的基线已较高，收益最小。在复杂多步推理中，运行框架的缺陷更容易导致失败。
- **更大模型在难题上受益更多**：32B 在 HMMT25 上的增益为 +27.2，高于 AIME24 上的 +10.6。较强模型有更多已有能力可通过改进 harness 发挥出来。
- **8B 的后续增益较小**：AIME24 上 R2（84.7）相较 R1（84.0）几乎没有提升。模型在该基准上的推理能力接近上限，剩余错误多来自模型内部，难以归因到 harness。

### 5.3 Harness Debt 反向证据

模型在补偿其弱点的运行框架下训练，可能产生依赖。实验中，每轮**测试时的绝对精度都在上升**（8B AIME25 56.9→66.7→78.3）。这些结果表明，模型学到了可迁移的推理技能，未形成对 harness 的依赖。

### 5.4 200+ 小时无人干预案例（Figure 7，Qwen3-8B × AIME24，22 个 harness 版本）

- **初始配置**：32 秒内因 vllm KV cache 错误崩溃。
- **Phase 1（init–v7）工程修复**：将 ThreadPool 换成 ProcessPool，用 SIGKILL 清理，并开启 thinking。v3 首次完成 90 题，得分 **59.6%**（3.78 h）。
- **Phase 2（v12–v15）效率优化**：全局批推理实现 **8.7× 加速**，v9 达到 61.5% / 1.11 h。
- **Phase 3 发现并验证 ensemble 策略**：v15 + v19 投票达到 **63.3% / 2.29 h**，精度最高，耗时在 3.33 h 的预算内。
- **v20–v22 回归**：新增的领域专用 prompt 与 Qwen3 内部推理冲突，导致回归。系统**自动检测到回归并回滚**。

崩溃率为 0%，过程覆盖三个优化阶段，全部 22 版均由 agent 生成。

## 6. 局限

1. **"首个共进化框架"的自称不成立**：结论称 Co-Harness 是"first framework to co-evolve both"，但 Continual Harness（arXiv 2605.09998，2026-05-11）早两个月已在具身域完成模型-harness 共学习闭环，由 Refiner 改 harness，PRM/教师重标注/soft SFT 改权重。CH 先在具身域实现，Co-Harness 首次用于通用 LLM agent 后训练。
2. **实验范围小于摘要所述范围**：摘要讨论"automated AI research 的后训练"，实验则全部采用工具集成数学推理。数学答案可验证，奖励信号明确，harness 归因也相对容易。能否迁移到 verifier 较弱的研究任务，尚未得到证明。
3. **归因能力受限**：作者说明，失败模式需要反事实控制流推理时，归因精度会下降。**结构性 harness 重设计仍由人负责**；HarnessCritic 只生成局部 diff，未搜索架构。
4. **依赖强 critic 与足够的初始失败轨迹**：系统需要能力足够的 critic LLM、最低数量的失败轨迹，以及多轮 SFT 所需的算力。这些要求更适合资源充足的大型团队，小团队较难承担相应的后训练成本。
5. **仍用固定基准评估**：验证集分数是接受 diff 的唯一判据，评估器共进化的问题（报告 03-06）仍未处理。
6. **只运行两轮**：R2 在 8B AIME24 上已趋于饱和。没有数据说明更多轮是否继续提高表现，或产生另一种 Harness Debt，即 harness 越来越适配特定模型版本。

## 7. 意义与位置

**对报告 10 分层分工的实现**：本文首次在通用 agent 上完整结合文本层快环（HarnessCritic diff，小时级）与权重层慢环（每轮 SFT）。它与 CH 的触发方式不同：CH 在 episode 内保留状态并在线提炼经验，Co-Harness 则按离线批次交替优化。

**对报告 11 能力地板的补充数据**：本文观察到更强模型在难题上受益更多，CH 则发现弱模型使用更强的运行框架后表现反而下降。这些结果对应的关系是：harness 收益随基座能力单调上升，低于最低能力要求时收益为负，接近能力上限时趋于饱和（8B AIME24 案例）。

**对报告 13 Meta-Harness 的分工**：Meta-Harness 让外层 coding agent 读取全部历史轨迹，自由改写 harness 代码，proposer 保持冻结。Co-Harness 用归因分类法将改动限制为局部 diff，并将收益蒸馏进权重。前者的搜索空间更大，后者的改动更易控制，且**只有后者将能力保留在模型中，使其可脱离 harness 使用**。Meta-Harness Discussion 提出进一步共进化 harness 与权重，Co-Harness 首次在通用域实现了这一设想。

**对报告 14 Self-Harness**：两者的接受条件结构相同（δ_in > 0 且 δ_out ≥ 0 vs Δ_in ≥ 0 且 Δ_ho ≥ 0 且 max > 0）。Self-Harness 不训练模型，Co-Harness 还会训练模型。Self-Harness 将 harness 作为最终优化产物，Co-Harness 将 harness 用于后续模型训练。

**对报告 02 Anthropic 叙事的微观印证**：系统在 200+ 小时内无人干预，从崩溃配置中恢复，并自行发现 ensemble 策略。这个案例展示了单次实验中"AI 改进 AI 训练基础设施"的可复现过程。按 Bostrom crossover（报告 00）的定义，可量化系统自身的贡献：22 版全部由 agent 生成。

**对报告 08 MOSS**：版本化注册表与回归回滚（v20–v22 案例）独立实现了与 MOSS 相似的检查机制。本文在文本/配置层使用了与生产系统相似的修改检查与撤销机制。

**对报告 18 Prime Agent**：Prime Agent 指出模型未接受操作 harness 的训练，Co-Harness 则训练模型掌握 harness 的行为。前者提出训练上的缺口，后者提供训练方法，对应 CH 关于"模型-harness 共学习将成主导路线"的预测。
