# Changelog

All notable changes to **Cortex** are documented in this file. This project follows [Semantic Versioning](https://semver.org/).

## [0.4.0] — 2026-11-24

A major developer-experience, IDE integration, and supply-chain hardening release adding first-class **Visual Studio Code** support, a zero-dependency **Light Swiss editorial website**, and fully SHA-pinned, self-auditing **GitHub Actions CI/CD**.

### Added
- **First-Class Visual Studio Code Support**:
  - Added native VS Code Chat Plugin & Marketplace manifests (`.github/plugin.json` and `.github/plugin/marketplace.json`) exposing `cortex`, `cortex-core`, and `cortex-extended` for `chat.plugins.marketplaces: ["JovianOps/cortex"]` and `@agentPlugins`.
  - Added `.github/copilot-instructions.md` for native VS Code / GitHub Copilot workspace guidance.
  - Added shared `.vscode/settings.json` (`chat.useAgentSkills: true`, LF line endings, Python `unittest` runner) and `.vscode/tasks.json` (ready-to-run Command Palette tasks for `Cortex: Doctor`, `Cortex: Run Full Validation & Tests`, `Cortex: Repackage ZIPs & Checksums`, `Cortex: Verify Website`, and `Cortex: Audit GitHub Actions Workflows`).
  - Promoted `vscode` (`Visual Studio Code`, with `vs-code` / `code` aliases) to a first-class target in `scripts/install_skills.py` (with `--agent all` destination deduplication) and added `--write-vscode-settings` to safely merge `"chat.useAgentSkills": true` into `.vscode/settings.json`.
  - Added a dedicated `vscode` detection probe in `scripts/cortex.py` (`~/.vscode`, `./.vscode`, `code` / `code-insiders` CLIs, and `.cortex-lock.json` counting from `.github/skills/` and `~/.copilot/skills/`).
- **Light Swiss Editorial Website & Verification (`index.html` + `scripts/verify_site.py`)**:
  - Rebuilt `index.html` from scratch as a clean, zero-dependency HTML/CSS/JS developer site with a **Light Swiss** default theme (`#F6F5F0` archival paper, sharp `0px` geometry, `1.5–2px` structural rules, International Swiss Red `#D92B1C` accent), Swiss Noir dark mode, and an explicit segmented **`Light | Dark`** toggle switch in the header.
  - Added 16 install targets (including dedicated **Visual Studio Code**), searchable 24-skill table, slide-over SHA-256 Skill Inspector, 6 one-click role packs, and `#verify` supply-chain ledger.
  - Added `scripts/verify_site.py` (using stdlib `HTMLParser` + `node --check`, `checksums.json`/`packs.json` parity checks, and WCAG 2.2 AA `a11y_scan.py`).
- **Hardened & Expanded CI/CD (`.github/workflows/ci.yml` & `publish-npm.yml`)**:
  - Pinned every GitHub Action across both workflows to verified 40-character release commit SHAs (removing the floating `aquasecurity/trivy-action@master` tag).
  - Added workflow self-auditing via Cortex's bundled `lint_actions.py`, Python 3.12 & 3.13 matrix testing, strict `compileall` + `ruff check --select E9,F`, hidden-directory YAML validation (including `.github/workflows/*.yml`), `verify_site.py`, `check_docs.py`, and an isolated `npm pack` CLI smoke test on every PR.
  - Added `concurrency` groups, explicit `timeout-minutes`, `if: always()` Trivy SARIF upload, and fixed the `release` job trigger (`tags: ['v*']`), permissions (`contents: write`), and `needs:` gates.
- **Expanded Automated Tests (`tests/test_cortex_tooling.py`)**:
  - Added `test_vscode_install_settings_and_detection` (**17/17 tests** passing in CI).

### Changed
- Bumped all 24 `SKILL.md` playbooks, `package.json`, `packs.json`, `evals/skill_evals.json`, `checksums.json`, CLI scripts, and all **9** multi-agent manifests (`.claude-plugin/`, `.github/plugin.json`, `.github/plugin/marketplace.json`, `.agents/plugins/`, `.cursor-plugin/`, `plugin.json`, `gemini-extension.json`) to `0.4.0`.
- Re-packaged all 24 deterministic skill ZIPs (`zips/` and `premium-zips/`) and regenerated `checksums.json` at `v0.4.0`.

### Fixed
- Fixed CI checksum drift after CodeQL output-sanitization updates to `premium-skills/security-auditor/scripts/secret_scan.py`.
- Fixed `scripts/validate_yaml.py` so hidden directories (including `.github/workflows/`) are actually validated.
- Fixed the `--write-aider-conf` flag generated in `index.html` and removed unused Python imports caught by `ruff`.

## [0.3.0] — 2026-11-23

A major platform release transforming Cortex from a collection of Markdown playbooks into a **complete, verifiable AI-agent skill platform** with a unified CLI, role-based skill packs, 10 bundled deterministic tools, SHA-256 integrity verification, and a live A/B benchmark harness.

### Added
- **Unified `cortex` Developer CLI (`scripts/cortex.py` + `bin/cortex.mjs`)**:
  - Exposed via `package.json` `"bin": { "cortex": "./bin/cortex.mjs" }` (`npx cortex` / `python scripts/cortex.py`) with 13 subcommands: `detect`, `doctor`, `search`, `packs`, `new`, `install`, `status`, `upgrade`, `uninstall`, `audit`, `eval`, `package`, `verify`.
  - `cortex detect` auto-detects installed AI coding agents and `.cortex-lock.json` installs across the workspace & home directory.
  - `cortex doctor` runs environment, ZIP/SHA-256, 7-manifest, `packs.json`, and lockfile drift diagnostics.
  - `cortex new <slug> [--with-script]` scaffolds a brand-new `SKILL.md` (+ optional helper script) guaranteed to pass Cortex's 100/100 structural quality audit.
- **6 Curated Role-Based Skill Packs (`packs.json`)**:
  - One-command role bundles (`fullstack`, `devops-sre`, `security-hardening`, `python-pro`, `academic`, `clean-migration`) wired into `--pack <id>` in `scripts/install_skills.py` / `scripts/cortex.py`, validated in `scripts/validate_manifests.py`, and available as one-click presets in `index.html`.
- **4 New Extended Engineering Skills (20 → 24 total skills)**:
  - `incident-response` — SEV-1/2/3 triage, blast-radius containment, reversible rollback-first stabilization, UTC timelines, and blameless postmortems.
  - `release-engineering` — Deterministic SemVer computation, manifest version-parity gates, SHA-256 checksums, Keep-a-Changelog notes, and rollback procedures.
  - `observability-setup` — Structured JSON logging with `trace_id` correlation, RED/USE golden metrics, cardinality stop gates, SLO error budgets, and burn-rate alerting.
  - `accessibility-auditor` — WCAG 2.2 AA auditing across semantic HTML, keyboard focus, contrast, `forced-colors: active`, and `prefers-reduced-motion`.
- **10 Bundled Executable Helper Scripts Inside Skills**:
  - `skills/college-report-card/scripts/grade_calc.py` — Zero-dependency `Decimal` weighted grade & GPA calculator with weight-sum (`1.00`) and duplicate-ID stop gates.
  - `skills/blender-3d-modeling/scripts/bmesh_check.py` — Automated Blender `bmesh` manifold, zero-area face, loose-vertex, and scale auditor.
  - `skills/memory-manager/scripts/memory_store.py` — Versioned JSON session-memory store with decision log, task lifecycle, and staleness detection.
  - `skills/documentation-generator/scripts/check_docs.py` — Offline Markdown relative-link and heading-anchor verifier.
  - `premium-skills/security-auditor/scripts/secret_scan.py` — Offline CWE-mapped secret & dangerous-sink scanner with mandatory secret redaction.
  - `premium-skills/api-designer/scripts/lint_openapi.py` — OpenAPI 3.0/3.1 contract linter (`operationId`, error envelopes, security schemes).
  - `premium-skills/accessibility-auditor/scripts/a11y_scan.py` — Static WCAG 2.2 AA HTML/CSS auditor.
  - `premium-skills/docker-generator/scripts/lint_dockerfile.py` — Offline Dockerfile security & best-practice linter (tag pinning, non-root `USER`, secret leaks, `HEALTHCHECK`).
  - `premium-skills/devops-pipeline/scripts/lint_actions.py` — Offline GitHub Actions security linter (40-char SHA pinning, least-privilege `permissions`, expression-injection checks).
  - `premium-skills/release-engineering/scripts/semver_bump.py` — Offline Conventional Commits -> next SemVer calculator + Keep-a-Changelog draft generator.
- **Cryptographic Checksums & Reproducible Multi-File ZIPs**:
  - Generated `checksums.json` recording SHA-256 hashes of every `SKILL.md`, bundled script, and `.zip` archive across all 24 skills.
  - Upgraded `scripts/package_skills.py` to bundle full skill directories (`SKILL.md` + `scripts/`) deterministically with fixed ZIP timestamps and verify `checksums.json` parity.
- **Full Lifecycle Multi-Agent Skill Manager (`scripts/install_skills.py`)**:
  - Added `--pack <id>` role-pack installs and `--remote` zero-clone installation with mandatory SHA-256 verification before writing any file.
  - Added `.cortex-lock.json` lockfile tracking plus `--status` (tamper/drift detection), `--check-updates`, `--upgrade`, and `--uninstall`.
- **Live A/B Benchmark Runner (`scripts/eval_skills.py --run`)**:
  - Expanded `evals/skill_evals.json` to 24 paired 100-point A/B rubrics covering all 24 skills.
  - Added zero-dependency `--run` harness supporting OpenAI, Anthropic, Gemini, and OpenAI-compatible endpoints with automatic Markdown scorecard generation.
- **Automated Test Suite (`tests/test_cortex_tooling.py`)**:
  - Added 16 end-to-end tests covering the `cortex` CLI (`detect`, `doctor`, `search`, `packs`, `new` -> 100/100 audit), pack installs, packaging, manifest validation, full installer lifecycle, SHA-256 remote tamper rejection, eval suite validation, and all 10 bundled helper scripts.

### Changed
- Bumped all 24 `SKILL.md` playbooks, `package.json`, `packs.json`, and all 7 multi-agent manifests (`.claude-plugin/`, `.agents/plugins/`, `.cursor-plugin/`, `plugin.json`, `gemini-extension.json`) to `0.3.0`.
- Upgraded `index.html` with 24 skills, `+ Script` card badges, `With Scripts (10)` catalog filter, 6 One-Click Role Packs in the Command Builder, `Python --remote (SHA-256)` 14th install target, and bundled script previews in the Skill Inspector drawer.
- Updated `README.md`, `AGENTS.md`, `GEMINI.md`, and `.github/workflows/ci.yml` for `v0.3.0`.

## [0.2.0] — 2026-11-23

### Added
- Native multi-agent support across 13 platforms (Claude Code, Claude Apps, OpenAI Codex CLI, ChatGPT, Gemini CLI, Cursor, GitHub Copilot & VS Code, OpenCode, OpenClaw, Goose, Aider, Cline, and Hermes Agent) via 7 plugin/extension manifests and `scripts/install_skills.py`.
- Redesigned interactive catalog website (`index.html`) with globally synced Agent Picker and Bash/PowerShell shell toggles.
- Upgraded all 20 skills to executable playbooks with stop gates, output contracts, and a 20-task 100-point A/B evaluation suite.

## [0.1.0] — 2026-11-01

### Added
- Initial release of 10 core and 10 extended Hermes Agent skills with ZIP packaging and CI validation.
