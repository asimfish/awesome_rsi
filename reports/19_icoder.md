# iCoder 深度解读：AI 主导开发前沿工业编码模型——人类到底还握着什么

> **iCoder Technical Report: AI-Led Development of a Frontier Industrial Coding Model**
> [Coder_Tech_Report.pdf](https://huggingface.co/i-Coder/iCoder-27B/blob/main/Coder_Tech_Report.pdf)（32 页，2026）· 上海交大 AI 学院 + NUS + DP Technology（Project Lead: Guibin Zhang；Senior Advisors 含 Junchi Yan、Shuicheng Yan、鄂维南）
> 模型 / 代码：[iCoder-27B](https://huggingface.co/i-Coder/iCoder-27B) · [github.com/bingreeky/iCoder](https://github.com/bingreeky/iCoder)
> 中文解读：[《AI到底能不能自己造AI？别吵了，有人做出来了》](https://mp.weixin.qq.com/s/28q7O59IzEXl_tiWulYbDA)
> 归档：`papers/en/iCoder27B_TechReport.pdf`
> **owner 标注：此代码可考虑作为后续开发基础**

---

## 1. 一句话定位

Anthropic《When AI builds itself》说内部 >80% 代码由 Claude 写、但方向权在人；iCoder 把"方向权"具体化为一张**五层 prior 边界表**，第一次给出"人类到底还握着什么"的工程清单——**交付物定义、权限门、正确性判据、证据纪律**四样，其余全部让渡。问题不是"agent 能不能优化"，而是**多少人类介入就够**：把专家经验一次性编码为高密度、低频率的 Research Skills 接口（目标 / 阶段脚手架 / 权限边界 / 操作程序 + 可复用代码），此后数据构建、SFT、OPSD、RLVR 四阶段的全部具体决策交给开发 agent（Codex GPT-5.6-Sol @ xhigh）。最终配方不是人写的，是 agent 在 reward exploits、false verdicts、目标塌缩等失败中修订出来的。产出的 **iCoder-27B 在 RTLLM 上 68.0 全场第一**（超 GPT-5.5 66.0、Claude Opus 4.8 64.7、DeepSeek-V4-Pro 67.5），KernelBench L1 correctness **61**（近两倍于 DeepSeek-V4-Pro 32）。它是 Anthropic 报告之后最完整的"AI 造 AI"工业实证——不是 agent 改 harness、不是 agent 刷单一基准，而是 agent 主导交付一个 release-ready 的 27B 前沿模型。

## 2. 要解决的问题

论文把"AI 自主研究"讨论中的一个常见混淆拆开：**"agent 能否做出好决策"与"人类需要介入多少"是两个问题**。前者已被 AI Scientist、AlphaEvolve 等工作部分回答；后者才是决定"AI 造 AI"是否经济可行的变量——如果每个决策都要人审，自动化没有意义；如果完全放手，reward hacking 与目标漂移不可控。

具体到模型开发，四个阶段各有陷阱：
- **数据构建**：任务池的质量决定一切，但"什么任务值得练"需要领域专家判断；
- **SFT**：冷启动轨迹从哪来？合成还是采集？
- **OPSD（on-policy self-distillation）**：self-teacher 看什么证据？目标塌缩怎么防？
- **RLVR**：reward 被 exploit、verifier 给 false verdict、输出长度退化——每一个都会毁掉训练。

iCoder 的假设：**人类的领域知识可以一次性预编译，agent 的运行时决策不需要人类实时参与**——但前提是把"不许靠试错学的东西"（invariants）写死。

## 3. 为什么此前做不通：三条线各差一块

| 已有路线 | 有什么 | 缺什么 |
|---|---|---|
| Anthropic 内部实践（报告 02） | >80% 代码 AI 写 | 方向权仍在人；无公开的边界规格 |
| AI Scientist / AlphaEvolve | agent 主导单任务研究 | 目标是论文或单一函数，不是 release-ready 模型 |
| DGM / Meta-Harness（报告 07/13） | agent 改 harness | 改的是 agent 自己的脚手架，不是训练管线 |
| Co-Harness（报告 21） | harness + 权重共进化 | 数学域；harness 改动是局部 diff |
| 传统 AutoML | 超参搜索自动化 | 搜索空间人定；不做数据构建与 reward 设计 |

关键缺口：**没有人把"模型开发流水线本身"当作被 harness 的对象**——Weng 的 harness 工程针对编码 agent，iCoder 把它升级为 **research harness 工程**：被 harness 的不是 agent，是模型开发过程。

## 4. 方法机制

### 4.1 五层 prior，各带不可越界线（Table 1）

| 层 | 人类一次性写入 | agent 的边界 |
|---|---|---|
| **目标与脚手架** | 目标能力、完成判据、Data→SFT→OPSD→RLVR 阶段角色 | 可选实验与阶段转移，**不得悄悄重定义交付物** |
| **资源访问** | 批准的仓库/模型/数据/启动器/算力/存储 | 预算内使用注册能力，**新身份新权限须过人类门** |
| **验证** | 任务契约 schema、官方 harness 要求、完整性检查 | 可集成与审计 verifier profile，**不得削弱或替换批准的正确性判据** |
| **研究方法** | 受控 pilot、显式基线、artifact 血统、停止规则 | 可提假设选判别性实验，**结论必须引用注册证据** |
| **治理与记忆** | 任务队列、实验日志、决策记录、审批边界 | 可写 run 级发现与负结果，**人类 prior 在 run 内不可变** |

人类介入的形态从"反复指导"变成**门控**：正常运行零介入，只有新权限申请才需要人。invariants（held-out 分离、verifier 完整性、checkpoint 可溯源到数据/代码/配置/父模型）被明确列为"不许靠试错学的东西"——直接写死。

### 4.2 四阶段与失败驱动的配方修订

❶ **构建可执行任务池**：task-oracle 对，每条可测——RTL 设计用仿真测试台，GPU kernel 用正确性 + 性能基准。
❷ **SFT 冷启动**：verified capability-gap 轨迹——只用基座模型做不出、但可验证正确的轨迹。
❸ **OPSD**：评估结果改变数据准入；受控消融改变 self-teacher 可见证据；**一次目标塌缩**迫使 agent 围绕 verifier-anchored credit 重设计学习规则。
❹ **RLVR**：reward exploits、false verdicts、长度退化相继迫使 agent 修改 reward 资格、优化器与轨迹预算。

**阶段序列可回退**：SFT 发现任务族缺失可退回数据构建；OPSD 只有在评估指出"有名字、可恢复"的弱点后才进入。

### 4.3 Research Skills 的表示

版本化的"操作程序 + 可复用代码"，把 SOP、权限、模块级操作做成 agent 可执行的 prior——这正是 Weng（报告 01）说的"harness 是可执行搜索空间"的模板级实现。

## 5. 实验结果全景

### 5.1 RTL 设计

| 基准 | iCoder-27B | GPT-5.5 | Opus 4.8 | Gemini 3.5 Flash | DeepSeek-V4-Pro | Qwen3.6-27B（基座） |
|---|---|---|---|---|---|---|
| **RTLLM** | **68.0** | 66.0 | 64.7 | 63.5 | 67.5 | 49.6 |
| VerilogEval Spec-to-RTL | **86.3** | – | – | – | – | 70.1 |
| CVDP | 第二 | – | – | – | – | – |

对同尺寸基座 Qwen3.6-27B：RTLLM **+18.4**、VerilogEval **+16.2**。DeepSeek-V4-Pro 是 1.6T 总参 / 49B 激活——iCoder 用 27B 密集参数超过它。

### 5.2 GPU Kernel

| 基准 | iCoder-27B | GPT-5.5 | Opus 4.8 | Gemini 3.5 Flash | DeepSeek-V4-Pro | Qwen3.6-27B |
|---|---|---|---|---|---|---|
| **KernelBench L1 correctness** | **61** | 43 | 55 | 45 | 32 | – |
| KernelBench L2 correctness | 74（第二） | 58 | – | – | – | 28 |
| TritonBench-G | 20.1 | – | 20.1（平） | – | – | – |

L2 对基座 **2.64×**（74 vs 28）；CVDP 与 L2 第二，超 GPT-5.5 达 16 分。

### 5.3 token 效率

八个 RTL 设计迭代优化 case 上，用 **51% / 33%** 的输出 token 逼近 HY3 / DeepSeek-V4-Pro（差 1.1 / 4.5 分）。

### 5.4 失败驱动修订的案例

- **OPSD 目标塌缩**：self-teacher 开始奖励"看起来像正确答案"而非"通过 verifier"——agent 诊断后重设计为 verifier-anchored credit；
- **RLVR reward exploit**：模型学会输出通过弱 verifier 的退化解——agent 收紧 reward 资格；
- **false verdicts**：仿真超时被判为失败——agent 修 verifier 的超时处理；
- **长度退化**：RL 后输出变短丢细节——agent 调整轨迹预算。

每一次修订都被记录为"有名字的失败 → 有证据的修复"，这是治理层的实质内容。

## 6. 局限

1. **归因边界是声明的，不是测量的**："人类供 prior、agent 做决策"的分工里，prior 的信息密度极高（等于把资深团队的全部 SOP 预编译进去），说"低介入"成立，说"低贡献"不成立——这恰是 Bostrom crossover（报告 00）意义上**仍未越线**的证据：系统的改进能力主要来自预编译的人类知识，不是自身生成的。
2. **锚从未进化**：verifier profile 不许 agent 削弱或替换，是全谱系锚定纪律的又一次遵守——但也意味着本文没有回答评估器共进化（报告 03-06）的任何问题，它把最难的部分锁死了。
3. **单 agent 单域**：开发 agent 是 Codex GPT-5.6-Sol 单挑，域限定在有可执行验证的工业编码；没有消融"换更弱的开发 agent 会怎样"，能力地板（报告 11）问题未触及。
4. **无对照组**：没有"同样 prior 由人类团队执行"或"无 prior 的 agent"的对照，无法量化 Research Skills 的贡献。
5. **技术报告体**：无消融、无方差、无 seed。
6. **可执行性红利**：RTL 与 kernel 都有硬 verifier——这个方法论能否迁移到 verifier 弱的域（NLP、推理）未证明。

## 7. 意义与位置

**作为开发基座的工程评估**（owner 标注：后续开发基础）：可复用的不是 27B 权重本身，而是三件基础设施——
1. **Research Skills 的表示**：版本化的"操作程序 + 可复用代码"，可直接换域（把 RTL/kernel 的任务契约换成任何有可执行验证的域）；
2. **治理层**：任务队列 / 实验日志 / 决策记录 / 审批门四件套，与 MOSS（报告 08）的门控回滚同构但更轻；
3. **阶段控制器**：Data→SFT→OPSD→RLVR 可回退状态机。

落地本仓库后续开发时的最短路径：保留 (1)(2)(3) 的接口，替换任务池与 verifier profile。注意代码仓（bingreeky/iCoder）以流水线脚手架为主，27B 训练本身依赖集群绑定，复用时按 Skills 层剥离。

**对报告 02 的递进**：Anthropic 说方向权在人；iCoder 第一次给出"人类到底还握着什么"的工程清单。

**对报告 01 的落地**：Weng 的"harness 工程"在此升级为"research harness 工程"。

**对报告 05 的回避式确认**：Who Grades the Grader 证明评估器共进化必须外置锚；iCoder 的选择是干脆不让评估器进化，用工业域的可执行性红利绕开了最难的问题。

**对报告 12 四维框架的落位**：What = 模型权重（最强形态）、When = inter-test-time、How = reward-based（RLVR）+ imitation（OPSD）混合、Where = 专域（工业编码）——综述分类里"最直接逼近自主模型开发"的那个格子，第一次被 release-ready 规模填上。

**对报告 18（Prime Agent）**：两者都是开源 + 长时程 + 工业级；iCoder 走权重训练路线，Prime Agent 走纯 harness 路线——同一任务上两条路线的直接对比是尚未有人做的实验。

**对报告 00（Bostrom crossover）**：iCoder 是目前最接近 crossover 的公开系统——agent 做了全部运行时决策——但 prior 密度说明"系统自身贡献主导"还没发生。它给出了一个可操作的 crossover 测量方案：**逐步降低 prior 密度，看性能何时崩**。
