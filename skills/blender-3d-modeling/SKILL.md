---
name: blender-3d-modeling
description: Build and validate Blender 3D meshes with bmesh checks.
version: 0.3.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [3d-modeling, blender, modeling, validation]
    related_skills: [academic-assistant, python-coding-assistant]
---

# Blender 3D Modeling & Mesh Validation

Guide reproducible Blender 3D modeling workflows (Blender 3.x / 4.x) and run deterministic `bpy`/`bmesh` topology, UV, transform, and export validations.

## When to Use

- Building low-poly, hard-surface, or game-ready assets in Blender step by step
- Writing Blender Python (`bpy`) procedural modeling or batch validation scripts
- Auditing `.blend`, `.glb`/`.gltf`, `.fbx`, or `.stl` meshes before game-engine import or 3D printing
- Fixing shading artifacts, inverted normals, non-manifold geometry, or broken UV unwraps

### When Not to Use

- CAD parametric solid modeling requiring FreeCAD/OpenSCAD/Fusion 360 BREP constraints

## How to Run

> **Bundled Helper Script (`v0.3.0`):** Run `blender --background scene.blend --python skills/blender-3d-modeling/scripts/bmesh_check.py` for automated manifold, normal, loose-vertex, and scale integrity checks.

```bash
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/skills/blender-3d-modeling --yes
hermes chat -q "Guide me through building and validating a game-ready low-poly chair in Blender"
```

## Mandatory Workflow

### Step 1 — Lock Target Constraints First

Before listing modeling steps or generating `bpy` code, establish or explicitly state defaults for:

1. **Blender version** (note 4.x API changes: `Auto Smooth` moved to `Smooth by Angle` modifier; `Principled BSDF` input names changed from `Subsurface` / `Specular` to `Subsurface Weight` / `Specular IOR Level`).
2. **Target destination**:
   - **Game engine (Unity / Unreal / Godot / WebGL)**: quad/tri budget, texel density, clean UV0 (and non-overlapping lightmap UV1 if baked), glTF 2.0 (`.glb`) or FBX, scale applied `(1,1,1)`, `+Y`/`-Z` forward convention.
   - **3D Printing (`.stl` / `.3mf`)**: strictly watertight (0 non-manifold edges, 0 boundary edges), real-world metric units (`mm`), minimum wall thickness (`>= 1.2mm` FDM).
   - **Render / Subdivision**: all-quad topology, support loops, no N-gons on curved surfaces, weighted normals / bevel modifier stack.

### Step 2 — Structured Non-Destructive Modeling Steps

Always structure modeling instructions in this exact order:

1. **Scene & Units**: Metric scale (`1.0`), real-world bounding box dimensions (e.g., chair seat height `0.45m`, total height `0.85m`).
2. **Blockout**: Primitive proportions with exact dimensions and pivot/origin placement (bottom-center at `(0, 0, 0)` for grounded props).
3. **Topology & Modifiers**: Non-destructive stack (`Mirror` → `Bevel` with `Clamp Overlap` → `Subdivision` / `Weighted Normal`), maintaining clean edge flow.
4. **Apply Transforms**: `Ctrl+A` → `Rotation & Scale` BEFORE UV unwrapping or beveling (unapplied non-uniform scale distorts bevels and stretches UVs).
5. **Seams & UV Unwrap**: Place seams on hard edges/hidden undersides, unwrap (`Angle Based` or `Conformal`), `Average Islands Scale`, `Pack Islands` with margin `>= 0.004` (at 2K texture).

### Step 3 — Deterministic `bmesh` Validation Script

Whenever validating a mesh or delivering a procedural `bpy` asset, include and run (when Blender CLI is available) this headless audit:

```bash
blender --background model.blend --python validate_mesh.py
```

```python
import bmesh
import bpy

def audit_mesh_objects() -> dict[str, dict[str, object]]:
    report: dict[str, dict[str, object]] = {}
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        non_manifold = sum(1 for e in bm.edges if not e.is_manifold)
        boundary = sum(1 for e in bm.edges if e.is_boundary)
        loose_verts = sum(1 for v in bm.verts if not v.link_edges)
        ngons = sum(1 for f in bm.faces if len(f.verts) > 4)
        zero_area = sum(1 for f in bm.faces if f.calc_area() < 1e-7)
        tris = sum(len(f.verts) - 2 for f in bm.faces)
        unapplied_scale = any(abs(s - 1.0) > 1e-4 for s in obj.scale)

        report[obj.name] = {
            "verts": len(bm.verts),
            "faces": len(bm.faces),
            "tris": tris,
            "ngons": ngons,
            "non_manifold_edges": non_manifold,
            "boundary_edges": boundary,
            "loose_verts": loose_verts,
            "zero_area_faces": zero_area,
            "unapplied_scale": unapplied_scale,
            "has_uv": bool(obj.data.uv_layers),
        }
        bm.free()
    return report

if __name__ == "__main__":
    import json
    print(json.dumps(audit_mesh_objects(), indent=2))
```

## Export Pre-Flight Checklist

- [ ] `Scale == (1.0, 1.0, 1.0)` and `Rotation == (0, 0, 0)` applied on all exported meshes
- [ ] `Merge by Distance` (`0.0001m`) executed; `loose_verts == 0` and `zero_area_faces == 0`
- [ ] Normals recalculated outside (`Shift+N`) and verified with **Face Orientation** overlay (all blue)
- [ ] For 3D print: `non_manifold_edges == 0` and `boundary_edges == 0`
- [ ] Clean naming convention (`SM_<AssetName>`, `M_<MaterialName>`, no `.001` leftovers)

## Output Contract

Deliver:

1. **Target Spec & Blender Version Note** — Engine/print constraints and Blender 3.x vs. 4.x API guards.
2. **Step-by-Step Modeling & UV Plan** — Exact dimensions, modifier stack order, and transform-apply gate.
3. **Headless `bmesh` Validation Script** — Runnable `blender --background ... --python validate_mesh.py` audit.
4. **Export Pre-Flight Report** — Mesh metrics (`verts`, `tris`, `ngons`, `non_manifold_edges`, `unapplied_scale`) and export settings.

## Common Traps to Prevent

- **Beveling before applying scale**: produces uneven bevel widths along stretched axes.
- **Using Blender 3.x APIs in Blender 4.x**: never reference removed `mesh.use_auto_smooth` without a version guard (`bpy.app.version < (4, 1, 0)`).
- **Forgetting `Clamp Overlap` / `Harden Normals` on Bevel**: causes self-intersecting geometry and shading artifacts.
