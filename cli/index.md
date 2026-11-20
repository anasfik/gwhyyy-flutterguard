# FlutterGuard CLI: scan Flutter APKs in CI

Canonical: https://flutterguard.dev/cli/

The same detection engine as the Android app, running on a plain JVM. Point it at one APK, get redacted JSON and SARIF, and decide whether a pipeline should stop. It reads a package without executing it and needs no phone, emulator or Android device.

In short: build the launcher from source with JDK 17 or newer, run `flutterguard scan INPUT.apk --json OUTPUT.json`, and add `--sarif` or `--fail-on confirmed` when a pipeline needs them. Output parents must already exist, and output files must not already exist. Exit 0 is success, 1 is the confirmed gate, 2 is an error.

## Build it from source

There is no published CLI download and no Maven or JitPack dependency to add:

```sh
git clone https://github.com/anasfik/FlutterGuard.git
cd FlutterGuard
echo "sdk.dir=$ANDROID_HOME" > local.properties
./gradlew :cli:installDist
cli/build/install/flutterguard/bin/flutterguard --help
```

You need JDK 17 or newer, plus an Android SDK with a platform and build-tools installed and `ANDROID_HOME` pointing at it. The repository build also configures the Android app module, so without that SDK the build fails during configuration; the SDK setup is described in the project README. The launcher runs the engine, `org.json` and `kotlinx-coroutines-core` from the distribution; the scanning machine does not need the Android SDK.

`--help` prints the usage line and exits 2. That is the argument-error convention, not a failed build.

## Scan one APK

```
flutterguard scan INPUT.apk --json OUTPUT.json [--sarif OUTPUT.sarif] [--fail-on confirmed]
```

Create the output directory and use fresh filenames:

```sh
mkdir -p ci-out
stamp="$(date -u +%Y%m%dT%H%M%SZ)"

cli/build/install/flutterguard/bin/flutterguard scan app-release.apk \
  --json "ci-out/report-$stamp.json" \
  --sarif "ci-out/report-$stamp.sarif" \
  --fail-on confirmed
```

The parent directory must exist, and neither destination may already exist: the CLI refuses to overwrite a file and exits 2. The timestamp keeps each run's names new; with fixed names, delete the previous files or use a fresh directory first. Output is staged as sibling temporary files, flushed, then published with atomic moves. A destination that appears during the scan is refused, and a failed publication rolls back what was already written.

## What the reports contain

- `--json` writes the engine's redacted report, schema `flutterguard/report/2`. Values detected as secrets are masked and never written to disk by the CLI.
- `--sarif` writes one run of SARIF 2.1.0 in the GitHub code-scanning shape: one rule per distinct finding id, and results with a rule id, level, scrubbed message, partial fingerprint and one location.
- Locations point at the APK as a `file:` URI with no region or line data. The artifact is a binary, and inventing source positions would be false precision.
- Fingerprints identify a finding as `findingId|evidence.source`; they contain no secret value, snippet or hash of one.
- Confirmed critical and high findings are errors; confirmed medium and low are warnings; confirmed informational and every suspected finding are notes. Inventory is omitted by default.
- Progress and errors go to stderr. stdout stays empty, and progress lines never print recovered values, snippets, hosts or file content.

## Exit codes and the CI gate

| Exit | Meaning |
|------|---------|
| `0` | Scan completed; the gate was not requested or was not hit. |
| `1` | Scan completed and `--fail-on confirmed` found at least one confirmed finding. |
| `2` | Invalid arguments, unreadable or unsupported input, scan failure, cancellation or output failure. |

The gate is evaluated only after both outputs are published, so exit 1 cannot hide a scan or write error. A confirmed finding means the artifact proves the configuration; it is not proof of exploitability, and only confirmed findings affect the grade.

## Use it in CI

The repository includes `.github/workflows/apk-scan.yml`:

- It sets up JDK 17, runs the CLI tests, builds the distribution, builds FlutterGuard's own debug APK as an owned fixture, scans it to JSON and SARIF, and retains both as workflow artifacts for 14 days.
- A separate job uploads the SARIF to code scanning and is the only one granted `security-events: write`. Fork pull requests skip that job.
- The workflow does not use `--fail-on` on its own fixture: a debug build legitimately contains confirmed findings such as a debuggable manifest and a debug certificate, so the gate would reject the repository itself.
- Gate usage belongs to the project being scanned, where a confirmed policy failure should stop the build.
- CI artifact retention, upload permissions and code-scanning ingestion are properties of the workflow you run. Local SARIF validation is not GitHub acceptance, and alert display and fingerprint deduplication remain unverified until the workflow runs on GitHub with those permissions.

## Limits and honest edges

- One APK per invocation. The CLI does not assemble split APK sets; convert an AAB to APKs with `bundletool` first.
- No comparison command. Comparing releases is an Android app feature, for compatible scans of the same package. The CLI has no diff mode.
- No decompilation. The compiled library is AOT machine code. Snapshot metadata describes how it was built; it is not decompiled Dart and does not definitively prove obfuscation.
- The engine lives at https://github.com/anasfik/FlutterGuard/tree/main/engine and is not a separately published SDK.
- Static evidence only. The scan does not run the target, test a backend or observe traffic. Confirmed findings are artifact facts; a lead still needs verification against a system you own or are authorised to test.
- The scan stays local. Building may fetch Gradle dependencies, and a CI job may upload artifacts according to its own policy.

## Questions people ask

- Can I download the FlutterGuard CLI? No published CLI distribution is established. Build the launcher from the repository. The GitHub release provides the Android app, and there is no Maven or JitPack package for the engine.
- Does the CLI need a device or Android Studio? The launcher runs on a JVM with JDK 17 or newer and needs no Android device or emulator. The repository build also configures the Android app module, so use the Android SDK setup described in the project README.
- Is a CLI scan offline? The scan itself is local and the report is written where you point it. Building the project may download Gradle dependencies, and a CI job uploads artifacts only if its own workflow says so.
- Can the CLI compare two releases? No CLI comparison command exists. Release comparisons happen in the Android app, for compatible scans of the same package.
- Does a SARIF file prove GitHub code scanning works? No. The CLI validates the SARIF document before writing it, but GitHub security-tab ingestion, alert display and fingerprint deduplication are unverified until the workflow runs on GitHub with the required permissions.
- Does a confirmed finding prove the app is exploitable? No. Confirmed means the artifact proves the configuration. It is not an exploitability verdict, and only confirmed findings affect the grade.

## Related

- [Flutter security: what a release APK exposes](https://flutterguard.dev/flutter-security/)
- [Flutter APK inspection: reading a release on Android](https://flutterguard.dev/flutter-apk-inspection/)
- [ProGuard for Flutter: what R8 and obfuscation hide](https://flutterguard.dev/proguard-flutter/)
- [MobSF alternative for auditing Flutter APKs](https://flutterguard.dev/mobsf-alternative/)
- [Flutter app security audit checklist](https://flutterguard.dev/flutter-security-checklist/)
- [FlutterGuard home](https://flutterguard.dev/)
- Source (MIT): https://github.com/anasfik/FlutterGuard
