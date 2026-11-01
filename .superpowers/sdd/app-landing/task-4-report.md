# S4 - App metadata rewrite: report

- Repo: /home/gwhyyy/real-projects/gwhyyy-flutterguard
- Branch: work/app-landing
- BASE (verified via `git rev-parse HEAD` before edits): 47441122224a9ce11e08b34bd8e0b55bdb7e8916
- HEAD after commit: 669f6c94f643b575e931ea170677d50803161e78
- Commit message: `docs(seo): rewrite metadata for app landing (S4)`
- Model: opencode-go / deepseek-v4.1-flash
- Files changed (7, exactly the slice): site.webmanifest, sitemap.xml, llms.txt, llms-full.txt, humans.txt, 404.html, robots.txt
- Not touched: index.html, styles.css, site.js, demo/*, Dockerfile, nginx.conf, icons, og-image.png, progress.md

## Changes

### site.webmanifest
- description rewritten: "Offline on-device Flutter APK security audit for Android. Grades A to F with evidence, no network, MIT."
- Kept: start_url "/", scope "/", display "standalone", background_color/theme_color #0a0c0b, icons 192x192 and 512x512.

### sitemap.xml
- Exactly two <url> entries: https://flutterguard.dev/ (lastmod 2026-11-01, priority 1.0) and https://flutterguard.dev/demo/ (lastmod 2026-11-01, priority 0.8).
- Early lastmod 2026-10-01 replaced by 2026-11-01 (content rewrite date).

### llms.txt
- Rewritten as an app description: on-device Flutter APK audit, Android 8.0+, no network access, MIT.
- Links: canonical, releases/latest download, source repo, privacy policy, work@gwhyyy.com, GitHub issues, maintainer Anas Fikhi.
- Sections: What it reads / Grades (A, C, F as triage labels, explicitly "not a security certification") / Offline by design (no INTERNET permission) / Limits (all 9 required limits verbatim) / Legal.
- No booking, no consulting scope/method/engagement language.

### llms-full.txt
- Full app reference: what it is, install (Android 8.0 / API 26, APK from releases/latest, no account/root/PC), what it reads (APK container, manifest, release contents, libapp.so AOT strings/symbols, signing, route-like strings), grades as triage labels, offline/private section, all 9 limits, legal, support links + /demo/.

### humans.txt
- Maintainer: Anas Fikhi; Role: Flutter and Software Engineer; contact work@gwhyyy.com; License: MIT; no booking link, no Calendly.
- Removed em-dash in THANKS line, replaced "Founder & reviewer" with "Maintainer", dropped LinkedIn/portfolio-of-service phrasing. Last update 2026-11-01.

### 404.html
- Title "Not found | FlutterGuard"; description de-consulting'd; h1 "That report does not exist."; body "The audit starts at the homepage."; home link + mailto contact link (subject no longer "Manual Security Audit").
- Kept `noindex, follow`, canonical to /, favicon/apple-touch-icon/stylesheet, skip-link and main landmark.

### robots.txt
- Allow/Deny policy byte-identical (verified: only 2 comment lines changed). 27 directive lines before and after.
- Comment fixes: "so the service can be cited" -> "so the app can be cited"; em-dashes in the two comments replaced with hyphens.

## Verification (commands + output)

1. Manifest JSON
```
$ python3 -m json.tool site.webmanifest >/dev/null; echo json_rc=$?
json_rc=0
```

2. Sitemap parse
```
$ python3 -c "import xml.dom.minidom as m;d=m.parse('sitemap.xml');print([x.firstChild.data for x in d.getElementsByTagName('loc')])"
['https://flutterguard.dev/', 'https://flutterguard.dev/demo/']
```
(exactly 2 <loc>)

3. Prohibited strings
```
$ grep -rEic 'manual flutter|calendly|book a call|why me|666\+|play\.google\.com' site.webmanifest sitemap.xml llms.txt llms-full.txt humans.txt 404.html robots.txt
site.webmanifest:0
sitemap.xml:0
llms.txt:0
llms-full.txt:0
humans.txt:0
404.html:0
robots.txt:0
```
All counts 0 (grep exit 1 = no matching lines).

4. No em/en dash
```
$ grep -n '—\|–' site.webmanifest sitemap.xml llms.txt llms-full.txt humans.txt 404.html robots.txt
(no output, exit 1)
```

5. Docker build
```
$ docker build -t fg-site:local . >/dev/null 2>&1; echo docker_rc=$?
docker_rc=0
```

6. Served smoke test (container on :8099, removed after)
```
/                  200 text/html; charset=utf-8
/site.webmanifest  200 application/manifest+json
/sitemap.xml       200 text/xml; charset=utf-8
/llms.txt          200 text/plain; charset=utf-8
/llms-full.txt     200 text/plain; charset=utf-8
/humans.txt        200 text/plain; charset=utf-8
/robots.txt        200 text/plain; charset=utf-8
/nope-xyz          404 text/html; charset=utf-8   (nginx error_page 404 /404.html at nginx.conf:41)
```

7. Required-limit coverage grep (both llms files)
evidence not proof, runtime hooking/traffic interception, AOT machine code/not decompiled Dart, routes as candidate strings not a navigation graph, AAB/bundletool, structural signature, ROMs block APK reads, scan only owned/authorized apps, uninstall deletes reports/history: all present in both files.

8. Commit scope
```
$ git show --stat --oneline HEAD
669f6c9 docs(seo): rewrite metadata for app landing (S4)
 7 files changed, 96 insertions(+), 81 deletions(-)
```
Working tree after commit shows no S4 file dirty; other dirty paths (apple-touch-icon.png, favicon.svg, icon-192.png, icon-512.png, og-image.png) belong to parallel S5 and were deliberately left unstaged/untouched.

## Concerns

1. /demo/ is in sitemap.xml but demo/ did not exist on disk at commit time (S3 parallel task owns it; Dockerfile has no demo COPY lines yet). Until S3 lands, https://flutterguard.dev/demo/ returns 404 and the sitemap advertises a 404. Resolve at S6/S7 by confirming demo/index.html exists and is served; no S4 edit can fix that.
2. site.webmanifest description says "Grades A to F" to stay consistent with index.html meta copy; llms.txt/llms-full.txt state "A, C or F are triage labels". Both are non-numeric and non-invented, but if a reviewer wants exact wording parity, change index.html (out of S4 scope) rather than the manifest.
3. sitemap lastmod is the rewrite date (2026-11-01), not a content-hash; treat as a manual bump on future content edits.
4. robots.txt comments changed (needed to drop em-dashes). Directive lines are unchanged, so crawl policy is identical.
5. 404.html uses inline padding/justify styles; CSP permits style-src 'unsafe-inline' in _headers, so it renders. No script, no new landmarks removed.

---

# S4 review fix round 1 (S4R1)

BASE: 64fab27babdde9e8486239148973e5a85904f5e9 (branch work/app-landing)

## Finding fixed (Important, Spec FAIL)
site.webmanifest:4 description said "Grades A to F", which implies grades B, D and E exist. The product scale is A/C/F anchors: index.html:257 legend plus index.html:262-270, demo/index.html:43, llms.txt:3, llms-full.txt:5. This also retires concern 2 from the S4 report above, which had explicitly deferred the manifest wording.

## Change
One line, description string only:

```
-  "description": "Offline on-device Flutter APK security audit for Android. Grades A to F with evidence, no network, MIT.",
+  "description": "Offline on-device Flutter APK security audit for Android. Grades A, C or F with evidence, no network, MIT.",
```

All other manifest fields are byte-identical (name, short_name, start_url, scope, display, background_color, theme_color, icons 192/512). No em-dash. Valid JSON.

## Verification
```
$ python3 -m json.tool site.webmanifest >/dev/null; echo $?
0
$ grep -c 'A to F' site.webmanifest
0
$ grep -c '—' site.webmanifest
0
$ git diff --stat
 site.webmanifest | 2 +-     (Dockerfile:1 is pre-existing dirt from another task, unstaged, untouched here)
$ git diff --name-only
site.webmanifest
$ docker build -t fg-site:local .
build_exit=0   (nginx image, 6/6 steps, tagged fg-site:local)
```

## Scope respected
Edited only site.webmanifest. No changes to icons, og-image, favicon (S5), demo/*, Dockerfile, index.html, styles.css or other S4 files. ledger/progress.md untouched.

## Concerns
None new. The A/C/F wording now matches all five other surfaces, so no residual scale drift remains in site metadata.
