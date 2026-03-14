---
id: mem.artifact-pattern-sync
name: artifact pattern list is mirrored in Python and TypeScript
kind: memory
status: active
memory_type: fact
created: "2026-03-14"
updated: "2026-03-14"
verified: "2026-03-14"
confidence: high
tags:
  - coupling
  - pi
  - artifact-events
summary: >-
  _ARTIFACT_PATTERNS in artifact_event.py has a TypeScript mirror in
  spec-driver-artifact-events.ts — changes to either must be applied to both.
scope:
  paths:
    - supekku/claude.hooks/artifact_event.py
    - supekku/pi.extensions/spec-driver-artifact-events.ts
  globs:
    - supekku/claude.hooks/**
    - supekku/pi.extensions/**
---

# artifact pattern list is mirrored in Python and TypeScript

The spec-driver artifact classification patterns exist in two places:

- **Python** (canonical): `supekku/claude.hooks/artifact_event.py` → `_ARTIFACT_PATTERNS`
- **TypeScript** (mirror): `supekku/pi.extensions/spec-driver-artifact-events.ts` → `ARTIFACT_PATTERNS`

Both lists must match. If you add, remove, or reorder a pattern in one, apply the
same change to the other.

Design rationale: [[DE-094]], DEC-094-01 — in-process TS avoids Python shell-out
overhead; manual sync accepted because the pattern list is stable and changes are
infrequent.
