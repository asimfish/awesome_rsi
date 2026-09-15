# Performance Log

Calibration v1: initial GELU naive kernel passed 18 correctness cases, but host-launch timed trials showed >15% variability. Archived in runs/kernel-001/gelu/naive. These values are not accepted optimization evidence. Profiler identified 8 eager CUDA launches per call (mul/add/pow/tanh) with intermediate memory traffic.

Before any tuning, freeze v2 protocol: capture the exact same function 30 times in a CUDA Graph; warm graph, time 10 replays per sample with CUDA events; 7 rotated-order paired samples vs both eager and torch.compile. This removes Python launch gaps. Graph timing excludes allocation and host overhead; same protocol for all candidates and references. Retain v1 and v2 separately.


## kernel-002 已完成：12 次评估，24 组形状测量

本轮顺序：三个朴素基线 → pointwise BLOCK 128→256→1024，Softmax warps 4→8→16（均保持其余代码不变）→ 各算子按跨形状 speedup 几何均值选择一个候选，在独立进程复测。选择使用调优形状，复测不是隐藏测试集。每次评估 18 组正确性用例、负对照及两个计时形状均通过。

| 算子 | 候选 | 形状 | 中位 µs | 对 eager | 对 compile | 波动 |
|---|---|---|---|---|---|---|
| relu | naive | 1024 × 1024 | 4.680 | 0.458× | 0.439× | 低 |
| relu | naive | 4096 × 4096 | 96.114 | 1.043× | 1.056× | 高 |
| softmax | naive | 256 × 1024 | 1.463 | 1.555× | 1.052× | 低 |
| softmax | naive | 1024 × 4096 | 7.930 | 1.744× | 1.415× | 低 |
| gelu | naive | 1024 × 1024 | 4.778 | 4.345× | 0.473× | 高 |
| gelu | naive | 2048 × 4096 | 37.488 | 5.195× | 0.550× | 高 |
| relu | block256 | 1024 × 1024 | 2.736 | 0.776× | 0.753× | 低 |
| relu | block256 | 4096 × 4096 | 97.071 | 1.020× | 1.051× | 高 |
| relu | block1024 | 1024 × 1024 | 2.055 | 1.033× | 0.999× | 低 |
| relu | block1024 | 4096 × 4096 | 95.835 | 1.038× | 1.045× | 低 |
| gelu | block256 | 1024 × 1024 | 2.871 | 6.483× | 0.796× | 低 |
| gelu | block256 | 2048 × 4096 | 19.874 | 10.163× | 1.026× | 高 |
| gelu | block1024 | 1024 × 1024 | 2.536 | 6.917× | 0.899× | 低 |
| gelu | block1024 | 2048 × 4096 | 19.038 | 10.731× | 1.067× | 低 |
| softmax | warps8 | 256 × 1024 | 1.501 | 1.501× | 1.004× | 低 |
| softmax | warps8 | 1024 × 4096 | 7.964 | 1.784× | 1.409× | 高 |
| softmax | warps16 | 256 × 1024 | 1.639 | 1.374× | 0.920× | 低 |
| softmax | warps16 | 1024 × 4096 | 6.909 | 1.996× | 1.636× | 低 |
| relu | retest | 1024 × 1024 | 2.057 | 1.031× | 1.000× | 低 |
| relu | retest | 4096 × 4096 | 97.500 | 0.989× | 1.001× | 高 |
| softmax | retest | 256 × 1024 | 1.644 | 1.371× | 0.917× | 低 |
| softmax | retest | 1024 × 4096 | 6.943 | 1.894× | 1.510× | 低 |
| gelu | retest | 1024 × 1024 | 2.538 | 6.919× | 0.904× | 低 |
| gelu | retest | 2048 × 4096 | 18.611 | 10.483× | 1.163× | 高 |

### 结论与边界

- Softmax 选中 warps16。大形状复测对 compile 约1.51×，对 eager 约1.89×；小形状对 compile 约0.92×，不能称为全形状优胜。
- GELU 融合减少 eager 的8次GPU算子调用；BLOCK1024大幅缩小与compile差距。大形状复测约1.16×对compile，但波动较大；小形状约0.90×，未超过compile。
- ReLU BLOCK1024基本追平compile；大形状复测抖动，没有可靠加速结论。
- 波动标志：eager/compile/candidate任一7组计时的标准差/中位数≥15%则标高；不是置信区间或显著性检验。原始7组读数和GPU共享负载快照完整保留。
- 本轮验证了反馈驱动的候选改进流程，尚未证明递归自改进的因果收益；无模型自主搜索、权重更新或官方KernelBench全榜成绩。

下一步：扩展独立尺寸验证、制定形状分派方案，再做固定预算下的有/无经验记忆搜索对照。当前实验已停止，分钟同步继续运行。
