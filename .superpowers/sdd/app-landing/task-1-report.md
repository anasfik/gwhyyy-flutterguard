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

---

# Fix round 1/5 (S1b) - webp MIME and caching

**Status:** DONE

## Finding addressed

Reviewer (Important): `nginx.conf` declares a server-level `types{}` that
replaces the image's `mime.types`, and its own comment requires every served
extension to be listed. `webp` was missing, so `assets/app/*.webp` would be
served as `application/octet-stream` with `Cache-Control: no-cache` (inherited
from the server-level `expires -1`). The `location ~* \.(?:png|svg)$` cache
block also did not match `.webp`.

## Change (nginx.conf only)

1. Inside `types{}`, after `image/png png;`:
   `image/webp                 webp;`
2. Cache location widened:
   `location ~* \.(?:png|svg)$` becomes `location ~* \.(?:png|svg|webp)$`
   (`expires 1d` unchanged, which yields `max-age=86400`).

Nothing else edited. No em-dash added.

## Tests

| # | Check | Command | Result |
|---|-------|---------|--------|
| 1 | Image rebuild | `flock /tmp/opencode/flutterguard-build.lock docker build -t fg-site:local .` | PASS, `EXIT=0`, `naming to docker.io/library/fg-site:local done` |
| 2 | Serve container | `docker run -d --rm --name fgfix -p 127.0.0.1:18080:80 fg-site:local sh -c 'nginx -g "daemon off;"'` | PASS, container id `5b407a3e...` |
| 3 | Webp headers | `curl -sI http://127.0.0.1:18080/assets/app/fg-01-inventory.webp \| grep -iE 'content-type\|cache-control'` | PASS: `Content-Type: image/webp`, `Cache-Control: max-age=86400` |
| 3b | Feature webp headers | same curl on `/assets/app/feature-1024x500.webp` | PASS: `image/webp`, `max-age=86400` |
| 4 | Png still correct | curl on `/assets/app/icon-512.png` and `/icon-192.png` | PASS: `Content-Type: image/png`, `max-age=86400` on both |
| 5 | No types{} regression | curl HEAD on `/`, `/styles.css`, `/site.js`, `/favicon.svg`, `/site.webmanifest`, `/robots.txt` | PASS: `text/html; charset=utf-8`, `text/css`, `application/javascript; charset=utf-8`, `image/svg+xml`, `application/manifest+json`, `text/plain; charset=utf-8` |
| 6 | Cleanup | `docker stop fgfix` | PASS, echoed `fgfix`; `docker ps -a --filter name=fgfix` lists nothing (container gone via `--rm`) |

### Deviation from the literal verify command

The supplied command ran the container without publishing a port and then
curled `http://127.0.0.1:80`, which is not reachable from the host on the
default bridge network. Port 80, 8080 and 18080 were all free on the host
(`ss -ltnp`). I kept the same image, same `nginx -g "daemon off;"` command and
same asset paths, and added `-p 127.0.0.1:18080:80`, curling 18080. Header
values asserted are identical to the requested ones.

## Files changed

- `nginx.conf` (2 lines: one added `types{}` entry, one widened cache location)
- `.superpowers/sdd/app-landing/task-1-report.md` (this section)

## Concerns / leftovers

- `.webp` now inherits the 1-day image cache shared with png/svg. Fine for these
  static, hash-free filenames; if the artwork is ever replaced in place, bump
  the filename (e.g. `fg-01-inventory-v2.webp`) rather than shortening the TTL.
- `ico` still has no dedicated cache location (falls back to `expires -1`). Out
  of scope for this finding; no `.ico` is referenced by the site.
- Site still references none of the `assets/app/` files until S3 markup lands.
