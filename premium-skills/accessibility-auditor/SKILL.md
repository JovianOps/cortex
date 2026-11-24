---
name: accessibility-auditor
description: Audit HTML/UI for WCAG 2.2 AA flaws with exact code fixes.
version: 0.4.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [accessibility, a11y, wcag, aria, frontend]
    related_skills: [code-review-assistant, testing-automation, security-auditor, documentation-generator]
---

# Accessibility Auditor

Audit web interfaces (HTML, CSS, React, Vue, Svelte) against **WCAG 2.2 AA** with deterministic automated scanning, keyboard-navigation verification, contrast & forced-colors checks, and exact minimal code patches.

## When to Use

- Pre-release accessibility audit of landing pages, web apps, forms, modals, toolbars, or component libraries
- Fixing keyboard traps, missing focus styles, broken ARIA attributes, or low-contrast themes
- Verifying `prefers-reduced-motion`, `forced-colors: active` (Windows High Contrast), and touch-target sizing (WCAG 2.2 `24x24px` minimum)
- Translating WCAG 2.2 AA criteria into concrete `file:line` patches and automated tests

### When Not to Use

- Pure backend APIs, CLI tools, or database layers with no user interface
- Claiming full legal/VPAT compliance from static checks alone (automated checks catch structural defects; screen-reader & manual keyboard testing remain mandatory)

## How to Run

```bash
# Universal CLI (Claude Code, Codex, Gemini CLI, Cursor, Copilot, OpenCode, OpenClaw, Goose, Cline)
npx skills add JovianOps/cortex --skill accessibility-auditor -g -y

# Run the bundled deterministic HTML accessibility scanner directly
python premium-skills/accessibility-auditor/scripts/a11y_scan.py path/to/index.html

# Hermes Agent
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/premium-skills/accessibility-auditor --yes
```

## Mandatory Accessibility Audit Protocol

### Step 1 — Run Deterministic Static Scan First

Execute the bundled static HTML/CSS auditor (plus `axe-core`/`pa11y` when available) and capture exact `file:line` findings:

```bash
python premium-skills/accessibility-auditor/scripts/a11y_scan.py index.html
```

Never fabricate WCAG issue counts or claim contrast passes without calculating luminance ratios.

### Step 2 — Audit Core WCAG 2.2 AA Pillars

Verify each area systematically and cite exact `file:line` evidence:

1. **Perceivable (1.x)**:
   - Meaningful `alt` on informative `<img>`, empty `alt=""` on decorative images, `aria-hidden="true"` on decorative icons.
   - Document `<html lang="...">`, unique `<title>`, and non-skipped heading hierarchy (`<h1>` → `<h2>` → `<h3>`).
   - Text contrast >= **4.5:1** (normal text) and >= **3.0:1** (large text & UI control boundaries/icons).
   - High-contrast support: `@media (forced-colors: active)` preserves visible borders and active states (`Highlight`, `CanvasText`, `ButtonText`).
2. **Operable (2.x)**:
   - Semantic interactive elements (`<button type="button">`, `<a href>`, `<dialog>`) — NO clickable `<div onclick>` or `<span onclick>` without full keyboard & role parity.
   - Zero positive `tabindex` (`tabindex > 0`), visible `:focus-visible` indicator (never bare `outline: none` without replacement), and no keyboard traps.
   - WCAG 2.2 Target Size (2.5.8): interactive controls >= **24x24 CSS px** (prefer >= 44px on `@media (pointer: coarse)`).
   - Motion safety: wrap transitions/animations in `@media (prefers-reduced-motion: no-preference)` or neutralize under `prefers-reduced-motion: reduce`.
3. **Understandable & Robust (3.x / 4.x)**:
   - Every form input has an explicit programmatic `<label for>`, `aria-label`, or `aria-labelledby` (placeholder is NOT a label).
   - First Rule of ARIA: prefer native HTML (`<dialog>`, `<details>`, `<button>`) before custom ARIA; verify `aria-expanded`, `aria-pressed`, `aria-controls`, `aria-live`, and `role="status"` match real DOM state.

### Step 3 — Deliver Minimal Verified Fixes & Re-Scan

Apply targeted fixes without breaking visual layout, then re-run `a11y_scan.py` (and any UI test suite) to confirm zero regressions.

## Strict Output Contract

```markdown
## Accessibility Audit Summary
- **Target:** Files/components audited and tools executed (`a11y_scan.py`, etc.).
- **Findings:** Blocker: <N> | Serious: <N> | Moderate: <N> | Minor: <N>

## Verified Findings

### [BLOCKER/SERIOUS/MODERATE/MINOR] Rule Title (WCAG X.Y.Z Level) — `path/to/file:line`
- **Impact:** Who is blocked (keyboard-only, screen-reader, low-vision, vestibular/motion-sensitive users).
- **Evidence:** Exact offending snippet.
- **Fix:** Minimal accessible HTML/CSS/JS replacement.

## Manual Verification Checklist
- Remaining checks requiring live assistive technology (keyboard Tab/Shift+Tab flow, screen-reader announcement, 200% zoom reflow).
```
