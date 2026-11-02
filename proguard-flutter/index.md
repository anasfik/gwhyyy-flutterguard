# ProGuard for Flutter: what R8 and obfuscation hide

Canonical: https://flutterguard.dev/proguard-flutter/

Two toolchains get mixed up in Flutter release builds. R8 and ProGuard work on Java and Kotlin. Dart has its own obfuscator. Neither one encrypts what you ship.

## Two toolchains, one APK

- Java and Kotlin: R8 reads ProGuard rules and shrinks, optimises and renames Android classes, methods and fields.
- Dart application: `flutter build --obfuscate` renames Dart symbols in the AOT snapshot.
- Assets and strings: nothing by default.

The Dart snapshot ends up in `libapp.so`. R8 does not rewrite it, and Dart obfuscation does not rename Kotlin plugin classes.

## What R8 and ProGuard do

R8 replaced ProGuard in the Android build pipeline and reads the same keep rules. Shrinking removes unused classes and members, rewrites what remains and renames surviving symbols. Resource shrinking removes unused resources. R8 runs before the DEX is written and must preserve entry points that Android, reflection or a plugin look up by name.

```gradle
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

Treat the obfuscation R8 provides as a speed bump, not a secret store.

## What Dart obfuscation does

```sh
flutter build apk --release --obfuscate --split-debug-info=build/symbols
```

The flag renames Dart symbols. Flutter's documentation is direct about the limit: it makes symbols harder to read and is not a security measure. String literals are not encrypted, asset names are not changed, and URLs, header names and key-like values remain recoverable with `strings`. Keep the symbol file with the release; without it, a release stack trace is a list of short names.

## What still shows up in the APK

- String literals: endpoints, query parameters, header names and hardcoded values.
- Compile-time configuration: `--dart-define` values are built into the binary.
- Asset files: JSON, fonts, images and bundled configuration are extractable.
- Dependency clues: `NOTICES.Z`, `package:` URIs and readable symbols.
- Android surface: manifest, exported components, permissions and network security configuration.
- Signing material: certificate and signature schemes.

If a value cannot be public, it should not be in the client.

## Check your own build

1. Build the release with and without `--obfuscate`, keep both artifacts.
2. Run `strings` over `libapp.so` from each build and compare. String literals stay; identifier names should not.
3. List `flutter_assets/` and confirm nothing private is bundled.
4. Read the manifest for debuggable flags, cleartext traffic and exported components.
5. Open the APK with an on-device inspector and record what a reviewer would see.

## Common mistakes

- Assuming ProGuard hides Dart code.
- Putting an API key in `--dart-define` and calling it hidden.
- Treating obfuscation as a substitute for server-side authorization.
- Enabling R8 without the keep rules a reflection-based plugin needs.
- Storing secrets in assets, JSON or a bundled `.env` file.
- Auditing only the repository and never the signed artifact users install.

## Related

- [Flutter security: what a release APK exposes](https://flutterguard.dev/flutter-security/)
- [Flutter APK inspection: reading a release on Android](https://flutterguard.dev/flutter-apk-inspection/)
- [MobSF alternative for auditing Flutter APKs](https://flutterguard.dev/mobsf-alternative/)
- [FlutterGuard](https://flutterguard.dev/)
