#!/usr/bin/env python3
"""Fail if two pages share a slug (Decap cannot warn natively).
Run: python3 scripts/check-slugs.py — add new pages, then run this before pushing.
Decap would silently overwrite same-named files, so this is the safety net."""
import glob, re, sys

seen: dict[str, str] = {}
dupes = []
for fp in sorted(glob.glob('src/content/pages/*.md')):
    t = open(fp, encoding='utf-8').read()
    m = re.search(r'^slug_key:\s*"?([^"\s]+)"?\s*$', t, re.M)
    keys = {m.group(1)} if m else set()
    keys.add(fp.split('/')[-1][:-3])
    for key in keys:
        if key in seen and seen[key] != fp:
            dupes.append((key, seen[key], fp))
        else:
            seen[key] = fp

if dupes:
    print('DUPLICATE SLUGS (Decap would overwrite one page with the other):')
    for key, a, b in dupes:
        print(f' - {key}: {a} vs {b}')
    sys.exit(1)
print(f'slugs OK: {len(seen)} unique')
