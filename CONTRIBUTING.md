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

用 [super_translate](https://github.com/asimfish/super_translate) 生成（保版式、冻结公式图表），输出到 `papers/zh/<同名>_zh.pdf`。提交前用 `pypdf` 核对页数与原版一致、抽样页含 CJK 文本。

## 添加精读报告

- 文件名 `reports/<两位编号>_<slug>.md`，编号顺延。
- 结构参照 `reports/11_continual_harness.md`：信息表 → 一句话核心主张 → 方法拆解 → 关键数字 → 局限与批评 → 与本调研的连线（至少 3 条，引用具体报告编号）。
- 写盘时用 shell heredoc 而非编辑器批量粘贴——本仓库曾因工具链 CJK 损坏重写过全部报告；提交前运行：

   ```bash
   python3 -c "import re,glob;[print(f) for f in glob.glob('reports/*.md') if chr(0xFFFD) in open(f,encoding='utf-8').read() or re.search(r'[\u4e00-\u9fff]\?[\u4e00-\u9fff]', open(f,encoding='utf-8').read())]"
   ```

## 更新计数与 slides

新增报告或 PDF 后，同步更新：README 顶部徽章、§7 目录树、§14 对照矩阵（如适用）、`awesome_rsi_slides.html` 的封面/材料地图/导览页计数，并重新生成 `awesome_rsi_slides.pdf`（Chrome headless `--print-to-pdf`）。

## 提交信息

`[scope/op]: 标题`，正文写 What / Why。示例：`[repo/feat]: 加入 X 论文与解读报告 NN`。
