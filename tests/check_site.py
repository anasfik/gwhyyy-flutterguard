#!/usr/bin/env python3
"""Real-path contract for the landing page, not a snapshot of its CSS layout.

Run: python3 tests/check_site.py URL [screenshot-dir] [--allow-default-404]
The flag is only for the plain Python preview; default checks shipped headers.
Requires the already-installed Playwright and /usr/bin/chromium.
"""
import json
import re
import struct
import sys
from pathlib import Path
from time import monotonic
from urllib.parse import urlparse
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


def wait_until(page, predicate, timeout=10):
    """Bounded browser-state polling without Playwright's CSP-sensitive eval."""
    deadline = monotonic() + timeout
    while monotonic() < deadline:
        if page.evaluate(predicate):
            return True
        page.wait_for_timeout(50)
    return False


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
        browser = pw.chromium.launch(executable_path="/usr/bin/chromium")
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        errors, failed, foreign = [], [], []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(f"{m.text} @ {m.location['url']}") if m.type == "error" else None)
        page.on("requestfailed", lambda r: failed.append(r.url))
        allowed_origins = {urlparse(base).netloc, "static.cloudflareinsights.com", "cloudflareinsights.com"}
        page.on("request", lambda r: foreign.append(r.url) if urlparse(r.url).netloc not in allowed_origins else None)
        response = page.goto(base, wait_until="load")
        page.evaluate("document.fonts.ready")
        check("homepage 200", response.status == 200)
        check("one accurate H1", page.locator("h1").all_text_contents() == ["Security audit any released Flutter app."])
        review_cta = page.locator(".hero .play-cta")
        apk_cta = page.locator(f'.hero a[href="{SOURCE}/releases/latest"]')
        check("hero states the Play listing is in review",
              review_cta.count() == 1 and review_cta.get_attribute("href") is None
              and "in review" in review_cta.inner_text().lower())
        check("hero has one working APK install action", apk_cta.count() == 1 and apk_cta.inner_text().strip().startswith("Download the APK"))
        check("no dead Play link anywhere", page.locator(f'a[href^="https://play.google.com/"]').count() == 0)
        check("no navbar install actions", page.locator(f'header a[href="{PLAY}"], header .navbar-cta, header .play-button').count() == 0)
        check("plain GitHub navbar link", page.locator(f'header a[href="{SOURCE}"]').count() == 1 and page.locator(f'header a[href="{SOURCE}"] img').count() == 0)
        check("graphical APK layers explain real files", page.locator(".apk-stack .layer").count() >= 3 and "libapp.so" in page.locator(".apk-stack").inner_text())
        check("capabilities cover the audit surface", page.locator(".capability-list > li").count() == 6)
        check("guides section links the cluster", page.locator('#guides a[href="/flutter-security/"], #guides a[href="/flutter-apk-inspection/"], #guides a[href="/proguard-flutter/"], #guides a[href="/mobsf-alternative/"]').count() == 4)
        check("workflow remains ordered, not a marquee", page.locator(".workflow-list > li h3").all_text_contents() == ["Discover", "Inspect", "Report"] and page.locator('[aria-hidden="true"] .workflow-list').count() == 0)
        check("explicit graphics pause control", page.locator('input#pause-motion[type="checkbox"]').count() == 1)
        check("email and issue recovery paths", page.locator('a[href="mailto:work@gwhyyy.com"]').count() >= 1 and page.locator(f'a[href="{SOURCE}/issues"]').count() >= 1)
        body = page.evaluate("() => {const b=document.body.cloneNode(true);b.querySelectorAll('script').forEach(e=>e.remove());return b.textContent.toLowerCase()}")
        check("removed labels stay removed even when hidden", all(s not in body for s in ("android 8", "android app", "before you install", "screen recording is coming later", "not affiliated", "navbar play button")))
        check("external links are safely new-tab", page.evaluate("() => [...document.querySelectorAll('a[href^=\"https://\"]')].every(a=>a.target==='_blank' && a.relList.contains('noopener') && a.relList.contains('noreferrer'))"))
        check("local anchors resolve", page.evaluate("() => [...document.querySelectorAll('a[href^=\"#\"]')].every(a=>document.getElementById(a.hash.slice(1)))"))

        # Media: prove decoded frames and actual playback, not only attributes.
        video = page.locator("video")
        check("one genuine same-origin demo", video.count() == 1 and video.locator("source").count() == 1 and video.locator("source").get_attribute("src") == "/assets/app/demo.mp4")
        check("video has native controls, inline playback and a poster", all(video.get_attribute(a) is not None for a in ("controls", "muted", "playsinline", "loop")) and video.get_attribute("poster") == "/assets/app/demo-poster.webp")
        page.evaluate("async () => {const v=document.querySelector('video'); v.muted=true; await v.play()}")
        first = video.evaluate("v=>v.currentTime")
        advances = wait_until(page, f"document.querySelector('video').currentTime > {first} + .7")
        check("video decodes and time advances", advances and video.evaluate("v=>v.videoWidth===540 && v.videoHeight===1200 && v.readyState>=2"))
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
            check(f"hero Play action in fold {width}", page.locator(".play-cta").evaluate("e=>e.getBoundingClientRect().bottom <= innerHeight"))
        page.set_viewport_size({"width": 390, "height": 844})
        page.evaluate("document.documentElement.style.fontSize='200%'")
        check("200% text reflows without clipping", page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1") and page.locator(".play-cta").evaluate("e=>e.scrollWidth<=e.clientWidth+1"))
        page.evaluate("document.documentElement.style.fontSize=''")

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
        page.locator(".hero .button").focus()
        check("forced-colors CTA and focus remain defined", page.locator(".hero .button").evaluate("e=>{const s=getComputedStyle(e);return parseFloat(s.outlineWidth)>=2 && parseFloat(s.borderTopWidth)>=1}"))
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
        check("all five FAQ answers match schema verbatim", len(pairs) == 5 and pairs == schema_pairs)
        check("no invented rating/review/version schema", not re.search(r'"(?:aggregateRating|ratingValue|review|softwareVersion)"', json.dumps(ld)))
        png = page.request.get(base + "/og-image.png").body()
        check("OG is a real 1200x630 PNG", png[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", png[16:24]) == (1200, 630))
        for path, mime in (("/styles.css", "text/css"), ("/site.js", "javascript"), ("/assets/fonts/manrope-latin.woff2", "font/woff2"), ("/assets/app/demo-poster.webp", "image/webp")):
            r = page.request.get(base + path)
            check(f"asset {path}", r.status == 200 and mime in r.headers.get("content-type", ""))
        sitemap = ET.fromstring(page.request.get(base + "/sitemap.xml").text())
        locations = [e.text for e in sitemap.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        check("sitemap lists the homepage and every guide", locations == [CANONICAL] + [CANONICAL + g.lstrip("/") for g in GUIDES])
        robots = page.request.get(base + "/robots.txt").text()
        check("robots keeps search and training policy", "Sitemap: " + CANONICAL + "sitemap.xml" in robots and "User-agent: GPTBot\nDisallow: /" in robots)
        indexnow = page.request.get(base + "/28d5bd8ab11b364e4a6e8e4ac44d2a11.txt")
        check("IndexNow key file served verbatim", indexnow.status == 200 and indexnow.text() == "28d5bd8ab11b364e4a6e8e4ac44d2a11")
        for path in ("/llms.txt", "/llms-full.txt"):
            r = page.request.get(base + path)
            check(f"agent reference {path}", r.status == 200 and "FlutterGuard" in r.text() and "Discover" in r.text() and "/demo/" not in r.text())
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
            for width in (390, 1280):
                page.set_viewport_size({"width": width, "height": 900})
                check(f"guide {gpath} no overflow {width}", page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"))
            page.set_viewport_size({"width": 1280, "height": 900})
            page.evaluate("scrollTo(0,0)")
            if shots:
                page.screenshot(path=str(shots / f"guide-{gpath.strip('/')}.png"), full_page=True)
        page.set_viewport_size({"width": 1440, "height": 900})
        page.goto(base, wait_until="load")

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
        check("no-JS real content and install path", np.locator("h1").is_visible() and np.locator(".play-cta").is_visible() and np.locator(f'.hero a[href="{SOURCE}/releases/latest"]').is_visible() and np.locator("#faq summary").first.is_visible() and np.locator("video").is_visible())
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
