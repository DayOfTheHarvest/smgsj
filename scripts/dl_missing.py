#!/usr/bin/env python3
import re, hashlib, urllib.parse as up, time
from pathlib import Path
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

OUT=Path("/home/dan/Projects/smgsj_new/crawl")
IMG_DIR=OUT/"images"; ASSET_DIR=OUT/"assets"
def asset_fname(au):
    import os
    p=up.urlparse(au)
    h=hashlib.md5(au.encode()).hexdigest()[:10]
    base=os.path.basename(p.path) or f"asset_{h}"
    base=re.sub(r"[^a-zA-Z0-9_.-]+","_",base).split("?")[0]
    return f"{h}_{base}"[:160]

existing=set(p.name for p in IMG_DIR.iterdir())|set(p.name for p in ASSET_DIR.iterdir())
assets=set()
for fp in Path("crawl/html").glob("*.html"):
    soup=BeautifulSoup(fp.read_bytes(),"html.parser")
    lc=soup.find("link",attrs={"rel":"canonical"})
    canon=lc.get("href").strip() if lc and lc.get("href") else None
    base="https://www.smgsj.org/"
    if canon:
        base=canon if canon.startswith("http") else up.urljoin("https://www.smgsj.org/",canon)
    for img in soup.find_all("img",src=True):
        u=up.urljoin(base,img["src"]); u,_=up.urldefrag(u)
        # skip google maps static? keep but will likely fail without key? try anyway
        if "maps.google.com" in u: continue
        assets.add(u)
    for a in soup.find_all("a",href=True):
        u=up.urljoin(base,a["href"]); u,_=up.urldefrag(u)
        if "uploads.weconnect.com" in u or "assets.weconnect.com" in u or re.search(r"\.(pdf|docx?|xlsx?)(\?|$)",u.lower()):
            assets.add(u)
    # srcset
    for t in soup.find_all(attrs={"srcset":True}):
        for part in t["srcset"].split(","):
            u2=part.strip().split(" ")[0]
            if not u2: continue
            u=up.urljoin(base,u2); u,_=up.urldefrag(u)
            if "weconnect" in u:
                assets.add(u)

miss=[au for au in assets if asset_fname(au) not in existing]
print(f"total {len(assets)} missing {len(miss)}")
(OUT/"assets_missing.txt").write_text("\n".join(sorted(miss)))

def dl(au):
    fn=asset_fname(au)
    low=au.lower()
    dest=(IMG_DIR if re.search(r"\.(png|jpe?g|gif|webp|svg|ico)(\?|$)",low) else ASSET_DIR)/fn
    if dest.exists(): return (au,"cached")
    try:
        r=requests.get(au,timeout=20,headers={"User-Agent":"Mozilla/5.0"})
        if r.status_code==200:
            dest.write_bytes(r.content)
            return (au,f"ok {len(r.content)}")
        return (au,f"http {r.status_code}")
    except Exception as e:
        return (au,f"err {e}")

with ThreadPoolExecutor(max_workers=8) as ex:
    futs={ex.submit(dl,au):au for au in miss}
    done=0
    for f in as_completed(futs):
        au,msg=f.result()
        done+=1
        print(f"[{done}/{len(miss)}] {msg} {au}")
