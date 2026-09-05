# Contributing to awesome_rsi

欢迎补充新论文、修正数字或改进解读。请遵守以下约定，保证仓库内所有数字都有出处、所有链接都可点。

## 添加论文

1. 在 `README.md` 对应分节（§3 按五侧分类，§4 前沿追踪按主题分组）追加条目，格式与 [awesome-ml4co](https://github.com/Thinklab-SJTU/awesome-ml4co) 一致：

   ```
   N. **标题.** 来源, 年份\. [paper](arXiv 链接), [code](可选), [PDF-en](papers/en/<id>_<Short>.pdf), [PDF-zh](可选), [解读](可选)
   _作者_ — 一句话定位（含最关键的一个数字）
   ```

2. 英文 PDF 放入 `papers/en/`，命名 `<arXiv id>_<ShortName>.pdf`；起源类经典放 `papers/classics/`，命名 `<年份>_<作者>_<Short>.pdf`。
3. 一句话定位里的数字必须来自论文正文或表格，不接受来自二手解读的数字。

## 添加中文翻译

用 [super_translate](https://github.com/asimfish/super_translate) 生成（保版式、冻结公式图表），输出到 `papers/zh/<同名>_zh.pdf`。批量翻译参照 `scripts/translate_batch5.sh`（三条可并行队列，跳过已存在的目标文件，缓存在 `/tmp/rsi_translate_cache/`）。提交前用 `pypdf` 核对页数与原版一致、抽样页含 CJK 文本（`pypdf` 对 CID 字体会报大量 warning，需 `warnings.filterwarnings('ignore')`，不代表文件损坏）。

## 添加深度解读

- 文件名 `reports/<两位编号>_<slug>.md`，编号顺延。
- **统一七节结构**（参照 `reports/05_who_grades_the_grader.md` 或 `reports/13_meta_harness.md`）：

  | 节 | 内容要求 |
  |---|---|
  | 引用块头部 | 标题 / arXiv 号与日期 / 作者机构 / 代码 / 归档路径 |
  | 1. 一句话定位 | 一段话说清问题、方法、最关键的 3–5 个数字、在谱系中的位置——读者只读这一段也能带走结论 |
  | 2. 要解决的问题 | 论文的出发点与结构性约束，不是摘要复述 |
  | 3. 为什么此前做不通 | **表格**：已有路线 / 有什么 / 缺什么，最后一行点出关键缺口 |
  | 4. 方法机制 | 分小节拆机制；公式、算法步骤、设计选择的理由 |
  | 5. 实验结果全景 | **表格化**主结果与消融；每个数字可回溯到论文表号 |
  | 6. 局限 | 编号列表，作者自认 + 本调研补充，区分标注 |
  | 7. 意义与位置 | 与本仓库其他报告的连线（≥ 4 条，引用具体报告编号），说明它改变了哪个 insight |

- 篇幅 2000–5000 中文字；数字必须来自论文正文或表格。
- 综述类报告可把 2–3 节改为"综述要回答的问题 / 与其他综述的分工"；合评类报告按"共同问题 → 分歧 → 共识与反面数据"组织，但保留七节编号。
- 写盘时用 shell heredoc 而非编辑器批量粘贴——本仓库曾因工具链 CJK 损坏重写过全部报告；提交前运行：

   ```bash
   python3 -c "import re,glob;[print(f) for f in glob.glob('reports/*.md') if chr(0xFFFD) in open(f,encoding='utf-8').read() or re.search(r'[\u4e00-\u9fff]\?[\u4e00-\u9fff]', open(f,encoding='utf-8').read())]"
   ```

## 更新计数与 slides

新增报告或 PDF 后，同步更新：README 顶部徽章、§7 目录树、§14 对照矩阵（如适用）、`report/awesome_rsi_slides.html` 的封面/材料地图/导览页计数并重新生成 `report/awesome_rsi_slides.pdf`（Chrome headless `--print-to-pdf`）；运行 `python3 scripts/build_full_report.py --pdf` 重建全文报告；若新增论文属于新家族或新子类，同步更新 `scripts/make_figures.py` 的 `WORKS` / `TAXONOMY` 并重新生成两图。

## 提交信息

`[scope/op]: 标题`，正文写 What / Why。示例：`[repo/feat]: 加入 X 论文与解读报告 NN`。
