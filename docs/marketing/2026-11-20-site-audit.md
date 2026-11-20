# FlutterGuard site audit and rework

Date: 2026-11-20. Website baseline: `784fcec`. Product source: `1c28d0f`,
FlutterGuard 0.4.0. Deployment remains separate from source delivery.

## Findings that determine the rework

| Priority | Finding | Evidence | Action |
|---|---|---|---|
| High | The homepage describes a phone-only product | Baseline `index.html` hero, workflow and SoftwareApplication description | Explain Android, source-built CLI and shared engine together |
| High | Confidence language no longer matches the engine | Old “a finding is a lead” copy versus `Confidence.kt` and confirmed-only grading | Separate artifact facts, suspected matches and inventory |
| High | The comparison page assigns CI only to MobSF | Baseline `/mobsf-alternative/` copy | Explain both tools fairly; FlutterGuard now has JSON/SARIF CLI output |
| High | Downloadable product and source modules can be confused | 0.4.0 release has an APK, not a CLI binary or Maven package | Label CLI/engine “build from source” and document prerequisites |
| Medium | Machine references repeat the mobile-only story | Baseline homepage Markdown, LLM references and AI catalog | Keep HTML, Markdown, catalog and sitemap consistent |
| Medium | Old media could imply visual verification of 0.4.0 | Android recording supplied on 2026-11-02 | Label it as recorded before 0.4.0 |
| Medium | Existing launch documents contain obsolete versions and unsupported exclusivity | `docs/marketing/` | Replace current drafts; retain historical records with dated warnings |
| Medium | Pushed source was not reflected on the live host | Earlier live changelog ended at 0.3.4 while source included 0.4.0 | Treat deployment verification as an explicit remaining gate |

## Public route inventory

| Route | Intent | Primary next action |
|---|---|---|
| `/` | Product and workflow selection | Android installation or CLI guide |
| `/cli/` | Terminal/CI setup | Build and run the documented scan command |
| `/flutter-security/` | Release-artifact security evidence | Apply the review workflow |
| `/flutter-apk-inspection/` | Inspecting a Flutter APK | Follow phone or terminal instructions |
| `/proguard-flutter/` | R8 versus Dart obfuscation | Review what remains in a release |
| `/mobsf-alternative/` | Choosing a static-review workflow | Compare scope, then choose a tool |
| `/flutter-security-checklist/` | Pre-release review process | Work through the checklist |
| `/flutter-release-corpus/` | Historical public APK observations | Read method and limitations |
| `/changelog/` | Release and install-channel history | Choose the correct distribution channel |
| `/about/` | Maintainer and product identity | Read source or start a workflow |
| `/contact/` | Support and security-report routing | Email or repository issue |
| `/privacy/` | Data-handling boundaries | Understand local scans and deliberate exports |

Every canonical route has a direct Markdown twin. The existing nginx configuration
negotiates `Accept: text/markdown` and sets `Vary: Accept`. A plain Python file
server cannot prove that delivery contract. The robots training opt-out is
preserved; discovery files do not override it or guarantee AI citations.

## Search demand: observed, not estimated

Source: GSC `sc-domain:flutterguard.dev`, final data for 2026-10-21 through
2026-11-17. Page-dimension rows:

| Page | Clicks | Impressions | Average position |
|---|---:|---:|---:|
| Homepage | 4 | 91 | 8.8 |
| `/proguard-flutter/` | 0 | 49 | 15.1 |
| `/mobsf-alternative/` | 0 | 11 | 37.3 |
| `/about/` | 0 | 10 | 10.3 |
| `/flutter-security/` | 0 | 10 | 39.3 |
| `/flutter-apk-inspection/` | 0 | 9 | 19.9 |

The returned page rows total 4 clicks and 180 impressions. Query rows are
privacy-filtered; do not sum them as total search traffic. Relevant observed
queries include `flutter security` (6 impressions, position 40.7),
`proguard flutter` (3, position 12), and `mobsf alternative` (1, position 19).
These samples are too small to establish conversion or copy winners.

Keep existing topic URLs and intent. `/cli/` is justified by a new product setup
path, not by invented search volume. No programmatic page expansion is warranted.

## Research and analytics limits

- MobSF's official site and documentation describe static and dynamic analysis,
  multiple platforms and API/CI workflows. It is not accurate to say it cannot
  support Flutter review or CI.
- The site uses a Cloudflare Web Analytics beacon. Its dashboard data was not
  retrieved. No verified FlutterGuard PostHog dataset was available.
- Download conversions, installed users, CLI adoption, current referral mix and
  retention are unmeasured here. No new tracking was added.
- No paid keywords, market-size estimates, testimonials or adoption counts are
  invented.

Sources: [MobSF](https://mobsf.github.io/Mobile-Security-Framework-MobSF/),
[official setup docs](https://mobsf.github.io/docs/running_mobsf_docker.md),
the product repository's README, `docs/cli.md`, engine and CLI source.

## Baseline and proof method

- Baseline strict local nginx browser contract: **203/203 passed**.
- Updated workflow contracts first failed: **195/220**, with 25 expected failures
  for the missing product paths and CLI content.
- Baseline navigation lab: three fresh Chromium contexts per viewport,
  1440×900 and 390×844, cache disabled, unthrottled localhost, five seconds of
  observation. Median LCP: 188 ms desktop (140–308), 116 ms mobile (112–164).
  Measured CLS was 0 in each sample.
- These are local regression measurements, not field Core Web Vitals or INP.
  Chrome DevTools MCP could not start its configured Chrome executable.
  Lighthouse and field data were not available through that route.
## Final results after implementation

Measured on the revised tree through the same strict local nginx config
(127.0.0.1:8786), source branch `work/changelog-0.4.0` on top of `784fcec`:

- Strict browser contract: **254/254 passed**, exit 0, on the exact shipped
  bytes. Covers all 12 routes in
  HTML and Markdown with `Vary: Accept`, schemas, media, eight viewport widths
  from 320 to 1920, 200% text, anchor clearance under the sticky header,
  no-JS navigation, video failure fallback, security and cache headers, plus
  keyboard-scrollable code blocks on every route and CLI command blocks that
  fit their container.
- Accessibility: axe-core 4.11.4 sweep over the same 12 routes at 1440×900 and
  390×844, tags WCAG 2.0/2.1/2.2 A and AA — **24 runs, 0 violating nodes**.
  The sweep found real issues on the first pass (widened code blocks were not
  keyboard scrollable); those `<pre>` blocks now carry `tabindex="0"` and the
  committed suite asserts it.
- Navigation lab, same method and conditions as the baseline: three fresh
  Chromium contexts per viewport, cache disabled, unthrottled localhost, five
  seconds of observation. LCP median **140 ms desktop** (136–220) and
  **136 ms mobile** (120–168); CLS 0 in all six samples; same-origin transfer
  about 3.07 MB. This is a local lab regression check, not field Core Web
  Vitals, and INP was not measured.
- Live `https://flutterguard.dev` was unreachable from this machine during the
  work (connect timeout), so **nothing about the deployed site is verified
  here**. Deployment remains a separate owner action.
- The Docker image was not built: its pinned `nginx:stable-alpine` digest is
  not present locally and no pull was performed. Packaging parity is asserted
  only by the committed `COPY` list, not by a built image.
- Two independent read-only reviews ran against the diff. The code review
  found the audit's own pass count stale and two weak assertions, plus a
  build recipe missing its Android SDK requirement; the UI review returned
  not-ready on clipped CLI command blocks and a 1.96:1 focus ring on the dark
  call-to-action. All of it was fixed and re-verified: code blocks wrap, the
  focus ring uses the accent at about 10.5:1, the build page names the SDK and
  `ANDROID_HOME`, diagnostics are asserted by phrase instead of character, and
  the count above is a fresh run.
