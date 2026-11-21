# Asset provenance

Last updated: 2026-11-20. The app icon, canonical captures and recorded demo
are genuine app assets. The recording predates the current build and is labelled that way
on the homepage; it does not demonstrate the new confidence or comparison UI.

## Screenshots

Canonical source: `/home/gwhyyy/Downloads/projects/real_projects/fg-remote/docs/play/raw/`

| Output | Source | Source size / SHA-256 | Output size / SHA-256 | Bytes |
|---|---|---|---|---|
| `assets/app/inventory.webp` | `raw-home.png` | 1080x2400 / `261be57e2b0f38bc999f1fffc68a705986f99fa2baefab029844dac93e234a93` | 720x1600 / `3c2c55f7db762388e1f76a2f0adf2c6b4bba46282fbfb80b8963124984b43bff` | 40,720 |
| `assets/app/report.webp` | `raw-overview.png` | 1080x2400 / `062932706e630a11f97c2a3a951e727b252418323d3434195d74771a744cac20` | 720x1600 / `453a8afbfdf891bf40326792b05cb67b05de79eb097d8c86c9fb34291c9c6ca2` | 40,574 |

Conversion (ImageMagick 7, no crop, no recolour, metadata stripped, 1080:2400
aspect preserved):

```
convert raw-home.png -resize 720x1600 -strip -quality 80 assets/app/inventory.webp
convert raw-overview.png -resize 720x1600 -strip -quality 80 assets/app/report.webp
```

The images keep the real Android status bar, app UI, package names and
navigation bar. `inventory.webp` shows the installed-app list; `report.webp`
shows the Conduit report overview. These remain reference captures. The
homepage uses the recording and its Findings poster described below;
`report.webp` is not copied into the nginx image.

## Demo recording

The user supplied the latest recording from their connected phone:
`/sdcard/Movies/screen-20261102-002011.mp4`, pulled on 2026-11-02. The source
is an 80.97-second, 1080x2400 HEVC recording, 108,560,057 bytes, with no audio.
It shows FlutterGuard's inventory, findings, dependencies and scan queue.

- `assets/app/demo.mp4`: H.264, yuv420p, 540x1200, 30 fps, 81 seconds,
  3,006,187 bytes, no audio, faststart. SHA-256:
  `4ca753f5c19b6852d8a9f1e65c4b1d78954314b90a0a70273152ef87c374b4c6`.
  This is the existing optimized delivery file, reused without modification
  for the current site rework. The exact optimization command is not recorded.
- `assets/app/demo-poster.webp`: Findings frame at 20 seconds, 360x800,
  30,270 bytes. SHA-256:
  `9b3c0542af6c41d53d900836cf56792d95b5606c816003a2016899b99790859e`.

The video has native controls and an explicit recording link on playback
failure. Reduced motion disables automatic playback; the page's pause
control pauses the video and decorative CSS animations.

## OG image

`og-image.png` (1200x630, SHA-256
`be6c43f39b817e88c190c0f552804c156fb82530f515af1116e35e056c9e69ab`) was
rendered on 2026-11-20 with headless Chromium from the homepage's real brand
icon, self-hosted Manrope face, color tokens and explanatory APK diagram.
It carries the headline, "See what ships in your Flutter app." The diagram
connects the shared engine to Android and terminal workflows; it is not a
product screenshot or measured scan result. No stock or AI-generated imagery.
The source composition is local scratch, not a site dependency.

## Official brand assets

Copied unmodified from the research assets in
`/tmp/opencode/flutterguard-showcase/`; no recoloring, cropping, filters or
re-typing.

| Output | Source | SHA-256 |
|---|---|---|
| `assets/brand/google-play-badge-en.svg` | `get-it-on-google-play-en.svg` (Google Play badge package, digital SVG, English) | `4ffa4c7edd2f10b297ca4de2131eddaa00d03b2278d1e178fe512920d824ca34` |
| `assets/brand/github-lockup-white.svg` | `github-lockup-white.svg` (`GitHub_Logos.zip`, `GitHub Logos/SVG/GitHub_Lockup_White.svg`) | `d26a77282b5f0fc5e36d52aa64d0a8dfeb042dab5b65802805ce83373d72f5f5` |

- The official badge and lockup remain unmodified reference assets but are
  not displayed in the direct redesign. GitHub is a plain navbar text link.
- The Android workflow links to the Google Play URL:
  `https://play.google.com/store/apps/details?id=com.flutterguard.app`.
  It uses the inline Google Play glyph from the prior implementation, not a
  modified official badge. The public US listing returned HTTP 200 on
  2026-11-20. GitHub releases are updated separately from the Play listing.
- The Flutter mark is reused from the repository's `flutter.svg` glyph.
  APK layers and workflow connections are explanatory CSS diagrams, not invented
  app screenshots or measured scan results. No endorsement is implied.

## Font

- Family: Manrope, variable weight range 400-600, latin subset.
- File: `assets/fonts/manrope-latin.woff2`, 24,532 bytes,
  SHA-256 `8c2def024c1bf31aacf3624ae3c4d701269b4ec3dc765c04830839f0d36b2d9e`.
- Source: Google Fonts CSS API v23 (`fonts.googleapis.com/css2?family=Manrope:wght@400..600`),
  binary from `fonts.gstatic.com/s/manrope/v23/xn7gYHE41ni1AdIRggexSg.woff2`.
- License: SIL Open Font License 1.1, copyright 2018 The Manrope Project
  Authors. Full text in `assets/fonts/OFL.txt`.
- Served locally from `/assets/fonts/` with `font/woff2`; the page makes no
  runtime request to a font CDN. Other scripts use the browser's sans-serif
  fallback. The technical captions use the platform monospace stack.
