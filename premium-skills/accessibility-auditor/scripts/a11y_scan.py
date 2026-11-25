#!/usr/bin/env python3
"""Deterministic static HTML/CSS WCAG 2.2 AA accessibility scanner.

Zero external dependencies (Python 3 stdlib only).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


class A11yHTMLAuditor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.findings: list[dict] = []
        self.has_html_lang = False
        self.has_title = False
        self.last_heading_level = 0
        self.label_fors: set[str] = set()
        self.inputs: list[tuple[int, dict[str, str | None]]] = []
        self._in_label = 0
        self._in_style = False
        self._style_chunks: list[tuple[int, str]] = []

    def add(self, severity: str, wcag: str, rule: str, line: int, message: str) -> None:
        self.findings.append({
            "severity": severity,
            "wcag": wcag,
            "rule": rule,
            "line": line,
            "message": message,
        })

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        line, _ = self.getpos()
        attrs = {k.lower(): v for k, v in attrs_list}
        t = tag.lower()

        if t == "html" and attrs.get("lang"):
            self.has_html_lang = True
        elif t == "title":
            self.has_title = True
        elif t == "label":
            self._in_label += 1
            if attrs.get("for"):
                self.label_fors.add(attrs["for"] or "")
        elif t == "style":
            self._in_style = True
        elif t == "img":
            if "alt" not in attrs and attrs.get("aria-hidden") != "true":
                self.add("SERIOUS", "1.1.1 A", "img-alt", line, "<img> is missing an alt attribute.")
        elif t in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = int(t[1])
            if self.last_heading_level and level > self.last_heading_level + 1:
                self.add(
                    "MODERATE",
                    "1.3.1 A",
                    "heading-order",
                    line,
                    f"Skipped heading level: <h{self.last_heading_level}> followed by <h{level}>.",
                )
            self.last_heading_level = level
        elif t in {"div", "span"} and "onclick" in attrs and "role" not in attrs:
            self.add(
                "BLOCKER",
                "2.1.1 A",
                "non-semantic-click",
                line,
                f"<{t} onclick=...> lacks keyboard semantics; use <button type=\"button\"> instead.",
            )
        elif t == "button" and "type" not in attrs:
            self.add("MINOR", "4.1.2 A", "button-type", line, "<button> is missing an explicit type attribute.")
        elif t in {"input", "select", "textarea"}:
            if t == "input" and (attrs.get("type") or "").lower() in {"hidden", "submit", "button", "reset"}:
                pass
            elif self._in_label == 0 and not (attrs.get("aria-label") or attrs.get("aria-labelledby")):
                self.inputs.append((line, attrs))

        if "tabindex" in attrs:
            try:
                ti = int(attrs["tabindex"] or "0")
                if ti > 0:
                    self.add("SERIOUS", "2.4.3 A", "positive-tabindex", line, f"Positive tabindex={ti} breaks natural focus order.")
            except ValueError:
                pass

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        if t == "label" and self._in_label > 0:
            self._in_label -= 1
        elif t == "style":
            self._in_style = False

    def handle_data(self, data: str) -> None:
        if self._in_style:
            line, _ = self.getpos()
            self._style_chunks.append((line, data))

    def finalize(self) -> list[dict]:
        if not self.has_html_lang:
            self.add("SERIOUS", "3.1.1 A", "html-lang", 1, "<html> element is missing a lang attribute.")
        if not self.has_title:
            self.add("SERIOUS", "2.4.2 A", "document-title", 1, "Document is missing a <title> element.")
        for line, attrs in self.inputs:
            input_id = attrs.get("id")
            if not input_id or input_id not in self.label_fors:
                self.add(
                    "SERIOUS",
                    "1.3.1 A",
                    "form-label",
                    line,
                    "Form control lacks a matching <label for>, aria-label, or aria-labelledby.",
                )
        css_all = "\n".join(chunk for _, chunk in self._style_chunks)
        if re.search(r"outline\s*:\s*(?:none|0)\b", css_all) and ":focus-visible" not in css_all:
            self.add(
                "SERIOUS",
                "2.4.7 AA",
                "focus-outline",
                self._style_chunks[0][0] if self._style_chunks else 1,
                "CSS removes outline without providing a :focus-visible replacement.",
            )
        return self.findings


def scan_html(path: Path) -> list[dict]:
    auditor = A11yHTMLAuditor()
    auditor.feed(path.read_text(encoding="utf-8", errors="replace"))
    return auditor.finalize()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Static WCAG 2.2 AA HTML accessibility scanner.")
    parser.add_argument("html_file", type=Path, help="Path to HTML file to audit.")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON output.")
    args = parser.parse_args(argv)
    if not args.html_file.is_file():
        print(f"ERROR: File not found: {args.html_file}", file=sys.stderr)
        return 2
    findings = scan_html(args.html_file)
    blockers_or_serious = [f for f in findings if f["severity"] in {"BLOCKER", "SERIOUS"}]
    if args.as_json:
        print(json.dumps({"file": args.html_file.as_posix(), "count": len(findings), "findings": findings}, indent=2))
    else:
        print(f"# Accessibility Scan ({len(findings)} finding(s))\n")
        for f in findings:
            print(f"- **[{f['severity']}] {f['rule']} (WCAG {f['wcag']})** — `{args.html_file}:{f['line']}`: {f['message']}")
        if not findings:
            print(f"OK: {args.html_file} passed all static WCAG 2.2 AA checks.")
    return 1 if blockers_or_serious else 0


if __name__ == "__main__":
    raise SystemExit(main())
