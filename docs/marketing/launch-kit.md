# FlutterGuard launch kit

Status: 2026-11-02. Site live at https://flutterguard.dev. App v0.3.3 on GitHub.
Blocking item: the Google Play listing (`com.flutterguard.app`) returns 404. The hero CTA is
kept on Play by decision; every visitor hits a dead store page until Google publishes it.

## Positioning

For Flutter developers and mobile-security reviewers who need to inspect an app they did not
build, FlutterGuard reads a released APK on the Android device itself: libraries, endpoints,
exposed strings, manifest and package policy, with a local report. No root, no account, no
network permission, MIT licensed.

Against the alternatives:

- Enterprise SAST (Black Duck, Ostorlab, Appknox) audits source in CI, priced and sold to
  security teams.
- Desktop CLI tooling needs a workstation, a JDK and setup time.
- FlutterGuard is the only option that runs on the phone, offline, against the shipped
  artifact a user actually installs.

Do not claim it proves an app is exploitable. The site FAQ already says a finding is a lead,
not a verdict. Keep that line in every channel.

## Audience

1. Flutter developers shipping to Play who want a pre-release check without CI wiring.
2. Security reviewers and bug-bounty hunters triaging APKs on a phone.
3. Privacy-conscious users checking what an app bundles.

## Proof points (verified 2026-11-02)

- v0.3.3 APK published 2026-11-01; earlier v0.3.0 and v0.3.1 also have APKs.
- 31 GitHub stars.
- MIT licence, source public.
- Offline; the app does not request the INTERNET permission.
- Existing coverage: one dev.to post and one r/FlutterDev beta thread, both already sending
  referral traffic (Search Console).

## Search baseline (Search Console, 28 days ending 2026-11-02)

6 queries, 3 clicks, 77 impressions, homepage average position ~15.

| Query | Clicks | Impressions | Position |
|---|---|---|---|
| flutter guard | 2 | 5 | 3 |
| flutter security | 0 | 4 | 51.5 |
| flutter vulnerabilities | 0 | 1 | 20 |
| how do i find security vulnerabilities in flutter and react native applications? | 0 | 1 | 6 |
| proguard flutter | 0 | 1 | 45 |
| seguridad flutter | 0 | 2 | 44 |

Read: brand demand exists at position 3. Non-brand queries sit at positions 20-51 with almost
no impressions, so the site has no informational page competing for them. The single URL is
indexed and canonical. Sitemap is valid with 1 URL.

## Launch gate

Simple, lovable, complete check:

- Simple: audit one APK, one job. Yes.
- Lovable: real recorded demo, one-tap install, local report. Yes, once install works.
- Complete: discovery, inspection, report, FAQ, privacy notice. Yes.

The only incomplete piece is distribution: Play is not public. Ship the launch the day the
listing resolves, or switch the hero CTA to GitHub if that slips past one week.

## Channels

### Owned

- Site: https://flutterguard.dev (single page, demo video, FAQ, contact).
- GitHub: https://github.com/anasfik/FlutterGuard (releases, issues, source).
- No email list. Do not fake one; a release-watch issue or GitHub "Watch > Releases" is the
  honest substitute.

### Rented

- r/FlutterDev: the beta thread already exists. Post again only with a real release and
  disclose authorship. Follow the subreddit self-promotion rule.
- Hacker News: Show HN, once, when the install path works.
- dev.to: the existing post ranks as a referring URL. Publish one technical follow-up.
- X and LinkedIn: short announcements, link to the site, no engagement bait.

### Borrowed

- Flutter newsletters and podcasts (Flutter Weekly, It's All Widgets, Flutter Dev Podcast).
  Pitch the "audit the shipped artifact, not the repo" angle.
- Mobile-security communities (OWASP MAS, r/androiddev) only with a technical write-up, not a
  product drop.

## Announcement copy

### Show HN

Title: `Show HN: FlutterGuard - audit a released Flutter APK on your phone`

Body:

> I kept wanting to check what a published Flutter app actually ships: which libraries, which
> endpoints, which strings are sitting in the binary. Desktop tooling means a JDK, a decompiler
> and setup time, so I built the check into an Android app instead.
>
> FlutterGuard opens an APK on the device, reads the manifest and package policy, the bundled
> libraries, endpoints and exposed strings, then writes a local report. It has no internet
> permission, no account and no telemetry. MIT licensed.
>
> APK: https://github.com/anasfik/FlutterGuard/releases/latest
> Site and demo: https://flutterguard.dev
>
> A finding is a lead, not proof of exploitability. I would like feedback on the report format
> and on which Flutter-specific checks matter most.

### r/FlutterDev

Title: `FlutterGuard v0.3.3 - inspect a released Flutter APK on the phone itself`

Body: state the problem in two sentences, list what it reads, link the APK and the site, say
it is MIT and offline, ask which checks are missing. Disclose that you built it. Do not lead
with the Play link until the listing is public.

### dev.to follow-up

Title: `What a released Flutter APK exposes (and what it does not)`

Outline: what ships inside a release APK; what `libapp.so` and the asset bundle reveal; why
strings and endpoints are leads rather than findings; a short walkthrough of a report; the
limits of static inspection. Link the app once, at the end.

### X thread

1. A released Flutter APK carries more than your Dart code: libraries, endpoints, strings,
   manifest policy.
2. Desktop tooling needs a JDK and setup. I wanted the check on the phone.
3. FlutterGuard opens the APK on-device and writes a local report. Offline, no account, MIT.
4. It reads libraries, connections, exposed strings, package policy and app structure.
5. A finding is a lead, not proof. The report says so.
6. APK and demo: https://flutterguard.dev

### LinkedIn

One paragraph: the problem, what the app does, offline and MIT, link. No hashtag wall.

## Directories and listings

Submit only after the Play listing or GitHub APK path is confirmed working from a logged-out
browser. Track status in this table.

| Directory | URL | Notes |
|---|---|---|
| Product Hunt | https://www.producthunt.com/posts/new | Needs gallery, tagline, first comment |
| AlternativeTo | https://alternativeto.net/manage/add-app/ | List as alternative to MobSF |
| SaaSHub | https://www.saashub.com/submit | Free listing |
| Awesome Flutter Security | https://github.com/search?q=awesome+flutter+security | PR to the list, follow its format |
| Awesome Android Security | https://github.com/search?q=awesome+android+security | PR, same |
| F-Droid | https://f-droid.org/en/docs/Submitting_to_F-Droid_Quick_Start_Guide/ | Only if the build is reproducible and free of proprietary deps |
| IzzyOnDroid | https://gitlab.com/IzzyOnDroid/repo | Needs a public reproducible APK |
| Hacker News | https://news.ycombinator.com/submit | Show HN, once |

Skip paid directories and any "submit to 100 sites" service.

## Measurement

Today: Search Console plus nginx access logs. No site analytics tag is installed, so on-site
behavior is unmeasured.

Recommended, in order:

1. Add a privacy-preserving page counter. Cloudflare Web Analytics or a log-based weekly
   report both avoid cookies and avoid changing the app's no-telemetry claim.
2. If GA4 is required, create a web stream for `flutterguard.dev`, add the tag, and extend the
   CSP to allow `googletagmanager.com` and `google-analytics.com`. Update the privacy notice.
3. Tag every campaign link with `utm_source`, `utm_medium`, `utm_campaign`.
4. Weekly: GSC queries with impressions and position 11-30, clicks, and which channel produced
   the install link click.

Baseline to beat: 3 clicks and 77 impressions per 28 days.

## 30-day cadence

- Week 1: confirm install path, apply host header fix, re-run the 76-check gate, add page
  measurement.
- Week 2: publish the dev.to technical follow-up; pitch two Flutter newsletters.
- Week 3: Show HN and r/FlutterDev release post, same day, respond all day.
- Week 4: review GSC queries, write one page for the strongest informational query, submit
  directory listings.

## Claims discipline

- Do not say "finds vulnerabilities". Say "surfaces libraries, endpoints and exposed strings".
- Do not say "available on Google Play" until the listing resolves.
- Do not quote star counts in copy that will age; link the repo instead.
- Do not add testimonials or ratings that do not exist.
