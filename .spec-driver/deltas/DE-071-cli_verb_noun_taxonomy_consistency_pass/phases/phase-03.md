---
id: IP-071.PHASE-03
slug: 071-guidance-sweep
name: 'P03: Guidance sweep'
created: '2026-03-09'
updated: '2026-03-09'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-071.PHASE-03
plan: IP-071
delta: DE-071
objective: >-
  Update all agent guidance (memories, skills, docs) to reference new command
  shapes. Verify no stale references remain.
entrance_criteria:
  - P02 complete
exit_criteria:
  - No stale command references in guidance layer (VA-071-01)
  - Memories, skills, generated docs all reference current commands
verification:
  tests: []
  evidence:
    - VA-071-01
tasks:
  - id: '3.1'
    description: Grep for stale command references
  - id: '3.2'
    description: Update memories referencing old commands
  - id: '3.3'
    description: Update skills referencing old commands
  - id: '3.4'
    description: Update CLAUDE.md and generated docs
  - id: '3.5'
    description: Re-run install to regenerate AGENTS.md
  - id: '3.6'
    description: Final verification grep
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-071.PHASE-03
```

# Phase 3 — Guidance Sweep

## 1. Objective

Ensure all agent-facing guidance references the new command shapes.
This is the migration mechanism — agents learn commands from guidance, not aliases.

## 2. Links & References

- **Delta**: [DE-071](../DE-071.md)
- **Design Revision**: [DR-071](../DR-071.md) §4.4

## 3. Entrance Criteria

- [ ] P02 complete

## 4. Exit Criteria / Done When

- [ ] Grep sweep: zero hits for stale command patterns
- [ ] All guidance references current command shapes

## 5. Stale Patterns to Search

```
"skills sync"
"schema list"
"schema show"
"spec-driver compact"  (not under admin)
"spec-driver resolve"  (not under admin)
"spec-driver backfill" (not under admin)
```

Search scope: `.spec-driver/`, `CLAUDE.md`, memory records, skill files.

## 6. Tasks

| Status | ID | Description | Notes |
|--------|-----|-------------|-------|
| [ ] | 3.1 | Grep for stale patterns | List all hits |
| [ ] | 3.2 | Update memory records | `/maintaining-memory` |
| [ ] | 3.3 | Update skill files | |
| [ ] | 3.4 | Update CLAUDE.md, README.md, generated docs | |
| [ ] | 3.5 | Re-run `spec-driver install` to regenerate AGENTS.md | |
| [ ] | 3.6 | Final verification grep (VA-071-01) | Must be zero hits |
