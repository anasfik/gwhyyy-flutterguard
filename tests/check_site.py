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

import json
import re
import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

CHROMIUM = "/usr/bin/chromium"
WORD_LIMIT = 300
OVERFLOW_WIDTHS = (320, 360, 390, 768, 1024, 1280, 1440, 1920)
CANONICAL = "https://flutterguard.dev/"
SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
BANNED_LD_KEYS = ("aggregateRating", "review", "ratingValue", "softwareVersion")
DOWNLOAD = "https://github.com/anasfik/FlutterGuard/releases/latest"
SOURCE = "https://github.com/anasfik/FlutterGuard"
EMAIL = "mailto:work@gwhyyy.com"
PRIVACY = "https://gwhyyy.com/privacy/flutterguard"
LICENSE = "https://github.com/anasfik/FlutterGuard/blob/main/LICENSE"
NEW_TAB_NOTE = "(opens in a new tab)"

STEPS = [
    ("Discover", "FlutterGuard lists the Flutter apps installed on this device, or you pick a single APK."),
    ("Inspect", "Read the SDK versions, endpoints and exposed strings inside the release."),
    ("Report", "Save the evidence on the phone and come back to it whenever you need it."),
]
WHY_COPY = (
    "Generic scanners stop at permissions and package names. A Flutter app keeps its real "
    "surface inside libapp.so and the asset bundle. FlutterGuard reads that layer: SDK "
    "versions, embedded endpoints, exposed strings, AI providers, signing and network "
    "policy. It runs on the phone with no INTERNET permission, and the source is MIT."
)
FAQ_ITEMS = [
    ("Is FlutterGuard free?",
     "Yes. It is open source under the MIT licence, with no account, no ads and no paid tier."),
    ("Does it need an internet connection?",
     "No. The app has no INTERNET permission, so scans run entirely on the device."),
    ("Which apps can it check?",
     "Flutter apps you own or are authorised to test, either installed on the device or supplied as a single APK."),
    ("Does a finding prove the app is exploitable?",
     "No. Findings are static evidence from the release, not a confirmed exploit."),
    ("Where do updates come from?",
     "GitHub releases. There is no Play listing to install from yet."),
]
FLUTTER_MARK_PATH = (
    "M14.314 0 2.3 12 6 15.7 21.684.013h-7.357zm.014 11.072-6.471 6.458 "
    "6.47 6.47H21.7l-6.46-6.468 6.46-6.46h-7.37z"
)


def norm(text: str) -> str:
    return " ".join((text or "").split())


def strip_note(text: str) -> str:
    return (text or "").replace(NEW_TAB_NOTE, "").strip()


def png_size(data: bytes) -> tuple[int, int] | None:
    """Read width/height straight out of the PNG IHDR chunk (no dependency)."""
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", data[16:24])


def ld_keys(node, out=None):
    """Collect every object key in a parsed JSON-LD tree."""
    out = [] if out is None else out
    if isinstance(node, dict):
        for key, value in node.items():
            out.append(key)
            ld_keys(value, out)
    elif isinstance(node, list):
        for value in node:
            ld_keys(value, out)
    return out

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

        # Head metadata: one of each, canonical exactly the production root, the
        # LLM pointer right after it, and lengths search engines will not truncate.
        head = page.evaluate("""() => {
            const contents = (sel) => [...document.querySelectorAll(sel)].map(e => e.getAttribute('content') || '');
            return {lang: document.documentElement.getAttribute('lang'),
                    titles: document.querySelectorAll('title').length,
                    description: contents('meta[name="description"]'),
                    canonical: [...document.querySelectorAll('link[rel="canonical"]')].map(e => e.getAttribute('href') || ''),
                    robots: contents('meta[name="robots"]'),
                    llms: [...document.querySelectorAll('link[rel="alternate"]')].map(e => ({
                        href: e.getAttribute('href') || '', type: e.getAttribute('type') || '',
                        title: e.getAttribute('title') || ''})),
                    llmsAfterCanonical: (() => {
                        const c = document.querySelector('link[rel="canonical"]');
                        const a = document.querySelector('link[rel="alternate"][href="/llms.txt"]');
                        if (!c || !a) return false;
                        return !!((c.compareDocumentPosition(a) & Node.DOCUMENT_POSITION_FOLLOWING));
                    })()};
        }""")
        check("head carries exactly one title, description, canonical and robots meta",
              head["titles"] == 1 and len(head["description"]) == 1
              and len(head["canonical"]) == 1 and len(head["robots"]) == 1
              and head["lang"] == "en", str(head))
        check("canonical is exactly the production root",
              head["canonical"] == [CANONICAL], str(head["canonical"]))
        check("title fits in 60 characters", 0 < len(titles["title"]) <= 60, f"{len(titles['title'])} chars: {titles['title']}")
        check("description is 120-160 characters",
              len(head["description"]) == 1 and 120 <= len(head["description"][0]) <= 160,
              f"{len(head['description'][0]) if head['description'] else 0} chars: {head['description']}")
        check("description states the audit subject plainly",
              bool(head["description"]) and "flutter" in head["description"][0].lower()
              and "audit" in head["description"][0].lower()
              and not re.search(r"\b(best|AI)\b", head["description"][0]), str(head["description"]))
        check("llms.txt is linked as an alternate right after the canonical",
              any(l["href"] == "/llms.txt" and l["type"] == "text/plain" and l["title"] for l in head["llms"])
              and head["llmsAfterCanonical"], str(head["llms"]))

        # Open Graph and Twitter: every URL absolute on the production origin,
        # the committed clip declared, and the image dimensions stated correctly.
        social = page.evaluate("""() => {
            const out = {};
            for (const m of document.querySelectorAll('meta[property^="og:"], meta[name^="twitter:"]')) {
                const key = m.getAttribute('property') || m.getAttribute('name');
                out[key] = m.getAttribute('content') || '';
            }
            return out;
        }""")
        social_urls = {k: v for k, v in social.items() if v.startswith(("http:", "https:"))}
        check("every og/twitter URL is absolute https on flutterguard.dev",
              len(social_urls) >= 3 and all(
                  v.startswith("https://") and urlparse(v).netloc == "flutterguard.dev"
                  for v in social_urls.values()), str(social_urls))
        check("og:url is the canonical",
              social.get("og:url") == CANONICAL, social.get("og:url"))
        check("og and twitter images are the absolute og-image.png",
              social.get("og:image") == CANONICAL + "og-image.png"
              and social.get("twitter:image") == CANONICAL + "og-image.png", str(social.get("og:image")))
        check("og:image declares the real 1200x630 frame",
              social.get("og:image:width") == "1200" and social.get("og:image:height") == "630"
              and social.get("og:image:type") == "image/png", str(social.get("og:image:width")))
        og_png = page.request.get(base + "/og-image.png")
        og_dims = png_size(og_png.body())
        check("served og-image.png is a real 1200x630 PNG",
              og_png.status == 200 and og_dims == (1200, 630), f"{og_png.status} {og_dims}")
        video_url = CANONICAL + "assets/app/demo.mp4"
        check("og:video declares the committed demo clip and its real size",
              social.get("og:video") == video_url and social.get("og:video:secure_url") == video_url
              and social.get("og:video:type") == "video/mp4"
              and social.get("og:video:width") == "540" and social.get("og:video:height") == "1200",
              str({k: social.get(k) for k in ("og:video", "og:video:secure_url", "og:video:type",
                                              "og:video:width", "og:video:height")}))
        og_video = page.request.get(base + "/assets/app/demo.mp4")
        check("og:video URL is served as video/mp4",
              og_video.status == 200
              and (og_video.headers.get("content-type") or "").startswith("video/mp4"),
              f"{og_video.status} {og_video.headers.get('content-type')}")
        hero_text = page.locator(".hero-copy").inner_text().lower()
        check("no visible Android 8+ copy in the hero", "android 8" not in hero_text, hero_text)
        # The old #pros sentence is gone with that section; the on-device claim
        # now lives in the "Report" step, and the absolute no-export promise
        # must still never appear anywhere.
        features_text = page.locator("#features").inner_text().lower()
        check("on-device privacy claim survives without an absolute guarantee",
              "save the evidence on the phone" in features_text
              and "cannot leave the device" not in hero_text + page.locator("body").inner_text().lower(), features_text[:200])

        page.evaluate("document.fonts.ready")
        check("Manrope self-hosted and loaded", page.evaluate("[...document.fonts].some(f => f.family.replace(/[\"\']/g, '') === 'Manrope' && f.status === 'loaded')"))
        check("font request served locally", any("/assets/fonts/manrope-latin.woff2" in u for u in requests))

        # Navbar: brand lockup left, four in-page anchors centred, actions right.
        check("navbar brand links home", page.locator('header a[href="/"]').count() >= 1)
        check("navbar brand mark loads", page.eval_on_selector("header .brand-mark", "e => e.complete && e.naturalWidth > 0"))
        nav_hrefs = page.eval_on_selector_all("header .site-nav > a", "els => els.map(e => e.getAttribute('href'))")
        check("navbar carries the four section anchors in order",
              nav_hrefs == ["#features", "#why", "#faq", "#contact"], str(nav_hrefs))
        check("no hamburger control", page.locator('header button, header [aria-expanded]').count() == 0)
        sticky = page.evaluate("""() => {
            const h = document.querySelector('header.site-header');
            const s = getComputedStyle(h);
            const sections = [...document.querySelectorAll('main[id], section[id]')].map(el => ({
                id: el.id, margin: parseFloat(getComputedStyle(el).scrollMarginBlockStart) || 0}));
            return {position: s.position, top: s.top, headerH: Math.round(h.getBoundingClientRect().height * 10) / 10,
                    sections};
        }""")
        check("header is sticky at the top of the viewport",
              sticky["position"] == "sticky" and sticky["top"] in ("0px", "0"), str(sticky))
        check("sticky header stays within 72px", sticky["headerH"] <= 72, str(sticky["headerH"]))
        check("every section id clears the sticky header when anchored",
              len(sticky["sections"]) >= 5
              and all(s["margin"] >= sticky["headerH"] - 1 for s in sticky["sections"]), str(sticky["sections"]))

        # Split hero with copy and one real, self-hosted demo clip inside a phone frame.
        check("split hero present", page.locator(".hero .hero-copy").count() == 1 and page.locator(".hero .hero-device").count() == 1)
        try:
            page.wait_for_function(
                "() => { const v = document.querySelector('.hero .hero-device video'); return !!v && v.readyState >= 1; }",
                timeout=15000,
            )
        except Exception:
            info("hero video metadata never loaded (absent or undecodable); the video contract checks report it")
        video = page.evaluate("""() => {
            const all = [...document.querySelectorAll('video')];
            const v = document.querySelector('.hero .hero-device video');
            if (!v) return {count: all.length, hero: false, srcs: all.map(e => e.getAttribute('src') || '')};
            const r = v.getBoundingClientRect();
            return {count: all.length, hero: true, autoplay: v.autoplay, muted: v.muted, loop: v.loop,
                    playsinline: v.hasAttribute('playsinline'), controls: v.controls,
                    poster: v.getAttribute('poster'), src: v.getAttribute('src'),
                    srcs: [...v.querySelectorAll('source')].map(s => s.getAttribute('src')),
                    label: v.getAttribute('aria-label') || '',
                    w: v.videoWidth, h: v.videoHeight, dur: Math.round(v.duration || 0),
                    renderedW: Math.round(r.width), renderedH: Math.round(r.height),
                    inFrame: !!v.closest('.device-frame'),
                    fallback: (v.textContent || '').replace(/\\s+/g, ' ').trim(),
                    links: [...v.querySelectorAll('a[href]')].map(a => a.getAttribute('href'))};
        }""")
        check("hero holds exactly one video", bool(video) and video["hero"] and video["count"] == 1, str(video))
        check("hero video autoplays muted on loop, inline, with native controls",
              bool(video) and video.get("autoplay") is True and video.get("muted") is True
              and video.get("loop") is True and video.get("playsinline") is True
              and video.get("controls") is True, str(video))
        check("hero video ships one same-origin mp4 source and a poster",
              bool(video) and video.get("srcs") == ["/assets/app/demo.mp4"] and not video.get("src")
              and video.get("poster") == "/assets/app/demo-poster.webp", str(video))
        check("hero video is 540x1200 and the full 81s clip",
              bool(video) and video.get("w") == 540 and video.get("h") == 1200 and video.get("dur") == 81, str(video))
        check("hero video keeps the phone aspect ratio",
              bool(video) and video.get("renderedH")
              and abs((video["renderedW"] / video["renderedH"]) - (540 / 1200)) < 0.02, str(video))
        check("hero video has an accessible label", bool(video) and len(video.get("label") or "") > 30, str(video))
        check("hero video carries an in-element fallback and a link to the clip",
              bool(video) and len(video.get("fallback") or "") > 10
              and video.get("links") == ["/assets/app/demo.mp4"], str(video))
        check("video sits in a phone frame", page.locator(".device-frame .device-video").count() == 1)
        check("no second video or fake player chrome",
              page.locator("video").count() == 1
              and page.locator(".player, [class*='play-button'], [class*='play-icon'], button[aria-label*='play' i]").count() == 0)
        media_urls = (video.get("srcs") or []) + (video.get("links") or [])
        check("no iframe and every media URL is same-origin",
              page.locator("iframe").count() == 0 and bool(media_urls)
              and all(u.startswith("/") and urlparse(u).netloc in ("", host) for u in media_urls), str(media_urls))
        check("no device caption element", page.locator(".device-caption, .hero-device figcaption").count() == 0
              and "screen recording is coming later" not in page.locator("body").inner_text().lower())

        # Playback proof: the clip decodes and media time advances in a real browser.
        playback = page.evaluate("""async () => {
            const v = document.querySelector('.hero .hero-device video');
            if (!v) return {missing: true};
            v.muted = true;
            try { await v.play(); } catch (e) { /* autoplay refusal is the poster+controls fallback */ }
            if (v.readyState < 2) await new Promise(r => {
                v.addEventListener('loadeddata', r, {once: true});
                setTimeout(r, 8000);
            });
            const t1 = v.currentTime;
            await new Promise(r => setTimeout(r, 2000));
            return {readyState: v.readyState, t1, t2: v.currentTime,
                    error: v.error && v.error.code, w: v.videoWidth, h: v.videoHeight};
        }""")
        check("hero video decodes past metadata (readyState >= 2)",
              bool(playback) and not playback.get("missing") and playback.get("readyState", 0) >= 2, str(playback))
        check("hero video playback advances in real time",
              bool(playback) and not playback.get("missing")
              and playback.get("t2", 0) - playback.get("t1", 0) >= 1.0, str(playback))

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

        # Install cluster: one working APK action, no Play badge or availability note.
        hrefs = page.eval_on_selector_all("a[href]", "els => els.map(e => ({href: e.getAttribute('href'), text: e.textContent.trim(), cls: e.className, target: e.getAttribute('target'), rel: e.getAttribute('rel')}))")
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
        check("Play badge, slot and availability note are gone from the markup",
              page.locator(".play-slot, .play-badge, .store-note, img[src*='google-play-badge']").count() == 0)
        early_dom = page.evaluate("""() => {
            const clone = document.body.cloneNode(true);
            clone.querySelectorAll('script, style, template, noscript').forEach(n => n.remove());
            return clone.textContent.replace(/\\s+/g, ' ').toLowerCase();
        }""")
        check("no unavailable Play copy anywhere in the DOM, hidden nodes included",
              "not yet available on google play" not in early_dom)
        check("no link points at the dead Play listing",
              not any("play.google.com" in (a["href"] or "") for a in hrefs))
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
            const els = [...document.querySelectorAll('.install-actions a, header a, footer a')];
            return els.every(e => { const r = e.getBoundingClientRect(); return r.height >= 43.5 || r.width >= 43.5; });
        }"""))

        # One clean primary row: no badge, no reserved slot, no stretched CTA.
        row = page.evaluate("""() => {
            const dEl = document.querySelector('.download-button');
            const aEl = document.querySelector('.install-actions');
            const cEl = document.querySelector('.hero-copy');
            if (!dEl || !aEl) return null;
            const d = dEl.getBoundingClientRect();
            const a = aEl.getBoundingClientRect();
            return {downloadH: Math.round(d.height * 10) / 10, downloadW: Math.round(d.width * 10) / 10,
                    actionsW: Math.round(a.width * 10) / 10, actionsH: Math.round(a.height * 10) / 10,
                    containerW: cEl ? Math.round(cEl.getBoundingClientRect().width) : 0,
                    childCount: aEl.querySelectorAll(':scope > *').length,
                    gap: getComputedStyle(aEl).columnGap,
                    leftGap: Math.round((d.left - a.left) * 10) / 10,
                    align: getComputedStyle(aEl).alignItems};
        }""")
        check("hero install row is one natural-width 48px action with no badge gap",
              bool(row) and row["downloadH"] >= 43.5 and abs(row["downloadH"] - 48) <= 0.6
              and row["childCount"] == 1 and row["gap"] in ("normal", "0px")
              and row["downloadW"] < row["containerW"] * 0.9, str(row))
        check("hero action row does not stretch the primary button",
              bool(row) and row["align"] == "flex-start" and row["leftGap"] <= 1
              and row["actionsH"] - row["downloadH"] <= 1, str(row))

        # Every external destination opens a new tab; in-page and mail links do not.
        external_links = [a for a in hrefs if (a["href"] or "").startswith(("http:", "https:"))]
        internal_links = [a for a in hrefs if (a["href"] or "").startswith(("#", "mailto:"))]
        check("every external link opens a new tab with noopener noreferrer",
              len(external_links) >= 7 and all(
                  a["target"] == "_blank"
                  and "noopener" in (a["rel"] or "").split()
                  and "noreferrer" in (a["rel"] or "").split()
                  for a in external_links),
              str([a for a in external_links if a["target"] != "_blank"
                   or "noopener" not in (a["rel"] or "").split()
                   or "noreferrer" not in (a["rel"] or "").split()]))
        check("anchor and mail links keep the current tab",
              bool(internal_links) and all(a["target"] is None for a in internal_links), str(internal_links))
        button_like = ("download-button", "navbar-cta", "github-button")
        text_links = [a for a in external_links if not any(c in (a["cls"] or "") for c in button_like)]
        check("external text links announce the new tab",
              len(text_links) >= 4 and all(NEW_TAB_NOTE in a["text"] for a in text_links),
              str([a["text"] for a in text_links]))
        check("button and icon links do not duplicate the new-tab suffix",
              all(NEW_TAB_NOTE not in a["text"] for a in external_links
                  if any(c in (a["cls"] or "") for c in button_like)))

        # "Why" section: one wide paragraph with the inline Flutter mark.
        check("why section sits between the hero and the features",
              page.evaluate("""() => {
                  const order = [...document.querySelectorAll('main > section')].map(s => s.id || 'hero');
                  return order.indexOf('why') === 1 && order.indexOf('features') === 2;
              }"""))
        why = page.evaluate("""() => {
            const s = document.querySelector('#why');
            if (!s) return null;
            const h2 = [...s.querySelectorAll('h2')];
            const p = s.querySelector('p');
            const marks = [...s.querySelectorAll('svg.flutter-mark')];
            const mark = marks[0];
            return {h2s: h2.map(h => h.textContent.trim()),
                    paras: s.querySelectorAll('p').length,
                    text: p ? p.textContent : '',
                    marks: marks.length,
                    viewBox: mark ? mark.getAttribute('viewBox') : null,
                    width: mark ? mark.getAttribute('width') : null,
                    height: mark ? mark.getAttribute('height') : null,
                    hidden: mark ? mark.getAttribute('aria-hidden') : null,
                    focusable: mark ? mark.getAttribute('focusable') : null,
                    path: mark && mark.querySelector('path') ? mark.querySelector('path').getAttribute('d') : null,
                    fill: mark && mark.querySelector('path') ? mark.querySelector('path').getAttribute('fill') : null,
                    inParagraph: !!mark && !!mark.closest('p'),
                    imgs: s.querySelectorAll('img').length};
        }""")
        check("why section has exactly one verbatim heading",
              bool(why) and why["h2s"] == ["Why this is not another APK scanner"], str(why))
        check("why section carries the copy verbatim with the Flutter mark inline",
              bool(why) and norm(why["text"]) == WHY_COPY, norm(why["text"]) if why else "missing")
        check("why mark is the exact inline Flutter glyph, not an image",
              bool(why) and why["marks"] == 1 and why["imgs"] == 0 and why["inParagraph"]
              and why["viewBox"] == "0 0 24 24" and why["width"] == "20" and why["height"] == "20"
              and why["hidden"] == "true" and why["focusable"] == "false"
              and why["path"] == FLUTTER_MARK_PATH and why["fill"] == "#54C5F8", str(why))

        # Content regions and copy.
        check("features section", page.locator("#features").count() == 1)
        check("features heading unchanged", page.locator("#features h2").inner_text().strip() == "What it does")
        nodes = STEPS
        chain = page.evaluate("""() => {
            const tracks = [...document.querySelectorAll('#features .chain__track')];
            const real = tracks.find(t => t.getAttribute('aria-hidden') !== 'true') || tracks[0];
            const dup = tracks.find(t => t.getAttribute('aria-hidden') === 'true');
            const read = (ul) => [...ul.querySelectorAll(':scope > li')].map(li => [
                (li.querySelector('h3')?.textContent || '').trim(),
                (li.querySelector('p')?.textContent || '').trim()]);
            const icons = real ? [...real.querySelectorAll(':scope > li')].map(li => {
                const svgs = [...li.querySelectorAll('svg')];
                const svg = svgs[0];
                const s = svg ? getComputedStyle(svg) : null;
                return {count: svgs.length,
                        hidden: svg ? svg.getAttribute('aria-hidden') : null,
                        focusable: svg ? svg.getAttribute('focusable') : null,
                        w: svg ? svg.getAttribute('width') : null,
                        h: svg ? svg.getAttribute('height') : null,
                        stroke: svg ? svg.getAttribute('stroke') : null,
                        fill: svg ? svg.getAttribute('fill') : null,
                        sw: svg ? svg.getAttribute('stroke-width') : null,
                        aboveHeading: !!svg && !!li.querySelector('h3')
                            && (svg.compareDocumentPosition(li.querySelector('h3')) & Node.DOCUMENT_POSITION_FOLLOWING) !== 0,
                        color: s ? s.color : null,
                        px: s ? Math.round(parseFloat(s.width) * 10) / 10 : null};
            }) : [];
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
                    dupUserSelect: dupStyle ? dupStyle.userSelect : '',
                    icons};
        }""")
        check("three named steps in one connected track with the new copy",
              chain["real"] == [[t, b] for t, b in nodes], str(chain["real"]))
        check("duplicate loop track is hidden from AT and inert",
              chain["tracks"] == 2 and chain["dup"] == chain["real"] and chain["dupFocusable"] == 0, str(chain))
        check("each step carries one decorative 20px stroked icon above its heading",
              len(chain["icons"]) == 3 and all(
                  i["count"] == 1 and i["hidden"] == "true" and i["focusable"] == "false"
                  and i["w"] == "20" and i["h"] == "20" and i["stroke"] == "currentColor"
                  and i["fill"] == "none" and i["sw"] == "1.5" and i["aboveHeading"]
                  and i["px"] == 20 and i["color"] == "rgb(82, 97, 89)"
                  for i in chain["icons"]), str(chain["icons"]))
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
              sorted(strip_note(l["text"]) for l in contact["links"]) == sorted(["Email work@gwhyyy.com", "Open a GitHub issue"])
              and all(l["h"] >= 43.5 for l in contact["links"]), str(contact["links"]))
        check("contact copy stays short", contact["words"] <= 40, f"{contact['words']} words")
        check("visible email link", any(strip_note(a["text"]) == "work@gwhyyy.com" for a in find(EMAIL))
              or any(strip_note(a["text"]) == "Email work@gwhyyy.com" for a in find(EMAIL)), str(find(EMAIL)))
        check("privacy link exact", bool(find(PRIVACY)))
        check("MIT license link exact", bool(find(LICENSE)))
        check("issues link exact", bool(find(SOURCE + "/issues")))
        check("footer maintainer and links", "FlutterGuard by Anas Fikhi" in page.locator("footer").inner_text() and page.locator(".footer-links a").count() == 2)
        check("at most five major content regions", page.evaluate("document.querySelectorAll('main > section, main > .hero').length") <= 5)

        # Demo route is fully removed from links, content and sitemap/llms metadata.
        # The shipped clip lives at /assets/app/demo.mp4, so only a /demo route is banned.
        check("no demo/sample links", not any(urlparse(a["href"] or "").path.startswith("/demo") for a in hrefs))
        body_text = page.locator("body").inner_text().lower()
        # textContent of a detached body clone still includes collapsed <details>
        # content, so removed disclosures cannot hide behind a summary.
        dom_text = page.evaluate("""() => {
            const clone = document.body.cloneNode(true);
            clone.querySelectorAll('script, style, template, noscript').forEach(n => n.remove());
            return clone.textContent.replace(/\\s+/g, ' ').toLowerCase();
        }""")
        check("no sample CTA copy", "see sample" not in body_text and "demo" not in body_text)
        check("the only disclosures are the five FAQ items",
              page.evaluate("""() => {
                  const all = [...document.querySelectorAll('details')];
                  return all.length === 5 && all.every(d => d.closest('#faq'));
              }"""))
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
            "not yet available on google play",
        )
        check("removed copy absent from body DOM text", all(s not in dom_text for s in removed),
              str([s for s in removed if s in dom_text]))
        check("removed copy absent from visible text", all(s not in body_text for s in removed),
              str([s for s in removed if s in body_text]))
        check("no visible Android 8+ copy", "android 8" not in body_text, body_text[:200])
        check("no absolute no-export privacy claim", "cannot leave the device" not in body_text)

        # FAQ: native details/summary, five exact answers, no script.
        check("faq section sits between the features and contact",
              page.evaluate("""() => {
                  const order = [...document.querySelectorAll('main > section')].map(s => s.id || 'hero');
                  return order.indexOf('features') < order.indexOf('faq')
                      && order.indexOf('faq') < order.indexOf('contact');
              }"""))
        faq = page.evaluate("""() => {
            const s = document.querySelector('#faq');
            if (!s) return null;
            const details = [...s.querySelectorAll('details')];
            return {h2: (s.querySelector('h2')?.textContent || '').trim(),
                    count: details.length,
                    items: details.map(d => [
                        (d.querySelector('summary')?.textContent || '').trim(),
                        (d.querySelector('p')?.textContent || '').trim()]),
                    nonEmpty: details.every(d => (d.querySelector('p')?.textContent || '').trim().length > 10),
                    roleButtons: s.querySelectorAll('[role="button"]').length,
                    scripts: s.querySelectorAll('script').length};
        }""")
        check("faq heading and exactly five native disclosures",
              bool(faq) and faq["h2"] == "Frequent questions" and faq["count"] == 5
              and faq["nonEmpty"] and faq["scripts"] == 0, str(faq))
        check("faq questions and answers are verbatim",
              bool(faq) and faq["items"] == [[q, a] for q, a in FAQ_ITEMS], str(faq["items"] if faq else None))
        check("faq uses no div[role=button]",
              bool(faq) and faq["roleButtons"] == 0, str(faq))
        first = page.locator("#faq details").first
        second = page.locator("#faq details").nth(1)
        if page.locator("#faq details").count() == 5:
            first.locator("summary").click()
            page.wait_for_timeout(80)
            second.locator("summary").click()
            page.wait_for_timeout(80)
        opened = page.evaluate("""() => {
            const d = [...document.querySelectorAll('#faq details')];
            return {open: d.map(x => x.open),
                    visible: d.slice(0, 2).map(x => {
                        const p = x.querySelector('p');
                        if (!p) return false;
                        const r = p.getBoundingClientRect();
                        return r.height > 0 && getComputedStyle(p).visibility !== 'hidden';
                    }),
                    marker: d.length ? getComputedStyle(d[0].querySelector('summary'), '::after').content : null};
        }""")
        check("opening a FAQ item reveals its answer and leaves the other open",
              bool(opened) and opened["open"][:2] == [True, True] and all(opened["visible"]), str(opened))
        check("faq summary carries a css +/− marker", opened["marker"] in ('"+"', '"-"', '"−"'), str(opened["marker"]))
        if page.locator("#faq details").count() == 5:
            first.locator("summary").click()
            second.locator("summary").click()
            page.wait_for_timeout(60)

        # Structured data: both blocks parse, the app facts stay true, and the
        # FAQPage is a copy of the served #faq text rather than a fixture.
        ld_raw = page.evaluate(
            """() => [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => s.textContent)""")
        parsed, ld_errors = [], []
        for raw in ld_raw:
            try:
                parsed.append(json.loads(raw))
            except Exception as exc:  # noqa: BLE001 - report, never abort the run
                ld_errors.append(f"{exc}: {raw[:120]}")
        by_type = {}
        for obj in parsed:
            if isinstance(obj, dict):
                by_type.setdefault(obj.get("@type"), obj)
        check("both JSON-LD blocks parse as JSON",
              len(ld_raw) == 2 and not ld_errors
              and set(by_type) == {"SoftwareApplication", "FAQPage"},
              f"{len(ld_raw)} blocks, errors={ld_errors}, types={sorted(by_type)}")
        check("every JSON-LD block uses the schema.org context",
              bool(parsed) and all(o.get("@context") == "https://schema.org" for o in parsed), str(parsed)[:200])

        app = by_type.get("SoftwareApplication") or {}
        offers = app.get("offers") or {}
        check("SoftwareApplication keeps the verified app facts",
              app.get("name") == "FlutterGuard" and app.get("url") == CANONICAL
              and app.get("applicationCategory") == "SecurityApplication"
              and app.get("operatingSystem") == "Android 8.0+"
              and app.get("downloadUrl") == DOWNLOAD and app.get("license") == LICENSE,
              str(app))
        check("SoftwareApplication is offered free with no rating or version",
              str(offers.get("price")) == "0" and offers.get("priceCurrency") == "USD"
              and not any(k in ld_keys(app) for k in BANNED_LD_KEYS), str(offers))
        check("SoftwareApplication points at images that exist",
              app.get("image") == CANONICAL + "og-image.png"
              and app.get("screenshot") == CANONICAL + "assets/app/demo-poster.webp", str(app.get("image")))
        for key in ("image", "screenshot"):
            value = app.get(key) or ""
            if value.startswith(CANONICAL):
                r = page.request.get(base + urlparse(value).path)
                check(f"SoftwareApplication {key} resolves with an image content type",
                      r.status == 200 and (r.headers.get("content-type") or "").startswith("image/"),
                      f"{value} {r.status} {r.headers.get('content-type')}")
        features = app.get("featureList")
        check("SoftwareApplication featureList matches the visible step names",
              isinstance(features, list) and [f for f in features] == [t for t, _ in STEPS],
              str(features))

        faq_dom = norm(page.evaluate("() => document.querySelector('#faq')?.textContent || ''"))
        faq_page = by_type.get("FAQPage") or {}
        entities = faq_page.get("mainEntity") or []
        pairs = []
        for entity in entities if isinstance(entities, list) else []:
            answer = (entity or {}).get("acceptedAnswer") or {}
            pairs.append((norm(entity.get("name")), norm(answer.get("text"))))
        check("FAQPage holds exactly the five visible question/answer pairs",
              len(entities) == 5 and pairs == [(q, a) for q, a in FAQ_ITEMS]
              and all(e.get("@type") == "Question" for e in entities), str(pairs))
        check("every FAQPage string appears verbatim in the served #faq text",
              len(pairs) == 5 and all(q and a and q in faq_dom and a in faq_dom for q, a in pairs),
              str([p for p in pairs if not (p[0] in faq_dom and p[1] in faq_dom)]))
        check("JSON-LD carries no invented rating, review or version",
              not [k for k in ld_keys(parsed) if k in BANNED_LD_KEYS]
              and not any(token in raw for raw in ld_raw
                          for token in ("aggregateRating", "ratingValue", "softwareVersion")),
              str([k for k in ld_keys(parsed) if k in BANNED_LD_KEYS]))

        # Sitemap: one canonical entry, a lastmod, and no /demo route.
        sitemap = page.request.get(base + "/sitemap.xml")
        sitemap_text = sitemap.text()
        sitemap_root = None
        try:
            sitemap_root = ET.fromstring(sitemap_text)
        except ET.ParseError as exc:
            info(f"sitemap.xml does not parse: {exc}")
        locs = [e.text or "" for e in sitemap_root.iter(SITEMAP_NS + "loc")] if sitemap_root is not None else []
        lastmods = [e.text or "" for e in sitemap_root.iter(SITEMAP_NS + "lastmod")] if sitemap_root is not None else []
        check("sitemap.xml parses with exactly one canonical loc",
              sitemap.status == 200 and sitemap_root is not None and locs == [CANONICAL],
              f"{sitemap.status} {locs}")
        check("sitemap.xml carries a lastmod date and no /demo route",
              bool(lastmods) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", lastmods[0]) is not None
              and "/demo" not in sitemap_text, f"{lastmods} {sitemap_text[:80]}")
        check("sitemap lastmod is the humans.txt last-update date",
              bool(lastmods) and f"Last update: {lastmods[0]}" in page.request.get(base + "/humans.txt").text(),
              f"{lastmods}")

        # robots.txt keeps the crawler policy and points at absolute files.
        robots = page.request.get(base + "/robots.txt")
        robots_text = robots.text()
        check("robots.txt allows the site and lists an absolute sitemap",
              robots.status == 200 and "Allow: /" in robots_text
              and re.search(r"^Sitemap:\s*https://flutterguard\.dev/sitemap\.xml\s*$", robots_text, re.M) is not None,
              f"{robots.status} {robots_text[:80]}")
        check("robots.txt points LLM agents at the absolute llms.txt",
              "https://flutterguard.dev/llms.txt" in robots_text)
        check("robots.txt allows the answer engines it claims",
              "OAI-SearchBot" in robots_text and "PerplexityBot" in robots_text
              and "GPTBot" in robots_text, robots_text[:80])
        robots_meta = page.evaluate("""() => [...document.querySelectorAll('meta[name="robots"]')]
            .map(m => m.getAttribute('content') || '').join(' ')""")
        check("home page is indexable: no noindex, no nofollow",
              "noindex" not in robots_meta and "nofollow" not in robots_meta, robots_meta)

        # LLM files describe the page that actually ships.
        h1_subject = norm(h1s[0] if h1s else "").rstrip(".").lower()
        for path in ("/llms.txt", "/llms-full.txt"):
            r = page.request.get(base + path)
            text = r.text()
            check(f"{path} describes the current page and steps",
                  r.status == 200 and h1_subject in text.lower()
                  and all(name.lower() in text.lower() for name, _ in STEPS)
                  and "/demo" not in text, f"{r.status} {len(text)} bytes")
            check(f"{path} stays factual: no ratings, benchmarks or Play availability",
                  r.status == 200
                  and not re.search(r"benchmark|ratingvalue|aggregaterating|available on google play|play listing is live",
                                    text, re.I),
                  text[:120])

        # Manifest: valid JSON, install metadata, icons that resolve.
        manifest_resp = page.request.get(base + "/site.webmanifest")
        try:
            manifest = json.loads(manifest_resp.text())
        except json.JSONDecodeError:
            manifest = {}
        icons = manifest.get("icons") or []
        icon_results = []
        for icon in icons:
            r = page.request.get(base + (icon.get("src") or ""))
            icon_results.append((icon.get("src") or "", r.status,
                                 (r.headers.get("content-type") or "").split(";")[0]))
        check("site.webmanifest parses with name, short_name, start_url and display",
              manifest_resp.status == 200 and manifest.get("name") and manifest.get("short_name")
              and manifest.get("start_url") == "/" and manifest.get("display") == "standalone"
              and manifest.get("theme_color") == "#f4f6f5"
              and manifest.get("description") == head["description"][0], str(manifest)[:200])
        check("every manifest icon resolves with an image content type",
              len(icons) == 2 and len(icon_results) == 2
              and all(status == 200 and ctype.startswith("image/") for _, status, ctype in icon_results),
              str(icon_results))

        home_html = page.request.get(base + "/").text()
        check("recording slot comment removed now that the clip ships",
              "Recording slot" not in home_html and "audit-recording.mp4" not in home_html)
        for path in ("/sitemap.xml", "/llms.txt", "/llms-full.txt"):
            r = page.request.get(base + path)
            check(f"{path} avoids demo", r.status == 200 and "/demo" not in r.text(), str(r.status))

        # Static assets and content types.
        for path, ctype in (
            ("/styles.css", "text/css"),
            ("/assets/fonts/manrope-latin.woff2", "font/woff2"),
            ("/assets/app/inventory.webp", "image/webp"),
            ("/assets/app/demo.mp4", "video/mp4"),
            ("/assets/app/demo-poster.webp", "image/webp"),
            ("/assets/brand/google-play-badge-en.svg", "image/svg+xml"),
            ("/assets/brand/github-lockup-white.svg", "image/svg+xml"),
            ("/icon-192.png", "image/png"),
            ("/og-image.png", "image/png"),
            ("/site.webmanifest", "application/manifest+json"),
        ):
            r = page.request.get(base + path)
            got = (r.headers.get("content-type") or "").split(";")[0]
            check(f"{path} 200 + {ctype}", r.status == 200 and got == ctype, f"{r.status} {got}")

        clip = page.request.get(base + "/assets/app/demo.mp4")
        check("demo clip is served and stays under 5 MB",
              clip.status == 200 and 0 < len(clip.body()) <= 5_000_000, f"{clip.status} {len(clip.body())} bytes")
        poster_asset = page.request.get(base + "/assets/app/demo-poster.webp")
        check("demo poster is served with an image content type",
              poster_asset.status == 200 and (poster_asset.headers.get("content-type") or "").startswith("image/"),
              f"{poster_asset.status} {poster_asset.headers.get('content-type')}")

        # Dead rules must not ship once their markup is gone.
        css = page.request.get(base + "/styles.css").text()
        for dead in (".eyebrow", ".device-caption", ".pros-list", ".feature-list",
                     ".play-slot", ".store-note", ".play-badge"):
            check(f"styles.css carries no dead {dead} rule", dead not in css)
        check("css no longer pauses the chain on hover",
              ":hover .chain__track" not in css
              and ".chain:hover" not in css, "hover pause rule still present")
        check("css keeps the keyboard focus pause",
              ".chain:focus-within .chain__track" in css, "focus-within pause rule missing")

        # Caching is a server concern; nginx must send it, Python preview may not.
        # Presence is asserted before policy: a vanished header must fail the run
        # instead of silently shrinking the denominator. `Server: nginx` is the
        # only regime signal available (the preview sends neither CSP nor
        # Cache-Control), so presence checks run only against the shipped server.
        server = (home_headers.get("server") or "").lower()
        strict_headers = "nginx" in server
        for path, needle in (("/assets/fonts/manrope-latin.woff2", "max-age=31536000"), ("/styles.css", "max-age=3600"),
                             ("/assets/app/demo.mp4", "max-age=604800")):
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
        for width in (1024, 1280, 1440, 1920):
            page.set_viewport_size({"width": width, "height": 900})
            page.wait_for_timeout(80)
            nav = page.evaluate("""() => {
                const sel = 'header .brand, header .site-nav > a, header .header-actions > a';
                const items = [...document.querySelectorAll(sel)]
                    .filter(e => e.getBoundingClientRect().width > 0)
                    .map(e => ({cls: e.className, r: e.getBoundingClientRect()}));
                const cys = items.map(i => i.r.top + i.r.height / 2);
                const brand = document.querySelector('header .brand').getBoundingClientRect();
                const anchors = [...document.querySelectorAll('header .site-nav > a')]
                    .map(a => a.getBoundingClientRect());
                const anchorMid = anchors.length
                    ? (Math.min(...anchors.map(r => r.left)) + Math.max(...anchors.map(r => r.right))) / 2 : 0;
                return {count: items.length, spread: Math.round((Math.max(...cys) - Math.min(...cys)) * 10) / 10,
                        headerH: Math.round(document.querySelector('header.site-header').getBoundingClientRect().height),
                        brandLeft: Math.round(brand.left),
                        anchorMid: Math.round(anchorMid), vw: innerWidth, anchors: anchors.length,
                        overflow: Math.round(document.documentElement.scrollWidth - innerWidth)};
            }""")
            check(f"navbar holds one row at {width}px", nav["count"] == 7 and nav["spread"] <= 2
                  and nav["headerH"] <= 72 and nav["overflow"] <= 1, str(nav))
            check(f"navbar anchors sit centred at {width}px",
                  abs(nav["anchorMid"] - nav["vw"] / 2) <= 24, str(nav))

        for width in (320, 390):
            page.set_viewport_size({"width": width, "height": 844})
            page.wait_for_timeout(80)
            navsmall = page.evaluate("""() => {
                const els = [...document.querySelectorAll('header .brand, header .site-nav > a, header .header-actions > a')]
                    .filter(e => e.getBoundingClientRect().width > 0)
                    .map(e => { const r = e.getBoundingClientRect();
                        return {cls: e.className, left: Math.round(r.left), right: Math.round(r.right),
                                h: Math.round(r.height * 10) / 10}; });
                return {els, vw: innerWidth, overflow: Math.round(document.documentElement.scrollWidth - innerWidth),
                        anchors: [...document.querySelectorAll('header .site-nav > a')]
                            .filter(a => a.getBoundingClientRect().width > 0).length};
            }""")
            check(f"navbar drops the four anchors and keeps brand, GitHub and Get app at {width}px",
                  navsmall["overflow"] <= 1 and len(navsmall["els"]) == 3 and navsmall["anchors"] == 0
                  and any("brand" in e["cls"] for e in navsmall["els"])
                  and any("github-button" in e["cls"] for e in navsmall["els"])
                  and any("navbar-cta" in e["cls"] for e in navsmall["els"])
                  and all(0 <= e["left"] and e["right"] <= navsmall["vw"] and e["h"] >= 43.5 for e in navsmall["els"]),
                  str(navsmall))

        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(100)
        page.evaluate("window.scrollTo(0, 0)")
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
            const n = document.querySelector('header .header-actions')?.getBoundingClientRect();
            return b && n ? {brandRight: Math.round(b.right), actionsLeft: Math.round(n.left)} : null;
        }""")
        check("header brand and actions do not collide at 320px", bool(header_fit) and header_fit["brandRight"] <= header_fit["actionsLeft"], str(header_fit))

        page.set_viewport_size({"width": 1280, "height": 720})
        page.wait_for_timeout(100)
        page.evaluate("window.scrollTo(0, 0)")
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
            page.evaluate("window.scrollTo(0, 0)")
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
        # The mobile CTA is one natural-width action, not a stretched full-bleed button.
        mobile_stack = page.evaluate("""() => {
            const d = document.querySelector('.download-button');
            const a = document.querySelector('.install-actions');
            const c = document.querySelector('.hero-copy');
            if (!d || !a || !c) return null;
            const dr = d.getBoundingClientRect();
            const ar = a.getBoundingClientRect();
            const cr = c.getBoundingClientRect();
            return {w: Math.round(dr.width), h: Math.round(dr.height * 10) / 10,
                    containerW: Math.round(cr.width), actionsW: Math.round(ar.width),
                    leftGap: Math.round((dr.left - cr.left) * 10) / 10};
        }""")
        check("narrow hero CTA keeps its natural width and left alignment",
              bool(mobile_stack) and mobile_stack["w"] < mobile_stack["containerW"] * 0.85
              and mobile_stack["leftGap"] <= 1 and mobile_stack["h"] >= 43.5, str(mobile_stack))
        page.set_viewport_size({"width": 1440, "height": 900})
        page.wait_for_timeout(120)
        reduce_chain = page.evaluate("""() => {
            const track = document.querySelector('#features .chain__track:not([aria-hidden="true"])');
            if (!track) return null;
            const nodes = [...track.querySelectorAll(':scope > li')];
            return nodes.map((li, i) => {
                const a = getComputedStyle(li, '::after');
                const r = li.getBoundingClientRect();
                const next = i < nodes.length - 1 ? nodes[i + 1].getBoundingClientRect() : null;
                return {insetEnd: parseFloat(a.insetInlineEnd), width: parseFloat(a.width),
                        content: a.content, nodeRight: Math.round(r.right * 100) / 100,
                        nextLeft: next ? Math.round(next.left * 100) / 100 : null,
                        reaches: next ? r.right + Math.abs(parseFloat(a.insetInlineEnd)) >= next.left - 1 : null};
            });
        }""")
        check("reduced-motion connectors span the grid gutter and meet the next dot",
              bool(reduce_chain) and len(reduce_chain) == 3
              and all(n["insetEnd"] <= -23.5 for n in reduce_chain[:2])
              and all(n["reaches"] for n in reduce_chain[:2])
              and reduce_chain[2]["content"] == "none", str(reduce_chain))
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
            const tracks = [...document.querySelectorAll('.chain__track')];
            const amb = document.querySelector('.device-ambient');
            if (tracks.length !== 2 || !amb) return null;
            const t = getComputedStyle(tracks[0]);
            const dup = getComputedStyle(tracks[1]);
            const a = getComputedStyle(amb);
            return {trackName: t.animationName, trackPlay: t.animationPlayState,
                    dupName: dup.animationName, dupDisplay: dup.display,
                    transform: t.transform, dupTransform: dup.transform,
                    ambName: a.animationName, ambPlay: a.animationPlayState, ambBg: a.backgroundImage};
        }""")
        check("reduced motion leaves both tracks and the hero backdrop fully static",
              bool(static_motion) and static_motion["trackName"] == "none"
              and static_motion["dupName"] == "none"
              and static_motion["trackPlay"] == "paused" and static_motion["dupDisplay"] == "none"
              and static_motion["transform"] == "none"
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
        check("chain loops on the 22s cycle, endlessly",
              bool(anim) and anim["trackName"] == "chain-scroll" and anim["trackDur"] == [22]
              and anim["trackIter"] == "infinite", str(anim))
        check("hero ambient drift runs behind the phone",
              bool(anim) and anim["ambName"] != "none" and all(d >= 25 for d in anim["ambDur"]), str(anim))
        check("chain connector bridges the gap to the next node",
              bool(anim) and bool(anim["connector"]) and anim["connector"]["content"] != "none"
              and anim["connector"]["insetEnd"] < -0.5 and anim["connector"]["width"] > 20, str(anim["connector"]))
        check("no horizontal overflow while the chain animates at 390px",
              bool(anim) and anim["overflowX"] <= 1, str(anim))
        mp.set_viewport_size({"width": 1440, "height": 900})
        mp.wait_for_timeout(250)
        # Read the row with the pointer parked on it: hovering must not freeze it.
        mp.locator("#features .chain").scroll_into_view_if_needed()
        mp.wait_for_timeout(100)
        box = mp.locator("#features .chain").bounding_box()
        if box:
            mp.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        mp.wait_for_timeout(150)
        hover_one = mp.evaluate("""() => {
            const t = document.querySelector('.chain__track');
            return {matrix: getComputedStyle(t).transform, at: Math.round(performance.now())};
        }""")
        mp.wait_for_timeout(1700)
        hover_two = mp.evaluate("""() => {
            const t = document.querySelector('.chain__track');
            return {matrix: getComputedStyle(t).transform, at: Math.round(performance.now()),
                    dur: getComputedStyle(t).animationDuration, name: getComputedStyle(t).animationName};
        }""")
        info(f"motion sample A {hover_one['at']}ms {hover_one['matrix']}")
        info(f"motion sample B {hover_two['at']}ms {hover_two['matrix']}")
        check("chain visibly advances while hovered (no hover freeze)",
              bool(hover_one) and bool(hover_two) and hover_one["matrix"] != hover_two["matrix"]
              and hover_two["name"] == "chain-scroll" and hover_two["dur"] == "22s",
              f"{hover_one} -> {hover_two}")
        mp.mouse.move(0, 0)
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
        check("same-origin media plays under the default-src CSP without a media-src exception",
              bool(playback) and playback.get("readyState", 0) >= 2
              and not any("Content Security Policy" in e or "Refused to load" in e for e in console_errors),
              "; ".join(console_errors))
        check("no page errors", not page_errors, "; ".join(page_errors))
        check("no failed requests", not failed, "; ".join(failed))
        check("no failed asset responses", not bad_responses, "; ".join(bad_responses))
        check("all requests stay on this origin", all(urlparse(u).netloc == host for u in requests), str(sorted({urlparse(u).netloc for u in requests})))

        # Content without JavaScript: poster, single install action, FAQ and why remain.
        nojs = browser.new_context(java_script_enabled=False, viewport={"width": 1440, "height": 900})
        njs = nojs.new_page()
        njs.goto(base + "/", wait_until="load")
        check("no-JS h1 visible", njs.locator("h1").is_visible())
        check("no-JS video poster visible", njs.locator(".device-video").is_visible())
        check("no-JS why paragraph with inline mark visible",
              njs.locator("#why p .flutter-mark").is_visible() and njs.locator("#why p").is_visible())
        check("no-JS FAQ summary visible", njs.locator("#faq summary").first.is_visible())
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
