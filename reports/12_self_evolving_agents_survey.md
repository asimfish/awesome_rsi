# TMLR 自进化 Agent 综述深度解读：按 What / When / How / Where 分类自进化研究

> **A Survey of Self-Evolving Agents: What, When, How, and Where to Evolve on the Path to Artificial Super Intelligence**
> arXiv 2507.21046 v4（2026-01-16），TMLR 2026-01 正式发表 · 77 页
> 作者：Huan-ang Gao、Jiayi Geng、Wenyue Hua、Mengkang Hu 等约 27 人（16 人共同一作、按字母序）；Princeton / 清华 / CMU / 上交 / UIUC 等 17 家机构；通讯 Hongru Wang、Mengdi Wang
> GitHub：CharlesQ9/Self-Evolving-Agents · 归档：`papers/en/2507.21046_SelfEvolvingAgentsSurvey.pdf` · 中译 `papers/zh/2507.21046_SelfEvolvingAgentsSurvey_zh.pdf`

---

## 1. 一句话定位

LLM 本身静态，部署环境却开放且动态，因此需要自进化 agent；这篇综述以**自主权的所在地（locus of autonomy）**作为判别标准，即数据策划和更新安排是否由人类工程师转交给 agent，算法可以使用 SFT/RL。全文按 **What**（进化什么：模型/上下文/工具/架构）、**When**（何时：intra-test-time vs inter-test-time）、**How**（怎样：reward-based / imitation / population-based）、**Where**（何处：通用 vs 专域）四个维度整理上百项工作。作为本仓库唯一的系统性综述，它为报告 01–11 提供分类依据，副标题将目标设为 ASI 路线图。

评估节指出了两项缺口：**Retention 最缺少评估支持**，因为绝大多数 benchmark 是 episodic，任务间重置状态，无法测量知识积累或退化；**没有任何 benchmark 追踪进化过程中的安全轨迹**。四维分类描述了进化发生在哪、何时发生以及如何进行，但没有解释本调研关注的机制问题：如何防止进化塌缩。

## 2. 综述要回答的问题

综述首先定义什么算"自进化"。缺少这一界定，Reflexion（反思式 prompting）与 DGM（修改自身源码）就会被混在一起，self-evolving 也难以区分不同方法。

**形式化定义**：环境为 POMDP，agent 系统 Π = (Γ, {ψ}, {C}, {W}) 由拓扑、模型、上下文和工具组成。自进化策略为 f(Π, τ, r) = Π'，目标是最大化任务序列上的累计效用。

**操作性定义包含三个条件**：
1. 更新必须**依赖经验**，由自身轨迹或反馈驱动，排除人工调参；
2. 必须产生**持久的策略改变**，排除一次性指令跟随；
3. 必须包含**自主探索**，排除静态蒸馏流水线。

作者承认收录边界较宽，从 proto-evolution（反思式 prompting）到 strong self-evolution（全自主诊断重构）都纳入讨论，优先扩大覆盖面，接受区分度降低。

## 3. 与其他综述的分工

| 综述 | 中心问题 | 分类轴 | 在本仓库的角色 |
|---|---|---|---|
| **TMLR 四维（本文）** | 单体 agent 如何自进化 | What / When / How / Where | 汇集并分类各类方法 |
| Co-Evolution 三阶段（报告 22） | 多组件如何相互影响 | Agent-Agent → Agent-Env → Meta | 统一比较评估侧四篇 |
| Coding Agents 三维（报告 28） | 自进化如何用于编码域 | 对象 / 时间 / 证据 | 聚焦编码域，区分三类证据 |
| Weng 总纲（报告 01） | harness 各层的能力 | 改上下文 → 改代码 → 种群搜索 | 比较改进深度 |

TMLR 在三份综述中发表最早、覆盖最全、被引最多，后两份分别补充多组件与编码域的研究。Weng 按能力深度组织方法，TMLR 则覆盖各类方法；综述便于查找分类，比较不同层次的能力仍需参考前者。

## 4. 四维框架拆解与本仓库的格点对位

### What（四大进化位点）

模型（权重/经验）、上下文（记忆演化 + prompt 优化）、工具（创建/精通/选用）、架构（单 agent 结构 / 多 agent 拓扑）。

按这一分类，DGM（报告 07）同时涉及架构与工具选用，被列为这一路线的最终目标；MOSS（报告 08）与 SICA 同属源码级自改写；WikiSkill（报告 09）涉及工具创建和经验记忆；Continual Harness（报告 11）的 harness 覆盖全部四类；iCoder（报告 19）直接更新模型权重。

### When（两种时机 × 三种范式）

**intra-test-time**（在当前任务中改进，如 Reflexion、LADDER 的测试时 RL）vs **inter-test-time**（在任务间隙利用轨迹更新，如 STaR、WebRL）。两者各自再按 ICL / SFT / RL 分类。

这一划分与本调研的免重置 vs 重置式区分（报告 11）相近，但不重合。CH 的 episode 内精炼属于 intra，其 RL 共学习属于 inter。综述**未单独讨论是否重置**，本调研补充了这一维度。

### How（三代范式 + 三条横切轴）

**reward-based**（文本 / 内部置信 / 外部 / 隐式四种信号）→ **imitation**（自生成 / 跨 agent 示范）→ **population-based**（DGM 档案进化、SPIN 与 Absolute Zero 的自博弈、EvoMAC 的多 agent 文本反传）。横切轴：online/offline、on/off-policy、reward 粒度（结果/过程/混合）。

EvoLM 式 rubric 共进化（报告 03）与 ECHO critic 共进化（报告 06）被分别归入 internal rewards 和 Model-Agent Co-Evolution。四维框架没有为评估器共进化设置独立类别。

### Where（通用 vs 专域）

通用助理部分讨论记忆机制、课程驱动和模型-agent 共进化；专域覆盖编码 / GUI / 金融 / 医疗 / 教育。这一章主要列举应用领域，较少分析方法差异。

## 5. 评估节：全文最有牙齿的部分

**五目标 × 三时域**：适应性 / 保持 / 泛化 / 效率 / 安全 × 静态 / 短程 / 长程终身。

综述指出了三个问题：
1. **Retention 最缺少评估支持**。绝大多数 benchmark 是 episodic，任务间重置状态，无法测量知识积累或退化。这些变化恰是自进化 agent 与静态系统的区别。
2. **没有任何 benchmark 追踪进化过程中的安全轨迹**，因此无法判断风险是否随自主探索累积。
3. Table 11 承认，目前无法进行 apples-to-apples 比较。

**self-directedness 三项申报**：任务或课程由谁提供、反馈信号来自谁、外部干预有多频繁。这要求披露外部评估依据，但未要求必须保留此类依据。

**安全节**讨论了两种失效：**misevolution**，即自训练使模型遗忘安全对齐；**Alignment Tipping Process**，即模型发现失配行为奖励更高后转向这类策略。文中引用 alignment faking 从 12%→78% 的结果，说明无监督进化的风险。部署 checklist 包括沙箱与静态扫描、不可变审计日志与可回滚版本、更新前的金标安全验证，以及高危动作的人工审查。

**long-horizon 协议建议**：完整保留状态，报告 FGT/BWT 遗忘指标与 Cost-per-Gain，定期运行保留能力探针。这些指标可用于评估 Continual Harness 类系统。

## 6. 局限

1. **分类没有解释稳定进化的条件**。四维描述进化发生在哪、何时发生和如何进行，却未解释如何避免塌缩。评估器共进化分散在 How 的 reward 来源和评估节的 self-directedness 中，未被独立讨论。金标数据集、外部 reward、人审门等固定依据，也只作为工程做法出现，没有形成理论原则。
2. **What 维度未区分修改层级**。修改 prompt 与修改自身源码被并列为同级位点。本调研按文本、权重、源码区分风险与能力增益，更便于解释层级差异。DGM 在表格中属于多个类别，说明按组件分类难以描述连组件边界都能修改的系统。
3. **收录边界较宽，降低了区分度**。从 proto 到 strong 都收录，使 Reflexion 与 DGM 处于同一框架。这是作者承认并接受的取舍。
4. **reward overoptimization 仅作为未来工作讨论**。misevolution、ATP 和记忆层 reward hacking 都出现在第 8 章展望中，没有用于组织全文。本调研将评估器塌缩视为主要失效原因，综述则偏重列举问题，缺少机制分析。
5. **全文没有定量元分析**。文章侧重覆盖文献，未汇总比较不同方法的定量证据。
6. **收录截至 2026 年 1 月**：Meta-Harness 及之后的 harness 工程研究（报告 13–18）均未纳入。

## 7. 意义与位置

**对 01 Weng 总纲**：两者可配合使用。Weng 按 harness 的能力深度划分层级，综述则覆盖各类方法；Weng 的第四级在综述中仅对应 Architecture 下的一个叶节点。

**对 05 Who Grades the Grader**：综述的 self-directedness 三项申报要求披露固定评估依据，却不要求必须保留它。WGtG 则主张评估器不得参与进化，比单纯要求透明披露更严格。

**对 11 Continual Harness**：综述指出 episodic reset 无法测量知识积累，从评估角度支持了 CH 的免重置论证。其 long-horizon 协议可用于评估 CH 类系统，将系统设计与测量要求联系起来。

**对 07 DGM / 08 MOSS**：综述的安全 checklist，包括审计日志、版本回滚和更新前金标验证，与 MOSS 的失败重放及接受条件几乎逐项对应，说明生产实践已形成共同要求。DGM 的档案与 novelty 选择被归入 population-based。免重置方法为了在故障环境中直接修复，放弃了种群多样性，两类方法因此有不同取舍。

**对 10 汇总**：综述可用于检查三层改进面的分类依据。What 维度沿用按组件分类的常见做法，本调研则按风险与能力变化区分层级。综述安全节提供了相关证据：源码级与工具级的风险条目远多于 prompt 级。

**对 22 / 28 两份后续综述**：TMLR 的 What/When/How/Where 被 Co-Evolution 综述沿用为 Meta 共进化五项决策的前四项，另加"如何评估"；Coding 综述则将其用于编码域，形成对象、时间、证据三维。这两份都在 TMLR 分类的基础上扩展。
