# FlutterGuard status report

Date: 2026-11-18. Scope: discoverability and reach for developers, agencies and researchers.
Every figure below was observed, not estimated.

## 1. Site

- 11 HTML pages, each with a Markdown twin served on `Accept: text/markdown`:
  `/`, `/flutter-security/`, `/flutter-apk-inspection/`, `/proguard-flutter/`,
  `/mobsf-alternative/`, `/flutter-security-checklist/`, `/flutter-release-corpus/`,
  `/changelog/`, `/about/`, `/contact/`, `/privacy/`.
- Discovery files: `sitemap.xml` (11 URLs), `robots.txt`, `llms.txt`, `llms-full.txt`,
  `feed.xml`, `.well-known/ai-catalog.json`, IndexNow key at the site root.
- Repo: `anasfik/gwhyyy-flutterguard`, branches `main` and `work/app-landing` identical at
  `970dcee`; container `gwhyyy-flutterguard-local` healthy on port 8081 behind nginx and
  Cloudflare.

### Verification

| Check | Result |
|---|---|
| Full site gate (`tests/check_site.py`, Chromium) | 203/203 passed |
| Lighthouse `/flutter-security-checklist/` | Accessibility 100, Best Practices 100, SEO 100, zero failing audits |
| Lighthouse `/` after video re-encode | Performance 99, other categories 100 |
| HTML `Accept: text/markdown` | 200 `text/markdown`, `Vary: Accept` |
| Markdown 404 | 404 `text/markdown`, body starts `# Page not found` |
| Sitemap | 11 URLs, 0 errors, 0 warnings, processed 2026-11-18 19:44 |
| IndexNow submission | HTTP 200 |

## 2. Distribution

Awesome-list pull requests, all one added line, each anchor verified in the upstream README
before submission:

| List | Section | PR | State |
|---|---|---|---|
| ashishb/android-security-awesome | App Vulnerability Scanners | #333 | merged |
| saeidshirazi/awesome-android-security | Tools, Static Analysis | #52 | merged |
| Schmiemandev/awesome-flutter-security | Static & Dynamic Analysis | #1 | open |
| vaib25vicky/awesome-mobile-security | Android, Static Analysis | #41 | open |
| 8kSec/awesome-mobile-security | Android Scanning & Automated Analysis | #1 | open |
| NetKingJ/awesome-android-security | Static / Dynamic Analysis | #3 | open |
| user1342/Awesome-Android-Reverse-Engineering | Static Analysis Tools | #13 | open |
| ByteHackr/AwesomeMobilePentest | Reverse Engineering and Static Analysis | #3 | open |
| kyawthiha7/Mobile-App-Pentest | Android, Tools | #3 | open |

Other surfaces updated: app repo README (Play, APK, website, guides, checklist, corpus,
privacy), `skill/SKILL.md` references, `docs/METHODOLOGY.md`, `CORPUS.md`.

Publish-ready drafts exist in `docs/marketing/publish-drafts.md` for Hacker News,
r/FlutterDev and dev.to. None has been posted.

## 3. Search Console

Property `sc-domain:flutterguard.dev`.

- 28-day page dimension: 4 clicks, 181 impressions across six older pages.
  Homepage 91 impressions at position 8.8; `/proguard-flutter/` 50 at 14.9;
  `/mobsf-alternative/` 11 at 37.3; `/flutter-security/` 10 at 39.3;
  `/flutter-apk-inspection/` 9 at 19.9; `/about/` 10 at 10.3.
- The three pages published 2026-11-18 have zero impressions so far.
- Indexing state flips between reads: `/flutter-release-corpus/` is "Discovered - currently
  not indexed", `/flutter-security-checklist/` and `/changelog/` read "URL is unknown to
  Google" in the latest read. The sitemap itself is processed with no errors, so this is
  crawl-queue state, not a site fault.
- No public API exists to request indexing; that action is UI-only.

## 4. Blocked on a human

1. Request indexing for the checklist, corpus and changelog in the Search Console UI.
2. Log in to Hacker News, Reddit or dev.to and publish the matching draft. Product Hunt,
   AlternativeTo, SaaSHub, F-Droid and IzzyOnDroid also require accounts; F-Droid and
   IzzyOnDroid additionally require a reproducible build recipe.
3. Report the Play listing state if it changes.

## 5. Next checkpoint

2026-12-02: confirm all three pages are indexed, record their first impressions and
positions, and compare the 28-day totals against the 4/181 baseline. A page with impressions
but no position movement after 28 days gets a rewrite; a page with no impressions gets a
content or internal-link review instead.
