# 解读报告 25 · RHO：在黑暗中进化——无任何外部评分的 harness 优化

| 项目 | 内容 |
|---|---|
| arXiv | 2606.05922 v3（2026-06 首发，v3 2026-08-29） |
| 作者 | Wenbo Pan, Shujie Liu, Chin-Yew Lin, Jingying Zeng, Xianfeng Tang, Xiangyang Zhou, Yan Lu, Xiaohua Jia（香港城市大学 + 微软亚洲研究院） |
| 代码 / 项目页 | github.com/wbopan/retro-harness · paper-rho.wenbo.io |
| 归档 | `papers/en/2606.05922_RHO.pdf` |
| 在调研中的位置 | 对"评估器瓶颈"最激进的回答：**不要外部评估器**，用组内相对信号替代——与 Who Grades the Grader（报告 05）的锚定路线、EvalCEGAR（报告 24）的锚驱动路线形成对极；也是全谱系唯一声称完全无标签的 harness 优化 |

## 一句话核心主张

harness 优化方法几乎都需要带 ground truth 的验证集，而部署场景里这种标注数据很难拿到。RHO（Retrospective Harness Optimization）只用过去的轨迹：从历史里选一个多样且困难的任务 coreset，并行重解，让 agent 用**自验证**（轨迹内）与**自一致性**（轨迹间分歧）诊断失败，生成候选 harness 更新，再用 agent 自己的**成对自偏好**选最优者。单轮优化把 SWE-Bench Pro 通过率从 **59% 提到 78%**，全程没有任何外部评分。

## 方法拆解（Algorithm 1，单轮）

**阶段 1 · coreset 选择。** 历史轨迹里大多是平凡任务，直接重放浪费预算。RHO 要求 coreset 同时困难且多样：用行列式点过程（DPP）核对轨迹排序，选出 k 条覆盖尽量多不同失败模式的轨迹。

**阶段 2 · 组 rollout 与自诊断。** 对 coreset 每个任务并行重解 G 次。两路信号：自验证——单条轨迹内部 agent 能否确认自己的结果；自一致性——G 条轨迹之间是否分歧（低一致性通常意味着任务对当前 harness 而言不稳定）。agent 据此写出改进指令 I_t，跨任务合并。

**阶段 3 · best-of-N harness 提案 + 自偏好选择。** harness 优化本身是随机的，即便输入信号有效也可能不涨。RHO 并行生成 N 个候选 harness，每个都在 coreset 上重跑得到新轨迹，然后对每个任务让 agent 把"新轨迹 vs 原 harness 的旧轨迹"做成对排序，跨任务聚合出偏好分，取最高者。整个过程不读任何 ground-truth 标签。

**harness 表面。** 编辑对象是 Skills + Tools：Skills 记录此前导致失败的 grader / 环境特异性（例如某个基准的验收习惯），Tools 是可执行的辅助程序（例如修复-验证工具）。

## 关键数字（Table 1，held-out 通过率，Codex 风格 CLI agent + GPT-5.5）

| 方法 | 编辑表面 | SWE-Bench Pro | Terminal-Bench 2 | GAIA-2 |
|---|---|---|---|---|
| Vanilla Codex | 无 | 0.59 | 0.71 | 0.29 |
| Dynamic Cheatsheet | Skills | 0.62 | 0.73 | 0.30 |
| ReasoningBank | Memory | 0.61 | 0.73 | 0.28 |
| Sleep-time Compute | Memory | 0.64 | 0.73 | 0.32 |
| **RHO** | Skills + Tools | **0.78（+0.19）** | **0.76（+0.05）** | **0.37（+0.08）** |

三个记忆/技能类基线的增益都在 +0.05 以内，RHO 在 SWE-Bench Pro 上一轮 +0.19。论文的行为分析显示优化后的 harness 确实针对了此前的失败模式，并在长时程会话中维持更高准确率。

## 局限与批评（作者自列五条 + 本调研两条）

作者自列：(1) 组 rollout 要求环境可干净重置、容忍重复尝试——一次性或不可逆任务不在覆盖范围；(2) 预设 agent 能力的相当部分由可编辑 harness 中介；(3) 单一骨干与框架（GPT-5.5 Codex CLI），迁移性未验证；(4) **只评估了单轮**，不声称多轮增益会累积甚至保持单调；(5) 优化后的 harness 适应了各自的基准环境（例如针对某基准的修复-验证工具）。

本调研补充：

6. **自偏好是已知偏差源**：LLM judge 的自偏好、位置、冗长偏差在文献里被反复记录（EvalCEGAR 报告 24 开篇即引），RHO 把这个偏差源当作唯一选择信号——单轮有效不等于它不会在多轮里放大成系统性漂移。作者自己的局限 (4) 恰好把这个最关键的问题留给了未来。
7. **"无外部评分"的边界值得追问**：Skills 里记录的是"grader 特异性"——也就是说 harness 学到的部分内容是**关于评估器的知识**。这在部署上合理，在方法论上意味着增益里混有"更懂考官"的成分；held-out split 能隔离任务泄漏，隔离不了 grader 泄漏。

## 与本调研的连线

1. **对报告 05 锚定纪律的最强反例候选**：Who Grades the Grader 说无锚则塌缩与进化不可区分，RHO 说单轮 +0.19 不需要锚。两者并不矛盾——WGtG 的结论是关于**多轮**动态的，RHO 只测了单轮；RHO 的多轮实验将是对锚定纪律最直接的检验。
2. **与 AutoSaddler（报告 16）的关键对照**：AutoSaddler 的消融显示去掉 dev 集泛化门后自动优化跌破未优化基线（50.6 vs 53.0），RHO 则宣称完全不用 dev 集也能 +0.19——差异可能在 RHO 的 best-of-N 自偏好选择起了"软泛化门"的作用，也可能在单轮与多轮的区别。这是当前谱系里最需要被复现裁决的分歧。
3. **与 EvalCEGAR（报告 24）的对极**：同一时期、同一问题（评估器稀缺），两种答案——最大化利用稀缺的锚 vs 完全不用锚。就实用性而言 RHO 的部署门槛更低；就可审计性而言 EvalCEGAR 的每个算子都能被读和证伪，RHO 的自偏好判断则是黑箱。
4. **对报告 10 insight 2（无锚不进化）的压力测试**：如果 RHO 的多轮结果保持单调，insight 2 需要修正为"无锚不**可验证地**进化"；如果不保持，它就是 insight 2 最干净的实证。

