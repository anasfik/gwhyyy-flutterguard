# FlutterGuard directory pack

Copy updated: 2026-11-20. Submission history below retains its original dates;
PR states have not been re-verified in this task. No new submission is authorized
by this document. Confirmed artifact facts do not prove exploitability.

## Shared fields

Name: FlutterGuard

Tagline:
`Inspect Flutter APKs on Android or in your build workflow.`

Short description:
`FlutterGuard inspects Flutter APKs locally on Android or through a source-built CLI. Review artifact facts, leads and inventory. Free and MIT-licensed.`

Long description:
`FlutterGuard inspects what ships inside a Flutter APK: package policy, native libraries, dependencies, endpoints, readable strings and signing evidence. Use the Android app or build the CLI from source for JSON and optional SARIF output. Both use the shared JVM engine.

Reports separate confirmed artifact facts, leads worth checking and inventory. Only confirmed facts affect the grade. The Android app can compare saved scans of the same app across releases. There is no CLI compare command.

Scanning is local. The Android app has no INTERNET permission, account system or telemetry. CI uploads are controlled by the user's workflow. Static evidence does not prove exploitability, runtime behavior or credential validity. Use APKs you own or have permission to assess.

MIT licensed. Android 8.0+ for the app; JDK 17+ for CLI runtime. CLI and engine require a source build and are not published binary packages. Source and Android APK: https://github.com/anasfik/FlutterGuard`

Categories: Developer Tools, Security, Android, Open Source.
Pricing: Free, open source.
Platform: Android; source-built JVM CLI and engine.
Licence: MIT.
Website: https://flutterguard.dev/
Source: https://github.com/anasfik/FlutterGuard
Download: https://github.com/anasfik/FlutterGuard/releases/latest
Contact: work@gwhyyy.com
Privacy: https://flutterguard.dev/privacy/
CLI setup: https://flutterguard.dev/cli/
Icon: https://flutterguard.dev/icon-512.png
Gallery: https://flutterguard.dev/og-image.png (replace with device screenshots before Product Hunt)
Video: https://flutterguard.dev/assets/app/demo.mp4 (recorded before 0.4.0)

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
| VoltAgent/awesome-agent-skills | Community Skills, Development and Testing | https://github.com/VoltAgent/awesome-agent-skills/pull/1444 | open (2026-11-18) |
| Solido/awesome-flutter | Open Source Apps, Top | https://github.com/Solido/awesome-flutter/pull/1094 | open (2026-11-18) |
| enaqx/awesome-pentest | Static Analyzers | https://github.com/enaqx/awesome-pentest/pull/786 | open (2026-11-18) |
| sbilly/awesome-security | Endpoint, Mobile / Android / iOS | https://github.com/sbilly/awesome-security/pull/831 | open (2026-11-18) |

The two 2026-11-18 PRs were placed after verifying the section anchor in the upstream README:
APKLeaks in the 8kSec scanning table, the MobSF bullet in the NetKingJ tool list, and the MobSF
bullet in the user1342 Static Analysis Tools list, and the Jadx bullet in the ByteHackr Android
static analysis list, and the modSF bullet in the kyawthiha7 Android tools list. Each PR shows one added line and one changed
file. The 2026-11-18 agent-skills PR links `anasfik/FlutterGuard/tree/main/skill` and was placed
after the `checking-a-page` bullet at the end of Community Skills → Development and Testing, in
the entry format the list's CONTRIBUTING.md requires; that list asks for proven community usage, so
a decline is possible. The app README now links the checklist and corpus next to Guides (commit ecfcf60). Forks live under `anasfik` (the mobile-security and
android-security names collided with existing forks, so GitHub created
`awesome-mobile-security-1` and `awesome-android-security-nkj`); delete them
after a merge or rejection.

The sbilly/awesome-security PR sits in Endpoint → Mobile / Android / iOS, directly after the
`reFlutter` bullet, which is the section's existing evidence that Flutter-specific mobile tooling
belongs there. `contributing.md` asks for one suggestion per PR, a capitalized title, placement at
the bottom of the category, no trailing whitespace and a useful PR title; the diff is one added
line and one changed file. Last upstream push was 2026-01-11, so review may be slow.

The Solido/awesome-flutter PR targets Flutter developers rather than mobile-security readers. That
list rejects README edits: `contributing.md` says to change `source.md`, which the generated README
comes from, so the PR modifies `source.md` and inserts one line at the bottom of Open Source Apps →
Top after the FluxDown entry. Its stated minimum is 35 stars; the repository has exactly 35. The
entry drops the word Flutter from the description as the guidelines require. A maintainer may still
decide the app is too narrow for an apps showcase.

The enaqx/awesome-pentest PR targets penetration testers and security teams. Its CONTRIBUTING.md
asks for one addition per PR, title-cased names, and placement at the bottom of the relevant
category, so the entry sits last in Static Analyzers after Agentic Radar, the section's only other
artifact-level tool. Verified in the PR diff: one added line, one file, zero deletions. The list is
large and mature, so a decline on scope is possible.

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

- Link the site workflow chooser, the GitHub Android release and the CLI guide
  according to the listing audience. Public Play was last observed at 0.3.2;
  do not claim it distributes 0.4.0 until verified.
- Keep the offline and no-INTERNET claims; they are verifiable from the manifest.
- Do not claim detection rates, coverage counts or "the only" tool.
- Do not ask for upvotes or cross-post the same text on the same day.
- Record the submitted URL and date here after each submission.
