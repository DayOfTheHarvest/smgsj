#!/usr/bin/env python3
"""Finalize crawl: rebuild manifest from saved html, check coverage, fetch missing assets."""
import re, json, hashlib, time, urllib.parse as up
from pathlib import Path
import requests
from bs4 import BeautifulSoup

OUT = Path("/home/dan/Projects/smgsj_new/crawl")
HTML_DIR = OUT/"html"; IMG_DIR=OUT/"images"; ASSET_DIR=OUT/"assets"
BASE="https://www.smgsj.org"

def url_to_fname(url):
    h=hashlib.md5(url.encode()).hexdigest()[:10]
    p=up.urlparse(url)
    path=p.path.strip("/").replace("/","_") or "index"
    if p.query:
        q=re.sub(r"[^a-zA-Z0-9_-]+","_",p.query)[:60]
        path=f"{path}_{q}"
    path=re.sub(r"[^a-zA-Z0-9_.-]+","_",path)[:150]
    return f"{path}_{h}.html"

# map files -> url via canonical
pages={}
internal_links=set()
asset_urls=set()
for fp in HTML_DIR.glob("*.html"):
    try:
        soup=BeautifulSoup(fp.read_bytes(),"lxml")
    except Exception as e:
        print(f"parse fail {fp}: {e}"); continue
    canon=None
    lc=soup.find("link",attrs={"rel":"canonical"})
    if lc and lc.get("href"):
        canon=lc.get("href").strip()
    title=soup.title.get_text(strip=True) if soup.title else ""
    # reconstruct url
    if canon:
        if canon.startswith("http"):
            url=canon
        else:
            url=up.urljoin(BASE+"/",canon)
    else:
        # fallback from filename
        url=f"{BASE}/{fp.stem}"
    pages[url]={"file":f"html/{fp.name}","bytes":fp.stat().st_size,"title":title}
    # collect internal links
    for a in soup.find_all("a",href=True):
        href=a["href"].strip()
        if href.startswith(("mailto:","tel:","javascript:")): continue
        u=up.urljoin(url,href); u,_=up.urldefrag(u)
        p=up.urlparse(u)
        if p.netloc in ("www.smgsj.org","smgsj.org"):
            if "/search/" in u: continue
            internal_links.add(u)
        # asset urls (uploads/assets + pdfs)
        low=u.lower()
        if "uploads.weconnect.com" in u or "assets.weconnect.com" in u or re.search(r"\.(pdf|docx?|xlsx?)(\?|$)",low):
            asset_urls.add(u)
    for img in soup.find_all("img",src=True):
        u=up.urljoin(url,img["src"]); u,_=up.urldefrag(u)
        asset_urls.add(u)
    for lk in soup.find_all("link",href=True):
        u=up.urljoin(url,lk["href"]); u,_=up.urldefrag(u)
        if "weconnect" in u or "smgsj" in u:
            asset_urls.add(u)

print(f"pages on disk: {len(pages)}")
print(f"unique internal links found: {len(internal_links)}")
missing=[u for u in internal_links if u not in pages]
# normalize trailing slash / index variations
def norm(u):
    p=up.urlparse(u)
    path=p.path.rstrip("/")
    if path=="": path="/"
    return p.netloc+path+("?"+p.query if p.query else "")
page_norms={norm(u):u for u in pages}
still_missing=[]
for u in missing:
    if norm(u) in page_norms: continue
    # check equivalent .html variations? e.g. /staff/list vs /staff/list.html
    still_missing.append(u)
print(f"missing pages (not fetched): {len(still_missing)}")
for u in sorted(still_missing)[:50]:
    print("  MISSING:",u)

# check assets on disk: map by hash prefix or basename
existing=set()
for d in (IMG_DIR,ASSET_DIR):
    for f in d.iterdir():
        existing.add(f.name)
# asset expected filename
def asset_fname(au):
    import os
    p=up.urlparse(au)
    h=hashlib.md5(au.encode()).hexdigest()[:10]
    base=os.path.basename(p.path) or f"asset_{h}"
    base=re.sub(r"[^a-zA-Z0-9_.-]+","_",base).split("?")[0]
    return f"{h}_{base}"[:160]

not_downloaded=[]
for au in asset_urls:
    fn=asset_fname(au)
    # protocol-relative //assets... -> https
    if fn not in existing:
        # also check if basename without hash exists? no
        not_downloaded.append((au,fn))
print(f"asset urls referenced: {len(asset_urls)}, missing on disk: {len(not_downloaded)}")
for au,fn in not_downloaded[:30]:
    print("  MISS asset:",au,"->",fn)

# download missing assets
s=requests.Session(); s.headers.update({"User-Agent":"Mozilla/5.0"})
downloaded=0
for au,fn in not_downloaded:
    low=au.lower()
    dest=(IMG_DIR if re.search(r"\.(png|jpe?g|gif|webp|svg|ico)(\?|$)",low) else ASSET_DIR)/fn
    try:
        print(f"fetch asset {au}")
        r=s.get(au,timeout=30)
        if r.status_code==200:
            dest.write_bytes(r.content); downloaded+=1; time.sleep(0.3)
        else:
            print(f"  status {r.status_code}")
    except Exception as e:
        print(f"  err {e}")
print(f"downloaded {downloaded} missing assets")

# rebuild full asset index
assets={}
for d in (IMG_DIR,ASSET_DIR):
    for f in d.iterdir():
        assets[f.name]={"file":f"{d.name}/{f.name}","bytes":f.stat().st_size}
# try to map url->file where possible
url_map={}
for au in asset_urls:
    fn=asset_fname(au)
    if (IMG_DIR/fn).exists(): url_map[au]=f"images/{fn}"
    elif (ASSET_DIR/fn).exists(): url_map[au]=f"assets/{fn}"

manifest={"base":BASE,"pages":pages,"asset_url_map":url_map,
 "stats":{"pages":len(pages),"asset_urls_referenced":len(asset_urls),"files_images":len(list(IMG_DIR.iterdir())),"files_assets":len(list(ASSET_DIR.iterdir())),"missing_pages":sorted(still_missing)},
 "note":"HTML in crawl/html (filename includes md5). Images in crawl/images. PDFs/CSS/JS/docs in crawl/assets. See pages.txt, inventory.csv."}
(OUT/"manifest.json").write_text(json.dumps(manifest,indent=2))
(OUT/"pages.txt").write_text("\n".join(sorted(pages.keys())))
# inventory csv
import csv
with open(OUT/"inventory.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["url","file","title","bytes"])
    for u in sorted(pages):
        w.writerow([u,pages[u]["file"],pages[u]["title"],pages[u]["bytes"]])
print("wrote manifest.json, pages.txt, inventory.csv")
