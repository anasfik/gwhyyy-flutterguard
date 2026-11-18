# FlutterGuard directory pack

Status: 2026-11-02. Copy-paste fields for listings, with the state of each submission.
Claims here match the site: offline, no INTERNET permission, no account, MIT, Android 8.0+.
Do not describe a finding as proof of exploitability.

## Shared fields

Name: FlutterGuard

Tagline (52 characters):
`Audit a released Flutter APK on your phone, offline.`

Short description (154 characters):
`FlutterGuard reads an installed Flutter app or a single APK on Android: permissions, SDKs, endpoints and exposed strings. Offline, no account, MIT.`

Long description:
`FlutterGuard is an Android app for inspecting a released Flutter app. It reads the installed package or a single APK on the device: the manifest and its policy, the AOT-compiled Dart library, bundled assets, dependency clues and the signing certificate. Findings stay in a local report; the app requests no INTERNET permission and has no account system.

It is built for the artifact users install rather than the repository. Flutter's release pipeline runs R8, resource shrinking, AOT compilation and signing, and the result can differ from source. FlutterGuard shows what survived that pipeline: readable endpoints, exposed strings, exported components, bundled configuration and the shape of the build.

A finding is a lead, not a verdict. Static inspection cannot prove an endpoint is unauthenticated or a component is exploitable. Use it on apps you own or have permission to test.

MIT licensed. Android 8.0 and newer. Source and APK: https://github.com/anasfik/FlutterGuard`

Categories: Developer Tools, Security, Android, Open Source.
Pricing: Free, open source.
Platform: Android.
Licence: MIT.
Website: https://flutterguard.dev/
Source: https://github.com/anasfik/FlutterGuard
Download: https://github.com/anasfik/FlutterGuard/releases/latest
Contact: work@gwhyyy.com
Privacy: https://gwhyyy.com/privacy/flutterguard
Icon: https://flutterguard.dev/icon-512.png
Gallery: https://flutterguard.dev/og-image.png (replace with device screenshots before Product Hunt)
Video: https://flutterguard.dev/assets/app/demo.mp4

## Awesome-list PRs (opened 2026-11-02; extended 2026-11-18)

| List | Section | PR | State |
|---|---|---|---|
| Schmiemandev/awesome-flutter-security | Static & Dynamic Analysis | https://github.com/Schmiemandev/awesome-flutter-security/pull/1 | open |
| ashishb/android-security-awesome | App Vulnerability Scanners | https://github.com/ashishb/android-security-awesome/pull/333 | open |
| vaib25vicky/awesome-mobile-security | Android, Static Analysis | https://github.com/vaib25vicky/awesome-mobile-security/pull/41 | open |
| saeidshirazi/awesome-android-security | Tools, Static Analysis | https://github.com/saeidshirazi/awesome-android-security/pull/52 | open |
| 8kSec/awesome-mobile-security | 1. Tools, Android Scanning & Automated Analysis | https://github.com/8kSec/awesome-mobile-security/pull/1 | open (2026-11-18) |
| NetKingJ/awesome-android-security | Tools, Static / Dynamic Analysis | https://github.com/NetKingJ/awesome-android-security/pull/3 | open (2026-11-18) |
| user1342/Awesome-Android-Reverse-Engineering | Tools, Static Analysis Tools | https://github.com/user1342/Awesome-Android-Reverse-Engineering/pull/13 | open (2026-11-18) |
| ByteHackr/AwesomeMobilePentest | Android, Reverse Engineering and Static Analysis | https://github.com/ByteHackr/AwesomeMobilePentest/pull/3 | open (2026-11-18) |
| kyawthiha7/Mobile-App-Pentest | Android, Tools | https://github.com/kyawthiha7/Mobile-App-Pentest/pull/3 | open (2026-11-18) |

The two 2026-11-18 PRs were placed after verifying the section anchor in the upstream README:
APKLeaks in the 8kSec scanning table, the MobSF bullet in the NetKingJ tool list, and the MobSF
bullet in the user1342 Static Analysis Tools list, and the Jadx bullet in the ByteHackr Android
static analysis list, and the modSF bullet in the kyawthiha7 Android tools list. Each PR shows one added line and one changed
file. The app README now links the checklist and corpus next to Guides (commit ecfcf60). Forks live under `anasfik` (the mobile-security and
android-security names collided with existing forks, so GitHub created
`awesome-mobile-security-1` and `awesome-android-security-nkj`); delete them
after a merge or rejection.

## Account-gated listings

| Directory | Where | What it needs | State |
|---|---|---|---|
| Product Hunt | https://www.producthunt.com/posts/new | Account, gallery images, first comment, launch date | blocked: needs your login |
| Hacker News | https://news.ycombinator.com/submit | Account with commenting history; Show HN copy is in launch-kit.md | blocked: needs your login |
| Reddit r/FlutterDev | https://www.reddit.com/r/FlutterDev/submit | Account, subreddit rules; copy is in launch-kit.md | blocked: needs your login |
| dev.to | https://dev.to/new | Account; the corpus summary is the planned post | blocked: needs your login |
| AlternativeTo | https://alternativeto.net/manage/add-app/ | Account; list as alternative to MobSF and jadx | blocked: needs your login |
| SaaSHub | https://www.saashub.com/submit | Account, free listing | blocked: needs your login |
| F-Droid | https://f-droid.org/en/docs/Submitting_to_F-Droid_Quick_Start_Guide/ | GitLab account, reproducible build recipe, no proprietary dependencies; the current APK path is a GitHub release | blocked: needs GitLab login |
| IzzyOnDroid | https://gitlab.com/IzzyOnDroid/repo/-/issues | GitLab account, public APK with a stable versionCode | blocked: needs GitLab login |
| Awesome Android Security (other) | see PR table above | GitHub account (available) | done |

No account-creation is attempted from this machine. The copy for each blocked channel is ready
in `launch-kit.md`; submission is a human login step.
| Hacker News | https://news.ycombinator.com/submit | Account; Show HN copy is in the launch kit | not submitted |
| Reddit r/FlutterDev | https://www.reddit.com/r/FlutterDev/ | Account; one follow-up post, APK link | not submitted |

## Rules for every listing

- Link Google Play as the primary install path, with the GitHub release as fallback.
- Keep the offline and no-INTERNET claims; they are verifiable from the manifest.
- Do not claim detection rates, coverage counts or "the only" tool.
- Do not ask for upvotes or cross-post the same text on the same day.
- Record the submitted URL and date here after each submission.
