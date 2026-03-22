# Notes for DE-107

## New Agent Instructions

### Task Card

**DE-107** — Pydantic model layer migration (repurposed from spike).

Status: `draft`. DR-107 approved. IP-107 gates passed. Ready for Phase 1.

### Context

Originally scoped as a Pydantic evaluation spike. The spike was answered by
DE-106 Phase 1 (PhaseSheet model — 37ms import, clean parsing, go decision).
Repurposed to cover the actual migration of all model files to Pydantic.

### Required Reading

1. [notes.md](./notes.md) — this file
2. [DE-107](./DE-107.md) — delta scope (reshaped)
3. [DR-107](./DR-107.md) — design revision with conversion pattern and open questions
4. [IP-107](./IP-107.md) — 3-phase implementation plan

### Key Files

| File | Lines | Model(s) | Priority |
|---|---|---|---|
| `supekku/scripts/lib/memory/models.py` | 161 | `MemoryRecord` | Phase 1 |
| `supekku/scripts/lib/backlog/models.py` | 128 | `BacklogItem` | Phase 2 |
| `supekku/scripts/lib/specs/models.py` | 140 | `SpecEntry` | Phase 2 |
| `supekku/scripts/lib/cards/models.py` | 102 | Card models | Phase 2 |
| `supekku/scripts/lib/drift/models.py` | 170 | 4 frozen dataclasses | Phase 3 |
| `supekku/scripts/lib/diagnostics/models.py` | 47 | Diagnostic models | Phase 3 |
| `supekku/scripts/lib/sync/models.py` | 68 | Sync models | Phase 3 |
| `supekku/scripts/lib/docs/python/models.py` | 59 | Doc models | Phase 3 |

### Reference Implementation

- `supekku/scripts/lib/changes/phase_model.py` — PhaseSheet (DE-106)

### Resolved Questions

1. `to_dict(root)`: thin wrapper over `model_dump(exclude_none=True)` + path fixup (DEC-107-003)
2. `dataclasses.fields()` / `asdict()`: zero usage in non-test code (DEC-107-005)
3. Import time: 37ms shared import, negligible incremental cost
4. `from_frontmatter()`: 1 call site per model in registry — remove classmethod, update call site (DEC-107-002)

### Subsumes

- IMPR-024: Kind-aware frontmatter validation for all artifact types via Pydantic models
