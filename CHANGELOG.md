# Changelog

All notable changes to **Cortex** are documented in this file. This project follows [Semantic Versioning](https://semver.org/).

## [0.3.0] — 2026-11-23

### Added
- **4 New Extended Engineering Skills (20 → 24 total skills)**:
  - `incident-response` — SEV-1/2/3 triage, blast-radius containment, reversible rollback-first stabilization, UTC timelines, and blameless postmortems.
  - `release-engineering` — Deterministic SemVer computation, manifest version-parity gates, SHA-256 checksums, Keep-a-Changelog notes, and rollback procedures.
  - `observability-setup` — Structured JSON logging with `trace_id` correlation, RED/USE golden metrics, cardinality stop gates, SLO error budgets, and burn-rate alerting.
  - `accessibility-auditor` — WCAG 2.2 AA auditing across semantic HTML, keyboard focus, contrast, `forced-colors: active`, and `prefers-reduced-motion`.
- **5 Bundled Executable Helper Scripts Inside Skills**:
  - `skills/college-report-card/scripts/grade_calc.py` — Zero-dependency `Decimal` weighted grade & GPA calculator with weight-sum (`1.00`) and duplicate-ID stop gates.
  - `skills/blender-3d-modeling/scripts/bmesh_check.py` — Automated Blender `bmesh` manifold, zero-area face, loose-vertex, and scale auditor.
  - `premium-skills/security-auditor/scripts/secret_scan.py` — Offline CWE-mapped secret & dangerous-sink scanner with mandatory secret redaction.
  - `premium-skills/api-designer/scripts/lint_openapi.py` — OpenAPI 3.0/3.1 contract linter (operationIds, error envelopes, security schemes).
  - `premium-skills/accessibility-auditor/scripts/a11y_scan.py` — Static WCAG 2.2 AA HTML/CSS auditor.
- **Cryptographic Checksums & Reproducible Multi-File ZIPs**:
  - Generated `checksums.json` recording SHA-256 hashes of every `SKILL.md`, bundled script, and `.zip` archive across all 24 skills.
  - Upgraded `scripts/package_skills.py` to bundle full skill directories (`SKILL.md` + `scripts/`) deterministically with fixed ZIP timestamps and verify `checksums.json` parity.
- **Full Lifecycle Multi-Agent Skill Manager (`scripts/install_skills.py`)**:
  - Added `--remote` zero-clone installation with mandatory SHA-256 verification before writing any file.
  - Added `.cortex-lock.json` lockfile tracking plus `--status` (tamper/drift detection), `--check-updates`, `--upgrade`, and `--uninstall`.
- **Live A/B Benchmark Runner (`scripts/eval_skills.py --run`)**:
  - Expanded `evals/skill_evals.json` to 24 paired 100-point A/B rubrics covering all 24 skills.
  - Added zero-dependency `--run` harness supporting OpenAI, Anthropic, Gemini, and OpenAI-compatible endpoints with automatic Markdown scorecard generation.
- **Automated Test Suite (`tests/test_cortex_tooling.py`)**:
  - Added 9 end-to-end tests covering packaging, manifest validation, full installer lifecycle, SHA-256 remote tamper rejection, eval suite validation, and all runnable bundled helper scripts.

### Changed
- Bumped all 24 `SKILL.md` playbooks, `package.json`, and all 7 multi-agent manifests (`.claude-plugin/`, `.agents/plugins/`, `.cursor-plugin/`, `plugin.json`, `gemini-extension.json`) to `0.3.0`.
- Updated `index.html`, `README.md`, `AGENTS.md`, `GEMINI.md`, and `.github/workflows/ci.yml` for `v0.3.0`.

## [0.2.0] — 2026-11-23

### Added
- Native multi-agent support across 13 platforms (Claude Code, Claude Apps, OpenAI Codex CLI, ChatGPT, Gemini CLI, Cursor, GitHub Copilot & VS Code, OpenCode, OpenClaw, Goose, Aider, Cline, and Hermes Agent) via 7 plugin/extension manifests and `scripts/install_skills.py`.
- Redesigned interactive catalog website (`index.html`) with globally synced Agent Picker and Bash/PowerShell shell toggles.
- Upgraded all 20 skills to executable playbooks with stop gates, output contracts, and a 20-task 100-point A/B evaluation suite.

## [0.1.0] — 2026-11-01

### Added
- Initial release of 10 core and 10 extended Hermes Agent skills with ZIP packaging and CI validation.
