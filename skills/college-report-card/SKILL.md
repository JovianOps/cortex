---
name: college-report-card
description: Generate college report cards with AI assistance, reducing hallucinations and maintaining context.
version: 0.1.0
author: Your Name (github-handle), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [education, report-cards, college, grading, memory]
    related_skills: []
---
# College Report Card Skill

Generate accurate college report cards with AI assistance, reducing hallucinations and maintaining persistent context across sessions.

## When to Use
- Generate student report cards from grades and attendance data
- Create consistent, accurate report cards from structured data
- Maintain grading context across multiple students/sessions
- Reduce hallucinations in grade calculations and comments

## Prerequisites
- Student data in CSV/JSON format (grades, attendance, assignments)
- Course syllabus and grading rubric
- Institution grading policies

## How to Run
```bash
hermes skills install owner/repo/skills/college-report-card
hermes chat -q "Generate report cards for CS101 Fall 2024 from grades.csv"
```

## Commands
| Command | Description |
|---------|-------------|
| `generate-report-cards` | Generate report cards from grade data |
| `validate-grades` | Validate grade data integrity |
| `generate-comments` | Generate personalized comments per student |
| `export-pdf` | Export report cards as PDF |

## Usage Examples
- "Generate report cards for CS101 Fall 2024 from grades.csv using the syllabus rubric"
- "Validate all grades in grades.csv against the syllabus weighting"
- "Generate personalized comments for each student based on performance"