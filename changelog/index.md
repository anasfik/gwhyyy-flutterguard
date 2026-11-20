# FlutterGuard changelog

Canonical: https://flutterguard.dev/changelog/

Release notes in the order they shipped. Atom feed: https://flutterguard.dev/feed.xml

Two install channels: Google Play carries 0.3.2; GitHub carries 0.4.0. The 0.4.0 release adds confidence classes, release diffing and the CLI, and it is not on Play yet. The 0.3.4 build changed the signing key, so a GitHub install over 0.3.3 requires an uninstall first. Play installs update normally.

## 0.4.0 — 19 November 2026

The detection release. Findings are now sorted by how much they actually prove, two releases can be compared, and the same engine runs outside Android.

- Confirmed artifact facts, leads worth checking and plain inventory are separated; the grade counts confirmed facts only.
- Release-to-release comparison of permissions, endpoints, SDKs, native libraries, signing certificates, network policy and findings.
- Dart snapshot metadata (kind, build features, serialization hash) read from the compiled library when the format is recognised.
- JVM CLI with JSON and SARIF output and a confirmed-only gate for CI.
- 388 unit tests across 53 suites; no INTERNET permission; versionCode 10.

## 0.3.4 — 2 November 2026

The brand pass. The app adopts the site's colour and type tokens, ruled rows and the current icon. Scanning behaviour is unchanged from 0.3.3. New signing key for GitHub builds; 0.3.3 to 0.3.4 needs an uninstall.

## 0.3.3 — 1 November 2026

The size and hardening release. R8 and resource shrinking were enabled for the Android shell.

- APK: 6.9 MB to 1.4 MB. AAB: 3.4 MB.
- Packed DEX: 13.5 MB plus 5.1 MB to a single 2.4 MB file.
- 282 unit tests across 38 suites.
- No INTERNET permission; versionCode 8.

## 0.3.2 — 1 November 2026

Consent and settings wave, plus the legal documents. This is the build Google Play serves.

- Settings and consent screens.
- Privacy and licence pages reachable from the app.
- versionCode 7.

## 0.3.1 — 30 October 2026

Third-party surface pass. Detectors gained the modern Flutter provider and SDK markers used in the release corpus.

## 0.3.0 — 30 October 2026

Corpus-driven detectors. Rules were derived from the public release APK study rather than from framework documentation alone.

## 0.2.0 — 29 October 2026

The research workbench: findings grouped by artifact, library, endpoint, string and policy, with JSON and Markdown reports.

## 0.1.0 and 0.1.1 — 28 October 2026

First public builds. Installed-package and single-APK inspection, on-device analysis, no network permission.

## What the numbers mean

File sizes, test counts and version codes are recorded from the release builds. They are not benchmarks against other tools.

## Related

- Flutter security: what a release APK exposes — https://flutterguard.dev/flutter-security/
- Flutter app security audit checklist — https://flutterguard.dev/flutter-security-checklist/
- What 26 released Flutter apps expose — https://flutterguard.dev/flutter-release-corpus/
- Source (MIT): https://github.com/anasfik/FlutterGuard
