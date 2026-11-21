# About FlutterGuard

Canonical: https://flutterguard.dev/about/

FlutterGuard is an open-source toolkit for reading a released Flutter application or a single APK. The Android app inspects the package on the device; the CLI runs the same JVM engine on a terminal or CI runner. Both read the manifest, the compiled Dart library, the bundled assets and the signing certificate, then report the libraries, endpoints and exposed strings they find.

## Why it exists

Mobile security tooling mostly assumes a workstation or a vendor upload. That is reasonable for a full assessment and awkward for the common question a developer asks after a build: what does this release expose? FlutterGuard keeps that first pass close to the artifact: on the phone that already has it, or on the build machine that produced it.

Flutter also breaks the assumption behind a DEX-shaped scan. The application logic is Dart compiled ahead of time into `lib/<abi>/libapp.so`, not Java in `classes.dex`. A tool that only decompiles Java can return a clean report on an app that still ships a staging endpoint.

## How it works

Both entry points read a package without executing it and group the result as confirmed artifact facts, suspected leads worth checking, and inventory across libraries and SDK markers, endpoints and routes, exposed strings, and package policy. Only confirmed findings affect the grade. Each finding is tied to the file or attribute that produced it. The app saves JSON or Markdown on the device; the CLI writes redacted JSON and SARIF 2.1.0.

## What it does not do

It does not run the app, intercept traffic, test authentication or confirm that a finding is exploitable. Static inspection shows what shipped and stops there. Confirmed findings are artifact facts, not exploitability. A lead still needs verification against a system you own or are authorised to assess. It does not decompile Dart, and it has no CLI comparison command; comparisons are an Android app feature for compatible scans of the same package. For runtime evidence, use a dynamic analyser such as MobSF; the comparison page states where each tool fits: https://flutterguard.dev/mobsf-alternative/

## Who builds it

FlutterGuard is built and maintained by Anas Fikhi (https://gwhyyy.com). The source is on GitHub under the MIT licence: https://github.com/anasfik/FlutterGuard

## Status

Install from Google Play or GitHub releases, and check the version you get: the verified GitHub release is 0.4.0, while the last observed public Play version is 0.3.2. Beta 0.4.0 availability on Play is not verified. Play and GitHub use separate signing channels, and GitHub builds before 0.3.4 used an older key; moving from one of those builds to 0.4.0 requires uninstalling, which deletes local reports, history and settings. Exporting a report does not restore that history. The CLI is built from source with JDK 17 or newer: https://flutterguard.dev/cli/ The website is static, stores no accounts and uses aggregate analytics without session recording; see https://flutterguard.dev/privacy/

## Related

- FlutterGuard CLI: scan Flutter APKs in CI — https://flutterguard.dev/cli/
- Contact and security reports: https://flutterguard.dev/contact/
- Privacy and data handling: https://flutterguard.dev/privacy/
- FlutterGuard home: https://flutterguard.dev/
