# FlutterGuard product marketing context

**Document version:** v1  
**Last updated:** 2026-11-20  
**Basis:** product source at `anasfik/FlutterGuard@1c28d0f`, public distribution checks, and the founder's request to cover Android, the shared engine, and CLI/CI.

## Product overview

**One-liner:** See what ships in your Flutter app.

FlutterGuard inspects Flutter Android APKs locally. The Android app offers installed-app discovery, saved reports and release comparisons. A source-built CLI uses the same pure-JVM engine and writes redacted JSON and SARIF for terminal and CI workflows.

**Category:** Flutter APK inspection and static security review.  
**Type and business model:** free, MIT-licensed open-source software; no account or paid tier.

## Audience and jobs

- Flutter developers reviewing what a release contains before handover.
- Security reviewers investigating an APK they own or are authorised to test.
- Build maintainers who need machine-readable evidence from an APK in CI.
- Contributors who want to reuse the scanner rather than write another one.

These audiences are inferred from the product and brief, not validated customer segments. No enterprise buyer, customer count, testimonial or adoption claim is established.

## Problem and differentiation

A release can retain endpoints, strings, assets and package policy that a source-only checklist misses. FlutterGuard brings evidence from the manifest, Flutter assets and compiled-library strings into one report. Android and terminal scans share the engine.

MobSF is a broader mobile analysis framework with static and dynamic workflows and automation. FlutterGuard's narrower fit is Flutter-oriented local artifact inspection. Manual extraction tools and source-review checklists remain complementary.

## Contracts and objections

| Question | Supported answer |
|---|---|
| Is a finding a vulnerability? | Confirmed means an observed artifact fact. Suspected matches are leads. Neither proves exploitability, credential validity or endpoint reachability. |
| What does the grade mean? | Only confirmed findings affect the current grade. An A is not a security certificate. |
| Can I compare releases in the terminal? | No CLI comparison command exists. Release comparisons are available in the Android app for compatible scans of the same package. |
| Can I download the CLI or add a Maven dependency? | No published CLI distribution or engine package is established. Build from the repository. |
| Does it decompile Dart? | No. Recognised snapshot headers expose metadata; names and obfuscation remain heuristics. |
| Does it replace a penetration test? | No. It does not execute the target, test a backend or observe live traffic. |
| Which input? | The CLI accepts one APK. AABs need conversion; it does not assemble split APKs. Android installed-app access depends on the device. |
| Is it offline? | Scanning is local. The Android app has no INTERNET permission. Building may download dependencies; CI uploads follow the workflow's policy. |

## Distribution and privacy

GitHub's verified 0.4.0 release contains an Android APK. The last observed public Play version is 0.3.2; beta 0.4.0 availability is not verified. Never imply feature parity across these channels.

Play and GitHub have separate signing channels. GitHub builds before 0.3.4 use an older key; uninstalling to change keys deletes local reports, history and settings. Exporting a report is not a history restore.

The app has no accounts or telemetry. This website uses the existing Cloudflare Web Analytics beacon, disclosed in `/privacy/`. Do not apply an app privacy promise to the website.

## Voice and customer language

The founder asked for friendly, welcoming copy and rejected excessive AOT/debug/runtime noise. Prefer “inspect,” “what ships,” “evidence,” “leads,” “compare releases,” and “local.” Explain technical details where they help someone act.

Avoid “100% secure,” “confirmed vulnerability,” “decompiler,” “live secrets,” “instant,” “only tool,” universal detection, invented performance lifts, or claims that CI ingestion is verified.

## Proof

- Source documents the scanner, rule catalogue, redaction and limitations.
- A public release corpus and synthetic benchmark recipe make methods inspectable. They do not establish global precision.
- Existing Android recordings predate 0.4.0. Label them; do not present them as proof of the new comparison or confidence UI.
- SARIF output exists. Successful GitHub Actions execution and Security-tab ingestion are not verified.

## Goals and measurement

Primary website job: help a visitor choose Android installation or the CLI quickstart and complete their first local scan. Downloads and outbound clicks are interest, not verified scans.

GSC final data, 2026-10-21 through 2026-11-17: homepage 4 clicks / 91 impressions; `/proguard-flutter/` 0 / 49, average position 15.1. Preserve the existing guide cluster. No verified FlutterGuard PostHog dataset or conversion baseline was available. No search-volume or conversion forecast is justified.

## Learnings

No controlled marketing experiment has been recorded. Product and copy constraints above are requirements, not measured conversion wins.

## Changelog

- v1 (2026-11-20) — Initial source-backed positioning for Android, CLI/CI and the shared engine; recorded distribution, confidence and privacy limits.
