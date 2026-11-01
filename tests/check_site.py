#!/usr/bin/env python3
"""Behavioral smoke check for the FlutterGuard site.

Usage: python3 tests/check_site.py [URL] [SCREENSHOT_DIR] [--allow-default-404]

Runs against the live URL it is given (Python preview or the local nginx
container). Exits non-zero if any assertion fails.

The custom 404 document body is asserted by default because the shipped server
is nginx. `--allow-default-404` is the only accepted opt-out and exists solely
for `python3 -m http.server`, which serves its own generic 404 page; the flag
still requires a real 404 status.
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
        check("privacy sentence matches the shipped policy",
              "scans run on your device, without uploads." in page.locator("#pros .pros-list > li:first-child p").inner_text().lower()
              and "cannot leave the device" not in hero_text + page.locator("body").inner_text().lower())

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
        caption = page.locator(".device-caption").inner_text().lower() if page.locator(".device-caption").count() else ""
        check("caption says preview and recording later", "preview" in caption and "recording" in caption, caption)

        # Install cluster: working GitHub/APK actions, honest unavailable Play badge.
        hrefs = page.eval_on_selector_all("a[href]", "els => els.map(e => ({href: e.getAttribute('href'), text: e.textContent.trim()}))")
        find = lambda h: [a for a in hrefs if a["href"] == h]
        check("GitHub source link exact + labelled", page.evaluate("""() => [...document.querySelectorAll('a[href="https://github.com/anasfik/FlutterGuard"]')]
            .some(a => (a.textContent || '').includes('GitHub') || [...a.querySelectorAll('img')].some(i => i.alt === 'GitHub'))"""))
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
            const a = document.querySelector('.github-button');
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

        # Same-row install actions share a height; the Play note has no orphan word.
        row = page.evaluate("""() => {
            const d = document.querySelector('.download-button').getBoundingClientRect();
            const g = document.querySelector('.github-button').getBoundingClientRect();
            const el = document.querySelector('.store-note');
            const s = el ? getComputedStyle(el) : null;
            const range = document.createRange();
            if (el) range.selectNodeContents(el);
            const widths = el ? [...range.getClientRects()].filter(r => r.width > 0).map(r => r.width) : [];
            return {download: Math.round(d.height * 10) / 10, github: Math.round(g.height * 10) / 10,
                    downloadW: Math.round(d.width), githubW: Math.round(g.width),
                    wrap: s ? (s.textWrap || s['text-wrap']) : null, lines: widths.length,
                    last: widths.length ? Math.round(widths[widths.length - 1]) : 0,
                    widest: widths.length ? Math.round(Math.max(...widths)) : 0};
        }""")
        check("same-row install actions share a height", row["download"] >= 44 and abs(row["download"] - row["github"]) <= 0.5, str(row))
        check("Play note wraps without a one-word orphan", row["wrap"] == "balance" and row["lines"] <= 2
              and row["last"] >= 0.35 * row["widest"], str(row))

        # Content regions and copy.
        check("features section", page.locator("#features").count() == 1)
        check("three feature rows", page.locator("#features .feature-list > li").count() == 3)
        check("pros section", page.locator("#pros").count() == 1)
        check("three pros", page.locator("#pros .pros-list > li").count() == 3)
        check("contact section", page.locator("#contact").count() == 1)
        check("visible email link", any(a["text"] == "work@gwhyyy.com" for a in find(EMAIL)))
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
            "android 8 or newer",
            "static analysis records what the apk contains",
            "scan only apps you own or are authorised to test",
            "requires an uninstall",
            "exports are not a history restore",
            "flutter is a trademark of google llc",
            "not affiliated with google",
        )
        check("removed disclosure copy absent from body DOM text", all(s not in dom_text for s in removed),
              str([s for s in removed if s in dom_text]))
        check("removed copy absent from visible text", all(s not in body_text for s in removed),
              str([s for s in removed if s in body_text]))
        check("no visible Android 8+ copy", "android 8" not in body_text, body_text[:200])
        check("no absolute no-export privacy claim", "cannot leave the device" not in body_text)
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

        # Caching is a server concern; nginx must send it, Python preview may not.
        for path, needle in (("/assets/fonts/manrope-latin.woff2", "max-age=31536000"), ("/styles.css", "max-age=3600")):
            r = page.request.get(base + path)
            cc = r.headers.get("cache-control")
            if cc:
                check(f"{path} cache policy", needle in cc, cc)
            else:
                info(f"{path} cache policy absent on this server")

        # Security headers when the server sends them (nginx); CSP never weakens.
        csp = home_headers.get("content-security-policy")
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
            const cap = document.querySelector('.device-caption');
            return {left: Math.round(fig.left - hero.left), right: Math.round(hero.right - fig.right),
                    captionAlign: getComputedStyle(cap).textAlign, captionWrap: getComputedStyle(cap).textWrap};
        }""")
        check("tablet phone figure and caption centered in the single column",
              abs(tablet["left"] - tablet["right"]) <= 8 and tablet["captionAlign"] == "center"
              and tablet["captionWrap"] == "balance", str(tablet))

        # Word budget covers the visible page.
        page.set_viewport_size({"width": 1440, "height": 900})
        page.wait_for_timeout(80)
        words = page.evaluate("document.body.innerText.trim().split(/\\s+/).filter(Boolean).length")
        check(f"visible words <= {WORD_LIMIT}", words <= WORD_LIMIT, f"{words} words")
        desktop_h = page.evaluate("document.documentElement.scrollHeight")
        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(100)
        mobile_h = page.evaluate("document.documentElement.scrollHeight")
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

        # Forced colors must keep the branded GitHub action visible and focusable.
        fc = browser.new_context(viewport={"width": 1440, "height": 900}, forced_colors="active")
        fcp = fc.new_page()
        fcp.goto(base + "/", wait_until="load")
        fcp.wait_for_timeout(150)
        fc_state = fcp.evaluate("""() => {
            const a = document.querySelector('.github-button');
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
        fcp.locator(".download-button").focus()
        fcp.keyboard.press("Tab")
        fc_focus = fcp.evaluate("""() => {
            const el = document.activeElement;
            const s = getComputedStyle(el);
            return {cls: el.className, focusVisible: el.matches(':focus-visible'),
                    style: s.outlineStyle, width: parseFloat(s.outlineWidth), color: s.outlineColor};
        }""")
        check("forced colors keeps a visible focus outline on the GitHub button",
              fc_focus["cls"] == "github-button" and fc_focus["focusVisible"]
              and fc_focus["style"] == "solid" and fc_focus["width"] >= 2
              and fc_focus["color"] not in ("rgba(0, 0, 0, 0)", "transparent"), str(fc_focus))
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
