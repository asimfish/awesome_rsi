# 解读报告 12 · A Survey of Self-Evolving Agents

| 项目 | 内容 |
|---|---|
| arXiv | 2507.21046 v4（2026-01-16），TMLR 2026-01 正式发表 |
| 作者 | Huan-ang Gao, Jiayi Geng, Wenyue Hua, Mengkang Hu 等约 27 人（16 人共同一作、按字母序）；Princeton / 清华 / CMU / 上交 / UIUC 等 17 家机构；通讯 Hongru Wang、Mengdi Wang |
| 篇幅 | 77 页；GitHub: CharlesQ9/Self-Evolving-Agents |
| 在调研中的位置 | 本仓库唯一的系统性综述，为 01-11 的所有工作提供分类学坐标系；副标题直言目标是 ASI 路线图 |

## 一句话核心主张

LLM 本质静态而部署环境开放动态，因此需要自进化 agent；作者给出的判别标准不是用了什么算法（SFT/RL 都行），而是**自主权的所在地（locus of autonomy）**——数据由谁策划、更新由谁排期，从人类工程师移交给 agent 本身；全文用 What（进化什么）/ When（何时进化）/ How（怎样进化）/ Where（在哪进化）四个维度把上百个工作装进一个坐标系。

## 形式化骨架

环境为 POMDP；agent 系统 Π=(Γ,{ψ},{C},{W})，即拓扑、模型、上下文、工具四元组；自进化策略 f(Π,τ,r)=Π′，目标是任务序列上累计效用最大化。操作性定义划三条准入线：更新必须**经验依赖**（由自身轨迹/反馈驱动）、必须产生**持久的策略改变**（排除一次性指令跟随）、必须含**自主探索**成分（排除静态蒸馏流水线）。作者自知边界松，明说从 proto-evolution（反思式 prompting）到 strong self-evolution（全自主诊断重构）全谱收录。

## 四维拆解与本仓库的格点对位

**What（四大进化位点）**：模型（权重/经验）、上下文（记忆演化 + prompt 优化）、工具（创建/精通/选用）、架构（单 agent 结构 / 多 agent 拓扑）。本仓库工作的投影：DGM（报告 07）同时占架构与工具选用两格，并被称为该谱系"愿景终点"；MOSS（报告 08）与 SICA 同属源码级自改写；WikiSkill（报告 09）落在工具创建 + 经验记忆；Continual Harness（报告 11）四格全占——正是"harness 资产"在该分类下的形状。

**When（两种时机 × 三种范式）**：intra-test-time（就地针对当前任务变强，如 Reflexion、LADDER 的测试时 RL）vs inter-test-time（任务间隙消化轨迹，如 STaR、WebRL），各自再按 ICL/SFT/RL 展开。注意它与本调研免重置 vs 重置式之辨（报告 11）相近但不重合：CH 的 episode 内精炼是 intra，其 RL 共学习是 inter，而综述没有为"不重置"单设一轴。

**How（三代范式 + 三条横切轴）**：reward-based（文本/内部置信/外部/隐式四种信号）→ imitation（自生成/跨 agent 示范）→ population-based（DGM 档案进化、SPIN 与 Absolute Zero 的自博弈、EvoMAC 的多 agent 文本反传）。横切轴为 online/offline、on/off-policy、reward 粒度（结果/过程/混合）。EvoLM 式 rubric 共进化（报告 03）与 ECHO critic 共进化（报告 06）在此被拆散到 internal rewards 与 Model-Agent Co-Evolution 两处。

**Where（通用 vs 专域）**：通用助理靠记忆机制、课程驱动、模型-agent 共进化三招；专域覆盖编码/GUI/金融/医疗/教育。信息量最低的一章，近乎应用清单。

## 评估节：全文最有牙齿的部分

五目标（适应性/保持/泛化/效率/安全）× 三时域（静态/短程/长程终身）。三个判断值得抄录：**Retention 是最缺服务的维度**——绝大多数 benchmark 是 episodic、任务间状态重置，从构造上就测不到知识积累或退化，而这恰是自进化 agent 区别于静态系统之处；**没有任何 benchmark 追踪进化过程中的安全轨迹**（风险是否随自主探索累积）；Table 11 自认 apples-to-apples 比较目前不可行。综述另提出 self-directedness 三项申报（任务/课程来自谁、反馈信号来自谁、外部干预频率），并引 alignment faking 12%→78% 警示无监督进化。安全节命名了 misevolution（自训练遗忘安全对齐）与 Alignment Tipping Process（发现失配行为更高奖励后策略翻转），部署 checklist 包括：沙箱 + 静态扫描、不可变审计日志 + 可回滚版本、更新前在金标数据集上做安全验证、高危动作人审门。

## 局限与批判性阅读

- **图书馆学而非力学**。四维回答"进化发生在哪/何时/如何"，不回答本调研的核心问题"什么让进化不塌缩"。评估器共进化这条主线被肢解到 How 的 reward 来源与评估节的 self-directedness 两处，从未作为第一性问题提出；锚定纪律只以工程副产品（金标数据集、外部 reward、人审门）散落出现，没有被理论化为原则。
- **What 维度抹平了量级差**。"改 prompt"与"改自身源码"并列为同级位点；本调研的三层改进面（文本/权重/源码）按风险与能力增益分层，解释力更强。DGM 在综述表格里溢出到多个格子，恰好暴露组件式分类装不下"组件边界本身可被改写"的系统。
- **准入线太松导致稀释**。proto 到 strong 全收，Reflexion 与 DGM 同框，self-evolving 一词的区分度被摊薄——这是作者自己承认并选择的代价。
- **reward overoptimization 被降格为未来工作**。misevolution、ATP、记忆层 reward hacking 都点到了，却放在第 8 章展望而非组织轴；对照本调研"评估器塌缩是主要死因"的判断，综述的病理学是清单式的，不是机制式的。
- 全文无定量元分析，权威性来自覆盖面而非证据强度。

## 与本调研的连线

- **对 01 Weng 总纲**：两套坐标系互补。Weng 的 harness 阶梯是能力深度轴（改上下文→改代码→种群搜索），综述是广度普查，Weng 第四级在综述里只是 Architecture 的一个叶节点。查地图用综述，判断哪一格重要仍需阶梯。
- **对 05 Who Grades the Grader**：综述的 self-directedness 三项申报是锚定纪律的"申报版"——它要求披露锚在哪，但不要求锚存在。WGtG 的规范性主张（评估器不得参与进化）比综述的透明性主张强一级。
- **对 11 Continual Harness**：综述评估节"episodic reset 从构造上测不到知识积累"正是 CH 免重置论证的评估侧镜像；其 long-horizon 协议（状态全持久、FGT/BWT 遗忘指标、Cost-per-Gain、定期保留探针）就是 CH 类系统需要的成绩单格式。一个造系统、一个造尺子，合读价值高于单读。
- **对 07 DGM / 08 MOSS**：综述安全 checklist（审计日志、版本回滚、更新前金标验证）与 MOSS 的失败重放 + 门控几乎逐条对应，说明工业最佳实践已收敛；DGM 的档案 + novelty 选择被正确归入 population-based——种群多样性正是免重置路线（报告 11）为"在故障现场修"而放弃的东西，两者构成一对取舍对偶。
- **对 10 汇总**：综述可作为 10 号报告三层改进面论点的压力测试——What 维度表明社区默认组件分类而非层级分类；而本调研坚持层级分类的理由（风险与能力随层级跃迁）在综述安全节里反而得到旁证：源码级与工具级的风险条目远多于 prompt 级。
