"""Build the standalone reading page. Requires Python-Markdown (pip install markdown)."""
from pathlib import Path
import re
import markdown
root = Path(__file__).resolve().parent
source = (root / 'research.md').read_text()
source = source.split('## 1.', 1)[1]
source = '## 1.' + source
source = re.sub(r'\]\(../../reports/([^)]*)\)', r'](https://github.com/asimfish/awesome_rsi/blob/main/reports/\1)', source)
md = markdown.Markdown(extensions=['tables', 'toc'], extension_configs={'toc': {'slugify': lambda value, sep: 'section-' + value.split('.')[0].strip() if re.match(r'^\d+\.', value) else re.sub(r'\W+', '-', value)}})
body = md.convert(source)
body = body.replace('<table>', '<div class="table-scroll"><table>').replace('</table>', '</table></div>')
links = []
for name, slug, aid, pages in [('Aspire','Aspire','2608.31111',23),('S³Gym','S3Gym','2608.31100',25),('HarnessDev','HarnessDev','2609.01437',41)]:
 base = 'https://raw.githubusercontent.com/asimfish/awesome_rsi/main/papers/'
 links.append(f'<div class="paper"><strong>{name}</strong><span>{pages} 页</span><a href="https://arxiv.org/abs/{aid}">原文</a><a href="{base}zh/{aid}_{slug}_zh.pdf">中文 PDF ↗</a></div>')
html = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="字节 Seed 与 TokenWave 的 Aspire、S³Gym、HarnessDev 三篇合读：目标形成、经验学习与执行框架改进，含实验对照与中文论文。"><title>自我改进的三个关口 · RSI 研究札记</title><link rel="stylesheet" href="blog.css"></head><body>
<a class="skip" href="#article">跳到正文</a><div class="progress" aria-hidden="true"></div><header class="topbar"><a class="brand" href="#">RSI <span>研究札记</span></a><div><a href="https://asimfish.github.io/awesome_rsi/">芯片专题</a><button id="theme" aria-label="切换深色模式">深色阅读</button></div></header><div class="layout"><aside><div class="eyebrow">ON THIS PAGE</div><nav aria-label="文章目录">TOC</nav><a class="back" href="#downloads">↓ 论文与中译</a><p class="sidebar-note">三个独立基准<br>一条共同问题线：<br>改进怎样得到验证？</p></aside><main id="article"><div class="hero"><div class="eyebrow">专题 01 / SELF-DEVELOPING AGENTS</div><h1>自我改进的<br><em>三个关口</em></h1><p class="dek">字节三篇合读：从选对目标，到学会经验，再到保留有效的系统改进。</p><p class="meta">ByteDance Seed × TokenWave 等合作团队 · 论文 v1<br>约 10 分钟阅读 · <a href="https://self-developing-agents.github.io/">官方项目页 ↗</a></p></div><div class="takeaway"><span>先读这个</span><p>能够完成更新循环，不等于获得可靠的能力提升。三篇论文把这段距离拆成了三个可以分别测量的问题。</p></div><div class="route" aria-label="三篇研究分工"><div><small>01 · 目标形成</small><b>Aspire</b><span>改进什么？</span></div><div><small>02 · 经验学习</small><b>S³Gym</b><span>学到了什么？</span></div><div><small>03 · 系统改进</small><b>HarnessDev</b><span>留下了什么？</span></div></div><section id="downloads"><h2>论文与中文翻译</h2>PAPERS<p class="fine">中文 PDF 保留原页面尺寸与页数。公式、部分图表文字以及提示词／代码块保留原文。</p></section><div class="article-body">BODY</div><section class="closing"><h2>继续阅读</h2><p>这是一份基于论文的研究解读，实验数字为作者报告值，未进行本地复现。作者机构以各篇署名为准。</p><a href="https://github.com/asimfish/awesome_rsi/tree/main/report/bytedance-self-developing">查看原始笔记与来源 →</a></section><footer>RSI 研究札记 · 从结果追问改进机制<br><a href="#">返回顶部 ↑</a></footer></main></div><script src="blog.js"></script></body></html>'''
html = html.replace('TOC', md.toc).replace('PAPERS', ''.join(links)).replace('BODY', body)
(root / 'index.html').write_text(html)
