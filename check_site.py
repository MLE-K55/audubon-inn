from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).parent
root = ROOT / 'dist'
config = json.loads((ROOT/'site-config.json').read_text(encoding='utf-8'))
base = config['site_url'].rstrip('/')+'/'
errors = []
class Page(HTMLParser):
 def __init__(self):
  super().__init__(); self.refs=[]; self.images=[]; self.h1=0; self.ids=[]; self.meta={}; self.canonical=[]; self.scripts=[]; self.kind=None; self.titles=[]; self.in_title=False
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='h1':self.h1+=1
  if a.get('id'):self.ids.append(a['id'])
  if tag=='title':self.in_title=True
  if tag=='meta':self.meta[a.get('name',a.get('property',''))]=a.get('content','')
  if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a.get('href'))
  for key in ['src','href']:
   if key in a:self.refs.append(a[key])
  if a.get('srcset'):
   self.refs += [x.strip().split()[0] for x in a['srcset'].split(',')]
  if tag=='img':self.images.append(a)
  if tag=='script' and a.get('type')=='application/ld+json':self.kind='schema'
 def handle_data(self,data):
  if self.in_title:self.titles.append(data)
  if self.kind=='schema':self.scripts.append(data)
 def handle_endtag(self,tag):
  if tag=='title':self.in_title=False
  if tag=='script':self.kind=None
pages={}
for path in root.glob('*.html'):
 p=Page();p.feed(path.read_text(encoding='utf-8'));pages[path.name]=p
 if p.h1!=1:errors.append(f'{path.name}: H1 count {p.h1}')
 if len(set(p.ids))!=len(p.ids):errors.append(f'{path.name}: duplicate IDs')
 for img in p.images:
  if not img.get('alt') or not img.get('width') or not img.get('height'):errors.append(f'{path.name}: image needs alt and dimensions')
  if 'placeholder' in img.get('src',''):errors.append(f'{path.name}: public placeholder')
 if path.name=='404.html':continue
 expected=base if path.name=='index.html' else base+path.name
 if p.canonical!=[expected]:errors.append(f'{path.name}: wrong canonical')
 if 'noindex' in p.meta.get('robots',''):errors.append(f'{path.name}: public indexing blocked')
 if not p.meta.get('description'):errors.append(f'{path.name}: missing description')
 for field in ['og:title','og:description','og:url','og:image','twitter:card']:
  if not p.meta.get(field):errors.append(f'{path.name}: missing {field}')
 if not p.scripts:errors.append(f'{path.name}: missing structured data')
 for schema in p.scripts:
  data=json.loads(schema)
  hotel=next(x for x in data['@graph'] if x['@type']=='Hotel')
  bar=next(x for x in data['@graph'] if x['@type']=='BarOrPub')
  if hotel['numberOfRooms']!=18 or hotel['checkinTime']!='14:00' or hotel['checkoutTime']!='10:00' or hotel['petsAllowed'] is not True:errors.append(f'{path.name}: incorrect confirmed hotel facts')
  if bar['openingHoursSpecification'][0]['closes']!='22:00':errors.append(f'{path.name}: bar hours mismatch')
for name,p in pages.items():
 for ref in p.refs:
  u=urlsplit(ref)
  if u.scheme or u.netloc:continue
  target=unquote(u.path) or name
  if not (root/target).exists():errors.append(f'{name}: missing {ref}')
  elif u.fragment and target in pages and u.fragment not in pages[target].ids:errors.append(f'{name}: broken fragment {ref}')
public=[p for name,p in pages.items() if name!='404.html']
for label,values in [('title',[''.join(p.titles) for p in public]),('description',[p.meta.get('description') for p in public])]:
 if len(set(values))!=len(values):errors.append(f'Duplicate page {label}')
locs=[node.text for node in ET.parse(root/'sitemap.xml').findall('.//{*}loc')]
expected={base if name=='index.html' else base+name for name in pages if name!='404.html'}
if set(locs)!=expected:errors.append('Sitemap does not match canonical public pages')
if any('booking-dialog' in (root/name).read_text(encoding='utf-8') for name in pages):errors.append('Redundant stay planner remains')
if errors:raise SystemExit('\n'.join(errors))
print(f'PASS: {len(public)} indexable pages; unique titles/descriptions, canonical URLs, sitemap, hotel/bar JSON-LD, image sizes/alt, local links and fragments; no public image placeholders or extra stay planner.')
