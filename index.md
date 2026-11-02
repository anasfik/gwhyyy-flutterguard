# FlutterGuard: security audit any released Flutter app

Canonical: https://flutterguard.dev/

FlutterGuard is an offline Android app that audits a released Flutter app or a single APK on the phone that runs it. It reads the manifest, the compiled Dart library, the bundled assets and the signing certificate, then reports libraries, endpoints and exposed strings. No account, no upload, no INTERNET permission. MIT licensed. Android 8.0 and newer.

## Why audit the APK

Source review and release review answer different questions. A release build passes through R8, resource shrinking, Dart AOT compilation and signing. What ships is the artifact an attacker can read, and that artifact is what FlutterGuard inspects.

## What it reports

- Package facts: application id, version, SDK levels, permissions and exported components.
- Library and SDK markers found in `lib/<abi>/libapp.so`, `classes.dex` and `NOTICES.Z`.
- Endpoints and routes recovered from string literals and assets.
- Exposed strings that look like keys, tokens or internal URLs, masked by default.
- Package policy: backup, debuggable, cleartext traffic and network security configuration.
- Signing certificate and signature schemes.

## How it works

1. Discover: pick an installed Flutter app or open an APK.
2. Inspect: read the package without executing it.
3. Report: save the evidence on the device as JSON or Markdown and return to it later.

## What it is not

FlutterGuard does not run the app, intercept traffic, test authentication or confirm exploitability. It is not an alternative to a dynamic assessment. A finding is a lead, not a verdict.

## Limits

Static inspection shows what shipped. It cannot prove an endpoint is unauthenticated or a key is privileged. Verify high-impact items against systems you own or are authorised to test.

## Install

- Download the APK: https://github.com/anasfik/FlutterGuard/releases/latest
- Source (MIT): https://github.com/anasfik/FlutterGuard
- Google Play listing is in review: https://play.google.com/store/apps/details?id=com.flutterguard.app

## Guides

- [Flutter security: what a release APK exposes](https://flutterguard.dev/flutter-security/)
- [Flutter APK inspection: reading a release on Android](https://flutterguard.dev/flutter-apk-inspection/)
- [ProGuard for Flutter: what R8 and obfuscation hide](https://flutterguard.dev/proguard-flutter/)
- [MobSF alternative for auditing Flutter APKs](https://flutterguard.dev/mobsf-alternative/)

## Site

- About: https://flutterguard.dev/about/
- Contact: https://flutterguard.dev/contact/
- Privacy: https://flutterguard.dev/privacy/
- Machine-readable summary: https://flutterguard.dev/llms.txt
- Full text for agents: https://flutterguard.dev/llms-full.txt
