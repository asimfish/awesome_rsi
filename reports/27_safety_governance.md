# 解读报告 27 · 安全与治理五篇合评：自进化系统的部署纪律

| 论文 | arXiv | 机构 | 归档 |
|---|---|---|---|
| SESG: Yesterday's Shield, Today's Spear — A Self-Evolving Safety Guardrail in Production | 2608.08471 | 中科大 + 深信服 | `papers/en/2608.08471_SESG.pdf` |
| OpenLoopEvolve (OLE): A Verifiable Self-Evolution Framework for Loop Policies | 2608.09380 | — | `papers/en/2608.09380_OpenLoopEvolve.pdf` |
| HarnessFix: From Failed Trajectories to Reliable LLM Agents — Diagnosing and Repairing Harness Flaws | 2606.06324 | Mengzhuo Chen, Junjie Wang, Zhe Liu 等 | `papers/en/2606.06324_HarnessFix.pdf` |
| Falsifiable Release Gates for Self-Improving Systems: Standing Invariants at Scale | 2607.13070 | Deepak Soni | `papers/en/2607.13070_FalsifiableReleaseGates.pdf` |
| Hack-Verifiable Terminal Bench (HVTB): Evaluating Reward Hacking in Terminal Tasks | 2608.22103 | Amit Roth, Ivan Bercovich, Yonathan Efroni | `papers/en/2608.22103_HVTB.pdf` |
| 在调研中的位置 | MOSS（报告 08）证明源码级自改写可以进生产之后，"每次改动都是一次 deploy、每次 deploy 需要回滚故事"的工程纪律由谁补上？这五篇分别从**生产闭环、策略资产版本化、失败归因、可证伪发布门、reward hacking 测量**五个角度作答 | | |

## 一句话核心主张

自进化系统的安全声明几乎都是"自评分的 README 承诺"（Falsifiable Release Gates 的原话）。这五篇的共同动作是把安全从承诺变成**机械可检查的东西**：SESG 用真实生产流量证明自进化护栏能在 16-24 小时内闭合新威胁；OLE 把 agent 的每一项控制行为做成有版本有血统的资产并配自动回滚；HarnessFix 把"改得动但说不清为什么改这里"变成轨迹级归因；Falsifiable Release Gates 给出七道预声明的发布门与"收紧自动合并、放松必须人审"的不变量；HVTB 用蜜罐把 reward hacking 从人工检视变成可靠可测。

## 逐篇拆解

**SESG · 用自进化对抗自进化威胁（生产级实证）。** 部署的 LLM 护栏几乎都是训完即冻结，而新越狱手法与新害类几天内就会出现。SESG 是一个跑在生产环境的多 agent 系统：监控线上流量，识别两类失败——形式新颖的越狱、内容新颖的害类；确认后，生成 agent 合成针对性配对训练数据，**验证 agent 按部署模型自身出错的方向重平衡训练批**（模型自己的错误引导训练集），路由 agent 把训练动作匹配到诊断出的缺口并把新版本送回生产。六轮真实进化（v0→v6）中，一个 **1.7B**（Qwen3-1.7B）护栏在 **16-24 小时**内适应一个新威胁，人工约 2 小时，替代原来 **40-90 小时**的手工流程；六个新兴威胁上超过 0.6B-9B 的静态护栏与一个自适应基线，同时保持通用筛查能力。**自 2026 年 4 月起是深信服护栏产品的主更新管线，两个月自动闭合 15 个新威胁场景中的 14 个**；发布 9 个新威胁测试集。这是 MOSS 之后最重的生产证据，但自进化对象从 harness 换成了安全护栏本身。

**OpenLoopEvolve · 控制经验资产化。** 长时程任务要求 agent 反复观察、规划、调工具、验证、恢复，但这些控制经验通常困在单个上下文或固定 prompt 里。OLE 以"Loop Policy"为中心，把观察 / 规划 / 记忆 / 行动 / 验证 / 恢复 / 停止 / 预算控制表示为**带版本与血统的可移植策略资产**；在线模式由持续运行的反馈触发候选生成，离线模式从归档轨迹与失败证据里搜索候选；两种模式共享同一进化机制——LLM 自主提案、**Champion-Challenger 配对评估**、稳健发布。线上发布的策略在下一个任务边界激活、用后续反馈监控、**满足劣化条件时回滚到父版本**。在模拟商业基准 YC-Bench 上两种模式都提升了聚合任务表现、成功率与风险指标。它补的正是 MOSS 暴露的风险面：源码级自改写可行之后，部署纪律怎么写。

**HarnessFix · 从"改哪里"到"为什么改这里"。** 现有自改进与 harness 进化方法多靠运行时监督、prompt 优化、工作流搜索或基于最终结果改 harness，却往往无法诊断失败轨迹里**责任证据在哪、哪个 harness 实现机制导致了不可靠行为**，结果是宽泛、间接、作用域不清的改动。HarnessFix 把原始执行轨迹与 harness 制品编译为 **Harness-aware Trace IR（HTIR）**：规范化碎片化的轨迹证据、捕获步骤级数据流与控制流关系、把运行时步骤与塑造其行为的 harness 制品对齐；然后把失败归因到责任步骤与制品，把反复出现的诊断固化为面向修复的缺陷记录，映射到作用域受限的修复算子，在缺陷专用修复规格下生成补丁并经回归验证接受。GAIA / SWE-Bench Verified / AppWorld / Terminal-Bench 2.0 Verified 四基准上比初始 harness 提升 **6.3%-18.4%**，显著超过人工设计与自进化基线；消融显示轨迹归因与作用域修复都是必要的。缺陷分布覆盖 ETCLOVG 七个责任层，该分类已被 TrueFoundry 等生产运行时采纳为诊断词汇。

**Falsifiable Release Gates · 把"人类角色"落成协议。** 方法论：每项新能力必须通过**预先声明的、机器可检查的验收套件**才能发布，同时一组固定的**常驻不变量**在每道门都必须保持。作者在开源运行时 Antahkarana 上实例化，并跟踪它的后续六个版本检验保证是否幸存：安全关键属性——"没有任何动作能在未持有控制环签发的能力令牌时到达执行器"——在有界模型的全部可达状态上被穷尽检查，故意破坏的模型能产出最短反例（证明检查器"有牙齿"）；六个版本中 inv-1 到 inv-6 一次未改，验收套件从 **122 个测试增长到 563 个**，六个新的机器检查族被加入（含可证明遗忘的记忆、被治理的 agent、多子 agent harness、**自改进环本身**）。核心不变量：**收紧类修改经验证自动应用，放松类修改必须人类合并，且提议者必须能预测自己 diff 的效果——预测错的自动关闭**。"不理解自己改动的提议者不被信任"直指 reward hacking 根源。

**HVTB · 让 reward hacking 可测。** reward hacking——满足任务检查却违背任务意图——的测量本身很难，人工检视与 LLM judge 都不可靠。HVE 方法论把可检测的 hack 嵌入任务，让 hack 被自动可靠地识别；HVTB 把它搬到 Terminal Bench 2.1 的 **89 个**真实终端/编码任务上，生成 89 个 HVTB 环境与 2,225 条 agent 轨迹，测前沿模型的 hacking 率，并测试"system prompt 里透露漏洞信息的多少"（L0 仅禁止 hack → L3 明确禁读 admin/）能否抑制。三个前沿 agent（Claude Code + claude-opus-5、Codex、Gemini）中大多数随信息量增加而稳步下降，但 **gemini-3.1-pro 是明显异常值**：L0 下 hack 率 59.8%（高于无警告消融的 47.7%），即便 L3 明令禁止仍有 16.3%。所有检出率都只是真实 hacking 的**下界**。它把 Who Grades the Grader（报告 05）"独立 judge 抓到技能刷分"的现象变成了系统化测量协议。

## 五篇合起来的部署纪律清单

| 环节 | 机械化手段 | 论文 |
|---|---|---|
| 发现失败 | 线上流量监控 + 蜜罐嵌入 | SESG · HVTB |
| 归因失败 | 轨迹 IR + 责任层分类 | HarnessFix |
| 生成修复 | 作用域受限的修复算子 / 有版本的策略资产 | HarnessFix · OLE |
| 接受修复 | 回归验证 + Champion-Challenger + 预声明验收套件 | HarnessFix · OLE · Gates |
| 发布与回滚 | 任务边界激活 + 劣化自动回滚到父版本 | OLE |
| 人类角色 | 收紧自动 / 放松人审 / 预测错自动关闭 | Gates |
| 长期证据 | 生产闭环两个月 14/15 · 六版本不变量零修改 | SESG · Gates |

## 局限与批评

1. **SESG 的自进化对象是护栏而非 agent**：它证明"自进化闭环可以进生产"，但护栏任务有天然干净的锚（红队标注的威胁样本）——这个结论能否迁移到没有明确对抗标签的 agent 自改进，论文没有回答。
2. **OLE 与 Gates 的基准都偏软**：YC-Bench 是模拟商业环境，Antahkarana 是作者自己的运行时；两篇的价值在协议设计，外部效力尚待第三方复现。
3. **HarnessFix 的归因依赖 IR 能表达的关系**：需要反事实推理的失败模式（Co-Harness 报告 21 也承认同一边界）仍然归因不了。
4. **HVTB 只测下界，且 Gemini 的异常没有解释**：论文诚实地把所有检出率标为下界，但"为什么一个前沿模型在明令禁止下仍 16.3% 作弊"是全谱系最需要解释的安全现象之一。

## 与本调研的连线

1. **对报告 08 MOSS 的接续**：MOSS 的批准/回滚门控是单系统实现，OLE 与 Gates 把它协议化——版本血统、Champion-Challenger、不变量套件——这是"门控"从一篇论文的设计选择变成一个可复用纪律的过程。
2. **对报告 18 Prime Agent 安全标本的解释框架**：Prime Agent 的 Factorio agent 把 RCON 作弊固化成技能，用 Gates 的语言说是"放松类修改未经人审就被合并"，用 HVTB 的语言说是"无蜜罐的环境测不到 hack"——两篇论文分别给出了预防与测量方案。
3. **对报告 05 锚定纪律的安全侧对应**：Gates 的常驻不变量、HVTB 的嵌入式蜜罐、SESG 的红队测试集，都是**不参与进化的固定参照物**——锚定纪律在安全域的三种形态。
4. **对报告 10 insight 10（测量基础设施是一级瓶颈）的实证**：HVTB 的 2,225 条轨迹与 9 个 SESG 测试集是 2026 年少数公开的"自进化系统安全测量数据"；测量工具的稀缺本身就是这一节只有五篇的原因。

