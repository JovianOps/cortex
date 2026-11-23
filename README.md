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
    <a href="#supported-agents--platforms">
      <img src="https://img.shields.io/badge/standard-SKILL.md%20Multi--Agent-EA580C?style=flat" alt="SKILL.md Multi-Agent Standard" />
    </a>
    <a href="#core-skills">
      <img src="https://img.shields.io/badge/core_skills-10-2C2B28?style=flat" alt="10 Core Skills" />
    </a>
    <a href="#extended-skills">
      <img src="https://img.shields.io/badge/extended_skills-10-B8421B?style=flat" alt="10 Extended Skills" />
    </a>
    <a href="#requirements">
      <img src="https://img.shields.io/badge/platforms-Linux%20%7C%20macOS%20%7C%20Windows-5C5A52?style=flat" alt="Linux, macOS, Windows" />
    </a>
    <a href="LICENSE">
      <img src="https://img.shields.io/badge/license-MIT-5C5A52?style=flat" alt="MIT License" />
    </a>
  </p>

  <p>
    <a href="#quick-start">Quick Start</a>
    &nbsp;&middot;&nbsp;
    <a href="#supported-agents--platforms">Supported Agents</a>
    &nbsp;&middot;&nbsp;
    <a href="#core-skills">Core Skills</a>
    &nbsp;&middot;&nbsp;
    <a href="#extended-skills">Extended Skills</a>
    &nbsp;&middot;&nbsp;
    <a href="#installation">Installation</a>
    &nbsp;&middot;&nbsp;
    <a href="#repository-structure">Structure</a>
    &nbsp;&middot;&nbsp;
    <a href="#validation-packaging--benchmarks">Development</a>
    &nbsp;&middot;&nbsp;
    <a href="CONTRIBUTING.md">Contributing</a>
  </p>
</div>

---

**Cortex** is a curated collection of **20 modular, deterministic Agent Skills (`SKILL.md`)** — organized into **10 core skills** (`skills/`) for academic, coding, validation, and 3D workflows, and **10 extended engineering skills** (`premium-skills/`) for APIs, databases, DevOps, security, and testing.

Built on the open **`SKILL.md`** standard, Cortex works natively across **Claude** (Claude Code & Claude apps), **OpenAI** (Codex CLI & ChatGPT), **Gemini CLI**, **Cursor**, **GitHub Copilot & VS Code**, **OpenCode**, **OpenClaw**, **Goose**, **Aider**, **Cline**, and **Hermes Agent**. Every skill ships with standardized YAML frontmatter, native plugin/extension manifests, a zero-dependency cross-platform installer, and verified one-file ZIP distributions (`<slug>/SKILL.md`) ready for instant upload.

## Quick Start

Install into any agent in one command using the universal **Agent Skills CLI (`npx skills`)**, or use your agent's native plugin marketplace / tap:

```bash
# Universal installer (Claude Code, Codex, Gemini CLI, Cursor, Copilot, OpenCode, OpenClaw, Goose, Cline...)
npx skills add JovianOps/cortex

# Or install a single skill globally for specific agents
npx skills add JovianOps/cortex --skill code-review-assistant -a claude-code -a cursor -g
```

```bash
# Hermes Agent native tap
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/skills/academic-assistant --yes
```

> [!TIP]
> Prefer a visual picker? Open [`index.html`](index.html) locally or via GitHub Pages to filter all 20 skills, pick your target agent (**Claude, Codex, Gemini CLI, Cursor, Copilot/VS Code, OpenCode, OpenClaw, Goose, Aider, Cline, or Hermes**), and assemble a custom Bash or PowerShell install command with one click.

## Supported Agents & Platforms

Cortex ships native manifests, directory installers, and upload-ready ZIPs so every major AI coding agent and chat app works out of the box:

| Platform | Native Manifest / Format | Fast Install / Setup | Local Skills Directory |
| :--- | :--- | :--- | :--- |
| **Claude Code** | `.claude-plugin/marketplace.json` | `/plugin marketplace add JovianOps/cortex` then `/plugin install cortex@cortex` — or `npx skills add JovianOps/cortex -a claude-code` | `~/.claude/skills/` · `.claude/skills/` |
| **Claude Apps** (claude.ai & Desktop) | One-file `<slug>/SKILL.md` ZIPs (`zips/`, `premium-zips/`) | Enable **Code execution** in **Settings → Capabilities**, then **Customize → Skills → Add → Upload skill** and upload any ZIP | Account-synced (web, desktop & mobile) |
| **OpenAI Codex CLI** | `.agents/plugins/marketplace.json` + `plugin.json` | `npx skills add JovianOps/cortex -a codex` or import `JovianOps/cortex` via Codex plugin marketplace | `~/.codex/skills/` · `.agents/skills/` |
| **ChatGPT** (Web & Desktop) | `SKILL.md` playbooks & `.agents/plugins/marketplace.json` | Upload any `SKILL.md` or ZIP to **ChatGPT Projects** (Project files / instructions) or **Custom GPTs**, or load via ChatGPT Desktop plugins | Project / Custom GPT knowledge |
| **Gemini CLI** | `gemini-extension.json` + `GEMINI.md` | `gemini extensions install https://github.com/JovianOps/cortex` or `npx skills add JovianOps/cortex -a gemini-cli` | `~/.gemini/skills/` · `.gemini/skills/` |
| **Cursor** | `.cursor-plugin/marketplace.json` + `plugin.json` | Import `https://github.com/JovianOps/cortex` in **Customize → Plugins**, or `npx skills add JovianOps/cortex -a cursor` | `~/.cursor/skills/` · `.cursor/skills/` |
| **GitHub Copilot & VS Code** | `plugin.json` + `.claude-plugin/marketplace.json` | VS Code: enable `chat.plugins.enabled` → **Chat: Install Plugin From Source** (`https://github.com/JovianOps/cortex`), or `npx skills add JovianOps/cortex -a github-copilot` | `~/.copilot/skills/` · `.github/skills/` |
| **OpenCode** | `SKILL.md` + `AGENTS.md` | `npx skills add JovianOps/cortex -a opencode` or `python scripts/install_skills.py --agent opencode` | `~/.config/opencode/skills/` · `.opencode/skills/` |
| **OpenClaw** | `SKILL.md` + one-file ZIPs | `npx skills add JovianOps/cortex -a openclaw`, `python scripts/install_skills.py --agent openclaw`, or unzip `zips/*.zip` into `~/.openclaw/skills/` | `~/.openclaw/skills/` · `.openclaw/skills/` |
| **Goose** | `SKILL.md` | `npx skills add JovianOps/cortex -a goose` or `python scripts/install_skills.py --agent goose` | `~/.config/goose/skills/` · `.goose/skills/` |
| **Aider** | `SKILL.md` + `--read` / `.aider.conf.yml` | `python scripts/install_skills.py --agent aider --scope project --write-aider-conf` or `aider --read skills/<slug>/SKILL.md` | `~/.aider/skills/` · `.aider/skills/` |
| **Cline** | `SKILL.md` | `npx skills add JovianOps/cortex -a cline` or `python scripts/install_skills.py --agent cline --scope project` | `~/.cline/skills/` · `.cline/skills/` |
| **Hermes Agent** | Native Cortex tap | `hermes skills tap add JovianOps/cortex` then `hermes skills install JovianOps/cortex/<dir>/<slug> --yes` | Managed by `hermes skills` |

## Core Skills

Ten foundational skills located in [`skills/`](skills/) with prebuilt archives in [`zips/`](zips/).

| Skill | Focus | Description | Spec | ZIP |
| :--- | :--- | :--- | :---: | :---: |
| **[academic-assistant](skills/academic-assistant)** | Academic & Multi-Domain | Core academic assistant for coding, report cards, 3D modeling, anti-hallucination, and persistent memory | [`SKILL.md`](skills/academic-assistant/SKILL.md) | [`.zip`](zips/academic-assistant.zip) |
| **[anti-hallucination](skills/anti-hallucination)** | Verification | Validation framework, fact-checking, and anti-hallucination safeguards for AI outputs | [`SKILL.md`](skills/anti-hallucination/SKILL.md) | [`.zip`](zips/anti-hallucination.zip) |
| **[blender-3d-modeling](skills/blender-3d-modeling)** | 3D & Graphics | Blender 3D modeling guidance with model integrity checks and step-by-step workflows | [`SKILL.md`](skills/blender-3d-modeling/SKILL.md) | [`.zip`](zips/blender-3d-modeling.zip) |
| **[code-review-assistant](skills/code-review-assistant)** | Code Quality | Automated code review with anti-hallucination checks, style enforcement, and deterministic validation | [`SKILL.md`](skills/code-review-assistant/SKILL.md) | [`.zip`](zips/code-review-assistant.zip) |
| **[college-report-card](skills/college-report-card)** | Education | Deterministic college report card generator from structured CSV/JSON grade data | [`SKILL.md`](skills/college-report-card/SKILL.md) | [`.zip`](zips/college-report-card.zip) |
| **[documentation-generator](skills/documentation-generator)** | Documentation | Automated API docs, READMEs, architecture diagrams, and changelogs from code and specs | [`SKILL.md`](skills/documentation-generator/SKILL.md) | [`.zip`](zips/documentation-generator.zip) |
| **[memory-manager](skills/memory-manager)** | Context | Persistent memory and task-state management across sessions with anti-forgetting measures | [`SKILL.md`](skills/memory-manager/SKILL.md) | [`.zip`](zips/memory-manager.zip) |
| **[python-coding-assistant](skills/python-coding-assistant)** | Python | Python development assistance with validation, type hints, and anti-hallucination checks | [`SKILL.md`](skills/python-coding-assistant/SKILL.md) | [`.zip`](zips/python-coding-assistant.zip) |
| **[testing-automation](skills/testing-automation)** | Testing | Automated test suites with `pytest`, coverage enforcement, and CI/CD integration | [`SKILL.md`](skills/testing-automation/SKILL.md) | [`.zip`](zips/testing-automation.zip) |
| **[web-scraper](skills/web-scraper)** | Data Extraction | Structured web scraping with output validation, rate limiting, and anti-hallucination extraction | [`SKILL.md`](skills/web-scraper/SKILL.md) | [`.zip`](zips/web-scraper.zip) |

## Extended Skills

Ten specialized software engineering and infrastructure skills located in [`premium-skills/`](premium-skills/) with prebuilt archives in [`premium-zips/`](premium-zips/).

| Skill | Focus | Description | Spec | ZIP |
| :--- | :--- | :--- | :---: | :---: |
| **[api-designer](premium-skills/api-designer)** | Architecture | Design and validate REST/GraphQL APIs from OpenAPI/SDL specifications with contract testing | [`SKILL.md`](premium-skills/api-designer/SKILL.md) | [`.zip`](premium-zips/api-designer.zip) |
| **[code-migration](premium-skills/code-migration)** | Modernization | Migrate code across languages, frameworks, or major versions with strict behavior preservation | [`SKILL.md`](premium-skills/code-migration/SKILL.md) | [`.zip`](premium-zips/code-migration.zip) |
| **[db-optimizer](premium-skills/db-optimizer)** | Databases | Analyze SQL queries, suggest indexes, resolve N+1 queries, and eliminate performance bottlenecks | [`SKILL.md`](premium-skills/db-optimizer/SKILL.md) | [`.zip`](premium-zips/db-optimizer.zip) |
| **[devops-pipeline](premium-skills/devops-pipeline)** | CI/CD | Generate, validate, and optimize pipelines for GitHub Actions, GitLab CI, and CircleCI | [`SKILL.md`](premium-skills/devops-pipeline/SKILL.md) | [`.zip`](premium-zips/devops-pipeline.zip) |
| **[docker-generator](premium-skills/docker-generator)** | Containers | Generate optimized multi-stage Dockerfiles, `docker-compose` setups, and container configs | [`SKILL.md`](premium-skills/docker-generator/SKILL.md) | [`.zip`](premium-zips/docker-generator.zip) |
| **[performance-profiler](premium-skills/performance-profiler)** | Performance | Profile and optimize CPU, memory, and I/O bottlenecks across applications | [`SKILL.md`](premium-skills/performance-profiler/SKILL.md) | [`.zip`](premium-zips/performance-profiler.zip) |
| **[refactoring-assistant](premium-skills/refactoring-assistant)** | Maintainability | Refactor complex codebases to reduce complexity and apply design patterns safely | [`SKILL.md`](premium-skills/refactoring-assistant/SKILL.md) | [`.zip`](premium-zips/refactoring-assistant.zip) |
| **[security-auditor](premium-skills/security-auditor)** | Security | Audit code for OWASP vulnerabilities, hardcoded secrets, and compliance issues | [`SKILL.md`](premium-skills/security-auditor/SKILL.md) | [`.zip`](premium-zips/security-auditor.zip) |
| **[terraform-generator](premium-skills/terraform-generator)** | Infrastructure | Generate and validate Terraform / OpenTofu infrastructure-as-code modules | [`SKILL.md`](premium-skills/terraform-generator/SKILL.md) | [`.zip`](premium-zips/terraform-generator.zip) |
| **[unit-test-generator](premium-skills/unit-test-generator)** | Testing | Generate comprehensive unit tests, edge cases, and regression suites with coverage analysis | [`SKILL.md`](premium-skills/unit-test-generator/SKILL.md) | [`.zip`](premium-zips/unit-test-generator.zip) |

## Installation

### 1. Universal CLI (`npx skills`) — Works Across 40+ Agents

Use the open Agent Skills CLI in **Bash or PowerShell** to install into Claude Code, Codex CLI, Gemini CLI, Cursor, GitHub Copilot, OpenCode, OpenClaw, Goose, Cline, and more:

```bash
# Interactive picker (auto-detects your installed agents)
npx skills add JovianOps/cortex

# Install all 20 skills globally across every detected agent
npx skills add JovianOps/cortex --all -g -y

# Install specific skills for specific agents
npx skills add JovianOps/cortex --skill security-auditor --skill code-review-assistant -a claude-code -a cursor -a codex -y

# Target other agents explicitly
npx skills add JovianOps/cortex -a gemini-cli -g          # Gemini CLI
npx skills add JovianOps/cortex -a github-copilot        # GitHub Copilot & VS Code (.github/skills/)
npx skills add JovianOps/cortex -a opencode -g           # OpenCode
npx skills add JovianOps/cortex -a openclaw -g           # OpenClaw
npx skills add JovianOps/cortex -a goose -g              # Goose
npx skills add JovianOps/cortex -a cline                 # Cline (.cline/skills/)
```

### 2. Platform-Specific Marketplaces & Apps

<details>
<summary><strong>Claude (Claude Code & Claude Apps — claude.ai / Desktop)</strong></summary>

**Claude Code (Plugin Marketplace):**

```text
/plugin marketplace add JovianOps/cortex
/plugin install cortex@cortex
# Or install just one collection:
/plugin install cortex-core@cortex
/plugin install cortex-extended@cortex
```

**Claude Apps (claude.ai & Claude Desktop):**

1. Download any skill ZIP from [`zips/`](zips/) or [`premium-zips/`](premium-zips/) (each archive already contains `<slug>/SKILL.md` in the exact folder format Claude requires).
2. Open **Settings → Capabilities** and enable **Code execution / Create and edit files**.
3. Open **Customize → Skills → Add → Upload skill** and select the downloaded `.zip` file.

</details>

<details>
<summary><strong>OpenAI (Codex CLI & ChatGPT)</strong></summary>

**Codex CLI:**

```bash
npx skills add JovianOps/cortex -a codex -g
# Or install directly via the Python installer (no Node.js required):
python scripts/install_skills.py --agent codex --collection all --scope global
```

Codex CLI and ChatGPT Desktop also discover `.agents/plugins/marketplace.json` and `plugin.json` directly from `https://github.com/JovianOps/cortex`.

**ChatGPT (Web & Desktop Projects / Custom GPTs):**

- **ChatGPT Projects**: Open your Project → **Files** → upload any `SKILL.md` (or `.zip` from `zips/` / `premium-zips/`) and instruct the project to follow the attached playbook.
- **Custom GPTs**: Create a GPT → paste or upload any `SKILL.md` into **Knowledge** and reference its workflow in **Instructions**.

</details>

<details>
<summary><strong>Gemini CLI</strong></summary>

```bash
# Install the entire Cortex extension (reads gemini-extension.json + GEMINI.md + skills/)
gemini extensions install https://github.com/JovianOps/cortex

# Or install individual SKILL.md directories into ~/.gemini/skills/ or .gemini/skills/
npx skills add JovianOps/cortex -a gemini-cli -g
```

</details>

<details>
<summary><strong>Cursor</strong></summary>

- **Cursor Marketplace / Plugins**: Open **Customize → Plugins** and import `https://github.com/JovianOps/cortex` (reads `.cursor-plugin/marketplace.json` and `plugin.json`).
- **CLI**:

```bash
npx skills add JovianOps/cortex -a cursor -g
```

</details>

<details>
<summary><strong>GitHub Copilot & VS Code</strong></summary>

- **VS Code Agent Plugins**: Enable `chat.plugins.enabled` in VS Code Settings, run **Chat: Install Plugin From Source**, and enter `https://github.com/JovianOps/cortex`.
- **GitHub Copilot CLI**:

```bash
copilot plugin marketplace add JovianOps/cortex
copilot plugin install cortex
```

- **Repository / Workspace Skills (`.github/skills/`)**:

```bash
npx skills add JovianOps/cortex -a github-copilot
```

</details>

<details>
<summary><strong>OpenCode, OpenClaw, Goose, Aider & Cline</strong></summary>

```bash
# OpenCode (~/.config/opencode/skills/ or .opencode/skills/)
npx skills add JovianOps/cortex -a opencode -g

# OpenClaw (~/.openclaw/skills/ or .openclaw/skills/)
npx skills add JovianOps/cortex -a openclaw -g
# Or unzip any archive directly:
unzip zips/code-review-assistant.zip -d ~/.openclaw/skills/

# Goose (~/.config/goose/skills/ or .goose/skills/)
npx skills add JovianOps/cortex -a goose -g

# Cline (.cline/skills/ or ~/.cline/skills/)
npx skills add JovianOps/cortex -a cline

# Aider (--read flag or .aider.conf.yml)
aider --read skills/code-review-assistant/SKILL.md
# Or copy skills into .aider/skills/ and auto-update .aider.conf.yml:
python scripts/install_skills.py --agent aider --scope project --write-aider-conf
```

</details>

### 3. Zero-Dependency Python Multi-Agent Installer (No Node.js Required)

Clone Cortex and install any subset of skills into one or all agents on **Linux, macOS, or Windows**:

```bash
# List all supported agents and their exact global/project directories
python scripts/install_skills.py --list

# Install all 20 skills globally for Claude Code, Codex, Cursor, and Gemini CLI
python scripts/install_skills.py --agent claude-code --agent codex --agent cursor --agent gemini-cli

# Install specific skills into the current project for Copilot, Cline, OpenCode, Goose, OpenClaw & Aider
python scripts/install_skills.py \
  --agent copilot --agent cline --agent opencode --agent goose --agent openclaw --agent aider \
  --skill code-review-assistant --skill security-auditor \
  --scope project --write-aider-conf

# Install everywhere at once (preview first with --dry-run)
python scripts/install_skills.py --agent all --collection all --dry-run
```

### 4. Hermes Agent Native Tap

All Hermes Agent commands use native shell syntax — no `jq` or `xargs` required.

> [!IMPORTANT]
> On **Windows**, use the **PowerShell** commands (`ForEach-Object`) below. Do not paste Bash `for ...; do ... done` loops into PowerShell.

#### Install a Single Skill

```bash
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/skills/academic-assistant --yes
```

```bash
# Example extended skill
hermes skills install JovianOps/cortex/premium-skills/security-auditor --yes
```

#### Install All 10 Core Skills (Hermes)

<details>
<summary><strong>Windows — PowerShell</strong></summary>

```powershell
hermes skills tap add JovianOps/cortex; 'academic-assistant','college-report-card','anti-hallucination','blender-3d-modeling','code-review-assistant','documentation-generator','memory-manager','python-coding-assistant','testing-automation','web-scraper' | ForEach-Object { hermes skills install "JovianOps/cortex/skills/$_" --yes }
```

</details>

<details>
<summary><strong>Linux / macOS — Bash</strong></summary>

```bash
hermes skills tap add JovianOps/cortex
for skill in academic-assistant college-report-card anti-hallucination blender-3d-modeling code-review-assistant documentation-generator memory-manager python-coding-assistant testing-automation web-scraper; do
  hermes skills install "JovianOps/cortex/skills/$skill" --yes
done
```

</details>

#### Install All 10 Extended Skills (Hermes)

<details>
<summary><strong>Windows — PowerShell</strong></summary>

```powershell
hermes skills tap add JovianOps/cortex; 'api-designer','code-migration','db-optimizer','devops-pipeline','docker-generator','performance-profiler','refactoring-assistant','security-auditor','terraform-generator','unit-test-generator' | ForEach-Object { hermes skills install "JovianOps/cortex/premium-skills/$_" --yes }
```

</details>

<details>
<summary><strong>Linux / macOS — Bash</strong></summary>

```bash
hermes skills tap add JovianOps/cortex
for skill in api-designer code-migration db-optimizer devops-pipeline docker-generator performance-profiler refactoring-assistant security-auditor terraform-generator unit-test-generator; do
  hermes skills install "JovianOps/cortex/premium-skills/$skill" --yes
done
```

</details>

## Requirements

| Dependency | Requirement | Notes |
| :--- | :--- | :--- |
| **Any Supported AI Agent / App** | Required | Claude Code / Claude apps, Codex CLI / ChatGPT, Gemini CLI, Cursor, GitHub Copilot & VS Code, OpenCode, OpenClaw, Goose, Aider, Cline, or Hermes Agent |
| **Node.js (`npx`) or Python 3** | Optional | Use `npx skills add` for instant multi-agent CLI installs, or `python scripts/install_skills.py` for zero-Node installs, PDF export, and local validation |
| **PowerShell 5.1+ / 7+ or Bash** | Optional | Native shell loops for Hermes Agent and CLI workflows on Windows, Linux, and macOS |

## Repository Structure

```text
cortex/
├── .claude-plugin/         # Claude Code (& Copilot/Codex) plugin & marketplace manifests
├── .agents/plugins/        # OpenAI Codex CLI & ChatGPT Desktop marketplace manifest
├── .cursor-plugin/         # Cursor plugin & marketplace manifests
├── plugin.json             # Agent Plugins 1.0 portable root manifest
├── gemini-extension.json   # Gemini CLI extension manifest
├── AGENTS.md               # Universal AAIF agent skill directory index
├── GEMINI.md               # Gemini CLI extension context file
├── assets/                 # Adaptive light & dark SVG branding assets
├── skills/                 # 10 core SKILL.md playbooks
├── premium-skills/         # 10 extended engineering SKILL.md playbooks
├── zips/                   # Verified one-file ZIPs (<slug>/SKILL.md) for Claude apps & manual install
├── premium-zips/           # Verified one-file ZIPs for extended skills
├── evals/
│   └── skill_evals.json    # 20 paired 100-point Without-Skill vs. With-Skill rubrics
├── scripts/
│   ├── install_skills.py   # Zero-dependency multi-agent installer (11 agent targets + Aider config)
│   ├── package_skills.py   # Build or verify skill ZIP archives
│   ├── validate_skills.py  # Validate skill frontmatter, sections & ZIP parity
│   ├── validate_manifests.py # Validate all multi-agent plugin & extension manifests
│   ├── validate_yaml.py    # Validate all YAML configuration files
│   └── eval_skills.py      # Audit skill quality & score Without vs. With Skill runs
├── .github/                # CI workflows, Dependabot & issue/PR templates
├── index.html              # Interactive multi-agent catalog & custom install command builder
├── CONTRIBUTING.md         # Authoring standards and contribution workflow
└── LICENSE                 # MIT License
```

## Validation, Packaging & Benchmarks

Before opening a pull request, regenerate ZIP archives if you edited any `SKILL.md` and run the repository checks:

```bash
# Rebuild ZIP archives after modifying a SKILL.md
python scripts/package_skills.py

# Verify ZIP parity, validate all 20 skills, and validate all multi-agent manifests
npm test
```

You can also run the validation and benchmark scripts directly:

```bash
python scripts/package_skills.py --check
python scripts/validate_skills.py
python scripts/validate_manifests.py
python scripts/validate_yaml.py

# Audit playbook quality across all 20 skills & validate eval rubrics
python scripts/eval_skills.py

# Export paired A/B prompts or score saved Without-Skill vs. With-Skill outputs
python scripts/eval_skills.py --export-prompts /tmp/paired_prompts.json
python scripts/eval_skills.py --score ./runs/without-skill ./runs/with-skill
```

## Contributing

Contributions and new skills are welcome! Read the **[Contributing Guide](CONTRIBUTING.md)** for the `SKILL.md` frontmatter schema, authoring standards, and pull request checklist.

## License

Released under the **MIT License** — see [`LICENSE`](LICENSE) for details.
