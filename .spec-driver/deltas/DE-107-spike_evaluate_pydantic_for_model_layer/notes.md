# Notes for DE-107

## New Agent Instructions

### Task Card

**DE-107** — Pydantic model layer migration.

Status: `draft`. DR-107 approved. IP-107 gates passed. Phase 1 sheet ready.

### What To Do

Invoke `/using-spec-driver` then `/execute-phase` for DE-107 Phase 1.

Read this file first — it has the full handoff including key files,
Phase 1 scope, implementation notes, and gotchas.

Phase 1: Convert `MemoryRecord` from `@dataclass` to Pydantic `BaseModel`.
- Phase sheet: `phases/phase-01.md` — has detailed task breakdown and implementation notes
- Reference implementation: `supekku/scripts/lib/changes/phase_model.py` (PhaseSheet from DE-106)

### Required Reading (in order)

1. [notes.md](./notes.md) — this file
2. [phases/phase-01.md](./phases/phase-01.md) — detailed task breakdown with implementation notes in §10
3. [DR-107](./DR-107.md) — approved design revision (conversion pattern §3, resolved questions §5)
4. [IP-107](./IP-107.md) — implementation plan with 3 phases
5. [DE-107](./DE-107.md) — delta scope

### Key Files

| File | Role | Phase 1 action |
|---|---|---|
| `supekku/scripts/lib/memory/models.py` | MemoryRecord model (161 lines) | **Convert to Pydantic BaseModel** |
| `supekku/scripts/lib/memory/registry.py` | Registry — constructs MemoryRecord at line 75 | **Update call site** |
| `supekku/scripts/lib/memory/models_test.py` | 26 tests (368 lines) | **Behavioural parity gate** |
| `supekku/scripts/lib/memory/registry_test.py` | Registry tests | **Must still pass** |
| `supekku/scripts/lib/changes/phase_model.py` | PhaseSheet — reference Pydantic model | **Read for pattern** |

### Conversion Recipe (from DR-107)

```python
# Before (@dataclass)
@dataclass
class MemoryRecord:
    id: str
    tags: list[str] = field(default_factory=list)
    created: date | None = None

    @classmethod
    def from_frontmatter(cls, path, fm):
        return cls(id=fm.get("id", ""), ...)

    def to_dict(self, root):
        data = {"id": self.id, ...}
        return data

# After (Pydantic)
class MemoryRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = ""
    tags: list[str] = []
    created: date | None = None

    @field_validator("created", ..., mode="before")
    @classmethod
    def _coerce_date(cls, v): ...

    def to_dict(self, root: Path) -> dict[str, Any]:
        # thin wrapper over model_dump
        ...
```

### Gotchas (read before implementing)

1. **`summary` field**: `str = ""`. Current `to_dict()` skips if falsy. `model_dump(exclude_none=True)` won't exclude `""`. Handle in `to_dict()` wrapper.

2. **Date coercion**: Pydantic v2 strict `date` type rejects strings. Use `@field_validator(mode="before")` to coerce. Must return `None` on bad input (test: `test_from_frontmatter_bad_date_ignored`).

3. **`path` field**: Not from frontmatter. Set by registry caller: `MemoryRecord(**fm, path=str(path))`. Use `path: str = ""`.

4. **Required fields aren't really required**: `id`, `name`, `status`, `memory_type` are "required" in the docstring but `from_frontmatter()` uses `fm.get("id", "")` — they default to empty string. Keep as `str = ""` in Pydantic.

5. **`to_dict()` always-include fields**: `id`, `name`, `status`, `memory_type`, `path` are always in output even if empty. Other fields only included if truthy/non-empty.

### Relevant Memories

- `mem.pattern.phase.canonical-fields` — PhaseSheet pattern reference
- `mem.pattern.phase.contract-vs-progress` — frontmatter vs markdown split

### Relevant Doctrine

- **POL-001**: maximise reuse, minimise sprawl (this delta's core motivation)
- **ADR-010**: placement heuristic (frontmatter-first for stable contract fields)
- **STD-002**: lint compliance

### Coordination

- **DE-109** (review state machine): `FindingDisposition` should use Pydantic BaseModel, not @dataclass. `coordinates_with` relation exists on both deltas. No ordering dependency — either can land first.

### Phases Overview

| Phase | Scope | Status |
|---|---|---|
| **P01** | `MemoryRecord` conversion | **Done** |
| **P02** | `BacklogItem`, `SpecEntry`, card models | Planned |
| **P03** | Drift models, remaining, frontmatter metadata, schema docs | Planned |

### Subsumes

- IMPR-024: Kind-aware frontmatter validation via Pydantic models (status: subsumed)
