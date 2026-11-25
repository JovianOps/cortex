# Cortex — VS Code & GitHub Copilot Workspace Instructions

This repository houses **Cortex v3.0.0** — 36 modular, deterministic `SKILL.md` Agent Skills (10 core in `skills/` and 26 extended in `premium-skills/`), 36 zero-dependency Python verifiers, native MCP 2025-03-26 server (`cortex mcp`, 11 tools and 39 resources), Local Studio Web Workbench (`cortex studio`, 7 panels and 12 REST endpoints), Universal Agent Rule Compiler (`cortex compile`), Unified Policy/SARIF Scanner (`cortex scan`), Capability Graph (`cortex graph`), deterministic Portable Bundles (`cortex bundle`), release gate and CI/hook generator (`cortex guard`), 10 role packs (`packs.json`), 4 JSON Schemas (`schemas/`), and SHA-256 verification tooling (`checksums.json`).

## Essential Rules for Contributors & Coding Agents

1. **Always repackage after editing any skill or bundled script**:
   - Run `python scripts/package_skills.py` whenever any file under `skills/` or `premium-skills/` changes.
   - If any `SKILL.md` or `.zip` SHA-256 changes, sync `index.html` and verify with `python scripts/verify_site.py`.
2. **Keep multi-agent manifests in sync**:
   - Every manifest (`.github/plugin.json`, `.github/plugin/marketplace.json`, `plugin.json`, `.claude-plugin/`, `.agents/plugins/`, `.cursor-plugin/`, `gemini-extension.json`, `packs.json`) must agree on the release version and all 36 skills.
   - Verify with `python scripts/validate_manifests.py`.
3. **Run the full validation gate before pushing**:
   - `python scripts/cortex.py guard check --json` (runs every gate below in one pass)
   - `python scripts/package_skills.py --check`
   - `python scripts/validate_skills.py`
   - `python scripts/validate_manifests.py`
   - `python scripts/eval_skills.py`
   - `python scripts/cortex_graph.py --check`
   - `python scripts/verify_site.py`
   - `python -m unittest discover -s tests -v`
4. **Hardened GitHub Actions**:
   - Pin every `uses:` action in `.github/workflows/` to a 40-character commit SHA and verify with `python premium-skills/devops-pipeline/scripts/lint_actions.py .github/workflows`.

## VS Code Quick Install for Downstream Projects

- **Native VS Code Chat Plugin Marketplace**: Enable `chat.plugins.enabled` and add `"JovianOps/cortex"` to `chat.plugins.marketplaces` in User Settings, then install from `@agentPlugins` in the Extensions view.
- **CLI Install into `.github/skills/`**:
  ```bash
  npx @jovianops/cortex install --agent vscode --pack fullstack --scope project
  ```
