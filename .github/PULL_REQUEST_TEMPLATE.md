## Summary
<!-- Briefly describe what changed and why. -->

## Type of Change
- [ ] Bug fix
- [ ] New skill or bundled helper script
- [ ] CLI / installer / manifest improvement
- [ ] Documentation or website (`index.html`) update
- [ ] CI / security hardening

## Verification Checklist
- [ ] `python3 scripts/package_skills.py --check` passes (re-ran `package_skills.py` if any skill/script changed)
- [ ] `python3 scripts/validate_skills.py` and `python3 scripts/validate_manifests.py` pass
- [ ] `python3 scripts/eval_skills.py` scores 100/100 across all skills
- [ ] `python3 scripts/verify_site.py` passes (JS syntax, `checksums.json` parity, WCAG 2.2 AA)
- [ ] `python3 -m unittest discover -s tests -v` passes
- [ ] Any GitHub Actions edits are pinned to 40-char commit SHAs (`lint_actions.py` passes)
