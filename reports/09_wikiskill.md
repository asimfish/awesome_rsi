# WikiSkill 深度解读：技能可以回滚，知识必须复利——在 raw 与 skill 之间插入永不重置的 wiki 层

> **WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution**
> arXiv 2608.27454 v1（2026-08-27）· Google Research + Virginia Tech
> 灵感：Karpathy (2026) "LLM Wiki"——把经验编译为持久、复利的知识
> 归档：`papers/en/2608.27454_WikiSkill.pdf`

---

## 1. 一句话定位

EvoSkill、Trace2Skill、SkillOpt 把"学到了什么"散落在优化历史里，无法跨迭代系统复用——同一个错误根因每轮重做，被拒方案换个措辞又被提出。WikiSkill 把 agent 工作区分成三层：**不可变 raw 轨迹**、**永不回滚的复利 wiki 知识库**、**门控可回滚的 skill**；持续把经验固化进 wiki，让后续技能更新站在越来越扎实的知识上。五基准五模型全面第一，比各模型下最强竞争方法高 **3.3–12.0 分**；Qwen 家族增益随规模递增（4B +12.3 / 9B +17.5 / 27B +23.9）；**9B+技能（47.4%）> 27B 无技能（39.4%）**——技能发现与技能执行可以解耦、跨模型交易。消融：Proposer 有 wiki **+15.0**；Inference Agent 训练时访问 wiki 反而 **−2.8**——知识层必须与执行层隔离。

## 2. 要解决的问题

Agent skill 是把领域专业知识（流程、脚本、资源）打包成文件系统模块（SKILL.md + 资源目录）的轻量格式——不动模型参数就能积累专业能力，支持 progressive disclosure 省上下文。近期工作从经验自动进化 skill：跑训练任务、分析成败轨迹、改 skill。

共同缺陷：**没有把"学到的东西"维护成独立演化的知识表示**。

- EvoSkill：只留提案+评估结果的累积历史；
- Trace2Skill：轨迹教训直接并进 skill 更新；
- SkillOpt：被拒编辑反馈 + 按 epoch 元指导——洞见全部散落在优化工件里。

后果：同一错误根因分析每轮重做；被拒方案换个措辞又被提出；跨迭代无法系统复用已验证的模式与失败归因。

WikiSkill 的命题：**在原始经验与可执行技能之间，必须有一个持久、只增不减、结构化沉淀的中间层**——不是 prompt 缓存，而是可审计、可索引、可引用的知识库。

## 3. 为什么此前做不通：三条线各差一块

| 已有路线 | 有什么 | 缺什么 |
|---|---|---|
| 直接轨迹→skill（Trace2Skill） | 端到端、简单 | 知识随 skill 回滚而丢失；无跨轮复利 |
| 优化历史累积（EvoSkill） | 保留提案记录 | 非结构化；Proposer 无法按需检索模式 |
| epoch 元指导（SkillOpt） | 高层进化方向 | 仍散落在优化工件；无独立知识层 |
| MOSS 源码自改写 | 改 harness 代码、确定性生效 | 不可跨代码库迁移；碰不到流程性知识 |
| ECHO/RQGM critic 共进化 | 评估信号跟随 policy | critic 每轮进化但不沉淀结构化知识 |

关键缺口：**技能层需要严格门控（坏 skill 必须可回滚），但证据层不能回滚（失败实验记录是人类科研的基本纪律）**——此前方法把两层混在一个对象里，要么全回滚丢知识，要么全保留污染 skill。

## 4. 方法机制

### 4.1 三层工作区（可变性刻意不同）

| 层 | 目录 | 内容 | 可变性 |
|---|---|---|---|
| Raw | `raw/` | 完整执行轨迹 | **不可变**，一次写入 |
| Wiki | `wiki/` | 模式页、进化日志、技能影响追踪 | **复利，永不重置、永不回滚** |
| Skill | `skills/` | SKILL.md + PURPOSE.md（回链 wiki 模式） | **可逆**，验证门控 + 回滚 |

`skill-impact.md` 由外层 harness **程序化**写入：每次验证后追加提案元数据、diff、验证分、接受/拒绝——给 Proposer 客观干预审计，避免重复提出已失败修改。

### 4.2 四组件循环

1. **Inference Agent**：活跃技能全文注入 system prompt；跑训练集 rollout 写 raw。**训练时禁止访问 wiki**（关键设计）。
2. **Wiki Maintainer**：对采样成败轨迹根因分析，patch-based 创建/更新模式页；更新数量不设上限。
3. **Skill Proposer**：多轮 ReAct——初始只给 wiki 索引、skill-impact、训练结果摘要，**按需** read_file 查模式页和 raw；产出**原子提案**（一次只动一个 skill）。
4. **Gating & Rollback**：验证集上只有超过历史最优 Rbest 才接受；被拒 skill 回滚——**wiki 无论结果如何都保留**。

**核心不对称**：技能（干预）严格门控、可回滚；知识（证据）自由复利、永不回滚。被拒提案本身也变成 wiki 知识（"这个方案试过，验证分 0.72，被拒"）。

## 5. 实验结果全景

**设置**：五基准 LiveMath / SealQA / SpreadSheet / OfficeQA / ALFWorld；五模型 Gemini-3.5-Flash、Qwen-3.6-27B 等；对比 EvoSkill、Trace2Skill、SkillOpt。

### 主结果

WikiSkill 全部五模型平均分第一：**Gemini Flash 68.1%（次优 56.1%）**、**Qwen-27B 63.3%（次优 53.3%）**。单点：Gemini LiveMath **33.0→72.6%**、SpreadSheet **50.5→76.6%**；Qwen ALFWorld **52.8→77.6%**。竞争方法**不稳定**：EvoSkill 把 Qwen-9B LiveMath 提 30 分却把 Gemma-31B 同基准降 4 分。

### 技能进化与模型规模互补

- 收益随规模递增：Qwen 4B/9B/27B 平均增益 **+12.3 / +17.5 / +23.9**；
- **9B+技能（47.4%）> 27B 无技能（39.4%）**——技能可以抵规模；
- 下限：OfficeQA 多步搜索对 4B 太难，轻微退化。

### 跨模型迁移

- Qwen-9B 用 27B 进化技能 ALFWorld **70.2%**（自己技能 **63.4%**）；
- 4B 技能把 Gemma-31B LiveMath 提到 **73.1%**；
- **负迁移**：4B SpreadSheet 技能把 Gemini Flash 从 **50.5% 打到 18.1%**——小模型技能编码低层 workaround，约束强模型用端到端脚本。

### 消融（Gemini Flash）

- Proposer 有 wiki：**48.7% → 63.7%（+15.0）**——持久知识是关键；
- Inference 训练时访问 wiki：**63.7% → 60.9（−2.8）**——解法从 wiki 泄漏，轨迹看不出 skill 缺陷，进化信号被污染。

### 案例（ALFWorld, Qwen-27B）

迭代 0：goal-directed-action 技能验证 0.72 被拒，diff 存入 skill-impact；迭代 1：参照拒绝史提 break-repetition-loop（0.78 通过）；迭代 2–4：新循环变体累积，技能再精化。39–52% 接受更新发生在早期，精化持续到中后期。

## 6. 局限

1. **评估侧仍是静态验证集 + Rbest 单调爬升**——与 EvoLM/RQGM/WGtG 批评的标准设置相同；主观质量域会遇到 DGM 式天花板。
2. **wiki 永不回滚 → 知识层污染风险**：skill 门控挡得住坏 skill，挡不住 wiki 里错误归因——没有 wiki 质量的独立审计；WGtG 锚定纪律用到知识层是显然补法。
3. **严格门控的保守性**：只接受验证分严格提升，排除"当下中性但为后续铺路"的修改——与 DGM"踏脚石常经过性能下跌"直接冲突；探索性全部由 wiki 承担。
4. **全文注入的实验室设定**：技能全文进 system prompt 回避检索/触发问题——生产技能库增长后检索失败会吃掉收益。
5. **与 MOSS 的张力**：MOSS 说文本层够不着 harness 故障；WikiSkill 证明文本层内部还有大量未挖收益且技能可跨模型交易——**结构性故障归源码层，流程性知识归文本层**。

## 7. 意义与位置

**"证据自由复利、干预严格门控"是不方法论上的真创新**——把科研组织方式（实验记录不可变、综述持续更新、结论过同行评审）搬进 agent 自改进循环。

**六篇核心的正交补位**：六篇聚焦评估器进化，WikiSkill 聚焦知识沉淀——两个正交轴。它的验证门控是最朴素的静态评估器；持久 wiki 层是 ECHO/RQGM 缺的东西。

**与 Anthropic**：wiki 正是"品味"的可积累形式——什么试过、为什么失败、什么模式反复出现；skill 迁移实验暗示品味可由强模型生产、弱模型消费。
