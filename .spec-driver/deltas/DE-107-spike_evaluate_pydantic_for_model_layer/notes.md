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

### Observations

1. **Conversion is mechanical for field-mapping models.** BacklogItem and Card needed zero test changes. MemoryRecord needed 7 (removing from_frontmatter calls). The pattern is proven and repeatable.
2. **`to_dict()` stays explicit.** For models with selective inclusion rules (always-include core fields, truthy-gate optionals), explicit `to_dict()` is simpler than `model_dump()` wrappers. This is a consistent finding across both phases.
3. **`extra="ignore"` is essential.** Frontmatter may contain unknown fields (e.g. `links` section fields not in the model). `extra="ignore"` silently absorbs these.
4. **Pydantic + @staticmethod/@classmethod works.** No metaclass conflicts. Card.from_file() and helpers work unchanged.

### Open Questions for Phase 3

- **Spec model**: defer to Phase 3 or separate delta? The wrapper-around-FrontmatterValidationResult pattern doesn't map to the mechanical conversion recipe.
- **Drift models**: `@dataclass(frozen=True)` → `ConfigDict(frozen=True)` — need to verify no mutation paths exist before converting.
- **Phase 3 scope may need narrowing** given the Spec deferral. Original IP-107 Phase 3 included "remaining models" which assumed Spec was done in Phase 2.

### Phases Overview

| Phase | Scope | Status |
|---|---|---|
| **P01** | `MemoryRecord` conversion | **Done** |
| **P02** | `BacklogItem`, `Card` models | **Done** |
| **P03** | Drift models, remaining, frontmatter metadata, schema docs | Planned |

### Coordination

- **DE-109** (review state machine): `FindingDisposition` should use Pydantic BaseModel, not @dataclass. `coordinates_with` relation exists on both deltas. No ordering dependency.

### Subsumes

- IMPR-024: Kind-aware frontmatter validation via Pydantic models (status: subsumed)
