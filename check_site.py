from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
root=Path(__file__).parent/'dist'
errors=[]
class Check(HTMLParser):
 def __init__(self):super().__init__();self.refs=[];self.h1=0;self.ids=[]
 def handle_starttag(self,t,a):
  a=dict(a)
  if t=='h1':self.h1+=1
  if a.get('id'):self.ids.append(a['id'])
  for key in ['src','href']:
   if key in a:self.refs.append(a[key])
  if t=='img' and not a.get('alt'):errors.append(f'{page.name}: missing image alt')
for page in root.glob('*.html'):
 if page.name.startswith('_'):continue
 c=Check();c.feed(page.read_text())
 if c.h1!=1:errors.append(f'{page.name}: expected one H1, got {c.h1}')
 if len(c.ids)!=len(set(c.ids)):errors.append(f'{page.name}: duplicate IDs')
 for ref in c.refs:
  u=urlsplit(ref)
  if u.scheme or u.netloc:continue
  target=(page.parent/unquote(u.path)) if u.path else page
  if not target.exists():errors.append(f'{page.name}: missing {ref}')
  if u.fragment and not u.path and u.fragment not in c.ids:errors.append(f'{page.name}: missing fragment {ref}')
if errors:raise SystemExit('\n'.join(errors))
print('PASS: all pages; one H1 per page; unique IDs; all local assets, page links, and fragments resolve; every image has alt text.')
