---
name: memory-manager
description: Persist versioned session memory with staleness checks.
version: 2.0.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [memory, context, persistence, anti-forgetting]
    related_skills: [academic-assistant, anti-hallucination]
---

# Memory Manager

Maintain durable, structured, staleness-checked project memory across sessions using a versioned `context.json` store so critical constraints, decisions, and task progress are never lost or silently overwritten.

## When to Use

- Resuming multi-step engineering, grading, or research projects across separate sessions
- Recording architectural decisions, verified facts, and open tasks so future turns stay consistent
- Auditing or compacting an existing session memory file before handing off work

### When Not to Use

- Storing secrets, API keys, passwords, or private credentials (never write secrets into memory files)

## How to Run

> **Bundled Helper Script (`v0.3.0`):** Run `python skills/memory-manager/scripts/memory_store.py init --project <name>` (plus `add-decision`, `add-task`, `complete-task`, `check-stale`, `summary`) for atomic JSON session persistence.

```bash
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/skills/memory-manager --yes
hermes chat -q "Save my current project state to context.json and summarize open tasks"
```

## Canonical Memory Schema (`context.json`)

Always store memory in a strict, versioned JSON schema rather than unstructured prose notes:

```json
{
  "schema_version": "1.0",
  "project": "project-slug",
  "updated_at": "2026-01-01T00:00:00Z",
  "goal": "Single-sentence active objective",
  "constraints": [
    "Must support Python 3.10+ with zero external dependencies"
  ],
  "decisions": [
    {
      "id": "DEC-001",
      "date": "2026-01-01",
      "decision": "Use Decimal ROUND_HALF_UP for all grade math",
      "rationale": "Avoids binary floating-point boundary drift",
      "status": "active"
    }
  ],
  "verified_facts": [
    {
      "fact": "All 20 skills pass scripts/validate_skills.py",
      "source": "scripts/validate_skills.py",
      "file_sha256": "<optional-hash>",
      "verified_at": "2026-01-01T00:00:00Z"
    }
  ],
  "tasks": [
    {
      "id": "TASK-001",
      "title": "Add unit tests for parser edge cases",
      "status": "in_progress",
      "notes": "Empty CSV row handling done; duplicate ID check pending"
    }
  ],
  "file_pointers": [
    "src/parser.py",
    "tests/test_parser.py"
  ]
}
```

## Mandatory Persistence Protocol

### Step 1 — Load & Check Staleness First

When resuming a session:

1. Read `context.json` and validate JSON syntax + `schema_version`.
2. **Staleness verification**: For every entry in `file_pointers` and `verified_facts`, confirm the file still exists and check whether its SHA-256 hash or `git status` changed since `updated_at`.
3. Flag any stale fact explicitly as `[STALE — RE-VERIFY]` before relying on it.

### Step 2 — Append-Only Decision Integrity

- **Never silently delete or overwrite prior `decisions`**. If a decision changes, mark the old entry `"status": "superseded"` and append a new `DEC-XXX` entry referencing the superseded ID.
- Separate `verified_facts` (backed by files/commands) from `open_questions` or hypotheses.

### Step 3 — Atomic & Secret-Free Writes

Before writing `context.json`:

1. **Secret scrub**: Reject any value matching API keys, bearer tokens, private keys, or passwords.
2. **Atomic write**: Write serialized JSON (sorted keys or stable formatting, UTF-8, trailing newline) to `context.json.tmp`, parse it back with `json.loads` to confirm validity, then atomically replace `context.json` (`os.replace`).

```python
import json, os
from pathlib import Path

def save_context_atomic(path: Path, data: dict) -> None:
    payload = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    json.loads(payload)  # sanity parse
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(payload, encoding="utf-8")
    os.replace(tmp, path)
```

### Step 4 — Context Compaction Rule

If `context.json` grows beyond 200 lines or 25 completed tasks:

- Archive `done` tasks into a concise `completed_summary` list while keeping all `active` decisions, `constraints`, and `in_progress`/`pending` tasks intact.

## Output Contract

Report on every memory operation:

1. **Operation** — `LOADED` | `SAVED` | `UPDATED` | `COMPACTED` | `CLEARED`
2. **Path & Timestamp** — Exact file path and `updated_at`
3. **Stale / Conflict Warnings** — Any referenced files modified or missing since last save
4. **Active Resume Brief** — Current goal, active constraints, and next pending task ID
