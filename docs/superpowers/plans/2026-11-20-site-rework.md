# FlutterGuard site rework implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the public site accurately explain and onboard Android, CLI/CI and engine users.

**Architecture:** Preserve static HTML, paired Markdown, shared CSS and progressive media JS. Update product claims together; add one CLI guide rather than a new documentation system.

**Tech stack:** HTML, CSS, existing JavaScript, nginx, existing Python Playwright checks.

**Spec:** `docs/superpowers/specs/2026-11-20-site-rework-design.md`

## Global constraints

- No new runtime or build dependency.
- Preserve existing URLs and `#why`, `#features`, `#guides`, `#faq`, `#contact` anchors.
- CLI and engine are source-built; do not invent downloads, registry packages or a CLI compare command.
- Confirmed artifact facts do not establish exploitability. Only confirmed findings affect the grade.
- Existing Android media predates 0.4.0 and must be labelled.
- Do not advertise Play beta as publicly available. Keep signing/data-loss caveats near installation guidance.
- Preserve robots training opt-out, analytics disclosure, headers and Markdown negotiation.
- No app-source, Play, production-host, original-checkout or unrelated-worktree mutation.
- No external marketing sends, submissions or indexing requests.

## Review focus

1. Wrong install channel: links and adjacent text must not promise 0.4.0 on public Play.
2. Copy-pasted CLI command: output parents must exist and destination files must not already exist.
3. Browser without JavaScript or failed media: all workflows remain reachable.
4. Narrow viewport, enlarged text and keyboard: controls remain visible and operable.
5. Alternative representations: HTML, schema, Markdown, references and Docker-served files agree.

### Task 1: Pin the new public contract and landing experience

**Files:** `tests/check_site.py`, `index.html`, `styles.css`, `site.js` only if needed.

**Interfaces:** Preserve video `.device-video`, `#pause-motion`, failure recovery and existing public anchors. Introduce `#get-started`, `#cli`, `#engine`, `#confidence`, `#compare`.

- [ ] Replace obsolete phone-only assertions with workflow, source-build, confidence, comparison and version-channel contracts; retain media/delivery checks.
- [ ] Run `python3 tests/check_site.py http://127.0.0.1:8786` and observe the expected new-content failures before product edits.
- [ ] Rework the homepage using existing tokens; add responsive styles without breaking article layouts.
- [ ] Run the contract and inspect 1440px / 390px screenshots; fix the affected path.

### Task 2: Add the CLI path and synchronise public truth

**Files:** new `cli/index.html`, `cli/index.md`; `index.md`, `llms.txt`, `llms-full.txt`, `.well-known/ai-catalog.json`, `sitemap.xml`, `Dockerfile`; existing HTML/Markdown under `about`, `privacy`, `mobsf-alternative`, `flutter-security`, `flutter-apk-inspection`, `flutter-security-checklist`; marketing documents and `assets/PROVENANCE.md`.

**Interfaces:** `/cli/` title/H1 `FlutterGuard CLI: scan Flutter APKs in CI`; paired Markdown canonical `https://flutterguard.dev/cli/`; source contract from `anasfik/FlutterGuard@1c28d0f`.

- [ ] Add `/cli/` to route/delivery and content assertions before creating it.
- [ ] Explain JDK 17+, repository build setup, `./gradlew :cli:installDist`, launcher, scan flags, fresh output paths, exits 0/1/2, redaction and CI limits.
- [ ] Update machine references and Docker COPY inventory together.
- [ ] Correct only conflicting mobile-only/confidence/CI claims in existing guides, About and Privacy; keep page intent, URLs and historical releases.
- [ ] Update launch and growth assets with dated GSC evidence and explicit publication gates.
- [ ] Run the full contract; require every HTML/Markdown twin and Docker input to exist.

### Task 3: Prove, review and deliver

**Files:** scoped fixes, `docs/marketing/2026-11-20-site-audit.md`, product context, proof report.

**Interfaces:** baseline `784fcec`; local production nginx at `http://127.0.0.1:8786`; screenshots under `/tmp/opencode/fg-site-rework-proof/`.

- [ ] Run full strict browser checks, contrast/semantics and focused keyboard paths; capture mobile and desktop screenshots.
- [ ] Repeat `/tmp/opencode/fg-site-rework-runtime/measure.py` with the same three-run local lab conditions.
- [ ] Request a read-only code review for the implementation wave and a screenshot-based visual review; fix blocking findings and recheck affected paths.
- [ ] Inspect final diff and original-worktree status, commit medium logical batches, then push approved scope as a separate action.
- [ ] Report exact checks, artifacts and remaining owner deployment/live-verification step. Stop only this task's preview process.

## Preflight

| Shared interface | Producer / consumer | Resolution |
|---|---|---|
| Homepage anchors | Task 1 / Task 2 Markdown and references | Preserve old anchors; use the named new anchors verbatim. |
| `/cli/` inventory | Task 2 / Task 1 tests | Add route expectation before creating files; full suite becomes green after Task 2. |
| Shared CSS | Task 1 / existing articles and new CLI page | Scope homepage layouts; retain article rules and test existing guide widths. |
| Product truth | Task 2 / schema, copy, launch assets | Source at 1c28d0f wins over stale marketing text. |
| Baseline checks | All tasks | Existing media, accessibility and delivery checks stay; only obsolete positioning assertions change. |

Ruling: keep the static stack and current brand rather than introduce a framework or redesign unrelated article layouts. If wrong, the cost is a later visual revision, not data loss.
