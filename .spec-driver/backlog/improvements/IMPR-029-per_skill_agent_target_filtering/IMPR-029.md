---
id: IMPR-029
name: Per-skill agent target filtering
created: "2026-04-16"
updated: "2026-04-16"
status: idea
kind: improvement
---

# Per-skill agent target filtering

## Summary

Add optional `targets:` field to SKILL.md frontmatter (e.g. `targets: [claude]`)
so `_ensure_target_symlinks` can skip skills for agent targets they don't belong
to. Currently the allowlist is global — every skill syncs to every target.

## Motivation

DE-132 introduced claude-only skills (dispatch, sub-driver) that are inert noise
in `.agents/skills/`. Per-skill targeting would keep target dirs clean.

## Relations

- Motivated by: DE-132 (dispatch/sub-driver are claude-only by intent)
- Applies to: `supekku/scripts/lib/skills/sync.py` (`_ensure_target_symlinks`)

