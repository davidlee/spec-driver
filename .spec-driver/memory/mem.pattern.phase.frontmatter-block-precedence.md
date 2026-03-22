---
id: mem.pattern.phase.frontmatter-block-precedence
name: Phase frontmatter-block reading precedence
kind: memory
status: active
memory_type: pattern
created: "2026-03-22"
updated: "2026-03-22"
verified: "2026-03-22"
confidence: high
tags: [phase, frontmatter, compatibility, artifacts]
summary: >-
  Frontmatter wins when canonical fields present; fall back to phase.overview
  blocks for legacy phases. Never merge.
scope:
  globs:
    - supekku/scripts/lib/changes/artifacts.py
    - supekku/scripts/lib/validation/validator.py
    - supekku/scripts/lib/formatters/change_formatters.py
provenance:
  sources:
    - kind: delta
      note: DR-106 OQ-001 — compatibility strategy
      ref: DE-106
    - kind: code
      note: artifacts.py frontmatter-first reading path
      ref: supekku/scripts/lib/changes/artifacts.py
---

# Phase frontmatter-block reading precedence

## Rule

1. Check `PhaseSheet.has_canonical_fields()` — True if `plan` and `delta` in frontmatter
2. If canonical: use `PhaseSheet.to_phase_entry()` — frontmatter is authoritative
3. If not canonical: extract from `phase.overview` block (legacy path)
4. **Never merge** frontmatter and block data. One source wins entirely.

## Where enforced

- **`artifacts.py`**: `load_change_artifact()` applies this precedence when building phase entries
- **`validator.py`**: skips "missing phase.overview block" warning for new-format phases
- **`_enrich_phase_data()`**: tries tracking block first, regex fallback for task stats

## Migration

No bulk migration of legacy phases. They migrate naturally when agents touch
them, or via a future targeted script (backlog item captured).

## See also

- [[mem.pattern.phase.canonical-fields]] field set
- [[ADR-010]] placement heuristic
