# Publish drafts

Status: 2026-11-18. Ready to publish. Nothing here has been posted; every channel needs your login.
Figures come from the public corpus page (`/flutter-release-corpus/`) and `CORPUS.md` in the app
repo. Do not add claims that are not in those two sources.

Rules that apply to all three drafts: no emojis, no "revolutionary" language, disclose that you
are the maintainer, link the APK or Play listing once, and answer technical questions rather
than pitching.

## 1. Hacker News — Show HN

Submit at https://news.ycombinator.com/submit. Post once. Best window: a weekday morning US
Eastern, and stay available for comments for the first three hours.

Title (67 characters):

```
Show HN: I inspected 26 released Flutter APKs; here is what shipped
```

Text:

```
I wanted to know what a published Flutter app actually carries, so I inspected 26 production
release APKs from public release channels: read-only, no execution, on a workstation and again
on an Android phone.

A few measured results:

- 9 of 26 apps carried at least one AI provider endpoint as a literal string. One app had 22.
  Two had local runtimes (localhost:11434 and localhost:1234) that a generic domain scanner has
  no reason to flag.
- A sweep of 82 known DEX prefixes matched 22 of 26 apps. Plugin code and the Android embedding
  still land in classes.dex even when the app logic is Dart.
- Only 1 of 26 shipped assets/flutter_assets/pubspec.yaml. Dependency evidence usually comes
  from notices, package: strings and readable symbols instead.
- Re-scanning one app on a device instead of a downloaded APK found more, because an earlier
  detector only collected hosts from strings containing "://" . The comparison is in the
  write-up; the miss was in my code, not in the app.

The tool is FlutterGuard: an Android app that reads the manifest, libapp.so strings, assets,
dependency markers and signing material on the device, then writes a local report. No INTERNET
permission, no account, MIT licensed.

Site and figures: https://flutterguard.dev/flutter-release-corpus/
Source: https://github.com/anasfik/FlutterGuard

The honest limit is the interesting part: a string in an APK is evidence of what shipped, not
proof that a key is privileged or an endpoint is reachable. I would like feedback on which
Flutter-specific checks belong in a report and what the false-positive rate looks like on apps
you own.
```

## 2. Reddit — r/FlutterDev

Check the subreddit rules before posting. Flair it as a tool or discussion, not a launch.
Disclose that you built it in the first two lines.

Title:

```
I statically inspected 26 released Flutter APKs. Here is what shipped.
```

Body:

```
I built FlutterGuard, an offline APK inspector for Android, and used it to read 26 production
release APKs from public release channels. Disclosure: I am the maintainer. No app is named
as insecure, and no live secret is published.

What the artifacts showed:

- 9 of 26 apps had at least one AI provider endpoint as a literal string; one had 22. Two had
  local Ollama/LM Studio hosts, which most domain scanners ignore.
- 82 known DEX prefixes matched 22 of 26 apps. Your Dart code is in libapp.so, but plugins and
  the embedding still put code in classes.dex, so DEX-only checks are not useless, just partial.
- pubspec.yaml shipped in 1 of 26, so dependency inventories are mostly reconstructed from
  NOTICES.Z, package: strings and readable symbols.
- Scanning an installed app on a device found more hosts than scanning the downloaded APK,
  which exposed a bug in my own detector: it only read strings containing "://".

The practical takeaway for a Flutter release: obfuscation renames symbols but does not encrypt
string literals, assets or endpoints. If a value cannot be public, it should not be in the
client.

FlutterGuard reads the manifest, libapp.so, assets and signing material on the phone and keeps
the report local. No INTERNET permission, MIT. Site: https://flutterguard.dev
APK: https://github.com/anasfik/FlutterGuard/releases/latest
Play: https://play.google.com/store/apps/details?id=com.flutterguard.app

What checks would you expect that are missing? I am especially interested in Flutter-specific
false positives.
```

## 3. dev.to — technical article

Publish at https://dev.to/new. Tags: `flutter`, `android`, `security`, `mobile`. Cover image: `https://flutterguard.dev/og-flutter-apk-inspection.png` (the closest shipped
cover; there is no corpus-specific image). Link the tool once, at the end.

Title:

```
What 26 released Flutter APKs exposed
```

Body (Markdown):

```markdown
Most Flutter security writing starts from source. This one starts from what users install.

I read 26 production release APKs from public release channels: no execution, no instrumentation,
read-only inspection of the archive. Eleven apps were also audited twice, once on a workstation
and once on an Android phone, to see whether the device changes the answer. All figures below are
from that corpus.

## Why the release artifact, not the repository

A release build passes through R8, resource shrinking, Dart AOT compilation and signing.
Configuration that was fine in development can survive that pipeline, and code that looked
harmless in source can leave a readable string in the binary. The repository tells you what you
meant to ship. The APK tells you what you did.

## What the 26 APKs carried

**AI provider endpoints are common.** Nine of 26 apps contained at least one provider host as a
literal string; one carried 22. Two carried local runtimes (`localhost:11434` for Ollama and
`localhost:1234` for LM Studio), which a generic domain scanner has no reason to flag. A host
string proves the endpoint is referenced in the build, not that it is called at runtime.

**DEX still matters in a Flutter app.** A sweep of 82 known prefixes matched 22 of 26 apps.
Google Mobile Services matched 11, `flutter_inappwebview` 10, AndroidX Media3 10, AndroidX WorkManager 8,
Firebase 5. Plugin code and the Android embedding land in `classes.dex` no matter how much logic
lives in Dart.

**The pubspec is usually absent.** Only 1 of 26 apps shipped `assets/flutter_assets/pubspec.yaml`.
Dependency inventories are reconstructed from `NOTICES.Z`, `package:` strings and readable
symbols, and version evidence is often partial. Treat a guessed version as a lead.

**Obfuscation is not encryption.** `flutter build --obfuscate` renames Dart symbols. It does not
encrypt string literals, asset names or URLs. ProGuard and R8 operate on Java and Kotlin bytecode
and never touch `libapp.so`. If a value cannot be public, it should not be in the client.

## The device changed the answer

One app, Conduit, was scanned on a Redmi Note 9 Pro running API 35, then compared with the
downloaded APK pass:

| Signal | APK scan | Device scan |
|---|---|---|
| Third-party services | 15 | 28 |
| AI providers | 4 | 17 |
| Provider hosts | 4 | 23 |

The difference was not the app. An early version of my host detector only collected strings
containing `://`, so bare host names were invisible in both passes; fixing it and re-reading the
installed package closed most of the gap. The lesson: a scanner that only reads the downloaded
archive can be wrong about the installed app, and you should test the detector against both.

## What a finding means

A string in an APK is evidence of what shipped. It is not proof that a key is privileged, an
endpoint is unauthenticated or a component is exploitable. Static inspection cannot observe
runtime behaviour, intercept traffic or confirm reachability.

The useful output is a short list with locations: a staging host that should not have shipped, a
debug certificate on a public release, an exported component that combines badly with a deep
link, a key that is actually privileged on the server side. Verify those before calling them
vulnerabilities.

## Repro on your own app

1. Build the release you are about to publish.
2. Read the manifest: permissions, exported components, backup and cleartext policy.
3. Run `strings` over `lib/arm64-v8a/libapp.so` and look for hosts, headers and key-like values.
4. List `flutter_assets/` and decide whether anything there would be embarrassing in a zip.
5. Read the signing certificate and the signature schemes.
6. Repeat on a device, because the installed package is the artifact users actually run.

The full checklist is at https://flutterguard.dev/flutter-security-checklist/ and the corpus with
its method and limits is at https://flutterguard.dev/flutter-release-corpus/.

I built FlutterGuard, the Android app used for the device pass: it reads the manifest,
`libapp.so`, assets and signing material on the phone, keeps the report local, and has no
INTERNET permission. MIT licensed. https://flutterguard.dev

If you run the checklist against your own release, the useful feedback is which checks produced
false alarms.
```
