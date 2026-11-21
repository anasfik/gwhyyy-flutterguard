# Publish drafts

Updated: 2026-11-20 for the current FlutterGuard build. None of these drafts was posted in this
work. Publish only after approval and live website verification.

## Published

- dev.to, 2026-11-21: "Reading a Flutter release APK from the terminal"
  (id 5089969, https://dev.to/flutterguard/reading-a-flutter-release-apk-from-the-terminal-1li9).
  Source: `docs/marketing/devto-terminal-apk-article.md`. Numbers are from LocalSend
  1.18.2 arm64; no third-party hostnames or strings reproduced.

Disclose authorship. Check current community rules. Do not ask for votes or
describe a static match as a confirmed vulnerability. The existing recording
predates the current build.

## Hacker News

Title:

```text
Show HN: FlutterGuard, local Flutter APK inspection on Android or in CI
```

Body:

```text
I built FlutterGuard to inspect what ships inside a released Flutter APK:
libraries, endpoints, readable strings, signing evidence and package policy.

The current build adds a source-built CLI with JSON and optional SARIF output. The
Android app and CLI share a pure-JVM engine. Reports separate confirmed artifact
facts from leads and inventory; only confirmed facts affect the grade. The
Android app can compare saved scans of the same app across releases.

The code is MIT-licensed and scans run locally. A confirmed artifact fact is not
proof of exploitability, credential validity or runtime behavior.

Website: https://flutterguard.dev/
CLI setup: https://flutterguard.dev/cli/
Source and Android APK: https://github.com/anasfik/FlutterGuard

I would value examples of false leads on APKs you own and feedback on the report
format. There is no prebuilt CLI download or published engine package yet.
```

## r/FlutterDev

Title:

```text
FlutterGuard: inspect a release APK on Android or from the terminal
```

Body:

```text
Disclosure: I maintain FlutterGuard, a free MIT-licensed inspector for Flutter
APKs.

The Android app now separates confirmed artifact facts, leads worth checking and
inventory. It also compares saved scans of the same app across releases.

For build workflows, a source-built CLI uses the same JVM engine.
It writes redacted JSON and optional SARIF. An optional --fail-on confirmed gate
returns exit 1 after writing reports when a confirmed artifact fact is present.
That gate is not a vulnerability verdict.

Scanning is local. The Android app has no INTERNET permission or telemetry. CI
report uploads are controlled by your workflow, not by the scanner.

Setup, Android install channels and limits: https://flutterguard.dev/
CLI guide: https://flutterguard.dev/cli/

What would make the evidence easier to review before your next release?
```

## Short announcement

```text
FlutterGuard inspects Flutter APKs on Android or through a source-built CLI.
The shared JVM engine produces artifact evidence; reports keep confirmed facts
separate from leads and inventory.

JSON/SARIF for build workflows, saved-release comparisons on Android, local
scanning, MIT licensed.

Setup and limits: https://flutterguard.dev/
```

## Technical article outline

**Title:** Reading a Flutter release APK from the terminal

1. Start with an APK you own and identify its build and digest.
2. Explain the packaged manifest, assets, native libraries and DEX evidence.
3. Build the CLI from source using the repository setup and JDK 17+.
4. Run a scan into fresh output paths; read JSON and optional SARIF.
5. Explain the three confidence groups and exit codes 0, 1 and 2.
6. Show how a CI artifact upload changes the privacy boundary.
7. Explain unsupported AAB/split assembly, runtime validation and CLI comparison.

Use real output from a permitted fixture before adding a walkthrough or numbers.
Do not reuse historical corpus counts as a measurement of current precision.
