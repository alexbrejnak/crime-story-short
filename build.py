#!/usr/bin/env python3
"""Statyczna strona Crime Story Short — GitHub Pages. Bez zależności Python."""
import json,os,re,html,pathlib,urllib.request,urllib.parse,datetime,xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parent
DATA=ROOT/'episodes.json'; DEST=ROOT/'docs'; DEST.mkdir(exist_ok=True)
PLAYLIST='PLXeYYxp3nFN6i5u8av2TYJJcNNVBDE454'
BASE='https://crimestoryshort.us.ci' # docelowo; dla podglądu testowego canonical wyłączony
PREVIEW=os.environ.get('PREVIEW','1')!='0'
API_KEY=os.environ.get('YOUTUBE_API_KEY','')
def req(ep,params):
 params['key']=API_KEY
 url='https://www.googleapis.com/youtube/v3/'+ep+'?'+urllib.parse.urlencode(params)
 with urllib.request.urlopen(url,timeout=30) as f:return json.load(f)
def sync():
 if not API_KEY:
  print('Brak klucza, pozostawiam wersję demonstracyjną episodes.json');return
 items=[];token=None
 while True:
  q={'part':'snippet,contentDetails','playlistId':PLAYLIST,'maxResults':'50'}
  if token:q['pageToken']=token
  d=req('playlistItems',q)
  items.extend(d.get('items',[]));token=d.get('nextPageToken')
  if not token:break
 ids=[]
 for x in items:
  sn=x.get('snippet',{});vid=x.get('contentDetails',{}).get('videoId') or sn.get('resourceId',{}).get('videoId')
  if vid and sn.get('title') not in ('Private video','Deleted video'):ids.append(vid)
 videos={}
 for i in range(0,len(ids),50):
  d=req('videos',{'part':'snippet,status,contentDetails','id':','.join(ids[i:i+50])})
  for e in d.get('items',[]):
   if not e.get('status',{}).get('embeddable',True):continue
   if e.get('status',{}).get('privacyStatus')!='public':continue
   sn=e['snippet']; videos[e['id']]={'id':e['id'],'title':sn['title'],'description':sn.get('description',''),'published':sn.get('publishedAt',''),'thumbnail':sn.get('thumbnails',{}).get('high',{}).get('url','')}
 result=[videos[i] for i in ids if i in videos]
 if len(result)<20:raise RuntimeError('Za mało filmów: '+str(len(result))+'; odmawiam nadpisania kompletnego katalogu')
 DATA.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 print('Pobrano',len(result),'filmów z playlisty')

def esc(v):return html.escape(str(v or ''),quote=True)
def head(title,description,path=''):
 canonical='' if PREVIEW else f'<link rel="canonical" href="{BASE}{path}">'
 robots='<meta name="robots" content="noindex,nofollow">' if PREVIEW else '<meta name="robots" content="index,follow">'
 return f"""<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(description[:160])}">{robots}{canonical}<link rel="icon" href="/crime-story-short/favicon-css.png"><link rel="stylesheet" href="/crime-story-short/design.css"><style>body{{background:#111212;color:#efeeea}}.static-wrap{{max-width:1100px;margin:6rem auto;padding:0 24px}}.static-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:24px}}.static-card{{color:inherit;text-decoration:none;border:1px solid #343535;background:#191919;border-radius:10px;overflow:hidden;display:block}}.static-card img{{width:100%;aspect-ratio:16/9;object-fit:cover}}.static-card h2{{padding:0 16px 16px;font-size:1.3rem}}.static-input{{width:100%;padding:14px;background:#222;color:white;border:1px solid #555;border-radius:7px;margin:20px 0}}.static-nav{{display:flex;gap:20px;align-items:center;flex-wrap:wrap;padding:20px;background:#1b1b1b}}.static-nav a{{color:#eee}}.static-article{{max-width:850px;line-height:1.85}}.static-article h1{{line-height:1.1}}.static-article iframe{{width:100%;aspect-ratio:16/9;border:0}}.meta{{color:#bbb}}</style></head><body><nav class="static-nav"><a href="/crime-story-short/"><img src="/crime-story-short/logo-white.png" width="95" alt="Crime Story Short"></a><a href="/crime-story-short/">Główna</a><a href="/crime-story-short/odcinki/">Wszystkie odcinki</a><a href="https://www.youtube.com/@CrimeStoryShort">YouTube</a></nav>"""
def finish():return '</body></html>'
def thumbnail(e):return esc(e.get('thumbnail') or 'https://i.ytimg.com/vi/'+e['id']+'/hqdefault.jpg')
def card(e):return f'<a class="static-card" href="/crime-story-short/odcinki/{esc(e["id"])}/"><img loading="lazy" src="{thumbnail(e)}" alt="Miniatura odcinka {esc(e["title"])}"><h2>{esc(e["title"])}</h2></a>'
def main():
 sync();episodes=json.loads(DATA.read_text(encoding='utf-8'))
 unique={e['id']:e for e in episodes};episodes=list(unique.values())
 if not episodes:raise RuntimeError('Brak odcinków')
 for e in episodes:
  vid=e['id'];title=e['title'];p=DEST/'odcinki'/vid;p.mkdir(parents=True,exist_ok=True)
  desc=e.get('description') or 'Posłuchaj odcinka polskiego podcastu kryminalnego Crime Story Short.'
  content=f'<main class="static-wrap static-article"><h1>{esc(title)}</h1><p class="meta">Crime Story Short. Polski podcast true crime.</p><iframe loading="lazy" allowfullscreen src="https://www.youtube-nocookie.com/embed/{esc(vid)}" title="{esc(title)}"></iframe><p><a href="https://www.youtube.com/watch?v={esc(vid)}">Oglądaj na YouTube</a></p><h2>O odcinku</h2><p>{esc(desc[:5000]).replace(chr(10),"<br>")}</p></main>'
  (p/'index.html').write_text(head(title+' | Crime Story Short',desc,'/odcinki/'+vid+'/')+content+finish(),encoding='utf-8')
 index=head('Wszystkie odcinki | Crime Story Short','Katalog odcinków polskiego podcastu true crime.')+'<main class="static-wrap"><h1>Wszystkie odcinki</h1><p>Wyszukaj prawdziwą historię kryminalną.</p><input id="q" class="static-input" placeholder="Szukaj po tytule" aria-label="Szukaj odcinków"><p id="count"></p><div class="static-grid" id="grid">'+''.join(card(e) for e in episodes)+'</div></main><script>const cards=[...document.querySelectorAll(".static-card")];document.getElementById("q").addEventListener("input",e=>{let q=e.target.value.toLocaleLowerCase("pl");let count=0;cards.forEach(c=>{let ok=c.textContent.toLocaleLowerCase("pl").includes(q);c.hidden=!ok;if(ok)count++});document.getElementById("count").textContent=count+" odcinków"});document.getElementById("count").textContent=cards.length+" odcinków";</script>'+finish()
 p=DEST/'odcinki';p.mkdir(exist_ok=True);(p/'index.html').write_text(index,encoding='utf-8')
 # home layout based on original design: same assets and stylesheet, simple section arrangement
 latest=episodes[0];previous=episodes[1:7]
 home=head('Crime Story Short | Polski podcast true crime','Prawdziwe historie, prawdziwe zbrodnie. Wszystkie odcinki Crime Story Short.')+f'<main class="static-wrap"><img src="/crime-story-short/street-logo.png" alt="Crime Story Short" style="width:100%;max-height:420px;object-fit:cover"><h1>Tu fakty są straszniejsze niż fikcja.</h1><h2>Najnowszy odcinek</h2><div class="static-grid">{card(latest)}</div><h2>Wcześniejsze odcinki</h2><div class="static-grid">'+''.join(card(e) for e in previous)+'</div><p style="margin-top:32px"><a href="/crime-story-short/odcinki/">Zobacz wszystkie odcinki</a></p><h2>Crime Story Short</h2><p>Prawdziwe historie. Prawdziwe zbrodnie. Prawdziwe konsekwencje.</p><p>Kontakt: <a href="mailto:crimestoryshort@gmail.com">crimestoryshort@gmail.com</a></p></main>'+finish()
 (DEST/'index.html').write_text(home,encoding='utf-8')
 for f in ROOT.glob('*.png'):(DEST/f.name).write_bytes(f.read_bytes())
 (DEST/'design.css').write_bytes((ROOT/'design.css').read_bytes())
 (DEST/'.nojekyll').write_text('')
 # During testing DO NOT expose production domain sitemap; only preview noindex.
 if not PREVIEW:
  urls=['/','/odcinki/']+['/odcinki/'+e['id']+'/' for e in episodes]
  xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+BASE+u+'</loc></url>' for u in urls)+'</urlset>'
  (DEST/'sitemap.xml').write_text(xml,encoding='utf-8')
  (DEST/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+BASE+'/sitemap.xml\n',encoding='utf-8')
 else:
  (DEST/'robots.txt').write_text('User-agent: *\nDisallow: /\n',encoding='utf-8')
 print('Gotowe:',len(episodes),'odcinków; tryb demonstracyjny:',PREVIEW)
if __name__=='__main__':main()
