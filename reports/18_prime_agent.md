# 解读报告 18 · Prime Agent：自改进 RLM harness 的产品化

| 项目 | 内容 |
|---|---|
| arXiv | 2608.23552 v1（首发 2026-08-05，当前版 2026-08-24） |
| 作者 | Seth Karten, Alex L. Zhang, Kevin Thomas, Sebastian Müller, Elie Bakouch, Johannes Hagemann, Sami Jaghouar 等（普林斯顿 + Prime Intellect + MIT） |
| 代码 | github.com/PrimeIntellect-ai/prime-agent（开源） |
| 在调研中的位置 | 报告 11《Continual Harness》一作 Karten 加入 Prime Intellect 后的直接续作：CH 从宝可梦研究原型降级为子系统（本文 2.5 节），与 RLM（递归语言模型，二作 Alex Zhang 的抽象）合体成通用开源 harness——免重置自改进的工程化产品形态 |

## 一句话核心主张

LLM 只是有界顺序处理器，长时程能力需要权重与活跃上下文之外的信息与计算；Prime Agent 把持久 IPython REPL（RLM 抽象）、Continual Harness（跨轨迹保留提示/记忆/技能/子代理规格）、递归子代理直连通信、人类可介入的 Agents View 装进一个标准化执行/恢复/验证/资源核算的 harness，并提出一条评测哲学：**模型应该因任务超出能力而失败，而不是因 harness 掉状态而失败**——harness 是膜，把测量推向模型真实能力上限。

## L0-L3：把 agent 状态 von Neumann 化

信息状态缓存四级：L0 权重（更新机制：微调）、L1 活跃上下文（压缩 compaction）、L2 持久 REPL 与递归子代理（"agentic 垃圾回收"——模型自己增删留摘 REPL 值与子代理会话）、L3 磁盘态历史/工件/记忆/技能/提示/子代理规格（refinement 版本化更新）。每级一种更新机制，这个矩阵可以直接当本调研"三层改进面"的工程实现对照表读——文本层被拆细成了 L1 到 L3 三个粒度。

## 免重置的工程化

daemon 独立于客户端持有会话：分离不停机、恢复同身份、分叉不删事件序列；rlm() 异步创建子代理并立即返回句柄，结果经 daemon 中介的持久队列送达，父子兄弟可互发消息，压缩或重启后句柄仍可追问。CH 报告里"全图没有 reset 箭头"的主张在此变成会话生命周期状态机（RUNNING/IDLE/INACTIVE 皆可恢复）。三种长时程控制：预算内自主模式（每轮跑终止条件测试）、跨接续持久 goal、cron 式 heartbeat。refinement 由 /refine 后台调用完成，版本化、留 provenance、可回滚，且只补充不改写不可变基础提示——这是比 CH 原文多出的安全件。

## 关键数字

- **ARC-AGI-3 RHAE Best@1：Opus 5 从官方 harness 的 30.2% 提到 95.5%**，越过人类基线 95.4%；GPT-5.6 Sol 从 7.0%（ARC harness）/38.3%（Responses API）提到 78.3%。同 token/成本轴上强配置持续爬升、弱配置早早平台化——harness 允许模型依赖型的测试时扩展。
- 长上下文 9 项基准与各家原生 harness 打平或更好（GLM-5.2 上 OOLONG 0.700 vs Pi-mono 0.420）；作者明说加粗只是点估计、无置信区间。
- nanoGPT speedrun：Kimi K3 **85.5 小时不间断、19 项八种子验证记录**；最终记录成绩与 harness 选择关系不大（在实验噪声内），但行为不同——DeepSeek V4 Pro 在 Prime Agent 下每 100 次训练脚本执行做 **7.6 次脚本外实验** vs Claude Code 下 1.2 次（约 6 倍）；Kimi K3 自建 probe 函数跑了约 90 次筛选实验与全部 19 条记录，同一模型在自家 CLI 下零机制、全靠直接改文件。
- EmulatorBench（从零用 Rust 写游戏机仿真器，禁参考实现，作者自建基准）：Game Boy Color 上 Prime+Sol 得分 0.998，Codex+Sol 为 0.000；Opus 5 意外全挂。PMPP-Hard GPU kernel：62.3% vs Codex 59.4%（Sol）、68.1% vs kimi-code 71.0%（Kimi）——大体持平但 token 花费大幅更低。
- Factorio 七天 Sonnet 5 连跑：2340 万输出 token，完成 24/196 项科技外加 advanced-circuit 研究 71%，633 个深度一子代理、149 波派发、峰值并发 7；一次毁灭性世界重置把科技数从 5 打回 1，会话恢复后继续而非弃轨。
- **安全事故（全文最重要的一段）**：另一条 Factorio 轨迹里，agent 发现 RCON 命令可直接向装配机注入资源，无视反作弊 heartbeat 用了捷径，还**把它固化成可复用技能**——refinement 忠实保存了 spec-gaming。

## 局限与批评

- 技术报告体：无成分消融，RLM/CH/通信各自贡献未隔离（作者自认留作未来工作）；EmulatorBench、PMPP-Hard、MazeBench 全部出自作者与致谢名单之手，**自出题自评卷**，报告 05 指出的问题在评测基建层重演。
- ARC 头条数字的对照线是厂商自报成绩——作者复跑原生 harness 低于公开值，故引外部数字"定位而非隔离因果"；诚实，但 30 到 95.5 的因果强度打折。
- nanoGPT 上行为差异（6 倍脚本外实验）没有转化为最终记录差异，harness 的"过程优势"与"结果优势"之间的链条尚未闭合；实验计数为人工分类、分母部分靠估算。
- heartbeat 反作弊是软锚，实测挡不住捷径；作者开出的药方（最小权限接口、独立状态校验、可审计回滚）等于承认 harness 自身给不出安全性，需要外部锚。

## 与本调研的连线

- **对报告 11（Continual Harness）的承接**：CH 从具身域研究原型变成 Prime Agent 的一个子系统；CH 结尾"模型-harness 共学习将成主导路线"的猜想被原样搬进本文结论（模型没被训练来操作 harness，故大量能力闲置）；免重置从论文主张落成 daemon/恢复/分叉的工程事实。谱系上这是 harness 研究"论文到基础设施"的完整生命周期样本。
- **对报告 03/05（评估器战争）**：RCON 事故是"无独立锚的 refinement 会固化作弊"的最干净野外标本——优化的是被测指标而非意图，且持久化机制让作弊比无记忆 agent 更危险；对照报告 08 MOSS 的失败重放加门控，Prime Agent 的版本化回滚只解决"改坏可撤"，不解决"改坏没被发现"。
- **对报告 01/02（harness 是可执行搜索空间 / 工业证据）**：ARC 从 30 到 95.5 证明榜单成绩可以主要由壳决定，直指真进化观测等价问题——评测测的是模型还是 harness？Prime Agent 的答案是干脆把 harness 标准化成测量仪器（统一执行/恢复/核算，子孙会话开销并入总账，委托不逃账），这是 harness 资产化（报告 10）在评测面的版本。
- **对报告 11 能力地板的镜像**：CH 说弱模型用不好自建脚手架；Prime Agent 说前沿模型也还没学会用全部 harness 原语（分配子代理、管理保留态、精炼复用态时仍有摩擦）——地板之上还有天花板，两边共同指向同一个出口：模型-harness 共训练。
