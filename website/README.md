# Awesome RSI 阅读网站

线上入口：https://asimfish.github.io/awesome_rsi/

- README 的全部 14 个章节均有网页版本，并提供完整导览。
- `reports/*.md` 全量生成长文阅读页，目录数量从文件统计。
- 论文目录按原有 15 个分类浏览，支持分类全文检索；解读目录支持标题与摘要检索。
- 中英文 PDF 链接到仓库原始文件，不重复打包大文件。
- 保留 `/bytedance/` 博客；原芯片首页归入 `/chip/`，已有资源和深层页面保留。

## 构建

```bash
python -m pip install -r website/requirements.txt
python website/build.py /tmp/rsi-site /path/to/existing-pages-checkout
python website/verify.py /tmp/rsi-site
```

第三个参数指向现有 `gh-pages` 检出目录，用于保留已发布的芯片专题。新站应先准备该目录再构建。输出为纯静态 HTML/CSS/JS，无服务器接口或构建时远程内容抓取。正文修改后重新构建即可同步，不需要逐篇维护 HTML。

## 发布

先提交并推送源文件，再将构建输出复制到 `gh-pages` 的独立 worktree，检查差异后提交并推送。不要清空发布目录：其中可能有独立维护的专题。发布后核实首页、论文检索、代表性解读和两个专题均可访问。

全景综述固定地址：https://asimfish.github.io/awesome_rsi/overview.html 。首页不再根据旧芯片锚点自动跳转；芯片专题始终从 `/chip/` 进入。
