# FlutterGuard 0.4.0 website design

## Intent

Replace the phone-only story with a complete, friendly explanation of FlutterGuard's Android, CLI/CI and shared-engine workflows. Keep the static site, existing green identity, real media, search routes and privacy choices. The founder delegated execution; these reversible design choices are the implementer's calls.

## Outcomes

1. A first-time visitor can describe what is inspected and choose Android or terminal use.
2. Android install links distinguish GitHub 0.4.0 from Play's last observed older release. CLI and engine are explicitly source-built.
3. Confirmed artifact facts, suspected leads and inventory are distinct. Only confirmed findings affect the grade; none certifies security.
4. Android comparisons, snapshot metadata, JSON/SARIF, CLI exits and limitations are described without implying a CLI diff command, decompiler, published SDK or verified CI ingestion.
5. HTML, Markdown twins, machine references, comparison copy and prepared marketing assets tell the same story.

## Visual system

Direction: a technical field guide with annotated artifact layers. Manrope and monospace remain self-hosted/native. Existing tokens are the locked system: pale green `#f3f5ef`, surface `#fafbf7`, ink `#132d25`, muted `#53675b`, line `#ced9cc`, accent `#bce6a0`, green `#285f42`; existing major-third type and quarter-rem spacing scales, `.75rem` content radius, existing motion durations.

Homepage composition: two-column hero with one explanatory APK-to-engine-to-workflows figure; small facts strip; readable coverage list; confidence definitions; asymmetric Android recording and CLI quickstart; a shared-engine note; Android release-comparison explanation; evidence and limits; existing guides; native FAQ; contact/footer. At small widths every multi-column section explicitly stacks. Keep navigation available without JavaScript.

Use the real Android recording with native controls, pause preference and failure recovery. Label it as recorded before 0.4.0. No generated images, invented UI, customer logos, live badges or decorative terminal windows. Command blocks are selectable instructions.

## User paths and failure states

- Hero “Get FlutterGuard” reaches the workflow/install section. “Use the CLI” reaches its visible quickstart; both work without JavaScript.
- Android visitor chooses Play or GitHub with channel/version and signing caveats nearby.
- Terminal visitor reaches `/cli/`: build prerequisites, exact build and scan commands, output locations, exit codes, SARIF and limits.
- Engine visitor reaches source and API documentation, not a nonexistent package registry.
- Missing media retains text, native controls and a recording recovery link. Reduced motion pauses automatic playback; all page content remains available.
- Missing page retains status 404, a way home and machine-readable delivery.
- No forms, user uploads, browser scanning, authentication or destructive actions are introduced.

## Public contracts and constraints

- Native HTML/CSS and existing tiny JS. No new runtime or build dependency.
- Preserve existing URLs and `#why`, `#features`, `#guides`, `#faq`, `#contact` anchors.
- Add only one focused public route: `/cli/`, with HTML and Markdown.
- Preserve robots training opt-out, Cloudflare beacon, security headers, Markdown negotiation and existing release history.
- Use one H1, meaningful headings, keyboard-visible focus, native disclosures, 44px practical targets, AA text contrast, and no page-level overflow from 320px through 1920px.
- App-source files, Play tracks, production hosting, original checkout and unrelated worktrees are out of scope.
- Commit/push follow standing authorisation. Deployment and any social, directory or indexing publication remain separate.

## Proof and rollback

Baseline `784fcec`: full production-nginx contract passes 203/203. New contracts must fail against that phone-only page, then pass the new site without removing existing delivery/media checks.

Run the full browser contract, HTML/Markdown route checks, Docker content inventory, keyboard/no-JS/media failure/reduced motion/forced colors, contrast and screenshot reviews. Compare three cold-context desktop/mobile lab navigations under the same local conditions. Lab LCP/CLS are not field CWV; INP is not measured.

Fresh code review and visual review gate delivery. Revert the scoped commits to restore baseline; no data migration is involved. The live site must be rechecked after the owner deploys the pushed revision.
