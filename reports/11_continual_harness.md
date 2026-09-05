# Continual Harness 深度解读：不重置的 harness 自精炼，以及第一个模型-harness 共学习闭环

> **Continual Harness: Online Adaptation for Self-Improving Foundation Agents**
> arXiv 2605.09998v1（2026-05-11）· 普林斯顿大学 + ARISE Foundation + Google DeepMind
> 作者：Seth Karten*、Joel Zhang*、Tersoo Upaa Jr、Ruirong Feng、Wenzhe Li、Chengshuai Shi、Chi Jin、Kiran Vodrahalli（* 同等贡献）
> 项目页：sethkarten.ai/continual-harness · 归档：`papers/en/2605.09998_ContinualHarness.pdf` · 中译 `papers/zh/2605.09998_ContinualHarness_zh.pdf`
> 中文解读：微信公众号「X0后的回忆」· 一作续作：Prime Agent（arXiv 2608.23552，报告 18）

---

## 1. 一句话定位

Claude Code、OpenHands 这类编码 harness 已是标配，但具身 agent 没有对应物——PokeAgent 挑战赛实测：没有领域脚手架，前沿视觉语言模型在 RPG 里几乎走不动。本文分三步回答：先用几千小时人在环的 **Gemini Plays Pokémon（GPP）** 证明 harness 迭代能解决这个问题（首个通关多款宝可梦 RPG 的 AI）；再用 **Continual Harness** 把人从环里完全拿掉——agent 在**单场不重置的连续 episode** 内交替"行动"与"精炼自己的系统提示 / 子代理 / 技能库 / 记忆"；最后把同一条轨迹同时喂给 harness 精炼器和权重训练器，完成第一个**模型-harness 共学习**闭环。

关键数字：Gemini 3.1 Pro 上从零起步的 Continual Harness 达到 **100% 里程碑 / 中位成本 130 美元**，极简基线 98% / 215 美元——更好且省约 40%，严格 Pareto 占优；但 Flash-Lite 上**每个 CH 变体都比极简基线更差**（3-13% vs 20%）——给弱模型更强的脚手架只会让它更迷茫，作者称之为**能力地板**。

## 2. 要解决的问题：具身 agent 没有 harness，且现有 harness 优化必须重置

1. **脚手架缺位**。编码 harness 让模型能导航代码库、运行命令、跨长交互保持状态；具身 agent 的长时程、部分可观测决策没有等价物。PokeAgent 挑战赛的结论是：无脚手架的前沿 VLM 在 RPG 里几乎零进展。
2. **人在环不可扩展**。GPP 靠人盯直播改 harness 打通了 Blue（2025-05）、Yellow Legacy 困难模式（2025-08）、Crystal 终局零败绩（2025-11），但那是几千小时的人力。
3. **现有自动化方法是重置式的**。GEPA 一类提示优化（报告 01 提及）必须**整局重跑**才能评估新提示，每次更新后从初始状态重来；这在构造上永远碰不到只在 episode 深处出现的失败模式——终局战斗、多步谜题、长对话链。而且免重置才是长时运行编码 agent、具身 agent、运维任务的现实主导场景：环境重置要么昂贵要么不可得。
4. **模型与 harness 分开训**。已有后训练把 harness 当固定物，harness 优化又把模型当冻结物；两者互相塑造轨迹分布这件事没人闭环。

## 3. 为什么此前做不通：重置式方法的结构性盲区

论文把"harness"按 Karten 等（PokeAgent）的分解定义为四个组件：**系统提示 p**（每步推理的指令与策略指导）、**子代理 G**（可被编排器调用的专用模块：战斗策略、解谜、自反思）、**技能 K**（可复用例程，既包括推理中引用的文本级启发式，也包括可执行程序如寻路器、工具封装；`press_buttons`、`get_game_state` 这类预置原语也是技能）、**记忆 M**（跨轨迹积累事实、策略、观察的持久存储）。此外 harness 暴露一组固定的**元工具**（`define_agent`、`run_code`、`process_memory` 等），agent 通过它们原地编辑 p、G、K、M。

三种 harness 条件：**H_min** 只有环境接口 + 通用提示，无子代理/记忆/技能；**H_expert** 是 PokeAgent 与 GPP 手工打造的完整 harness（内置子代理、A* 寻路、属性表、伤害计算器、精选目标）；**meta-harness** 给模型元工具让它自己在游戏中构造子代理、技能、记忆——这是 GPP 后期的运行点，模型未经要求就自建了寻路器、战斗策略师和可复用脚本。

重置式方法做不通的根因在第 2 节第 3 条：它们的效用信号来自**完整评测**，每次更新都回到起点。GPP 几千小时里最有价值的 harness 改动（Elite Four 阶段的战斗策略重写、Goldenrod 地下开关谜题的真值表）全发生在 episode 深处——重置式方法在结构上到不了那里。

## 4. 方法机制

### 4.1 两环架构：行动是内环，精炼是外环

Continual Harness 对 harness 状态 H 做**在线上下文学习**。写 s_t = (o_t, m_t) 为第 t 步观察（渲染帧 + 描述可见格子与可走位置的 ASCII 文本地图，地图不含攻略、目标列表或寻路）。**内环**是标准 agent 步：模型 M 被当前 harness H_t 包裹，从 s_t 与迄今轨迹产生动作 a_t。**外环**是 harness 精炼：预热 W 步后每 F 步，Refiner 读最近的轨迹窗口 τ_{t−F:t} 找失败特征，发出逐组件编辑 Δ = (Δp, ΔG, ΔK, ΔM)。**agent 不重置**：更新后的 H_{t+1} = H_t ⊕ Δ 在下一步直接进入 agent 上下文——p 被 Δp 替换，G、K、M 接受 CRUD 操作。Agent 与 Refiner **共用同一个模型 M**（Gemini 3.1 Pro / Flash / Flash-Lite 三档消融）；两者通过同一套元工具 API 发出编辑，区别只在何时被调用、看哪段轨迹。GPP 里 Refiner 角色由看直播的人担任，CH 把它自动化。

### 4.2 精炼环的四道处理

Refiner 在窗口上识别四类失败特征：导航循环、工具调用失败、目标停滞、错过的探索机会。然后跑四道，一道一个组件：(i) 依识别出的失败与轨迹窗口重写提示 p；(ii) 为反复出现的多步模式创建子代理条目、编辑现有条目修复失败、删除未被有效调用的条目；(iii) 从成功序列中固化技能、修复抛出异常的可执行代码；(iv) 添加记忆条目填补缺口、更新过时条目、降低已经走过的区域的重要性。

两条性质是全文的杠杆：**精炼信息在 episode 内单调累积**——早期观察到的失败特征对后续所有精炼都可用，精炼质量随 episode 长度复利，而重置式方法每次更新都重启这个累积；**可以针对只在 episode 深处出现的失败模式**——终局战斗、多步谜题、对话链，重置式方法在构造上到不了。

### 4.3 模型-harness 共学习环

把 CH 实例化为开源模型的训练循环（Figure 2b）：预热阶段后（先在前沿模型的 CH 轨迹上 SFT，再做一段按步过程奖励的离线 GRPO——两段预热**单独都不产生有意义的里程碑推进**），每个在线迭代让策略 π_θk 在一个**实时精炼中的 harness H_t** 里跑 K = 256 步（DAgger 式 rollout）。一个成对过程奖励模型 R(s_t, a_t, τ) ∈ [0, 1] 在最近转移的滑动窗口上给每个转移打分；**低奖励窗口由前沿教师（Gemini-3.1-pro）重标注**；在重标注分片上做 soft SFT（LoRA，3 epoch，学习率 5×10⁻⁶）产生 θ_{k+1}。**训练环免重置**：迭代 k 结束时保存的模拟器状态作为 k+1 的起点，模型的游戏内位置跨训练累积而非重启。

轨迹分布 D_θ 通过 harness 依赖 θ：模型动作诱导 τ，Refiner 读 τ 更新 H_t，H_t 又塑造下一步观察分布。**θ 跨迭代更新（SFT），H_t 迭代内更新（Refiner）**——这就是"共学习"的精确含义。注意两个不动点：PRM 是冻结的，教师是前沿模型——锚仍在进化之外。

### 4.4 三档 CH 变体

**from scratch**：从 H_min 起步在游戏中精炼；**bootstrap frozen**：加载一次成功的 from-scratch 运行的 harness，关闭精炼；**bootstrap updating**：同样的 bootstrap，精炼继续。三者对比回答"harness 是否是可迁移资产"以及"继承之后继续精炼还有没有价值"。

## 5. 实验结果全景

**设置**：Pokémon Red 与 Emerald（同类型 RPG，地图/机制/难度不同），PokeAgent 挑战赛的标准化里程碑评估，主指标是**到达里程碑的累计按键次数**。模型：Gemini 3 三档（Pro / Flash / Flash-Lite）覆盖全部 harness 条件；开源迁移用 Gemma-4（E2B、E4B、26B MoE、31B dense）。每个实验至少三个 seed，报 seed 中位数并淡色画出各 seed。

**GPP 的定性证据（§4.2）**：Blue 时代靠手写专家（Pathfinder Agent、Boulder Puzzle Strategist）；Yellow Legacy 起换成通用技能（`define_agent`、`run_code`、记事本编辑）让模型自建 harness。未经提示的涌现行为：把 `autopress_buttons` 的沙箱漏洞封装成通用的 `press_sequence` 原语；给多阶段战斗策略命名（Crystal 终局对 Red 的"Operation Zombie Phoenix"）；在记事本里为 Goldenrod 地下开关谜题写出显式真值表。Figure 3 的定量图：Yellow Legacy 全程 20 万回合里 CRUD 操作**持续发生而非收敛到固定脚手架**，且集中在一小撮导航与战斗组件（pathfinder、gem_pathfinder_v2、battle_strategist_agent、find_path、boulder_puzzle_solver）；Figure 4 跟踪 battle_strategist_agent 提示在 Elite Four 阶段 14 个结构检查点的节点数/决策门/深度/扇出——在生长与简化之间循环，并经历一次结构性重写（逐决策逻辑被吸收进一个分派到具名子检查的 master_battle_agent）。

**CH 缩小到手工 harness 的差距（§4.3，Figure 5）**：Red 上 11 个里程碑到 Thunder Badge，Emerald 上 9 个到 Knuckle Badge。两款游戏上 CH 相对 H_min 大幅降低每个监测里程碑的按键成本，**回收了 H_min 到 H_expert 效率差距的大半**——而它没有游戏反编译、没有里程碑时间表、没有任何构成 H_expert 的手写子代理。残余差距集中在对话密集的道馆内部与多回合战斗策略——CH 尚不能可靠合成的组件。Red 上 bootstrap-updating 在**每个**里程碑都比 from-scratch 高效：先前运行精炼出的 harness 加速下一次运行，即便游戏状态重置——精炼信号在 episode 内复利，也可跨运行迁移。

**能力地板（§4.4，Figure 6，Emerald 31 里程碑 × 24 小时 × 成本）**

| 模型（输入/输出价 USD/M） | H_min | CH from scratch | CH bootstrap | 判断 |
|---|---|---|---|---|
| Pro（1.25 / 10.00） | 98% / $215 | **100% / $130** | 96-100% / $110-140 | 严格 Pareto 占优，省约 40% |
| Flash（0.30 / 2.50） | 77% / $30 | 高方差 | updating 80% / $42 | 边际收益、方差极大 |
| Flash-Lite（0.10 / 0.40） | **20% / $11** | 3-13% | 3-13% | **每个 CH 变体都更差**，成本相当或更高 |

作者的结论只有一句："harness 收益需要一个能正确利用 harness 组件的模型"。这是全谱系第一次把"脚手架不是免费午餐"量化到具体模型档位。

**开源模型共学习（§4.5，Figure 7，Pokémon Red）**：五条推进的运行中，Gemma-4 的游戏内位置在每次训练迭代后都前进——从游戏开头起步的和从中期检查点起步的曲线呈同样的阶梯形状，说明训练信号不专属于早期游戏分布。未训练的 Gemma-4 基线在起始里程碑之外零推进。**负对照**：跨家族的 Qwen3.5（27B、35B）不做监督预热，能产出可解析的工具调用，却在实时 rollout 里走不出起始区域——排除了"是 rollout 协议本身在推动进展"这一假象。共学习环在实验范围内**未饱和**：报告了持续的里程碑进展，但没有建立收敛点。

**技能向 oracle 可测地自改进（§4.6，Figure 8）**：用 Dijkstra oracle 的路径成本作尺子，评估进化出的导航技能在 warp-to-warp 避障导航（贪心开放场跳跃会失败）上的表现——这是**独立于终任务效率的技能自改进直接测量**。H_min 从不调用导航技能；每个 CH 条件 24 小时内累积数百次调用。from-scratch 运行的路径成本超额从起初的**接近一半**降到**个位数**并保持——修复全在环内、免重置：早先调用的失败被 Refiner 诊断、受影响的技能在同一 episode 的后续调用前被修好。bootstrap-updating 继承精炼过的技能集并全程持平或优于 bootstrap-frozen——继承之上继续精炼仍有价值；bootstrap-frozen 的平坦曲线则给出"只继承不精炼"的上界。

## 6. 局限（作者自认 + 延伸批判）

作者自认（§6）：能力地板之下精炼环无法自举；共学习实验把前沿教师耦合到开源学生，框架理论上支持同一模型兼任两角，但评估过的开源模型（Gemma-4 至 31B）还不够强；共学习环未饱和也未建立收敛点；只做了免重置训练，**免重置 vs 重置式在同一任务上的正面对比仍开放**；残余差距在对话密集区与多回合战斗。

延伸几条：

1. **"免重置"的代价没有被正面计价**。放弃重置意味着放弃种群多样性与档案回溯（DGM 报告 07 的核心资产）：一个坏的精炼在 CH 里没有"回到上一个好版本"的机制，只能靠后续精炼再修——论文的 Figure 3 显示更新持续发生，但没有报告有多少更新是在撤销前一次更新。这是免重置范式最需要被测量的一件事。
2. **能力地板的机制未被解释**。Flash-Lite 上更强脚手架反而更差——是 Refiner 太弱写出了坏 harness，还是 Agent 太弱用不好好 harness？Agent 与 Refiner 共用模型让两者无法区分；Self-Harness（报告 14）后来用回归门（改坏即拒）让 35B 弱模型大幅提升，暗示地板至少部分来自"没有拒绝坏改动的门"，而非模型本身。
3. **锚全在进化之外但没被讨论**。共学习环的两个不动点——冻结 PRM 与前沿教师——是系统不塌缩的原因，论文把它们当作实现细节而非设计原则；按 Who Grades the Grader（报告 05）的框架，它们正是承重部件，且 PRM 的构成（Appendix D 的分量权重）应当被当作一等实验对象。
4. **评估域单一**。全部结果在两款宝可梦 RPG 上，里程碑评估来自同一作者组的挑战赛；"free-reset 是长时运行编码 agent 与运维任务的现实主导场景"这一动机没有在这些域上验证——Prime Agent（报告 18，同一一作）后来把 CH 作为子系统搬到 nanoGPT speedrun 与 Factorio，算是部分回应。

## 7. 意义与位置

2026-05 的 Continual Harness 在谱系里开了一条前人没有的轴：**重置式 vs 免重置**。DGM、RQGM、GEPA、Meta-Harness 的效用信号都来自完整评测，CH 证明 harness 精炼可以全部发生在故障现场——代价是失去种群多样性与档案回溯，换来对"只在 episode 深处出现的失败模式"的可达性。这条轴后来被 Prime Agent（报告 18）落成 daemon/恢复/分叉的工程事实，也被自进化综述（报告 12）从评估侧镜像为"Retention 是最缺服务的维度：episodic 基准从构造上测不到知识积累"。

它同时是**第一个模型-harness 共学习闭环**：同一份轨迹双消费——Refiner 改 harness（episode 内），PRM 打分 + 教师重标注 + soft SFT 改权重（每 256 步）。Co-Harness（报告 21）两个月后把同一双环推广到通用 LLM agent 并自称"首个"，本仓库按时间线把首发权记给 CH、把通用化记给 Co-Harness。报告 10 §2 的"分层分工"共识——文本层快环、权重层慢环——第一个完整实现就是这里。

三条与全谱系的硬连线：① **bootstrap 继承实验证明 harness 是可迁移资产**（与 WikiSkill 报告 09、Meta-Harness 报告 13 的跨模型迁移互证），但能力地板给这个资产市场加了消费门槛——不是所有模型都消费得起；② **共学习深处仍钉着两个不动点**（冻结 PRM + 前沿教师）——锚必须在进化之外，与报告 05 的结论同构；③ **Dijkstra 尺子**是全谱系少见的"技能层独立真值"——大多数工作只报终任务分，CH 单独测了技能本身向 oracle 收敛的曲线，这是评估器战争（报告 03-06、24-25）里最容易被忽略的一种锚：**为中间产物找一个可计算的 oracle**。

方法论上最值得借鉴的两点：**把 harness 拆成四个可 CRUD 的组件并给出统一的元工具 API**（Refiner 与 Agent 用同一套工具、只在调用时机与轨迹上下文上不同——这让"人在环"到"程序在环"的替换成为一次配置变更而非架构重写）；**用同一条轨迹同时驱动快环与慢环**（harness 与权重各取所需，避免了为两个环分别采样的算力浪费）。

