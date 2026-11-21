# See what ships in your Flutter app.

Canonical: https://flutterguard.dev/

FlutterGuard inspects Flutter Android APKs. Use the Android app when the file is on the phone, or build the CLI from source when the scan belongs in a terminal or CI. Both run the same JVM detection engine and read the manifest, the compiled Dart library, the bundled assets and the signing material. No account, no upload, MIT licensed.

## Two ways to scan

- **Android app.** Pick an installed Flutter app or open a single APK, read the evidence, and keep the report on the device. The app declares no INTERNET permission. Install from Google Play or from GitHub, and note which build each channel has.
- **CLI.** Build the launcher from source with JDK 17 or newer, then scan one APK to redacted JSON or SARIF 2.1.0. Exit codes support a CI gate. There is no published CLI download and no Maven or JitPack package.
- **Engine.** The shared engine lives in the repository at `engine/`. It is not a separately published SDK.

## Distribution and versions

GitHub releases contain the Android APK. Google Play is updated separately and its availability is not verified here. Features can differ between the channels, so check the version you installed rather than assuming parity.

Play and GitHub use different signing channels. Some older GitHub builds used an older signing key, so moving from one may require uninstalling the app. Uninstalling deletes local reports, history and settings, and exporting a report does not restore that history.

## What it reads

- Package facts: application id, version, SDK levels, permissions and exported components.
- Library and SDK markers in `lib/<abi>/libapp.so`, `classes.dex` and `NOTICES.Z`.
- Endpoints and routes recovered from string literals and assets.
- Exposed strings that look like keys, tokens or internal URLs, masked by default.
- Package policy: backup, debuggable, cleartext traffic and network security configuration.
- Signing certificate and signature schemes.
- Snapshot metadata that describes how the Dart library was built. It is not decompilation and does not definitively prove obfuscation.

## Confidence and grades

- **Confirmed artifact facts** are read directly from the package.
- **Leads worth checking** are suspected matches that need verification.
- **Inventory** lists what is present without judging it.

Only confirmed findings affect the grade. A-F are triage labels, not a security certificate. A confirmed finding still does not prove exploitability, credential validity or endpoint reachability; an A is not a guarantee of safety.

## Android release comparisons

The Android app can compare two saved scans of the same package, showing what arrived and what left across permissions, endpoints, SDK markers, libraries, certificates, policy and findings. If a category could not be read in one scan, the comparison says so instead of claiming nothing changed. A scan of a different package is refused. There is no CLI comparison command.

## Offline and network behaviour

Android scans run locally because the app has no INTERNET permission. CLI scans also read the artifact locally and write reports where you point them. Building either project may download dependencies, and a CI workflow may upload artifacts according to its own policy. Scanning is local; build and CI are separate network boundaries.

## Limits

Static inspection shows what shipped. It cannot prove an endpoint is unauthenticated, a key is privileged or a component is exploitable. It does not run the app, intercept traffic or test authentication. AABs are not supported; convert with `bundletool` first. Some Android ROMs block APK reads. The CLI takes one APK per invocation and does not assemble split APKs.

## Guides

- [Flutter security: what a release APK exposes](https://flutterguard.dev/flutter-security/)
- [Flutter APK inspection: reading a release on Android](https://flutterguard.dev/flutter-apk-inspection/)
- [ProGuard for Flutter: what R8 and obfuscation hide](https://flutterguard.dev/proguard-flutter/)
- [MobSF alternative for auditing Flutter APKs](https://flutterguard.dev/mobsf-alternative/)
- [Flutter app security audit checklist](https://flutterguard.dev/flutter-security-checklist/)
- [What 26 released Flutter apps expose](https://flutterguard.dev/flutter-release-corpus/)

## Start

- [FlutterGuard CLI: scan Flutter APKs in CI](https://flutterguard.dev/cli/)
- [Google Play listing](https://play.google.com/store/apps/details?id=com.flutterguard.app)
- [Latest GitHub release](https://github.com/anasfik/FlutterGuard/releases/latest)
- Source (MIT): https://github.com/anasfik/FlutterGuard
- Engine source: https://github.com/anasfik/FlutterGuard/tree/main/engine

## Site

- About: https://flutterguard.dev/about/
- Contact: https://flutterguard.dev/contact/
- Privacy: https://flutterguard.dev/privacy/
- Changelog: https://flutterguard.dev/changelog/
- Corpus: https://flutterguard.dev/flutter-release-corpus/
- Machine-readable summary: https://flutterguard.dev/llms.txt
- Full text for agents: https://flutterguard.dev/llms-full.txt
