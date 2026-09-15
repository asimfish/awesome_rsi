"""Verify static pages, internal file links and fragment targets."""
from pathlib import Path
from urllib.parse import urlsplit,unquote
import sys,json
from bs4 import BeautifulSoup
root=Path(sys.argv[1]).resolve();ids={};errors=[]
for p in root.rglob('*.html'):
 s=BeautifulSoup(p.read_text(),'html.parser')
 ids[p]={n['id'] for n in s.select('[id]')}
for p in root.rglob('*.html'):
 s=BeautifulSoup(p.read_text(),'html.parser')
 for n in s.select('a[href],img[src],link[href],script[src]'):
  u=n.get('href',n.get('src',''));v=urlsplit(u)
  if v.scheme or v.netloc:continue
  d=(p.parent/unquote(v.path)).resolve() if v.path else p
  if d.is_dir():d=d/'index.html'
  if not d.exists():errors.append((str(p.relative_to(root)),u,'missing file'))
  elif v.fragment and d in ids and unquote(v.fragment) not in ids[d]:errors.append((str(p.relative_to(root)),u,'missing anchor'))
meta=json.loads((root/'build-info.json').read_text())
assert len(list((root/'reports').glob('*.html')))==meta['reports']
assert len(list(root.glob('chapter-*.html')))==meta['readme_chapters']
if errors:raise SystemExit(str(errors))
print(f'OK: {len(ids)} HTML pages; {meta["reports"]} reports; all local links and anchors resolve.')
