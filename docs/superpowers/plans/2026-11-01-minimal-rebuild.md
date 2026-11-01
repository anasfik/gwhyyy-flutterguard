# FlutterGuard Minimal Rebuild Implementation Plan

> **For agentic workers:** Use subagent-driven-development. One product implementer, then independent Playwright UI verification and code review. Track steps below.

**Goal:** Replace the rejected long industrial landing with an approved compact, light product sheet using genuine app screens.
**Architecture:** Preserve vanilla HTML/CSS/JS, existing routes and nginx security. Build a short static homepage with native disclosure; keep the sample report explicitly synthetic and functional. Self-host all runtime assets.
**Tech Stack:** Semantic HTML, tokenized native CSS, minimal vanilla JavaScript, pinned nginx Docker image, existing Python Playwright for a runnable regression check; Playwright MCP for real visual review.
**Spec:** User approved in chat: "Build this (Recommended)" for a compact light product sheet with app identity, one-sentence introduction, download/GitHub/sample links, two genuine app screens, compact install disclosure and contact/privacy. No repeated feature sections. The design block below fixes the controller's remaining choices.

## Global Constraints
- Repository `/home/gwhyyy/real-projects/gwhyyy-flutterguard`; branch `work/app-landing`; rebuild BASE `77d1ad7`.
- Every child uses `opencode-go/deepseek-v4.1-flash`, never spawns children, never pushes/deploys/publishes.
- Primary orchestrates only. One mutator; at most two lightweight read-only children. Build under `/tmp/opencode/flutterguard-site-build.lock`; check `df -h /` first and stop if over 95%.
- Preserve unrelated work and old `.superpowers/sdd/app-landing` artifacts. Old S6/S7 gates are superseded. Do not redo Android release work.
- No new framework, runtime dependency, analytics, upload control, remote font request or backend. Never weaken CSP to make the design work.
- Genuine app logo and raw captures only. No invented screenshots, testimonials, grades, benchmarks, telemetry or live-on-Play claims.
- App is native Android software inspecting Flutter APKs, not a Flutter-built web app. Static findings are evidence for review, not proof of vulnerability. Scan times vary and may take minutes.
- Homepage has at most 260 visible words INCLUDING expanded install notes, navigation, captions and footer. Target at least 75% fewer words than the measured baseline, with 260 as an absolute ceiling.
- No feature grid, FAQ section, grade tiles, numbered marketing screenshots, repeated CTAs, oversized headline, sticky navigation or scroll reveal. Visible content must not depend on JavaScript.
- Keep `/`, `/demo/`, `/404.html`, metadata/robots/sitemap/security routes working. Download `https://github.com/anasfik/FlutterGuard/releases/latest`; source `https://github.com/anasfik/FlutterGuard`; contact `mailto:work@gwhyyy.com`; privacy `https://gwhyyy.com/privacy/flutterguard`.
- No deployment/push. Keep reachable local preview and give the user the real URL.

## Design and tokens
Reading this as a small Android utility product page, not a SaaS pitch. Direction: **cool contact sheet**. Light-first is explicitly user-approved. Dials: DESIGN_VARIANCE 6, MOTION_INTENSITY 2, VISUAL_DENSITY 2. Do not combine conflicting prior industrial/GSAP/card-grid instructions with this direction.

- Container max 1080px, responsive horizontal gutters 24px (16px below 400px).
- Compact header with actual app mark and name, no anchor navigation or hamburger. Main introduction is deliberately off-center in a generous sheet, not an enormous left headline beside an enormous phone.
- H1 exact copy: `Look inside a Flutter APK.` Body: `Inspect libraries, endpoints and exposed strings. On your Android device, without uploads or an account.`
- One primary `Download APK` link; `GitHub` and `See sample` are quiet text links. The sample goes to `/demo/`, never suggests live browser scanning.
- Two genuine raw screenshots arranged as a small contact sheet below the introduction, not card-based marketing features. Preserve their aspect ratios, readable UI and ROM chrome. Max CSS width 260px per image. On small screens use a deliberate two-up arrangement only if it remains clear; otherwise one column. Do not crop out data, recolor app pixels or add fake phone chrome.
- Short facts line: Android 8+, offline, MIT open source. Flutter mark may appear once, small and subordinate; it is not an endorsement badge.
- One native `<details>` titled `Before you install`. Include GitHub releases install path; Android 8+; static analysis limits/authorized apps; scans may take minutes; switching Play/GitHub signing requires uninstall, loses local reports/settings/history, export first (exports are not a history restore). Keep concise, do not bury the primary download behind a modal.
- Footer is one compact line/group: maintainer/contact, issues, privacy, license. One short Flutter/Google non-affiliation line only if the logo is used.
- Homepage target height <=1600px at 1440x900 with disclosure closed, <=2400px at 390x844; avoid whitespace padding to inflate a short page. Images must be explicit-dimension, not background decorations.
- Use a single verified open-license self-hosted humanist/geometric sans (Manrope preferred; a verified OFL alternative acceptable). Vendor the actual WOFF2 and license/provenance, no npm package. Do not assume a local font or licensing exists: reconnaissance found none in either repo. If acquisition fails, report the blocker instead of silently falling back to the rejected system-only typography.

```css
:root {
  --font: "Manrope", sans-serif;
  --text-small: .875rem; --text: 1rem; --text-lead: 1.25rem;
  --title-small: 1.953rem; --title: 3.052rem;
  --s1: .25rem; --s2: .5rem; --s3: .75rem; --s4: 1rem;
  --s6: 1.5rem; --s8: 2rem; --s12: 3rem; --s16: 4rem; --s24: 6rem;
  --page: #f4f6f5; --surface: #fafcfb; --ink: #19221e;
  --muted: #526159; --line: #d3dcd6; --accent: #285f42;
  --radius: .5rem;
  --fast: 120ms; --normal: 220ms;
  --ease: cubic-bezier(.2, 0, 0, 1);
}
```

Use one 1.25 type scale and the spacing scale throughout. H1 3.052rem desktop/1.953rem small, at most two lines desktop. Weights 400/500/600 only. No decorative shadows, gradients, noisy textures, card borders, pills or arbitrary tiny labels. Native focus outlines must be clear, >=44px touch targets, AA text contrast, reduced-motion supported. Only purposeful hover/pressed/focus feedback, no automatic motion.

## Review Focus
1. No JS/font/image: core introduction and links remain available; reserve images and use useful alt text.
2. 320px/390px/768px/1280x720/1440px, 200% zoom and expanded notes: no horizontal scroll, clipped text or obscured action.
3. Download/source/sample routes: exact truthful destinations, no browser upload implication or invented performance claims.
4. Shared CSS changes: sample tabs/reveal controls and 404 remain usable and visually aligned; sample stays noindex.
5. nginx deployment path: new font/image assets copied, correct MIME/cache, real 404 status and CSP retained; Python preview alone is insufficient proof.

## Task 1: Complete compact product-sheet rebuild

**Owner:** one `web-rebrand` implementer. No children.
**Dependencies:** baseline Playwright audit and raw-asset inventory complete; approved design above.

**Files:**
- Replace product presentation: `index.html`, `styles.css`, `site.js` (remove unused logic; keeping an empty script is unnecessary).
- Align dependent surfaces: `demo/index.html`, `demo/demo.css`, `demo/demo.js` only as needed, `404.html`.
- Synchronize presentation metadata: `site.webmanifest`, `og-image.png`, necessary metadata in HTML, and `llms.txt`/`llms-full.txt` only when new copy makes them inaccurate. Remove homepage FAQPage JSON-LD when removing visible FAQs; keep accurate SoftwareApplication JSON-LD without unverified current release version.
- Import `assets/app/inventory.webp` from canonical app `docs/play/raw/raw-home.png`, `assets/app/report.webp` from `raw-overview.png`. Recommended width 720px, height1600, preserving 1080:2400 aspect. Keep original screenshot files and app logo unchanged.
- Create `assets/fonts/manrope-latin.woff2`, its license and concise source/provenance note (equivalent verified font names allowed if choice is recorded).
- Integrate in `Dockerfile`, `nginx.conf`, `_headers`: font MIME `font/woff2`, cache alongside static images, correct Docker COPY. Preserve pinned image/security directives.
- Create `tests/check_site.py`: one small runnable Python Playwright behavioral smoke check, no new test framework. No exhaustive per-function suite.
- Do not touch app source, host proxy configuration, unrelated metadata, old coordination reports or old app-landing assets.

**Interfaces:**
- Input: genuine raw assets `/home/gwhyyy/Downloads/projects/real_projects/fg-remote/docs/play/raw/{raw-home,raw-overview}.png`; logo already in `assets/app/icon-512.png`; exact links in Global Constraints.
- Output: static pages above, same routes; behavioral check run as `python3 tests/check_site.py http://127.0.0.1:8791` (optional second screenshot-output argument allowed).
- Sample compatibility: retain clearly synthetic example, keyboard-operable tabs (arrows/Home/End), masked secrets toggles and home link. No real secrets or network requests. Keep three report views but remove decorative/repetitive surrounding copy; the sample need not share homepage word budget.

- [ ] Write the regression check first. Assert one H1; homepage word count <=260 with notes expanded; closed page height limits; exactly two genuine screenshot URLs; download/source/sample links exact; no screenshot or font resource failures; no console errors; no horizontal overflow at all listed widths; keyboard/native disclosure works; no-JS homepage content visible. Sample check covers banner, arrow/Home/End tabs, reveal/hide, home link and noindex. Check 404 page content/back link separately from HTTP status in nginx.
- [ ] Run against existing page and record meaningful RED failures (word count/composition; not setup failures).
- [ ] Implement the approved design, dependent routes, real assets, verified font and metadata. Update new screenshot provenance alongside font note. Avoid hardcoded release version/size promises. Re-read each changed file.
- [ ] Run smoke check GREEN and `git diff --check`. Build pinned nginx under the shared lock after disk check. Start a uniquely named local-only container on an unused loopback port, never touch reqistry/slowedlab or other containers. Probe home/demo/new images/font/OG/manifest/404 status and headers. Leave a proven reachable preview; record exact URL and who owns its process/container.
- [ ] Capture preliminary desktop/mobile using actual Playwright MCP (only if no other child is using the shared MCP browser). If unavailable, report exact failure; Python screenshots do not count as MCP proof. Independent visual QA follows anyway.
- [ ] Inspect diff and `git status --short`, stage only named product/task files, commit as one rebuild commit. No push. Write report `/tmp/opencode/flutterguard-minimal/implementation.md`: status, SHA, changed paths, RED/GREEN commands/results, container URL, font source/license, images dimensions/bytes/provenance, screenshots, unresolved risks.

**Done:** approved short design rendered, runnable regression passes, nginx integration verified, product diff committed without unrelated files. Rollback: controller may reverse only this rebuild commit after inspecting working state; never reset/clean the whole checkout.

## Task 2: Independent proof and final review

**Owner:** `ui-review` (Playwright MCP) and `code-review`, read-only, parallel if resources permit. They never implement fixes or spawn children.
**Scope:** Task1 changed paths, source and test evidence; live loopback nginx URL; this approved spec.
- [ ] UI reviewer uses actual Playwright MCP to navigate, resize, screenshot, inspect console/network and computed layout, and operate links/disclosure/sample by keyboard. At least 1440x900 and390x844 screenshots of homepage and sample, plus 320/768/1280x720 overflow checks, notes expanded, 200% zoom, no-JS/reduced motion, font/image loading. Read the pixels, do not infer quality from source. Capture in `/tmp/opencode/flutterguard-minimal/screens/`; report `/tmp/opencode/flutterguard-minimal/ui-review.md` with concrete cause/fix for each issue.
- [ ] Code reviewer verifies complete diff `77d1ad7..HEAD`, spec compliance, security, asset serving, metadata, test assertions and dependent demo/404 callers. Report `/tmp/opencode/flutterguard-minimal/code-review.md`. Reuse fresh implementer test evidence, do not duplicate a full build just for review.
- [ ] One implementer fixes blocking findings; run covering checks. Re-review only affected paths with original reviewers. No new aesthetic expansion beyond approved direction.
- [ ] Primary checks final git diff/status, confirms preview responds and unrelated work survived, records checks and screenshots, and closes with local URLs. Do not deploy or publish.

**Acceptance evidence:** compactness/links/no-JS/overflow/sample behavior = runnable check; visual craft/contrast/focus/touch = MCP screenshots plus computed values/manual operation; shipped file/MIME/security/404 = local nginx probes; metadata consistency = source/JSON review; regression safety = final code-review verdict. Screen-reader and live production performance are NOT RUN unless actually tested.
