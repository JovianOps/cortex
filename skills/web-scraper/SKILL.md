---
name: web-scraper
description: Web scraping with validation, rate limiting, and anti-hallucination extraction.
version: 0.1.0
author: Your Name (github-handle), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [web-scraping, automation, data-extraction]
    related_skills: [python-coding-assistant]
---
# Web Scraper Skill

Web scraping with validation, rate limiting, and anti-hallucination extraction.

## When to Use
- Extract structured data from websites
- Automate data collection
- Validate extracted data

## Prerequisites
- Python with requests/beautifulsoup4/selenium

## How to Run
```bash
hermes skills install owner/repo/skills/web-scraper
hermes chat -q "Scrape product data from example.com with validation"
```

## Features
- Rate limiting & polite scraping
- Data validation & schema enforcement
- Anti-hallucination: only extract what's present
- Robots.txt compliance
- Session persistence