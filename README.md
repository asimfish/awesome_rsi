# SILICON LOOP

公开网站：[https://asimfish.github.io/awesome_rsi/scenes.html](https://asimfish.github.io/awesome_rsi/scenes.html)（GitHub Pages，无需登录）。

中文 RSI × 芯片设计研究面板。建议通过 HTTP 或公开站点访问；实时记录由独立实验进程生成，页面只读展示。

- `live/`：两轮真实模型实验、形式/综合/时序日志、历史进度、复跑代码归档与结果说明。
- `index.html` / `assets/`：响应式深浅主题界面、设计过滤、指标对比、机制播放、加法器输入实验。
- `research.md`：来源明确的研究报告与复现边界。
- `data/paper-results.json`：Dr. RTL v2 表 2 的 20 行数据，未经独立 EDA 复现。
- `data/local-experiment.json`：独立 Python 穷举验证结果。
- `experiments/verify_adders.py`：仅依赖标准库的实验脚本。

本地预览：`python3 -m http.server 8765 --directory report/chip-rsi`（从仓库根目录运行）。

复跑实验后，用 `window.LOCAL_DATA = <JSON内容>;` 同步 `data/local-data.js`；该文件让双击 HTML 时无需跨域 fetch。论文 JSON 与 `data/paper-data.js` 同理。

实时研究区展示真实模型候选与工具反馈，已完成两轮共 10 个候选。模型优胜 ADP 比原始基线降低 9.238%，延迟降低 18.442%、面积增加 11.285%；RTL 与综合网表等价证明、独立复跑均通过。

[本轮结果与局限](live/results.md) · [代码与证据归档](live/research-bundle.zip)

论文数据、布尔演示与真实 EDA 实验分别标注。芯片图和机制播放仍是概念示意。页面每 30 秒读取真实状态，实验停止后显示已结束。页面本身不调用模型或 EDA。
