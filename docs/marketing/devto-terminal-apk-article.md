# Reading a Flutter release APK from the terminal

A Flutter release looks like a normal Android package until you open it and find
that most of the application is not in `classes.dex`. The Dart code is compiled
ahead of time into a native library, and the strings your app ships live there.

This is a read-only walkthrough on a real, public release APK: LocalSend 1.18.2
for `arm64-v8a`, an open-source Flutter app. Every number below came from that
file. Nothing was executed, nothing was uploaded, and no values that could be
mistaken for credentials are reproduced here.

Use it on an app you own or have written permission to test. Read-only is not the
same as authorised.

## 1. Get the artifact and fix its identity

```bash
gh release download v1.18.2 -R localsend/localsend -p '*arm64v8.apk'
sha256sum LocalSend-1.18.2-android-arm64v8.apk | cut -c1-16
```

```text
82ec3568fba2aa52
```

Record the digest and the version together. A finding without the artifact digest
is a rumour; the same package can be rebuilt with different content.

Then look at the shape of the archive before reading any of it:

```bash
unzip -l app.apk | awk '
  /lib\/[a-z0-9_-]+\/libapp\.so/ { app++; bytes=$1 }
  /flutter_assets\//              { assets++ }
  /classes[0-9]*\.dex$/           { dex++; dbytes+=$1 }
  END { printf "libapp.so entries: %d (largest %s bytes)\nflutter_assets entries: %d\nDEX files: %d (%d bytes)\n",
        app+0, bytes, assets+0, dex+0, dbytes }'
```

On this APK:

```text
libapp.so entries: 1 (largest 14549936 bytes)
flutter_assets entries: 29
DEX files: 1 (3179884 bytes)
```

That ratio is the whole story of Flutter packaging: a 14.5 MB compiled Dart
library next to a 3.2 MB DEX that holds the Android shell, the embedding and the
plugins. If you audit only `classes.dex`, you have read a small fraction of the
application.

## 2. Know what `libapp.so` is before you grep it

`libapp.so` is the AOT snapshot of your Dart code. It is machine code. It is not
recoverable Dart source, and tools that promise to give you the original classes
are usually pattern-matching symbol names, not decompiling them.

What it does keep is real: string literals, symbol metadata, type names, and the
URLs your code was compiled with. That is usually enough to answer the question a
release review actually asks — what does this build contact, and what does it
carry?

## 3. Read the assets, not just the code

```bash
unzip -l app.apk | awk '/flutter_assets\//{print $4}' | sed 's|flutter_assets/||' \
  | cut -d/ -f1 | sort | uniq -c | sort -rn
```

This build keeps all 29 entries under a single `assets/` subtree. Bundled
configuration is public configuration: anything you put in `flutter_assets` ships
to every user and is readable with `unzip`. If a value would be embarrassing in a
zip listing, it should not be in the package.

## 4. Extract hosts with a count first, values second

```bash
unzip -p app.apk 'lib/arm64-v8a/libapp.so' > libapp.so
strings libapp.so | grep -oE 'https?://[a-zA-Z0-9.-]+' | sort -u | wc -l
```

```text
10
```

Ten distinct hosts in this build. The first useful discipline is to count before
you read: a release with forty hosts deserves a slower review than one with
three, and the count is stable enough to compare across versions.

Then read them — privately. A hostname in a binary is evidence that a string was
compiled in. It is not evidence that the endpoint is live, reachable, or that any
credential is valid. Those are three different claims, and only the first one is
something `strings` can support.

## 5. Dependencies and obfuscation are heuristics

Dart package references survive compilation:

```bash
strings libapp.so | grep -oE '^package:[a-z0-9_]+' | sort -u
```

```text
package:archive
package:async
package:characters
package:collection
package:connectivity_plus
package:connectivity_plus_platform_interface
```

This tells you which packages are in the build. It rarely tells you the version,
so record a confidence with each entry rather than a fact.

Obfuscation is similar. Counting long identifiers is a signal, not a verdict:

```bash
strings libapp.so | grep -cE '^_?[A-Za-z][A-Za-z0-9_]{20,}$'
```

```text
2167
```

A build compiled with `--obfuscate` keeps more of this than people expect, because
string literals are not renamed. Symbol readability tells you something about the
build flags. It does not tell you whether the app is safe.

## 6. The manifest needs a decoder, so use one

`AndroidManifest.xml` inside an APK is binary XML. `strings` will hand you
fragments and call it a day. Use `aapt2 dump` or `apkanalyzer manifest print`,
and check policy in this order: package identity, `uses-permission`, exported
components and their intent filters, `allowBackup`, `debuggable`, cleartext
traffic and any network security config.

Those are decisions someone made, which makes them easier to grade than a random
string. A debug certificate on a distributed release, or a backup flag on an app
that stores reports, is a process failure you can state plainly.

I did not decode the binary manifest for this walkthrough; the numbers above all
come from archive structure and `libapp.so`, which need no Android SDK.

## 7. Repeat it per release, or it is a one-off

The value comes from the diff, not the snapshot. Save each report next to the
commit and the digest, then compare: a new host, a new package, a permission that
appeared, a signing certificate that changed. A release that grew three endpoints
is worth a conversation. A single scan is worth one paragraph.

## Doing it on a phone, or in CI

The same five passes work without a terminal. [FlutterGuard](https://flutterguard.dev/)
does the reading on the device, keeps the report local, and has no INTERNET
permission — so no cloud lookup, no reputation service, and no automatic CVE
matching. A source-built CLI runs the same JVM engine in a pipeline with JSON and
optional SARIF output when you need a record.

Neither one turns a static match into a vulnerability. They shorten the distance
between a released artifact and a decision you can defend.

The full workflow, including the desktop commands and the triage order, is at
[flutterguard.dev/flutter-apk-inspection](https://flutterguard.dev/flutter-apk-inspection/).

---

Scan only artifacts you are authorised to inspect. A string in a binary is a
lead; a validated behaviour is a finding.
