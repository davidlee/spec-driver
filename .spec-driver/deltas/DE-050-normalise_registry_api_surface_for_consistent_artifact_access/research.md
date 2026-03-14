# DE-050 Research: Registry API Audit

Comprehensive audit of registry implementations to scope normalisation work.

## Current State: 9 Registries, 5+ Patterns

### Comparison Matrix

| Registry         | Class?        | Constructor                              | Collection                                | ID Lookup                            | `iter()`          | `filter()`                           | Sync                      | Model Location |
| ---------------- | ------------- | ---------------------------------------- | ----------------------------------------- | ------------------------------------ | ----------------- | ------------------------------------ | ------------------------- | -------------- |
| **Spec**         | Yes           | `(root=None)` positional                 | `reload()` + cache, `all_specs()` -> list | `get(id)`                            | No                | `find_by_*()` x2                     | `reload()`                | models.py      |
| **Decision**     | Yes           | `(*, root=None)` kw-only                 | `collect()` -> dict                       | `find(id)`                           | Yes               | `filter(tag,spec,delta,req,pol,std)` | `sync()` + symlinks       | inline         |
| **Change**       | Yes           | `(*, root=None, kind)` kw-only           | `collect()` -> dict                       | None                                 | No                | `find_by_implements()`               | `sync()`                  | artifacts.py   |
| **Requirements** | Yes           | `(registry_path)` positional, required   | `.records` dict (eager)                   | None                                 | No                | `search()` + 3 `find_by_*()`         | `save()`                  | inline         |
| **Backlog**      | **Functions** | N/A                                      | `discover_backlog_items()`                | `find_backlog_items_by_id()` -> list | No                | kind param on discover               | `sync_backlog_registry()` | models.py      |
| **Policy**       | Yes           | `(*, root=None)` kw-only                 | `collect()` -> dict                       | `find(id)`                           | Yes               | `filter(tag,spec,delta,req,std)`     | `sync()`                  | inline         |
| **Standard**     | Yes           | `(*, root=None)` kw-only                 | `collect()` -> dict                       | `find(id)`                           | Yes               | `filter(tag,spec,delta,req,pol)`     | `sync()`                  | inline         |
| **Memory**       | Yes           | `(*, root=None, directory=None)` kw-only | `collect()` -> dict                       | `find(id)`                           | Yes               | `filter(memory_type,status,tag)`     | None                      | models.py      |
| **Card**         | Yes           | `(root)` positional, required            | `all_cards()` -> list                     | `resolve_card(id)` raises            | `cards_by_lane()` | None                                 | None                      | models.py      |

---

## Per-Registry Audit

### 1. SpecRegistry

**File:** `supekku/scripts/lib/specs/registry.py`

#### A. Class Structure

- **Class:** `SpecRegistry` (no parent)
- **Constructor** (lines 21-26):

  ```python
  def __init__(self, root: Path | None = None) -> None:
  ```

  - Positional `root`, optional, auto-discovers via `find_repo_root()`
  - **Eager**: calls `reload()` at construction, populating `self._specs: dict[str, Spec]`

#### B. Core API

| Method          | Signature                                                | Line  | Semantics                         |
| --------------- | -------------------------------------------------------- | ----- | --------------------------------- |
| **ID lookup**   | `get(spec_id: str) -> Spec \| None`                      | 42-44 | Returns None if not found         |
| **Collection**  | `all_specs() -> list[Spec]`                              | 46-48 | Returns list (not dict)           |
| **Filter**      | `find_by_package(package: str) -> list[Spec]`            | 50-52 | Empty list if no matches          |
| **Filter**      | `find_by_informed_by(adr_id: str \| None) -> list[Spec]` | 54-68 | Empty list if None/empty          |
| **Persistence** | `reload() -> None`                                       | 28-40 | Clears cache, re-scans filesystem |

No `find()`, `collect()`, `iter()`, or `filter()`.

#### C. Model Location

- `Spec` in `supekku/scripts/lib/specs/models.py:15` — `@dataclass(frozen=True)`

#### D. Error Handling

- Missing ID: returns None from `get()`
- Parse errors: silently skipped in `_register_spec()` (lines 91-95)

---

### 2. DecisionRegistry

**File:** `supekku/scripts/lib/decisions/registry.py`

#### A. Class Structure

- **Class:** `DecisionRegistry` (no parent)
- **Constructor** (lines 116-119):

  ```python
  def __init__(self, *, root: Path | None = None) -> None:
  ```

  - Keyword-only `root`, optional, auto-discovers
  - **Lazy**: does NOT load in `__init__`

- **Class method:** `load(root=None) -> DecisionRegistry` (lines 121-124)

#### B. Core API

| Method          | Signature                                                                         | Line    | Semantics                               |
| --------------- | --------------------------------------------------------------------------------- | ------- | --------------------------------------- |
| **Collection**  | `collect() -> dict[str, DecisionRecord]`                                          | 126-143 | Re-parses files each call               |
| **ID lookup**   | `find(decision_id: str) -> DecisionRecord \| None`                                | 294-297 | Returns None                            |
| **Iteration**   | `iter(status: str \| None = None) -> Iterator[DecisionRecord]`                    | 287-292 | Optional status filter                  |
| **Filter**      | `filter(tag, spec, delta, requirement, policy, standard) -> list[DecisionRecord]` | 299-332 | AND logic                               |
| **Persistence** | `write(path=None) -> None`                                                        | 243-262 | Collects, builds backlinks, writes YAML |
| **Persistence** | `sync() -> None`                                                                  | 283-285 | Wrapper for `write()`                   |
| **Persistence** | `sync_with_symlinks() -> None`                                                    | 393-397 | write + rebuild status symlinks         |

#### C. Model Location

- `DecisionRecord` defined inline (lines 21-111) — mutable `@dataclass`

#### D. Error Handling

- Missing ID: returns None
- Parse errors: silently skipped (lines 139-141)

---

### 3. ChangeRegistry

**File:** `supekku/scripts/lib/changes/registry.py`

#### A. Class Structure

- **Class:** `ChangeRegistry` (no parent)
- **Constructor** (lines 39-46):

  ```python
  def __init__(self, *, root: Path | None = None, kind: str) -> None:
  ```

  - Keyword-only `root` + required `kind` (delta/revision/audit)
  - Raises `ValueError` if kind invalid
  - **Lazy**: no loading in `__init__`

#### B. Core API

| Method          | Signature                                                                 | Line    | Semantics                    |
| --------------- | ------------------------------------------------------------------------- | ------- | ---------------------------- |
| **Collection**  | `collect() -> dict[str, ChangeArtifact]`                                  | 48-85   | Handles bundles + flat files |
| **Filter**      | `find_by_implements(requirement_id: str \| None) -> list[ChangeArtifact]` | 100-126 | Empty list if None           |
| **Persistence** | `sync() -> None`                                                          | 87-98   | Collects + writes YAML       |

No `find()`, `iter()`, or generic `filter()`.

Also: `discover_plans()` function (lines 143-197) and `PlanSummary` dataclass (lines 129-140).

#### C. Model Location

- `ChangeArtifact` in `supekku/scripts/lib/changes/artifacts.py`

#### D. Error Handling

- No `find()` method; consumers must `collect()` then dict access
- Parse errors: warning to stderr, file skipped (lines 76-81)

---

### 4. RequirementsRegistry

**File:** `supekku/scripts/lib/requirements/registry.py`

#### A. Class Structure

- **Class:** `RequirementsRegistry` (no parent)
- **Constructor** (lines 155-158):

  ```python
  def __init__(self, registry_path: Path) -> None:
  ```

  - **Positional required `registry_path`** — NOT `root`
  - No auto-discovery of repo root
  - **Eager**: calls `_load()` at construction

#### B. Core API

| Method          | Signature                                                                         | Line      | Semantics                    |
| --------------- | --------------------------------------------------------------------------------- | --------- | ---------------------------- |
| **Collection**  | `.records: dict[str, RequirementRecord]`                                          | 157       | Public mutable attribute     |
| **Persistence** | `save() -> None`                                                                  | 170-179   | Writes YAML                  |
| **Sync**        | `sync_from_specs(...) -> SyncStats`                                               | 182-335   | Complex multi-source sync    |
| **Search**      | `search(query, status, spec, implemented_by, introduced_by, verified_by) -> list` | 1079-1108 | Free-text + filters          |
| **Filter**      | `find_by_verified_by(artifact_pattern) -> list`                                   | 1124-1155 | Glob pattern on verified_by  |
| **Filter**      | `find_by_verification_status(statuses) -> list`                                   | 1157-1181 | OR logic on coverage status  |
| **Filter**      | `find_by_verification_kind(kinds) -> list`                                        | 1183-1207 | OR logic on coverage kind    |
| **Mutation**    | `move_requirement(uid, new_spec_id, ...) -> str`                                  | 1032-1076 | Raises KeyError/ValueError   |
| **Mutation**    | `set_status(uid, status) -> None`                                                 | 1110-1122 | Raises ValueError if invalid |

No `find()`, `collect()`, `iter()`, or generic `filter()`.

#### C. Model Location

- `RequirementRecord` defined inline (lines 61-141) — mutable `@dataclass`

#### D. Error Handling

- Missing ID: direct dict access returns None; `move_requirement()` raises `KeyError`
- Invalid status: `set_status()` raises `ValueError` (lines 1112-1116)

---

### 5. BacklogRegistry (functional)

**File:** `supekku/scripts/lib/backlog/registry.py`

#### A. Structure

**No class.** Module-level functions:

| Function      | Signature                                                                 | Line    | Semantics                |
| ------------- | ------------------------------------------------------------------------- | ------- | ------------------------ |
| **Load**      | `load_backlog_registry(root=None) -> list[str]`                           | 90-115  | Returns ordered ID list  |
| **Save**      | `save_backlog_registry(ordering, root=None) -> None`                      | 118-143 | Writes ordering YAML     |
| **Sync**      | `sync_backlog_registry(root=None) -> dict[str, int]`                      | 146-192 | Returns stats dict       |
| **Discover**  | `discover_backlog_items(root=None, kind="all") -> list[BacklogItem]`      | 324-418 | Sorted by ID             |
| **ID lookup** | `find_backlog_items_by_id(item_id, root, kind=None) -> list[BacklogItem]` | 421-491 | Returns list (may be >1) |
| **Create**    | `create_backlog_entry(kind, name, repo_root) -> Path`                     | 218-263 | Template-based           |

#### B. Model Location

- `BacklogItem` in `supekku/scripts/lib/backlog/models.py` — mutable `@dataclass`

#### C. Error Handling

- Missing ID: returns empty list
- Invalid kind: raises `ValueError` (line 239-240)
- Parse errors: warning to stderr, skipped (lines 382-388)

---

### 6. PolicyRegistry

**File:** `supekku/scripts/lib/policies/registry.py`

#### A. Class Structure

- **Class:** `PolicyRegistry` (no parent)
- **Constructor** (lines 102-105):

  ```python
  def __init__(self, *, root: Path | None = None) -> None:
  ```

  - Keyword-only, optional root, auto-discovers
  - **Lazy**

- **Class method:** `load(root=None)` (lines 107-110)

#### B. Core API

| Method          | Signature                                                 | Line    | Semantics        |
| --------------- | --------------------------------------------------------- | ------- | ---------------- |
| **Collection**  | `collect() -> dict[str, PolicyRecord]`                    | 112-129 |                  |
| **ID lookup**   | `find(policy_id: str) -> PolicyRecord \| None`            | 276-279 | Returns None     |
| **Iteration**   | `iter(status=None) -> Iterator[PolicyRecord]`             | 269-274 |                  |
| **Filter**      | `filter(tag, spec, delta, requirement, standard) -> list` | 281-311 | AND logic        |
| **Persistence** | `write(path=None) -> None`                                | 209-228 | Builds backlinks |
| **Persistence** | `sync() -> None`                                          | 265-267 |                  |

#### C. Model Location

- `PolicyRecord` defined inline (lines 22-96) — mutable `@dataclass`

Near-identical to DecisionRegistry.

---

### 7. StandardRegistry

**File:** `supekku/scripts/lib/standards/registry.py`

#### A. Class Structure

- **Class:** `StandardRegistry` (no parent)
- **Constructor** (lines 111-114):

  ```python
  def __init__(self, *, root: Path | None = None) -> None:
  ```

  - Keyword-only, optional root, auto-discovers
  - **Lazy**

- **Class method:** `load(root=None)` (lines 116-119)

#### B. Core API

| Method          | Signature                                               | Line    | Semantics                                  |
| --------------- | ------------------------------------------------------- | ------- | ------------------------------------------ |
| **Collection**  | `collect() -> dict[str, StandardRecord]`                | 121-138 |                                            |
| **ID lookup**   | `find(standard_id: str) -> StandardRecord \| None`      | 304-307 | Returns None                               |
| **Iteration**   | `iter(status=None) -> Iterator[StandardRecord]`         | 297-302 |                                            |
| **Filter**      | `filter(tag, spec, delta, requirement, policy) -> list` | 309-339 | AND logic                                  |
| **Persistence** | `write(path=None) -> None`                              | 218-237 | Builds backlinks from Decisions + Policies |
| **Persistence** | `sync() -> None`                                        | 293-295 |                                            |

#### C. Model Location

- `StandardRecord` defined inline (lines 24-105) — mutable `@dataclass`

Near-identical to PolicyRegistry. Builds backlinks from both DecisionRegistry and PolicyRegistry.

---

### 8. MemoryRegistry

**File:** `supekku/scripts/lib/memory/registry.py`

#### A. Class Structure

- **Class:** `MemoryRegistry` (no parent)
- **Constructor** (lines 26-33):

  ```python
  def __init__(self, *, root: Path | None = None, directory: Path | None = None) -> None:
  ```

  - Keyword-only, optional root + optional directory override
  - **Lazy**

#### B. Core API

| Method         | Signature                                      | Line    | Semantics               |
| -------------- | ---------------------------------------------- | ------- | ----------------------- |
| **Collection** | `collect() -> dict[str, MemoryRecord]`         | 35-53   |                         |
| **Collection** | `collect_bodies() -> dict[str, str]`           | 77-92   | Body text for graph ops |
| **ID lookup**  | `find(memory_id: str) -> MemoryRecord \| None` | 94-103  | Returns None            |
| **Iteration**  | `iter(status=None) -> Iterator[MemoryRecord]`  | 105-116 |                         |
| **Filter**     | `filter(memory_type, status, tag) -> list`     | 118-144 | AND logic               |

No sync/write (read-only).

#### C. Model Location

- `MemoryRecord` in `supekku/scripts/lib/memory/models.py` — mutable `@dataclass`

---

### 9. CardRegistry

**File:** `supekku/scripts/lib/cards/registry.py`

#### A. Class Structure

- **Class:** `CardRegistry` (no parent)
- **Constructor** (lines 29-36):

  ```python
  def __init__(self, root: Path) -> None:
  ```

  - **Positional required `root`** — no auto-discovery
  - **Lazy**

#### B. Core API

| Method         | Signature                                 | Line    | Semantics                               |
| -------------- | ----------------------------------------- | ------- | --------------------------------------- |
| **Discovery**  | `all_cards() -> list[Card]`               | 38-57   | Sorted list                             |
| **Lane**       | `cards_by_lane(lane: str) -> list[Card]`  | 59-68   |                                         |
| **ID alloc**   | `next_id() -> str`                        | 70-90   | Max+1                                   |
| **Create**     | `create_card(description, lane) -> Card`  | 92-133  | Template-based                          |
| **Resolution** | `resolve_card(card_id, anywhere) -> Card` | 135-169 | **Raises** FileNotFoundError/ValueError |
| **Resolution** | `resolve_path(card_id, anywhere) -> str`  | 171-182 |                                         |

No `find()`, `collect()`, `iter()`, `filter()`, or `sync()`.

#### C. Model Location

- `Card` in `supekku/scripts/lib/cards/models.py` — mutable `@dataclass`

#### D. Error Handling

- Missing ID: `resolve_card()` raises `FileNotFoundError` (lines 159-161)
- Ambiguous: raises `ValueError` with candidate list (lines 163-167)

---

## CLI Consumer: common.py

**File:** `supekku/cli/common.py`

### Resolver Functions

Each follows pattern: `_resolve_X(root, raw_id) -> ArtifactRef`

| Artifact    | Function               | Lines   | Registry Pattern                      | Workarounds                                                |
| ----------- | ---------------------- | ------- | ------------------------------------- | ---------------------------------------------------------- |
| spec        | `_resolve_spec`        | 333-340 | `registry.get(raw_id)`                | None                                                       |
| change      | `_resolve_change`      | 343-352 | `registry.collect()` then dict access | No `find()` — must collect all                             |
| decision    | `_resolve_decision`    | 355-363 | `registry.find(normalized)`           | None                                                       |
| policy      | `_resolve_policy`      | 366-374 | `registry.find(normalized)`           | None                                                       |
| standard    | `_resolve_standard`    | 377-385 | `registry.find(normalized)`           | None                                                       |
| requirement | `_resolve_requirement` | 388-402 | `registry.records.get(normalized)`    | Takes `registry_path` not `root`; colon->dot normalisation |
| card        | `_resolve_card`        | 405-413 | `registry.resolve_card(raw_id)`       | Try/except for FileNotFoundError/ValueError                |
| memory      | `_resolve_memory`      | 416-423 | `registry.find(raw_id)`               | None                                                       |
| backlog     | `_resolve_backlog`     | 456-467 | `find_backlog_items_by_id()` function | Ambiguity handling; function not method                    |

### ID Normalisation

- `normalize_id(artifact_type, raw_id) -> str` (lines 286-324): expands shorthand "1" -> "ADR-001"
- Requirement-specific: colon->dot conversion (lines 394-395, 654-655)
- Memory-specific: "mem." prefix addition (lines 632-634)

### Dispatch Tables

- `_ARTIFACT_RESOLVERS` (lines 471-487) — single artifact lookup
- `_ARTIFACT_FINDERS` (lines 695-712) — pattern-matching finder

---

## Convergence Groups

### Group A: Target Pattern (4 registries)

Decision, Policy, Standard, Memory all share:

- `__init__(*, root=None)` keyword-only
- `collect() -> dict[str, Record]`
- `find(id) -> Record | None`
- `iter(status=None)`
- `filter(**domain_kwargs)`
- Lazy loading (no work in `__init__`)

This is the target convention.

### Group B: Alignable with additive changes (2 registries)

- **SpecRegistry**: Rename `get()` -> `find()`. Add `collect()` returning dict. Add `iter()`. Constructor -> keyword-only. (Eager loading is a design choice, not a defect.)
- **ChangeRegistry**: Add `find(id)`. Add `iter()`. Already has `collect()`. Extra `kind` param is domain-specific, acceptable.

### Group C: Structural changes needed (3 registries)

- **RequirementsRegistry**: Constructor takes `registry_path` not `root`. Public `.records` attribute. No `find()`, `collect()`, `iter()`. Massive internal complexity — alignment is additive (add `find()`, `collect()` wrapper) but constructor change has blast radius.
- **BacklogRegistry**: No class at all. Would need class wrapper around existing functions.
- **CardRegistry**: Positional required `root`, no auto-discovery. `resolve_card()` raises instead of returning None. No `find()`, `collect()`, `iter()`.

---

## Risk Assessment

| Change                                     | Risk   | Mitigation                                                |
| ------------------------------------------ | ------ | --------------------------------------------------------- |
| Add `find()` to Change, Requirements, Card | Low    | Additive, no breaking changes                             |
| Rename `get()` -> `find()` on Spec         | Medium | Deprecation alias, grep for callers                       |
| Add `collect()` to Spec                    | Low    | Wrapper around existing cache                             |
| Add `iter()` everywhere                    | Low    | Additive                                                  |
| Normalise constructors to kw-only          | Medium | Keyword-only is breaking for positional callers           |
| Class-ify Backlog                          | High   | All callers must change; functional API must be preserved |
| RequirementsRegistry constructor change    | Medium | Many callers construct with path directly                 |

---

## References

- ISSUE-019: Registry API drift (this delta's origin)
- IMPR-009: TUI dashboard (downstream consumer)
- SPEC-110: CLI orchestration (documents current usage)
- SPEC-122: Requirements registry (most detailed spec)
- SPEC-115, SPEC-117, SPEC-123: Stub specs for Change, Decision, Spec registries
- ADR-002: No backlinks in frontmatter (partially violated by DecisionRecord)
