---
id: IMPR-030
name: Remove skills.allowlist — install all package skills by default
created: "2026-04-17"
updated: "2026-04-17"
status: idea
kind: improvement
---

# Remove skills.allowlist — install all package skills by default

## Summary

The allowlist adds friction to upgrades — every new skill requires a manual
allowlist entry. Remove it; install all skills from `supekku/skills/` by default.

## Touches

- `supekku/scripts/lib/skills/sync.py` — `parse_allowlist`, `sync_skills`
- `supekku/scripts/lib/skills/sync_test.py` — allowlist-related tests
- `.spec-driver/skills.allowlist` — delete

