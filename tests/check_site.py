#!/usr/bin/env python3
"""Real-path contract for the landing page, not a snapshot of its CSS layout.

Run: python3 tests/check_site.py URL [screenshot-dir] [--allow-default-404]
The flag is only for the plain Python preview; default checks shipped headers.
Requires the already-installed Playwright and /usr/bin/chromium.
"""
import json
import os
import re
import struct
import sys
from pathlib import Path
from time import monotonic
from urllib.parse import parse_qs, urlparse
from xml.etree import ElementTree as ET

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright

PLAY = "https://play.google.com/store/apps/details?id=com.flutterguard.app"
SOURCE = "https://github.com/anasfik/FlutterGuard"
CANONICAL = "https://flutterguard.dev/"
GUIDES = {
    "/flutter-security/": "Flutter security: what a release APK exposes",
    "/flutter-apk-inspection/": "Flutter APK inspection: reading a release on Android",
    "/proguard-flutter/": "ProGuard for Flutter: what R8 and obfuscation hide",
    "/mobsf-alternative/": "MobSF alternative for auditing Flutter APKs",
}
PAGES = {
    "/flutter-security-checklist/": "Flutter app security audit checklist",
    "/flutter-release-corpus/": "What 26 released Flutter apps expose",
    "/changelog/": "FlutterGuard changelog",
    "/about/": "About FlutterGuard",
    "/contact/": "Contact FlutterGuard",
    "/privacy/": "Privacy and data handling",
    "/cli/": "FlutterGuard CLI: scan Flutter APKs in CI",
}


def wait_until(page, predicate, timeout=10):
    """Bounded browser-state polling without Playwright's CSP-sensitive eval."""
    deadline = monotonic() + timeout
    while monotonic() < deadline:
        if page.evaluate(predicate):
            return True
        page.wait_for_timeout(50)
    return False


def check_code_blocks(page, path, check):
    nav = page.locator('header a[href$="#get-started"]')
    check(f"{path} navigation names App & CLI", nav.count() == 1 and nav.inner_text() == "App & CLI")
    for i, block in enumerate(page.locator("pre").all()):
        language = block.get_attribute("data-language")
        check(f"{path} code block {i} is highlighted and labelled",
              language in ("shell", "kotlin") and bool(block.get_attribute("data-title"))
              and block.locator("code .syntax-token").count() > 0)
        check(f"{path} code block {i} has the right presentation",
              ("terminal" in (block.get_attribute("class") or "").split()) == (language == "shell")
              and block.evaluate("e => getComputedStyle(e).backgroundColor")
              == page.evaluate("() => getComputedStyle(document.querySelector('.skip-link')).backgroundColor"))


def main(args):
    preview = "--allow-default-404" in args
    args = [a for a in args if a != "--allow-default-404"]
    if not 1 <= len(args) <= 2 or any(a.startswith("--") for a in args):
        print(__doc__)
        return 2
    base = args[0].rstrip("/")
    shots = Path(args[1]) if len(args) == 2 else None
    if shots:
        shots.mkdir(parents=True, exist_ok=True)
    results = []

    def check(name, ok, detail=""):
        results.append(bool(ok))
        print(f"{'PASS' if ok else 'FAIL'} {name}" + (f": {detail}" if detail else ""))

    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get("CHROMIUM", "/usr/bin/chromium"))
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        context.add_init_script("""(() => {
            window.mediaPlayAttempts = [];
            const play = HTMLMediaElement.prototype.play;
            HTMLMediaElement.prototype.play = function (...args) {
                const r = this.getBoundingClientRect();
                window.mediaPlayAttempts.push({top:r.top, bottom:r.bottom});
                return play.apply(this, args);
            };
        })();""")
        page = context.new_page()
        errors, failed, foreign = [], [], []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(f"{m.text} @ {m.location['url']}") if m.type == "error" else None)
        page.on("requestfailed", lambda r: failed.append(r.url) if not (r.url.endswith(".mp4") and (r.failure or "") == "net::ERR_ABORTED") else None)
        allowed_origins = {urlparse(base).netloc, "static.cloudflareinsights.com", "cloudflareinsights.com", "us-assets.i.posthog.com", "us.i.posthog.com"}
        page.on("request", lambda r: foreign.append(r.url) if urlparse(r.url).netloc not in allowed_origins else None)
        response = page.goto(base, wait_until="load")
        page.evaluate("document.fonts.ready")
        check("homepage 200", response.status == 200)
        check_code_blocks(page, "/", check)
        check("one accurate H1", page.locator("h1").all_text_contents() == ["See what ships in your Flutter app."])
        get_cta = page.locator('.hero a.get-cta[href="#get-started"]')
        check("hero offers Android and terminal entry paths",
              get_cta.count() == 1 and page.locator('.hero-actions a[href="#cli"]').count() == 1)
        check("Android has Play and current GitHub install paths",
              page.locator(f'#get-started a.store-badge[href="{PLAY}"]').count() == 1
              and page.locator(f'#get-started a[href="{SOURCE}/releases/latest"]').count() == 1)
        check("source-built CLI and engine have clear destinations",
              page.locator('#cli a[href="/cli/"]').count() >= 1
              and page.locator(f'#engine a[href="{SOURCE}/tree/main/engine"]').count() == 1)
        check("no navbar install actions", page.locator(f'header a[href="{PLAY}"], header .navbar-cta, header .play-button').count() == 0)
        check("plain GitHub navbar link", page.locator(f'header a[href="{SOURCE}"]').count() == 1 and page.locator(f'header a[href="{SOURCE}"] img').count() == 0)
        check("graphical APK layers explain real files", page.locator(".apk-stack .layer").count() >= 3 and "libapp.so" in page.locator(".apk-stack").inner_text())
        check("capabilities cover the audit surface", page.locator(".capability-list > li").count() == 6)
        check("guides section links the cluster", page.locator('#guides a[href="/flutter-security/"], #guides a[href="/flutter-apk-inspection/"], #guides a[href="/proguard-flutter/"], #guides a[href="/mobsf-alternative/"], #guides a[href="/flutter-security-checklist/"], #guides a[href="/flutter-release-corpus/"]').count() == 6)
        main_text = page.locator("main").inner_text().lower()
        check("confidence distinguishes facts, leads and inventory",
              all(s in main_text for s in ("confirmed artifact facts", "leads worth checking", "inventory", "only confirmed")))
        check("comparison and source-build limits are visible",
              page.locator("#compare").count() == 1 and "same app" in main_text
              and "build from source" in main_text and "0.4.0" in main_text)
        check("existing recording is dated, not passed off as new UI",
              "recorded before 0.4.0" in main_text)
        check("explicit graphics pause control", page.locator('input#pause-motion[type="checkbox"]').count() == 1)
        check("email and issue recovery paths", page.locator('a[href="mailto:work@gwhyyy.com"]').count() >= 1 and page.locator(f'a[href="{SOURCE}/issues"]').count() >= 1)
        body = page.evaluate("() => {const b=document.body.cloneNode(true);b.querySelectorAll('script').forEach(e=>e.remove());return b.textContent.toLowerCase()}")
        check("no unsupported distribution or exploit promises",
              all(s not in body for s in ("100% accurate", "zero false positives", "decompile dart", "download the cli", "maven central")))
        check("external links are safely new-tab", page.evaluate("() => [...document.querySelectorAll('a[href^=\"https://\"]')].every(a=>a.target==='_blank' && a.relList.contains('noopener') && a.relList.contains('noreferrer'))"))
        check("local anchors resolve", page.evaluate("() => [...document.querySelectorAll('a[href^=\"#\"]')].every(a=>document.getElementById(a.hash.slice(1)))"))

        # Media: prove decoded frames and actual playback, not only attributes.
        video = page.locator("video")
        check("one genuine same-origin demo", video.count() == 1 and video.locator("source").count() == 1 and video.locator("source").get_attribute("src") == "/assets/app/demo.mp4")
        check("video has native controls, inline playback and a poster", all(video.get_attribute(a) is not None for a in ("controls", "muted", "playsinline", "loop")) and video.get_attribute("poster") == "/assets/app/demo-poster.webp")
        check("demo defers playback until scrolled into view", video.get_attribute("autoplay") is None and video.evaluate("v=>v.paused"))
        check("offscreen demo never attempts startup playback", page.evaluate("mediaPlayAttempts.length === 0"))
        video.scroll_into_view_if_needed()
        check("visible demo starts automatically", wait_until(page, "!document.querySelector('video').paused"))
        page.evaluate("scrollTo(0,0)")
        check("offscreen demo pauses", wait_until(page, "document.querySelector('video').paused"))
        attempts = page.evaluate("mediaPlayAttempts.length")
        page.locator("#pause-motion").evaluate("e => {e.checked=true;e.dispatchEvent(new Event('change'))}")
        page.locator("#pause-motion").evaluate("e => {e.checked=false;e.dispatchEvent(new Event('change'))}")
        check("unpausing offscreen does not attempt playback", page.evaluate("mediaPlayAttempts.length") == attempts)
        # A partial intersection must not satisfy the 40% playback threshold.
        page.evaluate("""() => {
            const v=document.querySelector('video'), r=v.getBoundingClientRect();
            scrollTo(0, scrollY+r.top-innerHeight+r.height*.2);
        }""")
        page.wait_for_function("() => Math.min(document.querySelector('video').getBoundingClientRect().bottom,innerHeight)-Math.max(document.querySelector('video').getBoundingClientRect().top,0) > 0")
        check("20% visible demo stays paused", wait_until(page, "document.querySelector('video').paused"))
        video.scroll_into_view_if_needed()
        page.emulate_media(reduced_motion="reduce")
        check("changing motion preference pauses a visible demo", wait_until(page, "document.querySelector('video').paused"))
        page.evaluate("scrollTo(0,0)")
        video.scroll_into_view_if_needed()
        check("reentering view respects current reduced motion", wait_until(page, "document.querySelector('video').paused"))
        page.emulate_media(reduced_motion="no-preference")
        page.evaluate("async () => {const v=document.querySelector('video'); v.muted=true; await v.play()}")
        first = video.evaluate("v=>v.currentTime")
        advances = wait_until(page, f"document.querySelector('video').currentTime > {first} + .7")
        check("video decodes and time advances", advances and video.evaluate("v=>v.videoWidth===540 && v.videoHeight===1200 && v.readyState>=2"))
        check("healthy video does not show the failure overlay", not page.locator(".video-fallback").is_visible())
        clip = page.request.get(base + "/assets/app/demo.mp4")
        check("optimized demo under 3.2 MB and correct MIME", clip.status == 200 and 0 < len(clip.body()) <= 3_200_000 and "video/mp4" in clip.headers.get("content-type", ""))

        # Responsive geometry includes all visible controls, not just page width.
        for width in (320, 360, 390, 768, 1024, 1280, 1440, 1920):
            page.set_viewport_size({"width": width, "height": 900})
            check(f"no page overflow {width}", page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"))
            fit = page.evaluate("""() => [...document.querySelectorAll('header a')].filter(e=>e.getClientRects().length).every(e=>{const r=e.getBoundingClientRect();return r.left>=-1 && r.right<=innerWidth+1 && r.width>=43.5 && r.height>=43.5})""")
            check(f"navbar controls whole and touchable {width}", fit)
        for width, height in ((1280, 720), (1440, 900)):
            page.set_viewport_size({"width": width, "height": height})
            page.evaluate("scrollTo(0,0)")
            check(f"hero workflow action in fold {width}", get_cta.count() == 1 and get_cta.evaluate("e=>e.getBoundingClientRect().bottom <= innerHeight"))
        page.set_viewport_size({"width": 390, "height": 844})
        page.evaluate("document.documentElement.style.fontSize='200%'")
        check("200% text reflows without clipping", page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1") and (get_cta.count() == 0 or get_cta.evaluate("e=>e.scrollWidth<=e.clientWidth+1")))
        page.evaluate("document.documentElement.style.fontSize=''")
        page.emulate_media(reduced_motion="reduce")
        # Isolate navigation from the browser's scroll anchoring after text resizing.
        page.goto(base, wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        for target in ("get-started", "cli", "engine", "why"):
            page.evaluate("(id) => {location.hash=''; location.hash=id}", target)
            check(f"mobile anchor clears sticky header {target}",
                  page.locator("#" + target).evaluate("e=>e.getBoundingClientRect().top >= document.querySelector('header').getBoundingClientRect().bottom"))
        page.evaluate("location.hash=''")
        page.emulate_media(reduced_motion="no-preference")

        # Native keyboard flow and pause behavior.
        page.locator(".skip-link").focus()
        page.keyboard.press("Enter")
        check("skip link enters main", page.evaluate("document.activeElement.tagName==='MAIN'"))
        summary = page.locator("#faq summary").first
        summary.focus()
        page.keyboard.press("Enter")
        check("FAQ keyboard opens", summary.evaluate("e=>e.parentElement.open"))
        page.keyboard.press("Space")
        check("FAQ keyboard closes", not summary.evaluate("e=>e.parentElement.open"))
        page.locator("#pause-motion").focus()
        page.keyboard.press("Space")
        check("pause control stops decorative animations", page.evaluate("() => document.querySelector('#pause-motion').checked && document.getAnimations().filter(a=>a.effect.target!==document.querySelector('video')).every(a=>a.playState==='paused' || a.playState==='finished')"))
        page.keyboard.press("Space")
        page.emulate_media(reduced_motion="reduce")
        media_paused = wait_until(page, "document.querySelector('video').paused")
        check("reduced motion stops graphics and autoplay", media_paused and page.evaluate("() => document.getAnimations().every(a=>a.playState!=='running' || a.effect.getTiming().duration<=1)"))
        page.emulate_media(forced_colors="active")
        focus_cta = get_cta if get_cta.count() else page.locator(".play-cta")
        focus_cta.focus()
        check("forced-colors CTA and focus remain defined", focus_cta.evaluate("e=>{const s=getComputedStyle(e);return parseFloat(s.outlineWidth)>=2 && parseFloat(s.borderTopWidth)>=1}"))
        page.emulate_media(forced_colors="none", reduced_motion="no-preference")

        # Head/schema retain the actual searchable page and truthful app facts.
        check("language and indexability", page.locator("html").get_attribute("lang") == "en" and "noindex" not in page.locator('meta[name="robots"]').get_attribute("content"))
        for selector, minimum, maximum in (("title", 1, 60), ('meta[name="description"]', 120, 160)):
            item = page.locator(selector)
            value = item.inner_text() if selector == "title" else item.get_attribute("content")
            check(f"single valid {selector}", item.count() == 1 and minimum <= len(value) <= maximum)
        check("single exact canonical", page.locator('link[rel="canonical"]').count() == 1 and page.locator('link[rel="canonical"]').get_attribute("href") == CANONICAL)
        check("social URLs absolute", page.evaluate("() => [...document.querySelectorAll('meta[property^=\"og:\"],meta[name=\"twitter:image\"]')].filter(e=> /url|image$|secure_url|video$/.test(e.getAttribute('property')||e.name)).every(e=>e.content.startsWith('https://flutterguard.dev/'))"))
        ld = [json.loads(t) for t in page.locator('script[type="application/ld+json"]').all_text_contents()]
        app = next((x for x in ld if x.get("@type") == "SoftwareApplication"), {})
        faq = next((x for x in ld if x.get("@type") == "FAQPage"), {})
        check("truthful SoftwareApplication schema", app.get("name") == "FlutterGuard" and str(app.get("offers", {}).get("price")) == "0" and app.get("license") == SOURCE + "/blob/main/LICENSE")
        pairs = page.locator("#faq details").evaluate_all("es=>es.map(e=>[e.querySelector('summary').textContent.trim(),e.querySelector('p').textContent.trim()])")
        schema_pairs = [[e.get("name"), e.get("acceptedAnswer", {}).get("text")] for e in faq.get("mainEntity", [])]
        check("all seven FAQ answers match schema verbatim", len(pairs) == 7 and pairs == schema_pairs)
        check("no invented rating/review/version schema", not re.search(r'"(?:aggregateRating|ratingValue|review|softwareVersion)"', json.dumps(ld)))
        png = page.request.get(base + "/og-image.png").body()
        check("OG is a real 1200x630 PNG", png[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", png[16:24]) == (1200, 630))
        for path, mime in (("/styles.css", "text/css"), ("/site.js", "javascript"), ("/assets/fonts/manrope-latin.woff2", "font/woff2"), ("/assets/app/demo-poster.webp", "image/webp")):
            r = page.request.get(base + path)
            check(f"asset {path}", r.status == 200 and mime in r.headers.get("content-type", ""))
        sitemap = ET.fromstring(page.request.get(base + "/sitemap.xml").text())
        locations = [e.text for e in sitemap.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        check("sitemap lists every page", locations == [CANONICAL] + [CANONICAL + g.lstrip("/") for g in list(GUIDES) + list(PAGES)])
        robots = page.request.get(base + "/robots.txt").text()
        check("robots keeps search and training policy", "Sitemap: " + CANONICAL + "sitemap.xml" in robots and "User-agent: GPTBot\nDisallow: /" in robots)
        indexnow = page.request.get(base + "/28d5bd8ab11b364e4a6e8e4ac44d2a11.txt")
        check("IndexNow key file served verbatim", indexnow.status == 200 and indexnow.text() == "28d5bd8ab11b364e4a6e8e4ac44d2a11")
        feed = ET.fromstring(page.request.get(base + "/feed.xml").text())
        atom = "{http://www.w3.org/2005/Atom}"
        entries = feed.findall(atom + "entry")
        check("Atom feed lists dated releases", feed.tag == atom + "feed" and len(entries) >= 5 and all(e.findtext(atom + "updated") for e in entries) and any("changelog" in (e.findtext(atom + "id") or "") for e in entries))
        catalog = page.request.get(base + "/.well-known/ai-catalog.json").json()
        pages = catalog.get("pages", [])
        check("AI catalog describes the site", catalog.get("name") == "FlutterGuard" and catalog.get("url") == CANONICAL and len(pages) >= 10 and all(p.get("url", "").startswith(CANONICAL) and p.get("markdown", "").startswith(CANONICAL) for p in pages) and catalog.get("resources", {}).get("llms") == CANONICAL + "llms.txt")
        for path in ("/llms.txt", "/llms-full.txt"):
            r = page.request.get(base + path)
            check(f"agent reference {path}", r.status == 200 and all(s in r.text() for s in ("FlutterGuard", "CLI", "engine", "/cli/")) and "/demo/" not in r.text())
        manifest = page.request.get(base + "/site.webmanifest").json()
        check("manifest and theme match", manifest.get("theme_color") == page.locator('meta[name="theme-color"]').get_attribute("content"))
        for icon in manifest.get("icons", []):
            check("manifest icon resolves", page.request.get(base + icon["src"]).status == 200)

        security = page.request.get(base + "/.well-known/security.txt")
        policy = next((l.split(":", 1)[1].strip() for l in security.text().splitlines() if l.lower().startswith("policy:")), "")
        frag = policy.split("#", 1)[1] if "#" in policy else ""
        check("security.txt policy points at a real section", security.status == 200 and bool(frag) and f'id="{frag}"' in page.content())

        beacon = page.locator('script[src="https://static.cloudflareinsights.com/beacon.min.js"]')
        check("analytics beacon wired", beacon.count() == 1 and "f9110d5432f446d6833224ec262cdd83" in (beacon.get_attribute("data-cf-beacon") or ""))

        for gpath, gtitle in GUIDES.items():
            gr = page.goto(base + gpath, wait_until="load")
            check_code_blocks(page, gpath, check)
            page.evaluate("document.fonts.ready")
            check(f"guide {gpath} 200", gr.status == 200)
            check(f"guide {gpath} title", page.title() == gtitle and len(gtitle) <= 60)
            desc = page.locator('meta[name="description"]')
            check(f"guide {gpath} description", desc.count() == 1 and 120 <= len(desc.get_attribute("content") or "") <= 160)
            canon = page.locator('link[rel="canonical"]')
            check(f"guide {gpath} canonical", canon.count() == 1 and canon.get_attribute("href") == CANONICAL + gpath.lstrip("/"))
            og_url = CANONICAL + f"og-{gpath.strip('/')}.png"
            og = page.locator('meta[property="og:image"]')
            tw = page.locator('meta[name="twitter:image"]')
            check(f"guide {gpath} own OG image", og.count() == 1 and og.get_attribute("content") == og_url and tw.count() == 1 and tw.get_attribute("content") == og_url)
            png = page.request.get(base + f"/og-{gpath.strip('/')}.png").body()
            check(f"guide {gpath} OG is a real 1200x630 PNG", png[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", png[16:24]) == (1200, 630))
            check(f"guide {gpath} one H1", page.locator("h1").all_text_contents() == [gtitle])
            ld = [json.loads(t) for t in page.locator('script[type="application/ld+json"]').all_text_contents()]
            types = {x.get("@type") for x in ld}
            check(f"guide {gpath} article and breadcrumb schema", {"TechArticle", "BreadcrumbList"} <= types)
            links = page.evaluate("() => [...document.querySelectorAll('main a[href]')].map(a=>a.getAttribute('href'))")
            check(f"guide {gpath} links into the cluster", all(p in links for p in GUIDES if p != gpath) and "/" in links)
            check(f"guide {gpath} external links are safely new-tab", page.evaluate("() => [...document.querySelectorAll('a[href^=\"https://\"]')].every(a=>a.target==='_blank' && a.relList.contains('noopener') && a.relList.contains('noreferrer'))"))
            for width in (320, 390, 768, 1280):
                page.set_viewport_size({"width": width, "height": 900})
                check(f"guide {gpath} no overflow {width}", page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"))
            page.set_viewport_size({"width": 1280, "height": 900})
            page.evaluate("scrollTo(0,0)")
            if shots:
                page.screenshot(path=str(shots / f"guide-{gpath.strip('/')}.png"), full_page=True)
        page.set_viewport_size({"width": 1440, "height": 900})
        page.goto(base, wait_until="load")

        # Agent delivery: the same URL negotiates Markdown, and every page has a substantive twin.
        check("Vary: Accept on HTML", "accept" in (response.headers.get("vary") or "").lower())
        for path in ["/"] + list(GUIDES) + list(PAGES):
            r = page.request.get(base + path, headers={"Accept": "text/markdown"})
            body = r.text()
            check(f"markdown negotiation {path}",
                  r.status == 200 and "text/markdown" in r.headers.get("content-type", "")
                  and len(body) > 400 and body.startswith("# ") and "https://flutterguard.dev" in body
                  and "accept" in (r.headers.get("vary") or "").lower())
        for path in ["/"] + list(GUIDES) + list(PAGES):
            r = page.request.get(base + path.rstrip("/") + "/index.md" if path != "/" else base + "/index.md")
            check(f"markdown twin {path}", r.status == 200 and "text/markdown" in r.headers.get("content-type", "") and len(r.text()) > 400)
        missing_md = page.request.get(base + "/missing-page-xyz", headers={"Accept": "text/markdown"})
        check("markdown 404 keeps status and links", missing_md.status == 404 and "text/markdown" in missing_md.headers.get("content-type", "") and "llms.txt" in missing_md.text())

        for ppath, ptitle in PAGES.items():
            pr = page.goto(base + ppath, wait_until="load")
            check_code_blocks(page, ppath, check)
            page.evaluate("document.fonts.ready")
            check(f"page {ppath} 200", pr.status == 200)
            check(f"page {ppath} title", page.title() == ptitle and len(ptitle) <= 60)
            desc = page.locator('meta[name="description"]')
            check(f"page {ppath} description", desc.count() == 1 and 120 <= len(desc.get_attribute("content") or "") <= 160)
            canon = page.locator('link[rel="canonical"]')
            check(f"page {ppath} canonical", canon.count() == 1 and canon.get_attribute("href") == CANONICAL + ppath.lstrip("/"))
            check(f"page {ppath} shared OG description matches the cover",
                  page.locator('meta[property="og:image:alt"]').count() == 1 and
                  page.locator('meta[property="og:image:alt"]').get_attribute("content") ==
                  "FlutterGuard: see what ships in your Flutter app. Android, CLI and shared engine.")
            check(f"page {ppath} one H1", page.locator("h1").all_text_contents() == [ptitle])
            check(f"page {ppath} body is substantive", len(page.locator("main").inner_text()) > 500)
            check(f"page {ppath} links home", page.locator('main a[href="/"]').count() >= 1 or page.locator('header a[href="/"]').count() == 1)
            check(f"page {ppath} external links are safely new-tab", page.evaluate("() => [...document.querySelectorAll('a[href^=\"https://\"]')].every(a=>a.target==='_blank' && a.relList.contains('noopener') && a.relList.contains('noreferrer'))"))
            for width in (320, 390, 768, 1280):
                page.set_viewport_size({"width": width, "height": 900})
                check(f"page {ppath} no overflow {width}", page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"))
            if ppath in ("/cli/", "/about/"):
                check(f"{ppath} distinguishes artifact facts from leads",
                      "artifact fact" in page.locator("main").inner_text().lower())
            if '"@type":"SoftwareApplication"' in page.content():
                check(f"page {ppath} schema names both platforms",
                      '"operatingSystem":"Android 8.0+; source-built CLI requires JDK 17+"' in page.content()
                      and '"operatingSystem":"Android 8.0+"' not in page.content())
            if ppath == "/cli/":
                cli_text = page.locator("main").inner_text()
                check("CLI guide exposes the real source-build contract",
                      all(s in cli_text for s in ("JDK 17", "./gradlew :cli:installDist",
                          "cli/build/install/flutterguard/bin/flutterguard", "--json", "--sarif", "--fail-on confirmed",
                          "Android SDK", "ANDROID_HOME")))
                check("CLI guide explains fresh outputs, gate semantics and limits",
                      all(s in cli_text for s in ("must not already exist", "parent",
                          "Scan completed; the gate was not requested",
                          "found at least one confirmed finding", "Invalid arguments",
                          "artifact", "exploit", "redact", "compare")))
                for width in (320, 390, 1280):
                    page.set_viewport_size({"width": width, "height": 900})
                    check(f"CLI guide no overflow {width}", page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"))
                    check(f"CLI command blocks fit {width}", page.evaluate(
                        "() => [...document.querySelectorAll('.article-body pre')].every(p => p.scrollWidth <= p.clientWidth + 1)"))
                check("CLI call-to-action focus ring overrides the dark panel",
                      ".article-cta :focus-visible{outline-color:var(--accent)}" in
                      page.request.get(base + "/styles.css").text())
        # A code block wide enough to scroll must also be reachable by keyboard
        # (axe-core scrollable-region-focusable, WCAG 2.1.1).
        for path in ["/"] + list(GUIDES) + list(PAGES):
            body = page.request.get(base + path).text()
            check(f"code blocks are keyboard-scrollable {path}", not re.search(r"<pre(?![^>]*\btabindex)", body))

        page.goto(base, wait_until="load")

        # Exercise the native click listener without opening the external store.
        play_link = page.locator(f'a[href="{PLAY}"]').first
        play_link.evaluate("e => e.addEventListener('click', event => event.preventDefault(), {once:true})")
        with page.expect_response(lambda r: urlparse(r.url).path == "/_c/play" and r.request.method == "POST") as click_response:
            play_link.click()
        check("real Play click sends the first-party counter",
              click_response.value.status == 204 and
              parse_qs(urlparse(click_response.value.url).query).get("p") == ["/"])

        for path in ("/demo", "/demo/", "/demo/index.html", "/missing-page-xyz"):
            r = page.request.get(base + path)
            check(f"removed/missing route {path}", r.status == 404 and (preview or "That page does not exist." in r.text()))
        not_found = page.request.get(base + "/404.html").text()
        check("404 noindex, no canonical and way home", 'content="noindex' in not_found and 'rel="canonical"' not in not_found and 'href="/"' in not_found)
        if not preview:
            csp = response.headers.get("content-security-policy", "")
            check("strict security headers present", all(x in csp for x in ("default-src 'self'", "script-src 'self' https://static.cloudflareinsights.com", "style-src 'self'", "connect-src 'self' https://cloudflareinsights.com", "frame-ancestors 'none'")) and response.headers.get("x-content-type-options") == "nosniff" and response.headers.get("x-frame-options") == "DENY")
            for path, age in (("/styles.css", "3600"), ("/assets/app/demo.mp4", "604800"), ("/assets/fonts/manrope-latin.woff2", "31536000")):
                check(f"strict cache {path}", "max-age=" + age in page.request.get(base + path).headers.get("cache-control", ""))
        if urlparse(base).hostname in {"127.0.0.1", "localhost"}:
            # Cloudflare's RUM CORS reply drops the preview port, so the beacon cannot post locally.
            errors = [e for e in errors if "cloudflareinsights.com" not in e]
            failed = [u for u in failed if "cloudflareinsights.com" not in u]
        check("no runtime errors or failed requests", not errors and not failed, str(errors + failed))
        check("runtime requests same-origin only", not foreign, str(foreign))
        if shots:
            page.locator("#pause-motion").check()
            for width, height in ((1440, 900), (1280, 720), (768, 1024), (390, 844), (320, 844)):
                page.set_viewport_size({"width": width, "height": height})
                page.evaluate("scrollTo(0,0);document.activeElement.blur()")
                page.screenshot(path=str(shots / f"home-{width}.png"), full_page=True)
        context.close()
        nojs = browser.new_context(java_script_enabled=False, viewport={"width": 390, "height": 844})
        np = nojs.new_page()
        np.goto(base, wait_until="load")
        check("no-JS content and both workflow paths", np.locator("h1").is_visible()
              and np.locator('.hero a[href="#get-started"]').count() == 1
              and np.locator('#cli a[href="/cli/"]').count() >= 1
              and np.locator(".store-badge").is_visible() and np.locator("#faq summary").first.is_visible()
              and np.locator("video").is_visible())
        nojs.close()
        broken = browser.new_context(viewport={"width": 390, "height": 844})
        broken.route("**/assets/app/demo.mp4", lambda r: r.fulfill(status=503, content_type="text/plain", body="Demo unavailable"))
        bp = broken.new_page()
        bp.goto(base, wait_until="load")
        try:
            bp.locator(".video-fallback").wait_for(state="visible", timeout=3000)
            recovery = bp.locator('.video-fallback a[href="/assets/app/demo.mp4"]').is_visible()
        except PlaywrightTimeoutError:
            recovery = False
        check("failed demo keeps a visible recording recovery link", recovery)
        broken.close()
        browser.close()
    print(f"\n{sum(results)}/{len(results)} checks passed")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
