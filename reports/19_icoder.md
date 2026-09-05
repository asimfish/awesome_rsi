# iCoder 深度解读：AI 主导模型开发，人类规定目标、权限与验证要求

> **iCoder Technical Report: AI-Led Development of a Frontier Industrial Coding Model**
> [Coder_Tech_Report.pdf](https://huggingface.co/i-Coder/iCoder-27B/blob/main/Coder_Tech_Report.pdf)（32 页，2026）· 上海交大 AI 学院 + NUS + DP Technology（Project Lead: Guibin Zhang；Senior Advisors 含 Junchi Yan、Shuicheng Yan、鄂维南）
> 模型 / 代码：[iCoder-27B](https://huggingface.co/i-Coder/iCoder-27B) · [github.com/bingreeky/iCoder](https://github.com/bingreeky/iCoder)
> 中文解读：[《AI到底能不能自己造AI？别吵了，有人做出来了》](https://mp.weixin.qq.com/s/28q7O59IzEXl_tiWulYbDA)
> 归档：`papers/en/iCoder27B_TechReport.pdf`
> **owner 标注：此代码可考虑作为后续开发基础**

---

## 1. 一句话定位

Anthropic《When AI builds itself》称内部 >80% 的代码由 Claude 编写，研究方向仍由人决定。iCoder 用一张**五层 prior 边界表**首次列明人类保留的职责：**定义交付物、审批权限、规定正确性判据和证据要求**。它关注 **agent 开发过程中需要多少人工介入**，将专家经验集中写入低频更新的 Research Skills 接口（目标 / 阶段脚手架 / 权限边界 / 操作程序 + 可复用代码）。此后，数据构建、SFT、OPSD、RLVR 四阶段的全部具体决策交给开发 agent（Codex GPT-5.6-Sol @ xhigh），由 agent 根据 reward exploits、false verdicts、目标塌缩等失败修订训练方案。

产出的 **iCoder-27B 在 RTLLM 上得分 68.0，排名第一**，超过 GPT-5.5 66.0、Claude Opus 4.8 64.7、DeepSeek-V4-Pro 67.5。KernelBench L1 correctness 为 **61**，接近 DeepSeek-V4-Pro 32 的两倍。这是在 Anthropic 报告之后公开的"AI 造 AI"工业案例，涵盖模型开发全过程。已有工作中，agent 修改 harness，或由 agent 优化单一基准；本文由 agent 主导交付一个 release-ready 的 27B 前沿模型。

## 2. 要解决的问题

论文区分了"AI 自主研究"中的两个问题：**agent 能否做出好决策，以及人类需要介入多少**。AI Scientist、AlphaEvolve 等工作已部分回答前者。后者决定"AI 造 AI"是否经济可行：逐次审核每个决策会增加人工成本，完全放手又难以控制 reward hacking 与目标漂移。

模型开发的四个阶段各有待解决的问题：
- **数据构建**：任务池质量影响训练效果，选择值得训练的任务需要领域专家判断；
- **SFT**：需要确定冷启动轨迹的来源，以及采用合成还是采集；
- **OPSD（on-policy self-distillation）**：需要规定 self-teacher 可见的证据，并防止目标塌缩；
- **RLVR**：reward 被 exploit、verifier 给出 false verdict、输出长度退化，都可能使训练失败。

iCoder 假设，**人类可以预先写入领域知识，此后由 agent 独立做运行时决策**。前提是固定 invariants，让系统始终遵守这些要求，不能通过试错修改它们。

## 3. 为什么此前做不通：三条线各差一块

| 已有路线 | 有什么 | 缺什么 |
|---|---|---|
| Anthropic 内部实践（报告 02） | >80% 代码由 AI 编写 | 研究方向仍由人决定；未公开具体职责边界 |
| AI Scientist / AlphaEvolve | agent 主导单任务研究 | 目标是论文或单一函数，未涵盖 release-ready 模型的开发 |
| DGM / Meta-Harness（报告 07/13） | agent 改 harness | 修改 agent 自身的运行框架，未涵盖训练流程 |
| Co-Harness（报告 21） | harness + 权重共进化 | 数学域；harness 改动是局部 diff |
| 传统 AutoML | 自动搜索超参 | 搜索空间由人决定；不做数据构建与 reward 设计 |

此前尚未用 harness 管理**模型开发流程本身**。Weng 的 harness 工程针对编码 agent，iCoder 的 **research harness 工程**则针对模型开发过程，由 harness 规定 agent 在各阶段的操作与边界。

## 4. 方法机制

### 4.1 五层 prior，各带不可越界线（Table 1）

| 层 | 人类一次性写入 | agent 的边界 |
|---|---|---|
| **目标与脚手架** | 目标能力、完成判据、Data→SFT→OPSD→RLVR 阶段角色 | 可选择实验和阶段转移，**不得擅自重新定义交付物** |
| **资源访问** | 批准的仓库/模型/数据/启动器/算力/存储 | 在预算内使用注册能力，**申请新身份或权限须经人工批准** |
| **验证** | 任务契约 schema、官方 harness 要求、完整性检查 | 可集成与审计 verifier profile，**不得削弱或替换批准的正确性判据** |
| **研究方法** | 受控 pilot、显式基线、artifact 溯源、停止规则 | 可提出假设，选择能区分假设的实验，**结论必须引用注册证据** |
| **治理与记忆** | 任务队列、实验日志、决策记录、审批边界 | 可记录 run 中的发现与负结果，**人类 prior 在 run 内不可变** |

正常运行时无需人工介入，只有申请新权限时才需要**人工审批**。invariants 包括 held-out 分离、verifier 完整性，以及 checkpoint 可追溯到数据/代码/配置/父模型。这些要求预先固定，运行中不能通过试错修改。

### 4.2 四阶段与失败驱动的配方修订

❶ **构建可执行任务池**：以 task-oracle 对组织任务，每条均可测试。RTL 设计用仿真测试台，GPU kernel 用正确性与性能基准。
❷ **SFT 冷启动**：使用 verified capability-gap 轨迹，即基座模型无法完成、但能验证为正确的轨迹。
❸ **OPSD**：根据评估结果调整数据准入，通过受控消融调整 self-teacher 可见的证据。**一次目标塌缩**后，agent 围绕 verifier-anchored credit 重新设计学习规则。
❹ **RLVR**：出现 reward exploits、false verdicts 和长度退化后，agent 相继修改了 reward 资格、优化器与轨迹预算。

**阶段可回退**：SFT 中发现缺少某类任务时，可退回数据构建。只有评估明确指出可识别、可修复的弱点后，才进入 OPSD。

### 4.3 Research Skills 的表示

技能用保存版本的"操作程序 + 可复用代码"组织 SOP、权限与模块级操作，作为 agent 可执行的 prior。这通过模板实现了 Weng（报告 01）提出的"harness 是可执行搜索空间"。

## 5. 实验结果全景

### 5.1 RTL 设计

| 基准 | iCoder-27B | GPT-5.5 | Opus 4.8 | Gemini 3.5 Flash | DeepSeek-V4-Pro | Qwen3.6-27B（基座） |
|---|---|---|---|---|---|---|
| **RTLLM** | **68.0** | 66.0 | 64.7 | 63.5 | 67.5 | 49.6 |
| VerilogEval Spec-to-RTL | **86.3** | – | – | – | – | 70.1 |
| CVDP | 第二 | – | – | – | – | – |

相较同尺寸基座 Qwen3.6-27B，RTLLM 提高 **+18.4**，VerilogEval 提高 **+16.2**。DeepSeek-V4-Pro 有 1.6T 总参数 / 49B 激活参数，iCoder 用 27B 密集参数获得了更高分数。

### 5.2 GPU Kernel

| 基准 | iCoder-27B | GPT-5.5 | Opus 4.8 | Gemini 3.5 Flash | DeepSeek-V4-Pro | Qwen3.6-27B |
|---|---|---|---|---|---|---|
| **KernelBench L1 correctness** | **61** | 43 | 55 | 45 | 32 | – |
| KernelBench L2 correctness | 74（第二） | 58 | – | – | – | 28 |
| TritonBench-G | 20.1 | – | 20.1（平） | – | – | – |

L2 得分为基座的 **2.64×**（74 vs 28）。CVDP 与 L2 均排名第二，超过 GPT-5.5 达 16 分。

### 5.3 token 效率

在八个 RTL 设计迭代优化 case 上，使用 **51% / 33%** 的输出 token，得分接近 HY3 / DeepSeek-V4-Pro，分别相差 1.1 / 4.5 分。

### 5.4 失败驱动修订的案例

- **OPSD 目标塌缩**：self-teacher 开始奖励外观类似正确答案、却未通过 verifier 的输出。agent 诊断后改用 verifier-anchored credit；
- **RLVR reward exploit**：模型学会输出能通过弱 verifier 的退化解，agent 随后收紧 reward 资格；
- **false verdicts**：仿真超时被判为失败，agent 修正 verifier 的超时处理；
- **长度退化**：RL 后输出变短，遗漏细节，agent 因此调整轨迹预算。

每次修订都记录了具体的失败原因及修复证据。

## 6. 局限

1. **人类与系统的贡献尚未测量**：在"人类提供 prior、agent 做决策"的分工中，prior 包含大量信息，相当于预先写入资深团队的整套 SOP。人工介入次数少，仍可能高度依赖人类贡献。按 Bostrom crossover（报告 00）的标准看，系统**尚未由自身贡献主导改进**，改进能力主要来自预先写入的人类知识。
2. **评估依据保持固定**：agent 不得削弱或替换 verifier profile。本文因此没有处理评估器共进化的问题（报告 03-06），固定评估依据也是该设置成立的条件。
3. **单 agent 单域**：由 Codex GPT-5.6-Sol 担任开发 agent，领域限定为有可执行验证的工业编码。没有通过消融考察更弱的开发 agent，报告 11 所讨论的最低能力要求尚未得到检验。
4. **无对照组**：没有设置"同样 prior 由人类团队执行"或"无 prior 的 agent"的对照，无法量化 Research Skills 的贡献。
5. **技术报告未给出统计验证**：无消融、无方差、无 seed。
6. **依赖可执行验证**：RTL 与 kernel 都有可执行的 verifier。方法能否迁移到 verifier 较弱的领域（NLP、推理），尚未得到证明。

## 7. 意义与位置

**作为开发基座的工程评估**（owner 标注：后续开发基础）：从这个 27B 模型开发项目中，可复用以下三项基础设施：
1. **Research Skills 的表示**：保存版本的"操作程序 + 可复用代码"。将 RTL/kernel 的任务契约替换为其他有可执行验证领域的契约，即可用于新领域；
2. **治理层**：任务队列 / 实验日志 / 决策记录 / 审批检查，与 MOSS（报告 08）的检查和回滚机制结构相同，但更轻量；
3. **阶段控制器**：Data→SFT→OPSD→RLVR 可回退状态机。

用于本仓库后续开发时，可保留 (1)(2)(3) 的接口，替换任务池与 verifier profile。代码仓（bingreeky/iCoder）主要提供流程框架，27B 训练仍依赖特定集群配置，复用时需单独提取 Skills 层。

**对报告 02 的递进**：Anthropic 说明研究方向由人决定；iCoder 首次逐项列出人类保留的职责。

**对报告 01 的落地**：Weng 的 harness 工程在这里扩展为管理模型开发过程的 research harness 工程。

**对报告 05 的回避式确认**：Who Grades the Grader 证明评估器共进化需要独立的评估依据。iCoder 保持评估器不变，依靠工业领域的可执行验证开展训练，未处理评估器共进化。

**对报告 12 四维框架的落位**：What = 模型权重、When = inter-test-time、How = reward-based（RLVR）+ imitation（OPSD）混合、Where = 专域（工业编码）。本文首次在这一分类下完成了 release-ready 规模的自主模型开发。

**对报告 18（Prime Agent）**：两者都开源，支持工业任务中的长时程运行。iCoder 训练模型权重，Prime Agent 只修改 harness，目前尚无在同一任务上直接比较两种方法的实验。

**对报告 00（Bostrom crossover）**：评估 iCoder 是否达到 crossover 时，需要同时考虑 agent 做了全部运行时决策，以及 prior 中预先写入的大量人类知识。后一项说明系统自身贡献尚未主导改进。可采用的 crossover 测量方式是**逐步减少 prior 中的信息，观察性能在何时明显下降**。
