"""Build the complete RSI reading site. Usage: python website/build.py OUTPUT_DIR"""
from pathlib import Path
import sys,re,html,posixpath,json,shutil,hashlib
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
 if href in ['papers.html','reports.html','reference.html','slides.html']:return href
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
 versions={f:hashlib.sha256((ROOT/'website'/f).read_bytes()).hexdigest()[:12] for f in ['site.css','site.js']}
 nav=[('index.html','全景综述'),('papers.html','论文目录'),('reports.html','逐篇解读'),('topics.html','研究专题'),('reference.html','术语对照')]
 active='reports.html' if page.startswith('reports/') else 'topics.html' if page.startswith(('bytedance/','chip/')) else 'index.html' if page=='overview.html' else page
 navhtml=''.join(f'<a href="{prefix}{u}"'+(' aria-current="page"' if active==u else '')+f'>{t}</a>' for u,t in nav)
 toc_soup=BeautifulSoup(toc,'html.parser')
 # Only show section-level links; leave original anchors untouched.
 toc_links=[]
 for a in toc_soup.select('a'):
  if len(a.find_parents('ul'))>2:continue
  if a.get_text().strip()==title.strip():continue
  label=a.get_text(' ',strip=True)
  label=re.sub(r'^\d+[.、]\s*','',label)
  toc_links.append(f'<li><a href="{a["href"]}">{html.escape(label)}</a></li>')
 toc_html='<ul>'+''.join(toc_links)+'</ul>'
 contents=f'<details class="toc-panel" open><summary>本页目录 <span>展开 / 收起</span></summary><div class="toc-body"><div class="eyebrow">本页目录</div>{toc_html}</div></details>' if toc_links else ''
 doc=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Awesome RSI：递归自改进研究的综述、论文、中文解读与专题。"><title>{html.escape(title)} · RSI 研究札记</title><link rel="stylesheet" href="{prefix}site.css?v={versions['site.css']}"></head><body><a class="skip" href="#content">跳到正文</a><div id="progress" aria-hidden="true"></div><header class="topbar"><a class="brand" href="{prefix}index.html">RSI <span>研究札记</span></a><nav aria-label="全站导航">{navhtml}</nav><div class="reading-tools"><button id="font-size" aria-label="放大正文字号" aria-pressed="false">A＋</button><button id="theme" aria-label="切换深色模式">深色</button></div></header><div class="layout {'wide' if wide else ''}"><aside>{contents}<div class="aside-links"><a href="{prefix}index.html">全景综述</a><a href="{prefix}resources.html">资源与来源</a><a href="https://github.com/asimfish/awesome_rsi">GitHub ↗</a></div></aside><main id="content">{body}<footer><strong>RSI 研究札记</strong><p>从论文结果到研究判断。原始实验条件与来源见各篇解读。</p><a href="{prefix}resources.html">资料与引用</a> · <a href="#">返回顶部 ↑</a></footer></main></div><script src="{prefix}site.js?v={versions['site.js']}"></script></body></html>'''
 dest=OUT/page;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(doc)

def article(title,text,source,page,kind='长文阅读',extra=''):
 body,toc=render(text,source,page)
 soup=BeautifulSoup(body,'html.parser');h1=soup.find('h1')
 heading=h1.get_text(' ',strip=True) if h1 else title
 old_id=h1.get('id','') if h1 else ''
 if h1:h1.decompose()
 words=len(soup.get_text());minutes=max(2,round(words/420))
 short,sep,subtitle=heading.partition('：')
 if not sep:short=heading
 prefix='../'*(len(Path(page).parts)-1)
 crumb='全景综述' if page in ['index.html','overview.html'] else '逐篇解读' if page.startswith('reports/') else '研究资料'
 for h in soup.select('h2[id],h3[id]'):
  a=soup.new_tag('a',href='#'+h['id'],attrs={'class':'section-link','aria-label':'跳转到本节'});a.string='#';h.append(a)
 for table in soup.select('.table-scroll'):
  table['tabindex']='0';table['role']='region';table['aria-label']='对照表，可横向滚动'
 intro=''
 if page in ['index.html','overview.html']:
  intro='<div class="reading-note"><strong>这篇文章回答什么？</strong><p>哪些自改进已经有效，哪些结果还不能证明持续进步，以及下一步该如何验证。</p><div><a href="#先说结论">先看核心结论 ↓</a><a href="papers.html">查找具体论文 →</a></div></div>'
 if page.startswith('bytedance/'):
  downloads=[]
  for name,aid,pdf in [('Aspire','2608.31111','Aspire'),('S³Gym','2608.31100','S3Gym'),('HarnessDev','2609.01437','HarnessDev')]:
   downloads.append(f'<p><strong>{name}</strong> · <a href="https://arxiv.org/abs/{aid}">论文原文</a> · <a href="{RAW}papers/zh/{aid}_{pdf}_zh.pdf">中文 PDF</a></p>')
  intro='<div class="reading-note"><strong>配套论文</strong>'+''.join(downloads)+'</div>'
 if page.startswith('reports/32_'):
  intro='<p class="note">摘要级笔记 · 本文依据论文摘要整理，尚非全文深度解读。</p>'
 hero=f'<header class="article-header"><div class="breadcrumb"><a href="{prefix}index.html">RSI 研究札记</a><span>/</span>{crumb}</div><div class="eyebrow">{kind}</div><h1 id="{old_id}">{html.escape(short)}</h1>'+(f'<p class="subtitle">{html.escape(subtitle)}</p>' if subtitle else '')+f'<p class="meta">约 {minutes} 分钟阅读 · <a href="{BASE+source}">查看原始笔记 ↗</a></p></header>'
 shell(title,hero+intro+f'<div class="prose">{soup}</div>'+extra,page,toc,kind)

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
 cardtitle=title.partition('：')[0];carddesc=title.partition('：')[2] or excerpt
 cards.append(f'<article class="search-card" data-search="{html.escape(title+" "+text,quote=True)}"><div class="eyebrow">REPORT {p.name[:2]}</div><h2><a href="{page}">{html.escape(cardtitle)}</a></h2><p>{html.escape(carddesc)}</p></article>')
controls='<div class="searchbar"><label for="search">检索解读全文</label><input id="search" type="search" placeholder="搜索方法名、研究问题或正文关键词…"><p id="result-count" role="status"></p></div><p id="empty" hidden>没有匹配结果，试试其他关键词。</p>'
shell('全部解读',f'<div class="eyebrow">READING LIBRARY</div><h1>逐篇读懂 RSI 研究</h1><p class="lead">{len(reports)} 篇中文笔记，涵盖思想史、模型、评估、harness 与基础设施。报告 32 为摘要级笔记，其余沿用仓库深度解读。</p>{controls}<div class="cards">'+''.join(cards)+'</div>','reports.html',wide=True)
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
category_names=['起源与思想史','从自改写到 agent','综述与研究地图','框架与源码','评估器与反馈','模型与权重','知识、记忆与技能','在线适应','Harness 工程','自主研究与产业实践','安全与治理','程序进化谱系','宏观争论与测量','开源系统与基础设施','自改进基准']
for i,g in enumerate(groups):
 g.h3.string=f'{i+1:02d} · {category_names[i]}'
 # The Last AI entry is unnumbered in the README; include it in per-paper search.
 for para in list(g.find_all('p',recursive=False)):
  if para.find('strong') and para.find('strong').get_text().rstrip().endswith('.') and para.find('a') and not para.find_parent('blockquote'):
   record=soup.new_tag('article',attrs={'class':'paper-entry'})
   nxt=para.find_next_sibling('p')
   para.wrap(record)
   if nxt and nxt.find('em'):record.append(nxt.extract())
 for record in g.select('ol > li')+g.select('article.paper-entry'):
  record['class']=['paper-entry'];record['data-search']=record.get_text(' ',strip=True)
  title_node=record.find('strong')
  if title_node:
   h=soup.new_tag('h4');h.append(title_node.extract());record.insert(0,h)
  author=record.find('em')
  if author:author['class']=['paper-author']
  for a in record.find_all('a'):
   a['class']=['paper-link']
   translations={'paper':'原文','PDF-en':'英文 PDF','PDF-zh':'中文 PDF','code':'代码','project':'项目页','解读':'中文解读'}
   if a.get_text() in translations:a.string=translations[a.get_text()]
options=''.join(f'<option value="{g.h3.get("id","")}">{g.h3.get_text()}</option>' for g in groups)
for g in groups:
 g['data-category']=g.h3.get('id','')
 # Group text search guarantees all author/summary text stays with its category.
 g['data-search']=g.get_text(' ',strip=True)
shell('论文图谱',f'<div class="eyebrow">PAPER ATLAS</div><h1>按研究问题查找论文</h1><p class="lead">按 15 个研究方向整理。搜索可定位到具体论文，原文、中译与解读在同一条目中。</p><div class="searchbar"><label for="search">搜索论文</label><input id="search" type="search" placeholder="例如：S³Gym、评估器、Meta-Harness"><label for="category">按研究方向筛选</label><select id="category"><option value="">全部方向</option>{options}</select><p id="result-count" role="status"></p></div><p id="empty" hidden>没有匹配结果。</p>'+''.join(str(g) for g in groups),'papers.html',toc,'15 个研究方向')
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
article('递归自改进走到了哪一步？',(ROOT/'website/overview.md').read_text(),'website/overview.md','index.html','全景综述 / 从结果到判断')
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

article('递归自改进走到了哪一步？',(ROOT/'website/overview.md').read_text(),'website/overview.md','overview.html','全景综述 / 从结果到判断')

article('字节三篇：从目标到系统',(ROOT/'report/bytedance-self-developing/research.md').read_text(),'report/bytedance-self-developing/research.md','bytedance/index.html','专题 / 字节三篇')

# Keep the specialized chip interface, with a clear path back to the whole site.
p=OUT/'chip/index.html'
if p.exists():
 doc=BeautifulSoup(p.read_text(),'html.parser')
 if not doc.select_one('[data-rsi-return]'):
  nav=doc.new_tag('nav',attrs={'data-rsi-return':'true','aria-label':'返回 RSI 全站','style':'padding:10px 24px;background:#edf3ed;color:#293630;font:14px/1.6 system-ui;position:relative;z-index:100'})
  a=doc.new_tag('a',href='../index.html',attrs={'style':'color:#346c52;text-decoration:none'});a.string='← RSI 全景综述'
  nav.append(a);nav.append('  /  芯片设计专题');doc.body.insert(0,nav)
 p.write_text(str(doc))
