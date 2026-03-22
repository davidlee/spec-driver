---
id: IP-107-P02
slug: "107-spike_evaluate_pydantic_for_model_layer-phase-02"
name: "Phase 02 — BacklogItem and Card conversion"
created: "2026-03-22"
updated: "2026-03-22"
status: in-progress
kind: phase
plan: IP-107
delta: DE-107
objective: >-
  Convert BacklogItem and Card from @dataclass to Pydantic BaseModel.
  Update registry construction sites. All existing tests passing.
  Spec model deferred — structurally different (wrapper pattern, not
  field-mapping pattern).
entrance_criteria:
  - Phase 1 complete
  - MemoryRecord conversion pattern established
exit_criteria:
  - BacklogItem is a Pydantic BaseModel with ConfigDict(extra="ignore")
  - Card is a Pydantic BaseModel
  - BacklogItem registry construction updated to direct construction
  - Card.from_file() retained as classmethod (file I/O factory, not frontmatter mapping)
  - All existing backlog tests passing (models + registry + priority)
  - All existing card tests passing (registry)
  - Lint clean
---

# Phase 02 — BacklogItem and Card conversion

## 1. Objective

Convert `BacklogItem` and `Card` from `@dataclass` to Pydantic `BaseModel`. This follows the pattern established in Phase 1 (MemoryRecord). The `Spec` model is deferred — see §10 for rationale.

## 2. Links & References

- **Delta**: DE-107
- **Design Revision**: DR-107 §3 (conversion recipe), DEC-107-001 through DEC-107-005
- **Phase 1**: Phase 01 (MemoryRecord — pattern reference)
- **Specs**: SPEC-116 (backlog)

## 3. Entrance Criteria

- [x] Phase 1 complete (MemoryRecord converted, 262 tests passing)
- [x] MemoryRecord conversion pattern established

## 4. Exit Criteria / Done When

- [x] BacklogItem is a Pydantic BaseModel with `ConfigDict(extra="ignore")`
- [x] Card is a Pydantic BaseModel
- [x] BacklogItem registry construction — no change needed, already constructs with kwargs
- [x] Card.from_file() retained as classmethod (file I/O factory)
- [x] All existing backlog tests passing (models + registry + priority) — 132 tests
- [x] All existing card tests passing (registry) — included in 132
- [x] Lint clean

## 5. Verification

- `uv run pytest supekku/scripts/lib/backlog/ -q` — all tests passing
- `uv run pytest supekku/scripts/lib/cards/ -q` — all tests passing
- `uv run ruff check supekku/scripts/lib/backlog/models.py supekku/scripts/lib/backlog/registry.py supekku/scripts/lib/cards/models.py`

## 6. Assumptions & STOP Conditions

- Assumptions: BacklogItem follows the same conversion pattern as MemoryRecord
- Assumptions: Card.from_file() stays as classmethod — Pydantic BaseModel supports classmethods fine
- Assumptions: BacklogItem.frontmatter dict field can stay as `dict[str, Any] = {}` — it's used by to_dict() for linked_deltas/related_requirements
- STOP when: Card static methods conflict with Pydantic model metaclass

## 7. Tasks & Progress

| Status | ID  | Description | Notes |
| ------ | --- | ----------- | ----- |
| [x]    | 2.1 | Convert BacklogItem to BaseModel | Done — BaseModel + ConfigDict(extra="ignore") |
| [x]    | 2.2 | Update BacklogItem registry construction | No change needed — already uses kwargs |
| [x]    | 2.3 | Convert Card to BaseModel | Done — from_file() + static methods retained |
| [x]    | 2.4 | Run tests and fix assertions | 132 passed, no test changes needed |
| [x]    | 2.5 | Lint and format | ruff check + ruff format clean |

### Task Details

- **2.1 Convert BacklogItem to BaseModel**
  - `from pydantic import BaseModel, ConfigDict`
  - `model_config = ConfigDict(extra="ignore")`
  - `path: Path` — keep as Path (not str like MemoryRecord); registry passes `md_file` directly
  - `frontmatter: dict[str, Any] = {}` — Pydantic handles mutable dict default
  - `tags: list[str] = []`, `categories: list[str] = []`
  - No date coercion needed — `created` and `updated` are `str`, not `date`
  - `likelihood: float = 0.0` — Pydantic handles float coercion natively

- **2.2 Update BacklogItem registry construction**
  - Current: explicit `BacklogItem(id=..., kind=str(fm.get("kind", ""))...)`
  - The registry does normalization (lowercase kind, fallback title, etc.) — this stays
  - Keep explicit construction but on BaseModel instead of dataclass
  - No `from_frontmatter()` to remove — BacklogItem never had one

- **2.3 Convert Card to BaseModel**
  - `model_config = ConfigDict(extra="ignore")` — though Card doesn't get extra fields
  - Keep `from_file()` classmethod — it's a file I/O factory, not frontmatter unpacking
  - Keep all `@staticmethod` helpers — Pydantic BaseModel supports these fine
  - `path: Path` — keep as Path
  - `lane: str | None = None`, `created: str | None = None`

- **2.4 Run tests and fix assertions**
  - No `from_frontmatter()` tests to update for either model
  - Backlog: models_test.py (196 lines), registry_test.py, priority_test.py
  - Cards: registry_test.py only (no models_test.py)

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| ---- | ---------- | ------ |
| BacklogItem.frontmatter dict field semantics differ | to_dict() reads linked_deltas/related_requirements from frontmatter — kept field and logic | mitigated |
| Card static methods conflict with Pydantic metaclass | Confirmed: no conflict. Pydantic supports @staticmethod and @classmethod. | mitigated |

## 9. Decisions & Outcomes

- **Spec model deferred**: See §10. Not a straightforward conversion — needs separate design thought.

## 10. Findings / Research Notes

### Spec model deferral rationale

The `Spec` model (`specs/models.py`) is structurally different from BacklogItem/Card/MemoryRecord:

1. It's `@dataclass(frozen=True)` wrapping a `FrontmatterValidationResult` object
2. All field accessors are `@property` methods reaching into `self.frontmatter.data`
3. It does NOT have the from_frontmatter/to_dict boilerplate pattern — its properties ARE the abstraction
4. Converting it would either:
   - Keep the wrapper pattern (minimal benefit from Pydantic)
   - Extract all frontmatter fields into proper model fields (bigger restructuring)

This needs separate design thought, possibly a DR addendum. Deferring to Phase 3 or a separate delta.

The IP-107 Phase 2 scope says "BacklogItem, SpecEntry, and card models" but the actual Spec model doesn't fit the mechanical conversion pattern. Narrowing Phase 2 to BacklogItem + Card and noting the Spec tension.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Notes updated
- [ ] Hand-off notes to Phase 3
