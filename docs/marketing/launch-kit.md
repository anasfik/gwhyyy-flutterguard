# FlutterGuard 0.4.0 launch kit

Updated: 2026-11-20. Prepared copy, not permission to publish.
Product truth: `.agents/product-marketing.md`. Search evidence and delivery gaps:
[`2026-11-20-site-audit.md`](2026-11-20-site-audit.md).

## Positioning

FlutterGuard inspects what ships in a Flutter APK. Use the Android app for local
review, build the CLI for terminal or CI scans, or work with the shared JVM engine
in the source repository. Reports separate confirmed artifact facts, leads worth
checking and inventory.

The product is free and MIT-licensed. Scanning runs locally. The Android app has
no INTERNET permission, account system or telemetry. Website analytics and any CI
artifact uploads are separate from that app privacy claim.

## Who it serves

- Flutter developers checking a release before publishing.
- Security reviewers inspecting an APK they own or have permission to assess.
- Teams that want redacted JSON or SARIF from an existing build workflow.
- JVM developers willing to build and integrate the engine from source.

Do not describe the engine as a published SDK or the CLI as an available binary.
The current GitHub release contains the Android APK.

## What changed

- Confirmed artifact facts are separate from suspected matches and inventory.
  Only confirmed facts contribute to the grade.
- The Android app compares saved scans of the same app across releases.
- The source-built CLI writes JSON and optional SARIF, with an optional
  confirmed-finding exit-code gate.
- Android and CLI scans use the shared pure-JVM engine.
- Recognized Dart snapshot metadata adds artifact evidence. It does not
  decompile Dart or establish obfuscation, ownership or exploitability.

## Proof and distribution

| Claim | Evidence and boundary |
|---|---|
| GitHub 0.4.0 | `https://github.com/anasfik/FlutterGuard/releases/tag/v0.4.0`; Android APK |
| Public Play channel | Last observed 0.3.2 on 2026-11-20; do not announce 0.4.0 as public on Play |
| Local Android scanning | App manifest has no INTERNET permission |
| CLI contract | Repository `docs/cli.md`; JDK 17+, build from source |
| Detection method | Repository `docs/METHODOLOGY.md`, corpus and synthetic benchmark |
| Release comparison | Android feature; there is no CLI compare command |

The benchmark is a scoped synthetic regression check, not a global precision
score. The existing Android recording predates 0.4.0; it is not visual proof of
the new confidence grouping or comparison UI.

## Channels and sequence

1. **Owned:** deploy the revised site, then verify homepage, `/cli/`, changelog,
   Markdown negotiation and machine-readable references. Link the versioned
   release and source documentation.
2. **Rented:** choose one relevant community thread or technical article. Check
   current community rules, disclose authorship, and stay available for questions.
3. **Borrowed:** prepare a focused Flutter newsletter pitch about inspecting the
   shipped artifact. Avoid unsupported competitor or exclusivity claims.

Publication, directory submissions, outreach and indexing requests need approval.
Existing PR history is in `directory-pack.md`; those statuses are historical
unless checked again.

## Announcement

**Headline:** FlutterGuard 0.4.0 brings APK inspection to the terminal

> I built FlutterGuard to see what survives inside a released Flutter APK:
> bundled libraries, endpoints, readable strings and package policy.
>
> Version 0.4.0 adds a source-built CLI with JSON and SARIF output. It uses the
> same JVM scan engine as the Android app. Reports now separate confirmed
> artifact facts from leads and inventory; only confirmed facts affect the grade.
> The Android app also compares saved scans of the same app across releases.
>
> Scanning stays local. The code is MIT-licensed. A confirmed fact says what is
> present in the artifact, not whether it is exploitable or whether a credential
> works.
>
> Android APK: https://github.com/anasfik/FlutterGuard/releases/tag/v0.4.0
> CLI setup and limits: https://flutterguard.dev/cli/
> Site: https://flutterguard.dev/

## Success measures

Use GSC impressions, clicks and positions over comparable, closed 28-day windows.
The current page rows show 4 clicks and 180 impressions for 2026-10-21 through
2026-11-17. Query rows are privacy-filtered and are not a complete total.

Website visits are not installs. Install-link clicks are not measured by the
existing page-view beacon, and CLI adoption is not measured. Do not claim a
conversion improvement without that evidence. Keep app telemetry out of scope.
