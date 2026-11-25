---
name: web-scraper
description: Scrape web data politely with strict schema validation.
version: 2.0.1
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [web-scraping, automation, data-extraction, validation]
    related_skills: [python-coding-assistant, anti-hallucination, testing-automation]
---

# Web Scraper

Build polite, resilient, and anti-hallucination web scraping pipelines that respect `robots.txt`, enforce rate limits and retries, validate every extracted record against a strict schema, and never fabricate missing fields.

## When to Use

- Extracting structured tabular/JSON data from public HTML pages or paginated listings
- Building reproducible, rate-limited scrapers with local HTML caching and schema checks
- Debugging brittle CSS/XPath selectors or adding retry/backoff/encoding resilience

### When Not to Use

- Bypassing authentication walls, CAPTCHAs, paywalls, or sites whose `robots.txt` / Terms of Service disallow automated access

## How to Run

> **Bundled Helper Script (`v1.0.0`):** Run `python skills/web-scraper/scripts/check_robots.py robots.txt /path` to verify `robots.txt` allow/disallow rules and crawl-delay compliance offline.

```bash
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/skills/web-scraper --yes
hermes chat -q "Build a polite Python scraper for product listings with robots.txt check and JSONL export"
```

## Mandatory Scraping Engineering Protocol

### Step 1 — Compliance & Target Inspection First

1. **Prefer structured feeds/APIs first**: Check whether the site exposes public JSON endpoints, RSS/Atom feeds, or embedded JSON-LD (`<script type="application/ld+json">`) before writing brittle HTML selectors.
2. **Enforce `robots.txt` check**: Always inspect `https://<domain>/robots.txt` via `urllib.robotparser.RobotFileParser` using the scraper's real `User-Agent`, and abort disallowed paths cleanly.
3. **Explicit identification**: Always set a descriptive `User-Agent` header (e.g., `CortexScraper/1.0 (+contact@example.com)`).

### Step 2 — Resilient Networking & Politeness Guards

Every scraper MUST include:

- **Explicit timeouts**: Always set connect + read timeouts (`timeout=(5, 15)`) — never hang indefinitely.
- **Per-domain rate limiting + jitter**: Respect `Crawl-delay` from `robots.txt` or default to `>= 1.0s` + random jitter between requests.
- **Bounded retries with exponential backoff**: Retry only idempotent `GET` requests on transient errors (`429`, `500`, `502`, `503`, `504`, network timeouts), honoring the `Retry-After` header when present, with a strict max-retry cap (`<= 3`).
- **Disk caching for development**: Save raw HTML snapshots locally during parsing development so selector iteration does not hammer the origin server.
- **Pagination cycle guard**: Track visited canonical URLs in a `set` and enforce a hard `max_pages` cap to prevent infinite pagination loops.

### Step 3 — Anti-Hallucination Extraction & Schema Validation

1. **Strict extraction rule**: Extract **only** values literally present in the fetched DOM/JSON. If a selector returns `None`, record `None` (and log a selector-miss warning) — **never infer, synthesize, or default missing prices, dates, or ratings**.
2. **Explicit normalization**: Preserve raw extracted strings alongside parsed values (e.g., `price_raw: "$19.99"`, `price_decimal: "19.99"`, `currency: "USD"`) using `Decimal` for monetary amounts.
3. **Schema validation**: Validate every record using a `dataclass` or Pydantic model before writing to JSONL/CSV; quarantine invalid records into `rejected.jsonl` with exact URL and validation error.
4. **Provenance fields**: Include `source_url` and `fetched_at` (UTC ISO-8601) on every extracted record.

### Step 4 — Selector Unit Test with Saved HTML Fixture

Always test extraction logic against a saved static HTML fixture (no live network required) covering a complete item, a missing optional field (`None`, no crash), and a malformed price string (quarantined cleanly):

```python
from decimal import Decimal, InvalidOperation
from urllib.robotparser import RobotFileParser

def can_fetch_url(robots_url: str, user_agent: str, target_url: str) -> bool:
    rp = RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    return rp.can_fetch(user_agent, target_url)

def parse_price(raw: str | None) -> Decimal | None:
    if not raw:
        return None
    cleaned = raw.strip().lstrip("$€£").replace(",", "")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None
```

## Output Contract

Deliver:

1. **Scraper Script** — Typed Python script with `robots.txt` gate, rate limiting, retries, schema validation, and JSONL/CSV writer.
2. **Fixture Test** — Offline unit test verifying selectors and missing-field handling.
3. **Run Audit Summary** — Pages fetched, records valid, records quarantined, selector-miss counts, and output file path.
