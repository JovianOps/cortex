#!/usr/bin/env python3
"""Deterministic Decimal grade & GPA calculator for college-report-card skill.

Zero external dependencies (Python 3 stdlib only).
Enforces mandatory stop gates:
  1. Syllabus weights must sum to exactly 1.00 (within 0.0001 tolerance).
  2. Duplicate student IDs abort execution immediately.
  3. Missing or non-numeric scores are flagged explicitly (never silently treated as 0).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

GRADE_SCALE: tuple[tuple[Decimal, str, Decimal], ...] = (
    (Decimal("93"), "A", Decimal("4.00")),
    (Decimal("90"), "A-", Decimal("3.70")),
    (Decimal("87"), "B+", Decimal("3.30")),
    (Decimal("83"), "B", Decimal("3.00")),
    (Decimal("80"), "B-", Decimal("2.70")),
    (Decimal("77"), "C+", Decimal("2.30")),
    (Decimal("73"), "C", Decimal("2.00")),
    (Decimal("70"), "C-", Decimal("1.70")),
    (Decimal("67"), "D+", Decimal("1.30")),
    (Decimal("63"), "D", Decimal("1.00")),
    (Decimal("60"), "D-", Decimal("0.70")),
    (Decimal("0"), "F", Decimal("0.00")),
)


def quantize_2(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def letter_and_gpa(score: Decimal) -> tuple[str, Decimal]:
    for threshold, letter, gpa in GRADE_SCALE:
        if score >= threshold:
            return letter, gpa
    return "F", Decimal("0.00")


def load_weights(path: Path) -> dict[str, Decimal]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    weights_obj = raw.get("weights", raw) if isinstance(raw, dict) else None
    if not isinstance(weights_obj, dict) or not weights_obj:
        raise ValueError("Syllabus JSON must be an object or contain a 'weights' mapping.")
    weights: dict[str, Decimal] = {}
    for key, val in weights_obj.items():
        try:
            dec = Decimal(str(val))
        except InvalidOperation as exc:
            raise ValueError(f"Invalid weight for {key!r}: {val!r}") from exc
        if dec < 0 or dec > 1:
            raise ValueError(f"Weight for {key!r} out of range [0, 1]: {dec}")
        weights[key] = dec
    total = sum(weights.values(), Decimal("0"))
    if abs(total - Decimal("1")) > Decimal("0.0001"):
        raise ValueError(
            f"STOP GATE: Syllabus weights sum to {total} (expected 1.00). Fix syllabus before grading."
        )
    return weights


def compute_grades(grades_csv: Path, syllabus_json: Path) -> dict:
    weights = load_weights(syllabus_json)
    seen_ids: set[str] = set()
    duplicates: list[str] = []
    students: list[dict] = []
    incomplete: list[dict] = []

    with grades_csv.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("Grades CSV is empty or missing headers.")
        id_col = "student_id" if "student_id" in reader.fieldnames else reader.fieldnames[0]
        missing_cols = [col for col in weights if col not in reader.fieldnames]
        if missing_cols:
            raise ValueError(f"STOP GATE: Grades CSV missing syllabus columns: {missing_cols}")

        for row_num, row in enumerate(reader, start=2):
            sid = (row.get(id_col) or "").strip()
            if not sid:
                raise ValueError(f"STOP GATE: Blank student ID at CSV line {row_num}.")
            if sid in seen_ids:
                duplicates.append(sid)
                continue
            seen_ids.add(sid)

            missing_fields: list[str] = []
            weighted_sum = Decimal("0")
            for col, weight in weights.items():
                raw_val = (row.get(col) or "").strip()
                if raw_val == "":
                    missing_fields.append(col)
                    continue
                try:
                    score = Decimal(raw_val)
                except InvalidOperation as exc:
                    raise ValueError(f"STOP GATE: Non-numeric score {raw_val!r} for {sid}.{col} (line {row_num}).") from exc
                if score < 0 or score > 100:
                    raise ValueError(f"STOP GATE: Out-of-range score {score} for {sid}.{col} (line {row_num}).")
                weighted_sum += score * weight

            if missing_fields:
                incomplete.append({"student_id": sid, "missing_components": missing_fields})
                continue

            final_score = quantize_2(weighted_sum)
            letter, gpa = letter_and_gpa(final_score)
            students.append({
                "student_id": sid,
                "name": (row.get("name") or sid).strip(),
                "final_score": str(final_score),
                "letter": letter,
                "gpa": str(gpa),
            })

    if duplicates:
        raise ValueError(f"STOP GATE: Duplicate student IDs detected: {sorted(set(duplicates))}")

    class_avg = (
        str(quantize_2(sum((Decimal(s["final_score"]) for s in students), Decimal("0")) / Decimal(len(students))))
        if students
        else None
    )
    return {
        "weights": {k: str(v) for k, v in weights.items()},
        "graded_count": len(students),
        "incomplete_count": len(incomplete),
        "class_average": class_avg,
        "students": students,
        "incomplete": incomplete,
    }


def format_markdown(report: dict) -> str:
    lines = [
        "# Academic Report Card Summary",
        "",
        f"- **Graded Students:** {report['graded_count']}",
        f"- **Incomplete Records:** {report['incomplete_count']}",
        f"- **Class Average:** {report['class_average'] or 'N/A'}",
        "",
        "| Student ID | Name | Final Score | Letter | GPA |",
        "| :--- | :--- | :---: | :---: | :---: |",
    ]
    for s in report["students"]:
        lines.append(f"| `{s['student_id']}` | {s['name']} | {s['final_score']} | {s['letter']} | {s['gpa']} |")
    if report["incomplete"]:
        lines.extend(["", "## Incomplete Records (Requires Resolution)", ""])
        for item in report["incomplete"]:
            lines.append(f"- `{item['student_id']}`: missing {', '.join(item['missing_components'])}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic Decimal grade & GPA calculator.")
    parser.add_argument("grades_csv", type=Path, help="Path to student grades CSV file.")
    parser.add_argument("syllabus_json", type=Path, help="Path to syllabus weights JSON file.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    args = parser.parse_args(argv)
    try:
        report = compute_grades(args.grades_csv, args.syllabus_json)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(format_markdown(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
