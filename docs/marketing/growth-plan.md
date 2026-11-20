# FlutterGuard growth plan

Updated: 2026-11-20. This is the website delivery and follow-up plan, not a new
budget or a replacement for the separate long-form marketing strategy.

## Current evidence

| Surface | State |
|---|---|
| Product | Android app, source-built CLI and shared JVM engine, version 0.4.0 |
| Distribution | GitHub 0.4.0 APK; public Play last observed at 0.3.2 |
| Public content | 12 canonical pages after this rework, including the new `/cli/` guide |
| Search | GSC page rows: 4 clicks / 180 impressions, 2026-10-21 through 2026-11-17 |
| Search opportunity | `/proguard-flutter/`: 49 impressions, 0 clicks, average position 15.1 |
| Measurement | Existing Cloudflare page-view beacon and GSC; no verified FlutterGuard PostHog dataset |
| Unknown | Install conversions, CLI adoption, retention, paid budget and current third-party referral performance |

These are small samples, not a basis for traffic forecasts. See the dated audit
for the route inventory, source checks and measurement limitations.

## Strategy

Make the expanded product understandable before adding acquisition channels.
The homepage explains the evidence and directs people to the Android install
paths or a complete CLI setup guide. Existing topic guides keep their URLs and
search intent.

| Stage | Work | Leading signal | Owner |
|---|---|---|---|
| Acquisition | Preserve the security, ProGuard and APK-inspection guides; correct the MobSF comparison | Existing pages retain impressions and earn relevant clicks | Maintainer |
| Activation | Give Android and terminal users a usable first step, prerequisites and failure guidance | First-scan feedback; conversion data currently unavailable | Maintainer |
| Retention | Explain Android release comparisons and link the release feed | Repeat use is unmeasured; qualitative feedback only | Maintainer |
| Referral | Prepare a factual release announcement and directory descriptions | Approved placements and their observed referral visits | Maintainer |
| Revenue | Keep the free MIT product positioning | No new paid offer or revenue target in this task | Maintainer |

## Next 30 days

1. Deploy the reviewed revision. Verify the live `/cli/`, homepage, feed, sitemap,
   social image and negotiated Markdown. A successful push is not a deployment.
2. After live verification, choose one announcement from `publish-drafts.md`.
   Check the channel's current rules and obtain publication approval first.
3. Review GSC after a complete 28-day post-deployment window. Compare the same
   pages and queries, accounting for low volume and publication timing.
4. Read the existing ProGuard page against queries that earn impressions. Improve
   an answer only when the query and page disagree; do not create a duplicate
   page for each wording.
5. Ask willing users which evidence was useful and which matches were false
   leads. Do not add app tracking to answer this question.

## What stays out

- Paid acquisition, pricing changes, signup forms and newsletter infrastructure.
- Programmatic pages without a real dataset or separate search intent.
- A new language without a useful translated experience and evidence of demand.
- Claims that the site has reached a quality ceiling or will rank because it
  contains JSON-LD or `llms.txt`.
- Automatic social posting, outreach, new directory submissions or indexing
  requests. Prepare the asset; approval comes before the external action.

## Measurement rules

Use GSC page rows for the reported page totals, not the smaller privacy-filtered
query set. Keep observation dates with all figures. Distinguish page views,
download-link clicks, store installs and first successful scans; none is a proxy
for the others. Do not treat one zero-click window as proof a title failed.

Field Core Web Vitals and INP remain unmeasured in this session. The local
three-run navigation samples are lab regression evidence only.
