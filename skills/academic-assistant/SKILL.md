---
name: academic-assistant
description: Multi-purpose academic assistant for coding, report cards, 3D modeling with anti-hallucination and persistent memory.
version: 0.1.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [education, coding, 3d-modeling, report-cards, anti-hallucination, memory]
    related_skills: []
---

A comprehensive academic assistant for coding, college report cards, and 3D modeling with built-in anti-hallucination measures and persistent memory management.

## When to Use
- Generate accurate college report cards from structured grade data
- Get coding assistance with anti-hallucination measures
- Get 3D modeling guidance with validation
- Maintain persistent context across sessions to prevent hallucination
- Reduce AI hallucinations through structured validation and deterministic outputs

## Prerequisites
- Student data in CSV/JSON format (grades, attendance, assignments)
- Course syllabus and grading rubric (JSON)
- For 3D modeling: Blender/3D software installed
- Python/PowerShell for report generation scripts

## How to Run
```bash
hermes skills install owner/repo/skills/academic-assistant
hermes chat -q "Generate report cards for CS101 Fall 2024 from grades.csv"
hermes chat -q "Help me write a Python script for data analysis"
hermes chat -q "Guide me through creating a 3D model of a chair in Blender"
```

## Core Capabilities

### 1. College Report Card Generation (Primary)
- Deterministic grade calculation from structured data
- Template-based report card generation (HTML/PDF)
- Data validation to prevent hallucination
- Persistent memory across sessions

### 2. Coding Assistance
- Code review with anti-hallucination checks
- Deterministic code generation from specs
- Best practices enforcement

### 2. 3D Modeling Guidance
- Step-by-step modeling workflows
- Validation checks for model integrity
- Export format validation

### Anti-Hallucination Measures
- Deterministic calculations (no AI math)
- Data validation before processing
- Template-based generation (no free-form generation)
- Structured validation with explicit error reporting
- Source-cited outputs only

### Memory & Context Management
- Persistent context file (`context.json`)
- Student grade cache across sessions
- Course/syllabus context persistence
- Session resumption support

## Commands
| Command | Description |
|---------|-------------|
| `generate-report-cards` | Generate report cards from grade data |
| `validate-grades` | Validate grade data against syllabus |
| `coding-assist` | Coding help with anti-hallucination |
| `3d-model-guide` | 3D modeling step-by-step |
| `validate-data` | Validate data before processing |
| `load-context` | Load persistent context |
| `save-context` | Save current context |

## Usage Examples
- `hermes chat -q "Generate report cards for CS101 Fall 2024 from grades.csv"`
- `hermes chat -q "Help me write a Python script for data analysis with validation"`
- `hermes chat -q "Guide me through creating a low-poly chair in Blender"`
- `hermes chat -q "Load my CS101 context and continue grading"`

## Anti-Hallucination Architecture
1. **Deterministic calculations only** - All math done by code, not LLM
2. **Input validation first** - All data validated before processing
3. **Template-based output** - No free-form generation
4. **Explicit error reporting** - Fail fast with clear messages
4. **Source-cited outputs** - Every number traced to source data

## Memory System
- `context.json` - Course, term, grading policy, student cache
- `grade_cache.json` - Student grades across sessions
- Auto-save after each student processed
- Resume capability with `--continue` flag