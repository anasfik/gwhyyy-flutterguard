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

## Where Flutter vulnerabilities come from

Flutter changes the packaging, not the classes of mistake that reach the store:

- Secrets in the artifact: keys, tokens and private endpoints in Dart strings, `--dart-define` values or bundled JSON. Evidence: `libapp.so` and `flutter_assets`.
- Environment leaks: staging hosts, admin paths or storage buckets shipped next to production configuration.
- Exported Android components: activities, services, receivers, providers and the deep links that route into them. Evidence: `AndroidManifest.xml`.
- Transport policy: permissive `usesCleartextTraffic`, missing network security configuration, or a client that trusts every certificate.
- WebView bridges: plugin JavaScript interfaces that accept content from unpinned origins.
- Stale dependencies: SDKs with known issues from notices and symbols; version evidence is usually partial.

Every item is a lead until verified against the running system.

## Questions people ask

- What does Flutter security mean for a shipped app? The surface the package exposes to someone who has it installed: permissions and exported components, endpoints and environment names, string literals that look like credentials, bundled assets, third-party SDKs, and the signing certificate. Source can disagree with what shipped.
- Can a Flutter app be decompiled? Dart is compiled ahead of time into machine code in `libapp.so`, so there is no bytecode to recover as source. String literals, symbol names and metadata survive, which is enough to recover endpoints, configuration and dependency clues.
- Does obfuscation protect API keys in a Flutter app? No. `--obfuscate` renames Dart symbols; it does not encrypt strings, assets or configuration, and a `--dart-define` value is baked into the build.
- Is it legal to inspect an APK? Only for apps you own or have written permission to assess, within the scope that permission names. Reading a package is not the same as testing the service behind it.
- What are common Flutter app vulnerabilities? Secrets baked into strings or assets, staging endpoints left in production, exported Android components and deep links, cleartext traffic or a permissive network policy, WebView bridges, and outdated SDKs.

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
