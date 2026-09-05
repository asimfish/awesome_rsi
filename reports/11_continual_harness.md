# Continual Harness 深度解读：在连续任务中精炼 harness，并联合更新模型与 harness

> **Continual Harness: Online Adaptation for Self-Improving Foundation Agents**
> arXiv 2605.09998v1（2026-05-11）· 普林斯顿大学 + ARISE Foundation + Google DeepMind
> 作者：Seth Karten*、Joel Zhang*、Tersoo Upaa Jr、Ruirong Feng、Wenzhe Li、Chengshuai Shi、Chi Jin、Kiran Vodrahalli（* 同等贡献）
> 项目页：sethkarten.ai/continual-harness · 归档：`papers/en/2605.09998_ContinualHarness.pdf` · 中译 `papers/zh/2605.09998_ContinualHarness_zh.pdf`
> 中文解读：微信公众号「X0后的回忆」· 一作续作：Prime Agent（arXiv 2608.23552，报告 18）

---

## 1. 一句话定位

Claude Code、OpenHands 这类编码 harness 已被广泛使用，具身 agent 却没有对应系统，PokeAgent 挑战赛也显示：缺少领域脚手架时，前沿视觉语言模型在 RPG 中几乎没有进展。本文先通过几千小时人工参与的 **Gemini Plays Pokémon（GPP）** 迭代 harness，首次让 AI 通关多款宝可梦 RPG。随后，**Continual Harness** 实现自动精炼，让 agent 在**单场不重置的连续 episode** 内交替执行任务与精炼自己的系统提示、子代理、技能库和记忆。最后，同一条轨迹同时用于 harness 精炼器与权重训练器，形成第一个**模型-harness 共学习**循环。

Gemini 3.1 Pro 上，从零起步的 Continual Harness 达到 **100% 里程碑 / 中位成本 130 美元**，极简基线为 98% / 215 美元。完成度更高，成本降低约 40%，严格 Pareto 占优。Flash-Lite 上则**每个 CH 变体都低于极简基线**（3-13% vs 20%），说明弱模型可能无法有效使用更复杂的脚手架。作者将这一最低能力要求称为**能力地板**。

## 2. 要解决的问题：具身 agent 没有 harness，且现有 harness 优化必须重置

1. **缺少具身脚手架**。编码 harness 帮助模型导航代码库、运行命令、在长交互中保持状态；具身 agent 的长时程、部分可观测决策缺少对应支持。PokeAgent 挑战赛中，没有脚手架的前沿 VLM 在 RPG 里几乎没有进展。
2. **人工参与难以扩展**。GPP 由人观看直播并修改 harness，通关了 Blue（2025-05）、Yellow Legacy 困难模式（2025-08），并在 Crystal 终局取得零败绩（2025-11），但耗费了几千小时人力。
3. **现有自动化方法依赖重置**。GEPA 一类提示优化（报告 01 提及）必须**整局重跑**才能评估新提示，每次更新后都从初始状态开始。它无法处理只在 episode 后期出现的失败，如终局战斗、多步谜题和长对话链。长时运行的编码 agent、具身 agent 和运维任务也主要在免重置环境中运行，因为重置环境成本高，或根本无法重置。
4. **模型与 harness 分开训练**。已有后训练固定 harness，harness 优化又冻结模型。两者都会影响轨迹分布，却尚未在同一循环中共同更新。

## 3. 为什么此前做不通：重置式方法的结构性盲区

论文沿用 Karten 等（PokeAgent）的定义，将 harness 分为四个组件：**系统提示 p**，提供每步推理的指令与策略指导；**子代理 G**，由编排器调用，负责战斗策略、解谜、自反思等专门任务；**技能 K**，保存可复用例程，包括推理中引用的文本启发式，以及寻路器、工具封装等可执行程序，`press_buttons`、`get_game_state` 等预置原语也属于技能；**记忆 M**，跨轨迹保存事实、策略和观察。harness 还提供一组固定的**元工具**（`define_agent`、`run_code`、`process_memory` 等），agent 通过它们原地编辑 p、G、K、M。

实验比较三种 harness 条件。**H_min** 只有环境接口和通用提示，没有子代理、记忆或技能。**H_expert** 是 PokeAgent 与 GPP 手工构建的完整 harness，内置子代理、A* 寻路、属性表、伤害计算器和精选目标。**meta-harness** 向模型提供元工具，让它在游戏中自行构造子代理、技能和记忆。GPP 后期采用这一设置，模型在未被要求的情况下，自建了寻路器、战斗策略师和可复用脚本。

第 2 节第 3 条指出了重置式方法的限制：效用信号来自**完整评测**，每次更新都回到起点。GPP 几千小时中的重要 harness 改动，包括 Elite Four 阶段的战斗策略重写和 Goldenrod 地下开关谜题的真值表，都发生在 episode 后期，重置式方法无法覆盖。

## 4. 方法机制

### 4.1 两环架构：行动是内环，精炼是外环

Continual Harness 对 harness 状态 H 进行**在线上下文学习**。第 t 步观察写为 s_t = (o_t, m_t)，包含渲染帧与 ASCII 文本地图。地图描述可见格子和可走位置，不含攻略、目标列表或寻路。**内环**执行标准 agent 步骤：模型 M 在当前 harness H_t 下，根据 s_t 和已有轨迹生成动作 a_t。**外环**精炼 harness：预热 W 步后，每 F 步由 Refiner 读取最近的轨迹窗口 τ_{t−F:t}，识别失败特征，发出逐组件编辑 Δ = (Δp, ΔG, ΔK, ΔM)。

**agent 不重置**：更新后的 H_{t+1} = H_t ⊕ Δ 在下一步直接进入 agent 上下文。其中 p 由 Δp 替换，G、K、M 通过 CRUD 操作更新。Agent 与 Refiner **共用同一个模型 M**，实验比较 Gemini 3.1 Pro / Flash / Flash-Lite 三档。两者使用同一套元工具 API 编辑，只有调用时机和所读轨迹不同。GPP 中，Refiner 由观看直播的人担任，CH 将这项工作自动化。

### 4.2 精炼环的四道处理

Refiner 从窗口中识别导航循环、工具调用失败、目标停滞和错过的探索机会，再依次处理四个组件：(i) 根据失败特征和轨迹窗口重写提示 p；(ii) 为反复出现的多步模式创建子代理，修改现有条目以修复失败，删除未被有效调用的条目；(iii) 从成功序列提取技能，修复抛出异常的可执行代码；(iv) 补充缺失的记忆，更新过时条目，降低已走过区域的重要性。

这套方法有两项性质。**精炼信息在 episode 内单调累积**，早期观察到的失败可用于后续所有精炼，质量随 episode 延长而提高；重置式方法每次更新都重新开始积累。它还**能够处理只在 episode 后期出现的失败**，如终局战斗、多步谜题和对话链，这些是重置式方法无法覆盖的场景。

### 4.3 模型-harness 共学习环

CH 也被用于开源模型的训练循环（Figure 2b）。预热时，先在前沿模型的 CH 轨迹上做 SFT，再按步过程奖励做离线 GRPO；这两段预热**单独都未带来有意义的里程碑推进**。此后，每个在线迭代让策略 π_θk 在**实时精炼的 harness H_t** 中运行 K = 256 步，执行 DAgger 式 rollout。成对过程奖励模型 R(s_t, a_t, τ) ∈ [0, 1] 在最近转移的滑动窗口上逐个打分。**低奖励窗口由前沿教师（Gemini-3.1-pro）重标注**，再在这些分片上做 soft SFT（LoRA，3 epoch，学习率 5×10⁻⁶），得到 θ_{k+1}。**训练循环不重置**：迭代 k 结束时保存模拟器状态，作为 k+1 的起点，游戏内位置随训练持续推进。

轨迹分布 D_θ 通过 harness 依赖 θ：模型动作产生 τ，Refiner 读取 τ 并更新 H_t，H_t 再影响下一步的观察分布。这里的共学习指 **θ 跨迭代更新（SFT），H_t 在迭代内更新（Refiner）**。PRM 保持冻结，教师由前沿模型担任，两者都在进化循环之外提供固定依据。

### 4.4 三档 CH 变体

**from scratch** 从 H_min 起步，在游戏中精炼；**bootstrap frozen** 加载一次成功的 from-scratch 运行得到的 harness，关闭精炼；**bootstrap updating** 使用相同的 bootstrap，继续精炼。比较三者可以检验 harness 能否迁移，以及继承之后继续精炼是否仍有收益。

## 5. 实验结果全景

**设置**：实验使用 Pokémon Red 与 Emerald，两者同属 RPG，但地图、机制和难度不同。评估沿用 PokeAgent 挑战赛的标准化里程碑，主指标为**到达里程碑的累计按键次数**。Gemini 3 三档（Pro / Flash / Flash-Lite）覆盖全部 harness 条件；开源迁移使用 Gemma-4（E2B、E4B、26B MoE、31B dense）。每个实验至少三个 seed，报告 seed 中位数，并以淡色绘出各 seed。

**GPP 的定性证据（§4.2）**：Blue 阶段依赖手写专家模块（Pathfinder Agent、Boulder Puzzle Strategist）。从 Yellow Legacy 起，系统提供通用技能（`define_agent`、`run_code`、记事本编辑），让模型自建 harness。模型未经提示就把 `autopress_buttons` 的沙箱漏洞封装为通用的 `press_sequence` 原语，为多阶段战斗策略命名，如 Crystal 终局对 Red 的"Operation Zombie Phoenix"，还在记事本中为 Goldenrod 地下开关谜题写出显式真值表。

Figure 3 显示，在 Yellow Legacy 全程 20 万回合中，CRUD 操作持续发生，脚手架没有固定下来。修改主要集中在少数导航与战斗组件（pathfinder、gem_pathfinder_v2、battle_strategist_agent、find_path、boulder_puzzle_solver）。Figure 4 跟踪 battle_strategist_agent 提示在 Elite Four 阶段 14 个结构检查点的节点数、决策门、深度和扇出。结构反复扩展和简化，并经历了一次重写：逐决策逻辑被合并进 master_battle_agent，由它分派到具名子检查。

**CH 与手工 harness 的差距（§4.3，Figure 5）**：Red 评估到 Thunder Badge，共 11 个里程碑；Emerald 评估到 Knuckle Badge，共 9 个。两款游戏中，CH 相对 H_min 都大幅降低了每个监测里程碑的按键成本，缩小了 H_min 与 H_expert 之间一半以上的效率差距。它未使用游戏反编译、里程碑时间表，也未使用构成 H_expert 的手写子代理。剩余差距集中在对话密集的道馆内部和多回合战斗策略，这些组件尚不能由 CH 可靠生成。Red 中，bootstrap-updating 在**每个**里程碑上都比 from-scratch 高效，说明即使重置游戏状态，先前精炼的 harness 仍能加速下次运行。episode 内积累的精炼结果可以跨运行迁移。

**能力地板（§4.4，Figure 6，Emerald 31 里程碑 × 24 小时 × 成本）**

| 模型（输入/输出价 USD/M） | H_min | CH from scratch | CH bootstrap | 判断 |
|---|---|---|---|---|
| Pro（1.25 / 10.00） | 98% / $215 | **100% / $130** | 96-100% / $110-140 | 严格 Pareto 占优，省约 40% |
| Flash（0.30 / 2.50） | 77% / $30 | 高方差 | updating 80% / $42 | 收益有限，方差很大 |
| Flash-Lite（0.10 / 0.40） | **20% / $11** | 3-13% | 3-13% | **每个 CH 变体都更差**，成本相当或更高 |

作者据此认为，harness 要产生收益，模型必须能正确使用 harness 组件。这项研究首次按具体模型档位量化了脚手架对模型能力的要求。

**开源模型共学习（§4.5，Figure 7，Pokémon Red）**：五条有进展的运行中，Gemma-4 的游戏内位置在每次训练迭代后都继续推进。从游戏开头和中期检查点起步的曲线都呈阶梯状，说明训练信号也适用于早期之外的游戏分布。未训练的 Gemma-4 基线未越过起始里程碑。**负对照**中，跨家族的 Qwen3.5（27B、35B）未做监督预热，虽能生成可解析的工具调用，却在实时 rollout 中无法离开起始区域。这排除了仅由 rollout 协议推动进展的解释。共学习环在实验范围内**未饱和**，里程碑持续推进，但尚未确定收敛点。

**技能相对 oracle 的改进（§4.6，Figure 8）**：实验以 Dijkstra oracle 的路径成本为依据，评估导航技能在 warp-to-warp 避障任务上的表现，贪心的开放场跳跃在此会失败。这项测量独立于终任务效率，直接检查技能是否改进。H_min 从不调用导航技能，每个 CH 条件在 24 小时内则累积数百次调用。from-scratch 运行的路径成本超额从起初的**接近一半**降至**个位数**，并保持下来。修复均在不重置的循环内完成：Refiner 诊断早先调用的失败，在同一 episode 的后续调用前修好相关技能。bootstrap-updating 继承精炼过的技能集，全程持平或优于 bootstrap-frozen，表明继续精炼仍有收益。bootstrap-frozen 的平坦曲线则给出了仅继承、不精炼时的表现上界。

## 6. 局限（作者自认 + 延伸批判）

作者列出的局限（§6）包括：模型低于最低能力要求时，精炼环无法自举；共学习实验仍需要前沿教师指导开源学生，虽然框架允许同一模型兼任两角，但受测的开源模型（Gemma-4 至 31B）还不够强；共学习环尚未饱和，也未确定收敛点；实验只做了免重置训练，**免重置 vs 重置式在同一任务上的直接比较仍未完成**；与手工系统的差距仍集中在对话密集区和多回合战斗。

还有几处需要进一步检验：

1. **尚未量化免重置的代价**。取消重置后，系统失去了 DGM（报告 07）所保留的种群多样性与档案回溯。CH 没有恢复到先前有效版本的机制，错误精炼只能由后续精炼修复。Figure 3 显示更新持续发生，却未报告多少次更新是在撤销前一次修改。需要测量这一比例，才能评估免重置的代价。
2. **最低能力要求的成因尚不明确**。Flash-Lite 使用更复杂的脚手架后表现下降，可能是 Refiner 写出了无效 harness，也可能是 Agent 无法正确使用有效 harness。Agent 与 Refiner 共用模型，无法区分两种原因。Self-Harness（报告 14）后来通过回归检查拒绝有害改动，使 35B 弱模型大幅提升，说明接受机制至少可能解释部分能力限制。
3. **缺少对外部评估依据的讨论**。冻结 PRM 与前沿教师使共学习环避免塌缩，论文却仅将它们作为实现细节。按 Who Grades the Grader（报告 05）的框架，两者承担了维持评估可靠性的作用，应作为设计原则讨论。PRM 的构成，尤其 Appendix D 中的分量权重，也需要专门实验检验。
4. **评估域单一**。全部结果来自两款宝可梦 RPG，里程碑评估也由同一作者组的挑战赛提供。论文以"free-reset 是长时运行编码 agent 与运维任务的现实主导场景"为动机，却未在这些领域验证。同一一作后来的 Prime Agent（报告 18）将 CH 作为子系统用于 nanoGPT speedrun 和 Factorio，提供了部分补充。

## 7. 意义与位置

2026-05 的 Continual Harness 首次引入了**重置式 vs 免重置**这一研究维度。DGM、RQGM、GEPA、Meta-Harness 的效用信号来自完整评测，CH 则证明 harness 可以直接在发生故障的环境中精炼。它失去了种群多样性与档案回溯，但能处理只在 episode 后期出现的失败。Prime Agent（报告 18）后来以 daemon、恢复和分叉机制实现了这类持续运行。自进化综述（报告 12）从评估角度提出了相关问题：Retention 是最缺少评估支持的维度，episodic 基准无法测量持续的知识积累。

它也是**第一个模型-harness 共学习循环**。同一份轨迹用于两类更新：Refiner 在 episode 内修改 harness，PRM 打分后由教师重标注，再通过 soft SFT 每 256 步更新权重。Co-Harness（报告 21）两个月后将这两个循环推广到通用 LLM agent，并自称"首个"。本仓库按时间线将首次实现归于 CH，将通用化归于 Co-Harness。报告 10 §2 所说的文本层快速迭代、权重层低频更新，在这里首次完整实现。

与其他研究有三处关联：① **bootstrap 继承实验验证了 harness 可迁移**，与 WikiSkill（报告 09）、Meta-Harness（报告 13）的跨模型迁移结果相互支持，但使用者仍需达到最低模型能力要求；② 共学习仍保留**冻结 PRM 与前沿教师**，在进化循环之外提供评估依据，与报告 05 的结论一致；③ **Dijkstra 提供了技能层的独立真值**。多数工作只报告终任务分，CH 则单独测量技能向 oracle 收敛的曲线。评估器研究（报告 03-06、24-25）中较少使用这种做法，即为中间产物设置可计算的 oracle。

实现上有两项具体设计。harness 被拆成四个可 CRUD 的组件，通过统一的元工具 API 编辑。Refiner 与 Agent 使用同一套工具，只在调用时机和轨迹上下文上不同，因此可以通过配置变更，将人工精炼替换为程序精炼。同一条轨迹也同时用于 harness 和权重更新，减少了分别为两个循环采样的算力开销。
