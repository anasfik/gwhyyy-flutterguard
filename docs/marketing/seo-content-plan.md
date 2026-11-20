# FlutterGuard SEO content plan

> Historical research and publication log below. For current positioning,
> the 2026-11-20 GSC window, route inventory and follow-up priorities, use
> `2026-11-20-site-audit.md` and `growth-plan.md`. Indexing and ranking states
> in this log are observations on their stated dates, not current guarantees.
> The new `/cli/` page documents a shipped setup path. FAQ markup describes
> visible answers; it is not a promise of Google FAQ rich results.

Status: 2026-11-02, after the MobSF page. Companion to `launch-kit.md`, which holds positioning, channel copy and
directory work. This file covers search: what the site targets, why, and how it will be judged.

## Measured baseline

Search Console, property `sc-domain:flutterguard.dev`, 28 days ending 2026-11-02:

| Metric | Value |
| --- | --- |
| Clicks | 3 |
| Impressions | 77 |
| Queries | 6 |
| Indexed URLs | 1 (the homepage) |

| Query | Clicks | Impressions | Average position |
| --- | --- | --- | --- |
| flutter guard | 2 | 5 | 3 |
| flutter security | 0 | 4 | 51.5 |
| flutter vulnerabilities | 0 | 1 | 20 |
| how do i find security vulnerabilities in flutter and react native applications? | 0 | 1 | 6 |
| proguard flutter | 0 | 1 | 45 |
| seguridad flutter | 0 | 2 | 44 |

Two facts follow from that table. Brand demand is already satisfied by the homepage. Every
non-brand query lands on a page about the app rather than a page about the question, and
`flutter security` sits at position 51 with no page written for it.

No third-party volume figures are used in this plan. Where a query has no Search Console data,
it is marked unmeasured instead of estimated.

## Keyword map

| Query | Intent | Target | State |
| --- | --- | --- | --- |
| flutter guard | Branded, navigational | `/` | Position 3 |
| flutter security | Informational, broad | `/flutter-security/` | Page shipped, not yet indexed |
| flutter vulnerabilities | Informational, checklist | `/flutter-security/` | Page shipped, not yet indexed |
| how do i find security vulnerabilities in flutter and react native applications? | Long-tail how-to | `/flutter-security/`, then `/flutter-apk-inspection/` | Page shipped, not yet indexed |
| proguard flutter | Informational, tooling confusion | `/proguard-flutter/` | Page shipped, not yet indexed |
| how to inspect a flutter apk | Informational, how-to (unmeasured) | `/flutter-apk-inspection/` | Page shipped, not yet indexed |
| mobsf alternative | Commercial comparison (unmeasured) | `/mobsf-alternative/` | Page shipped, not yet indexed |
| seguridad flutter | Spanish, informational | none | Gap: not targeted |

`seguridad flutter` is recorded demand with no Spanish content. It stays a gap until the
English cluster has data; translating a page that has not ranked yet spends effort before the
answer is known.

## What shipped on 2026-11-02

Four static pages, each with a single intent, one H1, a unique title under 60 characters, a
description between 120 and 160 characters, an exact canonical, and `TechArticle`, `BreadcrumbList`
plus `FAQPage` JSON-LD. Each opens with a one-paragraph answer and closes with the questions people
type into a search box. All are server-rendered, carry the site's CSP and cache headers, and work
with JavaScript disabled.

| URL | Title | Job |
| --- | --- | --- |
| `/flutter-security/` | Flutter security: what a release APK exposes | Pillar. The checks that find real problems in a shipped APK, and what static inspection cannot prove. |
| `/flutter-apk-inspection/` | Flutter APK inspection: reading a release on Android | How-to. Phone-first workflow, desktop commands, triage rules that avoid false alarms. |
| `/proguard-flutter/` | ProGuard for Flutter: what R8 and obfuscation hide | Explainer. Android shrinking versus Dart obfuscation, and what remains readable. |
| `/mobsf-alternative/` | MobSF alternative for auditing Flutter APKs | Comparison. What MobSF does well, where a Flutter release differs, and when each tool is the better fit. |

Each page differentiates on the released artifact. The SERP for `proguard flutter` is
tutorials without artifact evidence, and `how to inspect a flutter apk` mostly returns Flutter
Inspector, which debugs widgets rather than reading a package. The pages say so explicitly and
then show the APK-layer method.

## Internal links

- Homepage `#guides` section links all four pages; the navbar points at `#guides`.
- Each guide links the other three and the homepage in its "Continue reading" block.
- Every guide ends with the same install action: GitHub APK release, then source.
- Breadcrumbs on each guide return to the homepage.

No orphan pages, no cross-links to unrelated sections.

## Structured data

- Guides: `TechArticle` with headline, description, dates, author, publisher, image and an
  `about` reference to the `SoftwareApplication`; `BreadcrumbList` matching the visible
  breadcrumb; `FAQPage` matching the visible questions and answers verbatim.
- Homepage: `SoftwareApplication` and `FAQPage`, both already matching visible content
  verbatim. Do not add ratings, review counts or version numbers that the app does not have.

## Measurement

Review at 14 and 28 days after indexing, using the same 28-day window:

1. Search Console, per page: impressions, clicks, average position for each mapped query.
   The target for `/flutter-security/` is a position better than the homepage's 51.5 on
   `flutter security`; the target for `/proguard-flutter/` is better than 45.
2. Search Console, index status: all five URLs indexed, no canonical mismatch.
3. Cloudflare Web Analytics: page views and referrers per guide, to see whether the pages pull
   traffic the homepage did not.
4. Rich results: confirm `TechArticle` and `BreadcrumbList` are detected on each guide.

If a guide earns impressions but no clicks after 28 days, the fix is the title and description,
not a new page. If it earns no impressions, the query was wrong and the page should be rewritten
or removed rather than multiplied.

## Backlog, in order

1. Request indexing for the four guides in Search Console. Sitemap resubmitted 2026-11-02 22:18.
   The API can inspect but cannot request indexing; that click is a Search Console UI action.
2. Wait for 28 days of data before adding a page. Remaining unmeasured candidates: reading
   `libapp.so` strings and a walkthrough with a real open-source APK. The MobSF comparison page
   shipped early because the comparison intent had no page at all.
3. Spanish page for `seguridad flutter` once the English pillar shows it can rank.
4. Per-guide Open Graph images shipped with the pages; check social referrals before making more.

## Guardrails

- Keep the claims discipline from `launch-kit.md`: a finding is a lead, not a verdict. Static
  inspection shows what shipped, not what is exploitable.
- No keyword stuffing, no doorway pages, no invented statistics or volumes.
- The Play listing is live; link it as the primary install path with the GitHub APK as fallback.
- Every page keeps the offline, no-account, MIT facts accurate.

## Addendum: 2026-11-18

Three supporting pages shipped with the growth plan: `/flutter-security-checklist/`
(release-review intent), `/flutter-release-corpus/` (measured evidence from 26 public release
APKs), and `/changelog/` with `/feed.xml`. `.well-known/ai-catalog.json` lists every page and
its Markdown twin. The homepage links six cards; sitemap now carries 11 URLs, resubmitted
2026-11-18 19:44. IndexNow returned 200 for the three new URLs.

Search Console state at publication: the three new URLs are unknown to Google, which is
expected on day one. Request indexing from the UI; the API cannot do it. The checklist page
scores 100 accessibility / 100 best practices / 100 SEO in Lighthouse with no failing audits.

Do not add another page until the corpus and checklist have 28 days of impressions. The next
candidates are a Spanish pillar and a walkthrough on a real open-source APK, in that order.

### Measurement, 2026-11-18 (28-day window ending today)

Search Console, `sc-domain:flutterguard.dev`, page dimension: 4 clicks / 181 impressions across
six pages. Homepage 91 impressions at position 8.8. `/proguard-flutter/` 50 impressions at
14.9; `/mobsf-alternative/` 11 at 37.3; `/flutter-security/` 10 at 39.3;
`/flutter-apk-inspection/` 9 at 19.9; `/about/` 10 at 10.3. The three pages published today
have no impressions yet. Query dimension reports 26 impressions and 1 click, because Search
Console withholds low-volume queries; use the page dimension for totals.

Indexing: `/changelog/` is "Discovered - currently not indexed"; the checklist and corpus are
still "URL is unknown to Google". Request indexing for all three from the UI, then leave them
alone for at least two weeks.

Distribution added the same day: PRs to 8kSec/awesome-mobile-security (#1, Android scanning
table) and NetKingJ/awesome-android-security (#3, static/dynamic tools), both open with a
one-line diff. Together with the two merged lists this gives four live entries and two open
PRs.

Next measurement: 2026-12-02. Success for the new pages is first impressions, then a position
better than 20 on their mapped queries; a rewrite follows only if there are impressions and no
movement after 28 days.
