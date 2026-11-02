# About FlutterGuard

Canonical: https://flutterguard.dev/about/

FlutterGuard is an open-source Android app that inspects a released Flutter application or a single APK on the device. It reads the manifest, the compiled Dart library, the bundled assets and the signing certificate, then reports the libraries, endpoints and exposed strings it finds. The report stays on the phone.

## Why it exists

Mobile security tooling mostly assumes a workstation. That is reasonable for a full assessment and awkward for the common question a developer asks after a build: what does this release expose? By the time an APK is on a phone or in a review queue, standing up a container, a database and a browser is more work than the first pass deserves.

Flutter also breaks the assumption behind a DEX-shaped scan. The application logic is Dart compiled ahead of time into `lib/<abi>/libapp.so`, not Java in `classes.dex`. A tool that only decompiles Java can return a clean report on an app that still ships a staging endpoint.

## How it works

The app asks for no network permission, so nothing leaves the device. It reads a package without executing it and groups the result as artifact facts, library and SDK markers, endpoints and routes, exposed strings, and package policy. Each finding is tied to the file or attribute that produced it. Reports can be saved as JSON or Markdown and revisited later.

## What it does not do

It does not run the app, intercept traffic, test authentication or confirm that a finding is exploitable. Static inspection shows what shipped and stops there. A finding is a lead that needs verification against a system you own or are authorised to assess. For runtime evidence, use a dynamic analyser such as MobSF; the comparison page states where each tool fits: https://flutterguard.dev/mobsf-alternative/

## Who builds it

FlutterGuard is built and maintained by Anas Fikhi (https://gwhyyy.com). The source is on GitHub under the MIT licence: https://github.com/anasfik/FlutterGuard

## Status

The APK is available from GitHub releases. The Google Play listing is in review. The website is static, stores no accounts and uses cookieless analytics; see https://flutterguard.dev/privacy/

## Related

- Contact and security reports: https://flutterguard.dev/contact/
- Privacy and data handling: https://flutterguard.dev/privacy/
- FlutterGuard home: https://flutterguard.dev/
