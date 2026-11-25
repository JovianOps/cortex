#!/usr/bin/env python3
"""Deterministic Blender bmesh geometry & transform integrity auditor.

Usage inside headless Blender:
  blender --background scene.blend --python skills/blender-3d-modeling/scripts/bmesh_check.py -- --json
"""
from __future__ import annotations

import argparse
import json
import sys


def audit_scene() -> dict:
    try:
        import bmesh  # type: ignore[import-not-found]
        import bpy  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError(
            "bmesh_check.py must be executed inside Blender: "
            "blender --background <file.blend> --python bmesh_check.py"
        ) from exc

    results = []
    overall_pass = True

    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        bm.verts.ensure_lookup_table()

        non_manifold_edges = sum(1 for e in bm.edges if not e.is_manifold)
        zero_area_faces = sum(1 for f in bm.faces if f.calc_area() < 1e-8)
        loose_verts = sum(1 for v in bm.verts if len(v.link_edges) == 0)
        unapplied_scale = any(abs(axis - 1.0) > 1e-4 for axis in obj.scale)

        issues = []
        if non_manifold_edges:
            issues.append(f"{non_manifold_edges} non-manifold edge(s)")
        if zero_area_faces:
            issues.append(f"{zero_area_faces} zero-area face(s)")
        if loose_verts:
            issues.append(f"{loose_verts} loose vertex/vertices")
        if unapplied_scale:
            issues.append(f"unapplied scale {tuple(round(x, 4) for x in obj.scale)}")

        passed = len(issues) == 0
        if not passed:
            overall_pass = False

        results.append({
            "object": obj.name,
            "vertices": len(bm.verts),
            "edges": len(bm.edges),
            "faces": len(bm.faces),
            "non_manifold_edges": non_manifold_edges,
            "zero_area_faces": zero_area_faces,
            "loose_verts": loose_verts,
            "unapplied_scale": unapplied_scale,
            "passed": passed,
            "issues": issues,
        })
        bm.free()

    return {"passed": overall_pass, "mesh_count": len(results), "meshes": results}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic Blender bmesh geometry & transform integrity auditor.")
    parser.add_argument("target", nargs="?", default=None, help="Optional blend path context (used when invoked inside Blender).")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit structured JSON output.")
    args, _unknown = parser.parse_known_args(argv)
    try:
        report = audit_scene()
    except RuntimeError as exc:
        if args.as_json:
            print(json.dumps({"passed": False, "mesh_count": 0, "meshes": [], "error": str(exc)}, indent=2))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
