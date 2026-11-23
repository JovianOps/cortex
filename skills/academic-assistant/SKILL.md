---
name: academic-assistant
description: Orchestrate grading, coding, and 3D academic workflows.
version: 0.3.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [education, coding, 3d-modeling, report-cards, anti-hallucination, memory]
    related_skills: [college-report-card, python-coding-assistant, blender-3d-modeling, anti-hallucination, memory-manager]
---

# Academic Assistant

Orchestrate high-accuracy academic tasks across grading/report cards, Python coding, and Blender 3D modeling with mandatory deterministic verification and cross-session state persistence.

## When to Use

- Multi-domain coursework tasks combining data processing, grading, code, or 3D modeling
- Generating student report cards or grade summaries from CSV/JSON datasets
- Continuing multi-session academic projects that require persistent `context.json` state
- Any academic deliverable where calculation errors, invented citations, or unverified code are unacceptable

### When Not to Use

- Purely creative essays or open-ended brainstorming with no source data or verification criteria

## How to Run

```bash
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/skills/academic-assistant --yes
hermes chat -q "Generate report cards for CS101 Fall 2024 from grades.csv using syllabus.json"
```

## Mandatory Operating Protocol

Follow these gates in strict order before producing any final academic deliverable:

### Step 1 — Load Context & Inspect Source Inputs First

1. Check whether `context.json` exists in the working directory; if present, load course metadata, rubric rules, and prior decisions before acting.
2. Read all referenced source files (`grades.csv`, `syllabus.json`, source scripts, `.blend` specs) directly.
3. Never assume column names, grading scales, or library versions that were not read from disk or tool output.

### Step 2 — Route to the Strict Domain Workflow

| Task Domain | Mandatory Deterministic Rule | Verification Gate |
| :--- | :--- | :--- |
| **Grading / Report Cards** | Compute all averages, weights, GPAs, and letter grades in Python using `decimal.Decimal` (`ROUND_HALF_UP`). **Never perform arithmetic in LLM text.** | Rubric weights sum to `1.00`; zero duplicate IDs; every score within `[0, max_points]` |
| **Academic Coding** | Write typed, self-contained scripts with explicit input validation and edge-case handling. | Execute `python -m py_compile` and run the script on sample/real inputs |
| **3D Modeling (Blender)** | Provide exact Blender steps plus a `bmesh` integrity check script (manifoldness, normals, scale `(1,1,1)`). | Verify mesh topology and target export format (`.gltf`, `.fbx`, `.stl`) |
| **Research / Citations** | Quote or cite only files, datasets, or verified references actually inspected. | Tag any unverified claim as `[UNVERIFIED]` — never fabricate citations or stats |

### Step 3 — Anti-Hallucination Audit Gate

Before outputting the final answer, verify every item below:

- [ ] Every numeric value (grade, GPA, count, percentage, metric) came directly from script output or a cited source file.
- [ ] Every file path, column name, function signature, and CLI flag was confirmed to exist.
- [ ] Missing or malformed input records are reported explicitly instead of silently filled or guessed.
- [ ] If a rubric rule or threshold is ambiguous (e.g., rounding `89.5` vs `89.49`), state the ambiguity and ask or apply the documented policy explicitly.

### Step 4 — Persist Session State

After completing a milestone, write an atomic update to `context.json` (write to `context.json.tmp` then rename) containing:

```json
{
  "schema_version": "1.0",
  "course": "CS101",
  "term": "Fall 2024",
  "updated_at": "2026-01-01T00:00:00Z",
  "source_files": ["grades.csv", "syllabus.json"],
  "decisions": ["Used ROUND_HALF_UP to 2 decimal places per syllabus"],
  "completed_items": ["Validated 32 student rows"],
  "open_tasks": ["Export PDF report cards"]
}
```

## Output Contract

Structure every completed response with:

1. **Summary** — 1–3 sentences stating what was executed and verified.
2. **Evidence & Verification** — Exact commands run, files inspected, row/check counts, and any anomalies caught.
3. **Deliverable** — Generated artifact paths, validated code, or structured results.
4. **State & Next Step** — Whether `context.json` was updated and any remaining items.

## Failure-Mode Guards

- **Never do mental math** on weighted grades, GPAs, or statistical summaries — always execute Python.
- **Never invent student comments** citing attendance, participation, or exam trends not supported by actual columns in the input file.
- **Never silently drop bad rows** (NaN, negative scores, unknown IDs); quarantine and report them with row numbers.
