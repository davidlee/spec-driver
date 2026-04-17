---
id: IMPR-031
name: Installer support for .claude/agents/ — agent sync pipeline
created: "2026-04-17"
updated: "2026-04-17"
status: idea
kind: improvement
---

# Installer support for .claude/agents/ — agent sync pipeline

## Summary

`spec-driver install` currently handles skills (package source → canonical →
symlinks) but has no awareness of `.claude/agents/`. Agent definitions like
`dispatch-worker.md` are committed to git but not managed by the installer.

Add an agent sync step: copy from `supekku/agents/` (package source) to
`.claude/agents/` on install, following the same idempotent pattern as skills.

## Design notes

- Package source: `supekku/agents/*.md`
- Install target: `.claude/agents/` (no symlink chain needed — direct copy)
- Ownership model: same as skills — managed files overwritten on install,
  user-created agents left untouched
- May need an allowlist or naming convention to distinguish managed vs
  user-created agents (e.g. prefix, or a manifest file)
- Consider whether `.agents/` (codex target) needs agent support too

## Touches

- `supekku/scripts/install.py` — add agent sync step
- `supekku/agents/` — new package source directory (create)
- `supekku/agents/dispatch-worker.md` — move from `.claude/agents/`

## Relations

- Motivated by: DE-132 (dispatch-worker agent not managed by installer)
- Related: IMPR-029 (per-skill target filtering — similar ownership question)

