# Notes for DE-112

## New Agent Instructions

### Task Card

**DE-112** — Kind-aware Pydantic validation and remaining dataclass cleanup.

Status: `draft`. DR-112 approved. IP-112 has 3 phases planned. No workflow state yet.

### What To Do

Invoke `/using-spec-driver` then `/execute-phase` for DE-112 Phase 1.

Read this file first, then the phase sheets and DR.

### Required Reading (in order)

1. [notes.md](./notes.md) — this file
2. [phases/phase-01.md](./phases/phase-01.md) — Phase 1 task breakdown
3. [phases/phase-02.md](./phases/phase-02.md) — Phase 2 task breakdown (read ahead)
4. [DR-112.md](./DR-112.md) — approved design revision (all 3 items, design decisions, code samples)
5. [DE-112.md](./DE-112.md) — delta scope

### Key Files

| File | Role | Phase action |
|---|---|---|
| `supekku/scripts/lib/core/frontmatter_schema.py` | FrontmatterValidationResult + Relation (frozen dataclasses) | **P01: Convert to Pydantic** |
| `supekku/scripts/lib/validation/validator.py` | WorkspaceValidator — PhaseSheet validation pattern at lines 506-522 | **P02: Add 3 kind-aware validation methods** |
| `supekku/scripts/lib/memory/models.py` | MemoryRecord (Pydantic, from DE-107) | **P02: Wire into validator** |
| `supekku/scripts/lib/backlog/models.py` | BacklogItem (Pydantic, from DE-107) | **P02: Wire into validator** |
| `supekku/scripts/lib/drift/models.py` | DriftLedger (Pydantic, from DE-107) | **P02: Wire into validator** |
| `.spec-driver/audits/AUD-012-*/AUD-012.md` | 11 findings with wrong status vocabulary | **P03: Fix resolved→reconciled** |

### Relevant Memories

- `mem.gotcha.pydantic.migration` — **critical**: 3 gotchas for frozen model conversion (TYPE_CHECKING, ValidationError vs AttributeError, no positional args)

### Relevant Doctrine

- **POL-001**: maximise reuse — use existing Pydantic models for validation, don't create parallel
- **STD-002**: lint compliance

### Key Design Decisions (from DR-112)

- **DEC-112-001**: Validator-level validation (not registry-level). Each kind gets a `_validate_*_frontmatter(fm, artifact)` method callable from batch now, extractable later.
- **DEC-112-002**: Convert FrontmatterValidationResult + Relation to Pydantic frozen BaseModel.
- **DEC-112-003**: Fix historical noise in-place.

### Gotchas for Phase 1

1. **`Relation.type` shadows `type` builtin** — Pydantic handles this fine, but note it.
2. ~~**`FrontmatterValidationResult.data` is `Mapping[str, Any]`** (immutable MappingProxyType)~~ — **RESOLVED (DEC-112-005)**: Simplify to `dict[str, Any]`, drop MappingProxyType wrapping. Frozen model provides immutability.
3. **`FrontmatterValidationResult.relations` is `tuple[Relation, ...]`** — Pydantic handles nested frozen models, but verify tuple construction works.
4. ~~**Tests checking frozen mutation**~~ — **PHANTOM**: No frozen-mutation tests exist for Relation or FrontmatterValidationResult. No test updates needed.
5. **`from __future__ import annotations`** — present but harmless; no TYPE_CHECKING-guarded field type imports.
6. **NEW (DEC-112-004)**: `FrontmatterValidationResult.dict()` collides with Pydantic `BaseModel.dict()`. Zero callers — drop the method.
7. **NEW (DEC-112-005)**: `Relation.attributes` also receives `MappingProxyType` — simplify to `dict[str, Any]` in `_normalize_relations()`.

### Gotchas for Phase 2

- The PhaseSheet validation pattern (`validator.py:506-522`) is the template. Each new method follows the same shape: `try: Model(**fm)` / `except ValidationError: self._warning(...)`.
- `MemoryRecord(**fm)` needs a `path` field — but memory validation doesn't need a real path. Pass `path=""` or omit (defaults to `""`).
- Backlog files are in per-kind subdirectories (`issues/`, `improvements/`, `problems/`, `risks/`). Traversal must glob each.
- Drift files are `DL-*.md` in the drift directory.

### Phases Overview

| Phase | Scope | Status |
|-------|-------|--------|
| **P01** | Convert FrontmatterValidationResult + Relation to Pydantic | Planned |
| **P02** | Wire kind-aware validation into validator | Planned |
| **P03** | Fix historical validation noise | Planned |

### Commit State

- All `.spec-driver/` changes committed (`6a27b90`).
- Worktree is clean.
- No pending code or workflow artefact changes.
