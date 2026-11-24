#!/usr/bin/env python3
"""Offline robots.txt politeness & URL allowance verifier for web-scraper skill."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.robotparser import RobotFileParser


def check_robots(robots_text: str, user_agent: str, urls: list[str]) -> dict:
    rp = RobotFileParser()
    rp.parse(robots_text.splitlines())
    delay = rp.crawl_delay(user_agent)
    results = [{"url": u, "allowed": rp.can_fetch(user_agent, u)} for u in urls]
    blocked = [r["url"] for r in results if not r["allowed"]]
    return {
        "user_agent": user_agent,
        "crawl_delay_seconds": delay,
        "checked": len(results),
        "blocked": blocked,
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check target URLs against a local robots.txt file.")
    parser.add_argument("robots_file", type=Path, help="Path to local robots.txt file.")
    parser.add_argument("urls", nargs="+", help="One or more URLs/paths to test.")
    parser.add_argument("--user-agent", default="*", help="Crawler User-Agent token (default: '*').")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    if not args.robots_file.is_file():
        print(f"ERROR: File not found: {args.robots_file}", file=sys.stderr)
        return 2

    res = check_robots(args.robots_file.read_text(encoding="utf-8"), args.user_agent, args.urls)
    if args.as_json:
        print(json.dumps(res, indent=2))
    else:
        print(f"User-Agent: {res['user_agent']} | Crawl-Delay: {res['crawl_delay_seconds']}s")
        for r in res["results"]:
            status = "ALLOW" if r["allowed"] else "DISALLOW"
            print(f"  [{status}] {r['url']}")
    return 1 if res["blocked"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
