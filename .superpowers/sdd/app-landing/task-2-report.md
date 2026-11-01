# Task 2 (S2) - Android app landing rewrite

**Status:** DONE

**Commit:** see `git log -1 --format=%H` on `work/app-landing` (single S2
commit on top of BASE 7fcebdb)

## Scope delivered

Rewrote the consulting page as the FlutterGuard Android app landing page,
using only the copy deck strings and the real `assets/app/*.webp` screenshots.
Kept the nginx Docker deploy path, single dark theme, zero new dependencies and
no webfont.

- `index.html`: new header, hero (copy + `fg-02-grade.webp` in a phone frame),
  facts rail, report trio (`fg-01`, `fg-02`, `fg-03`), 5-cell bento with the
  feature graphic, A/C/F grade band, offline ledger, install stack + checksum
  block + uninstall warning, limits, 6-item FAQ, contact and footer.
  Anchors `#method`, `#scope`, `#why`, `#faq`, `#contact` retained (plus
  `#install`, `#top`, `#main-content`). Removed the analysis console, report
  preview, reviewer bio, comparison, credibility strip and Calendly links.
- `styles.css`: replaced the token block with the approved semantic tokens
  (`--bg`, `--bg-raised`, `--surface`, `--surface-2`, `--text`, `--text-soft`,
  `--text-muted`, `--line`, `--line-strong`, `--accent`, `--accent-strong`,
  `--accent-dim`, `--warn`, `--danger`, `--info`, `--radius: 0`,
  `--container: 86rem`, `--header-height: 4rem`) plus a fluid type scale,
  spacing scale, system sans/mono stacks with Arabic fallbacks, logical
  properties throughout, sharp corners, one mint accent, and a single subtle
  body glow. The `ponytail:` comment records the system-stack choice.
- `site.js`: kept the mobile-nav close handler and added one
  IntersectionObserver reveal. It is skipped under
  `prefers-reduced-motion: reduce`; without JS the content stays visible.
- Removed all Play Store anchors; the install status mentions Play as text
  only. No em dash or en dash appears in any of the three files.

## Test summary

| # | Check | Command | Result |
|---|-------|---------|--------|
| 1 | Image build | `flock /tmp/opencode/flutterguard-build.lock docker build -t fg-site:local .` | PASS, `EXIT=0` (final build after last CSS edit) |
| 2 | Built bytes match source | `docker run --rm fg-site:local sha256sum ...` vs `sha256sum` | PASS, identical hashes for `index.html`, `styles.css`, `site.js` |
| 3 | Old copy gone | `curl -s localhost:8080/ \| grep -Eic 'manual flutter\|calendly\|book a call\|why me\|666\+'` | PASS, `0` |
| 4 | No em/en dash | `grep -n '—\|–' index.html styles.css site.js` | PASS, no matches |
| 5 | No Play anchor | `[...document.querySelectorAll("a")].filter(a=>/play\.google/.test(a.href)).length` | PASS, `0` |
| 6 | Images 200 | container curl on the 4 unique `assets/app` srcs | PASS: `200 image/webp` for `fg-01`, `fg-02`, `fg-03`, `feature-1024x500` |
| 7 | All page images decode | headless CDP `img.decode()` + `naturalWidth` | PASS: 5/5 loaded; 720px screenshots, 1024px feature |
| 8 | Hero CTA above the fold | headless CDP metrics at 1440x900 and 390x844 | PASS: CTA bottom 623 < 900; 434 < 844 |
| 9 | No horizontal overflow | CDP `scrollWidth` vs `innerWidth` at 1440, 768, 390; RTL 390 | PASS: 1440/1440, 768/768, 390/390, RTL 390/390; zero overhanging elements |
| 10 | Reveal behavior | CDP normal motion, scroll to `#scope` | PASS: `reveal-ready` added, bento opacity `0` then `1` |
| 11 | Reduced motion | CDP `prefers-reduced-motion: reduce` | PASS: no `reveal-ready`, bento opacity `1`; no transitions |
| 12 | Mobile nav | CDP open `details` at 390px | PASS: 6 links: What it reads, How it works, Install, FAQ, GitHub, Download APK |
| 13 | Contrast | computed WCAG ratios | PASS: text 17.40, soft 10.33, muted 6.19, accent 13.43, warn 11.63, muted-on-surface 5.85 |
| 14 | JSON-LD parses | Python `json.loads` on both blocks | PASS: `SoftwareApplication`, `FAQPage` with 6 questions |
| 15 | No scroll listeners / webfonts | grep for `addEventListener("scroll`, `fonts.google`, `@font-face` | PASS, no matches |
| 16 | Screenshots | headless Chromium (CDP) | `/tmp/opencode/fg-final-1440x900.png`, `/tmp/opencode/fg-final-390x844.png`, plus full-page `fg-final-desktop.png` / `fg-final-mobile.png`, `fg-mobile-menu.png` |

## Files changed

- `index.html` (rewritten)
- `styles.css` (rewritten)
- `site.js` (+ IntersectionObserver reveal, mobile handler kept)
- `.superpowers/sdd/app-landing/task-2-report.md` (this file)

Untouched: `Dockerfile`, `nginx.conf`, `assets/`, manifest, robots, sitemap,
llms files, 404, `demo/`.

## Concerns / leftovers

- `/demo/` returns 404 in the container until S3 lands. The hero `Test now`
  link points there by spec.
- `og-image.png`, `site.webmanifest`, `404.html`, `sitemap.xml`, `llms.txt`,
  `llms-full.txt` still carry consulting-era content; S4/S5 own them.
- The JSON-LD in `index.html` was updated to `SoftwareApplication` + the new
  FAQ, but S4 may want to replace it with its own structured data.
- The checksum block gives `sha256sum FlutterGuard-*.apk` and points at the
  release-page digest; no hash is hardcoded because no APK file was available
  locally.
- The facts rail values (`0.3.3`, `1.4 MB`) come from the approved copy deck,
  not re-measured here.
- The feature graphic is used as the bento background at a 1024:500 cell ratio;
  below 44rem it becomes a stacked image with the caption band underneath.
- No auth, consent or form surfaces exist on this static page, so no such
  states were added; the 404 surface is still the old nginx page (S4/S5).
- Not run (parent owns): `ui-review`, `seo-polish`, deployment.
