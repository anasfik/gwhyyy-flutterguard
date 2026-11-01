# Task 1 (S1) - App asset import

**Status:** DONE

**Commit:** see `git log -1 --format=%H` on `work/app-landing` (single S1 commit)

## Scope delivered

Imported real FlutterGuard app artwork from
`fg-remote/docs/play/` into `assets/app/` as WebP, and wired the 8 files into
the Docker image. No HTML, CSS, JS, manifest, robots, sitemap, llms*, 404,
nginx.conf or `_headers` changes.

## Test summary

| # | Check | Command | Result |
|---|-------|---------|--------|
| 1 | WebP decode + widths | `python3 -c "from PIL import Image; ..."` over `assets/app/*.webp` | PASS - 7/7 `WEBP`; 6 screenshots `(720, 1280)`, feature `(1024, 500)`; printed `ALL_WEBP_OK` |
| 1b | Icon byte copy | `file assets/app/icon-512.png` and `cmp <src> assets/app/icon-512.png` | PASS - `PNG image data, 512 x 512, 8-bit/color RGB`; `cmp` silent, printed `ICON_BYTE_IDENTICAL` (1973 B) |
| 2 | Image build | `flock /tmp/opencode/flutterguard-build.lock docker build -t fg-site:local .` | PASS - `EXIT=0`, `naming to docker.io/library/fg-site:local done` |
| 3 | Assets present in image | `docker run --rm fg-site:local sh -c 'ls -R /usr/share/nginx/html/assets/app'` | PASS - exactly 8 entries: `feature-1024x500.webp`, `fg-01-inventory.webp` ... `fg-06-privacy.webp`, `icon-512.png`; `wc -l` = 8 |
| 4 | Single commit | `git add assets/app Dockerfile .superpowers/sdd/app-landing/task-1-report.md && git commit -m "feat(assets): import real app screenshots, feature graphic, icon (S1)"` | PASS - one commit on `work/app-landing` |

## Files changed

Created:
- `assets/app/fg-01-inventory.webp` (40,848 B)
- `assets/app/fg-02-grade.webp` (38,726 B)
- `assets/app/fg-03-findings.webp` (46,120 B)
- `assets/app/fg-04-services.webp` (50,586 B)
- `assets/app/fg-05-settings.webp` (52,120 B)
- `assets/app/fg-06-privacy.webp` (61,408 B)
- `assets/app/feature-1024x500.webp` (13,312 B)
- `assets/app/icon-512.png` (1,973 B, byte copy of `docs/play/icon-512.png`)
- `.superpowers/sdd/app-landing/task-1-report.md`

Modified:
- `Dockerfile` - one added `COPY` line listing the 8 new paths to
  `/usr/share/nginx/html/assets/app/`. Pinned digest base image, healthcheck,
  EXPOSE and the existing root COPY list untouched.

## Conversion parameters

- Screenshots: 1080x1920 RGB source, LANCZOS resize to width 720 (→ 1280 tall),
  WebP `quality=82`, `method=6`.
- Feature graphic: 1024x500 source kept at 1024 wide, WebP `quality=82`,
  `method=6`.
- Icon: no re-encode, straight `cp` so bytes match the app's shipped icon.
- Total added payload: 304,050 B (~297 KiB) for all 8 files.

## Concerns / leftovers

- Site root `icon-512.png` (8,456 B) is deliberately NOT replaced. The real app
  icon lives only at `assets/app/icon-512.png`. Swapping the root icon and
  manifest/head references is S5 scope.
- `assets/app/` is now a tracked directory but no HTML references these files
  yet; until S3 lands markup the paths are dead weight in the image (harmless,
  ~297 KiB).
- Downloaded sources under `fg-remote/docs/play/` were read only, never modified.
- Not run (out of scope, parent owns): `ui-review`, `seo-polish`, deploy.
- Site-wide OG image (`og-image.png`, 53 KB) is unchanged; `feature-1024x500.webp`
  is imported but not yet used for social cards.
