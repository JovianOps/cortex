#!/usr/bin/env python3
"""Audit Cortex skill quality and score Without-Skill vs. With-Skill eval outputs."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECTIONS = ("skills", "premium-skills")
EVALS_PATH = ROOT / "evals" / "skill_evals.json"


def discover_skills() -> dict[str, Path]:
    found: dict[str, Path] = {}
    for collection in COLLECTIONS:
        base = ROOT / collection
        if not base.is_dir():
            continue
        for skill_dir in sorted(p for p in base.iterdir() if p.is_dir()):
            skill_file = skill_dir / "SKILL.md"
            if skill_file.is_file():
                found[skill_dir.name] = skill_file
    return found


def parse_frontmatter_lines(frontmatter: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if ":" in line and not line.startswith((" ", "\t", "-")):
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def extract_related_skills(frontmatter: str) -> list[str]:
    match = re.search(r"related_skills:\s*\[([^\]]*)\]", frontmatter)
    if not match:
        return []
    raw = match.group(1).strip()
    if not raw:
        return []
    return [item.strip().strip("'\"") for item in raw.split(",") if item.strip()]


def audit_skill(name: str, path: Path, all_skill_names: set[str]) -> tuple[int, list[str]]:
    content = path.read_text(encoding="utf-8")
    issues: list[str] = []
    score = 0

    if not content.startswith("---\n"):
        return 0, ["Missing YAML frontmatter"]
    parts = content.split("---", 2)
    if len(parts) < 3:
        return 0, ["Malformed YAML frontmatter"]
    frontmatter, body = parts[1], parts[2]
    fields = parse_frontmatter_lines(frontmatter)

    # 1. Concise description <= 60 chars ending in period (15 pts)
    desc = fields.get("description", "").strip("'\"")
    if desc and len(desc) <= 60 and desc.endswith("."):
        score += 15
    else:
        issues.append(f"description must be <=60 chars ending in '.' (got {len(desc)} chars)")

    # 2. Complete hermes metadata (tags + valid in-repo related_skills) (15 pts)
    has_tags = bool(re.search(r"tags:\s*\[.+\]", frontmatter))
    related = extract_related_skills(frontmatter)
    invalid_related = [r for r in related if r not in all_skill_names]
    if has_tags and not invalid_related:
        score += 15
    else:
        if not has_tags:
            issues.append("missing metadata.hermes.tags")
        if invalid_related:
            issues.append(f"invalid related_skills: {invalid_related}")

    # 3. Trigger & Non-Trigger boundary (10 pts)
    if "## When to Use" in body and "When Not to Use" in body:
        score += 10
    else:
        issues.append("missing '## When to Use' or 'When Not to Use' boundary")

    # 4. Step-by-step Mandatory Protocol (15 pts)
    steps = re.findall(r"^###\s+(?:Step|Layer)\s+\d+", body, flags=re.MULTILINE)
    if len(steps) >= 3:
        score += 15
    else:
        issues.append(f"expected >=3 structured '### Step N' / '### Layer N' workflow stages (found {len(steps)})")

    # 5. Concrete verification/code snippets (>=2 fenced blocks) (10 pts)
    fenced_blocks = re.findall(r"```[a-zA-Z0-9_-]+", body)
    if len(fenced_blocks) >= 2:
        score += 10
    else:
        issues.append("expected >=2 concrete fenced command/code/contract blocks")

    # 6. Explicit Output Contract / Strict Output Format (15 pts)
    if re.search(r"^##\s+(Strict\s+)?Output\s+(Contract|Format)", body, flags=re.MULTILINE):
        score += 15
    else:
        issues.append("missing explicit '## Output Contract' or '## Strict Output Format'")

    # 7. Clean heading structure (zero duplicate H2 headings) (10 pts)
    h2s = [h.strip() for h in re.findall(r"^##\s+(.+)$", body, flags=re.MULTILINE)]
    if len(h2s) == len(set(h2s)) and "## How to Run" in body:
        score += 10
    else:
        issues.append("duplicate H2 headings or missing '## How to Run'")

    # 8. Bundled verifier is actually referenced by name (5 pts)
    # A skill that ships scripts/ must tell the agent what to run; otherwise the
    # helper is dead weight and the playbook silently falls back to guessing.
    script_dir = path.parent / "scripts"
    bundled = sorted(p.name for p in script_dir.glob("*.py")) if script_dir.is_dir() else []
    unreferenced = [name for name in bundled if name not in body]
    if not bundled:
        score += 5
    elif not unreferenced:
        score += 5
    else:
        issues.append(f"bundled script not referenced in playbook: {unreferenced}")

    # 9. Concrete non-trigger boundary, not just a heading (5 pts)
    non_trigger = re.search(
        r"###\s+When Not to Use\s*\n(.*?)(?=\n##\s|\n###\s|\Z)", body, flags=re.DOTALL
    )
    if non_trigger and re.search(r"^\s*-\s+\S", non_trigger.group(1), flags=re.MULTILINE):
        score += 5
    else:
        issues.append("'When Not to Use' needs at least one concrete bullet (route to a sibling skill)")

    return score, issues


def run_audit() -> int:
    skills = discover_skills()
    all_names = set(skills)
    failed = False
    total = 0

    print(f"{'Skill':<26} {'Collection':<15} {'Score':>7}  Status")
    print("-" * 68)
    for name, path in sorted(skills.items()):
        collection = path.parent.parent.name
        score, issues = audit_skill(name, path, all_names)
        total += score
        status = "OK" if score == 100 else "; ".join(issues)
        if score < 100:
            failed = True
        print(f"{name:<26} {collection:<15} {score:>5}/100  {status}")

    avg = total / len(skills) if skills else 0.0
    print("-" * 68)
    print(f"Audited {len(skills)} skills — average structural quality score: {avg:.1f}/100")
    return 1 if failed else 0


def validate_evals() -> int:
    if not EVALS_PATH.is_file():
        print(f"ERROR: Missing eval suite at {EVALS_PATH}", file=sys.stderr)
        return 1
    data = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    skills = discover_skills()
    tasks = data.get("tasks", [])
    seen: set[str] = set()
    errors: list[str] = []

    for task in tasks:
        skill = task.get("skill", "")
        if skill not in skills:
            errors.append(f"Eval references unknown skill: {skill!r}")
        if skill in seen:
            errors.append(f"Duplicate eval task for skill: {skill!r}")
        seen.add(skill)

        rubric = task.get("rubric", [])
        total_pts = sum(item.get("points", 0) for item in rubric)
        if total_pts != 100:
            errors.append(f"{skill}: rubric points sum to {total_pts}, expected 100")
        for item in rubric:
            for pattern in item.get("patterns", []):
                try:
                    re.compile(pattern, re.IGNORECASE | re.DOTALL)
                except re.error as exc:
                    errors.append(f"{skill}/{item.get('id')}: invalid regex {pattern!r} ({exc})")

    missing = sorted(set(skills) - seen)
    if missing:
        errors.append(f"Skills missing eval coverage: {missing}")

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1

    print(f"Eval suite valid: {len(tasks)} tasks covering all {len(skills)} skills (100 pts each).")
    return 0


def score_response(text: str, rubric: list[dict[str, object]]) -> tuple[int, list[str]]:
    earned = 0
    missed: list[str] = []
    for item in rubric:
        patterns = item.get("patterns", [])
        if all(re.search(str(pat), text, flags=re.IGNORECASE | re.DOTALL) for pat in patterns):
            earned += int(item.get("points", 0))
        else:
            missed.append(str(item.get("id")))
    return earned, missed


def run_compare(baseline_dir: Path, with_skill_dir: Path) -> int:
    data = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    tasks = data.get("tasks", [])
    base_scores: list[int] = []
    skill_scores: list[int] = []

    print(f"{'Skill':<26} {'Without':>8} {'With':>8} {'Delta':>8}")
    print("-" * 56)
    for task in tasks:
        slug = task["skill"]
        base_file = baseline_dir / f"{slug}.md"
        skill_file = with_skill_dir / f"{slug}.md"
        if not base_file.is_file() or not skill_file.is_file():
            print(f"{slug:<26} {'MISSING':>8} {'MISSING':>8} {'-':>8}")
            continue
        b_score, _ = score_response(base_file.read_text(encoding="utf-8"), task["rubric"])
        s_score, _ = score_response(skill_file.read_text(encoding="utf-8"), task["rubric"])
        base_scores.append(b_score)
        skill_scores.append(s_score)
        delta = s_score - b_score
        sign = "+" if delta >= 0 else ""
        print(f"{slug:<26} {b_score:>7}% {s_score:>7}% {sign}{delta:>6}%")

    if not base_scores:
        print("No paired response files (<skill>.md) found in the provided directories.", file=sys.stderr)
        return 1

    avg_b = sum(base_scores) / len(base_scores)
    avg_s = sum(skill_scores) / len(skill_scores)
    delta_avg = avg_s - avg_b
    sign = "+" if delta_avg >= 0 else ""
    print("-" * 56)
    print(f"{'AVERAGE (' + str(len(base_scores)) + ' skills)':<26} {avg_b:>7.1f}% {avg_s:>7.1f}% {sign}{delta_avg:>6.1f}%")
    return 0


def export_prompts(destination: Path) -> int:
    data = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    skills = discover_skills()
    exported: list[dict[str, str]] = []
    for task in data["tasks"]:
        slug = task["skill"]
        skill_text = skills[slug].read_text(encoding="utf-8")
        exported.append(
            {
                "id": task["id"],
                "skill": slug,
                "baseline_prompt": task["prompt"],
                "with_skill_system": skill_text,
                "with_skill_prompt": task["prompt"],
            }
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(exported, indent=2) + "\n", encoding="utf-8")
    print(f"Exported {len(exported)} paired A/B prompts to {destination}")
    return 0


def call_provider(
    provider: str,
    model: str,
    prompt: str,
    system: str | None = None,
    base_url: str | None = None,
    timeout: int = 90,
) -> str:
    """Zero-dependency HTTP caller for OpenAI, Anthropic, Gemini, or OpenAI-compatible endpoints."""
    if provider in {"openai", "openai-compat"}:
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key and provider == "openai":
            raise RuntimeError("OPENAI_API_KEY environment variable is required for --provider openai")
        url = (base_url or "https://api.openai.com/v1").rstrip("/") + "/chat/completions"
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        body = json.dumps({"model": model, "messages": messages, "temperature": 0.2}).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        req = urllib.request.Request(url, data=body, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        return str(payload["choices"][0]["message"]["content"])

    if provider == "anthropic":
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY environment variable is required for --provider anthropic")
        url = (base_url or "https://api.anthropic.com/v1").rstrip("/") + "/messages"
        req_body: dict[str, object] = {
            "model": model,
            "max_tokens": 2048,
            "temperature": 0.2,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            req_body["system"] = system
        req = urllib.request.Request(
            url,
            data=json.dumps(req_body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        return "".join(block.get("text", "") for block in payload.get("content", []) if block.get("type") == "text")

    if provider == "gemini":
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable is required for --provider gemini")
        endpoint = (base_url or "https://generativelanguage.googleapis.com/v1beta").rstrip("/")
        url = f"{endpoint}/models/{model}:generateContent?key={api_key}"
        req_body = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2},
        }
        if system:
            req_body["systemInstruction"] = {"parts": [{"text": system}]}
        req = urllib.request.Request(
            url,
            data=json.dumps(req_body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        parts = payload["candidates"][0]["content"]["parts"]
        return "".join(str(p.get("text", "")) for p in parts)

    raise RuntimeError(f"Unsupported provider: {provider!r}")


def run_ab_benchmark(
    provider: str,
    model: str,
    out_dir: Path,
    selected_skills: list[str],
    base_url: str | None = None,
) -> int:
    data = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    skills = discover_skills()
    base_dir = out_dir / "without-skill"
    with_dir = out_dir / "with-skill"
    base_dir.mkdir(parents=True, exist_ok=True)
    with_dir.mkdir(parents=True, exist_ok=True)

    tasks = data["tasks"]
    if selected_skills:
        wanted = set(selected_skills)
        tasks = [t for t in tasks if t["skill"] in wanted]
        if not tasks:
            print(f"ERROR: No matching tasks for skills: {selected_skills}", file=sys.stderr)
            return 2

    rows: list[tuple[str, int, int]] = []
    for task in tasks:
        slug = task["skill"]
        skill_text = skills[slug].read_text(encoding="utf-8")
        print(f"Running A/B eval for {slug} ({provider}/{model})...")
        without_resp = call_provider(provider, model, task["prompt"], system=None, base_url=base_url)
        with_resp = call_provider(provider, model, task["prompt"], system=skill_text, base_url=base_url)
        (base_dir / f"{slug}.md").write_text(without_resp, encoding="utf-8")
        (with_dir / f"{slug}.md").write_text(with_resp, encoding="utf-8")
        b_score, _ = score_response(without_resp, task["rubric"])
        s_score, _ = score_response(with_resp, task["rubric"])
        rows.append((slug, b_score, s_score))

    avg_b = sum(r[1] for r in rows) / len(rows)
    avg_s = sum(r[2] for r in rows) / len(rows)
    report_lines = [
        f"# Cortex A/B Benchmark Scorecard ({provider} / `{model}`)",
        "",
        "| Skill | Without Skill | With Skill | Lift |",
        "| :--- | :---: | :---: | :---: |",
    ]
    for slug, b, s in rows:
        delta = s - b
        sign = "+" if delta >= 0 else ""
        report_lines.append(f"| `{slug}` | {b}% | {s}% | {sign}{delta}% |")
    sign_avg = "+" if (avg_s - avg_b) >= 0 else ""
    report_lines.extend([
        "",
        f"**Average ({len(rows)} skills):** Without `{avg_b:.1f}%` → With `{avg_s:.1f}%` (**{sign_avg}{avg_s - avg_b:.1f}%** lift)",
    ])
    scorecard = out_dir / "scorecard.md"
    scorecard.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"\nWrote scorecard to {scorecard}")
    return run_compare(base_dir, with_dir)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-skills", action="store_true", help="audit all SKILL.md files for playbook quality")
    parser.add_argument("--validate-evals", action="store_true", help="validate evals/skill_evals.json integrity")
    parser.add_argument("--score", nargs=2, metavar=("BASELINE_DIR", "WITH_SKILL_DIR"), help="score paired A/B response directories")
    parser.add_argument("--export-prompts", type=Path, metavar="OUT_JSON", help="export paired A/B prompts for evaluation runners")
    parser.add_argument("--run", action="store_true", help="execute live paired A/B benchmark against an LLM provider")
    parser.add_argument("--provider", choices=("openai", "anthropic", "gemini", "openai-compat"), default="openai")
    parser.add_argument("--model", default="gpt-4o-mini", help="model identifier used with --run")
    parser.add_argument("--base-url", default=None, help="optional custom API base URL for --provider")
    parser.add_argument("--out-dir", type=Path, default=Path("evals/results/latest"), help="output directory for --run")
    parser.add_argument("--skill", action="append", default=[], help="filter --run to specific skill slug(s)")
    args = parser.parse_args()

    if not any([args.audit_skills, args.validate_evals, args.score, args.export_prompts, args.run]):
        rc1 = run_audit()
        rc2 = validate_evals()
        return 1 if (rc1 or rc2) else 0

    rc = 0
    if args.audit_skills:
        rc |= run_audit()
    if args.validate_evals:
        rc |= validate_evals()
    if args.score:
        rc |= run_compare(Path(args.score[0]), Path(args.score[1]))
    if args.export_prompts:
        rc |= export_prompts(args.export_prompts)
    if args.run:
        rc |= run_ab_benchmark(args.provider, args.model, args.out_dir, args.skill, args.base_url)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
