"""Build the complete RSI reading site. Usage: python website/build.py OUTPUT_DIR"""
from pathlib import Path
import sys,re,html,posixpath,json,shutil
from urllib.parse import urlsplit,unquote
import markdown
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True)
BASE='https://github.com/asimfish/awesome_rsi/blob/main/'
RAW='https://raw.githubusercontent.com/asimfish/awesome_rsi/main/'
reports=sorted((ROOT/'reports').glob('*.md'))
readme=(ROOT/'README.md').read_text()
labels={1:'从这里开始',2:'核心阅读',3:'分类框架',4:'论文图谱',5:'解读目录',6:'洞察与开放问题',7:'术语、时间线与系统对照',8:'中文导读',9:'仓库与构建',10:'研究路线图',11:'相关资源',12:'更新记录',13:'引用本站',14:'说明与致谢'}
sections={int(m[1]):(m[2],m[3]) for m in re.finditer(r'^## (\d+)\. ([^\n]+)\n(.*?)(?=^## \d+\.|\Z)',readme,re.M|re.S)}
report_map={'reports/'+p.name:'reports/'+p.stem+'.html' for p in reports}
map_paths={**report_map,'README.md':'guide.html','report/awesome_rsi_slides.html':'slides.html','report/awesome_rsi_full_report.html':'full-report.html','report/bytedance-self-developing/index.html':'bytedance/','report/bytedance-self-developing/research.md':'bytedance/research.html','report/bytedance-self-developing/README.md':'bytedance/','report/chip-rsi/index.html':'chip/','report/chip-rsi/research.md':'chip/research.html'}
def slug(s,sep):
 return re.sub(r'[^\w\-\u4e00-\u9fff]','',s.lower().replace(' ','-'))
def target(href,source,page):
 if not href or href.startswith(('#','http:','https:','mailto:','data:')):return href
 part=urlsplit(href);path=unquote(part.path)
 # Existing reports use both repository-relative and file-relative links.
 resolved=path if path.startswith(('papers/','reports/','report/','assets/')) else posixpath.normpath(str(Path(source).parent/path))
 if resolved.startswith('report/chip-rsi/') and resolved not in map_paths:
  return posixpath.relpath(resolved.replace('report/chip-rsi/','chip/',1),posixpath.dirname(page) or '.')+('#'+part.fragment if part.fragment else '')
 if resolved in map_paths:
  dest=posixpath.relpath(map_paths[resolved],posixpath.dirname(page) or '.')
  if map_paths[resolved].endswith('/'):dest+='/'
  return dest+('#'+part.fragment if part.fragment else '')
 if resolved.startswith('assets/') and (ROOT/resolved).is_file():
  dst=OUT/resolved;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/resolved,dst)
  return posixpath.relpath(resolved,posixpath.dirname(page) or '.')
 if (ROOT/resolved).exists():return (RAW if resolved.endswith(('.pdf','.svg','.png','.jpg')) else BASE)+resolved+('#'+part.fragment if part.fragment else '')
 return BASE+resolved

def render(text,source,page):
 md=markdown.Markdown(extensions=['tables','fenced_code','toc','sane_lists'],extension_configs={'toc':{'slugify':slug}})
 soup=BeautifulSoup(md.convert(text),'html.parser')
 for node in soup.select('[href], [src]'):
  for attr in ['href','src']:
   if node.has_attr(attr):node[attr]=target(node[attr],source,page)
 if source == 'README.md' and page != 'guide.html':
  ids={n.get('id') for n in soup.select('[id]')}
  for a in soup.select('a[href^="#"]'):
   if unquote(a['href'][1:]) not in ids:
    a['href']='guide.html'+a['href']
 for node in soup.find_all('table'):
  wrap=soup.new_tag('div',attrs={'class':'table-scroll'});node.wrap(wrap)
 for node in soup.find_all('code'):
  text=node.get_text()
  if text.startswith('papers/') and text.endswith('.pdf') and (ROOT/text).is_file():
   a=soup.new_tag('a',href=RAW+text);a.string=text;node.replace_with(a)
 return str(soup),md.toc

def shell(title,body,page,toc='',kind='阅读',wide=False):
 prefix='../'*(len(Path(page).parts)-1)
 nav=[('index.html','首页'),('papers.html','论文'),('reports.html','解读'),('insights.html','洞察'),('topics.html','专题'),('resources.html','资源')]
 navhtml=''.join(f'<a href="{prefix}{u}"'+(' aria-current="page"' if page==u else '')+f'>{t}</a>' for u,t in nav)
 doc=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Awesome RSI：递归自改进研究的论文、中文解读、分类与专题。"><title>{html.escape(title)} · RSI 研究札记</title><link rel="stylesheet" href="{prefix}site.css"></head><body><a class="skip" href="#content">跳到正文</a><div id="progress"></div><header class="topbar"><a class="brand" href="{prefix}index.html">RSI <span>研究札记</span></a><nav aria-label="全站导航">{navhtml}</nav><button id="theme" aria-label="切换深色模式">深色阅读</button></header><div class="layout {'wide' if wide else ''}"><aside><div class="eyebrow">{kind}</div>{toc or '<p>从论文到方法，<br>从方法到评估。</p>'}<div class="aside-links"><a href="{prefix}guide.html">完整仓库导览 ↗</a><a href="https://github.com/asimfish/awesome_rsi">GitHub 源码 ↗</a></div></aside><main id="content">{body}<footer>RSI 研究札记 · 根据 awesome_rsi 仓库生成<br>论文结论与研究判断以各篇来源及实验边界为准。<a href="#">返回顶部 ↑</a></footer></main></div><script src="{prefix}site.js"></script></body></html>'''
 dest=OUT/page;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(doc)

def article(title,text,source,page,kind='长文阅读',extra=''):
 body,toc=render(text,source,page)
 shell(title,f'<div class="eyebrow">{kind}</div>{body}{extra}',page,toc,kind)

cards=[]
for i,p in enumerate(reports):
 text=p.read_text();title=text.splitlines()[0].lstrip('# ').strip()
 excerpt=re.split(r'^## .*\n',text,flags=re.M)[1] if '## ' in text else text
 excerpt=re.sub(r'[#*_>`\[\]]','',excerpt).strip().split('\n\n')[0][:155]
 page=report_map['reports/'+p.name]
 links=''
 if i:links+=f'<a href="{reports[i-1].stem}.html">← 上一篇</a>'
 if i+1<len(reports):links+=f'<a href="{reports[i+1].stem}.html">下一篇 →</a>'
 article(title,text,'reports/'+p.name,page, '解读 / '+p.name[:2],f'<div class="prevnext">{links}</div>')
 cards.append(f'<article class="search-card" data-search="{html.escape(title+" "+excerpt,quote=True)}"><div class="eyebrow">REPORT {p.name[:2]}</div><h2><a href="{page}">{html.escape(title)}</a></h2><p>{html.escape(excerpt)}…</p></article>')
controls='<div class="searchbar"><label for="search">搜索当前目录</label><input id="search" type="search" placeholder="输入标题、作者、方法或关键词…"><p id="result-count" role="status"></p></div><p id="empty" hidden>没有匹配结果，试试其他关键词。</p>'
shell('全部解读',f'<div class="eyebrow">READING LIBRARY</div><h1>把论文<br><em>读成研究线索。</em></h1><p class="lead">{len(reports)} 篇中文笔记，涵盖思想史、模型、评估、harness 与基础设施。报告 32 为摘要级笔记，其余沿用仓库深度解读。</p>{controls}<div class="cards">'+''.join(cards)+'</div>','reports.html',wide=True)
# Full categorized paper catalog, preserving every source entry.
paperbody,toc=render(sections[4][1],'README.md','papers.html')
soup=BeautifulSoup(paperbody,'html.parser')
for li in soup.select('ol > li'):li['class']=['search-card']
# Filter entire category sections so unnumbered entries and notes remain searchable too.
groups=[];current=None
for node in list(soup.contents):
 if getattr(node,'name',None)=='h3':
  current=soup.new_tag('section',attrs={'class':'paper-group'});groups.append(current)
 if current is not None:current.append(node.extract())
 else:continue
options=''.join(f'<option value="{g.h3.get("id","")}">{g.h3.get_text()}</option>' for g in groups)
for g in groups:
 g['data-category']=g.h3.get('id','')
 # Group text search guarantees all author/summary text stays with its category.
 g['data-search']=g.get_text(' ',strip=True)
shell('论文图谱',f'<div class="eyebrow">PAPER ATLAS</div><h1>沿着问题，<br><em>找到论文。</em></h1><p class="lead">完整保留仓库的 15 个分类，以及原文、中文 PDF、代码和解读入口。</p><div class="searchbar"><label for="search">搜索论文分类全文</label><input id="search" type="search" placeholder="例如：S³Gym、评估器、Meta-Harness"><label for="category">按研究方向筛选</label><select id="category"><option value="">全部方向</option>{options}</select><p id="result-count" role="status"></p></div><p id="empty" hidden>没有匹配结果。</p>'+''.join(str(g) for g in groups),'papers.html',toc,'15 个研究方向')
article('汇总洞察',(ROOT/'reports/10_synthesis_insights.md').read_text(),'reports/10_synthesis_insights.md','insights.html')
# Each README chapter has a readable page; original contents anchors remain on guide.html.
for n,(title,text) in sections.items():
 article(labels.get(n,title),'# '+labels.get(n,title)+'\n\n'+text,'README.md',f'chapter-{n}.html')
article('完整仓库导览',readme,'README.md','guide.html')
article('术语与系统对照','# 术语、时间线与系统对照\n\n'+sections[7][1],'README.md','reference.html')
article('资源与引用','# 资源与引用\n\n'+ '\n\n'.join('## '+labels[n]+'\n'+sections[n][1] for n in [8,9,10,11,12,13,14]),'README.md','resources.html')
# Existing topic reading pages.
article('字节三篇合读',(ROOT/'report/bytedance-self-developing/research.md').read_text(),'report/bytedance-self-developing/research.md','bytedance/research.html')
if (ROOT/'report/chip-rsi/research.md').exists():article('芯片设计专题',(ROOT/'report/chip-rsi/research.md').read_text(),'report/chip-rsi/research.md','chip/research.html')
for src,dst in [('report/awesome_rsi_slides.html','slides.html'),('report/awesome_rsi_full_report.html','full-report.html')]:
 soup=BeautifulSoup((ROOT/src).read_text(),'html.parser')
 for n in soup.select('[src], [href]'):
  for attr in ['src','href']:
   if n.has_attr(attr):n[attr]=target(n[attr],src,dst)
 (OUT/dst).write_text(str(soup))

n_en=len(list((ROOT/'papers/en').glob('*.pdf')));n_classic=len([p for p in (ROOT/'papers/classics').glob('*.pdf') if not p.name.endswith('_zh.pdf')]);n_zh=len(list((ROOT/'papers/zh').glob('*.pdf')))+len(list((ROOT/'papers/classics').glob('*_zh.pdf')))
topics='''<div class="cards"><article class="feature"><div class="eyebrow">专题 01 · 目标 / 经验 / 系统</div><h2><a href="bytedance/">字节三篇：自我改进的三个关口</a></h2><p>Aspire、S³Gym、HarnessDev。把目标形成、经验迁移与系统更新放在一起读。</p></article><article class="feature"><div class="eyebrow">专题 02 · 芯片设计</div><h2><a href="chip/">SILICON LOOP · RSI × 芯片</a></h2><p>RTL 改写、技能积累与验证反馈，附论文数据探索和加法器实验。</p></article></div>'''
shell('研究专题','<div class="eyebrow">COLLECTIONS</div><h1>把相关研究，<br><em>放在一起读。</em></h1>'+topics,'topics.html',wide=True)
home=f'''<div class="eyebrow">AWESOME RECURSIVE SELF-IMPROVEMENT</div><h1>AI 如何<br><em>改进自己？</em></h1><p class="lead">从哥德尔机到自进化 agent，追踪目标、经验、代码与评估的变化。一个可以按问题阅读的 RSI 研究资料库。</p><div class="actions"><a class="primary" href="chapter-1.html">开始阅读 →</a><a href="papers.html">浏览全部论文</a></div><div class="stats"><div><strong>{n_en+n_classic}</strong><span>英文 PDF（含 {n_classic} 篇经典）</span></div><div><strong>{n_zh}</strong><span>中文翻译</span></div><div><strong>{len(reports)}</strong><span>中文解读与笔记</span></div></div><h2>选择你的阅读路线</h2><div class="cards"><article class="feature"><div class="eyebrow">15 分钟 · 先看全貌</div><h3><a href="slides.html">35 页汇总演示</a></h3><p>浏览研究版图、代表方法与评估问题。</p></article><article class="feature"><div class="eyebrow">2 小时 · 抓住主线</div><h3><a href="insights.html">洞察与开放问题</a></h3><p>从“锚在哪”出发，再进入模型与评估器的共进化。</p></article><article class="feature"><div class="eyebrow">系统研读 · 逐篇展开</div><h3><a href="reports.html">全部中文解读</a></h3><p>按标题检索，阅读问题、机制、结果与局限。</p></article><article class="feature"><div class="eyebrow">查阅 · 随时回访</div><h3><a href="reference.html">术语与系统对照</a></h3><p>查询谱系、比较不同系统的改进对象和评估依据。</p></article></div><h2>研究专题</h2>{topics}<h2>研究地图</h2><a href="chapter-3.html"><img class="map" src="assets/fig2_taxonomy.svg" alt="递归自改进分类图：思想史、改进对象、时机与评估依据"></a><div class="callout"><h3>从论文结果到研究判断</h3><p>仓库围绕固定评估依据整理自改进研究。这个视角是一条阅读主线；各篇的实验条件、适用范围和反面结果，需结合原文理解。</p><a href="guide.html">查看完整仓库导览 →</a></div>'''
shell('首页',home,'index.html',wide=True)
for f in ['site.css','site.js']:shutil.copyfile(ROOT/'website'/f,OUT/f)
(OUT/'.nojekyll').touch()
(OUT/'build-info.json').write_text(json.dumps({'reports':len(reports),'english_pdfs':n_en,'classic_pdfs':n_classic,'chinese_pdfs':n_zh,'readme_chapters':len(sections)},indent=2))
print(f'Built {len(list(OUT.rglob("*.html")))} pages; {len(reports)} reports; {len(sections)} README chapters')

# Preserve legacy topic assets from the existing Pages checkout on repeat builds.
if len(sys.argv)>2:
 legacy=Path(sys.argv[2]).resolve()
 chip=legacy/'chip' if (legacy/'chip/index.html').exists() else legacy
 for name in ['index.html','scenes.html','assets','data','experiments','live','research.md']:
  src=chip/name;dst=OUT/'chip'/name
  if src.is_dir():shutil.copytree(src,dst,dirs_exist_ok=True)
  elif src.exists():dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
 for name in ['assets','data','experiments','live','scenes.html','research.md']:
  src=legacy/name;dst=OUT/name
  if src.is_dir():shutil.copytree(src,dst,dirs_exist_ok=True)
  elif src.exists():shutil.copyfile(src,dst)
for name in ['index.html','blog.css','blog.js']:
 dst=OUT/'bytedance'/name;dst.parent.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(ROOT/'report/bytedance-self-developing'/name,dst)
p=OUT/'bytedance/index.html'
p.write_text(p.read_text().replace('https://asimfish.github.io/awesome_rsi/">芯片专题','https://asimfish.github.io/awesome_rsi/chip/">芯片专题'))
# Old chip home fragment links keep their destination after the new site takes over /.
chip_page=OUT/'chip/index.html'
if chip_page.exists():
 anchors=[n['id'] for n in BeautifulSoup(chip_page.read_text(),'html.parser').select('[id]')]
 home=BeautifulSoup((OUT/'index.html').read_text(),'html.parser')
 home.body['data-legacy-chip-anchors']=json.dumps(anchors)
 (OUT/'index.html').write_text(str(home))
