"""Build the public website; --preview keeps private copies out of search."""
from pathlib import Path
from html import escape
import argparse
import json
from xml.sax.saxutils import escape as xml_escape
from PIL import Image

ROOT = Path(__file__).parent
CONFIG = json.loads((ROOT / 'site-config.json').read_text(encoding='utf-8'))
parser = argparse.ArgumentParser()
parser.add_argument('--preview', action='store_true')
parser.add_argument('--output', type=Path, default=ROOT / 'dist')
OPTIONS = parser.parse_args()
D = OPTIONS.output
D.mkdir(parents=True, exist_ok=True)
BASE = CONFIG['site_url'].rstrip('/') + '/'
BOOK = CONFIG['booking_url']
EVENT = CONFIG.get('managed_inquiry_url') or CONFIG['inquiry_url']
MAP = 'https://www.google.com/maps/search/?api=1&query=Audubon+Inn+45+N+Main+St+Mayville+WI'
LOGO = (ROOT / 'brand.html').read_text(encoding='utf-8')
NAV = [('index.html','Home'),('rooms.html','Stay'),('events.html','Gather'),('weddings.html','Weddings'),('bar.html','The Beaumont'),('things-to-do.html','Explore'),('dining.html','Dine'),('history.html','Our story')]

def button(label, url, cls='btn', external=False, event=''):
    external = external and url.startswith('https://')
    attrs = ' target="_blank" rel="noopener"' if external else ''
    attrs += f' data-track="{escape(event)}"' if event else ''
    return f'<a class="{cls}" href="{escape(url, quote=True)}"{attrs}>{label} <span aria-hidden="true">{"↗" if external else "→"}</span></a>'

def image(name, alt, cls='', lazy=True, sizes='(max-width: 700px) 100vw, 50vw'):
    path = ROOT / 'dist/assets' / name
    with Image.open(path) as im:
        width, height = im.size
    variants = [(w,f'{path.stem}-{w}.webp') for w in [640,1280] if (path.parent / f'{path.stem}-{w}.webp').exists()]
    src = variants[-1][1] if variants else name
    srcset = ' srcset="'+', '.join(f'assets/{n} {w}w' for w,n in variants)+f'" sizes="{sizes}"' if variants else ''
    return f'<img src="assets/{src}"{srcset} alt="{escape(alt, quote=True)}" class="{cls}" width="{width}" height="{height}" loading="{"lazy" if lazy else "eager"}" decoding="async"'+(' fetchpriority="high"' if not lazy else '')+'>'

def photo(name, alt, caption='', cls=''):
    return f'<figure class="{cls}">{image(name,alt)}'+(f'<figcaption>{caption}</figcaption>' if caption else '')+'</figure>'

def title(kicker, heading, desc):
    return f'<section class="page-intro wrap"><p class="eyebrow">{kicker}</p><h1>{heading}</h1><p class="lede">{desc}</p></section>'

def faq_items(items):
    return ''.join(f'<details><summary>{q}<span aria-hidden="true">+</span></summary><div>{a}</div></details>' for q,a in items)

def cta(kind='stay'):
    event = kind == 'event'
    return '<section class="closing"><div class="wrap closing-inner"><div><p class="eyebrow">'+('BRING YOUR PEOPLE TOGETHER' if event else 'A STAY WITH A STORY')+'</p><h2>'+('Let’s talk about your date.' if event else 'Find your way to Mayville.')+'</h2></div>'+button('Ask about your event' if event else 'Check room availability',EVENT if event else BOOK,'btn light',True,'event_inquiry_start' if event else 'availability_click')+'</div></section>'

def actions(kind='stay'):
    if kind == 'event':
        return '<div class="local-links">'+button('Ask about your date',EVENT,external=True,event='event_inquiry_start')+button('Request a tour',EVENT,'text-link',True,'tour_request')+'</div>'
    return '<div class="local-links">'+button('Check room availability',BOOK,external=True,event='availability_click')+button('Plan a wedding or event','weddings.html','text-link')+'</div>'

FAQ = [
 ('When are check-in and checkout?','Check-in starts after 2 p.m. Checkout is at 10 a.m. Arrange instructions with the front desk before traveling if you expect to arrive outside your planned schedule.'),
 ('Are pets welcome?','Yes, we are pet friendly for an extra fee. Tell the team about your pet before booking so they can confirm the fee and a suitable room.'),
 ('How do I check room prices and availability?',f'<a href="{BOOK}" target="_blank" rel="noopener" data-track="availability_click">Check live room availability on ResNexus</a>. Choose your dates there once, compare available rooms, and review the full price and reservation terms before confirming.'),
 ('Can we reserve a wedding room block?','Ask about a block of 9 or 18 guest rooms, subject to availability. The team will confirm allocation, payment arrangements, release dates, minimum stays, and any exclusivity in your agreement.'),
 ('How many guests can the event space accommodate?','The event space accommodates up to 150 people, with around 70 guests for a comfortable gathering. Your layout, furniture, and celebration plans affect how the space works; discuss these with the events team.'),
 ('When is the Beaumont Bar open?','Friday and Saturday, 5–10 p.m. Check with the inn about private-event closures before a special visit.'),
 ('What food and bar arrangements are available?','We offer event-space rental and private bar service. Discuss food arrangements, packages, staffing, and what is included for your date before booking suppliers.'),
 ('Where should I park or unload?','Call 920-644-2087 for current parking and unloading arrangements before arriving. The inn is at 45 North Main Street in downtown Mayville.'),
 ('How do I check accessibility for my visit?','The inn is a historic building. Before reserving, describe the entrance, elevator, room, bathroom, or step-free route you need. The front desk can discuss the specific route and room for your stay.'),
 ('How is an event inquiry confirmed?','Prepare your event email on our contact page, then send it through your email app, or call the inn. Preparing a draft does not send it. Dates, guest rooms, price, and inclusions are confirmed through your agreement.'),
 ('What should I know before visiting Horicon Marsh?','Choose the national refuge or the state wildlife area before setting out, and check the official visitor guide for current access and facilities. Our <a href="marsh-weekend.html">marsh weekend guide</a> helps you plan the day.')
]
from site_content import create_pages
pages = create_pages(CONFIG,button,image,photo,title,faq_items,cta,actions,FAQ,BOOK,EVENT,MAP)

def canonical(filename):
    return BASE if filename == 'index.html' else BASE+filename

hotel_id, bar_id = BASE+'#hotel', BASE+'bar.html#bar'
hotel = {'@type':'Hotel','@id':hotel_id,'name':'The Audubon Inn','url':BASE,'description':'Historic hotel, event space, and the Beaumont Bar in downtown Mayville, Wisconsin.','telephone':CONFIG['phone'],'email':CONFIG['email'],'address':{'@type':'PostalAddress','streetAddress':'45 North Main Street','addressLocality':'Mayville','addressRegion':'WI','postalCode':'53050','addressCountry':'US'},'numberOfRooms':CONFIG['room_count'],'checkinTime':CONFIG['check_in'],'checkoutTime':CONFIG['check_out'],'petsAllowed':CONFIG['pets_allowed'],'image':BASE+'assets/audubon-exterior-1280.webp'}
hotel['logo'] = BASE+'assets/audubon-logo.webp'
bar = {'@type':'BarOrPub','@id':bar_id,'name':'The Beaumont Bar','url':BASE+'bar.html','containedInPlace':{'@id':hotel_id},'telephone':CONFIG['phone'],'address':hotel['address'],'image':BASE+'assets/bar-640.webp','openingHoursSpecification':[{'@type':'OpeningHoursSpecification','dayOfWeek':['https://schema.org/'+day for day in CONFIG['bar_days']],'opens':CONFIG['bar_opens'],'closes':CONFIG['bar_closes']}]}
if CONFIG['bar_menu_url']:
    bar['hasMenu'] = CONFIG['bar_menu_url']
indexable = CONFIG['index_public_site'] and not OPTIONS.preview
for filename,(pagetitle,description,body,cover) in pages.items():
    body = body.replace('contact.html#event-inquiry', escape(EVENT, quote=True))
    url = canonical(filename)
    nav = ''.join(f'<a href="{href}"'+(' aria-current="page"' if href == filename else '')+f'>{label}</a>' for href,label in NAV)
    graph = [hotel,bar,{'@type':'WebSite','@id':BASE+'#website','url':BASE,'name':'The Audubon Inn'},{'@type':'WebPage','@id':url+'#page','url':url,'name':pagetitle,'description':description,'isPartOf':{'@id':BASE+'#website'},'about':{'@id':bar_id if filename == 'bar.html' else hotel_id}}]
    if filename != 'index.html':
        graph.append({'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Home','item':BASE},{'@type':'ListItem','position':2,'name':pagetitle.split(' — ')[0],'item':url}]})
    if filename == 'rooms.html':
        for name,bed in [('King rooms','King bed'),('Queen rooms','Queen bed'),('Double queen rooms','Two queen beds'),('Classic suites','Queen bed and separate living area')]:
            graph.append({'@type':'HotelRoom','name':name,'description':bed,'containedInPlace':{'@id':hotel_id}})
    verification = '<meta name="google-site-verification" content="'+escape(CONFIG['search_console_verification'],quote=True)+'">' if CONFIG['search_console_verification'] else ''
    schema = json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False).replace('</','<\\/')
    settings = json.dumps({'measurementId':CONFIG['analytics_measurement_id'],'timeZone':'America/Chicago'}).replace('</','<\\/')
    share_image = BASE+'assets/'+cover
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(pagetitle)}</title><meta name="description" content="{escape(description,quote=True)}"><meta name="robots" content="{'index,follow,max-image-preview:large' if indexable else 'noindex,nofollow'}"><link rel="canonical" href="{url}"><meta name="theme-color" content="#243e35">{verification}
<meta property="og:type" content="website"><meta property="og:site_name" content="The Audubon Inn"><meta property="og:locale" content="en_US"><meta property="og:title" content="{escape(pagetitle,quote=True)}"><meta property="og:description" content="{escape(description,quote=True)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{share_image}"><meta property="og:image:alt" content="The Audubon Inn in Mayville, Wisconsin"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(pagetitle,quote=True)}"><meta name="twitter:description" content="{escape(description,quote=True)}"><meta name="twitter:image" content="{share_image}">
<link rel="icon" href="assets/favicon.svg?v=official-logo" type="image/svg+xml"><link rel="stylesheet" href="style.css"><script type="application/ld+json">{schema}</script><script type="application/json" id="site-settings">{settings}</script><script defer src="app.js"></script></head>
<body data-page="{filename.removesuffix('.html')}"><a class="skip" href="#main">Skip to content</a><div class="topline"><span>A HISTORIC STAY. A NATURAL ESCAPE.</span><a href="tel:{CONFIG['phone']}">920-644-2087</a></div>
<header><div class="nav-wrap"><a href="index.html" class="brand" aria-label="The Audubon Inn home">{LOGO}</a><button class="menu-toggle" aria-label="Open navigation" aria-controls="main-nav" aria-expanded="false"><span></span><span></span></button><nav id="main-nav" aria-label="Main navigation">{nav}<a href="contact.html" class="mobile-contact">Contact</a></nav>{button('Check availability',BOOK,'btn nav-book',True,'availability_click')}</div></header>
<main id="main">{body}</main>
<footer><div class="wrap footer-grid"><div><a href="index.html" class="brand">{LOGO}</a><p>A historic stay.<br>A natural escape.</p></div><div><span class="tiny">EXPLORE THE INN</span>{''.join(f'<a href="{href}">{label}</a>' for href,label in NAV[1:])}</div><div><span class="tiny">PLAN YOUR VISIT</span><a href="contact.html">Contact &amp; directions</a><a href="faq.html">Guest questions</a><a href="wedding-guide.html">Wedding planning guide</a><a href="marsh-weekend.html">Marsh weekend guide</a><a href="privacy.html">Privacy &amp; website use</a><a href="sources.html">Information &amp; photo credits</a></div><div><span class="tiny">COME SAY HELLO</span><address>45 North Main Street<br>Mayville, WI 53050</address><a href="tel:{CONFIG['phone']}">920-644-2087</a><a href="mailto:{CONFIG['email']}">Email the inn ↗</a><a href="{MAP}" target="_blank" rel="noopener" data-track="directions_click">Get directions ↗</a></div></div><div class="wrap footer-bottom"><span>© 2026 The Audubon Inn</span><span>ROOTED IN MAYVILLE. INSPIRED BY THE MARSH.</span><button type="button" class="text-link" data-privacy-settings hidden>Privacy choices</button></div></footer>
<div class="mobile-actions" aria-label="Quick booking actions">{button('Rooms &amp; rates',BOOK,'btn',True,'availability_click')}{button('Plan an event',EVENT,'btn light',True,'event_inquiry_start')}</div>
<section class="privacy-banner" aria-label="Analytics choices" hidden><p>Allow optional analytics to help us understand which pages and booking links are useful? We do not include inquiry details in analytics.</p><div><button type="button" class="btn" data-consent="accepted">Allow analytics</button><button type="button" class="btn light" data-consent="declined">Continue without analytics</button><a href="privacy.html">Privacy details</a></div></section></body></html>'''
    (D/filename).write_text(html,encoding='utf-8')
links = ''.join(f'<url><loc>{xml_escape(canonical(name))}</loc></url>' for name in pages) if indexable else ''
(D/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+links+'</urlset>',encoding='utf-8')
(D/'.nojekyll').touch()
(D/'404.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Page not found — The Audubon Inn</title><link rel="stylesheet" href="'+BASE+'style.css"></head><body><main class="wrap section"><p class="eyebrow">THE AUDUBON INN</p><h1>Let’s find your way.</h1><p>This page has moved or is unavailable.</p><a class="btn" href="'+BASE+'">Return to the inn →</a></main></body></html>',encoding='utf-8')
print(f'Built {len(pages)} pages, sitemap and 404; search indexing {"enabled" if indexable else "disabled for preview"}.')
