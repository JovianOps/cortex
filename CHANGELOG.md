# Changelog

All notable changes to **Cortex** are documented in this file. This project follows [Semantic Versioning](https://semver.org/).

## [3.0.0] — 2026-11-25

**Agent OS Release.** Cortex stops being only a catalog plus runtime and becomes a closed-loop platform: a **capability graph** that models how skills and role packs actually connect (`cortex graph`), **deterministic portable bundles** with per-file SHA-256 manifests for offline and air-gapped delivery (`cortex bundle`), and a **single release gate** that runs every check and can generate its own hardened CI and Git hooks (`cortex guard`). The MCP server grows to **11 tools and 39 resources**, Studio to **7 panels and 12 REST endpoints**, the docs to **9 guides**, and the whole catalog, manifests, ZIPs, checksums and site are graduated to **`3.0.0`**.

### Added
- **Capability Graph Engine (`scripts/cortex_graph.py`, CLI: `cortex graph`)**: Builds a deterministic directed graph from all 36 skills, 10 role packs, pack membership and `metadata.hermes.related_skills`. Reports nodes, typed edges, per-skill degree centrality (`hub_score`), the top hubs, orphaned skills, and dangling pack/related references. Emits JSON, **Mermaid**, or **Graphviz DOT**, with `--check` and `--strict` CI gates and `--out` file output.
- **Portable Bundle Engine (`scripts/cortex_bundle.py`, CLI: `cortex bundle`)**: Builds a single reproducible ZIP containing selected skills, a `bundle.json` manifest with a SHA-256 for every file, and an install README. Supports `--pack`, `--skill`, `--collection core|extended|all`, deterministic timestamps and sorted members, and offline `--verify` that fails on any missing, extra, or modified file.
- **Guard Gate & Enforcement Generator (`scripts/cortex_guard.py`, CLI: `cortex guard`)**: `guard check` runs packaging, skill validation, manifest validation, the 100-point audit, the capability graph, and the policy/SARIF scan in one pass with stable JSON output and `--only`/`--fail-fast`; `--print-workflow` / `--write-workflow` emit a hardened, SHA-pinned GitHub Actions workflow that passes `lint_actions.py`; `--print-pre-commit` / `guard install` write a Git pre-commit hook into versionable `.githooks/` and configure `core.hooksPath`.
- **MCP Expansion (`cortex mcp`)**: 3 new tools (`cortex_skill_graph`, `cortex_build_bundle`, `cortex_release_gate`) for **11 tools total**, plus the `cortex://graph` resource for **39 resources total**. Prompt surface remains 36.
- **Studio Expansion (`cortex studio`)**: New **07 / Capability Graph** panel with live JSON/Mermaid graph rendering and a one-click release gate, backed by `GET /api/graph` and `POST /api/guard` for **12 REST endpoints across 7 panels**, plus a graph-edge KPI.
- **Documentation**: Added [docs/graph-guide.md](docs/graph-guide.md), [docs/bundle-guide.md](docs/bundle-guide.md), and [docs/guard-guide.md](docs/guard-guide.md) with report schemas, exit codes, CI usage, and enforcement recipes.
- **Tests (`tests/test_cortex_v3.py`)**: End-to-end coverage for graph construction/checking/rendering, bundle determinism and tamper detection, guard check aggregation, workflow and hook generation, CLI dispatch, MCP tools/resources, and the new Studio endpoints.

### Changed
- Graduated all 36 `SKILL.md` playbooks, 9 multi-agent manifests, `package.json`, `packs.json`, `evals/skill_evals.json`, `checksums.json`, all 36 ZIPs, the CLI engines, and `index.html` to **`3.0.0`**.
- `scripts/bump_version.py` now also bumps the three new engines so future releases stay atomic.
- `cortex guard check` is the documented pre-release and pre-commit command; `cortex verify` remains the fast integrity-only check.
- `web-scraper` now ships in the `python-pro` role pack, so every skill belongs to at least one pack (no graph orphans); the guard's graph gate runs `--strict` to keep it that way, and `index.html` reads pack sizes from `packs.json` instead of assuming six skills per pack.

## [2.0.1] — 2026-11-25

**Release Hardening, npm Publish Fix, CLI/MCP Parity & Security Remediation.** Fixes npm tag matching for uppercase/lowercase tags, achieves 100% `--json` and `opencode` parity across CLI/MCP/Studio/site, adds root `.cortex-policy.json`, hardens remote URL/path-traversal/CSRF checks, and eliminates all hardcoded demo secret/PII literal fixtures across the codebase.

### Fixed
- **npm Release Workflow (`.github/workflows/publish-npm.yml` & `ci.yml`)**: Fixed release tag version comparison (`${GITHUB_REF_NAME#[vV]}`) so both `v*` and `V*` tags verify cleanly against `package.json`, added `ruff` + `cortex scan` + `cortex audit --json` to smoke tests, and fixed CI eval count copy (`24-task` → `36-task`).
- **Full-Codebase Secret, Key, PII & DOM Sink Remediation**:
  - Replaced literal demo token/key/SSN/email fixtures in `evals/skill_evals.json`, `premium-skills/db-optimizer/SKILL.md`, `index.html`, and `tests/test_cortex_v2.py` with non-matching placeholder patterns or runtime-constructed test strings (`0` literal credential or PII findings across the repository).
  - Hardened `scripts/install_skills.py` (`https://` scheme enforcement, `--repo`/`--ref` validation, slug regex, and `.resolve().relative_to()` path-traversal confinement on install/uninstall), `scripts/eval_skills.py` (`https://`/loopback URL scheme check), `scripts/cortex_studio.py` (`1 MiB` request body cap and `Origin` CSRF validation on `POST`), and `index.html` (`escapeHtml()` across catalog, packs, platforms, and inspector DOM templates).
- **CLI, MCP, Studio & Site Parity**:
  - Added `--json` parity across `cortex scan . --json` (plus `--init-policy`), `cortex audit --json`, `cortex doctor --json`, `cortex new --json`, `grade_calc.py --json`, `memory_store.py --json`, and `bmesh_check.py --json`, plus fixed `cortex_run_verifier` invocation for `memory-manager`.
  - Added `opencode` target parity to `scripts/cortex_compile.py` (`AGENTS.md`), `scripts/cortex_studio.py` compiler UI, `scripts/cortex_mcp.py`, and `index.html` MCP simulator; corrected `index.html` manifest count (`11` → `9`) and npm verify commands.
  - Added `IGNORE_DIRS` and `.github/skills` pruning to `lint_terraform.py`, `lint_k8s.py`, `lint_graphql.py`, and `audit_finops.py` so installed skill trees are skipped cleanly.
- **Repository Scanner Policy (`.cortex-policy.json`)**: Added starter root policy aligned with `schemas/policy.schema.json` and wired `cortex scan . --format sarif --fail-on high` into `.github/workflows/ci.yml`.

## [2.0.0] — 2026-11-24

**Next-Generation Multi-Agent Platform Release.** Transforms Cortex from a static skill repository into a complete zero-dependency multi-agent engineering runtime — introducing a native MCP 2025-03-26 JSON-RPC stdio server (`cortex mcp`), Local Light/Dark Swiss Web Workbench (`cortex studio`), Universal Agent Rule Compiler (`cortex compile`), Unified Policy & SARIF 2.1.0 / JUnit XML Scanner (`cortex scan`), 12 brand-new flagship skills (24 → 36 skills & 36 bundled Python verifiers), 4 new role packs (6 → 10 packs), and a 6-guide `docs/` engineering handbook.

### Added
- **Native MCP 2025-03-26 Server (`scripts/cortex_mcp.py`, CLI: `cortex mcp`)**:
  - Zero-dependency JSON-RPC 2.0 stdio server supporting both `Content-Length` framed and newline-delimited messages.
  - Exposes 8 workspace-confined MCP Tools (`cortex_list_skills`, `cortex_get_skill`, `cortex_search_skills`, `cortex_list_packs`, `cortex_verify_workspace`, `cortex_run_verifier`, `cortex_compile_rules`, `cortex_scan_repo`), 38 MCP Resources (`cortex://skills/<slug>`, `cortex://packs`, `cortex://checksums`), and 36 invocable MCP Prompts (`cortex/<slug>`).
  - Includes `--print-config <vscode|claude-code|cursor|codex|windsurf>` for instant client setup.
- **Cortex Studio Local Web Workbench (`scripts/cortex_studio.py`, CLI: `cortex studio`)**:
  - Zero-dependency Light/Dark Swiss local web UI + 10 REST API endpoints (`/api/overview`, `/api/skills`, `/api/skills/<slug>`, `/api/packs`, `/api/verify`, `/api/mcp-config`, `/api/run-tool`, `/api/compile`, `/api/scan`).
- **Universal Agent Rule Compiler (`scripts/cortex_compile.py`, CLI: `cortex compile`)**:
  - Deterministically compiles `SKILL.md` playbooks into 7 native IDE/agent formats: Cursor (`.cursor/rules/*.mdc`), VS Code (`.github/instructions/*.instructions.md`), Windsurf (`.windsurf/rules/*.md`), Cline (`.clinerules/*.md`), `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md`, with `--dry-run`, `--check` CI drift verification, and SHA-256 provenance comments.
- **Unified Policy & SARIF 2.1.0 Scanner (`scripts/cortex_scan.py`, CLI: `cortex scan`)**:
  - Runs 14 bundled verifiers in a single pass with `.cortex-policy.json` (`schemas/policy.schema.json`), `--fail-on` severity gates, and Table, JSON, SARIF 2.1.0 (GitHub Code Scanning), and JUnit XML outputs.
- **12 New Flagship Extended Skills (24 → 36 Skills, 36/36 Bundled Python Verifiers, 36 Eval Rubrics)**:
  - `kubernetes-architect` (`lint_k8s.py`)
  - `typescript-architect` (`lint_ts.py`)
  - `rust-systems-engineer` (`lint_rust.py`)
  - `go-backend-engineer` (`lint_go.py`)
  - `graphql-architect` (`lint_graphql.py`)
  - `llm-security-auditor` (`audit_prompts.py`)
  - `supply-chain-sbom` (`audit_sbom.py`)
  - `privacy-compliance-auditor` (`scan_pii.py`)
  - `finops-cost-optimizer` (`audit_finops.py`)
  - `chaos-resilience-engineer` (`audit_resilience.py`)
  - `architecture-decision-records` (`check_adrs.py`)
  - `git-history-surgeon` (`audit_git_hygiene.py`)
- **4 New Curated Role-Based Skill Packs (6 → 10 Packs in `packs.json`)**: `cloud-native`, `ai-red-team`, `polyglot-systems`, and `platform-architecture`.
- **Comprehensive Reference Docs (`docs/`)**: `architecture.md`, `mcp-guide.md`, `studio-guide.md`, `compiler-guide.md`, `policy-and-sarif.md`, and `skill-authoring.md`.
- **Expanded Automated Tests (`tests/test_cortex_v2.py`)**: End-to-end tests for MCP JSON-RPC protocol, Studio HTTP server API, Universal Compiler (all 7 targets + drift checks), Unified Policy/SARIF/JUnit Scanner, and all 12 new bundled helper scripts.

### Changed
- Upgraded `scripts/bump_version.py` to regenerate the entire `SKILLS` and `PACKS` arrays in `index.html` atomically from disk, `checksums.json`, and `packs.json`.
- Pinned `.github/workflows/dependency-review.yml` to 40-character commit SHAs (`actions/checkout`, `actions/dependency-review-action`) so all 3 workflows pass `lint_actions.py`.
- Graduated all 36 skills, 36 deterministic multi-file ZIPs (72 verified files in `checksums.json`), all 9 multi-agent manifests, `package.json`, `packs.json`, `evals/skill_evals.json`, `index.html`, and CLI engines to **`2.0.0`**.

## [1.0.0] — 2026-11-24

**First Stable General Availability (GA) release of Cortex.** Graduates Cortex out of `0.x` beta with 100% bundled executable tool coverage across all 24 skills, a complete `cortex` CLI (`init`, `info`, `verify`), formal `1.0.0` JSON Schemas, atomic release tooling, first-class Visual Studio Code support, a zero-dependency Light Swiss editorial site, and SHA-pinned cross-platform CI (Linux, macOS, Windows).

### Added
- **24/24 Bundled Zero-Dependency Python Helper Scripts (100% Skill Coverage)**:
  - `premium-skills/terraform-generator/scripts/lint_terraform.py` — Audits `.tf` files for unpinned provider versions, `0.0.0.0/0` admin ports, hardcoded secrets, disabled encryption, and unpinned Git modules.
  - `premium-skills/db-optimizer/scripts/lint_sql.py` — Flags `SELECT *`, `DELETE`/`UPDATE` without `WHERE`, leading-wildcard `LIKE`, deep `OFFSET`, and `ORDER BY RANDOM()`.
  - `premium-skills/observability-setup/scripts/check_slo.py` — Computes exact `Decimal` SLO error budgets, multi-window burn-rate thresholds, and detects high-cardinality metric labels.
  - `premium-skills/incident-response/scripts/incident_timeline.py` — Validates monotonic UTC ISO-8601 timelines, corrective action owners/due dates, and computes MTTD/MTTR.
  - `skills/code-review-assistant/scripts/diff_review.py` — Pre-reviews unified diffs for debug leftovers (`console.log`, `debugger`, `breakpoint`), TODOs, and source edits without companion tests.
  - `skills/anti-hallucination/scripts/verify_claims.py` — Offline claim verifier checking that backticked relative file paths actually exist in the repository.
  - `skills/python-coding-assistant/scripts/check_python_ast.py` — AST auditor for mutable default arguments, bare `except:`, and missing public return annotations.
  - `skills/testing-automation/scripts/check_test_coverage_map.py` — Detects assertion-free Python test functions via AST.
  - `premium-skills/unit-test-generator/scripts/test_skeleton.py` — Emits AST-derived branch and edge-case unit test checklists for every public Python function.
  - `skills/academic-assistant/scripts/citation_check.py` — Verifies numeric inline citations `[1]` match `## References`.
  - `skills/web-scraper/scripts/check_robots.py` — Offline `robots.txt` allow/disallow and crawl-delay checker.
  - `premium-skills/code-migration/scripts/migration_inventory.py` — Generates deterministic file, LOC, and dependency-manifest inventories.
  - `premium-skills/performance-profiler/scripts/bench_compare.py` — Compares baseline vs. candidate p50/p95/p99 latency samples against regression gates.
  - `premium-skills/refactoring-assistant/scripts/complexity_scan.py` — Finds Python AST cyclomatic complexity and function-length hotspots.
- **Production `cortex` CLI Enhancements (`scripts/cortex.py`)**:
  - `cortex init`: Auto-detects repository stack signals and installed AI agents, installs the matching role pack with SHA-256 checks, and optionally configures `.vscode/settings.json` / `.aider.conf.yml`.
  - `cortex info <slug> [--json]`: Inspects any skill's metadata, bundled script, role packs, SHA-256 digests, and install command.
  - `cortex verify [--json]`: Machine-readable offline verification of checksums/ZIPs, 9 manifests, eval/audit scores, and project lockfiles.
  - `cortex --version` / `-V`: Prints `cortex 1.0.0`.
- **Stable `1.0.0` Schemas & Atomic Release Tooling**:
  - Added `schemas/checksums.schema.json`, `schemas/packs.schema.json`, and `schemas/cortex-lock.schema.json` (validated in `scripts/validate_manifests.py` and shipped in the npm tarball).
  - Added `scripts/bump_version.py <version>` to atomically bump all 24 `SKILL.md` files, all 9 manifests, `package.json`, `packs.json`, `evals/skill_evals.json`, CLI scripts, docs, deterministic ZIPs, `checksums.json`, and `index.html`.
- **Cross-Platform CI & Open-Source Governance**:
  - Added `Cross-Platform CLI` matrix (`ubuntu-latest`, `macos-latest`, `windows-latest`) to `.github/workflows/ci.yml`.
  - Added `SECURITY.md`, `CONTRIBUTING.md`, `.github/PULL_REQUEST_TEMPLATE.md`, and `.github/ISSUE_TEMPLATE/` (`bug_report.yml`, `new_skill.yml`).

### Changed
- Graduated all 24 `SKILL.md` playbooks, 24 multi-file ZIP archives (every ZIP now bundles both `SKILL.md` and its Python helper script), `checksums.json` (48 verified files), all 9 multi-agent manifests, `package.json`, `packs.json`, `index.html`, and docs to **`1.0.0`**.

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
