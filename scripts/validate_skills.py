#!/usr/bin/env python3
import yaml
import sys
import os
import glob

errors = []
warnings = []

for skill_file in glob.glob('skills/**/SKILL.md', recursive=True):
    print(f'Checking {skill_file}...')
    try:
        with open(skill_file, 'r') as f:
            content = f.read()

        if not content.startswith('---'):
            errors.append(f'{skill_file}: Missing frontmatter (must start with ---)')
            continue

        parts = content.split('---', 2)
        if len(parts) < 3:
            errors.append(f'{skill_file}: Invalid frontmatter structure')
            continue

        fm = yaml.safe_load(parts[1])

        # Required fields
        for field in ['name', 'description', 'version', 'author', 'license', 'platforms']:
            if field not in fm:
                errors.append(f'{skill_file}: Missing required field: {field}')

        if 'metadata' in fm and 'hermes' in fm['metadata']:
            hermes = fm['metadata']['hermes']
            if 'tags' not in hermes:
                warnings.append(f'{skill_file}: Missing hermes.tags')
            if 'related_skills' not in fm['metadata']['hermes']:
                warnings.append(f'{skill_file}: Missing hermes.related_skills')

        # Description length check
        if 'description' in fm and len(fm['description']) > 60:
            warnings.append(f'{skill_file}: Description > 60 chars ({len(fm["description"])} chars)')

        if 'description' in fm and not fm['description'].endswith('.'):
            warnings.append(f'{skill_file}: Description should end with period')

        # Check platforms
        valid_platforms = {'linux', 'macos', 'windows'}
        if 'platforms' in fm:
            for p in fm['platforms']:
                if p not in valid_platforms:
                    warnings.append(f'{skill_file}: Unknown platform: {p}')

    except yaml.YAMLError as e:
        errors.append(f'{skill_file}: Invalid YAML: {e}')
    except Exception as e:
        errors.append(f'{skill_file}: {e}')

if warnings:
    for w in warnings:
        print(f'::warning file={skill_file}::{w}')

if errors:
    for e in errors:
        print(f'::error::{e}')
    sys.exit(1)

print('All SKILL.md files validated successfully!')