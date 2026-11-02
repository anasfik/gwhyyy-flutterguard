# Flutter APK inspection: reading a release on Android

Canonical: https://flutterguard.dev/flutter-apk-inspection/

A Flutter package can be read on the phone that runs it. No root, no workstation, no upload. The useful checks fit in one careful pass over the manifest, the compiled library and the assets.

Inspect only an app you own or have written permission to test. The techniques are read-only, but authorisation is the boundary between an audit and an intrusion.

## Get the APK

- Your own build: `flutter build apk --release`, then inspect the artifact you are about to publish.
- A downloaded artifact: use the publisher's official release channel and verify the signature.
- An installed app on a device you control: a package reader on the device is the practical route, because pulling another app's base APK over `adb` often needs root.

An AAB is a publishing format, not an installable package. Convert it with `bundletool` or audit the APK generated from it.

## Read it in five passes

1. Manifest and policy: package identity, permissions, exported components, intent filters, backup, debuggable, cleartext traffic, network security configuration.
2. Compiled Dart: `lib/<abi>/libapp.so` holds the AOT snapshot. It keeps string literals and symbol metadata; symbol readability shows whether `--obfuscate` was used.
3. Assets: `flutter_assets/` is a file tree. Bundled configuration is public configuration.
4. Dependencies: `NOTICES.Z`, `package:` URIs and readable symbols. Record confidence with each entry.
5. Signing: certificate and signature schemes. A debug certificate on a distributed release is a process failure.

## With FlutterGuard

1. Install the APK from https://github.com/anasfik/FlutterGuard/releases/latest
2. Choose an installed Flutter app or open a single APK.
3. Run the scan and review policy, strings, assets, structure and signing.
4. Reveal a masked value only when you need to judge it.
5. Save the report as JSON or Markdown. Reports stay in the app's private storage.

The app has no INTERNET permission, so nothing leaves the device. There are no cloud lookups, reputation services or automatic CVE matching.

## On a desktop

```sh
unzip -l app-release.apk
apktool d app-release.apk -o decoded
strings lib/arm64-v8a/libapp.so | grep -Ei 'https?://|api[_-]?key|token|secret' | head -50
```

The manifest is binary XML. `apktool`, `aapt2 dump` or `apkanalyzer` decode it. MobSF wraps these steps and adds scoring, but generic rules produce false positives on Flutter apps because it cannot see Dart source.

## Triage without false alarms

- Public client keys: Firebase and Supabase anon keys are designed to ship. Check the server rules instead.
- Placeholders and test values are not live secrets.
- A package name does not prove a vulnerable version.
- A production API host is expected; a staging host or public bucket is worth verifying.
- An exported component is a surface, not an exploit.

Static evidence has a ceiling. Report what you saw, where it lives, and what would verify it.

## Related

- [Flutter security: what a release APK exposes](https://flutterguard.dev/flutter-security/)
- [ProGuard for Flutter: what R8 and obfuscation hide](https://flutterguard.dev/proguard-flutter/)
- [MobSF alternative for auditing Flutter APKs](https://flutterguard.dev/mobsf-alternative/)
- [FlutterGuard](https://flutterguard.dev/)
