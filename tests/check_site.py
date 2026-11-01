#!/usr/bin/env python3
"""Behavioral smoke check for the FlutterGuard site.

Usage: python3 tests/check_site.py [URL] [SCREENSHOT_DIR] [--allow-default-404]

Runs against the live URL it is given (Python preview or the local nginx
container). Exits non-zero if any assertion fails.

The custom 404 document body is asserted by default because the shipped server
is nginx. `--allow-default-404` is the only accepted opt-out and exists solely
for `python3 -m http.server`, which serves its own generic 404 page; the flag
still requires a real 404 status.

Header presence is asserted whenever the server identifies as nginx, before the
policy each header carries is checked, so a dropped CSP or Cache-Control fails
the run instead of shrinking the denominator. The Python preview sends neither
header and keeps its INFO downgrade.
"""

from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

CHROMIUM = "/usr/bin/chromium"
WORD_LIMIT = 300
OVERFLOW_WIDTHS = (320, 390, 768, 1280, 1440)
DOWNLOAD = "https://github.com/anasfik/FlutterGuard/releases/latest"
SOURCE = "https://github.com/anasfik/FlutterGuard"
PLAY = "https://play.google.com/store/apps/details?id=com.flutterguard.app"
EMAIL = "mailto:work@gwhyyy.com"
PRIVACY = "https://gwhyyy.com/privacy/flutterguard"
LICENSE = "https://github.com/anasfik/FlutterGuard/blob/main/LICENSE"

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + ("" if ok or not detail else f"  [{detail}]"))


def info(message: str) -> None:
    print(f"INFO  {message}")


def main(argv: list[str]) -> int:
    allow_default_404 = "--allow-default-404" in argv
    unknown = [a for a in argv if a.startswith("--") and a != "--allow-default-404"]
    if unknown:
        print(f"unknown option(s): {' '.join(unknown)}", file=sys.stderr)
        print(__doc__.strip(), file=sys.stderr)
        return 2
    positional = [a for a in argv if not a.startswith("--")]
    base = (positional[0] if positional else "http://127.0.0.1:8791").rstrip("/")
    shots = Path(positional[1]) if len(positional) > 1 else None
    host = urlparse(base).netloc
    if shots:
        shots.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROMIUM, headless=True)

        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        page = ctx.new_page()
        console_errors: list[str] = []
        page_errors: list[str] = []
        failed: list[str] = []
        requests: list[str] = []
        bad_responses: list[str] = []
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        page.on("requestfailed", lambda r: failed.append(f"{r.url} :: {r.failure}"))
        page.on("request", lambda r: requests.append(r.url))
        page.on("response", lambda r: bad_responses.append(f"{r.status} {r.url}") if r.status >= 400 and r.url != base + "/missing-page-xyz" else None)

        resp = page.goto(base + "/", wait_until="load")
        home_headers = resp.headers if resp else {}
        check("homepage returns 200", resp is not None and resp.status == 200, str(resp.status if resp else "no response"))
        check("language is English", page.locator("html").get_attribute("lang") == "en")

        h1s = page.eval_on_selector_all("h1", "els => els.map(e => e.textContent.trim())")
        check("exactly one h1", len(h1s) == 1, str(h1s))
        check("h1 copy", h1s == ["Security audit any released Flutter app."], str(h1s))
        check("no eyebrow above the headline", page.locator(".hero .eyebrow").count() == 0)
        check("no removed facts line element", page.locator(".facts").count() == 0)
        titles = page.evaluate("""() => {
            const meta = (sel) => document.querySelector(sel)?.getAttribute('content') || '';
            return {title: document.title, og: meta('meta[property="og:title"]'),
                    twitter: meta('meta[name="twitter:title"]'),
                    alt: meta('meta[property="og:image:alt"]')};
        }""")
        check("metadata titles share the new headline", "Security audit any released Flutter app" in titles["title"]
              and "—" not in titles["title"]
              and titles["og"] == "Security audit any released Flutter app."
              and titles["twitter"] == "Security audit any released Flutter app."
              and "Security audit any released Flutter app" in titles["alt"], str(titles))
        hero_text = page.locator(".hero-copy").inner_text().lower()
        check("no visible Android 8+ copy in the hero", "android 8" not in hero_text, hero_text)
        # The old #pros sentence is gone with that section; the on-device claim
        # now lives in the "Report" step, and the absolute no-export promise
        # must still never appear anywhere.
        features_text = page.locator("#features").inner_text().lower()
        check("on-device privacy claim survives without an absolute guarantee",
              "nothing is uploaded" in features_text
              and "cannot leave the device" not in hero_text + page.locator("body").inner_text().lower(), features_text[:200])

        page.evaluate("document.fonts.ready")
        check("Manrope self-hosted and loaded", page.evaluate("[...document.fonts].some(f => f.family.replace(/[\"\']/g, '') === 'Manrope' && f.status === 'loaded')"))
        check("font request served locally", any("/assets/fonts/manrope-latin.woff2" in u for u in requests))

        # Navbar: real mark and wordmark left, short in-page links right.
        check("navbar brand links home", page.locator('header a[href="/"]').count() >= 1)
        check("navbar brand mark loads", page.eval_on_selector("header .brand-mark", "e => e.complete && e.naturalWidth > 0"))
        check("navbar Features link", page.locator('header a[href="#features"]').count() == 1)
        check("navbar Contact link", page.locator('header a[href="#contact"]').count() == 1)
        check("no hamburger control", page.locator('header button, header [aria-expanded]').count() == 0)

        # Split hero with copy and one real poster inside a phone frame.
        check("split hero present", page.locator(".hero .hero-copy").count() == 1 and page.locator(".hero .hero-device").count() == 1)
        poster = page.evaluate("""() => {
            const img = document.querySelector('.device-poster');
            if (!img) return null;
            const r = img.getBoundingClientRect();
            return {src: img.getAttribute('src'), alt: img.alt, w: img.naturalWidth, h: img.naturalHeight,
                    ok: img.complete && img.naturalWidth > 0, renderedW: Math.round(r.width), renderedH: Math.round(r.height)};
        }""")
        check("phone poster is the real inventory capture", bool(poster) and (poster["src"] or "").endswith("/assets/app/inventory.webp"), str(poster))
        check("phone poster 720x1600 and loaded", bool(poster) and poster["w"] == 720 and poster["h"] == 1600 and poster["ok"], str(poster))
        check("phone poster keeps aspect ratio", bool(poster) and abs((poster["renderedW"] / poster["renderedH"]) - (720 / 1600)) < 0.02, str(poster))
        check("phone poster has useful alt text", bool(poster) and len(poster["alt"]) > 30)
        check("poster sits in a phone frame", page.locator(".device-frame .device-poster").count() == 1)
        check("no fake video/player", page.locator("video, .player, [class*='play-button'], [class*='play-icon'], button[aria-label*='play' i]").count() == 0)
        check("no device caption element", page.locator(".device-caption, .hero-device figcaption").count() == 0
              and "screen recording is coming later" not in page.locator("body").inner_text().lower())

        # Ambient backdrop behind the phone: decorative, clipped, physics-free.
        ambient = page.evaluate("""() => {
            const el = document.querySelector('.hero-device .device-ambient');
            const frame = document.querySelector('.hero-device .device-frame');
            if (!el || !frame) return null;
            const s = getComputedStyle(el);
            const host = getComputedStyle(el.parentElement);
            return {hidden: el.getAttribute('aria-hidden'), pe: s.pointerEvents, pos: s.position,
                    bg: s.backgroundImage, z: s.zIndex,
                    inside: el.parentElement.classList.contains('hero-device'),
                    beforeFrame: !!(el.compareDocumentPosition(frame) & Node.DOCUMENT_POSITION_FOLLOWING),
                    clip: host.overflow || host.overflowX,
                    anim: s.animationName, play: s.animationPlayState};
        }""")
        check("hero ambient layer is decorative, clipped and behind the frame",
              bool(ambient) and ambient["hidden"] == "true" and ambient["pe"] == "none"
              and ambient["pos"] == "absolute" and ambient["inside"] and ambient["beforeFrame"]
              and ambient["bg"] != "none" and ambient["clip"] in ("clip", "hidden"), str(ambient))

        # Install cluster: working GitHub/APK actions, honest unavailable Play badge.
        hrefs = page.eval_on_selector_all("a[href]", "els => els.map(e => ({href: e.getAttribute('href'), text: e.textContent.trim()}))")
        find = lambda h: [a for a in hrefs if a["href"] == h]
        check("GitHub source link in the navbar + labelled", page.evaluate("""() => [...document.querySelectorAll('header a[href="https://github.com/anasfik/FlutterGuard"]')]
            .some(a => (a.getAttribute('aria-label') || a.textContent || '').includes('GitHub') || [...a.querySelectorAll('img')].some(i => i.alt === 'GitHub'))"""))
        check("Get app primary in the navbar links the working release",
              page.locator(f'header a[href="{DOWNLOAD}"]').count() == 1
              and page.locator(f'header a[href="{DOWNLOAD}"]').inner_text().strip() == "Get app",
              str(find(DOWNLOAD)))
        check("hero action row no longer holds a GitHub button",
              page.locator(".install-actions .github-button").count() == 0
              and page.locator(f'.hero a[href="{SOURCE}"]').count() == 0)
        check("hero holds exactly one interactive install action",
              page.locator(".install-actions a").count() == 1
              and page.locator(".install-actions a").first.get_attribute("href") == DOWNLOAD)
        check("Download APK link exact + labelled", any("Download APK" in a["text"] for a in find(DOWNLOAD)))
        check("Play badge is not a link to a dead listing", not any(a["href"] == PLAY for a in hrefs))
        check("unavailable Play text is explicit", "Not yet available on Google Play" in page.locator(".store-note").inner_text() if page.locator(".store-note").count() else False)
        badge = page.evaluate("""() => {
            const img = document.querySelector('.play-badge img');
            if (!img) return null;
            const s = getComputedStyle(img);
            const r = img.getBoundingClientRect();
            return {src: img.getAttribute('src'), alt: img.alt, w: img.naturalWidth, h: img.naturalHeight,
                    hCss: r.height, linked: !!img.closest('a'), tab: img.tabIndex,
                    opacity: s.opacity, filter: s.filter, radius: s.borderRadius};
        }""")
        check("official Play badge asset loads", bool(badge) and (badge["src"] or "").startswith("/assets/brand/") and badge["w"] > 0, str(badge))
        check("official Play badge is unaltered and >=44px", bool(badge) and badge["opacity"] == "1"
              and badge["filter"] == "none" and badge["radius"] in ("0px", "")
              and badge["hCss"] >= 44 and abs(badge["w"] / badge["h"] - 238.96 / 70.87) < 0.02, str(badge))
        check("official Play badge is non-interactive", bool(badge) and not badge["linked"] and badge["tab"] == -1, str(badge))
        check("official Play badge alt tells the truth", bool(badge) and "Google Play" in badge["alt"] and "not yet available" in badge["alt"].lower(), str(badge))
        gh = page.evaluate("""() => {
            const a = document.querySelector('header .github-button');
            if (!a) return null;
            const s = getComputedStyle(a);
            const img = a.querySelector('img');
            return {href: a.getAttribute('href'), name: (a.getAttribute('aria-label') || img?.alt || a.textContent || '').trim(),
                    bg: s.backgroundColor, color: s.color,
                    icon: img ? img.getAttribute('src') : null, iconOk: img ? img.complete && img.naturalWidth > 0 : false};
        }""")
        check("black GitHub button with official white lockup", bool(gh) and gh["href"] == SOURCE and gh["name"] == "GitHub"
              and gh["bg"] in ("rgb(24, 23, 23)", "rgb(0, 0, 0)") and gh["icon"] == "/assets/brand/github-lockup-white.svg"
              and gh["iconOk"], str(gh))
        check("touch targets >= 44px", page.evaluate("""() => {
            const els = [...document.querySelectorAll('.install-actions a, .install-actions .play-badge, header a, footer a')];
            return els.every(e => { const r = e.getBoundingClientRect(); return r.height >= 43.5 || r.width >= 43.5; });
        }"""))

        # One aligned install row: primary button and the official badge are 48px
        # high on the same optical line, note attached to the badge cluster.
        row = page.evaluate("""() => {
            const dEl = document.querySelector('.download-button');
            const bEl = document.querySelector('.play-badge');
            if (!dEl || !bEl) return null;
            const d = dEl.getBoundingClientRect();
            const b = bEl.getBoundingClientRect();
            const el = document.querySelector('.store-note');
            const s = el ? getComputedStyle(el) : null;
            const range = document.createRange();
            if (el) range.selectNodeContents(el);
            const widths = el ? [...range.getClientRects()].filter(r => r.width > 0).map(r => r.width) : [];
            const slot = document.querySelector('.install-actions .play-slot');
            return {download: Math.round(d.height * 10) / 10, badge: Math.round(b.height * 10) / 10,
                    topGap: Math.round(Math.abs(d.top - b.top) * 10) / 10,
                    downloadW: Math.round(d.width), badgeW: Math.round(b.width),
                    badgeInSlot: !!slot && !!slot.querySelector('.play-badge'),
                    noteInSlot: !!slot && !!slot.querySelector('.store-note'),
                    wrap: s ? (s.textWrap || s['text-wrap']) : null, lines: widths.length,
                    last: widths.length ? Math.round(widths[widths.length - 1]) : 0,
                    widest: widths.length ? Math.round(Math.max(...widths)) : 0};
        }""")
        check("hero install row: primary and Play badge share one aligned 48px row",
              bool(row) and abs(row["download"] - 48) <= 0.6 and abs(row["badge"] - 48) <= 0.6 and row["topGap"] <= 1, str(row))
        check("Play note is attached to the badge cluster", bool(row) and row["badgeInSlot"] and row["noteInSlot"], str(row))
        check("Play note wraps without a one-word orphan", bool(row) and row["wrap"] == "balance" and row["lines"] <= 2
              and row["last"] >= 0.35 * row["widest"], str(row))

        # Content regions and copy.
        check("features section", page.locator("#features").count() == 1)
        check("features heading unchanged", page.locator("#features h2").inner_text().strip() == "What it does")
        nodes = [
            ("Discover", "Find Flutter apps already installed, or pick a single APK."),
            ("Inspect", "Read libraries, endpoints and exposed strings from the release."),
            ("Report", "Save the evidence on the phone; nothing is uploaded."),
        ]
        chain = page.evaluate("""() => {
            const tracks = [...document.querySelectorAll('#features .chain__track')];
            const real = tracks.find(t => t.getAttribute('aria-hidden') !== 'true') || tracks[0];
            const dup = tracks.find(t => t.getAttribute('aria-hidden') === 'true');
            const read = (ul) => [...ul.querySelectorAll(':scope > li')].map(li => [
                (li.querySelector('h3')?.textContent || '').trim(),
                (li.querySelector('p')?.textContent || '').trim()]);
            // The connector is ::after only: ::before is the dot, so an OR over
            // both is always true. The bridging geometry is asserted in the
            // moving context, where the gap actually exists.
            const first = real && real.querySelector('li');
            const conn = first ? getComputedStyle(first, '::after') : null;
            const dupStyle = dup ? getComputedStyle(dup) : null;
            return {tracks: tracks.length,
                    real: real ? read(real) : [], dup: dup ? read(dup) : [],
                    dupFocusable: dup ? dup.querySelectorAll('a, button, input, select, textarea, [tabindex]').length : -1,
                    connector: !!conn && conn.content !== 'none',
                    dupUserSelect: dupStyle ? dupStyle.userSelect : ''};
        }""")
        check("three named steps in one connected track", chain["real"] == [[t, b] for t, b in nodes], str(chain["real"]))
        check("duplicate loop track is hidden from AT and inert",
              chain["tracks"] == 2 and chain["dup"] == chain["real"] and chain["dupFocusable"] == 0, str(chain))
        check("chain nodes are visually connected", chain["connector"], str(chain))
        check("duplicate loop track is not copy-selectable", chain["dupUserSelect"] == "none", str(chain))
        check("no removed 'Why it stays local' section",
              page.locator("#pros, #pros-title, .pros-list").count() == 0
              and "why it stays local" not in page.locator("body").inner_text().lower())
        check("no dead #pros anchor", page.locator('a[href="#pros"]').count() == 0)
        check("contact section", page.locator("#contact").count() == 1)
        contact = page.evaluate("""() => {
            const s = document.querySelector('#contact');
            const links = [...s.querySelectorAll('a')].map(a => {
                const r = a.getBoundingClientRect();
                return {href: a.getAttribute('href'), text: (a.textContent || '').trim(),
                        h: Math.round(r.height * 10) / 10, w: Math.round(r.width * 10) / 10};
            });
            return {links, h2: (s.querySelector('h2')?.textContent || '').trim(),
                    forms: document.querySelectorAll('form').length, words: s.innerText.trim().split(/\\s+/).length};
        }""")
        check("contact offers exactly two actions and no form",
              contact["h2"] == "Contact" and len(contact["links"]) == 2 and contact["forms"] == 0, str(contact))
        check("contact actions are the email and issue channels",
              sorted(l["href"] for l in contact["links"]) == sorted([EMAIL, SOURCE + "/issues"]), str(contact["links"]))
        check("contact labels are explicit and >=44px tall",
              sorted(l["text"] for l in contact["links"]) == sorted(["Email work@gwhyyy.com", "Open a GitHub issue"])
              and all(l["h"] >= 43.5 for l in contact["links"]), str(contact["links"]))
        check("contact copy stays short", contact["words"] <= 40, f"{contact['words']} words")
        check("visible email link", any(a["text"] == "work@gwhyyy.com" for a in find(EMAIL))
              or any(a["text"] == "Email work@gwhyyy.com" for a in find(EMAIL)), str(find(EMAIL)))
        check("privacy link exact", bool(find(PRIVACY)))
        check("MIT license link exact", bool(find(LICENSE)))
        check("issues link exact", bool(find(SOURCE + "/issues")))
        check("footer maintainer and links", "FlutterGuard by Anas Fikhi" in page.locator("footer").inner_text() and page.locator(".footer-links a").count() == 2)
        check("at most five major content regions", page.evaluate("document.querySelectorAll('main > section, main > .hero').length") <= 5)

        # Demo is fully removed from links, content and sitemap/llms metadata.
        check("no demo/sample links", not any("/demo" in (a["href"] or "") for a in hrefs))
        body_text = page.locator("body").inner_text().lower()
        # textContent of a detached body clone still includes collapsed <details>
        # content, so removed disclosures cannot hide behind a summary.
        dom_text = page.evaluate("""() => {
            const clone = document.body.cloneNode(true);
            clone.querySelectorAll('script, style, template, noscript').forEach(n => n.remove());
            return clone.textContent.replace(/\\s+/g, ' ').toLowerCase();
        }""")
        check("no sample CTA copy", "see sample" not in body_text and "demo" not in body_text)
        check("no collapsed disclosure element", page.locator("details").count() == 0)
        removed = (
            "before you install",
            "android 8",
            "static analysis records what the apk contains",
            "scan only apps you own or are authorised to test",
            "requires an uninstall",
            "exports are not a history restore",
            "flutter is a trademark of google llc",
            "not affiliated with google",
            "why it stays local",
            "app preview. a screen recording is coming later",
            "screen recording is coming later",
        )
        check("removed copy absent from body DOM text", all(s not in dom_text for s in removed),
              str([s for s in removed if s in dom_text]))
        check("removed copy absent from visible text", all(s not in body_text for s in removed),
              str([s for s in removed if s in body_text]))
        check("no visible Android 8+ copy", "android 8" not in body_text, body_text[:200])
        check("no absolute no-export privacy claim", "cannot leave the device" not in body_text)
        home_html = page.request.get(base + "/").text()
        check("recording handoff comment preserved for the real clip",
              "Recording slot" in home_html and "<video" in home_html and "audit-recording.mp4" in home_html)
        for path in ("/sitemap.xml", "/llms.txt", "/llms-full.txt"):
            r = page.request.get(base + path)
            check(f"{path} avoids demo", r.status == 200 and "/demo" not in r.text(), str(r.status))

        # Static assets and content types.
        for path, ctype in (
            ("/styles.css", "text/css"),
            ("/assets/fonts/manrope-latin.woff2", "font/woff2"),
            ("/assets/app/inventory.webp", "image/webp"),
            ("/assets/brand/google-play-badge-en.svg", "image/svg+xml"),
            ("/assets/brand/github-lockup-white.svg", "image/svg+xml"),
            ("/icon-192.png", "image/png"),
            ("/og-image.png", "image/png"),
            ("/site.webmanifest", "application/manifest+json"),
        ):
            r = page.request.get(base + path)
            got = (r.headers.get("content-type") or "").split(";")[0]
            check(f"{path} 200 + {ctype}", r.status == 200 and got == ctype, f"{r.status} {got}")

        # Dead rules must not ship once their markup is gone.
        css = page.request.get(base + "/styles.css").text()
        for dead in (".eyebrow", ".device-caption", ".pros-list", ".feature-list"):
            check(f"styles.css carries no dead {dead} rule", dead not in css)

        # Caching is a server concern; nginx must send it, Python preview may not.
        # Presence is asserted before policy: a vanished header must fail the run
        # instead of silently shrinking the denominator. `Server: nginx` is the
        # only regime signal available (the preview sends neither CSP nor
        # Cache-Control), so presence checks run only against the shipped server.
        server = (home_headers.get("server") or "").lower()
        strict_headers = "nginx" in server
        for path, needle in (("/assets/fonts/manrope-latin.woff2", "max-age=31536000"), ("/styles.css", "max-age=3600")):
            r = page.request.get(base + path)
            cc = r.headers.get("cache-control")
            if strict_headers:
                check(f"{path} sends Cache-Control", bool(cc), f"Server: {server}")
            if cc:
                check(f"{path} cache policy", needle in cc, cc)
            else:
                info(f"{path} cache policy absent on this server")

        # Security headers when the server sends them (nginx); CSP never weakens.
        csp = home_headers.get("content-security-policy")
        if strict_headers:
            check("CSP header present", bool(csp), f"Server: {server}")
        if csp:
            for needle in ("default-src 'self'", "style-src 'self'", "font-src 'self'", "connect-src 'none'", "object-src 'none'", "frame-ancestors 'none'"):
                check(f"CSP {needle}", needle in csp, csp)
            check("no header errors", home_headers.get("x-content-type-options") == "nosniff" and home_headers.get("x-frame-options") == "DENY")
        else:
            info("security headers absent on this server (expected for Python preview)")

        # Layout: action before device on mobile, install visible at 1280x720.
        for width in OVERFLOW_WIDTHS:
            page.set_viewport_size({"width": width, "height": 844})
            page.wait_for_timeout(80)
            overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            check(f"no horizontal overflow at {width}px", overflow <= 1, f"{overflow}px")

        # Navbar is one row of reachable controls at desktop widths.
        for width in (1024, 1280, 1440):
            page.set_viewport_size({"width": width, "height": 900})
            page.wait_for_timeout(80)
            nav = page.evaluate("""() => {
                const items = [...document.querySelectorAll('header .brand, header .site-nav > a')]
                    .filter(e => e.getBoundingClientRect().width > 0)
                    .map(e => e.getBoundingClientRect());
                const cys = items.map(r => r.top + r.height / 2);
                return {count: items.length, spread: Math.round((Math.max(...cys) - Math.min(...cys)) * 10) / 10,
                        headerH: Math.round(document.querySelector('.header-inner').getBoundingClientRect().height),
                        overflow: Math.round(document.documentElement.scrollWidth - innerWidth)};
            }""")
            check(f"navbar holds one row at {width}px", nav["count"] >= 5 and nav["spread"] <= 1.5
                  and nav["headerH"] <= 96 and nav["overflow"] <= 1, str(nav))

        for width in (320, 390):
            page.set_viewport_size({"width": width, "height": 844})
            page.wait_for_timeout(80)
            navsmall = page.evaluate("""() => {
                const els = [...document.querySelectorAll('header .brand, header .site-nav > a')]
                    .filter(e => e.getBoundingClientRect().width > 0)
                    .map(e => { const r = e.getBoundingClientRect();
                        return {cls: e.className, left: Math.round(r.left), right: Math.round(r.right),
                                h: Math.round(r.height * 10) / 10}; });
                return {els, vw: innerWidth, overflow: Math.round(document.documentElement.scrollWidth - innerWidth)};
            }""")
            check(f"navbar brand, GitHub and Get app stay reachable at {width}px",
                  navsmall["overflow"] <= 1 and len(navsmall["els"]) >= 3
                  and any("github-button" in e["cls"] for e in navsmall["els"])
                  and any("navbar-cta" in e["cls"] for e in navsmall["els"])
                  and all(0 <= e["left"] and e["right"] <= navsmall["vw"] and e["h"] >= 43.5 for e in navsmall["els"]),
                  str(navsmall))

        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(100)
        order = page.evaluate("""() => {
            const a = document.querySelector('.install-actions')?.getBoundingClientRect();
            const d = document.querySelector('.device-frame')?.getBoundingClientRect();
            return a && d ? {actionsTop: Math.round(a.top), deviceTop: Math.round(d.top)} : null;
        }""")
        check("mobile installation actions precede phone", bool(order) and order["actionsTop"] < order["deviceTop"], str(order))

        page.set_viewport_size({"width": 320, "height": 800})
        page.wait_for_timeout(120)
        header_fit = page.evaluate("""() => {
            const b = document.querySelector('header .brand')?.getBoundingClientRect();
            const n = document.querySelector('header .site-nav')?.getBoundingClientRect();
            return b && n ? {brandRight: Math.round(b.right), navLeft: Math.round(n.left)} : null;
        }""")
        check("header brand and nav do not collide at 320px", bool(header_fit) and header_fit["brandRight"] <= header_fit["navLeft"], str(header_fit))

        page.set_viewport_size({"width": 1280, "height": 720})
        page.wait_for_timeout(100)
        visible = page.evaluate("""() => {
            const el = document.querySelector('.install-actions');
            if (!el) return false;
            const r = el.getBoundingClientRect();
            return r.top >= 0 && r.top < 720 && r.bottom > 0;
        }""")
        check("installation actions visible at 1280x720", visible)

        # The longer headline must stay short enough to keep the CTA in the fold.
        for width, height in ((1280, 720), (1440, 900)):
            page.set_viewport_size({"width": width, "height": height})
            page.wait_for_timeout(120)
            fold = page.evaluate("""() => {
                const h1 = document.querySelector('h1');
                const range = document.createRange();
                range.selectNodeContents(h1);
                const lines = [...range.getClientRects()].filter(r => r.height > 1).length;
                const a = document.querySelector('.install-actions').getBoundingClientRect();
                return {lines, actionsBottom: Math.round(a.bottom), fold: innerHeight,
                        clipped: h1.scrollWidth > h1.clientWidth + 1};
            }""")
            check(f"h1 renders in at most three lines at {width}px", fold["lines"] <= 3, str(fold))
            check(f"install actions visible without scrolling at {width}x{height}", 0 <= fold["actionsBottom"] <= fold["fold"], str(fold))
            info(f"h1 lines at {width}x{height}: {fold['lines']}; actions bottom {fold['actionsBottom']}px of {fold['fold']}px")

        for width in (320, 390):
            page.set_viewport_size({"width": width, "height": 844})
            page.wait_for_timeout(120)
            fit = page.evaluate("""() => {
                const h1 = document.querySelector('h1').getBoundingClientRect();
                return {left: Math.round(h1.left), right: Math.round(h1.right), vw: innerWidth,
                        clipped: document.querySelector('h1').scrollWidth > document.querySelector('h1').clientWidth + 1,
                        overflow: document.documentElement.scrollWidth - innerWidth};
            }""")
            check(f"h1 not clipped or overflowing at {width}px", not fit["clipped"] and fit["left"] >= 0
                  and fit["right"] <= fit["vw"] and fit["overflow"] <= 1, str(fit))

        page.set_viewport_size({"width": 768, "height": 1024})
        page.wait_for_timeout(120)
        tablet = page.evaluate("""() => {
            const fig = document.querySelector('.hero-device').getBoundingClientRect();
            const hero = document.querySelector('.hero').getBoundingClientRect();
            return {left: Math.round(fig.left - hero.left), right: Math.round(hero.right - fig.right)};
        }""")
        check("tablet phone figure centered in the single column",
              abs(tablet["left"] - tablet["right"]) <= 8, str(tablet))

        # Word budget covers the visible page.
        page.set_viewport_size({"width": 1440, "height": 900})
        page.wait_for_timeout(80)
        words = page.evaluate("document.body.innerText.trim().split(/\\s+/).filter(Boolean).length")
        check(f"visible words <= {WORD_LIMIT}", words <= WORD_LIMIT, f"{words} words")
        desktop_h = page.evaluate("document.documentElement.scrollHeight")
        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(100)
        mobile_h = page.evaluate("document.documentElement.scrollHeight")
        # Static (reduce) fallback at one column: a connector may not reach the
        # container edge as a decorative divider. Short or absent, never full width.
        mobile_chain = page.evaluate("""() => {
            const track = document.querySelector('#features .chain__track:not([aria-hidden="true"])');
            if (!track) return null;
            const nodes = [...track.querySelectorAll(':scope > li')];
            const cols = getComputedStyle(track).gridTemplateColumns.split(' ').filter(v => parseFloat(v) > 0).length;
            return {cols, rules: nodes.map(li => {
                const a = getComputedStyle(li, '::after');
                const w = parseFloat(a.width);
                return {content: a.content, width: a.width, insetEnd: a.insetInlineEnd,
                        short: a.content === 'none' || (w > 0 && w <= 24)};
            })};
        }""")
        check("reduced-motion single column keeps each connector short",
              bool(mobile_chain) and mobile_chain["cols"] == 1
              and all(r["short"] for r in mobile_chain["rules"]), str(mobile_chain))
        # The stacked install column is centred, not hard-left under a full-width CTA.
        mobile_stack = page.evaluate("""() => {
            const slot = document.querySelector('.install-actions .play-slot');
            const badge = document.querySelector('.play-badge');
            const note = document.querySelector('.store-note');
            if (!slot || !badge || !note) return null;
            const mid = (el) => { const r = el.getBoundingClientRect(); return Math.round((r.left + r.width / 2) * 10) / 10; };
            return {slot: mid(slot), badge: mid(badge), note: mid(note)};
        }""")
        check("narrow install stack is centred under the primary action",
              bool(mobile_stack) and abs(mobile_stack["badge"] - mobile_stack["slot"]) <= 2
              and abs(mobile_stack["note"] - mobile_stack["slot"]) <= 2, str(mobile_stack))
        page.set_viewport_size({"width": 1440, "height": 900})
        check("desktop height within showcase range", desktop_h <= 2600, f"{desktop_h}px")
        check("mobile height within showcase range", mobile_h <= 3600, f"{mobile_h}px")
        info(f"heights: desktop {desktop_h}px, mobile {mobile_h}px; words {words}")

        # Keyboard path: skip link, brand, then footer links.
        page.evaluate("document.querySelector('.skip-link').focus()")
        check("skip link receives focus", page.evaluate("document.activeElement.classList.contains('skip-link')"))
        page.keyboard.press("Tab")
        check("tab reaches navbar brand", page.evaluate("document.activeElement.classList.contains('brand')"))
        page.evaluate("document.querySelector('.footer-links a').focus()")
        check("footer links are focusable", page.evaluate("document.activeElement.closest('.footer-links') !== null"))

        # Reduced motion dial.
        durations = page.evaluate("""() => [...document.querySelectorAll('.button, .github-button, .download-button, a')]
            .slice(0, 8).map(e => getComputedStyle(e).transitionDuration)""")
        check("reduced motion collapses transitions", all(d in ("0.00001s", "0s", "0.01ms", "1e-05s") for d in durations), str(durations))

        static_motion = page.evaluate("""() => {
            const track = document.querySelector('.chain__track');
            const amb = document.querySelector('.device-ambient');
            if (!track || !amb) return null;
            const t = getComputedStyle(track);
            const a = getComputedStyle(amb);
            return {trackName: t.animationName, trackPlay: t.animationPlayState,
                    ambName: a.animationName, ambPlay: a.animationPlayState, ambBg: a.backgroundImage};
        }""")
        check("reduced motion leaves a static, still-decorated chain and hero backdrop",
              bool(static_motion) and static_motion["trackName"] == "none" and static_motion["trackPlay"] == "paused"
              and static_motion["ambName"] == "none" and static_motion["ambPlay"] == "paused"
              and static_motion["ambBg"] not in ("", "none"), str(static_motion))

        # Motion context: the loop and the drift run, and the native pause control works.
        # Measured at 390px first: that is where a missing clip on .chain turns the
        # moving tracks into a horizontal scrollbar (the reduce branch cannot see it).
        motion = browser.new_context(viewport={"width": 390, "height": 844}, reduced_motion="no-preference")
        mp = motion.new_page()
        mp.goto(base + "/", wait_until="load")
        mp.wait_for_timeout(250)
        anim = mp.evaluate("""() => {
            const track = document.querySelector('.chain__track');
            const amb = document.querySelector('.device-ambient');
            if (!track || !amb) return null;
            const t = getComputedStyle(track);
            const a = getComputedStyle(amb);
            const secs = (s) => (s || '0s').split(',').map(v => parseFloat(v) || 0);
            const li = document.querySelector('#features .chain__track:not([aria-hidden="true"]) > li');
            const conn = li ? getComputedStyle(li, '::after') : null;
            return {trackName: t.animationName, trackDur: secs(t.animationDuration), trackPlay: t.animationPlayState,
                    trackIter: t.animationIterationCount, ambName: a.animationName,
                    ambDur: secs(a.animationDuration), ambPlay: a.animationPlayState,
                    overflowX: document.documentElement.scrollWidth - innerWidth,
                    connector: conn ? {content: conn.content, insetEnd: parseFloat(conn.insetInlineEnd),
                                       width: parseFloat(conn.width)} : null};
        }""")
        check("chain loops slowly and endlessly",
              bool(anim) and anim["trackName"] != "none" and all(d >= 25 for d in anim["trackDur"])
              and anim["trackIter"] == "infinite", str(anim))
        check("hero ambient drift runs behind the phone",
              bool(anim) and anim["ambName"] != "none" and all(d >= 25 for d in anim["ambDur"]), str(anim))
        check("chain connector bridges the gap to the next node",
              bool(anim) and bool(anim["connector"]) and anim["connector"]["content"] != "none"
              and anim["connector"]["insetEnd"] < -0.5 and anim["connector"]["width"] > 20, str(anim["connector"]))
        check("no horizontal overflow while the chain animates at 390px",
              bool(anim) and anim["overflowX"] <= 1, str(anim))
        mp.set_viewport_size({"width": 1440, "height": 900})
        mp.wait_for_timeout(150)
        props = mp.evaluate("""() => {
            const out = [];
            for (const sheet of document.styleSheets) {
                let rules; try { rules = sheet.cssRules; } catch (e) { continue; }
                for (const rule of rules) {
                    if (rule.type !== CSSRule.KEYFRAMES_RULE) continue;
                    for (const kf of rule.cssRules) for (const p of kf.style) out.push(p);
                }
            }
            return [...new Set(out)].sort();
        }""")
        check("keyframes animate transform/opacity only", bool(props) and set(props) <= {"transform", "opacity"}, str(props))
        ctl = mp.evaluate("""() => {
            const box = document.querySelector('#pause-motion');
            const label = box ? ((box.labels && box.labels[0]) || document.querySelector('label[for="pause-motion"]')) : null;
            if (!box || !label) return null;
            const r = label.getBoundingClientRect();
            return {type: box.type, inFeatures: !!box.closest('#features'), checked: box.checked,
                    label: (label.textContent || '').trim(), h: Math.round(r.height * 10) / 10,
                    w: Math.round(r.width * 10) / 10, focusable: box.tabIndex >= 0,
                    inlineScript: document.querySelectorAll('script:not([type="application/ld+json"])').length,
                    handlers: document.querySelectorAll('[onclick], [onmouseover], [onload]').length};
        }""")
        check("pause control is a labelled checkbox in the features section",
              bool(ctl) and ctl["type"] == "checkbox" and ctl["inFeatures"] and ctl["label"] == "Pause motion"
              and ctl["focusable"] and ctl["checked"] is False, str(ctl))
        check("pause control target >= 44px", bool(ctl) and ctl["h"] >= 43.5, str(ctl))
        check("no script or inline handler needed for pause", bool(ctl) and ctl["inlineScript"] == 0 and ctl["handlers"] == 0, str(ctl))
        if ctl:
            mp.locator('label[for="pause-motion"]').click()
            mp.wait_for_timeout(60)
        paused = mp.evaluate("""() => {
            const box = document.querySelector('#pause-motion');
            const track = document.querySelector('.chain__track');
            const amb = document.querySelector('.device-ambient');
            if (!box || !track || !amb) return null;
            return {checked: box.checked, trackPlay: getComputedStyle(track).animationPlayState,
                    ambPlay: getComputedStyle(amb).animationPlayState};
        }""")
        check("pause control freezes the chain and the ambient drift",
              bool(paused) and paused["checked"] and paused["trackPlay"] == "paused"
              and paused["ambPlay"] == "paused", str(paused))
        if shots and ctl:
            mp.set_viewport_size({"width": 1440, "height": 900})
            mp.locator("#features").scroll_into_view_if_needed()
            mp.wait_for_timeout(150)
            mp.locator("#features").screenshot(path=str(shots / "preliminary-chain-1440-paused.png"))
            mp.locator('label[for="pause-motion"]').click()
            mp.wait_for_timeout(150)
            mp.locator("#features").screenshot(path=str(shots / "preliminary-chain-1440.png"))
        motion.close()

        if shots:
            page.set_viewport_size({"width": 1440, "height": 900})
            page.wait_for_timeout(120)
            page.evaluate("document.activeElement && document.activeElement.blur(); window.scrollTo(0, 0)")
            page.screenshot(path=str(shots / "preliminary-desktop-1440.png"), full_page=True)
            page.set_viewport_size({"width": 1280, "height": 720})
            page.wait_for_timeout(150)
            page.evaluate("window.scrollTo(0, 0)")
            page.screenshot(path=str(shots / "preliminary-desktop-1280x720.png"))
            page.set_viewport_size({"width": 768, "height": 1024})
            page.wait_for_timeout(150)
            page.evaluate("window.scrollTo(0, 0)")
            page.screenshot(path=str(shots / "preliminary-tablet-768.png"), full_page=True)
            page.set_viewport_size({"width": 390, "height": 844})
            page.wait_for_timeout(150)
            page.evaluate("window.scrollTo(0, 0)")
            page.screenshot(path=str(shots / "preliminary-mobile-390.png"), full_page=True)
            page.set_viewport_size({"width": 320, "height": 844})
            page.wait_for_timeout(150)
            page.evaluate("window.scrollTo(0, 0)")
            page.screenshot(path=str(shots / "preliminary-mobile-320.png"), full_page=True)
            info(f"captures written to {shots}")

        check("no console errors", not console_errors, "; ".join(console_errors))
        check("no page errors", not page_errors, "; ".join(page_errors))
        check("no failed requests", not failed, "; ".join(failed))
        check("no failed asset responses", not bad_responses, "; ".join(bad_responses))
        check("all requests stay on this origin", all(urlparse(u).netloc == host for u in requests), str(sorted({urlparse(u).netloc for u in requests})))

        # Content without JavaScript: poster, badge and working install remain.
        nojs = browser.new_context(java_script_enabled=False, viewport={"width": 1440, "height": 900})
        njs = nojs.new_page()
        njs.goto(base + "/", wait_until="load")
        check("no-JS h1 visible", njs.locator("h1").is_visible())
        check("no-JS poster visible", njs.locator(".device-poster").is_visible())
        check("no-JS Play badge visible", njs.locator(".play-badge img").is_visible())
        check("no-JS working actions visible", njs.locator(f'a[href="{DOWNLOAD}"]').first.is_visible() and njs.locator(f'a[href="{SOURCE}"]').first.is_visible())
        nojs.close()

        # Demo route is gone in every form; the custom 404 is real by default.
        for path in ("/demo", "/demo/", "/demo/index.html"):
            r = page.request.get(base + path)
            check(f"{path} returns 404", r.status == 404, str(r.status))
        missing = page.request.get(base + "/missing-page-xyz")
        html = missing.text()
        check("missing route returns 404", missing.status == 404, str(missing.status))
        custom_body = "That page does not exist." in html and 'href="/"' in html and "/styles.css" in html
        if allow_default_404 and missing.status == 404 and not custom_body:
            info("404 body is the server default (permitted by --allow-default-404 for the Python preview)")
        else:
            check("missing route serves the custom 404 body", custom_body,
                  "server default 404 body" if not custom_body else "")
        direct = page.request.get(base + "/404.html")
        direct_html = direct.text()
        check("404 document copy + home link", direct.status == 200 and "That page does not exist." in direct_html and 'href="/"' in direct_html, str(direct.status))
        check("404 uses product stylesheet", "/styles.css" in direct_html)
        check("404 document stays noindex", 'name="robots" content="noindex' in direct_html)
        check("404 document has no canonical", 'rel="canonical"' not in direct_html)

        # Forced colors must keep every primary action readable and button-like.
        fc = browser.new_context(viewport={"width": 1440, "height": 900}, forced_colors="active")
        fcp = fc.new_page()
        fcp.goto(base + "/", wait_until="load")
        fcp.wait_for_timeout(150)
        fc_state = fcp.evaluate("""() => {
            const a = document.querySelector('header .github-button');
            if (!a) return null;
            const s = getComputedStyle(a);
            const img = a.querySelector('img');
            return {bg: s.backgroundColor, adjust: s.forcedColorAdjust,
                    icon: img ? img.getAttribute('src') : null,
                    iconOk: img ? img.complete && img.naturalWidth > 0 : false,
                    iconFilter: img ? getComputedStyle(img).filter : null};
        }""")
        check("forced colors keeps the black GitHub button with its white lockup",
              bool(fc_state) and fc_state["bg"] in ("rgb(24, 23, 23)", "rgb(0, 0, 0)")
              and fc_state["adjust"] == "none" and fc_state["icon"] == "/assets/brand/github-lockup-white.svg"
              and fc_state["iconOk"] and fc_state["iconFilter"] == "none", str(fc_state))
        fc_primary = fcp.evaluate("""() => {
            const lum = (c) => {
                const parts = (c.match(/[\\d.]+/g) || ['0', '0', '0']).slice(0, 3).map(Number).map(v => {
                    const s = v / 255;
                    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
                });
                return 0.2126 * parts[0] + 0.7152 * parts[1] + 0.0722 * parts[2];
            };
            const ratio = (a, b) => { const p = [lum(a), lum(b)].sort((x, y) => y - x); return (p[0] + 0.05) / (p[1] + 0.05); };
            const read = (el) => {
                if (!el) return null;
                const s = getComputedStyle(el);
                const r = el.getBoundingClientRect();
                return {bg: s.backgroundColor, color: s.color,
                        borderW: parseFloat(s.borderTopWidth), borderStyle: s.borderTopStyle,
                        borderColor: s.borderTopColor,
                        contrast: Math.round(ratio(s.color, s.backgroundColor) * 100) / 100,
                        h: Math.round(r.height * 10) / 10};
            };
            return {download: read(document.querySelector('.download-button')),
                    cta: read(document.querySelector('.navbar-cta')),
                    page: getComputedStyle(document.body).backgroundColor};
        }""")
        visible_border = ("rgba(0, 0, 0, 0)", "transparent")
        check("forced colors keeps the hero primary action a readable button",
              bool(fc_primary) and fc_primary["download"] is not None
              and fc_primary["download"]["borderW"] >= 1 and fc_primary["download"]["borderStyle"] == "solid"
              and fc_primary["download"]["borderColor"] not in visible_border
              and fc_primary["download"]["contrast"] >= 4.5 and fc_primary["download"]["h"] >= 43.5,
              str(fc_primary))
        check("forced colors keeps the navbar Get app a readable button",
              bool(fc_primary) and fc_primary["cta"] is not None
              and fc_primary["cta"]["borderW"] >= 1 and fc_primary["cta"]["borderStyle"] == "solid"
              and fc_primary["cta"]["borderColor"] not in visible_border
              and fc_primary["cta"]["contrast"] >= 4.5 and fc_primary["cta"]["h"] >= 43.5,
              str(fc_primary))

        def focus_state(pg):
            return pg.evaluate("""() => {
                const el = document.activeElement;
                const s = getComputedStyle(el);
                return {cls: el.className, focusVisible: el.matches(':focus-visible'),
                        style: s.outlineStyle, width: parseFloat(s.outlineWidth),
                        color: s.outlineColor, bg: s.backgroundColor};
            }""")

        def ring_ok(state):
            return (state["focusVisible"] and state["style"] == "solid" and state["width"] >= 2
                    and state["color"] not in visible_border and state["color"] != state["bg"])

        fcp.locator(".download-button").focus()
        fcp.keyboard.press("Shift+Tab")  # backwards lands on the navbar primary
        fc_nav_focus = focus_state(fcp)
        check("forced colors keeps a visible focus outline on the navbar Get app",
              fc_nav_focus["cls"] == "navbar-cta" and ring_ok(fc_nav_focus), str(fc_nav_focus))
        fcp.keyboard.press("Shift+Tab")
        fc_focus = focus_state(fcp)
        check("forced colors keeps a visible focus outline on the GitHub button",
              fc_focus["cls"] == "github-button" and ring_ok(fc_focus), str(fc_focus))
        fcp.keyboard.press("Tab")
        fcp.keyboard.press("Tab")
        fc_hero_focus = focus_state(fcp)
        check("forced colors keeps a visible focus outline on the hero primary action",
              fc_hero_focus["cls"] == "download-button" and ring_ok(fc_hero_focus), str(fc_hero_focus))
        if shots:
            fcp.screenshot(path=str(shots / "preliminary-forced-colors-1440.png"))
            info(f"forced-colors capture: {shots / 'preliminary-forced-colors-1440.png'}")
        fc.close()

        ctx.close()
        browser.close()

    failed_checks = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed_checks)}/{len(results)} checks passed")
    return 1 if failed_checks else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
