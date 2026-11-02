# Flutter security: what a release APK exposes

Canonical: https://flutterguard.dev/flutter-security/

Most reviews start with the repository. An attacker starts with the APK you shipped. Auditing the release artifact answers a narrower question: what can someone with the app installed actually see?

## What a Flutter release contains

- `AndroidManifest.xml`: package identity, permissions, exported components, intent filters, backup and cleartext policy.
- `classes.dex`: the Android shell, plugins and embedding code.
- `lib/<abi>/libapp.so`: compiled Dart application, string literals and symbol metadata.
- `lib/<abi>/libflutter.so`: the Flutter engine.
- `flutter_assets/`: asset manifest, fonts, images, bundled configuration and `NOTICES.Z`.
- `META-INF/`: signing material and digests.

## The checks that find real problems

1. Manifest policy: permissions plus exported components, intent filters, `allowBackup`, `debuggable`, `usesCleartextTraffic` and network security configuration.
2. Endpoints and environment leaks: staging hosts, internal admin URLs, anonymous-write buckets.
3. Exposed strings and assets: keys, tokens, passwords, bundled JSON and `.env` files. Mask values during triage.
4. Dependency inventory: `NOTICES.Z`, `package:` URIs and readable symbols. Version evidence is often partial.
5. Signing and build hygiene: certificate, signature schemes, debug certificates on public releases.

## Flutter-specific traps

- Obfuscation is not encryption. `flutter build --obfuscate` renames Dart symbols; it does not encrypt strings, assets or endpoints.
- Compile-time constants ship. `--dart-define` values are baked into the binary.
- Routes are candidates, not a runtime map.
- Assets are files and extractable.
- Flutter does not remove Android risk: exported components, WebView bridges and deep links still follow Android rules.

A finding is a lead, not a verdict. Verify against the running system with permission before reporting impact.

## What static inspection cannot tell you

It cannot observe runtime behaviour, intercept traffic, test authentication or confirm reachability. Server-side authorization, rate limits and data exposure are outside the APK.

## Repeatable workflow

1. Obtain an APK you are authorised to test.
2. Read the manifest, then the compiled library, then assets.
3. Record each finding with its source location and a masked value.
4. Verify high-impact items against your own backend or a test environment.
5. Keep the report with the release version and certificate as a baseline.

## Related

- [Flutter APK inspection: reading a release on Android](https://flutterguard.dev/flutter-apk-inspection/)
- [ProGuard for Flutter: what R8 and obfuscation hide](https://flutterguard.dev/proguard-flutter/)
- [MobSF alternative for auditing Flutter APKs](https://flutterguard.dev/mobsf-alternative/)
- [FlutterGuard](https://flutterguard.dev/)
