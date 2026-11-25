# Universal Agent Rule Compiler (`cortex compile`)

Different AI coding IDEs and harnesses expect different instruction file formats. **`cortex compile`** treats Cortex's `SKILL.md` playbooks as the single source of truth and compiles them deterministically into native rule files with SHA-256 provenance comments.

## Supported Targets

| Target | Output Path(s) | Format Details |
| :--- | :--- | :--- |
| `cursor` | `.cursor/rules/cortex-<slug>.mdc` | Cursor MDC with YAML frontmatter (`description`, `globs`, `alwaysApply: false`) |
| `vscode` | `.github/instructions/cortex-<slug>.instructions.md` | VS Code / Copilot scoped instructions with `applyTo` glob frontmatter |
| `windsurf` | `.windsurf/rules/cortex-<slug>.md` | Windsurf workspace rules with SHA-256 header |
| `cline` | `.clinerules/cortex-<slug>.md` | Cline / Roo Code modular rule files |
| `claude` | `CLAUDE.md` | Idempotent `<!-- BEGIN CORTEX MANAGED -->` table preserving user content |
| `agents` | `AGENTS.md` | Idempotent `<!-- BEGIN CORTEX MANAGED -->` table preserving user content |
| `opencode` | `AGENTS.md` | OpenCode alias targeting `AGENTS.md` managed rules block |
| `gemini` | `GEMINI.md` | Idempotent `<!-- BEGIN CORTEX MANAGED -->` table preserving user content |

## Common Commands

```bash
# Compile the cloud-native pack for Cursor and VS Code
npx @jovianops/cortex compile --pack cloud-native --target cursor --target vscode

# Compile specific skills across ALL 8 targets (dry-run preview first)
npx @jovianops/cortex compile --skill kubernetes-architect --skill security-auditor --target all --dry-run

# CI Drift Gate: exit 1 if compiled files on disk do not match current Cortex skills
npx @jovianops/cortex compile --pack fullstack --target cursor --target vscode --check --json
```

## Idempotent Managed Blocks

For root index files (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`), `cortex compile` only updates content between `<!-- BEGIN CORTEX MANAGED -->` and `<!-- END CORTEX MANAGED -->`, leaving all surrounding project-specific guidance untouched.
