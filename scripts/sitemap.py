#!/usr/bin/env python3
"""Post-build sitemap with hreflang per locale. Run: python3 scripts/sitemap.py"""
import os, glob, datetime
DIST = os.path.join(os.path.dirname(__file__), '..', 'dist')
SITE = 'https://www.smgsj.org'
pages = sorted(glob.glob(DIST + '/en/**/*.html', recursive=True) + glob.glob(DIST + '/en/*.html') + glob.glob(DIST + '/*/index.html'))
urls = {'/': []}  # site root serves the English homepage directly
for p in pages:
    rel = os.path.relpath(p, DIST).replace(os.sep, '/')
    if rel == 'index.html':
        continue  # root already listed above
    elif rel.endswith('/index.html'):
        rel = '/' + rel[:-len('/index.html')] + '/'
    elif rel.endswith('.html'):
        rel = '/' + rel[:-5]
    if rel.startswith('/en/') or rel in ('/en/', '/es/', '/vi/'):
        urls.setdefault(rel.replace('/en/', '/{lang}/').replace('/en', '/{lang}'), []).append(rel)
today = datetime.date.today().isoformat()
out = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
for tpl in sorted(urls):
    if tpl == '/':
        # Root serves English content: one URL, alternates to each locale home.
        out.append('  <url>')
        out.append(f'    <loc>{SITE}/</loc>')
        out.append(f'    <lastmod>{today}</lastmod>')
        for l in ('en', 'es', 'vi'):
            out.append(f'    <xhtml:link rel="alternate" hreflang="{l}" href="{SITE}/{l}/" />')
        out.append('  </url>')
        continue
    for lang in ('en', 'es', 'vi'):
        loc = SITE + tpl.replace('{lang}', lang)
        out.append('  <url>')
        out.append(f'    <loc>{loc}</loc>')
        out.append(f'    <lastmod>{today}</lastmod>')
        for l in ('en', 'es', 'vi'):
            out.append(f'    <xhtml:link rel="alternate" hreflang="{l}" href="{SITE + tpl.replace("{lang}", l)}" />')
        out.append('  </url>')
out.append('</urlset>')
with open(os.path.join(DIST, 'sitemap.xml'), 'w') as f:
    f.write('\n'.join(out) + '\n')
print(f'sitemap.xml: {len(urls)*3} urls')
