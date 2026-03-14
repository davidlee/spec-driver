---
id: mem.pattern.git.spec-driver-commit-cleanliness
name: Keep .spec-driver commits small and the worktree clean
kind: memory
status: active
memory_type: pattern
updated: "2026-03-08"
verified: "2026-03-08"
tags:
  - git
  - commit
  - spec-driver
  - workflow
  - doctrine
summary: In this repo, prefer frequent, small `.spec-driver` commits and a clean
  working tree; when `.spec-driver` changes and code changes both exist, commit
  them together or separately based on what naturally goes out first.
priority:
  severity: high
  weight: 8
scope:
  commands:
    - git commit
  paths:
    - .spec-driver/hooks/doctrine.md
    - supekku/templates/hooks/doctrine.md
    - supekku/skills/execute-phase/SKILL.md
    - supekku/skills/notes/SKILL.md
    - supekku/skills/close-change/SKILL.md
    - supekku/skills/continuation/SKILL.md
provenance:
  sources:
    - kind: delta
      ref: DE-055
    - kind: doc
      note: Template hook seed
      ref: supekku/templates/hooks/doctrine.md
    - kind: doc
      note: Local repo doctrine hook
      ref: .spec-driver/hooks/doctrine.md
---

# Keep .spec-driver commits small and the worktree clean

## Summary

- Prefer frequent, small `.spec-driver/**` commits.
- Bias toward a clean working tree over waiting for perfectly related
  `.spec-driver` batches.
- When `.spec-driver/**` changes and code changes both exist, commit them
  together or separately based on what naturally gets committed first.
- Use short, conventional commit messages by default, for example:
  `fix(DE-093): address memory leaks in flux capacitor`.

## Context

- This is a repo-local doctrine preference, not a universal package rule.
- Packaged skills should defer to doctrine for the final policy, and the hook
  template now seeds the same commit-policy seam for fresh installs.
