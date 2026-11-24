<div align="center">
  <a href="https://github.com/JovianOps/cortex">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg" />
      <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg" />
      <img alt="Cortex — Modular Agent Skills" src="assets/banner-light.svg" width="100%" />
    </picture>
  </a>

  <br />
  <br />

  <p>
    <a href="https://github.com/JovianOps/cortex/actions/workflows/ci.yml">
      <img src="https://github.com/JovianOps/cortex/actions/workflows/ci.yml/badge.svg" alt="CI Status" />
    </a>
    <a href="https://www.npmjs.com/package/@jovianops/cortex">
      <img src="https://img.shields.io/npm/v/%40jovianops%2Fcortex?style=flat&color=CB3837&label=npm" alt="npm @jovianops/cortex" />
    </a>
    <a href="https://www.npmjs.com/package/@jovianops/cortex">
      <img src="https://img.shields.io/npm/dt/%40jovianops%2Fcortex?style=flat&color=CB3837&label=npm%20downloads" alt="npm downloads" />
    </a>
    <a href="CHANGELOG.md">
      <img src="https://img.shields.io/badge/release-v2.0.0-EA580C?style=flat" alt="Release v2.0.0" />
    </a>
    <a href="#supported-agents--platforms">
      <img src="https://img.shields.io/badge/standard-SKILL.md%20%2B%20MCP-2C2B28?style=flat" alt="SKILL.md and MCP Standard" />
    </a>
    <a href="#core-skills">
      <img src="https://img.shields.io/badge/core_skills-10-2C2B28?style=flat" alt="10 Core Skills" />
    </a>
    <a href="#extended-skills">
      <img src="https://img.shields.io/badge/extended_skills-26-B8421B?style=flat" alt="26 Extended Skills" />
    </a>
    <a href="#verify-authenticity-sha-256--provenance">
      <img src="https://img.shields.io/badge/integrity-SHA--256%20Verified-16A34A?style=flat" alt="SHA-256 Verified" />
    </a>
    <a href="LICENSE">
      <img src="https://img.shields.io/badge/license-MIT-5C5A52?style=flat" alt="MIT License" />
    </a>
  </p>

  <p>
    <a href="#whats-new-in-v200">What's New in v2.0.0</a>
    &nbsp;&middot;&nbsp;
    <a href="#quick-start">Quick Start</a>
    &nbsp;&middot;&nbsp;
    <a href="docs/mcp-guide.md">MCP Server</a>
    &nbsp;&middot;&nbsp;
    <a href="docs/studio-guide.md">Studio UI</a>
    &nbsp;&middot;&nbsp;
    <a href="docs/compiler-guide.md">Rule Compiler</a>
    &nbsp;&middot;&nbsp;
    <a href="docs/policy-and-sarif.md">SARIF Scanner</a>
    &nbsp;&middot;&nbsp;
    <a href="#verify-authenticity-sha-256--provenance">Verify SHA-256</a>
    &nbsp;&middot;&nbsp;
    <a href="CHANGELOG.md">Changelog</a>
  </p>
</div>

---

**Cortex `v2.0.0`** is the next-generation, zero-dependency AI-agent skill & runtime platform shipping **36 modular, deterministic Agent Skills (`SKILL.md`)** across **10 core skills** (`skills/`) and **26 extended engineering skills** (`premium-skills/`), with **36/36 bundled zero-dependency Python verifiers (100% coverage)**, a **native MCP 2025-03-26 JSON-RPC stdio server (`cortex mcp`)**, a **local Light/Dark Swiss Web Workbench (`cortex studio`)**, a **Universal Agent Rule Compiler (`cortex compile`)**, a **Unified Policy & SARIF 2.1.0 / JUnit XML Scanner (`cortex scan`)**, **10 curated Role-Based Skill Packs** (`packs.json`), **4 stable JSON Schemas (`schemas/`)**, **SHA-256 integrity verification (`checksums.json`, 72 files)**, and a **36-task live A/B benchmark harness**.

Built on the open **`SKILL.md`** and **MCP** standards, Cortex works natively across **Visual Studio Code**, **GitHub Copilot**, **Claude** (Claude Code & Claude apps), **OpenAI** (Codex CLI & ChatGPT), **Gemini CLI**, **Cursor**, **Windsurf**, **OpenCode**, **OpenClaw**, **Goose**, **Aider**, **Cline**, and **Hermes Agent**.

## What's New in `v2.0.0`

- **Native Model Context Protocol Server (`cortex mcp`)**: Zero-dependency MCP 2025-03-26 JSON-RPC 2.0 stdio server exposing **8 tools**, **38 resources** (`cortex://skills/<slug>`, `cortex://packs`, `cortex://checksums`), and **36 invocable prompts** (`cortex/<slug>`), plus `--print-config <vscode|claude-code|cursor|codex|windsurf>`. See [docs/mcp-guide.md](docs/mcp-guide.md).
- **Cortex Studio Local Web Workbench (`cortex studio`)**: Zero-dependency Light/Dark Swiss local web UI & 10-endpoint REST API for inspecting all 36 skills and scripts, running any bundled verifier live against your workspace, compiling native agent rules, running SARIF scans, and generating MCP configs. See [docs/studio-guide.md](docs/studio-guide.md).
- **Universal Agent Rule Compiler (`cortex compile`)**: Deterministically transpiles `SKILL.md` playbooks into **7 native IDE/agent formats** — Cursor (`.cursor/rules/*.mdc`), VS Code (`.github/instructions/*.instructions.md`), Windsurf (`.windsurf/rules/*.md`), Cline (`.clinerules/*.md`), `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md` — with `--check` CI drift verification. See [docs/compiler-guide.md](docs/compiler-guide.md).
- **Unified Policy & SARIF 2.1.0 Scanner (`cortex scan`)**: Orchestrates 14 bundled verifiers in one pass with `.cortex-policy.json` (`schemas/policy.schema.json`), severity gates (`--fail-on`), **SARIF 2.1.0** (GitHub Code Scanning), and **JUnit XML** output. See [docs/policy-and-sarif.md](docs/policy-and-sarif.md).
- **24 → 36 Skills, 36/36 Bundled Python Verifiers & 6 → 10 Role Packs**: Added 12 flagship extended skills (`kubernetes-architect`, `typescript-architect`, `rust-systems-engineer`, `go-backend-engineer`, `graphql-architect`, `llm-security-auditor`, `supply-chain-sbom`, `privacy-compliance-auditor`, `finops-cost-optimizer`, `chaos-resilience-engineer`, `architecture-decision-records`, `git-history-surgeon`) — all scoring **100.0/100** with paired 100-point A/B eval rubrics and 4 new packs (`cloud-native`, `ai-red-team`, `polyglot-systems`, `platform-architecture`).
- **Complete Technical Documentation (`docs/`)**: Added [architecture.md](docs/architecture.md), [mcp-guide.md](docs/mcp-guide.md), [studio-guide.md](docs/studio-guide.md), [compiler-guide.md](docs/compiler-guide.md), [policy-and-sarif.md](docs/policy-and-sarif.md), and [skill-authoring.md](docs/skill-authoring.md).

## Quick Start

Install into any agent in one command using the **Cortex CLI**, universal **Agent Skills CLI (`npx skills`)**, zero-clone **Python `--remote`** (with SHA-256 verification), or your agent's native plugin marketplace / tap:

```bash
# Cortex Unified CLI via npm (no git clone needed — detect agents, verify SHA-256, install role packs)
npx @jovianops/cortex detect
npx @jovianops/cortex doctor
npx @jovianops/cortex packs
npx @jovianops/cortex install --agent claude-code --pack fullstack
npx @jovianops/cortex new my-new-skill --with-script

# Or install globally: npm install -g @jovianops/cortex  (then run `cortex detect`, `cortex packs`, ...)

# Universal Agent Skills CLI (Claude Code, Codex, Gemini CLI, Cursor, Copilot, OpenCode, OpenClaw, Goose, Cline...)
npx skills add JovianOps/cortex

# Install a single skill globally for specific agents
npx skills add JovianOps/cortex --skill security-auditor -a claude-code -a cursor -g
```

```bash
# Zero-clone Python remote install with a Role Pack (no git clone, no Node.js — verifies SHA-256 via checksums.json)
curl -fsSL https://raw.githubusercontent.com/JovianOps/cortex/main/scripts/install_skills.py | python3 - --remote --agent claude-code --pack fullstack
```

```powershell
# Windows PowerShell zero-clone remote install (SHA-256 verified)
irm https://raw.githubusercontent.com/JovianOps/cortex/main/scripts/install_skills.py | python - --remote --agent claude-code --pack fullstack
```

```bash
# Hermes Agent native tap
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/skills/academic-assistant --yes
```

> [!TIP]
> Prefer a visual picker? Open [`index.html`](index.html) locally or via GitHub Pages to filter all **24 skills**, pick your target agent, and assemble a custom Bash or PowerShell install command with one click.

## Supported Agents & Platforms

Cortex ships 9 validated native manifests, a zero-dependency multi-agent manager, and upload-ready ZIPs (`<slug>/SKILL.md` + bundled `scripts/`) so every major AI coding agent, IDE, and chat app works out of the box:

| Platform | Native Manifest / Format | Fast Install / Setup | Local Skills Directory |
| :--- | :--- | :--- | :--- |
| **Claude Code** | `.claude-plugin/marketplace.json` | `/plugin marketplace add JovianOps/cortex` then `/plugin install cortex@cortex` — or `npx skills add JovianOps/cortex -a claude-code` | `~/.claude/skills/` · `.claude/skills/` |
| **Claude Apps** (claude.ai & Desktop) | Multi-file `<slug>/SKILL.md` ZIPs (`zips/`, `premium-zips/`) | Enable **Code execution** in **Settings → Capabilities**, then **Customize → Skills → Add → Upload skill** and upload any ZIP | Account-synced (web, desktop & mobile) |
| **OpenAI Codex CLI** | `.agents/plugins/marketplace.json` + `plugin.json` | `npx skills add JovianOps/cortex -a codex` or import `JovianOps/cortex` via Codex plugin marketplace | `~/.codex/skills/` · `.agents/skills/` |
| **ChatGPT** (Web & Desktop) | `SKILL.md` playbooks & `.agents/plugins/marketplace.json` | Upload any `SKILL.md` or ZIP to **ChatGPT Projects** (Project files / instructions) or **Custom GPTs**, or load via ChatGPT Desktop plugins | Project / Custom GPT knowledge |
| **Gemini CLI** | `gemini-extension.json` + `GEMINI.md` | `gemini extensions install https://github.com/JovianOps/cortex` or `npx skills add JovianOps/cortex -a gemini-cli` | `~/.gemini/skills/` · `.gemini/skills/` |
| **Cursor** | `.cursor-plugin/marketplace.json` + `plugin.json` | Import `https://github.com/JovianOps/cortex` in **Customize → Plugins**, or `npx skills add JovianOps/cortex -a cursor` | `~/.cursor/skills/` · `.cursor/skills/` |
| **Visual Studio Code** | `.github/plugin/marketplace.json` + `.github/plugin.json` + `.github/copilot-instructions.md` | Add `"JovianOps/cortex"` to `chat.plugins.marketplaces` (with `chat.plugins.enabled: true`) & browse `@agentPlugins`, or run `npx @jovianops/cortex install --agent vscode --pack fullstack --scope project --write-vscode-settings` | `~/.copilot/skills/` · `.github/skills/` |
| **GitHub Copilot** | `.github/plugin.json` + `plugin.json` | `npx @jovianops/cortex install --agent copilot --pack fullstack --scope project` or `npx skills add JovianOps/cortex -a github-copilot` | `~/.copilot/skills/` · `.github/skills/` |
| **OpenCode** | `SKILL.md` + `AGENTS.md` | `npx skills add JovianOps/cortex -a opencode` or `python scripts/install_skills.py --agent opencode` | `~/.config/opencode/skills/` · `.opencode/skills/` |
| **OpenClaw** | `SKILL.md` + ZIP packages | `npx skills add JovianOps/cortex -a openclaw`, `python scripts/install_skills.py --agent openclaw`, or unzip `zips/*.zip` into `~/.openclaw/skills/` | `~/.openclaw/skills/` · `.openclaw/skills/` |
| **Goose** | `SKILL.md` | `npx skills add JovianOps/cortex -a goose` or `python scripts/install_skills.py --agent goose` | `~/.config/goose/skills/` · `.goose/skills/` |
| **Aider** | `SKILL.md` + `--read` / `.aider.conf.yml` | `python scripts/install_skills.py --agent aider --scope project --write-aider-conf` or `aider --read skills/<slug>/SKILL.md` | `~/.aider/skills/` · `.aider/skills/` |
| **Cline** | `SKILL.md` | `npx skills add JovianOps/cortex -a cline` or `python scripts/install_skills.py --agent cline --scope project` | `~/.cline/skills/` · `.cline/skills/` |
| **Hermes Agent** | Native Cortex tap | `hermes skills tap add JovianOps/cortex` then `hermes skills install JovianOps/cortex/<dir>/<slug> --yes` | Managed by `hermes skills` |

## Core Skills

Ten foundational skills located in [`skills/`](skills/) with deterministic ZIP archives in [`zips/`](zips/).

| Skill | Focus | Description | Bundled Tool | Spec | ZIP |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **[academic-assistant](skills/academic-assistant)** | Academic & Multi-Domain | Orchestrate grading, coding, and 3D academic workflows | — | [`SKILL.md`](skills/academic-assistant/SKILL.md) | [`.zip`](zips/academic-assistant.zip) |
| **[anti-hallucination](skills/anti-hallucination)** | Verification | Verify AI claims and code with deterministic audit gates | — | [`SKILL.md`](skills/anti-hallucination/SKILL.md) | [`.zip`](zips/anti-hallucination.zip) |
| **[blender-3d-modeling](skills/blender-3d-modeling)** | 3D & Graphics | Build and validate Blender 3D meshes with `bmesh` checks | [`bmesh_check.py`](skills/blender-3d-modeling/scripts/bmesh_check.py) | [`SKILL.md`](skills/blender-3d-modeling/SKILL.md) | [`.zip`](zips/blender-3d-modeling.zip) |
| **[code-review-assistant](skills/code-review-assistant)** | Code Quality | Run evidence-backed code reviews with severity rubrics | — | [`SKILL.md`](skills/code-review-assistant/SKILL.md) | [`.zip`](zips/code-review-assistant.zip) |
| **[college-report-card](skills/college-report-card)** | Education | Generate exact report cards using `Decimal` grade scripts | [`grade_calc.py`](skills/college-report-card/scripts/grade_calc.py) | [`SKILL.md`](skills/college-report-card/SKILL.md) | [`.zip`](zips/college-report-card.zip) |
| **[documentation-generator](skills/documentation-generator)** | Documentation | Generate code-verified docs, API specs, and diagrams | — | [`SKILL.md`](skills/documentation-generator/SKILL.md) | [`.zip`](zips/documentation-generator.zip) |
| **[memory-manager](skills/memory-manager)** | Context | Persist versioned session memory with staleness checks | — | [`SKILL.md`](skills/memory-manager/SKILL.md) | [`.zip`](zips/memory-manager.zip) |
| **[python-coding-assistant](skills/python-coding-assistant)** | Python | Write typed, linted, and tested Python code reliably | — | [`SKILL.md`](skills/python-coding-assistant/SKILL.md) | [`.zip`](zips/python-coding-assistant.zip) |
| **[testing-automation](skills/testing-automation)** | Testing | Build branch-tested `pytest` suites with CI coverage gates | — | [`SKILL.md`](skills/testing-automation/SKILL.md) | [`.zip`](zips/testing-automation.zip) |
| **[web-scraper](skills/web-scraper)** | Data Extraction | Scrape web data politely with strict schema validation | — | [`SKILL.md`](skills/web-scraper/SKILL.md) | [`.zip`](zips/web-scraper.zip) |

## Extended Skills

Fourteen specialized software engineering, SRE, security, and accessibility skills located in [`premium-skills/`](premium-skills/) with deterministic ZIP archives in [`premium-zips/`](premium-zips/).

| Skill | Focus | Description | Bundled Tool | Spec | ZIP |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **[accessibility-auditor](premium-skills/accessibility-auditor)** | Accessibility *(New)* | Audit HTML/UI for WCAG 2.2 AA flaws with exact code fixes | [`a11y_scan.py`](premium-skills/accessibility-auditor/scripts/a11y_scan.py) | [`SKILL.md`](premium-skills/accessibility-auditor/SKILL.md) | [`.zip`](premium-zips/accessibility-auditor.zip) |
| **[api-designer](premium-skills/api-designer)** | Architecture | Design strict OpenAPI and GraphQL specs with contracts | [`lint_openapi.py`](premium-skills/api-designer/scripts/lint_openapi.py) | [`SKILL.md`](premium-skills/api-designer/SKILL.md) | [`.zip`](premium-zips/api-designer.zip) |
| **[code-migration](premium-skills/code-migration)** | Modernization | Migrate languages and frameworks with parity tests | — | [`SKILL.md`](premium-skills/code-migration/SKILL.md) | [`.zip`](premium-zips/code-migration.zip) |
| **[db-optimizer](premium-skills/db-optimizer)** | Databases | Optimize SQL queries and indexes using `EXPLAIN` plans | — | [`SKILL.md`](premium-skills/db-optimizer/SKILL.md) | [`.zip`](premium-zips/db-optimizer.zip) |
| **[devops-pipeline](premium-skills/devops-pipeline)** | CI/CD | Build hardened, SHA-pinned CI/CD pipelines across tools | — | [`SKILL.md`](premium-skills/devops-pipeline/SKILL.md) | [`.zip`](premium-zips/devops-pipeline.zip) |
| **[docker-generator](premium-skills/docker-generator)** | Containers | Generate hardened multi-stage Docker and Compose setups | — | [`SKILL.md`](premium-skills/docker-generator/SKILL.md) | [`.zip`](premium-zips/docker-generator.zip) |
| **[incident-response](premium-skills/incident-response)** | SRE / Ops *(New)* | Triage outages, contain blast radius, and write postmortems | — | [`SKILL.md`](premium-skills/incident-response/SKILL.md) | [`.zip`](premium-zips/incident-response.zip) |
| **[observability-setup](premium-skills/observability-setup)** | Telemetry *(New)* | Add structured logs, OTel traces, SLOs, and clean alerts | — | [`SKILL.md`](premium-skills/observability-setup/SKILL.md) | [`.zip`](premium-zips/observability-setup.zip) |
| **[performance-profiler](premium-skills/performance-profiler)** | Performance | Profile CPU, memory, and I/O with measured benchmarks | — | [`SKILL.md`](premium-skills/performance-profiler/SKILL.md) | [`.zip`](premium-zips/performance-profiler.zip) |
| **[refactoring-assistant](premium-skills/refactoring-assistant)** | Maintainability | Refactor complex code safely with parity verification | — | [`SKILL.md`](premium-skills/refactoring-assistant/SKILL.md) | [`.zip`](premium-zips/refactoring-assistant.zip) |
| **[release-engineering](premium-skills/release-engineering)** | Releases *(New)* | Cut SemVer releases with changelogs, checksums, and gates | — | [`SKILL.md`](premium-skills/release-engineering/SKILL.md) | [`.zip`](premium-zips/release-engineering.zip) |
| **[security-auditor](premium-skills/security-auditor)** | Security | Audit code for OWASP flaws, secrets, and CWE findings | [`secret_scan.py`](premium-skills/security-auditor/scripts/secret_scan.py) | [`SKILL.md`](premium-skills/security-auditor/SKILL.md) | [`.zip`](premium-zips/security-auditor.zip) |
| **[terraform-generator](premium-skills/terraform-generator)** | Infrastructure | Generate hardened, validated Terraform and OpenTofu IaC | — | [`SKILL.md`](premium-skills/terraform-generator/SKILL.md) | [`.zip`](premium-zips/terraform-generator.zip) |
| **[unit-test-generator](premium-skills/unit-test-generator)** | Testing | Generate branch-covering unit tests from source code | — | [`SKILL.md`](premium-skills/unit-test-generator/SKILL.md) | [`.zip`](premium-zips/unit-test-generator.zip) |

## Installation

### 1. Universal CLI (`npx skills`) — Works Across 40+ Agents

```bash
# Interactive picker (auto-detects your installed agents)
npx skills add JovianOps/cortex

# Install all 24 skills globally across every detected agent
npx skills add JovianOps/cortex --all -g -y

# Install specific skills for specific agents
npx skills add JovianOps/cortex --skill security-auditor --skill incident-response -a claude-code -a cursor -a codex -y

# Target other agents explicitly
npx skills add JovianOps/cortex -a gemini-cli -g          # Gemini CLI
npx skills add JovianOps/cortex -a github-copilot        # GitHub Copilot & VS Code (.github/skills/)
npx skills add JovianOps/cortex -a opencode -g           # OpenCode
npx skills add JovianOps/cortex -a openclaw -g           # OpenClaw
npx skills add JovianOps/cortex -a goose -g              # Goose
npx skills add JovianOps/cortex -a cline                 # Cline (.cline/skills/)
```

### 2. Full-Lifecycle Multi-Agent Manager (`scripts/install_skills.py` — Zero Dependencies)

Works on **Linux, macOS, and Windows** with Python 3 stdlib only — copies both `SKILL.md` AND bundled `scripts/`, verifies **SHA-256 checksums** in `--remote` mode, and manages `.cortex-lock.json`:

```bash
# List all supported agents and all 24 skills (showing bundled scripts)
python scripts/install_skills.py --list

# Zero-clone remote install with SHA-256 verification (no git clone required)
python scripts/install_skills.py --remote --agent claude-code --agent cursor --collection all

# Verify local files against .cortex-lock.json SHA-256 hashes (detects tampering/drift)
python scripts/install_skills.py --agent claude-code --status

# Check for newer releases and upgrade installed skills cleanly
python scripts/install_skills.py --remote --agent claude-code --check-updates
python scripts/install_skills.py --remote --agent claude-code --upgrade

# Uninstall a specific skill or all Cortex skills cleanly
python scripts/install_skills.py --agent claude-code --uninstall --skill web-scraper

# Project-scoped Aider install + auto-update .aider.conf.yml
python scripts/install_skills.py --agent aider --skill security-auditor --skill code-review-assistant --scope project --write-aider-conf
```

### 3. Platform-Specific Marketplaces & Apps

<details>
<summary><strong>Claude (Claude Code & Claude Apps — claude.ai / Desktop)</strong></summary>

**Claude Code (Plugin Marketplace):**

```text
/plugin marketplace add JovianOps/cortex
/plugin install cortex@cortex
# Or install a single collection:
/plugin install cortex-core@cortex
/plugin install cortex-extended@cortex
```

**Claude Apps (claude.ai & Claude Desktop):**

1. Download any skill ZIP from [`zips/`](zips/) or [`premium-zips/`](premium-zips/) (each archive contains `<slug>/SKILL.md` plus any bundled `scripts/`).
2. Open **Settings → Capabilities** and enable **Code execution / Create and edit files**.
3. Open **Customize → Skills → Add → Upload skill** and select the downloaded `.zip` file.

</details>

<details>
<summary><strong>OpenAI (Codex CLI & ChatGPT)</strong></summary>

- **Codex CLI**: `npx skills add JovianOps/cortex -a codex -g` or `python scripts/install_skills.py --remote --agent codex`. Codex CLI and ChatGPT Desktop also read `.agents/plugins/marketplace.json` and `plugin.json`.
- **ChatGPT (Web & Desktop Projects / Custom GPTs)**: Upload any `SKILL.md` or `.zip` into **ChatGPT Projects → Files** or **Custom GPTs → Knowledge**.

</details>

<details>
<summary><strong>Visual Studio Code (Native Chat Plugin Marketplace & CLI)</strong></summary>

1. **Native VS Code Chat Plugin Marketplace** (`.github/plugin/marketplace.json`):
   Add to your VS Code User `settings.json`, then search `@agentPlugins` in the Extensions view (or run **Chat: Plugins**):

   ```json
   {
     "chat.plugins.enabled": true,
     "chat.plugins.marketplaces": ["JovianOps/cortex"]
   }
   ```

2. **CLI Install into `.github/skills/` + workspace settings**:

   ```bash
   npx @jovianops/cortex install --agent vscode --pack fullstack --scope project --write-vscode-settings
   ```

   This writes SHA-256 verified skills into `.github/skills/`, records `.cortex-lock.json`, and ensures `"chat.useAgentSkills": true` in `.vscode/settings.json`.

3. **Workspace Tasks**: Opening this repository in VS Code provides ready-to-run Command Palette tasks (`.vscode/tasks.json`) for `Cortex: Doctor`, `Cortex: Run Full Validation & Tests`, `Cortex: Repackage ZIPs & Checksums`, `Cortex: Verify Website`, and `Cortex: Audit GitHub Actions Workflows`.

</details>

<details>
<summary><strong>Gemini CLI, Cursor & GitHub Copilot</strong></summary>

- **Gemini CLI**: `gemini extensions install https://github.com/JovianOps/cortex` or `npx skills add JovianOps/cortex -a gemini-cli -g`.
- **Cursor**: Import `https://github.com/JovianOps/cortex` in **Customize → Plugins**, or run `npx skills add JovianOps/cortex -a cursor -g`.
- **GitHub Copilot**: `npx @jovianops/cortex install --agent copilot --pack fullstack --scope project` or `npx skills add JovianOps/cortex -a github-copilot`.

</details>

<details>
<summary><strong>Hermes Agent (Native Bash & PowerShell — No jq or xargs)</strong></summary>

**Core 10 — Windows PowerShell:**

```powershell
hermes skills tap add JovianOps/cortex; 'academic-assistant','anti-hallucination','blender-3d-modeling','code-review-assistant','college-report-card','documentation-generator','memory-manager','python-coding-assistant','testing-automation','web-scraper' | ForEach-Object { hermes skills install "JovianOps/cortex/skills/$_" --yes }
```

**Core 10 — Linux / macOS Bash:**

```bash
hermes skills tap add JovianOps/cortex
for skill in academic-assistant anti-hallucination blender-3d-modeling code-review-assistant college-report-card documentation-generator memory-manager python-coding-assistant testing-automation web-scraper; do
  hermes skills install "JovianOps/cortex/skills/$skill" --yes
done
```

**Extended 14 — Windows PowerShell:**

```powershell
hermes skills tap add JovianOps/cortex; 'accessibility-auditor','api-designer','code-migration','db-optimizer','devops-pipeline','docker-generator','incident-response','observability-setup','performance-profiler','refactoring-assistant','release-engineering','security-auditor','terraform-generator','unit-test-generator' | ForEach-Object { hermes skills install "JovianOps/cortex/premium-skills/$_" --yes }
```

**Extended 14 — Linux / macOS Bash:**

```bash
hermes skills tap add JovianOps/cortex
for skill in accessibility-auditor api-designer code-migration db-optimizer devops-pipeline docker-generator incident-response observability-setup performance-profiler refactoring-assistant release-engineering security-auditor terraform-generator unit-test-generator; do
  hermes skills install "JovianOps/cortex/premium-skills/$skill" --yes
done
```

</details>

## Verify Authenticity (SHA-256 & Provenance)

Every official release of **`@jovianops/cortex`** is published from GitHub Actions with **SLSA v1 Provenance** and deterministic **SHA-256 checksums** so you can verify you installed the real, untampered release before your AI agent reads a single instruction.

### Official `@jovianops/cortex@1.0.0` Package Hashes

| Artifact | Algorithm | Expected Fingerprint |
| :--- | :--- | :--- |
| **`@jovianops/cortex@1.0.0`** npm tarball (`cortex-1.0.0.tgz`) | **SHA-256** | `cbb9ce6a26086fc9481052bead73d9ec9f496cc9628341f0c92d1f72fd5e6247` |
| **`@jovianops/cortex@1.0.0`** npm tarball (SRI) | **SHA-512** | `sha512-erM0hXT5nh6M0HcUwqbwqJt2nB7IQjTvXQuAfsJtOQJ+HOoIZ5ez74povVkr/vOkxAeQK1LfZU9388V5fcKKsA==` |
| **SLSA v1 Provenance Attestation** | Sigstore / OIDC | [`registry.npmjs.org/-/npm/v1/attestations/@jovianops%2fcortex@1.0.0`](https://registry.npmjs.org/-/npm/v1/attestations/@jovianops%2fcortex@1.0.0) |
| **All 36 Skills, 36 Bundled Scripts & 36 ZIPs** | **SHA-256** | [`checksums.json`](checksums.json) |

### 1. Verify the npm Package Tarball SHA-256

**Linux / macOS (Bash):**

```bash
# Should print: cbb9ce6a26086fc9481052bead73d9ec9f496cc9628341f0c92d1f72fd5e6247
curl -fsSL https://registry.npmjs.org/@jovianops/cortex/-/cortex-1.0.0.tgz | sha256sum
```

**Windows (PowerShell):**

```powershell
# Should print: CBB9CE6A26086FC9481052BEAD73D9EC9F496CC9628341F0C92D1F72FD5E6247
$tmp = "$env:TEMP\cortex-1.0.0.tgz"
Invoke-WebRequest https://registry.npmjs.org/@jovianops/cortex/-/cortex-1.0.0.tgz -OutFile $tmp
(Get-FileHash $tmp -Algorithm SHA256).Hash
Remove-Item $tmp
```

### 2. Verify npm SLSA Provenance & Installed Skill Integrity

```bash
# Verify registry signatures & SLSA v1 provenance attestation
npm audit signatures

# Verify all 24 bundled skills (48 files) & any installed .cortex-lock.json against checksums.json
npx @jovianops/cortex doctor

# Verify a specific agent's installed skills for tampering or drift
npx @jovianops/cortex status --agent claude-code
```

## Requirements

| Dependency | Requirement | Notes |
| :--- | :--- | :--- |
| **Any Supported AI Agent / App** | Required | Claude Code / Claude apps, Codex CLI / ChatGPT, Gemini CLI, Cursor, GitHub Copilot & VS Code, OpenCode, OpenClaw, Goose, Aider, Cline, or Hermes Agent |
| **Python 3.10+ or Node.js (`npx`)** | Optional | Zero-dependency Python installer (`--remote`, lockfile, helper scripts, tests) or `npx skills add` |
| **PowerShell 5.1+ / 7+ or Bash** | Optional | Native shell loops for Hermes Agent and CLI workflows on Windows, Linux, and macOS |

## Repository Structure

```text
cortex/
├── .claude-plugin/         # Claude Code (& Copilot/Codex) plugin & marketplace manifests
├── .agents/plugins/        # OpenAI Codex CLI & ChatGPT Desktop marketplace manifest
├── .cursor-plugin/         # Cursor plugin & marketplace manifests
├── plugin.json             # Agent Plugins 1.0 portable root manifest
├── gemini-extension.json   # Gemini CLI extension manifest
├── checksums.json          # Deterministic SHA-256 hashes for all 24 skills, scripts & ZIPs
├── AGENTS.md               # Universal AAIF agent skill directory index
├── GEMINI.md               # Gemini CLI extension context file
├── CHANGELOG.md            # Keep-a-Changelog release history
├── assets/                 # Adaptive light & dark SVG branding assets
├── skills/                 # 10 core SKILL.md playbooks (+ bundled scripts/)
├── premium-skills/         # 14 extended engineering SKILL.md playbooks (+ bundled scripts/)
├── zips/                   # Reproducible multi-file ZIP packages for core skills
├── premium-zips/           # Reproducible multi-file ZIP packages for extended skills
├── evals/
│   └── skill_evals.json    # 24 paired 100-point Without-Skill vs. With-Skill rubrics
├── scripts/
│   ├── install_skills.py   # Zero-dependency multi-agent skill manager (--remote, lockfile, upgrade)
│   ├── package_skills.py   # Build or verify reproducible ZIPs & checksums.json
│   ├── validate_skills.py  # Validate skill frontmatter, sections & ZIP parity
│   ├── validate_manifests.py # Validate all 7 multi-agent plugin & extension manifests
│   ├── validate_yaml.py    # Validate all YAML configuration files
│   └── eval_skills.py      # Audit skill quality, run live A/B benchmarks & generate scorecards
├── tests/
│   └── test_cortex_tooling.py # End-to-end automated test suite
├── .github/                # CI workflows, Dependabot & issue/PR templates
├── index.html              # Interactive multi-agent catalog & custom install command builder
├── CONTRIBUTING.md         # Authoring standards and contribution workflow
└── LICENSE                 # MIT License
```

## Validation, Packaging & Benchmarks

Before opening a pull request, regenerate ZIP archives and `checksums.json` after editing any skill or bundled script, then run the full verification suite:

```bash
# Rebuild reproducible ZIP archives and checksums.json
python scripts/package_skills.py

# Run complete validation, audit, and automated test suite
npm test
```

Run live paired A/B benchmarks against OpenAI, Anthropic, Gemini, or any OpenAI-compatible model endpoint:

```bash
# Static audit across all 24 skills + rubric validation
python scripts/eval_skills.py

# Execute live Without-Skill vs. With-Skill benchmark & emit scorecard.md
OPENAI_API_KEY=... python scripts/eval_skills.py --run --provider openai --model gpt-4o-mini --out-dir evals/results/gpt-4o-mini
ANTHROPIC_API_KEY=... python scripts/eval_skills.py --run --provider anthropic --model claude-sonnet-4-5 --out-dir evals/results/claude
GEMINI_API_KEY=... python scripts/eval_skills.py --run --provider gemini --model gemini-2.5-pro --out-dir evals/results/gemini
```

## Contributing

Contributions and new skills are welcome! Read the **[Contributing Guide](CONTRIBUTING.md)** for the `SKILL.md` frontmatter schema, authoring standards, and pull request checklist.

## License

Released under the **MIT License** — see [`LICENSE`](LICENSE) for details.
