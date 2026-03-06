# DE-050 Research: Registry API Audit

Comprehensive audit of registry implementations to scope normalisation work.

## Current State: 9 Registries, 5+ Patterns

### Comparison Matrix

| Registry | Class? | Constructor | Collection | ID Lookup | `iter()` | `filter()` | Sync | Model Location |
|---|---|---|---|---|---|---|---|---|
| **Spec** | Yes | `(root=None)` positional | `reload()` → cache, `all_specs()` → list | `get(id)` | No | `find_by_*()` x2 | `reload()` | models.py |
| **Decision** | Yes | `(*, root=None)` kw-only | `collect()` → dict | `find(id)` | Yes | `filter(tag,spec,delta,req,pol,std)` | `sync()` + symlinks | inline |
| **Change** | Yes | `(*, root=None, kind)` kw-only | `collect()` → dict | None | No | `find_by_implements()` | `sync()` | artifacts.py |
| **Requirements** | Yes | `(registry_path)` positional, required | `.records` dict (eager) | None | No | `search()` + 3 `find_by_*()` | `save()` | inline |
| **Backlog** | **Functions** | N/A | `discover_backlog_items()` | `find_backlog_items_by_id()` → list | No | kind param on discover | `sync_backlog_registry()` | models.py |
| **Policy** | Yes | `(*, root=None)` kw-only | `collect()` → dict | `find(id)` | Yes | `filter(tag,spec,delta,req,std)` | `sync()` | inline |
| **Standard** | Yes | `(*, root=None)` kw-only | `collect()` → dict | `find(id)` | Yes | `filter(tag,spec,delta,req,pol)` | `sync()` | inline |
| **Memory** | Yes | `(*, root=None, directory=None)` kw-only | `collect()` → dict | `find(id)` | Yes | `filter(memory_type,status,tag)` | None | models.py |
| **Card** | Yes | `(root)` positional, required | `all_cards()` → list | `resolve_card(id)` raises | `cards_by_lane()` | None | None | models.py |

### Inconsistency Categories

#### 1. Constructor patterns (4 variants)

- **Keyword-only, optional root**: Decision, Change, Policy, Standard, Memory — the emerging convention
- **Positional, optional root**: Spec — oldest registry
- **Positional, required path**: Requirements (`registry_path`), Card (`root`) — no auto-discovery
- **No class**: Backlog — bare functions

#### 2. Collection (4 variants)

- `collect() → dict[str, Record]`: Decision, Change, Policy, Standard, Memory — the convention
- `reload()` + `all_specs() → list[Spec]`: Spec — eager, cached, returns list not dict
- `.records` dict: Requirements — eager-loaded, exposed directly
- `discover_*() → list`: Backlog — functional

#### 3. ID lookup (5 variants)

- `find(id) → Record | None`: Decision, Policy, Standard, Memory — the convention
- `get(id) → Spec | None`: Spec — different name, same semantics
- `resolve_card(id) → Card` (raises): Card — different name, raises instead of returning None
- `find_backlog_items_by_id() → list`: Backlog — returns list, takes extra params
- None: Change, Requirements — must use `collect()` then dict access

#### 4. Iteration (inconsistent)

- `iter(status=None)`: Decision, Policy, Standard, Memory — consistent among themselves
- No `iter()`: Spec, Change, Requirements, Backlog
- `cards_by_lane(lane)`: Card — different concept

#### 5. Filtering (7 approaches)

- Generic `filter(**kwargs)`: Decision, Policy, Standard — consistent params per domain
- `filter(memory_type, status, tag)`: Memory — different params
- Specialised methods: Spec (`find_by_package`, `find_by_informed_by`)
- Complex `search()` + specialised: Requirements (4 methods)
- Single specialised: Change (`find_by_implements`)
- None: Card
- Functional: Backlog (kind param on discovery)

#### 6. Persistence naming

- `sync()`: Decision, Change, Policy, Standard
- `save()`: Requirements
- `reload()`: Spec
- `sync_backlog_registry()`: Backlog (function)
- None: Memory, Card

#### 7. Model location & mutability

- Separate `models.py`: Spec (frozen), Backlog, Memory, Card
- Inline in registry: Decision, Requirements, Policy, Standard (mutable)
- Separate `artifacts.py`: Change (frozen)

#### 8. Side effects

- **Symlinks**: Decision only (status symlink dirs)
- **File creation**: Card (`create_card()`), Backlog (`create_backlog_entry()`)
- **YAML writes**: Decision, Change, Policy, Standard, Requirements, Backlog
- **Read-only**: Spec, Memory

#### 9. Error handling

- Returns None: Spec, Decision, Policy, Standard, Memory
- Raises exceptions: Card (`FileNotFoundError`), Requirements (`ValueError`), Backlog (`ValueError`)
- Warns and continues: Change (ValidationError → console warning)

---

## Spec Coverage

### Stub specs (no content)

- **SPEC-115**: ChangeRegistry — stub
- **SPEC-117**: DecisionRegistry — stub
- **SPEC-123**: SpecRegistry — stub

These are heavily depended on by SPEC-110 (CLI) and SPEC-125 (workspace
validation) but have no defined API contract.

### Substantive specs

- **SPEC-110** (CLI): Defines which registry methods the CLI calls, but doesn't
  constrain registry API shape
- **SPEC-122** (Requirements): Most detailed — defines `RequirementRecord`
  schema, sync semantics, search API. Implementation exceeds spec (coverage
  block processing, multiple `find_by_*` methods undocumented)

### Missing

No spec defines what "registry" means architecturally. No consistency
requirements exist for registry APIs. The drift is unsurprising given this gap.

---

## Convergence Groups

### Group A: The "modern" convention (4 registries)

Decision, Policy, Standard, Memory all share:
- `__init__(*, root=None)` keyword-only
- `collect() → dict[str, Record]`
- `find(id) → Record | None`
- `iter(status=None)`
- `filter(**domain_kwargs)`

This is the target pattern. These 4 are already consistent.

### Group B: Need alignment (3 registries)

- **Spec**: Rename `get()` → `find()`. Add `collect()` returning dict. Add
  `iter()`. Constructor → keyword-only.
- **Change**: Add `find(id)`. Add `iter()`. Already has `collect()`.
- **Requirements**: Add `find(uid)`. Consider exposing `collect()` instead of
  raw `.records`. Constructor needs rethinking (registry_path vs root).

### Group C: Structural changes needed (2 registries)

- **Backlog**: Class-ify. Adopt `collect()`, `find()`, `iter()` convention.
- **Card**: Adopt `find()` returning Optional (not raising). Constructor →
  keyword-only with optional root.

---

## Proposed Normalisation Tiers

### Tier 1: Unblock IMPR-009 (minimum viable consistency)

Add `find(id) → Record | None` to every registry that lacks it:
- ChangeRegistry
- RequirementsRegistry
- BacklogRegistry (as function or on new class)

Add `collect() → dict[str, Record]` where missing:
- SpecRegistry (wrap `_specs` dict)

Rename `get()` → `find()` on SpecRegistry (with deprecation alias).

**Outcome**: Every artifact type has a consistent `find(id)` path. The TUI
adapter layer becomes trivial.

### Tier 2: API consistency (recommended)

Align Group B registries to Group A pattern:
- Add `iter(status=None)` to Spec, Change, Requirements
- Normalise constructor to `(*, root=None)` keyword-only
- Normalise persistence naming to `sync()`

### Tier 3: Structural (optional, higher risk)

- Class-ify BacklogRegistry
- Separate model definitions consistently (all in `models.py`)
- Define a Registry Protocol (only after Tier 2 proves the interface stable)

---

## Risk Assessment

| Change | Risk | Mitigation |
|---|---|---|
| Add `find()` to registries | Low | Additive, no breaking changes |
| Rename `get()` → `find()` on Spec | Medium | Deprecation alias, grep for callers |
| Add `collect()` to Spec | Low | Wrapper around existing cache |
| Add `iter()` everywhere | Low | Additive |
| Normalise constructors | Medium | Keyword-only is breaking for positional callers |
| Class-ify Backlog | High | All callers must change; functional API must be preserved or migrated |
| Define Protocol | Low | Purely descriptive if done after normalisation |

---

## CLI Adapter Layer (current workarounds)

`supekku/cli/common.py` already bridges inconsistencies:
- RequirementsRegistry: special `registry_path` setup
- CardRegistry: `resolve_card()` exception handling
- Backlog: bare function calls with extra params
- Plans: manual file scanning (not a registry at all)
- ID normalisation: colon→dot for Requirements

These workarounds are evidence of the cost of drift. Normalisation would
simplify `common.py` significantly.

---

## References

- ISSUE-019: Registry API drift (this delta's origin)
- IMPR-009: TUI dashboard (downstream consumer)
- SPEC-110: CLI orchestration (documents current usage)
- SPEC-122: Requirements registry (most detailed spec)
- SPEC-115, SPEC-117, SPEC-123: Stub specs for Change, Decision, Spec registries
- ADR-002: No backlinks in frontmatter (partially violated by DecisionRecord)
