# FlutterGuard growth plan

Status: 2026-11-18. Written after the Play listing went live. This plan targets three
audiences with different jobs: developers shipping Flutter apps, agencies auditing client
apps, and researchers who need a reproducible artifact.

## What exists today

| Asset | State |
|---|---|
| Site | 8 pages: home, 4 guides, MobSF comparison, about, contact, privacy; static HTML, Markdown negotiation, 8-URL sitemap |
| Install paths | Google Play (live, 0.3.2) and GitHub APK (0.3.4) |
| Search | 3 clicks / 83 impressions over 28 days, average position 13; indexed home, security guide, MobSF page |
| AI surfaces | `llms.txt`, `llms-full.txt`, JSON-LD, Markdown twins, robots policy allowing answer bots |
| Third-party | 2 awesome-list PRs merged, 2 open; one dev.to post; one r/FlutterDev thread |
| Measurement | Cloudflare Web Analytics (cookieless); Search Console |

## The honest gap

Traffic is almost entirely branded. The site has no page that answers a query a buyer
types before they know the product exists, and no original data that a writer or an
assistant would cite. Everything else — metadata, performance, accessibility, agent
readability — is already at the ceiling (Lighthouse 100/100/100 on content pages).

## Strategy: three assets, one loop

1. **A checklist** for people who need a release review process, not a tool explanation.
2. **A measured corpus** — 26 shipped Flutter releases audited twice — the only original
   data in this niche that is reproducible from public APKs.
3. **A changelog with a feed** so the site shows dated activity and developers can follow it.

Then a distribution loop: every new asset is linked from the homepage, `llms.txt`, the
sitemap and the relevant guide; every merged awesome-list entry and post points back.

## Audience map

| Audience | Job | Entry query | Asset |
|---|---|---|---|
| Flutter developers | "Is my release leaking anything?" | flutter app security, proguard flutter, inspect flutter apk | security pillar, ProGuard guide, checklist |
| Agencies / consultancies | "What do I check before handover?" | flutter app security audit checklist | checklist, MobSF comparison, corpus |
| Security researchers | "What does a real Flutter corpus look like?" | flutter apk static analysis corpus | corpus, inspection how-to |

## Content contracts

- The checklist page is a working document: grouped checks, each with why it matters and
  how to verify it, no tool pitch until the end.
- The corpus page publishes method and measured counts, never app-shaming or live secrets.
  Every claim is a string found in a public release APK, which is evidence, not proof of
  behaviour. State that limit in the page.
- The changelog is dated from real releases and says which build Play carries.

## Distribution backlog

| Channel | Action | State |
|---|---|---|
| Awesome lists | Open PRs to lists that name MobSF or Flutter security | running |
| GitHub README | Play link first, guides second | done |
| Search Console | Request indexing for new pages (UI only) | manual |
| IndexNow | POST new URLs | running |
| r/FlutterDev, Hacker News, dev.to | Post copy prepared in `launch-kit.md` | account-gated |
| Product Hunt, AlternativeTo, SaaSHub, F-Droid, IzzyOnDroid | Submit listing | account-gated |

## Measurement

- Weekly: Search Console impressions/clicks by page and query; new indexed URLs.
- Monthly: which pages earn impressions without clicks (title problem) and which queries
  have position 8–20 (content problem).
- Quarterly: re-run the corpus page numbers if the app's rule set changes.
- Do not forecast traffic from vendor statistics. Record what Search Console reports.

## 90-day cadence

- Week 1: ship checklist, corpus, changelog, feed, AI catalog; resubmit sitemap.
- Week 2–3: two more awesome-list PRs; publish the corpus summary as a dev.to post if an
  account is available; reply to Flutter security threads with the checklist.
- Week 4: review Search Console; rewrite titles that earn impressions but no clicks.
- Week 6: Spanish pillar (`seguridad flutter`) if the English pillar has impressions.
- Week 8: re-measure the corpus if detectors changed; update the page date.
- Week 12: decide whether a second comparison page is justified by query data.

## Guardrails

- No invented statistics, ratings, testimonials or user counts.
- No doorway pages or per-city/per-keyword templates.
- No claims that a finding is an exploit, or that an app is insecure.
- Publishing to a new account is a human step; prepare the asset and stop there.
