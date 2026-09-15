# Awesome RSI 阅读网站

线上入口：https://asimfish.github.io/awesome_rsi/

- README 的全部 14 个章节均有网页版本，并提供完整导览。
- `reports/*.md` 全量生成长文阅读页，目录数量从文件统计。
- 论文目录按原有 15 个分类浏览，逐条检索并显示匹配数量；解读目录支持全文检索。
- 长文提供桌面侧栏目录、手机折叠目录、阅读进度、预计阅读时间、字号切换和深色模式。
- 中英文 PDF 链接到仓库原始文件，不重复打包大文件。
- `/bytedance/` 使用统一的长文阅读界面；原芯片首页归入 `/chip/`，已有资源和深层页面保留，并提供返回全站入口。

## 构建

```bash
python -m pip install -r website/requirements.txt
python website/build.py /tmp/rsi-site /path/to/existing-pages-checkout
python website/verify.py /tmp/rsi-site
```

第三个参数指向现有 `gh-pages` 检出目录，用于保留已发布的芯片专题。新站应先准备该目录再构建。输出为纯静态 HTML/CSS/JS，无服务器接口或构建时远程内容抓取。正文修改后重新构建即可同步，不需要逐篇维护 HTML。

可选浏览器检查需安装 `playwright`，并提供 `/usr/bin/google-chrome`。启动静态服务器后运行：

```bash
python website/check_reading.py http://localhost:8000/
python website/check_home_routes.py http://localhost:8000/
```

检查覆盖桌面与手机目录、页面溢出、字号、主题保存、逐条检索，以及旧芯片锚点不会改变首页内容。

## 发布

先提交并推送源文件，再将构建输出复制到 `gh-pages` 的独立 worktree，检查差异后提交并推送。不要清空发布目录：其中可能有独立维护的专题。发布后核实首页、论文检索、代表性解读和两个专题均可访问。

全景综述固定地址：https://asimfish.github.io/awesome_rsi/overview.html 。首页不再根据旧芯片锚点自动跳转；芯片专题始终从 `/chip/` 进入。
