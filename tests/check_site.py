#!/usr/bin/env python3
"""Behavioral smoke check for the FlutterGuard site.

Usage: python3 tests/check_site.py http://127.0.0.1:8791 [screenshot-dir]

Runs against the live URL it is given (Python preview or the local nginx
container). Exits non-zero on the first failed assertion group.
"""

from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

CHROMIUM = "/usr/bin/chromium"
WORD_LIMIT = 149
HEIGHT_LIMITS = {1440: 1600, 390: 2400}
OVERFLOW_WIDTHS = (320, 390, 768, 1280, 1440)
DOWNLOAD = "https://github.com/anasfik/FlutterGuard/releases/latest"
SOURCE = "https://github.com/anasfik/FlutterGuard"
SCREENS = ("inventory.webp", "report.webp")

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + ("" if ok or not detail else f"  [{detail}]"))


def main() -> int:
    base = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8791").rstrip("/")
    shots = Path(sys.argv[2]) if len(sys.argv) > 2 else None
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
        check("homepage returns 200", resp is not None and resp.status == 200, str(resp.status if resp else "no response"))

        h1s = page.eval_on_selector_all("h1", "els => els.map(e => e.textContent.trim())")
        check("exactly one h1", len(h1s) == 1, str(h1s))
        check("h1 copy", h1s == ["Look inside a Flutter APK."], str(h1s))
        lines = page.evaluate("""() => {
            const h = document.querySelector('h1');
            return Math.round(h.getBoundingClientRect().height / parseFloat(getComputedStyle(h).lineHeight));
        }""")
        check("h1 at most two lines at 1440px", lines <= 2, f"{lines} lines")

        page.evaluate("document.fonts.ready")
        check("Manrope self-hosted and loaded", page.evaluate("[...document.fonts].some(f => f.family.replace(/[\"\']/g, '') === 'Manrope' && f.status === 'loaded')"))
        check("font request served locally", any("/assets/fonts/manrope-latin.woff2" in u for u in requests))

        # Genuine raw screenshots, explicit dimensions, no old storeframes.
        imgs = page.eval_on_selector_all(
            "main img",
            "els => els.map(e => ({src: e.getAttribute('src'), w: e.naturalWidth, h: e.naturalHeight, ok: e.complete && e.naturalWidth > 0, alt: e.alt}))",
        )
        check("exactly two app screenshots", len(imgs) == 2, str([i["src"] for i in imgs]))
        check("screenshots are new real captures", sorted((i["src"] or "").rsplit("/", 1)[-1] for i in imgs) == sorted(SCREENS), str([i["src"] for i in imgs]))
        check("screenshots 720x1600 and loaded", all(i["w"] == 720 and i["h"] == 1600 and i["ok"] for i in imgs), str(imgs))
        check("screenshots have useful alt text", all(len(i["alt"]) > 20 for i in imgs))

        hrefs = page.eval_on_selector_all("a[href]", "els => els.map(e => ({href: e.getAttribute('href'), text: e.textContent.trim()}))")
        find = lambda h: [a for a in hrefs if a["href"] == h]
        check("download link exact + labelled", any(a["text"] == "Download APK" for a in find(DOWNLOAD)))
        check("source link exact", any(a["text"] == "GitHub" for a in find(SOURCE)))
        check("sample link exact", any(a["text"] == "See sample" for a in find("/demo/")))
        check("contact link", bool(find("mailto:work@gwhyyy.com")))
        check("privacy link", bool(find("https://gwhyyy.com/privacy/flutterguard")))
        check("issues link", bool(find(SOURCE + "/issues")))

        # Closed page stays short.
        for width, limit in HEIGHT_LIMITS.items():
            page.set_viewport_size({"width": width, "height": 900 if width > 500 else 844})
            page.wait_for_timeout(120)
            height = page.evaluate("document.documentElement.scrollHeight")
            check(f"closed height {width}px <= {limit}", height <= limit, f"{height}px")

        # Word budget includes expanded install notes, nav and footer.
        page.set_viewport_size({"width": 1440, "height": 900})
        page.eval_on_selector("main details", "d => d.open = true")
        page.wait_for_timeout(80)
        words = page.evaluate("document.body.innerText.trim().split(/\\s+/).filter(Boolean).length")
        check(f"visible words <= {WORD_LIMIT} with notes expanded", words <= WORD_LIMIT, f"{words} words")
        height_open = page.evaluate("document.documentElement.scrollHeight")
        print(f"INFO  expanded height 1440px: {height_open}px; words: {words}")
        page.eval_on_selector("main details", "d => d.open = false")

        # Keyboard-native disclosure.
        summary = page.locator("main details summary").first
        summary.focus()
        page.keyboard.press("Enter")
        opened = page.eval_on_selector("main details", "d => d.open")
        page.keyboard.press("Enter")
        closed = page.eval_on_selector("main details", "d => !d.open")
        check("native disclosure opens and closes by keyboard", opened and closed)

        # No horizontal overflow at the listed widths.
        for width in OVERFLOW_WIDTHS:
            page.set_viewport_size({"width": width, "height": 844})
            page.wait_for_timeout(80)
            overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            check(f"no horizontal overflow at {width}px", overflow <= 1, f"{overflow}px")

        if shots:
            page.evaluate("document.activeElement && document.activeElement.blur()")
            page.set_viewport_size({"width": 1440, "height": 900})
            page.screenshot(path=str(shots / "preliminary-desktop-1440.png"), full_page=True)
            page.set_viewport_size({"width": 390, "height": 844})
            page.screenshot(path=str(shots / "preliminary-mobile-390.png"), full_page=True)

        check("no console errors", not console_errors, "; ".join(console_errors))
        check("no page errors", not page_errors, "; ".join(page_errors))
        check("no failed requests", not failed, "; ".join(failed))
        check("no failed asset responses", not bad_responses, "; ".join(bad_responses))
        check("all requests stay on this origin", all(urlparse(u).netloc == host for u in requests), str(sorted({urlparse(u).netloc for u in requests})))

        # Content without JavaScript.
        nojs = browser.new_context(java_script_enabled=False, viewport={"width": 1440, "height": 900})
        njs = nojs.new_page()
        njs.goto(base + "/", wait_until="load")
        check("no-JS h1 visible", njs.locator("h1").is_visible())
        check("no-JS screenshot count", njs.locator("main img").count() == 2)
        check("no-JS download visible", njs.locator(f'a[href="{DOWNLOAD}"]').first.is_visible())
        nojs.close()

        # Sample report behavior.
        page.goto(base + "/demo/", wait_until="load")
        check("sample is noindex", page.locator('meta[name="robots"]').get_attribute("content").startswith("noindex"))
        check("sample banner is explicit", "Synthetic" in page.locator(".sample-banner").inner_text())
        check("sample home link", page.locator('a[href="/"]').count() > 0)

        tabs = page.locator('[role="tab"]')
        check("three sample views", tabs.count() == 3)
        tabs.nth(0).focus()
        page.keyboard.press("ArrowRight")
        check("tab ArrowRight", tabs.nth(1).get_attribute("aria-selected") == "true" and page.evaluate("document.activeElement.id") == "tab-findings")
        page.keyboard.press("End")
        check("tab End", tabs.nth(2).get_attribute("aria-selected") == "true" and page.evaluate("document.activeElement.id") == "tab-explore")
        page.keyboard.press("Home")
        check("tab Home", tabs.nth(0).get_attribute("aria-selected") == "true" and page.evaluate("document.activeElement.id") == "tab-overview")

        tabs.nth(1).click()
        reveal = page.locator(".reveal").first
        masked = page.locator("#ev-1").inner_text()
        reveal.click()
        shown = page.locator("#ev-1").inner_text()
        expanded = reveal.get_attribute("aria-expanded")
        reveal.click()
        hidden = page.locator("#ev-1").inner_text()
        check("sample reveal and hide", shown != masked and hidden == masked and expanded == "true")

        for width in (320, 390):
            page.set_viewport_size({"width": width, "height": 844})
            page.wait_for_timeout(80)
            overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            check(f"sample no horizontal overflow at {width}px", overflow <= 1, f"{overflow}px")

        if shots:
            page.screenshot(path=str(shots / "preliminary-sample-1440.png"), full_page=True)

        # 404 body and status are checked separately: page content here, status via the server.
        body = page.request.get(base + "/404.html")
        html = body.text()
        check("404 page content", body.status == 200 and "That report does not exist." in html and 'href="/"' in html, str(body.status))
        missing = page.request.get(base + "/missing-page-xyz")
        check("missing route returns 404", missing.status == 404, str(missing.status))
        if missing.status == 404 and "That report does not exist." not in missing.text():
            print("INFO  server 404 body is not the custom page (expected for python -m http.server; nginx probe asserts it)")

        ctx.close()
        browser.close()

    failed_checks = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed_checks)}/{len(results)} checks passed")
    return 1 if failed_checks else 0


if __name__ == "__main__":
    sys.exit(main())
