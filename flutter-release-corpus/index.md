# What 26 released Flutter apps expose

Canonical: https://flutterguard.dev/flutter-release-corpus/

Public release APKs, read twice: once on a workstation and once on a phone. Every figure comes from a public release artifact, inspected without executing it. The numbers describe a sample, not the Flutter ecosystem.

A provider host or SDK marker in an APK proves the string is present in the artifact. It does not prove the code path runs, that a key is valid, or that the app is insecure. Counts were measured 2026-10-30; detector rules changed afterwards.

## Method

- 11 Flutter apps plus one non-Flutter control, audited with host tools and with FlutterGuard on a device.
- 22 production APKs downloaded from the projects' own GitHub release pages.
- Gap study over 26 release APKs combining both collections.
- 33 Flutter apps of 306 installed apps classified from package contents, no misses recorded.
- Host tooling: `aapt2`, `unzip`, `strings`, plus the app's own parsers.

## AI provider endpoints

109 literal provider hosts in the detector. 9 of 26 apps matched at least one.

| App | Matching hooks | Examples |
|---|---|---|
| Conduit | 22 | OpenAI, Anthropic, Gemini, Groq, Mistral, OpenRouter |
| Anx Reader | 5 | Hosted inference providers |
| OpenNutriTracker | 3 | Hosted inference providers |
| AppFlowy | 2 | localhost:11434, localhost:1234 |

An early host detector only collected strings containing `://`. Fixing it changed one device result from 4 provider hosts to 23.

## Native SDK markers in the DEX

82 prefixes swept; 22 of 26 apps matched.

| Marker | Apps |
|---|---|
| Google Mobile Services | 11 |
| flutter_inappwebview | 10 |
| AndroidX Media3 | 10 |
| AndroidX WorkManager | 8 |
| Firebase | 5 |
| Flutter Firebase plugins | 4 |
| Google Play Billing | 4 |
| Biometric libraries | 3 |
| ML Kit | 2 |
| Sentry, gRPC, RevenueCat, PostHog, Play Integrity, ExoPlayer2 | 1 each |

## What is usually absent

A bundled `assets/flutter_assets/pubspec.yaml` appeared in 1 of 26 apps: Anx Reader 1.14.0+6321, with 92 declared dependencies. Root `.properties` SDK markers are more common.

## Workstation pass versus device pass

One app, Conduit, scanned on a Redmi Note 9 Pro running API 35:

| Signal | Host scan | Device scan |
|---|---|---|
| Third-party services | 15 | 28 |
| AI providers | 4 | 17 |
| Provider hosts | 4 | 23 |

The 17 providers were OpenAI, Anthropic, Gemini, OpenRouter, DeepSeek, Groq, Mistral, Cohere, Together, Fireworks, Perplexity, xAI, HuggingFace, Alibaba Qwen/DashScope, Moonshot, Zhipu GLM, and the Ollama/LM Studio local runtime pair.

## Limits

26 APKs is a sample, not a prevalence rate. Counts depend on the detector version; provider rules grew from 35 to roughly 135 services. A string match is evidence of presence, not of behaviour or exploitability. Only public release artifacts were used; no credentials are published.

## Related

- Full method and per-app notes: https://github.com/anasfik/FlutterGuard/blob/main/CORPUS.md
- Flutter app security audit checklist — https://flutterguard.dev/flutter-security-checklist/
- Flutter security: what a release APK exposes — https://flutterguard.dev/flutter-security/
- Flutter APK inspection: reading a release on Android — https://flutterguard.dev/flutter-apk-inspection/
- Install: https://play.google.com/store/apps/details?id=com.flutterguard.app
