---
id: IP-071.PHASE-02
slug: 071-install-feedback
name: 'P02: Install skill-change feedback'
created: '2026-03-09'
updated: '2026-03-09'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-071.PHASE-02
plan: IP-071
delta: DE-071
objective: >-
  Surface sync_skills result in install command output so users see what changed.
entrance_criteria:
  - P01 complete (skills group removed)
exit_criteria:
  - install reports skill install/prune/symlink changes
  - tests pass, linters clean
verification:
  tests:
    - VT-071-04
  evidence: []
tasks:
  - id: '2.1'
    description: Capture and format sync_skills result in install
  - id: '2.2'
    description: Test install skill-change output
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-071.PHASE-02
```

# Phase 2 — Install Skill-Change Feedback

## 1. Objective

Surface the `sync_skills()` return value in `install` output.

## 2. Links & References

- **Delta**: [DE-071](../DE-071.md)
- **Design Revision**: [DR-071](../DR-071.md) §4.1

## 3. Entrance Criteria

- [ ] P01 complete

## 4. Exit Criteria / Done When

- [ ] `spec-driver install` prints skill changes (installed/pruned/up-to-date)
- [ ] Tests pass, linters clean

## 5. Tasks

| Status | ID | Description | Notes |
|--------|-----|-------------|-------|
| [ ] | 2.1 | Capture `sync_skills()` result in `install.py`, print summary | Reuse pattern from deleted `skills.py` |
| [ ] | 2.2 | Test install skill-change output | |

### Detail

- **2.1**: In `supekku/scripts/install.py` ~line 745, capture the `sync_skills()`
  return value and print a "Skills:" section. The result dict has `canonical`
  (installed/pruned), `symlinks`, `agents_md_changed`, `written`, `warnings`.
  Print concise summary lines matching the style of other install output.
