#!/usr/bin/env python3
"""Deterministic OpenAPI 3.0/3.1 contract linter for api-designer skill.

Supports JSON specs with zero dependencies (and YAML when PyYAML is installed).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}


def load_spec(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(text)
    else:
        try:
            import yaml  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError("Install PyYAML to lint YAML OpenAPI specs, or pass a .json spec.") from exc
        data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("OpenAPI document must be a top-level mapping/object.")
    return data


def lint_spec(spec: dict) -> list[dict]:
    issues: list[dict] = []
    version = str(spec.get("openapi", ""))
    if not version.startswith("3."):
        issues.append({"severity": "ERROR", "rule": "openapi-version", "message": f"Expected OpenAPI 3.x, found {version!r}"})

    info = spec.get("info")
    if not isinstance(info, dict) or not info.get("title") or not info.get("version"):
        issues.append({"severity": "ERROR", "rule": "info-required", "message": "info.title and info.version are required"})

    paths = spec.get("paths")
    if not isinstance(paths, dict) or not paths:
        issues.append({"severity": "ERROR", "rule": "paths-non-empty", "message": "paths must define at least one route"})
        return issues

    seen_op_ids: set[str] = set()
    for route, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        for method, op in path_item.items():
            m = method.lower()
            if m not in HTTP_METHODS or not isinstance(op, dict):
                continue
            op_id = op.get("operationId")
            if not op_id:
                issues.append({"severity": "ERROR", "rule": "operation-id", "message": f"{m.upper()} {route}: missing operationId"})
            elif op_id in seen_op_ids:
                issues.append({"severity": "ERROR", "rule": "operation-id-unique", "message": f"Duplicate operationId {op_id!r}"})
            else:
                seen_op_ids.add(op_id)

            responses = op.get("responses")
            if not isinstance(responses, dict) or not responses:
                issues.append({"severity": "ERROR", "rule": "responses-required", "message": f"{m.upper()} {route}: missing responses"})
                continue
            codes = {str(c) for c in responses}
            has_4xx = any(c.startswith("4") or c == "default" for c in codes)
            if not has_4xx:
                issues.append({
                    "severity": "WARNING",
                    "rule": "error-envelope",
                    "message": f"{m.upper()} {route}: define 4xx/default error response (e.g., RFC 9457 Problem Details)",
                })
            if m == "post" and "201" not in codes and "202" not in codes and "200" not in codes:
                issues.append({"severity": "WARNING", "rule": "post-status", "message": f"POST {route}: expected 201/202/200 success code"})

    components = spec.get("components")
    if not isinstance(components, dict) or not components.get("securitySchemes"):
        issues.append({"severity": "WARNING", "rule": "security-schemes", "message": "components.securitySchemes is not defined"})

    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint OpenAPI 3.x specs for contract discipline.")
    parser.add_argument("spec_path", type=Path, help="Path to OpenAPI JSON or YAML file.")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON output.")
    args = parser.parse_args(argv)
    try:
        spec = load_spec(args.spec_path)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    issues = lint_spec(spec)
    errors = [i for i in issues if i["severity"] == "ERROR"]
    if args.as_json:
        print(json.dumps({"file": args.spec_path.as_posix(), "error_count": len(errors), "issues": issues}, indent=2))
    else:
        for i in issues:
            print(f"[{i['severity']}] ({i['rule']}) {i['message']}")
        if not issues:
            print(f"OK: {args.spec_path} passed all OpenAPI contract checks.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
