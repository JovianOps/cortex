#!/usr/bin/env python3
"""Cortex Studio — Zero-dependency Light/Dark Swiss local web workbench for Cortex v2.0.0."""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
VERSION = "2.0.0"


def load_local(name: str):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"cortex_studio_{name}", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


STUDIO_HTML = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Cortex Studio v2.0.0 — Local Workbench</title>
  <style>
    :root, [data-theme="light"] {
      --bg: #ffffff; --surface: #f7f7f5; --surface-2: #efefec;
      --fg: #111111; --muted: #595954; --border: #e2e2dc; --border-strong: #111111;
      --accent: #d9381e; --accent-fg: #ffffff; --ok: #15803d; --warn: #b45309; --bad: #b91c1c;
      --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      --sans: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Helvetica, Arial, sans-serif;
    }
    [data-theme="dark"] {
      --bg: #0e0e0d; --surface: #161614; --surface-2: #1f1f1c;
      --fg: #f4f4f0; --muted: #a1a19a; --border: #2a2a26; --border-strong: #f4f4f0;
      --accent: #f05a3a; --accent-fg: #0e0e0d; --ok: #4ade80; --warn: #fbbf24; --bad: #f87171;
    }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: var(--sans); background: var(--bg); color: var(--fg); line-height: 1.5; }
    header { position: sticky; top: 0; z-index: 20; background: var(--bg); border-bottom: 2px solid var(--border-strong); padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
    .brand { display: flex; align-items: baseline; gap: 10px; }
    .brand h1 { margin: 0; font-size: 16px; letter-spacing: 0.08em; text-transform: uppercase; font-weight: 800; }
    .badge { font-family: var(--mono); font-size: 11px; padding: 2px 7px; border: 1px solid var(--border-strong); text-transform: uppercase; }
    .badge.accent { background: var(--accent); color: var(--accent-fg); border-color: var(--accent); }
    nav { display: flex; gap: 4px; flex-wrap: wrap; }
    button { font-family: var(--mono); font-size: 12px; cursor: pointer; border: 1px solid var(--border); background: var(--surface); color: var(--fg); padding: 7px 12px; transition: background 0.12s; }
    button:hover { border-color: var(--border-strong); }
    button.active, button.primary { background: var(--fg); color: var(--bg); border-color: var(--fg); }
    button.accent-btn { background: var(--accent); color: var(--accent-fg); border-color: var(--accent); font-weight: 700; }
    .theme-seg { display: inline-flex; border: 1px solid var(--border-strong); }
    .theme-seg button { border: 0; padding: 6px 10px; }
    main { max-width: 1320px; margin: 0 auto; padding: 24px; }
    .panel { display: none; }
    .panel.active { display: block; }
    .grid-4 { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 12px; margin-bottom: 20px; }
    .kpi { border: 1px solid var(--border); background: var(--surface); padding: 16px; }
    .kpi-label { font-family: var(--mono); font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; }
    .kpi-val { font-size: 28px; font-weight: 800; margin-top: 6px; letter-spacing: -0.02em; }
    .split { display: grid; grid-template-columns: 360px 1fr; gap: 16px; }
    @media (max-width: 900px) { .split { grid-template-columns: 1fr; } }
    .box { border: 1px solid var(--border); background: var(--surface); padding: 16px; }
    .box h2, .box h3 { margin: 0 0 12px; font-size: 13px; font-family: var(--mono); text-transform: uppercase; letter-spacing: 0.08em; }
    input, select, textarea { width: 100%; font-family: var(--mono); font-size: 12px; padding: 8px 10px; border: 1px solid var(--border); background: var(--bg); color: var(--fg); margin-bottom: 10px; }
    .list { max-height: 540px; overflow: auto; border: 1px solid var(--border); background: var(--bg); }
    .row { padding: 10px 12px; border-bottom: 1px solid var(--border); cursor: pointer; display: flex; justify-content: space-between; align-items: center; gap: 8px; }
    .row:hover, .row.selected { background: var(--surface-2); }
    .row-title { font-family: var(--mono); font-size: 12px; font-weight: 700; }
    .row-sub { font-size: 12px; color: var(--muted); margin-top: 2px; }
    pre { font-family: var(--mono); font-size: 12px; background: var(--bg); border: 1px solid var(--border); padding: 14px; overflow: auto; max-height: 460px; white-space: pre-wrap; word-break: break-word; margin: 10px 0 0; }
    .status-ok { color: var(--ok); font-weight: 700; }
    .status-bad { color: var(--bad); font-weight: 700; }
    .toolbar { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-bottom: 12px; }
    .checks { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 12px; font-family: var(--mono); font-size: 12px; }
    .checks label { display: inline-flex; align-items: center; gap: 5px; cursor: pointer; }
    .checks input { width: auto; margin: 0; }
    table { width: 100%; border-collapse: collapse; font-size: 12px; font-family: var(--mono); }
    th, td { border-bottom: 1px solid var(--border); text-align: left; padding: 8px; }
    th { font-size: 11px; text-transform: uppercase; color: var(--muted); }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <h1>Cortex Studio</h1>
      <span class="badge accent">v2.0.0</span>
      <span class="badge" id="wsBadge">workspace</span>
    </div>
    <nav id="tabs">
      <button type="button" class="active" data-tab="overview">01 / Overview</button>
      <button type="button" data-tab="skills">02 / Skills (36)</button>
      <button type="button" data-tab="runner">03 / Tool Runner</button>
      <button type="button" data-tab="compiler">04 / Compiler</button>
      <button type="button" data-tab="scanner">05 / Policy &amp; SARIF</button>
      <button type="button" data-tab="mcp">06 / MCP Server</button>
    </nav>
    <div class="theme-seg" role="group" aria-label="Color theme">
      <button type="button" id="btnLight" class="active">Light</button>
      <button type="button" id="btnDark">Dark</button>
    </div>
  </header>

  <main>
    <section id="tab-overview" class="panel active">
      <div class="grid-4" id="kpiGrid"></div>
      <div class="box">
        <div class="toolbar">
          <h2 style="margin:0;">Supply-Chain Integrity &amp; Workspace Checks</h2>
          <button type="button" class="accent-btn" id="btnRunVerify">Run cortex verify</button>
        </div>
        <pre id="verifyOut">Loading overview...</pre>
      </div>
    </section>

    <section id="tab-skills" class="panel">
      <div class="split">
        <div class="box">
          <h2>Skill Catalog</h2>
          <input type="search" id="skillFilter" placeholder="Filter by slug, tier, or script..." />
          <div class="list" id="skillList"></div>
        </div>
        <div class="box">
          <div class="toolbar">
            <h2 id="detailTitle" style="margin:0;">Select a skill</h2>
            <button type="button" id="btnShowMd" class="active">SKILL.md</button>
            <button type="button" id="btnShowPy">Bundled Script</button>
          </div>
          <div id="detailMeta" style="font-family:var(--mono);font-size:12px;color:var(--muted);"></div>
          <pre id="detailCode">Pick any skill on the left to inspect its SKILL.md, SHA-256 fingerprint, and bundled Python verifier.</pre>
        </div>
      </div>
    </section>

    <section id="tab-runner" class="panel">
      <div class="box">
        <h2>Execute Any Bundled Python Verifier Live</h2>
        <div class="toolbar">
          <select id="runnerSkill" style="max-width:300px;margin:0;"></select>
          <input type="text" id="runnerTarget" value="." placeholder="Relative path inside workspace" style="max-width:340px;margin:0;" />
          <button type="button" class="accent-btn" id="btnExecTool">Run Verifier</button>
        </div>
        <pre id="runnerOut">Select a skill verifier and click Run Verifier.</pre>
      </div>
    </section>

    <section id="tab-compiler" class="panel">
      <div class="box">
        <h2>Universal Agent Rule Compiler (cortex compile)</h2>
        <div class="toolbar">
          <select id="compilePack" style="max-width:260px;margin:0;"></select>
          <button type="button" id="btnCompileDry">Preview (Dry Run)</button>
          <button type="button" class="accent-btn" id="btnCompileWrite">Compile &amp; Write Files</button>
        </div>
        <div class="checks" id="compileTargets">
          <label><input type="checkbox" value="cursor" checked /> Cursor (.cursor/rules/*.mdc)</label>
          <label><input type="checkbox" value="vscode" checked /> VS Code (.github/instructions/*.instructions.md)</label>
          <label><input type="checkbox" value="windsurf" /> Windsurf (.windsurf/rules/*.md)</label>
          <label><input type="checkbox" value="cline" /> Cline (.clinerules/*.md)</label>
          <label><input type="checkbox" value="claude" /> CLAUDE.md</label>
          <label><input type="checkbox" value="agents" /> AGENTS.md</label>
          <label><input type="checkbox" value="gemini" /> GEMINI.md</label>
        </div>
        <pre id="compileOut">Choose a pack and target formats to preview or generate native agent rule files.</pre>
      </div>
    </section>

    <section id="tab-scanner" class="panel">
      <div class="box">
        <h2>Unified Policy &amp; SARIF 2.1.0 Repository Scanner</h2>
        <div class="toolbar">
          <select id="scanFailOn" style="max-width:180px;margin:0;">
            <option value="high" selected>fail-on: high</option>
            <option value="critical">fail-on: critical</option>
            <option value="medium">fail-on: medium</option>
            <option value="low">fail-on: low</option>
            <option value="none">fail-on: none</option>
          </select>
          <button type="button" class="accent-btn" id="btnRunScan">Run Unified Scan</button>
          <button type="button" id="btnDownloadSarif">Download SARIF 2.1.0</button>
        </div>
        <pre id="scanOut">Click Run Unified Scan to audit this workspace across Cortex's bundled security, IaC, PII, SBOM, and resilience verifiers.</pre>
      </div>
    </section>

    <section id="tab-mcp" class="panel">
      <div class="box">
        <h2>Model Context Protocol (MCP) Client Configuration</h2>
        <div class="toolbar">
          <select id="mcpClient" style="max-width:220px;margin:0;">
            <option value="vscode">Visual Studio Code (.vscode/mcp.json)</option>
            <option value="claude-code">Claude Code (.mcp.json)</option>
            <option value="cursor">Cursor (.cursor/mcp.json)</option>
            <option value="codex">OpenAI Codex CLI</option>
            <option value="windsurf">Windsurf</option>
          </select>
          <button type="button" class="primary" id="btnLoadMcp">Generate Config</button>
        </div>
        <pre id="mcpOut">Loading MCP configuration...</pre>
      </div>
    </section>
  </main>

  <script>
    const state = { skills: [], packs: {}, selectedSkill: null, viewMode: "md", lastSarif: null };
    const $ = (id) => document.getElementById(id);

    function setTheme(theme) {
      document.documentElement.setAttribute("data-theme", theme);
      $("btnLight").classList.toggle("active", theme === "light");
      $("btnDark").classList.toggle("active", theme === "dark");
      try { localStorage.setItem("cortex-studio-theme", theme); } catch (_) {}
    }
    $("btnLight").onclick = () => setTheme("light");
    $("btnDark").onclick = () => setTheme("dark");
    try { const saved = localStorage.getItem("cortex-studio-theme"); if (saved) setTheme(saved); } catch (_) {}

    document.querySelectorAll("#tabs button").forEach((btn) => {
      btn.onclick = () => {
        document.querySelectorAll("#tabs button").forEach((b) => b.classList.remove("active"));
        document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
        btn.classList.add("active");
        $("tab-" + btn.dataset.tab).classList.add("active");
      };
    });

    async function api(path, opts) {
      const res = await fetch(path, opts);
      return res.json();
    }

    function renderSkillList() {
      const q = $("skillFilter").value.trim().toLowerCase();
      const box = $("skillList");
      box.textContent = "";
      state.skills
        .filter((s) => !q || s.slug.includes(q) || s.tier.includes(q) || s.description.toLowerCase().includes(q) || (s.scripts[0] || "").toLowerCase().includes(q))
        .forEach((s) => {
          const row = document.createElement("div");
          row.className = "row" + (state.selectedSkill && state.selectedSkill.slug === s.slug ? " selected" : "");
          const left = document.createElement("div");
          const t = document.createElement("div"); t.className = "row-title"; t.textContent = s.slug;
          const sub = document.createElement("div"); sub.className = "row-sub"; sub.textContent = s.description;
          left.appendChild(t); left.appendChild(sub);
          const tag = document.createElement("span"); tag.className = "badge"; tag.textContent = s.tier;
          row.appendChild(left); row.appendChild(tag);
          row.onclick = () => loadSkillDetail(s.slug);
          box.appendChild(row);
        });
    }

    async function loadSkillDetail(slug) {
      const data = await api("/api/skills/" + encodeURIComponent(slug));
      state.selectedSkill = data;
      $("detailTitle").textContent = data.slug + " (" + data.tier + ")";
      $("detailMeta").textContent = "SHA-256: " + (data.sha256 || "n/a") + "  |  Script: " + (data.scripts[0] || "none");
      renderDetailCode();
      renderSkillList();
    }

    function renderDetailCode() {
      if (!state.selectedSkill) return;
      $("btnShowMd").classList.toggle("active", state.viewMode === "md");
      $("btnShowPy").classList.toggle("active", state.viewMode === "py");
      $("detailCode").textContent = state.viewMode === "md" ? state.selectedSkill.skill_md : (state.selectedSkill.script_source || "No bundled script.");
    }
    $("btnShowMd").onclick = () => { state.viewMode = "md"; renderDetailCode(); };
    $("btnShowPy").onclick = () => { state.viewMode = "py"; renderDetailCode(); };
    $("skillFilter").oninput = renderSkillList;

    $("btnRunVerify").onclick = async () => {
      $("verifyOut").textContent = "Running cortex verify --json ...";
      const data = await api("/api/verify");
      $("verifyOut").textContent = JSON.stringify(data, null, 2);
    };

    $("btnExecTool").onclick = async () => {
      $("runnerOut").textContent = "Running verifier...";
      const data = await api("/api/run-tool", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ slug: $("runnerSkill").value, target: $("runnerTarget").value }),
      });
      $("runnerOut").textContent = JSON.stringify(data, null, 2);
    };

    async function runCompile(dryRun) {
      const targets = Array.from(document.querySelectorAll("#compileTargets input:checked")).map((i) => i.value);
      $("compileOut").textContent = "Compiling rules...";
      const data = await api("/api/compile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pack: $("compilePack").value, targets, dry_run: dryRun }),
      });
      $("compileOut").textContent = JSON.stringify(data, null, 2);
    }
    $("btnCompileDry").onclick = () => runCompile(true);
    $("btnCompileWrite").onclick = () => runCompile(false);

    $("btnRunScan").onclick = async () => {
      $("scanOut").textContent = "Running unified multi-tool repository scan...";
      const data = await api("/api/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fail_on: $("scanFailOn").value }),
      });
      state.lastSarif = data.sarif || null;
      $("scanOut").textContent = JSON.stringify(data.report || data, null, 2);
    };

    $("btnDownloadSarif").onclick = () => {
      if (!state.lastSarif) { $("scanOut").textContent = "Run Unified Scan first to generate SARIF 2.1.0 output."; return; }
      const blob = new Blob([JSON.stringify(state.lastSarif, null, 2)], { type: "application/sarif+json" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "cortex-scan.sarif";
      a.click();
    };

    async function loadMcp() {
      const client = $("mcpClient").value;
      const data = await api("/api/mcp-config?client=" + encodeURIComponent(client));
      $("mcpOut").textContent = JSON.stringify(data, null, 2);
    }
    $("btnLoadMcp").onclick = loadMcp;
    $("mcpClient").onchange = loadMcp;

    async function boot() {
      const [ov, sk, pk] = await Promise.all([api("/api/overview"), api("/api/skills"), api("/api/packs")]);
      $("wsBadge").textContent = ov.workspace;
      const kpis = [
        ["Skills", ov.skill_count],
        ["Bundled Scripts", ov.script_count + "/" + ov.skill_count],
        ["Role Packs", ov.pack_count],
        ["MCP Tools", ov.mcp_tool_count],
      ];
      const grid = $("kpiGrid");
      grid.textContent = "";
      kpis.forEach(([k, v]) => {
        const d = document.createElement("div"); d.className = "kpi";
        const l = document.createElement("div"); l.className = "kpi-label"; l.textContent = k;
        const val = document.createElement("div"); val.className = "kpi-val"; val.textContent = String(v);
        d.appendChild(l); d.appendChild(val); grid.appendChild(d);
      });
      $("verifyOut").textContent = JSON.stringify(ov, null, 2);

      state.skills = sk.skills || [];
      renderSkillList();
      const sel = $("runnerSkill");
      sel.textContent = "";
      state.skills.forEach((s) => {
        const opt = document.createElement("option");
        opt.value = s.slug;
        opt.textContent = s.slug + " (" + (s.scripts[0] || "no script") + ")";
        sel.appendChild(opt);
      });
      if (state.skills.length) loadSkillDetail(state.skills[0].slug);

      state.packs = pk.packs || {};
      const pSel = $("compilePack");
      pSel.textContent = "";
      Object.entries(state.packs).forEach(([id, meta]) => {
        const opt = document.createElement("option");
        opt.value = id;
        opt.textContent = id + " — " + meta.label;
        pSel.appendChild(opt);
      });
      loadMcp();
    }
    boot();
  </script>
</body>
</html>
"""


def make_handler(workspace_dir: Path):
    mcp_mod = load_local("cortex_mcp")
    compile_mod = load_local("cortex_compile")
    scan_mod = load_local("cortex_scan")
    mcp_server = mcp_mod.CortexMCPServer(workspace_dir)

    class StudioHandler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
            return

        def _send_json(self, payload: Any, status: int = HTTPStatus.OK) -> None:
            raw = json.dumps(payload, indent=2).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def _send_html(self, html: str) -> None:
            raw = html.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def _read_json_body(self) -> dict:
            length = int(self.headers.get("Content-Length", "0") or "0")
            raw = self.rfile.read(length) if length > 0 else b"{}"
            return json.loads(raw.decode("utf-8")) if raw else {}

        def do_GET(self) -> None:
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path
            qs = urllib.parse.parse_qs(parsed.query)

            if path in {"/", "/index.html"}:
                self._send_html(STUDIO_HTML)
                return

            if path == "/api/overview":
                packs_data = json.loads((ROOT / "packs.json").read_text(encoding="utf-8"))
                skills = list(mcp_server.skills.values())
                self._send_json({
                    "version": VERSION,
                    "workspace": workspace_dir.as_posix(),
                    "skill_count": len(skills),
                    "script_count": sum(1 for s in skills if s["scripts"]),
                    "pack_count": len(packs_data.get("packs", {})),
                    "mcp_tool_count": len(mcp_server.tool_definitions()),
                    "compile_targets": list(compile_mod.SUPPORTED_TARGETS),
                    "scanners": [s[0] for s in scan_mod.SCANNER_SPECS],
                })
                return

            if path == "/api/skills":
                self._send_json({"count": len(mcp_server.skills), "skills": list(mcp_server.skills.values())})
                return

            if path.startswith("/api/skills/"):
                slug = urllib.parse.unquote(path.removeprefix("/api/skills/")).strip().lower()
                if slug not in mcp_server.skills:
                    self._send_json({"error": f"Unknown skill: {slug}"}, HTTPStatus.NOT_FOUND)
                    return
                meta = dict(mcp_server.skills[slug])
                meta["skill_md"] = Path(meta["skill_path"]).read_text(encoding="utf-8")
                script_src = ""
                if meta["scripts"]:
                    sp = ROOT / meta["dir"] / slug / meta["scripts"][0]
                    if sp.is_file():
                        script_src = sp.read_text(encoding="utf-8")
                meta["script_source"] = script_src
                self._send_json(meta)
                return

            if path == "/api/packs":
                self._send_json(json.loads((ROOT / "packs.json").read_text(encoding="utf-8")))
                return

            if path == "/api/verify":
                res = subprocess.run(
                    [sys.executable, str(SCRIPTS / "cortex.py"), "verify", "--project-dir", str(workspace_dir), "--json"],
                    cwd=ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                payload = json.loads(res.stdout) if res.stdout.strip().startswith("{") else {"ok": res.returncode == 0, "stdout": res.stdout, "stderr": res.stderr}
                self._send_json(payload)
                return

            if path == "/api/mcp-config":
                client = (qs.get("client") or ["vscode"])[0]
                self._send_json(mcp_mod.client_mcp_config(client, workspace_dir))
                return

            self._send_json({"error": f"Not found: {path}"}, HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path
            try:
                body = self._read_json_body()
                if path == "/api/run-tool":
                    out = mcp_server.call_tool("cortex_run_verifier", body)
                    self._send_json(out)
                    return
                if path == "/api/compile":
                    out = mcp_server.call_tool("cortex_compile_rules", body)
                    self._send_json(out)
                    return
                if path == "/api/scan":
                    pol = scan_mod.load_policy(None, workspace_dir)
                    report = scan_mod.run_scan(workspace_dir, only=body.get("only") or None, policy=pol, fail_on_override=body.get("fail_on"))
                    self._send_json({"report": report, "sarif": scan_mod.to_sarif(report)})
                    return
                self._send_json({"error": f"Not found: {path}"}, HTTPStatus.NOT_FOUND)
            except Exception as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)

    return StudioHandler


def create_server(host: str, port: int, workspace_dir: Path) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), make_handler(workspace_dir.resolve()))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Launch Cortex Studio — zero-dependency local Light/Dark Swiss web workbench.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (use 0.0.0.0 for remote/container previews).")
    parser.add_argument("--port", type=int, default=4310, help="TCP port to listen on (default: 4310).")
    parser.add_argument("--project-dir", type=Path, default=Path.cwd(), help="Workspace directory to inspect.")
    args = parser.parse_args(argv)

    server = create_server(args.host, args.port, args.project_dir)
    actual_port = server.server_address[1]
    print(f"Cortex Studio v{VERSION} running at http://{args.host}:{actual_port} (workspace: {args.project_dir.resolve()})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Cortex Studio.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
