# Notes for DE-050

## 2026-03-07 - Phase 1 complete (SpecRegistry + ChangeRegistry)

### Done

- **SpecRegistry** (`supekku/scripts/lib/specs/registry.py`):
  - Added `find()`, `collect()`, `iter(status=)`, `filter(status=, category=, kind=, tag=)`
  - `get()` now delegates to `find()` with `DeprecationWarning`
  - `filter()` params chosen from Spec model properties: status, category, kind, tag
- **ChangeRegistry** (`supekku/scripts/lib/changes/registry.py`):
  - Added `find()`, `iter(status=)`, `filter(status=)`
  - `collect()` already existed — `find()` and `iter()` delegate to it
  - `filter()` has only `status` param; `kind` is constructor-level, not per-artifact
- **Tests**: 16 new tests across both registries (29 total spec, 18 total change)
- **Verification**: `just` passes — 2673 tests, ruff clean, pylint 9.55/10

### Observations

- ~10 callers of `SpecRegistry.get()` in production code — deprecation alias keeps
  them all working. DeprecationWarnings visible in test output.
- ChangeRegistry `find()`/`iter()` call `collect()` each time (lazy, re-parses).
  Acceptable for current corpus size per ADR-009 §4.
- ChangeRegistry `filter()` is minimal (status only). Could add `tag` later if
  ChangeArtifact tags become used in practice.

### Follow-up

- Phase 2: Requirements, Card, Backlog registries (higher risk — constructor changes)
- Existing callers of `get()` should migrate to `find()` in a future cleanup pass

### Git state

- Committed as 344e6e5

## 2026-03-07 - Phase 2 complete (Requirements + Card + Backlog)

### Done

- **RequirementsRegistry** (`supekku/scripts/lib/requirements/registry.py`):
  - Constructor now accepts optional `root` keyword alongside existing positional
    `registry_path`. `RequirementsRegistry(path)` still works;
    `RequirementsRegistry(root=root)` auto-discovers path.
  - Added `find(uid)`, `collect()`, `iter(status=)`, `filter(status=, spec=, kind=, tag=)`
- **CardRegistry** (`supekku/scripts/lib/cards/registry.py`):
  - Added `find(id)`, `collect()`, `iter(lane=)`, `filter(lane=)` per DEC-050-05
  - `resolve_card()` kept for strict resolution (raises on missing/ambiguous)
- **BacklogRegistry** (`supekku/scripts/lib/backlog/registry.py`):
  - Added `find_item(id, root, kind)` convenience function
  - Returns first match or None; warns on multiple matches per DEC-050-02
- **Tests**: 27 new tests across three registries (2700 total suite)
- **Verification**: `just` passes — 2700 tests, ruff clean, pylint 9.54/10

### Observations

- RequirementsRegistry constructor change was clean — `registry_path` is now
  `Path | None = None` with `root` as keyword-only alternative. Lazy import of
  `get_registry_dir` avoids circular import.
- CardRegistry `find()` scans `all_cards()` each call (no cache). Acceptable for
  small kanban boards. `collect()` similarly builds dict from `all_cards()`.
- All 36+ existing callers of `RequirementsRegistry(path)` continue working.

### Git state

- Uncommitted work

## 2026-03-06 - ADR draft for registry convention

- Drafted `ADR-009: standard registry API convention`.
- Decision: codify the minimum registry read surface as `find()`, `collect()`,
  `iter(status=None)`, and `filter(...)` plus keyword-only optional `root`
  auto-discovery for class-based registries.
- Adaptation: kept `filter()` mandatory, but as a domain-specific method rather
  than a shared universal signature; explicitly deferred any `Protocol`/ABC
  until post-normalisation convergence is proven.
- Rough edges / follow-up:
  - Requirements, backlog, and card registries remain structurally different;
    ADR-009 deliberately leaves their deeper reshaping to DE-050 implementation.
- Git state: uncommitted work, including unrelated repo changes already present.
- Verification: no commands run after this edit; this was ADR/notes drafting only.
