# Asset provenance

Last updated: 2026-11-01. Only the files below are new; existing `icon-512.png`
files and the canonical raw captures were left untouched.

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
shows the Conduit report overview. The homepage now uses `inventory.webp` as
the single phone poster; `report.webp` stays in the repository as an unused
canonical capture and is not copied into the nginx image. The poster is
referenced with explicit 720x1600 dimensions and a documented native-video
replacement point (see the HTML comment beside it); no recording exists yet.

## OG image

`og-image.png` (1200x630, SHA-256
`d3d18a56b8da25683f04c514250b1b90a97680ecf196f75c801e38066287d9f6`) was
rendered for the split showcase with headless Chromium from the real app
poster, the self-hosted Manrope face and the page's own color tokens. No stock
or generated imagery. The source composition is a local scratch file, not a
site dependency.

## Official brand assets

Copied unmodified from the research assets in
`/tmp/opencode/flutterguard-showcase/`; no recoloring, cropping, filters or
re-typing.

| Output | Source | SHA-256 |
|---|---|---|
| `assets/brand/google-play-badge-en.svg` | `get-it-on-google-play-en.svg` (Google Play badge package, digital SVG, English) | `4ffa4c7edd2f10b297ca4de2131eddaa00d03b2278d1e178fe512920d824ca34` |
| `assets/brand/github-lockup-white.svg` | `github-lockup-white.svg` (`GitHub_Logos.zip`, `GitHub Logos/SVG/GitHub_Lockup_White.svg`) | `d26a77282b5f0fc5e36d52aa64d0a8dfeb042dab5b65802805ce83373d72f5f5` |

- Google Play badge: official Partner Marketing Hub artwork, kept full color at
  48 CSS px high (natural ratio 238.96:70.87), with one-quarter-height clear
  space and a solid page background. It is non-interactive (no link, no tab
  stop) and is paired with the page's own text, "Not yet available on Google
  Play". Availability was verified 2026-11-01: the listing URL returned HTTP
  404 for default and US requests while a known-live control returned 200.
  That proves those requests, not worldwide availability or Play Console
  review state. There is no published Google rule for showing this badge while
  a listing is unpublished; this truthful unavailable treatment is our
  explicit product decision, not a Google-sanctioned pattern. When the listing
  returns 200, make the badge a link to
  `https://play.google.com/store/apps/details?id=com.flutterguard.app`.
- GitHub lockup: official white mark plus wordmark on the brand-exception black
  button, unchanged, linking to the source repository. GitHub's brand page
  permits the Invertocat as a link/social button; this does not imply GitHub
  endorsement. File-level hashes above match the research copies.

## Font

- Family: Manrope, variable weight range 400–600, latin subset.
- File: `assets/fonts/manrope-latin.woff2` — 24,532 bytes,
  SHA-256 `8c2def024c1bf31aacf3624ae3c4d701269b4ec3dc765c04830839f0d36b2d9e`.
- Source: Google Fonts CSS API v23 (`fonts.googleapis.com/css2?family=Manrope:wght@400..600`),
  binary from `fonts.gstatic.com/s/manrope/v23/xn7gYHE41ni1AdIRggexSg.woff2`.
- License: SIL Open Font License 1.1, copyright 2018 The Manrope Project
  Authors. Full text in `assets/fonts/OFL.txt`.
- Served locally from `/assets/fonts/` with `font/woff2`; the page makes no
  runtime request to a font CDN. Arabic and other non-latin text falls back to
  `Noto Sans Arabic`/`Tahoma` from the font stack.
