# Cortex Studio Local Workbench (`cortex studio`)

**Cortex Studio** is a zero-dependency local web workbench rendered in Light Swiss & Dark Swiss design, powered by Python's built-in `ThreadingHTTPServer`.

## Launching Cortex Studio

```bash
# Default local bind (http://127.0.0.1:4310)
npx @jovianops/cortex studio

# Custom port and workspace directory
npx @jovianops/cortex studio --host 127.0.0.1 --port 4310 --project-dir /path/to/repo

# Container / remote preview bind
npx @jovianops/cortex studio --host 0.0.0.0 --port 4310
```

## Workbench Views

1. **01 / Overview**: Live skill/script/pack/MCP KPIs and one-click `cortex verify` integrity audit.
2. **02 / Skills (36)**: Instant filter across all 36 skills with side-by-side `SKILL.md` and bundled Python script source viewer plus SHA-256 fingerprint.
3. **03 / Tool Runner**: Execute any of the 36 bundled Python verifiers directly against files/folders in your workspace and inspect structured JSON findings.
4. **04 / Compiler**: Preview (`dry_run: true`) or generate native rule files for Cursor, VS Code, Windsurf, Cline, `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md`.
5. **05 / Policy & SARIF**: Run unified repository scans with configurable severity gates and export **SARIF 2.1.0** (`cortex-scan.sarif`) directly from the browser.
6. **06 / MCP Server**: Generate copy-paste MCP client configs for VS Code, Claude Code, Cursor, Codex, Windsurf, and OpenCode.
7. **07 / Capability Graph**: Build JSON, Mermaid, or Graphviz DOT skill graphs and run the 6-gate `cortex guard check` release verifier.

## REST API Reference

| Method & Route | Description |
| :--- | :--- |
| `GET /api/overview` | Version, workspace path, skill/script/pack/tool counts, available scanners |
| `GET /api/skills` | Full metadata list for all 36 skills |
| `GET /api/skills/<slug>` | Skill metadata + full `SKILL.md` + bundled script source |
| `GET /api/packs` | All 10 role packs (`packs.json`) |
| `GET /api/verify` | Runs `cortex verify --json` against the workspace |
| `GET /api/graph?format=json\|mermaid\|dot&pack=<id>` | Builds capability graph (`cortex graph`) in JSON, Mermaid, or Graphviz DOT, optionally scoped to a role pack |
| `GET /api/mcp-config?client=vscode` | Returns MCP JSON config for `vscode`, `claude-code`, `cursor`, `codex`, `windsurf`, or `opencode` |
| `POST /api/run-tool` | Body `{"slug": "...", "target": "."}` — runs bundled Python verifier |
| `POST /api/compile` | Body `{"pack": "fullstack", "targets": ["cursor","vscode"], "dry_run": true}` |
| `POST /api/scan` | Body `{"fail_on": "high", "only": []}` — returns `{report, sarif}` |
| `POST /api/guard` | Body `{"fail_fast": false, "only": []}` — runs `cortex guard check` |
