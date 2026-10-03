# Parish Website — Office Handbook (laptop only)

**Who is who in this guide:**
- **You / office staff** — the parish employees or volunteers who update words, photos, and
  schedules on the website.
- **Web volunteer** — the technical person who built the site and handles
  anything behind the scenes (logins, design, emergencies). Call this person
  when a step below says so.

**Website address for editing:** `www.smgsj.org/admin`. Log in with the email
address you were invited with.
**Use a laptop.** You can look at the website on a phone, but always do your
editing on a laptop.
**Saving puts your change live.** There is no approval step. The website
updates itself about 2 minutes after you save, so check your work on the live
site afterward.

## The one rule

You can freely change **words, photos, and schedules**. Never change anything
marked **"do not change"** (codes, web addresses, time spellings) — those keep
different pages matching each other. Screens with a yellow WARNING box tell
you exactly what can go wrong; read it before saving.

## Every week (each job takes under 5 minutes)

### New Sunday bulletin
1. On the left menu, open **Media** and press Upload. Pick the new bulletin
   file (must be a PDF, smaller than 5 MB). Click the uploaded file and copy
   its address (it looks like `/uploads/20261011B.pdf`).
2. Open **Bulletins**. Add a new row at the TOP of the list: the date, a label
   like "October 11, 2026", and paste the address you copied. The "past N weeks"
   box controls how many show — normally leave it at 3.
3. Save. Check `/en/` on your phone after about 2 minutes. Old bulletins
   disappear from the card on their own by date.

### Who says which Mass (presiders)
Open **Mass schedule & presiders** → Mass times, places & presiders. Update
"Week of" to the coming Sunday, then type each priest's name in that Mass's
row (for example `Fr. Andrew`). Leave it empty if not decided yet. Save —
names appear on the homepage schedule and the Mass times table. Adding a new
place? Type its exact name, then add its translations under Location names.

### Urgent message for everyone (closures, emergencies, holy-day changes)
Open **Notices, forms & galleries** → Urgent notice. Write the message in all
3 languages, add a link if there is one, and switch it **ON**. Switch it
**OFF** when it no longer applies — while on, the gold message bar shows on
every page of the site.

## Fixing things

| What you want to change | Where to go in the editing screen |
|---|---|
| Page text (41 topics, English/Spanish/Vietnamese) | Pages → pick the topic. English is required; if Spanish or Vietnamese is empty, visitors see the English with a small note (never a broken page). **New page:** Pages → New Page → set its address once (lowercase-with-dashes), write the English, save — it appears in all 3 languages at once. Then link it from another page. The website itself checks for duplicate addresses — if you made one, the web developer volunteer will see an error and help fix it. |
| Mass times, places, notes | Mass schedule → Mass times, places & presiders. Day, language, and place are picked from lists. Each row also holds that Mass's presider name, so nothing can silently mismatch. |
| Confession wording | Mass schedule → Confession text. Shows beside the Mass schedule. |
| Office hours wording | Parish info → Office hours. Hours update everywhere at once (homepage Contact section, bottom of every page, contact page). |
| Staff names, job titles, phone numbers, biographies | Staff directory. Photos: press Choose image, never type an address. Empty biography = no personal page. |
| Homepage moving pictures | Homepage carousel. The first picture shows on load; each picture has its own seconds and size (leave sizes at 1920×480 unless the web developer volunteer says otherwise). Upload wide pictures (about 1920 wide) under Media first. |
| Homepage boxes (Bulletin, Giving, Payment, Requests) | Site settings → Homepage action cards. Kinds: bulletin list (only ONE box), link button, text only. Web addresses for parish pages must start AND end with `/`. You can also type a @shortcut word (@giving, @payment, @calendar-suggest, @calendar-view, @flocknote, @youtube) instead of an address — those follow Site settings automatically. |
| Homepage order | Site settings → Homepage welcome → Page layout. Drag sections to reorder; add a section under Hidden to remove it without deleting it. |
| Welcome text, buttons, events, facility line, church icons | Site settings → Homepage welcome (welcome / events / facility / church blocks). The pastor's words should stay as he wrote them. |
| Top menu | Site settings → Header menu structure. Links must start AND end with `/`. Add a temporary entry (for example a fundraiser) and remove it when done. |
| Phone, email, address, Giving/Payment, Calendar, YouTube, social media | Site settings → Contact info & external links. A wrong address here shows on every page — double-check. |
| Request forms, photo albums | Notices, forms & galleries. Update form addresses when yearly sign-ups roll over; paste Google Photos album addresses as albums move over. |
| Fundraisers (capital campaign and future ones) | Site settings → Fundraisers. Each row powers one fundraiser page (thermometer + donate button). Update goal, raised, date, donate link any time. New fundraiser: create its page under Pages first, add its money row with the same address, feature it with a carousel slide. Finished fundraiser: remove its carousel slide and its money row, then rewrite the page as a thank-you note — no volunteer needed. |
| Button and heading wording (all 3 languages) | Interface words. **Wording only — never rename, remove, or add rows**, or text across the site goes blank. |

## Photos and files

**Media** → Upload. Rules of thumb: PDFs under 5 MB, photos under 1 MB,
wide banners about 1920 wide. Every upload lands in `/uploads/` — copy its
address into the bulletin list, moving pictures, or page. Big files (weekly
bulletins over 5 MB) stay as links — ask the web developer volunteer before
uploading those.

## What NOT to touch (tell the web developer volunteer)

Page design, colors and fonts, logins, the `netlify.toml` file, redirects,
the Flocknote group address, visitor statistics. If the editing screen shows an
error you do not understand, stop and tell — do not guess.

## If something looks wrong after saving

1. Wait 2–3 minutes (the site needs time to update) and refresh the page
   fully (hold Ctrl and press Shift+R together).
2. Re-open what you edited — most problems are a typo in a web address or a
   changed time or code word.
3. Fix the typo and save again.
4. Still broken → call the web developer volunteer. Tell them the page address and what
   you changed.

## Undo / earlier versions (how it works)
*Things can be undone, but there's effort to undo them, so make sure your changes are correct.*
- **Every save is recorded.** Each save stores who changed what and when.
  Nothing is ever truly lost — even weeks later, any older version can be
  brought back by the web developer volunteer.
- **Whole-site undo (web developer volunteer, 1 click):** every published version of the
  site is kept. The volunteer picks the last good version and puts it live.
  Use this if a change broke many pages at once.
- **Single-page undo (web developer volunteer):** the volunteer finds your change in the
  history and undoes just that save.
- You cannot delete history or other people's changes by accident — saving
  only ever *adds* a new version on top.


## Special-week Mass image + custom homepage blocks
Mass schedule → Mass times: flip Display to Image and pick an uploaded picture
to replace the whole schedule block for a special week (switch back after).
Homepage welcome → Custom sections: add freeform cards (picture and/or heading
and/or text and/or button), then place the Custom block in Page layout order.
