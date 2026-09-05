# -*- coding: utf-8 -*-
"""Build the consolidated full-text report: all reports/*.md -> report/awesome_rsi_full_report.html (+ PDF via Chrome).
Usage: python3 scripts/build_full_report.py [--pdf]
"""
import subprocess, pathlib, re, sys, glob, datetime

REPO = pathlib.Path(__file__).resolve().parent.parent
files = sorted((REPO/"reports").glob("*.md"))

CSS = """
@page{size:A4;margin:22mm 18mm 20mm 18mm}
body{font-family:"PingFang SC","Hiragino Sans GB","Noto Sans CJK SC",sans-serif;color:#1a2332;line-height:1.75;font-size:10.5pt;max-width:none;margin:0}
h1{font-size:17pt;color:#3b1f0e;border-bottom:2.5px solid #c2410c;padding-bottom:8px;margin:0 0 14px;line-height:1.4;page-break-before:always}
h1.first{page-break-before:avoid}
h2{font-size:13pt;color:#c2410c;margin:20px 0 8px}
h3{font-size:11pt;color:#1a2332;margin:14px 0 6px}
blockquote{border-left:3px solid #c2410c;background:#fdf4ee;padding:8px 14px;margin:10px 0;color:#5b4636;font-size:9.5pt}
blockquote p{margin:2px 0}
table{border-collapse:collapse;width:100%;font-size:9pt;margin:10px 0}
th{background:#3b1f0e;color:#fff;padding:5px 8px;text-align:left;font-weight:600}
td{border:1px solid #e0d3c8;padding:4.5px 8px;vertical-align:top}
tr:nth-child(even) td{background:#faf6f2}
code{background:#f3ede8;padding:1px 5px;border-radius:3px;font-size:9pt;font-family:Menlo,monospace}
strong{color:#3b1f0e}
li{margin-bottom:3px}
p{margin:6px 0}
hr{border:none;border-top:1px solid #e8ddd4;margin:16px 0}
a{color:#c2410c;text-decoration:none}
.cover{page-break-after:always;padding-top:170px;text-align:left}
.cover .t1{font-size:26pt;font-weight:700;color:#3b1f0e;line-height:1.35;margin-bottom:14px}
.cover .t2{font-size:13pt;color:#5b4636;margin-bottom:40px;line-height:1.7}
.cover .meta{font-size:10.5pt;color:#7a6a5e;line-height:2.1}
.toc{page-break-after:always}
.toc h1{page-break-before:avoid}
.toc ol{font-size:11pt;line-height:2.2;color:#1a2332;padding-left:1.4em}
@page fig1{size:A3 landscape;margin:12mm}
.figpage1{page:fig1;page-break-before:always;page-break-after:always}
.figpage2{page-break-before:always;page-break-after:always}
.figpage1 svg,.figpage2 svg{width:100%;height:auto}
.figcap{font-size:9.5pt;color:#5b4636;margin-top:6px}
"""

toc_titles, bodies = [], []
for i, f in enumerate(files):
    r = subprocess.run(["pandoc", str(f), "-f", "gfm", "-t", "html"], capture_output=True, text=True)
    html = r.stdout
    first_line = f.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip()
    toc_titles.append(first_line)
    if i == 0:
        html = html.replace("<h1", '<h1 class="first"', 1)
    # relative links inside reports (papers/..., reports/...) -> GitHub blob links
    html = re.sub(r'href="(?!http|#)(papers/[^"]+|reports/[^"]+|assets/[^"]+)"', r'href="https://github.com/asimfish/awesome_rsi/blob/main/\1"', html)
    bodies.append(f'<article id="ch{i+1}">{html}</article>')

toc_html = "".join(f"<li>{t}</li>" for t in toc_titles)

def _svg(path):
    s = (REPO/path).read_text(encoding="utf-8")
    return re.sub(r'<svg xmlns="http://www.w3.org/2000/svg" width="\d+" height="\d+"', '<svg xmlns="http://www.w3.org/2000/svg"', s, count=1)

n_en = len(glob.glob(str(REPO/"papers/en/*.pdf"))); n_zh = len(glob.glob(str(REPO/"papers/zh/*.pdf"))); n_cl = len([f for f in glob.glob(str(REPO/"papers/classics/*.pdf")) if not f.endswith("_zh.pdf")]); n_clzh = len(glob.glob(str(REPO/"papers/classics/*_zh.pdf")))
fig_html = f"""<div class="figpage1">{_svg('assets/fig1_timeline.svg')}<div class="figcap">图 1 · 71 项工作的时间线：按十个家族分泳道、按 arXiv 首版年月定位（非 arXiv 材料取发布月近似），★ 为核心精读材料；1965-2014 思想史与 2023-2026 工程爆发之间断轴。</div></div>
<div class="figpage2">{_svg('assets/fig2_taxonomy.svg')}<div class="figcap">图 2 · 递归自改进的分类体系：七个一级维度、37 个子类；"锚在哪"是本仓库独有的主轴。同一工作可出现在多个维度。</div></div>"""

today = datetime.date.today().isoformat()
doc = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>递归自改进（RSI）调研全文报告</title><style>{CSS}</style></head><body>
<div class="cover">
  <div class="t1">递归自改进（Recursive Self-Improvement）<br>调研全文报告</div>
  <div class="t2">从 Good 1965 的智能爆炸猜想到 2026 年的评估器战争与 harness 工业化：{len(files)} 份精读报告合订<br>核心论点——执行已经自动化，品味正在被编译，锚是最后的手工业</div>
  <div class="meta">构建日期：{today}（首版 2026-08-31）<br>材料范围：Lilian Weng《Harness Engineering for Self-Improvement》· Anthropic《When AI builds itself》· EvoLM · Red Queen Gödel Machine · Who Grades the Grader · ECHO · Darwin Gödel Machine · MOSS · WikiSkill · Continual Harness · A Survey of Self-Evolving Agents（TMLR）· Meta-Harness · Self-Harness · EnvHarness · AutoSaddler · MetaCaster · Prime Agent · iCoder · Metan · Co-Harness · Co-Evolution in Agentic Systems · Gödel Agent · SICA · EvalCEGAR · RHO · 技能进化红海五篇 · 安全治理五篇 · Self-Evolving Coding Agents 综述；前史：Good 1965 · Vinge 1993 · GISAI 2001 · Gödel Machine 2003 · Omohundro 2008 · Chalmers 2010 · IEM 2013 · Superintelligence 2014<br>配套材料：{n_en} 篇英文 PDF + {n_cl} 篇起源经典 · {n_zh + n_clzh} 篇中译 PDF（全部英文 PDF 均有中译，仅 Good 1965 扫描件除外） · 汇总 PPT（report/awesome_rsi_slides.html / .pdf）· 图 1 时间线 / 图 2 分类树（assets/）<br>仓库：github.com/asimfish/awesome_rsi</div>
</div>
<div class="toc"><h1 class="first" style="page-break-before:avoid">目录</h1><ol>{toc_html}</ol></div>
{fig_html}
{"".join(bodies)}
</body></html>"""

out = REPO/"report/awesome_rsi_full_report.html"
out.parent.mkdir(exist_ok=True)
out.write_text(doc, encoding="utf-8")
print("written:", out, len(doc.encode()), "bytes, chapters:", len(files))

if "--pdf" in sys.argv:
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    pdf = REPO/"report/awesome_rsi_full_report.pdf"
    subprocess.run(["timeout","-k","5","300",chrome,"--headless=new","--disable-gpu","--no-pdf-header-footer",f"--print-to-pdf={pdf}",f"file://{out}"], capture_output=True)
    print("pdf:", pdf, pdf.stat().st_size if pdf.exists() else "MISSING")
