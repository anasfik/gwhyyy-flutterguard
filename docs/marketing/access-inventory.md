# Third-party access inventory

Date: 2026-11-21. What exists, what is missing, and what each missing item
unlocks. Only items that change a decision are listed; a token that grants
nothing measurable is not on the list.

## Already held and working

| Access | Scope | Used for |
|---|---|---|
| GitHub `anasfik` (gh CLI) | repo read/write, PR create | 13 awesome-list PRs, traffic API, releases |
| Google Search Console API | `sc-domain:flutterguard.dev` | impressions, clicks, positions, query reads |
| Cloudflare API | zone `dee32975072ecf91bd4ba231ce63b22c` | DNS, cache, RUM config, zone settings |
| IndexNow | key `28d5bd8a…` at site root | Bing/Yandex crawl ping on publish |
| dev.to API | user `flutterguard` (id 3686109) | publish and edit articles |
| PostHog project key | write-only, US region | pageviews and `play_cta_clicked` |
| Cloudflare Web Analytics | beacon on the site | aggregate visits (dashboard only) |

## Essential — blocks a decision, not a task

1. **Google Play Console, app-scoped read for `com.flutterguard.app`.**
   Invite a Google account as *View app information (read-only)*.
   Unlocks: installs, store-listing visitors, acquisition by source, crash-free
   rate, review replies. Without it, "did the marketing work" cannot be
   answered — listing clicks are not installs, and the site has no app telemetry
   by design. Export fallback if no invite is wanted: Play Console → Statistics →
   export the last 28 days of *Installs* and *Store listing visitors* as CSV and
   drop both into `docs/marketing/`.

2. **Play Console release permission — ship 0.4.0 over 0.3.2.**
   The hero button on the site installs **0.3.2 (updated 31 Oct)**; GitHub serves
   **0.4.0**. Every Play install today gets a build without the CLI/JSON/SARIF
   work the site describes. This is the largest single reach defect and only the
   owner can clear it. Needs an upload key or Play App Signing access, plus a
   completed release review.

3. **PostHog project read access** (personal API key, or a screenshot of the
   project home). Unlocks: whether the Play buttons are actually clicked, and
   which guides lead to them. The write key proves events are sent, not received.

## Optional — a channel, a cost, or a one-time action

| Access | Cost / gate | Unlocks | Verdict |
|---|---|---|---|
| Bing Webmaster Tools | free, ownership token | Bing index status, its own query data | Low: IndexNow already feeds Bing; GSC does not feed it, so it is additive at the margin |
| GitLab account | free | F-Droid submission | Needed only when the app is F-Droid ready; prep is done |
| Product Hunt maker profile | free | a launch moment | Plan exists, unposted; one-shot, so timing matters more than access |
| Reddit account | free | r/FlutterDev draft | Owner previously skipped; 2 organic threads already rank and are the top external referrer |
| Hacker News account | free | Show HN draft | Owner previously skipped; best fit is a 0.4.0 follow-up, not a relaunch |
| dev.to profile fields | manual, 2 min | author bio and links beside both articles | Forem API cannot edit profile fields |
| Cloudflare Web Analytics dashboard | already owned | referrers and top paths | No query tool in the MCP; needs a browser session or a Cloudflare GraphQL token |
| Paid SEO data (DataForSEO, Ahrefs, SE Ranking) | paid | real volumes, rank tracking, AI-citation share | Not required: GSC already supplies real query data for pages that rank |
| AI citation tracking (Profound, Otterly) | paid | whether assistants cite the site | `llms.txt`, `llms-full.txt` and `ai-catalog.json` are already live; tracking is measurement, not reach |

## Access that cannot help

- **GA4 measurement ID.** Never provided, and PostHog already covers the same
  questions. Adding GA4 now would duplicate collection and require a new consent
  sentence in the privacy page. Skip it.
- **App telemetry.** The Android app has no INTERNET permission. That is a
  product promise and a marketing claim; do not trade it for install analytics.
- **Play Developer Reporting API.** Disabled in the GCP project, and it exposes
  no acquisition metrics even when enabled. Console export or the API above.

## The short version

Two items move the needle: **Play Console read** (so installs are measurable) and
**Play 0.4.0 release** (so the site's promise matches what installs). Everything
else is either already held, already shipped, or a channel the owner has
deliberately skipped.
