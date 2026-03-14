---
id: IP-057.PHASE-01
slug: "057-backlogregistry_class_normalisation-phase-01"
name: IP-057 Phase 01 - Core Modelling
created: "2026-03-07"
updated: "2026-03-07"
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-057.PHASE-01
plan: IP-057
delta: DE-057
objective: >-
  BacklogRegistry class with ADR-009 surface + per-kind status sets + tests
entrance_criteria:
  - DR-057 decisions resolved
exit_criteria:
  - BacklogRegistry class passes ADR-009 checklist (find/collect/iter/filter)
  - Per-kind status frozensets defined with is_valid_status() helper
  - DEFAULT_HIDDEN_STATUSES matches current list_backlog() exclusion
  - Module-level wrapper functions delegate to registry class
  - VT-057-registry and VT-057-status-enums pass
  - just passes
verification:
  tests:
    - VT-057-registry
    - VT-057-status-enums
  evidence: []
tasks:
  - id: "1.1"
    description: Define per-kind status sets in models.py
  - id: "1.2"
    description: Implement BacklogRegistry class in registry.py
  - id: "1.3"
    description: Convert module-level functions to thin wrappers
  - id: "1.4"
    description: Write tests for registry class and status sets
risks:
  - description: Status sets incomplete
    mitigation: Derive from TEMPLATES + grep observed values; permissive validation
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-057.PHASE-01
```

# Phase 1 - Core Modelling

## 1. Objective

Implement `BacklogRegistry` class conforming to ADR-009 and define per-kind
status sets. This phase produces the foundation that Phase 2 integrates into
consumers.

## 2. Links & References

- **Delta**: DE-057
- **Design Revision**: DR-057 (DEC-057-01 through -05, -08)
- **ADR**: ADR-009 (standard registry API convention)
- **Existing code**:
  - `supekku/scripts/lib/backlog/registry.py` (current functions)
  - `supekku/scripts/lib/backlog/models.py` (BacklogItem dataclass)
  - `supekku/scripts/lib/decisions/registry.py` (reference pattern)

## 3. Entrance Criteria

- [x] DR-057 all decisions resolved (DEC-057-01 through -09)
- [x] Adversarial review findings addressed

## 4. Exit Criteria / Done When

- [ ] `BacklogRegistry` exposes `find()`, `collect()`, `iter()`, `filter()`
- [ ] Constructor is `(*, root: Path | None = None)` with auto-discovery
- [ ] Eager loading: constructor scans once, methods read from cache
- [ ] `iter(kind=None, status=None)` and `filter(kind=None, status=None)`
      support kind as domain-specific parameter
- [ ] Per-kind status frozensets defined in `models.py`
- [ ] `DEFAULT_HIDDEN_STATUSES` = `{"resolved", "implemented"}` (current behaviour)
- [ ] `is_valid_status(kind, status) -> bool` helper with `logger.warning()`
      for unknown values
- [ ] Module-level functions (`discover_backlog_items`, `find_item`,
      `find_backlog_items_by_id`) delegate to `BacklogRegistry`
- [ ] VT-057-registry passes
- [ ] VT-057-status-enums passes
- [ ] `just` passes

## 5. Verification

- `VT-057-registry`: BacklogRegistry tests in `registry_test.py`
  - `find(id)` returns correct item or None
  - `collect()` returns full dict keyed by ID
  - `iter()` yields all items; `iter(kind="issue")` yields issues only;
    `iter(status="open")` yields open items only
  - `filter(kind="issue", status="open")` combines filters
  - Empty corpus (no backlog dir) returns empty results
  - Constructor auto-discovers root when `root=None`
- `VT-057-status-enums`: Status set tests in `models_test.py`
  - Each kind's default status (from TEMPLATES) is in its status set
  - `is_valid_status("issue", "open")` returns True
  - `is_valid_status("issue", "xyzzy")` returns False + logs warning
  - `DEFAULT_HIDDEN_STATUSES` == `{"resolved", "implemented"}`
- Run: `just test`, `just lint`, `just pylint`

## 6. Assumptions & STOP Conditions

- Assumptions:
  - DecisionRegistry pattern is the reference implementation
  - Eager loading is appropriate for ~60 item corpus
  - Existing `discover_backlog_items()` logic is correct and can be wrapped
- STOP when:
  - Existing module-level functions have unexpected callers that break with
    wrapper approach
  - Status sets need broader discussion (escalate to user)

## 7. Tasks & Progress

| Status | ID  | Description                                | Parallel? | Notes                 |
| ------ | --- | ------------------------------------------ | --------- | --------------------- |
| [ ]    | 1.1 | Define per-kind status sets in models.py   | [P]       | DEC-057-02, -08       |
| [ ]    | 1.2 | Implement BacklogRegistry class            |           | DEC-057-01, -05       |
| [ ]    | 1.3 | Convert module-level functions to wrappers |           | DEC-057-04; after 1.2 |
| [ ]    | 1.4 | Write VT-057-registry tests                |           | After 1.2             |
| [ ]    | 1.5 | Write VT-057-status-enums tests            | [P]       | After 1.1             |
| [ ]    | 1.6 | Lint + full test pass                      |           | After all above       |

### Task Details

- **1.1 Define per-kind status sets**
  - **Files**: `supekku/scripts/lib/backlog/models.py`
  - **Approach**: Add `ISSUE_STATUSES`, `PROBLEM_STATUSES`,
    `IMPROVEMENT_STATUSES`, `RISK_STATUSES` frozensets. Add
    `BACKLOG_STATUSES` dict mapping kind→set. Add
    `DEFAULT_HIDDEN_STATUSES` frozenset = `{"resolved", "implemented"}`.
    Add `is_valid_status(kind: str, status: str) -> bool` that checks
    membership and logs warning for unknown values.
  - **Testing**: VT-057-status-enums (task 1.5)

- **1.2 Implement BacklogRegistry class**
  - **Files**: `supekku/scripts/lib/backlog/registry.py`
  - **Approach**: New class at top of module. Constructor calls existing
    discovery logic, caches in `self._items: dict[str, BacklogItem]`.
    `collect()` returns `dict(self._items)`. `find(id)` does
    `self._items.get(id)`. `iter(kind, status)` filters cache.
    `filter(kind, status, ...)` filters cache and returns list.
  - **Design**: Mirror DecisionRegistry shape. `kind` param on iter/filter
    only, not on collect (DEC-057-05). Auto-discover root via
    `find_repo_root()` (DEC-057-01).
  - **Testing**: VT-057-registry (task 1.4)

- **1.3 Convert module-level functions to wrappers**
  - **Files**: `supekku/scripts/lib/backlog/registry.py`
  - **Approach**: `discover_backlog_items()` → instantiate registry, call
    `iter()`. `find_item()` → instantiate registry, call `find()`.
    `find_backlog_items_by_id()` → instantiate registry, call `find()`.
    Keep signatures identical.
  - **Risk**: Callers may depend on subtle behaviour differences. Grep all
    callers first.

- **1.4 Write VT-057-registry tests**
  - **Files**: `supekku/scripts/lib/backlog/registry_test.py`
  - **Approach**: Extend existing test file. Use existing test fixtures
    where possible. Test find/collect/iter/filter with kind and status
    params. Test empty corpus. Test constructor auto-discovery.

- **1.5 Write VT-057-status-enums tests**
  - **Files**: `supekku/scripts/lib/backlog/models_test.py` (new)
  - **Approach**: Test each kind's default in its set. Test valid/invalid
    status. Test warning on unknown. Test DEFAULT_HIDDEN_STATUSES value.

## 8. Risks & Mitigations

| Risk                                      | Mitigation                                                | Status    |
| ----------------------------------------- | --------------------------------------------------------- | --------- |
| Wrapper functions change subtle behaviour | Grep all callers; test existing behaviour before wrapping | open      |
| Status sets miss valid values             | Permissive validation (warn, don't reject)                | mitigated |

## 9. Decisions & Outcomes

- 2026-03-07 - All design decisions pre-resolved in DR-057

## 10. Findings / Research Notes

- Reference pattern: DecisionRegistry in `decisions/registry.py`
- Existing discovery logic in `discover_backlog_items()` handles filesystem
  walk, YAML parsing, BacklogItem construction — wrap, don't rewrite

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Hand-off notes to Phase 2
