---
name: college-report-card
description: Generate exact report cards using Decimal grade scripts.
version: 0.2.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [education, report-cards, college, grading, memory]
    related_skills: [academic-assistant, anti-hallucination, memory-manager]
---

# College Report Card Generator

Generate deterministic, auditable college report cards from structured CSV/JSON grade data and syllabus rubrics with zero LLM arithmetic and strict source provenance.

## When to Use

- Computing weighted course averages, GPAs, and letter grades from CSV/JSON gradebooks
- Rendering consistent HTML, Markdown, or PDF student report cards from a template
- Auditing gradebooks for missing entries, duplicate student IDs, or rubric weight mismatches
- Producing fact-grounded performance comments tied strictly to recorded student metrics

### When Not to Use

- Unstructured narrative evaluations with no quantitative grade or attendance data

## How to Run

```bash
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/skills/college-report-card --yes
hermes chat -q "Generate report cards for CS101 Fall 2024 from grades.csv using syllabus.json"
```

## Prerequisites

- Student grade/attendance data in CSV or JSON
- Course rubric (category weights, max points, letter-grade cutoffs, GPA scale)
- Python 3.9+ (or PowerShell 5.1+); optional HTML-to-PDF backend (e.g., `weasyprint` or Chromium headless) for PDF export

## Mandatory Execution Pipeline

### Step 1 — Validate Rubric & Input Schema Before Calculating

Write and run a Python validation script that checks ALL of the following and fails fast on errors:

1. **Rubric weight sum**: Confirm `sum(Decimal(str(w)) for w in weights.values()) == Decimal("1.00")`.
2. **Grade cutoff integrity**: Confirm letter-grade thresholds are strictly descending with no gaps or overlaps (e.g., `A >= 93`, `A- >= 90`, ...).
3. **Student ID uniqueness**: Reject or quarantine duplicate `student_id` rows with exact line numbers.
4. **Range & missingness audit**: Flag negative scores, scores exceeding `max_points` (unless extra credit is explicitly allowed in rubric), empty cells, or non-numeric strings.

### Step 2 — Deterministic `Decimal` Calculation (Never LLM Math)

**Never compute any average, weighted score, GPA, or rank in natural language.** Always execute Python using `decimal.Decimal` with explicit quantization:

```python
from decimal import Decimal, ROUND_HALF_UP

def round_score(value: Decimal, places: str = "0.01") -> Decimal:
    return value.quantize(Decimal(places), rounding=ROUND_HALF_UP)

def compute_weighted_percent(
    scores: dict[str, Decimal],
    max_points: dict[str, Decimal],
    weights: dict[str, Decimal],
) -> Decimal:
    total = Decimal("0")
    for category, weight in weights.items():
        pct = (scores[category] / max_points[category]) * Decimal("100")
        total += pct * weight
    return round_score(total)
```

### Step 3 — Template-Based Report Rendering & Grounded Comments

- Populate a deterministic HTML/Markdown template directly from the computed JSON records so numbers cannot drift between calculation and rendering.
- **Grounded comments rule**: Every sentence in a student's performance comment MUST reference a concrete, computed fact (e.g., `"Strong lab average (94.50%) offset a lower midterm (76.00%)."`). Never invent claims about classroom attitude, participation, or study habits unless those columns exist in the dataset.
- Escape HTML special characters (`html.escape`) for student names and notes before rendering HTML/PDF.

### Step 4 — Reconciliation & Audit Summary

After generating all report cards, run an automated post-check verifying:

1. `generated_card_count == valid_student_count`
2. Re-parsing rendered output matches `computed_grades.json` for every `student_id`
3. Class statistics (mean, median, min, max, letter-grade distribution) are computed via Python and saved alongside the batch in `audit_summary.json`

## Output Contract

Deliver:

1. **Validation Report** — Rows read, valid count, quarantined anomalies (`row_number`, `student_id`, `reason`).
2. **Class Distribution Summary** — Exact Python-computed mean, median, min, max, and letter-grade counts.
3. **Generated Artifacts** — Paths to `computed_grades.json`, HTML/Markdown/PDF report cards, and `audit_summary.json`.
4. **Reconciliation Verdict** — `VERIFIED` only when count and value checks pass 100%.

## Common Failure Modes Prevented

- **Floating-point rounding drift**: `89.49999999999999` turning an `A-`/`B+` boundary wrong — prevented by `Decimal` + explicit `ROUND_HALF_UP`.
- **Silent `NaN` / blank-cell corruption**: Treating an unsubmitted blank as `0` vs excused without checking rubric policy — always apply the explicit missing-grade policy and log every affected cell.
- **Hallucinated student commentary**: Prevented by strictly binding comment generation to computed category breakdown fields.
