# Privacy and data handling

Canonical: https://flutterguard.dev/privacy/

The Android app cannot send what it can read, and the CLI writes only where you point it. The site collects no accounts.

## The Android app

FlutterGuard declares no INTERNET permission. It cannot upload a report, contact a server or fetch a lookup. Everything it reads stays on the device, and saved reports live in the app's private storage, removed when the app is uninstalled. There is no account, no sign-in, no advertising SDK and no crash reporter.

The app reads an APK you choose or an installed app you select. It does not run the app, record the screen or collect device identifiers. Values that look like credentials are masked in the interface by default and only revealed on request.

## The CLI

The CLI runs locally and reads the APK you pass to it. It writes reports to the paths you choose and makes no network request during a scan. Building the project may download Gradle dependencies, and a CI workflow that runs the CLI may upload the JSON or SARIF artifacts it produces; that upload is the workflow's decision and is visible in its configuration. Detected secret values stay masked in the JSON report the CLI writes.

## This website

The site is static, with no login and no contact form. Cloudflare Web Analytics reports aggregate page views and performance without cookies, fingerprinting or cross-site tracking. PostHog uses a first-party cookie to count visits, page views and Google Play clicks. PostHog also receives the page URL, including query parameters, and referrer. Session recording and autocapture are disabled; this project does not use PostHog for advertising or cross-site tracking.

A Google Play click also sends a first-party counter request. The container records only the time, event name and a known page category, with unknown paths grouped as “other”. This counter record excludes IP addresses, user agents, referrers, cookies and raw query values. It is separate from PostHog's click event.

The hosting service, Cloudflare and PostHog process connection data, including IP addresses, under their respective policies. The limited counter format does not make those other services anonymous. Cloudflare's analytics beacon reports the page path, referrer, country and basic device class in aggregate.

## Email and GitHub

If you write to work@gwhyyy.com or security@gwhyyy.com, the message is handled by the mail provider and read by the maintainer. GitHub issues, pull requests and stars are handled by GitHub under its own privacy policy. Do not include live secrets, third-party personal data or an APK you are not allowed to share.

## External links

Pages link to GitHub and to gwhyyy.com. Following a link leaves this site and the destination's policy applies. The full legal privacy notice is published at https://gwhyyy.com/privacy/flutterguard

## Changes

If data handling changes, this page is updated with the site. The app's permission list is visible in its manifest and on the GitHub release page, so the claims above can be checked against the artifact.
