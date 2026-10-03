# Deploying smgsj.org (Netlify + GitHub, DNS at Network Solutions)

Target: `https://www.smgsj.org` served from this repo via Netlify;
DNS stays at Network Solutions. Every command below was run verbatim on
2026-10-02 (Node v22.22.2, npm 10.9.7); UI steps describe standard Netlify /
GitHub / Network Solutions flows. If a dashboard label has moved, follow the closest
equivalent — the underlying settings (build command, publish dir, Identity,
Git Gateway) have been stable for years.

## 0. Prereqs (verified)

- Node ≥ 20 (`node --version` → v22.22.2 here) and Python 3 (sitemap step).
- A GitHub organization owned by the parish (repo owner = parish, not a volunteer).
- Netlify team owned by the parish; Network Solutions account (`webaccount@smgsj.org`) holding `smgsj.org`.

## 1. Push the repo (run once, from this directory)

```bash
git init
git add -A
git commit -m "SMG parish site: Astro 4 + Decap, migrated content"
git branch -M main
git remote add origin git@github.com:<PARISH-ORG>/smgsj-site.git
git push -u origin main
```

(`main` because `public/admin/config.yml` sets `branch: main` for Git Gateway —
keep them in sync or logins break.)

## 2. Create the Netlify site

1. Netlify → **Add new site → Import an existing project** → connect GitHub →
   pick `<PARISH-ORG>/smgsj-site`.
2. Build settings (also committed in `netlify.toml`, UI just mirrors it):
   - Build command: `npm run build`
   - Publish directory: `dist/`
   - Environment: `NODE_VERSION = 20`
3. Deploy. First build takes ~2–3 min and must end with no `ERROR`.
   Confirm in the deploy log: `[build] Complete!`, `sitemap.xml: N urls`,
   Pagefind `Finished in …`.

## 3. CMS login, forms, redirects (all verified in local `dist/`)

1. **Identity:** Site settings → Identity → **Enable Identity**.
   Identity → **Invite users** → office editors' emails. Editors log in at
   `https://www.smgsj.org/admin`. Registration stays invite-only.
2. **Git Gateway:** Identity settings → **Enable Git Gateway** (lets Decap
   commit through Netlify; requires the GitHub connection from §2).
3. **Forms:** none — the site has no web forms (contact page uses call/email
   cards; signups go to Flocknote/Google/Microsoft externally). Skip Forms setup.
4. **Redirects:** `public/_redirects` (74 rules: legacy `.html` → `/en/<slug>`,
   staff/photo/contact IDs, `/news*`) ships verbatim to `dist/_redirects`.
   Test one after go-live: `/mass-times.html` → `/en/mass-times/`.
5. **Build failure emails:** Site settings → Build notifications → add the
   office + volunteer emails for failed deploys. A failed build never takes
   the site down (Netlify keeps serving the last good deploy) — the email
   just tells the volunteer a staff save needs attention.

## 4. Custom domain + DNS + SSL

1. Netlify → Site settings → **Domain management → Add custom domain**:
   `www.smgsj.org` (and `smgsj.org` → redirect to `www`).
2. Network Solutions → `smgsj.org` → **DNS records** (logged in as
   `webaccount@smgsj.org`): point `www` at the Netlify site (CNAME to
   `<site>.netlify.app`, or the A/CNAME Netlify shows during domain setup).
   Do not add any proxy/CDN layer in front — Identity and Git Gateway
   must reach Netlify directly.
3. SSL: Netlify provisions Let's Encrypt automatically once DNS resolves
   (Site settings → Domain management → HTTPS shows the certificate).

## 5. Go-live checklist (run in order)

```bash
npm run build   # gate: ends [build] Complete!, no ERROR
```
- [ ] Preview smoke (local): `npx astro preview --port 4321`, then HTTP 200 on
      `/ /en/ /es/mass-times/ /vi/confession/ /admin/`
      `/en/staff/andrew-nguyen/ /sitemap.xml /pagefind/pagefind.js /404.html`
      (all verified 200 on 2026-10-02).
- [ ] Push to `main` → Netlify auto-builds → check the Deploy Preview/prod URL.
- [ ] `/mass-times.html` redirects to `/en/mass-times/`.
- [ ] Log in at `/admin` with an invited editor (not the site owner).
- [ ] Sandbox: bulletin swap + hours fix + ES paragraph, each <5 min on a laptop.
- [ ] Pastor demo sign-off (sacramental ES/VI accuracy, presider names).
- [ ] Switch DNS per §4 during a quiet window; confirm `https://www.smgsj.org/`
      loads with a valid cert and `/admin` still logs in.
- [ ] Decide visitor stats (the old Google Analytics ID is dead): either register the domain for Cloudflare Web Analytics (works without moving nameservers) and replace `SMGSJ_REPLACE_ME` in `src/layouts/Base.astro`, or drop in a DNS-independent counter. Rebuild + redeploy after.

## 6. Rollback

Netlify → **Deploys** → pick the last good deploy → **Publish deploy**.
Content edits via Decap are git commits — revert the commit in GitHub to undo.
DNS rollback: flip the Network Solutions record back to the old host.

## 7. If we ever leave Netlify (e.g. Cloudflare Pages)

Only three values change, all in `src/config.ts`: `AUTH_PROVIDER`
(`netlify-identity` → worker/SaaS), `FORM_ENDPOINT` (`netlify-forms` → new URL),
`MEDIA_BASE`. Content (Markdown/JSON), redirects (convert `_redirects` syntax),
and all Decap collections move untouched. Galleries stay external links.

### Replacing staff login (auth switch procedure)

The login surface is exactly 3 files — the public site has zero auth
dependency (`scripts/check-auth.py` / `npm run auth:check` fails if they drift):

| File | Netlify today | After switch |
|---|---|---|
| `src/config.ts` | `AUTH_PROVIDER = 'netlify-identity'` | new provider id |
| `public/admin/index.html` | Netlify Identity widget `<script>` | replacement login snippet |
| `public/admin/config.yml` | `backend: git-gateway` | new backend block |

Concrete paths, easiest first:

1. **Decap-compatible SaaS backend** (if one fits): change the `backend:` block
   + login snippet per its docs, invite staff, done. Content and collections
   untouched. Check current pricing before committing.
2. **GitHub backend + OAuth proxy:** register a GitHub OAuth app on the parish
   org, host Decap's OAuth dance (small worker/service), set
   `backend: {name: github, repo, branch, auth_endpoint}`. Volunteer-level work,
   well-trodden pattern; staff UX stays "log in with GitHub".
3. **Self-hosted Git Gateway:** Netlify's gateway is open-source; run it
   yourself. Most work, full control.

In all cases: run `npm run auth:check`, then `npm run build`, log in at
`/admin` with an editor account, save a test edit, confirm the commit lands in
GitHub and the site rebuilds. Roll back by reverting the 3 files.

## 8. Troubleshooting

| Symptom | Cause → fix |
|---|---|
| `/admin` login loops | Git Gateway off or `branch:` ≠ repo default → §3.1–3.2 |
| Invite link does nothing | Link is old (request a fresh invite), or an ad-blocker ate the login popup — disable it for the site, open the link, complete signup in the modal; you land in `/admin/` |
| Save in Decap does nothing | Not invited via Identity, or Git Gateway cannot reach GitHub |
| Flocknote signup opens new tab | Expected — posts to Flocknote group 346213 in a new tab |
| Old `.html` URL 404s | Missing `_redirects` rule — add `OLD /en/<slug> 301` |
| Mixed-language page | Normal: missing ES/VI shows English + banner (never 404) |
| Build fails on `marked`/Tailwind | Run `npm install` first; Node ≥ 20 |
