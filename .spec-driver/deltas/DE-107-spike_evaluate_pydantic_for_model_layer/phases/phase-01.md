---
id: IP-107-P01
slug: "107-spike_evaluate_pydantic_for_model_layer-phase-01"
name: Phase 01 — MemoryRecord conversion
created: "2026-03-22"
updated: "2026-03-22"
status: completed
kind: phase
plan: IP-107
delta: DE-107
objective: "Convert MemoryRecord from @dataclass to Pydantic BaseModel. Replace from_frontmatter(), to_dict(), _parse_date() with Pydantic construction and serialization. Update registry. All existing tests passing."
entrance_criteria:
  - DR-107 approved
  - Existing memory model and registry tests passing
exit_criteria:
  - MemoryRecord is a Pydantic BaseModel
  - from_frontmatter() removed
  - to_dict() replaced with model_dump-based thin wrapper
  - _parse_date() removed
  - All existing memory tests passing (26 model tests + registry tests)
  - Corpus validation against real .spec-driver/memory/ files
  - Lint clean
---

# Phase 01 — MemoryRecord conversion

## 1. Objective

Convert `MemoryRecord` from `@dataclass` to Pydantic `BaseModel`. This is the first model conversion, establishing the pattern for remaining phases.

## 2. Links & References

- **Delta**: DE-107
- **Design Revision**: DR-107 §3 (conversion pattern), DEC-107-001 through DEC-107-005
- **Reference Implementation**: `supekku/scripts/lib/changes/phase_model.py` (PhaseSheet)
- **Specs**: SPEC-132

## 3. Entrance Criteria

- [x] DR-107 approved (all OQs closed, 5 design decisions)
- [ ] Existing memory model and registry tests passing (baseline)

## 4. Exit Criteria / Done When

- [x] MemoryRecord is a Pydantic BaseModel with `ConfigDict(extra="ignore")`
- [x] `from_frontmatter()` classmethod removed; registry calls `MemoryRecord(**fm, path=str(path))`
- [x] `to_dict(root)` reimplemented as thin wrapper over `model_dump()`
- [x] `_parse_date()` removed — Pydantic handles date coercion
- [x] Bad date handling: Pydantic validator that returns None on unparseable dates (not error)
- [x] All 26 model tests passing without modification (or minimal assertion updates)
- [x] Registry tests passing
- [x] Corpus validation: all `.spec-driver/memory/*.md` files parse through new model
- [x] Lint clean

## 5. Verification

- `uv run pytest supekku/scripts/lib/memory/ -q` — all tests passing
- `uv run ruff check supekku/scripts/lib/memory/models.py supekku/scripts/lib/memory/registry.py`
- Corpus: load every `.spec-driver/memory/*.md` through `MemoryRecord(**fm, path=...)`

## 6. Assumptions & STOP Conditions

- Assumptions: Pydantic date coercion handles `YYYY-MM-DD`, `datetime`, and `date` objects (proven by PhaseSheet)
- Assumptions: `extra="ignore"` absorbs unknown frontmatter fields without error
- STOP when: any existing test fails in a way that suggests the conversion pattern doesn't work for this model's complexity level

## 7. Tasks & Progress

| Status | ID  | Description | Notes |
| ------ | --- | ----------- | ----- |
| [x]    | 1.1 | Convert MemoryRecord to BaseModel | Done — BaseModel + ConfigDict(extra="ignore") |
| [x]    | 1.2 | Add date validator | Done — `@field_validator` mode="before", returns None on bad input |
| [x]    | 1.3 | Reimplement to_dict(root) | Done — kept explicit logic (not model_dump), see §9 |
| [x]    | 1.4 | Remove from_frontmatter() | Done — registry uses `MemoryRecord(**fm, path=str(path))` |
| [x]    | 1.5 | Remove _parse_date() | Done — replaced by `_coerce_date` validator |
| [x]    | 1.6 | Run tests and fix assertions | 262 passed — 7 tests updated (from_frontmatter → direct construction) |
| [x]    | 1.7 | Corpus validation | 63/63 memory files parsed + serialized OK |
| [x]    | 1.8 | Lint and format | ruff check + ruff format clean |

### Task Details

- **1.1 Convert MemoryRecord to BaseModel**
  - `from pydantic import BaseModel, ConfigDict, field_validator`
  - `model_config = ConfigDict(extra="ignore")`
  - Replace `field(default_factory=list)` with `list[str] = []` (Pydantic handles mutable defaults safely)
  - Replace `field(default_factory=dict)` with `dict[str, Any] = {}`
  - `path: str = ""` — set by caller, not from frontmatter

- **1.2 Add date validator**
  - Need `@field_validator("created", "updated", "verified", "review_by", mode="before")`
  - Must handle: `date` object (pass through), `datetime` object (`.date()`), `str` (parse multiple formats), bad values (return `None`)
  - Pydantic v2 validators return the coerced value or raise — but we need permissive parsing
  - Use `mode="before"` to intercept before Pydantic's strict date validation

- **1.3 Reimplement to_dict(root)**
  - Always include: `id`, `name`, `status`, `memory_type`, `path` (relativized)
  - Dates: include only if present, as `.isoformat()`
  - Optional scalars: include only if truthy
  - Lists/dicts: include only if non-empty
  - Consider: `model_dump(exclude_none=True)` + post-processing for path and dates
  - Note: `model_dump()` returns `date` objects, not strings — need `.isoformat()` conversion
  - Note: `summary: str = ""` — empty string is not None, so `exclude_none` won't exclude it. Current `to_dict` includes summary only if truthy. Watch this.

- **1.4 Remove from_frontmatter()**
  - `registry.py:75`: change `MemoryRecord.from_frontmatter(path, frontmatter)` to `MemoryRecord(**frontmatter, path=str(path))`
  - Frontmatter `id` fallback to `path.stem` happens at line 73 — keep that logic in registry

- **1.5 Remove _parse_date()**
  - Standalone function at module top. Remove after validator handles all cases.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| ---- | ---------- | ------ |
| `to_dict()` serialization mismatch | Compare output field-by-field with existing implementation | mitigated — kept explicit to_dict logic |
| Bad date handling differs | Test `test_from_frontmatter_bad_date_ignored` — must still return None | mitigated — test passes |
| `summary=""` vs `summary=None` semantics | Current: empty string default, to_dict skips if falsy. Watch model_dump behaviour. | mitigated — kept truthy check in to_dict |

## 9. Decisions & Outcomes

- **DEC-P01-001**: Kept explicit `to_dict()` logic rather than wrapping `model_dump()`. Rationale: the selective inclusion rules (always-include vs truthy-gated) and date `.isoformat()` conversion make a pure `model_dump` wrapper more complex than just keeping the clear explicit logic. The field list is identical to the dataclass version. No behavioural change.
- **DEC-P01-002**: Named the validator `_coerce_date` (not `_parse_date`) to differentiate from the removed standalone function and signal its role as a Pydantic validator.

## 10. Findings / Research Notes

### Key implementation notes for the converting agent

1. **`summary` field**: Currently `str = ""`. `to_dict()` includes it only if truthy (non-empty). With Pydantic, `model_dump(exclude_none=True)` won't exclude `""`. Options: use `exclude_defaults=True` (but that excludes all defaults), or handle in the thin `to_dict()` wrapper.

2. **Date coercion**: Pydantic v2 `date` type accepts `date` objects and ISO strings natively. For `datetime` → `date` and multi-format parsing, a `@field_validator(mode="before")` is needed. Return `None` on failure (permissive).

3. **`relations: list[dict[str, Any]]`**: Pydantic handles `list[dict[str, Any]]` natively. No special treatment.

4. **`path` field**: Not from frontmatter — set by the registry caller. Use `path: str = ""` with Pydantic. The registry passes `path=str(path)`.

5. **Mutable defaults**: Pydantic handles `list[str] = []` and `dict[str, Any] = {}` safely (creates new instances per model). No `Field(default_factory=...)` needed for simple cases.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Notes updated
- [ ] Hand-off notes to Phase 2
