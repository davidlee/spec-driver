---
id: IP-112-P01
slug: "112-kind_aware_pydantic_validation-phase-01"
name: "Phase 01 — Convert FrontmatterValidationResult and Relation"
created: "2026-03-22"
updated: "2026-03-22"
status: draft
kind: phase
plan: IP-112
delta: DE-112
objective: >-
  Convert FrontmatterValidationResult and Relation from @dataclass(frozen=True)
  to Pydantic BaseModel(frozen=True). Update validate_frontmatter() call site.
entrance_criteria:
  - DR-112 approved
  - Existing core tests passing
exit_criteria:
  - Both classes are Pydantic BaseModel with frozen=True
  - validate_frontmatter() constructs FrontmatterValidationResult via Pydantic
  - All existing tests passing
  - Lint clean
---

# Phase 01 — Convert FrontmatterValidationResult and Relation

## Tasks

| Status | ID  | Description | Notes |
| ------ | --- | ----------- | ----- |
| [ ]    | 1.1 | Convert Relation to frozen BaseModel | field(default_factory=dict) → dict default; change attributes to dict[str, Any] |
| [ ]    | 1.2 | Convert FrontmatterValidationResult to frozen BaseModel | tuple fields stay as tuple; change data to dict[str, Any] |
| [ ]    | 1.3 | Drop dead `.dict()` method from FrontmatterValidationResult | Collides with Pydantic BaseModel.dict(); zero callers (DEC-112-004) |
| [ ]    | 1.4 | Simplify MappingProxyType away in validate_frontmatter() and _normalize_relations() | Pass plain dict instead of MappingProxyType (DEC-112-005) |
| [ ]    | 1.5 | Update imports (add BaseModel; remove dataclass/field if unused) | TYPE_CHECKING not an issue — no Path fields |
| [ ]    | 1.6 | Run tests and lint | Core tests + specs tests (Spec uses FrontmatterValidationResult) |

### Notes

- `Relation.type` shadows `type` builtin — Pydantic handles this fine
- `FrontmatterValidationResult.data` → change from `Mapping[str, Any]` to `dict[str, Any]`; drop MappingProxyType wrapping in validate_frontmatter()
- `Relation.attributes` → change from `Mapping[str, Any]` to `dict[str, Any]`; drop MappingProxyType wrapping in _normalize_relations()
- `FrontmatterValidationResult.relations` is `tuple[Relation, ...]` — Pydantic handles nested frozen models
- `.dict()` method is dead code (zero callers) — drop it; conflicts with Pydantic BaseModel.dict()
- No frozen-mutation tests exist for these two classes — the gotcha from mem.gotcha.pydantic.migration is a phantom here
- `from __future__ import annotations` is present but harmless — no TYPE_CHECKING-guarded imports for field types
