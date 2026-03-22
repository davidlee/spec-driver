# Notes for DE-107

## Implementation Log

### Phase 1 — MemoryRecord (done)

- Converted `models.py` from `@dataclass` → `BaseModel + ConfigDict(extra="ignore")`
- Added `@field_validator("created", "updated", "verified", "review_by", mode="before")` for permissive date coercion (returns `None` on bad input)
- Kept explicit `to_dict()` logic — `model_dump()` wrapper was more complex due to selective inclusion rules and date `.isoformat()` conversion
- Removed `from_frontmatter()` classmethod; registry uses `MemoryRecord(**fm, path=str(path))`
- Removed standalone `_parse_date()` function
- 7 tests updated (from_frontmatter → direct construction), 262 tests passing
- 63/63 corpus memory files validated
- Commits: `dcf9a79` (code), `4067d15` (docs)

### Phase 2 — BacklogItem + Card (done)

- Both models: `@dataclass` → `BaseModel + ConfigDict(extra="ignore")`
- BacklogItem registry: no change needed — already uses kwargs construction
- Card: `from_file()` classmethod and `@staticmethod` helpers retained — Pydantic supports both fine
- Zero test changes needed — all 132 tests pass as-is
- Net change: +4 lines (import swaps only)
- Commits: `2e6cf16` (code), `7295b50` (docs)

**Spec model deferred**: `Spec` (`specs/models.py`) is structurally different — frozen dataclass wrapping `FrontmatterValidationResult`, all attributes are `@property` accessors into `frontmatter.data`. Not the from_frontmatter/to_dict boilerplate pattern. Needs separate design thought. See phase-02 §10.

### Phase 3 — Drift, diagnostics, sync, docs (done)

- Drift: 3 frozen (`Source`, `Claim`, `DiscoveredBy`) + 2 mutable (`DriftEntry`, `DriftLedger`)
- Diagnostics: 2 frozen (`DiagnosticResult`, `CategorySummary`)
- Sync: 3 frozen (`SourceUnit`, `DocVariant`, `SourceDescriptor`) + 1 mutable (`SyncOutcome`)
- Docs/python: `VariantSpec` (classmethods retained), `DocResult`
- **Gotcha: `TYPE_CHECKING` guard on Path imports**. Pydantic needs runtime access to `Path` for field resolution. `from __future__ import annotations` defers annotation evaluation but `model_rebuild()` still needs the type available. Moved `Path` imports out of `TYPE_CHECKING` blocks.
- **Gotcha: frozen mutation tests**. `@dataclass(frozen=True)` raises `AttributeError`; Pydantic `frozen=True` raises `ValidationError`. Updated 4 tests.
- **Gotcha: positional construction**. Dataclasses accept positional args; Pydantic BaseModel requires keyword args. Updated ~20 test call sites across 8 files.
- Net model file change: 0 lines (52 added, 52 removed — import swaps and config additions)
- Commits: `7467e09` (models), `7813055` (tests)

### Observations

1. **Conversion is mechanical for field-mapping models.** BacklogItem and Card needed zero test changes. MemoryRecord needed 7 (removing from_frontmatter calls). The pattern is proven and repeatable.
2. **`to_dict()` stays explicit.** For models with selective inclusion rules (always-include core fields, truthy-gate optionals), explicit `to_dict()` is simpler than `model_dump()` wrappers. This is a consistent finding across both phases.
3. **`extra="ignore"` is essential.** Frontmatter may contain unknown fields (e.g. `links` section fields not in the model). `extra="ignore"` silently absorbs these.
4. **Pydantic + @staticmethod/@classmethod works.** No metaclass conflicts. Card.from_file() and helpers work unchanged.

### Open Questions

- **Spec model**: needs separate design thought or separate delta. Wrapper-around-FrontmatterValidationResult pattern doesn't map to mechanical conversion.
- **IP-107 remaining scope**: frontmatter metadata updates and schema docs from original Phase 3 not yet addressed. May be out of scope for this spike delta.

### Phases Overview

| Phase | Scope | Status |
|---|---|---|
| **P01** | `MemoryRecord` conversion | **Done** |
| **P02** | `BacklogItem`, `Card` models | **Done** |
| **P03** | Drift, diagnostics, sync, docs models | **Done** |

### Coordination

- **DE-109** (review state machine): `FindingDisposition` should use Pydantic BaseModel, not @dataclass. `coordinates_with` relation exists on both deltas. No ordering dependency.

### Subsumes

- IMPR-024: Kind-aware frontmatter validation via Pydantic models (status: subsumed)
