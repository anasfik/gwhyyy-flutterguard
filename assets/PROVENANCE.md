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
shows the Conduit report overview. They are the only screenshots on the
homepage and are referenced with explicit 720x1600 dimensions.

## OG image

`og-image.png` (1200x630) was rendered from the live local page assets — the
real app icon, both new screenshots and the self-hosted Manrope face — with
headless Chromium. No stock or generated imagery.

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
