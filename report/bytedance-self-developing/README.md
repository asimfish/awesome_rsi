# 字节 Seed × TokenWave：Self-Developing Agents 专题

[在线博客](https://asimfish.github.io/awesome_rsi/bytedance/) · [本地页面](index.html) · [三篇合读](research.md) · [官方项目页](https://self-developing-agents.github.io/)

本专题集中整理 Aspire、S³Gym、HarnessDev。作者团队还包括高校及其他合作机构，具体以各篇论文署名为准。研究对象依次是目标形成、经验学习和持久化 harness 改进。它们是三个独立的评测研究，不能把不同实验拼成一套已验证的端到端 RSI 系统。

| 论文 | 问题 | 英文 | 中文 |
|---|---|---|---|
| [Aspire](https://arxiv.org/abs/2608.31111) | 模糊目标怎样变成有效的学习目标 | [23 页](../../papers/en/2608.31111_Aspire.pdf) | [23 页](../../papers/zh/2608.31111_Aspire_zh.pdf) |
| [S³Gym](https://arxiv.org/abs/2608.31100) | 自测、自评怎样改善后续决策 | [25 页](../../papers/en/2608.31100_S3Gym.pdf) | [25 页](../../papers/zh/2608.31100_S3Gym_zh.pdf) |
| [HarnessDev](https://arxiv.org/abs/2609.01437) | 自建与迭代的 harness 能否泛化 | [41 页](../../papers/en/2609.01437_HarnessDev.pdf) | [41 页](../../papers/zh/2609.01437_HarnessDev_zh.pdf) |

网页无需构建或联网即可浏览，外部原文链接除外。页面中的实验结果为论文报告值，不是本地复现；中译保留公式、部分图表文字及提示词/代码块的原文。

## 维护博客

正文来源为 `research.md`，运行 `python build_blog.py` 生成 `index.html`（依赖 `Markdown` 包）。样式与交互分别位于 `blog.css`、`blog.js`。发布时将这三个网页文件复制到 GitHub Pages 的 `gh-pages` 分支 `bytedance/` 目录；保留已有站点根目录。
