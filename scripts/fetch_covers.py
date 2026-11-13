#!/usr/bin/env python3
"""Download album artwork into the repository (run on GitHub Actions)."""
import json, pathlib, urllib.parse, urllib.request, unicodedata, re, time
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"images"; OUT.mkdir(exist_ok=True)
albums=[
("after-hours","The Weeknd","After Hours"),
("hurry-up-tomorrow","The Weeknd","Hurry Up Tomorrow"),
("my-dear-melancholy","The Weeknd","My Dear Melancholy"),
("starboy","The Weeknd","Starboy"),
("question-mark","XXXTENTACION","?"),
("spider-verse","Metro Boomin","METRO BOOMIN PRESENTS SPIDER-MAN: ACROSS THE SPIDER-VERSE"),
("heroes-villains","Metro Boomin","HEROES & VILLAINS"),
("rodeo","Travis Scott","Rodeo"),
("on-a-trip","ANOTR","On A Trip"),
("withness","ANOTR","Withness"),
("octane","Don Toliver","Octane"),
]
def norm(s):
 s=unicodedata.normalize("NFKD",s).casefold()
 return re.sub(r"[^a-z0-9]+","",s)
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 WishlistAlbumArtwork/1.0"})
 with urllib.request.urlopen(req,timeout=25) as response:return response.read()
for slug,artist,album in albums:
 if slug not in {"question-mark","on-a-trip","octane"}: continue
 try:
  if slug in {"question-mark","on-a-trip"}:
   release={"question-mark":"ca1e1e7b-ac08-4ebe-a809-fe3a949daa55","on-a-trip":"fe2a9747-d008-462b-b1db-25f413c0ebfa"}[slug]
   raw=get("https://coverartarchive.org/release/"+release+"/front-500")
   if len(raw)<2000: raise ValueError("Artwork too small")
   (OUT/(slug+".jpg")).write_bytes(raw)
   print("SAVED verified cover",slug,len(raw))
   continue
  query=urllib.parse.urlencode({"term":artist+" "+album,"entity":"album","media":"music","limit":100,"country":"fr"})
  data=json.loads(get("https://itunes.apple.com/search?"+query))
  results=data.get("results",[])
  exact=[r for r in results if norm(r.get("artistName",""))==norm(artist) and norm(r.get("collectionName",""))==norm(album)]
  if not exact:
   exact=[r for r in results if norm(artist) in norm(r.get("artistName","")) and norm(album) in norm(r.get("collectionName",""))]
  if not exact:
   print("MISSING",slug,album);continue
  record=exact[0]
  artwork=record.get("artworkUrl100","")
  if not artwork:continue
  url=artwork.replace("100x100bb","600x600bb").replace("100x100","600x600")
  raw=get(url)
  if len(raw)<2000 or raw[:3]!=b"\xff\xd8\xff":raise ValueError("Not a valid JPEG")
  (OUT/(slug+".jpg")).write_bytes(raw)
  print("SAVED",slug,record.get("collectionName"),len(raw))
 except Exception as e:print("FAILED",slug,str(e))
 time.sleep(.2)
