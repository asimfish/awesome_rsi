# RSI 算子优化

目标：与芯片研究并行，在独立个人面板展示真实 GPU 算子优化、正确性和计时结果。

本轮：KernelBench 来源 ReLU / Softmax / minGPT GELU，冻结上游 forward，使用自定有界 shape；非完整官方分数。GPU 1，RTX 5090；共享服务器，保留负载记录。

协议：先 PyTorch profiler 和 eager / torch.compile 基线，再朴素 Triton 与单变量 block-size / warp 改动；每候选先正确性，再 warmup 和交替顺序 CUDA event 配对计时，7组，每组30操作×10次图回放，中位数与分布；独立重复验证。测试随机种子、边界尺寸、负数/零/大值与输入不被修改。仅报告固定 FP32 / contiguous 范围。

预算：3个算子、每个最多3个手工/助手编写候选，本轮不调用外部模型API、不改验证标准。单子进程10分钟，GPU内存预算1.5GiB，GPU1使用；若资源不足或抖动大则记录为不可确证。

里程碑：K1 固定来源与基线；K2 正确性及性能反馈迭代；K3 独立复测；K4 部署独立面板、代码日志下载、两项目入口与持续状态采集。

Current Focus: K1–K3 完成；K4 面板发布与验收。PyTorch 2.7.0+cu128 / Triton 3.3.0 / sm120。不能据此宣称 RSI 因果有效或官方KernelBench排名。

校准调整：v1 主机逐次发射计时抖动超过15%，所有结果保留但不作为优化证据。调优前冻结 v2 CUDA Graph 30操作×10次回放×7组轮换计时；不包含Python发射/分配开销。
