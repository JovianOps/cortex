# Cortex MCP Server Guide (`cortex mcp`)

Cortex `v2.0.0` includes a zero-dependency **Model Context Protocol (MCP 2025-03-26)** JSON-RPC 2.0 server over stdio, supporting both `Content-Length` framed (LSP-style) and newline-delimited JSON-RPC transport.

## Quick Start

Generate ready-to-paste MCP client config for your editor or agent:

```bash
# Visual Studio Code (.vscode/mcp.json)
npx @jovianops/cortex mcp --print-config vscode

# Claude Code (.mcp.json)
npx @jovianops/cortex mcp --print-config claude-code

# Cursor (.cursor/mcp.json)
npx @jovianops/cortex mcp --print-config cursor

# OpenAI Codex CLI / Windsurf
npx @jovianops/cortex mcp --print-config codex
npx @jovianops/cortex mcp --print-config windsurf
```

### Example `.vscode/mcp.json`

```json
{
  "servers": {
    "cortex": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@jovianops/cortex", "mcp", "--project-dir", "${workspaceFolder}"]
    }
  }
}
```

## Exposed MCP Capabilities

### 1. Tools (8)

| Tool Name | Purpose |
| :--- | :--- |
| `cortex_list_skills` | List all 36 Cortex skills (filterable by `tier: core \| extended`) |
| `cortex_get_skill` | Read full `SKILL.md` content, script path, and SHA-256 digest for any slug |
| `cortex_search_skills` | Search skills by keyword across slug, description, and bundled script |
| `cortex_list_packs` | Return all 10 curated role packs from `packs.json` |
| `cortex_verify_workspace` | Run `cortex verify --json` (checksums, manifests, evals, project lockfiles) |
| `cortex_run_verifier` | Safely execute any skill's bundled Python verifier inside `--project-dir` |
| `cortex_compile_rules` | Compile skills/packs into native Cursor, VS Code, Windsurf, Cline, Claude, AGENTS, or Gemini rules |
| `cortex_scan_repo` | Execute the unified multi-tool security/quality scanner across the workspace |

### 2. Resources (38)

- `cortex://skills/<slug>` — Live `SKILL.md` Markdown for all 36 skills
- `cortex://packs` — Canonical `packs.json`
- `cortex://checksums` — Canonical `checksums.json`

### 3. Prompts (36)

Every skill is registered as an invocable MCP Prompt (`cortex/<slug>`) accepting an optional `task` argument.

## Security Model

- **Workspace Confinement**: All file/directory arguments passed to `cortex_run_verifier` are canonicalized via `Path.resolve()` and verified with `relative_to(workspace_dir)`. Any path escaping the workspace root is rejected before execution.
- **No Shell Interpolation**: All verifier invocations use `subprocess.run([...])` with explicit argument lists and a 60-second execution timeout.
