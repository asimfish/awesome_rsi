# 解读报告 19 · iCoder：AI 主导开发前沿工业编码模型

| 项目 | 内容 |
|---|---|
| 技术报告 | [Coder_Tech_Report.pdf](https://huggingface.co/i-Coder/iCoder-27B/blob/main/Coder_Tech_Report.pdf)（32 页，2026） |
| 机构 | 上海交大 AI 学院 + NUS + DP Technology（Project Lead: Guibin Zhang；Senior Advisors 含 Junchi Yan、Shuicheng Yan、鄂维南） |
| 模型 / 代码 | [iCoder-27B](https://huggingface.co/i-Coder/iCoder-27B) · [github.com/bingreeky/iCoder](https://github.com/bingreeky/iCoder) |
| 中文解读 | [《AI到底能不能自己造AI？别吵了，有人做出来了》](https://mp.weixin.qq.com/s/28q7O59IzEXl_tiWulYbDA) |
| 在调研中的位置 | Anthropic《When AI builds itself》（报告 02）之后最完整的"AI 造 AI"工业实证：不是 agent 改 harness、也不是 agent 刷单一基准，而是 agent 主导交付一个 release-ready 的 27B 前沿模型；也是本仓库后续开发的候选基座 |

## 一句话核心主张

问题不是"agent 能不能优化"，而是**多少人类介入就够**：把专家经验一次性编码为高密度、低频率的"Research Skills"接口（目标/阶段脚手架/权限边界/操作程序 + 可复用代码），此后数据构建、SFT、OPSD、RLVR 四阶段的全部具体决策交给开发 agent（Codex GPT-5.6-Sol @ xhigh）——最终配方不是人写的，是 agent 在 reward exploits、false verdicts、目标塌缩等失败中修订出来的，产出的 iCoder-27B 在 RTL 设计与 GPU kernel 两个工业域追平或超过大它数十倍的前沿模型。

## 方法拆解：人类接口如何被压缩

**五层 prior，各带不可越界线（Table 1）**：

| 层 | 人类一次性写入 | agent 的边界 |
|---|---|---|
| 目标与脚手架 | 目标能力、完成判据、Data→SFT→OPSD→RLVR 阶段角色 | 可选实验与阶段转移，**不得悄悄重定义交付物** |
| 资源访问 | 批准的仓库/模型/数据/启动器/算力/存储 | 预算内使用注册能力，**新身份新权限须过人类门** |
| 验证 | 任务契约 schema、官方 harness 要求、完整性检查 | 可集成与审计 verifier profile，**不得削弱或替换批准的正确性判据** |
| 研究方法 | 受控 pilot、显式基线、artifact 血统、停止规则 | 可提假设选判别性实验，**结论必须引用注册证据** |
| 治理与记忆 | 任务队列、实验日志、决策记录、审批边界 | 可写 run 级发现与负结果，**人类 prior 在 run 内不可变** |

人类介入的形态从"反复指导"变成**门控**：正常运行零介入，只有新权限申请才需要人。invariants（held-out 分离、verifier 完整性、checkpoint 可溯源到数据/代码/配置/父模型）被明确列为"不许靠试错学的东西"——直接写死。

**四阶段与失败驱动的配方修订**：❶ 构建可执行任务池（task-oracle 对，每条可测）→ ❷ SFT 冷启动（verified capability-gap 轨迹）→ ❸ OPSD（on-policy self-distillation：评估结果改变数据准入、受控消融改变 self-teacher 可见证据、一次目标塌缩迫使 agent 围绕 verifier-anchored credit 重设计学习规则）→ ❹ RLVR（reward exploits、false verdicts、长度退化相继迫使 agent 修改 reward 资格、优化器与轨迹预算）。阶段序列可回退：SFT 发现任务族缺失可退回数据构建，OPSD 只有在评估指出"有名字、可恢复"的弱点后才进入。

## 关键数字

- **RTLLM 68.0 全场第一**：超 GPT-5.5（66.0）、Claude Opus 4.8（64.7）、Gemini 3.5 Flash（63.5），也超 1.6T 总参/49B 激活的 DeepSeek-V4-Pro（67.5）
- **对同尺寸基座 Qwen3.6-27B 的提升**：RTLLM +18.4（68.0 vs 49.6）、VerilogEval Spec-to-RTL +16.2（86.3 vs 70.1）、KernelBench L2 correctness **2.64×**（74 vs 28）
- **KernelBench L1 correctness 61**：近两倍于 DeepSeek-V4-Pro（32），超 GPT-5.5（43）/Opus 4.8（55）/Gemini 3.5 Flash（45）；CVDP 与 KernelBench L2 第二，超 GPT-5.5 达 16 分；TritonBench-G 20.1 平 Opus 4.8
- **token 效率**：八个 RTL 设计迭代优化 case 上，用 51% / 33% 的输出 token 逼近 HY3 / DeepSeek-V4-Pro（差 1.1 / 4.5 分）

## 作为开发基座的工程评估（owner 标注：后续开发基础）

可复用的不是 27B 权重本身，而是三件基础设施：**(1) Research Skills 的表示**——版本化的"操作程序 + 可复用代码"，把 SOP、权限、模块级操作做成 agent 可执行的 prior，这正是 Weng（报告 01）说的"harness 是可执行搜索空间"的模板级实现，可以直接换域（把 RTL/kernel 的任务契约换成任何有可执行验证的域）；**(2) 治理层**——任务队列/实验日志/决策记录/审批门的四件套，与 MOSS（报告 08）的门控回滚同构但更轻；**(3) 阶段控制器**——Data→SFT→OPSD→RLVR 可回退状态机。落地本仓库后续开发时的最短路径：保留 (1)(2)(3) 的接口，替换任务池与 verifier profile。注意代码仓（bingreeky/iCoder）以流水线脚手架为主，27B 训练本身依赖集群绑定，复用时按 Skills 层剥离。

## 局限与批评

1. **归因边界是声明的，不是测量的**："人类供 prior、agent 做决策"的分工里，prior 的信息密度极高（等于把资深团队的全部 SOP 预编译进去），说"低介入"成立，说"低贡献"不成立——这恰是 Bostrom crossover（报告 00）意义上仍未越线的证据。
2. **锚从未进化**：verifier profile 不许 agent 削弱或替换，是全谱系锚定纪律的又一次遵守——但也意味着本文没有回答评估器共进化（报告 03-06）的任何问题，它把最难的部分锁死了。
3. **单 agent 单域**：开发 agent 是 Codex GPT-5.6-Sol 单挑，域限定在有可执行验证的工业编码；没有消融"换更弱的开发 agent 会怎样"，能力地板（报告 11）问题未触及。

## 与本调研的连线

1. **对报告 02 的递进**：Anthropic 说内部 >80% 代码由 Claude 写但方向权在人；iCoder 把"方向权"具体化为五层 prior 的边界表，第一次给出"人类到底还握着什么"的工程清单——答案是：交付物定义、权限门、正确性判据、证据纪律四样，其余全部让渡。
2. **对报告 01 的落地**：Weng 的"harness 工程"在此升级为"research harness 工程"——被 harness 的不是编码 agent 而是模型开发过程本身。
3. **对报告 05 的回避式确认**：Who Grades the Grader 证明评估器共进化必须外置锚；iCoder 的选择是干脆不让评估器进化（executable toolchain + 官方 harness 锁死），用工业域的可执行性红利绕开了最难的问题。
4. **对报告 12 四维框架的落位**：What=模型权重（最强形态）、When=inter-test-time、How=reward-based（RLVR）+imitation（OPSD）混合、Where=专域（工业编码）——综述分类里"最直接逼近自主模型开发"的那个格子，第一次被 release-ready 规模填上。

