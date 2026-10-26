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
PREFIX='/crime-story-short/'
def head(title,description,path=''):
 canonical='' if PREVIEW else f'<link rel="canonical" href="{BASE}{path}">'
 robots='<meta name="robots" content="noindex,nofollow">' if PREVIEW else '<meta name="robots" content="index,follow">'
 return f'''<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(description[:160])}">{robots}{canonical}<link rel="icon" href="{PREFIX}favicon-css.png"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800&family=DM+Sans:wght@400;500;600;700&display=swap"><link rel="stylesheet" href="{PREFIX}design.css"><link rel="stylesheet" href="{PREFIX}faithful.css"></head><body><div class="blood-background" aria-hidden="true"></div>'''
def header(home=False):
 return f'''<div class="masthead"><header class="css-header"><div class="header-tagline eyebrow">Podcast true crime</div><nav><a href="{PREFIX}odcinki/">Odcinki</a><a href="{PREFIX}#o-podcascie">O podcaście</a><a class="yt" target="_blank" rel="noopener" href="https://www.youtube.com/@CrimeStoryShort">YouTube ↗</a></nav></header></div>'''
def footer():
 return f'''<section class="closing-cta"><div><p class="kicker">ZOSTAŃ NA KOLEJNY ODCINEK</p><h2>NIE PRZEGAP NASTĘPNEJ HISTORII.</h2><p>Subskrybuj Crime Story Short na YouTube.</p></div><a class="button primary" href="https://www.youtube.com/@CrimeStoryShort?sub_confirmation=1">▶ Subskrybuj kanał ↗</a></section><footer class="css-footer"><a href="{PREFIX}" class="footer-logo" aria-label="Crime Story Short, strona główna"><img src="{PREFIX}logo-white.png" alt="CSS, Crime Story Short" loading="lazy"></a><span>© 2026 Crime Story Short. Podcast true crime.</span><div class="social-links"><a href="https://www.instagram.com/crimestoryshort/" target="_blank" rel="noopener noreferrer">Instagram ↗</a><a href="https://www.facebook.com/crimestoryshort" target="_blank" rel="noopener noreferrer">Facebook ↗</a><a href="https://www.tiktok.com/@crimestoryshort" target="_blank" rel="noopener noreferrer">TikTok ↗</a><a href="https://www.youtube.com/@CrimeStoryShort" target="_blank" rel="noopener noreferrer">YouTube ↗</a><a href="https://open.spotify.com/show/182RSiGTvilaF1uaTAxZNc" target="_blank" rel="noopener noreferrer">Spotify ↗</a></div></footer>'''
def finish():return footer()+'</body></html>'
def thumbnail(e):return esc(e.get('thumbnail') or 'https://i.ytimg.com/vi/'+e['id']+'/hqdefault.jpg')
def card(e):
 return f'''<a class="episode-card" href="{PREFIX}odcinki/{esc(e['id'])}/"><div class="episode-thumb"><img loading="lazy" src="{thumbnail(e)}" alt="Miniatura: {esc(e['title'])}"><span class="episode-play">▶</span></div><h3>{esc(e['title'])}</h3></a>'''
def main():
 sync()
 episodes=json.loads(DATA.read_text(encoding='utf-8'))
 unique={e['id']:e for e in episodes}
 episodes=sorted(unique.values(), key=lambda e: e.get('published') or '', reverse=True)
 if not episodes:raise RuntimeError('Brak odcinków')
 for e in episodes:
  vid=e['id'];title=e['title'];p=DEST/'odcinki'/vid;p.mkdir(parents=True,exist_ok=True)
  desc=e.get('description') or 'Posłuchaj odcinka polskiego podcastu kryminalnego Crime Story Short.'
  content=f'''{header()}<main class="page-shell episode-page"><p class="kicker">CRIME STORY SHORT / ODCINEK</p><h1>{esc(title)}</h1><p class="meta">{esc(e.get('published','')[:10])} · Polski podcast true crime</p><div class="player"><iframe loading="lazy" allowfullscreen allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" src="https://www.youtube-nocookie.com/embed/{esc(vid)}" title="{esc(title)}"></iframe></div><p class="player-caption"><strong>{esc(title)}</strong><a href="https://www.youtube.com/watch?v={esc(vid)}">Otwórz na YouTube ↗</a></p><section class="episode-description"><h2>O odcinku</h2><p>{esc(desc[:8000]).replace(chr(10),'<br>')}</p></section><a class="text-link" href="{PREFIX}odcinki/">← Wszystkie odcinki</a></main>'''
  (p/'index.html').write_text(head(title+' | Crime Story Short',desc,'/odcinki/'+vid+'/')+content+finish(),encoding='utf-8')
 cards=''.join(card(e) for e in episodes)
 index=head('Wszystkie odcinki | Crime Story Short','Katalog odcinków polskiego podcastu true crime.')+header()+f'''<main class="page-shell catalog"><p class="kicker">CRIME STORY SHORT / KATALOG</p><h1>Wszystkie odcinki</h1><p class="intro">Wyszukaj prawdziwą historię kryminalną.</p><input id="q" class="static-input" placeholder="Szukaj po tytule" aria-label="Szukaj odcinków"><p id="count" class="meta"></p><div class="catalog-grid" id="grid">{cards}</div></main><script>const cards=[...document.querySelectorAll('.episode-card')];const count=document.getElementById('count');document.getElementById('q').addEventListener('input',e=>{{let q=e.target.value.toLocaleLowerCase('pl');let n=0;cards.forEach(c=>{{let match=c.textContent.toLocaleLowerCase('pl').includes(q);c.hidden=!match;if(match)n++}});count.textContent=n+' odcinków'}});count.textContent=cards.length+' odcinków';</script>'''+finish()
 p=DEST/'odcinki';p.mkdir(exist_ok=True);(p/'index.html').write_text(index,encoding='utf-8')
 latest=episodes[0];previous=episodes[1:7]
 home=head('Crime Story Short | Polski podcast true crime','Crime Story Short to polski podcast kryminalny. Prawdziwe historie zbrodni, seryjni mordercy i zagadki kryminalne.')+f'''{header(True)}<section class="home-hero"><div class="home-hero-content"><h1>TU <span>FAKTY</span> SĄ<br>STRASZNIEJSZE<br>NIŻ FIKCJA.</h1><p>Podcast kryminalny. Prawdziwe historie zbrodni.<br>Witaj w świecie Crime Story Short.</p><div class="actions"><a class="button primary" href="#odcinki">▶ Posłuchaj odcinków　 ↓</a><a class="button" href="https://www.youtube.com/@CrimeStoryShort?sub_confirmation=1">Subskrybuj kanał ↗</a></div></div></section><main class="home-main"><section id="odcinki" class="feature"><p class="kicker">Najnowszy odcinek</p><div class="player"><iframe title="{esc(latest['title'])}" src="https://www.youtube-nocookie.com/embed/{esc(latest['id'])}" allowfullscreen allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"></iframe></div><p class="player-caption"><strong>{esc(latest['title'])}</strong><a href="https://www.youtube.com/watch?v={esc(latest['id'])}">Otwórz na YouTube ↗</a></p><h2 class="previous-heading">Wcześniejsze odcinki</h2><div class="episode-grid">{''.join(card(e) for e in previous)}</div><a class="button more" href="{PREFIX}odcinki/">Wszystkie odcinki →</a></section><section id="o-podcascie" class="about"><div><p class="eyebrow">ZA KAŻDĄ SPRAWĄ STOI HISTORIA</p><h2>CRIME<br>STORY SHORT<span class="dot">.</span></h2></div><div><p class="quote">PRAWDZIWE HISTORIE.<br>PRAWDZIWE ZBRODNIE.<br>PRAWDZIWE KONSEKWENCJE.</p><p>Crime Story Short to polski podcast true crime. Historie kryminalne z Polski i ze świata. Seryjni mordercy, zagadki kryminalne i niewyjaśnione zbrodnie.</p><p>Wybierz odcinek, załóż słuchawki i posłuchaj. A potem dołącz do rozmowy w komentarzach na kanale.</p><a class="text-link" href="https://www.youtube.com/@CrimeStoryShort">Poznaj kanał ↗</a></div></section><section class="news"><div class="note"><span class="label">CRIME STORY SHORT</span><h2>MASZ SPRAWĘ, O KTÓREJ WARTO OPOWIEDZIEĆ?</h2><p>Zostaw propozycję w komentarzu na YouTube albo napisz: <a href="mailto:crimestoryshort@gmail.com">crimestoryshort@gmail.com</a></p><a class="text-link" href="{PREFIX}odcinki/">Przejdź do odcinków ↗</a></div></section></main>'''+finish()
 (DEST/'index.html').write_text(home,encoding='utf-8')
 for f in ROOT.glob('*.png'):(DEST/f.name).write_bytes(f.read_bytes())
 for f in ('design.css','faithful.css'):(DEST/f).write_bytes((ROOT/f).read_bytes())
 (DEST/'.nojekyll').write_text('')
 if not PREVIEW:
  urls=['/','/odcinki/']+['/odcinki/'+e['id']+'/' for e in episodes]
  xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+BASE+u+'</loc></url>' for u in urls)+'</urlset>'
  (DEST/'sitemap.xml').write_text(xml,encoding='utf-8')
  (DEST/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+BASE+'/sitemap.xml\n',encoding='utf-8')
 else:
  (DEST/'robots.txt').write_text('User-agent: *\nDisallow: /\n',encoding='utf-8')
 print('Gotowe:',len(episodes),'odcinków; tryb demonstracyjny:',PREVIEW)
if __name__=='__main__':main()
