# Flutter app security audit checklist

Canonical: https://flutterguard.dev/flutter-security-checklist/

A working checklist for the release you are about to hand over. It runs against the APK, not the repository, because the artifact is what users install. Inspect only apps you own or are authorised to assess. Static inspection shows what shipped; it does not prove that a string is used, that an endpoint is reachable, or that a component is exploitable.

## 1. Artifact and identity

- Confirm the artifact is the release: version name and code, build type, signing certificate.
- Record the certificate digest; it is the baseline for the next release.
- Note the Flutter engine and ABI set.
- Keep one SHA-256 per release.

## 2. Manifest and Android policy

- List permissions and justify each one.
- Review exported components and their intent filters.
- Check `android:allowBackup`, `android:debuggable` and cleartext traffic settings.
- Read the deep-link surface and whether the target validates input.

## 3. Exposed data

- Search `lib/<abi>/libapp.so` for keys, tokens, passwords and private URLs.
- Search assets: bundled JSON, `.env` files and configuration are extractable.
- Treat `--dart-define` values as public.
- Mask values before sharing; verify before escalating.

## 4. Dependencies and native SDKs

- Build the component list from `NOTICES.Z`, `package:` strings and readable symbols.
- Mark confidence per entry; a package name is not a version.
- Prioritise authentication, payments, analytics, WebView bridges, ad SDKs and AI providers.
- Look for an unexpected environment or sandbox endpoint.

## 5. Endpoints and network surface

- Collect hosts and base URLs from the library, assets and manifest.
- Flag staging hosts, admin paths, internal hostnames and open buckets.
- Check pinning configuration and cleartext exceptions where visible.
- Test only systems you own or are authorised to assess.

## 6. Signing and distribution

- Verify the signature scheme.
- Compare certificate, package name and version code with the previous release.
- Note whether distribution uses Play App Signing, a GitHub release or an internal track.
- Compare the SHA-256 of the published artifact with the file you inspected.

## 7. Report and handover

- One line per item: what was checked, what was found, where it lives.
- Separate evidence from impact.
- List the runtime, authentication and server checks static review cannot answer.
- Keep the report as the baseline for the next audit.

## Limits

Static inspection cannot observe runtime behaviour, intercept traffic, test authentication or confirm exploitability. A report is strongest when every item names its source and says what would confirm it.

FlutterGuard performs groups 1 to 6 on an Android phone, or from the source-built CLI in a terminal. The app keeps the report local. The CLI writes redacted JSON or SARIF, takes one APK per invocation, and has no comparison command; release comparisons are an Android app feature for the same package.

## Related

- Flutter security: what a release APK exposes — https://flutterguard.dev/flutter-security/
- Flutter APK inspection: reading a release on Android — https://flutterguard.dev/flutter-apk-inspection/
- FlutterGuard CLI: scan Flutter APKs in CI — https://flutterguard.dev/cli/
- What 26 released Flutter apps expose — https://flutterguard.dev/flutter-release-corpus/
- Install: https://play.google.com/store/apps/details?id=com.flutterguard.app
- Source (MIT): https://github.com/anasfik/FlutterGuard
