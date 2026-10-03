#!/usr/bin/env python3
"""Crawl www.smgsj.org - save HTML + download images/assets."""
import os, re, json, hashlib, time, urllib.parse as up
from pathlib import Path
import requests
from bs4 import BeautifulSoup

BASE = "https://www.smgsj.org"
OUT = Path("/home/dan/Projects/smgsj_new/crawl")
HTML_DIR = OUT / "html"
ASSET_DIR = OUT / "assets"
IMG_DIR = OUT / "images"
RAW_DIR = OUT / "raw"  # raw mirrored structure
for d in (HTML_DIR, ASSET_DIR, IMG_DIR, RAW_DIR):
    d.mkdir(parents=True, exist_ok=True)

SEEN = set()
QUEUE = [BASE + "/"]
PAGES = {}  # url -> file
ASSETS = {} # url -> file
ERRORS = []

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 ( parish-migration crawl; contact parish office )"})

def normalize(href, base):
    if not href: return None
    href = href.strip()
    if href.startswith(("mailto:", "tel:", "javascript:", "#")):
        return None
    u = up.urljoin(base, href)
    # strip fragment
    u, frag = up.urldefrag(u)
    return u

def is_internal(u):
    p = up.urlparse(u)
    return p.netloc in ("www.smgsj.org", "smgsj.org", "") and p.scheme in ("http","https","")

def is_asset_url(u):
    low = u.lower()
    # uploads, assets, pdfs, images, docs
    if "uploads.weconnect.com" in u or "assets.weconnect.com" in u:
        return True
    if re.search(r"\.(pdf|png|jpe?g|gif|webp|svg|ico|css|js|woff2?|ttf|eot|mp4|mp3)(\?|$)", low):
        return True
    return False

def safe_name(url, prefix=""):
    h = hashlib.md5(url.encode()).hexdigest()[:10]
    p = up.urlparse(url)
    path = p.path.strip("/").replace("/", "_") or "index"
    if p.query:
        q = re.sub(r"[^a-zA-Z0-9_-]+", "_", p.query)[:60]
        path = f"{path}_{q}"
    path = re.sub(r"[^a-zA-Z0-9_.-]+", "_", path)[:150]
    # keep extension if asset
    return f"{path}_{h}"

def fetch(url, retries=3):
    for i in range(retries):
        try:
            r = session.get(url, timeout=30)
            return r
        except Exception as e:
            if i == retries-1:
                raise
            time.sleep(2*(i+1))
    return None

def save_page(url):
    try:
        r = fetch(url)
    except Exception as e:
        ERRORS.append({"url": url, "error": str(e)})
        print(f"ERR {url}: {e}")
        return None, []
    if r.status_code != 200:
        ERRORS.append({"url": url, "status": r.status_code})
        print(f"{r.status_code} {url}")
        # still save if useful? skip
        return None, []
    ctype = r.headers.get("Content-Type","")
    # only parse html
    if "html" not in ctype and "text" not in ctype and len(r.content) < 100:
        print(f"SKIP non-html {url} {ctype}")
        return None, []
    # save raw html
    name = safe_name(url)
    if not name.endswith(".html"):
        name += ".html"
    fp = HTML_DIR / name
    fp.write_bytes(r.content)
    # also save with url mapping: raw path mirror
    PAGES[url] = {"file": f"html/{name}", "status": r.status_code, "bytes": len(r.content), "title": ""}
    try:
        soup = BeautifulSoup(r.content, "lxml")
        title = soup.title.get_text(strip=True) if soup.title else ""
        PAGES[url]["title"] = title
        # find links
        out_links = []
        for a in soup.find_all("a", href=True):
            nu = normalize(a["href"], url)
            if not nu: continue
            # record asset links (pdf etc) even if external uploads host
            if is_asset_url(nu):
                queue_asset(nu)
            if is_internal(nu):
                # filter out search, calendarwiz, google scripts already external - is_internal false for those
                # skip weird contact/index/id map urls? keep but they are internal
                out_links.append(nu)
        # images
        for img in soup.find_all("img", src=True):
            iu = normalize(img["src"], url)
            if iu: queue_asset(iu)
        for tag in soup.find_all(attrs={"srcset": True}):
            for part in tag["srcset"].split(","):
                u2 = part.strip().split(" ")[0]
                iu = normalize(u2, url)
                if iu: queue_asset(iu)
        # link css, script
        for lk in soup.find_all("link", href=True):
            lu = normalize(lk["href"], url)
            if lu and is_asset_url(lu):
                queue_asset(lu)
        for sc in soup.find_all("script", src=True):
            su = normalize(sc["src"], url)
            if su and ("weconnect" in su or su.endswith(".js")):
                # only queue weconnect assets to avoid google etc bloat, but record all
                if "weconnect" in su or "smgsj" in su:
                    queue_asset(su)
        return soup, out_links
    except Exception as e:
        ERRORS.append({"url": url, "error": f"parse: {e}"})
        return None, []

ASSET_QUEUE = []
ASSET_SEEN = set()
def queue_asset(u):
    if u in ASSET_SEEN: return
    # only download uploads.weconnect, assets.weconnect, smgsj.org assets, plus pdfs linked from site
    p = up.urlparse(u)
    allowed_hosts = ("uploads.weconnect.com", "assets.weconnect.com", "www.smgsj.org", "smgsj.org")
    # also allow external pdfs? e.g. bulletins are on uploads.weconnect so covered. Skip google, facebook etc.
    if p.netloc not in allowed_hosts:
        # still record but don't download unless pdf/image?
        # download pdfs regardless? Keep list but mark external
        if not re.search(r"\.(pdf|png|jpe?g|gif|webp)(\?|$)", u.lower()):
            return
    ASSET_SEEN.add(u)
    ASSET_QUEUE.append(u)

# BFS crawl
visited_order = []
count = 0
while QUEUE:
    url = QUEUE.pop(0)
    # canonicalize: remove trailing? keep as-is but dedupe
    if url in SEEN: continue
    SEEN.add(url)
    print(f"[{len(SEEN)}] FETCH {url}")
    soup, links = save_page(url)
    if soup is None and url not in PAGES:
        continue
    visited_order.append(url)
    count += 1
    for l in links:
        # normalize: drop empty query? keep news?page=N distinct
        # skip /search/results? and staff photos infinite? include but limit
        if "/search/" in l:
            continue
        if l in SEEN: continue
        if l not in QUEUE:
            QUEUE.append(l)
    time.sleep(0.6)  # politeness (robots Crawl-delay 10 is excessive; use 0.6)
    if len(SEEN) > 500:
        print("LIMIT 500 reached, stopping")
        break

print(f"\nPages fetched: {len(PAGES)}, queued left: {len(QUEUE)}")
print(f"Assets queued: {len(ASSET_QUEUE)}")

# Download assets
for i, au in enumerate(list(ASSET_QUEUE)):
    try:
        # filename
        p = up.urlparse(au)
        ext_match = re.search(r"\.([a-zA-Z0-9]{2,4})(\?|$)", p.path + ("?"+p.query if p.query else ""))
        # Use hash name preserving ext
        h = hashlib.md5(au.encode()).hexdigest()[:10]
        base = os.path.basename(p.path) or f"asset_{h}"
        base = re.sub(r"[^a-zA-Z0-9_.-]+", "_", base)
        if "?" in base:
            base = base.split("?")[0]
        # prefix to avoid collisions
        fname = f"{h}_{base}"[:160]
        # decide dir
        low = au.lower()
        if re.search(r"\.(png|jpe?g|gif|webp|svg|ico)(\?|$)", low):
            dest = IMG_DIR / fname
            kind = "image"
        else:
            dest = ASSET_DIR / fname
            kind = "asset"
        if dest.exists():
            ASSETS[au] = {"file": f"{kind}s/{fname}", "cached": True}
            continue
        print(f"  asset [{i+1}/{len(ASSET_QUEUE)}] {au}")
        r = fetch(au)
        if r.status_code == 200:
            dest.write_bytes(r.content)
            ASSETS[au] = {"file": f"{'images' if dest.parent==IMG_DIR else 'assets'}/{fname}", "bytes": len(r.content), "content_type": r.headers.get("Content-Type","")}
        else:
            ERRORS.append({"asset": au, "status": r.status_code})
            print(f"    -> {r.status_code}")
    except Exception as e:
        ERRORS.append({"asset": au, "error": str(e)})
        print(f"    ERR {e}")
    time.sleep(0.3)

# also run wget mirror for raw fidelity? Do lightweight: save manifest
manifest = {
    "base": BASE,
    "crawled_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "pages": PAGES,
    "assets": ASSETS,
    "errors": ERRORS,
    "queue_remaining": [u for u in QUEUE if u not in SEEN][:100],
}
(OUT / "manifest.json").write_text(json.dumps(manifest, indent=2))
# write url list
(OUT / "pages.txt").write_text("\n".join(sorted(PAGES.keys())))
(OUT / "assets.txt").write_text("\n".join(sorted(ASSETS.keys())))
print(f"\nDONE: {len(PAGES)} pages, {len(ASSETS)} assets downloaded, {len(ERRORS)} errors")
print(f"OUT: {OUT}")
