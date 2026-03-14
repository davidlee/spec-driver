# Notes for DE-057

## Preflight Research (2026-03-07)

### Current State

- Backlog is function-based: `discover_backlog_items()`, `find_item()`,
  `find_backlog_items_by_id()` in `backlog/registry.py` (536 lines)
- `BacklogItem` dataclass in `backlog/models.py` (28 lines) — unified model
  with kind-specific fields (severity, impact for issues+risks; likelihood
  for risks)
- Priority ordering in `backlog/priority.py` (360 lines) — head-tail
  partitioning algorithm, editor integration, `backlog.yaml` ordering
- 4 item types: issue (ISSUE-), problem (PROB-), improvement (IMPR-),
  risk (RISK-)
- Templates dict in registry.py defines per-kind defaults (prefix, subdir,
  status, kind-specific fields)
- Registry file: `.spec-driver/registry/backlog.yaml` — ordering only,
  no metadata

### artifact_view.py Shim (DE-053)

- `_collect_backlog()` (lines 213-242): duplicates `_collect_safe()` error
  isolation pattern because no class-based registry exists
- `_load_type()` (line 264): `if art_type == ArtifactType.BACKLOG:` special
  case bypasses `_make_registry()` / `_REGISTRY_FACTORIES`
- `ArtifactType.BACKLOG` is single enum value — "Backlog Item(s)"
- DEC-053-08: shim is explicitly disposable
- DEC-053-11: "backlog sub-kinds expected to evolve" — but we decided
  against speciation (unified registry with kind filter)

### Speciation Decision

Decided: **Option A — unified `BacklogRegistry`** with `kind` as filter param.

Rationale:

- Items share single model cleanly
- Priority ordering operates across types
- Unified backlog view is the primary interaction surface
- 4 separate registries = 4x boilerplate for marginal gain
- `list issues` = `filter(kind="issue")` underneath

### Related Backlog Items (in scope)

- **ISSUE-009** (p2): Status fields lack enums — define per-kind status enums
- **ISSUE-026** (p3): `_sync_backlog()` doesn't thread `dry_run` param
- **ISSUE-034**: `resolve links` doesn't support backlog items
- **ISSUE-043** (p3): `--from-backlog` greedy flag consumes subsequent flags

### Related Backlog Items (deferred)

- **ISSUE-016** (p2): Sync backlog requirements to requirements registry
  (cross-domain, separate delta)
- **IMPR-010**: Status-aware checkboxes in prioritize UX (depends on status
  enums from this delta)

### Reference Registries (ADR-009 conformant)

Target pattern from DecisionRegistry/PolicyRegistry/StandardRegistry/MemoryRegistry:

- `find(id) -> Record | None`
- `collect() -> dict[str, Record]`
- `iter(status=None) -> Iterator[Record]`
- `filter(...) -> list[Record]`
- Constructor: `(*, root: Path | None = None)`

### Existing Status Values (observed)

From TEMPLATES dict and frontmatter:

- **issue**: open, in-progress, resolved, done, implemented
- **problem**: captured, investigating, mitigated, resolved
- **improvement**: idea, planned, in-progress, implemented
- **risk**: suspected, confirmed, mitigated, accepted, expired

## Phase 1 Implementation (2026-03-07)

### Done

- **BacklogRegistry class** in `backlog/registry.py` — ADR-009 conformant:
  `find()`, `collect()`, `iter(kind, status)`, `filter(kind, status, tag, severity)`.
  Eager loading with dict cache. Constructor `(*, root=None)` with auto-discovery.
- **Per-kind status frozensets** in `backlog/models.py` — `ISSUE_STATUSES`,
  `PROBLEM_STATUSES`, `IMPROVEMENT_STATUSES`, `RISK_STATUSES`, `BACKLOG_STATUSES`,
  `DEFAULT_HIDDEN_STATUSES`, `ALL_VALID_STATUSES`, `is_valid_status()`.
- **Module-level wrappers**: `discover_backlog_items()`, `find_backlog_items_by_id()`,
  `find_item()` now delegate to `BacklogRegistry`. Signatures preserved.
- **Tests**: 26 new tests (17 BacklogRegistry, 9 status sets) — all pass.
  Existing 25 tests adapted and passing. 51 total in backlog package.
- **Full suite**: 2881 passed, 3 skipped (user confirmed green at 3% context remaining).

### Surprises / Adaptations

- **Duplicate ID handling changed**: `find_backlog_items_by_id()` previously returned
  multiple items for duplicate IDs; now returns 1 (registry deduplicates, last wins).
  Registry logs a warning on duplicates. Updated tests:
  - `registry_test.py::test_duplicate_ids_logs_warning` (was `test_duplicate_ids_returns_multiple`)
  - `registry_test.py::test_find_item_logs_warning_on_duplicate` (was `test_find_item_warns_on_multiple`)
  - `common_test.py::test_duplicate_ids_resolves_one` (was `test_raises_ambiguous_for_duplicates`)
- Warning mechanism changed from `warnings.warn()` to `logger.warning()` for
  duplicate IDs — more consistent with rest of codebase.
- Removed unused `sys` and `warnings` imports from registry.py.

### Rough Edges / Follow-up

- `common.py::_resolve_backlog()` still calls `find_backlog_items_by_id()` wrapper
  rather than `BacklogRegistry` directly — Phase 2 will update this.
- `list.py::list_backlog()` still uses `discover_backlog_items()` wrapper — Phase 2.
- Formatter auto-reformatted models.py frozenset definitions to multi-line.

### Verification

- `just test`: green (2881 passed, user confirmed)
- `ruff check`: clean on backlog package
- `pylint`: 9.92/10 on changed source files
- Uncommitted work.

### Next: Phase 2 (Integration)

Remove artifact_view.py shim, update CLI consumers, fix ISSUE-026/-034/-043.
See `phases/phase-02.md` for task breakdown.

## Phase 2 Implementation (2026-03-07)

### Done

- **2.1 Remove artifact_view.py shim**: Deleted `_collect_backlog()` (30 lines).
  Removed `_load_type()` special-case for BACKLOG. Added `_make_backlog_registry`
  factory and `ArtifactType.BACKLOG` entry in `_REGISTRY_FACTORIES`. Backlog now
  flows through standard `_collect_safe()` path like all other types.
- **2.2 Update cli/common.py resolvers**: `_resolve_backlog()` and `_find_backlog()`
  now use `BacklogRegistry(root=root)` directly. Kind scoping preserved in resolver
  (filter by kind when kind specified). Ambiguity detection simplified: registry
  deduplicates, so no multi-match possible.
- **2.3 Update cli/list.py**: `list_backlog()` uses `BacklogRegistry(root=)` with
  `iter(kind=)` instead of `discover_backlog_items()`. Default hidden statuses
  now use `DEFAULT_HIDDEN_STATUSES` from `backlog/models.py`.
- **2.4 Fix ISSUE-026**: Added `dry_run: bool = False` keyword param to
  `sync_backlog_registry()`. When True, computes stats but skips
  `save_backlog_registry()`. `_sync_backlog()` in `cli/sync.py` threads the
  `dry_run` param from the CLI option.
- **2.5 Fix ISSUE-034**: Added `_collect_backlog_items()` to `cli/resolve.py`
  following existing `_collect_decisions()` pattern. Called from
  `_build_artifact_index()`. Keys: item IDs (ISSUE-016, PROB-002, etc.).
  Values: `(relative_path, item.kind)`.
- **2.6 Fix ISSUE-043**: Added `_validate_backlog_id()` callback on `--from-backlog`
  option in `cli/create.py`. Rejects non-ID values with clear `BadParameter` message.
  Replaced `discover_backlog_items()` with `BacklogRegistry.find()` for item lookup.
  Mitigation only — Click root cause unfixable per DEC-057-07.
- **2.7 Tests**: Added 14 new tests:
  - `artifact_view_test.py`: 4 tests (VT-057-artifact-view) — factory in registry,
    returns BacklogRegistry, snapshot loads via standard path, malformed item handling
  - `resolve_test.py`: 3 tests (VT-057-link-resolver) — includes backlog items,
    multiple kinds, unknown ID absent
  - `sync_test.py`: 2 tests (VT-057-sync-dryrun) — dry_run skips write, non-dry writes
  - `create_test.py`: 4 tests (VT-057-from-backlog) — rejects non-ID, rejects garbage,
    accepts valid issue ID, accepts valid risk ID

### Surprises / Adaptations

- **Rich box formatting in test assertions**: Typer's `BadParameter` output uses Rich
  box rendering (`│`, `╭╮╰╯`) which breaks multi-line strings across lines with box
  characters. Test assertions strip non-ASCII and normalise whitespace to match.
- **DEC-057-09 error behaviour**: Malformed backlog items are skipped at parse time
  inside `BacklogRegistry._parse_item()` (warning logged), so they never reach
  `_collect_safe()`. The behaviour change is subtle: the old shim also logged-and-skipped,
  but if `collect()` itself threw, `_collect_safe()` would now produce a corpus-level
  error entry. Net effect is correct — consistent with all other registries.
- **Test count variance**: Phase 1 reported 2881. Phase 2 final: 2894 passed. The
  increase is from new tests (14) plus the evolving uncommitted baseline.

### Rough Edges / Follow-up

- `AmbiguousArtifactError` path in `_resolve_backlog()` is now unreachable because
  `BacklogRegistry.find()` returns at most one item (deduplication). The kind guard
  still raises `ArtifactNotFoundError` if the item exists but kind doesn't match.
  This is correct behaviour but the `AmbiguousArtifactError` import is vestigial in
  the backlog context (still needed by other resolvers, so no import to remove).
- `list.py` still has the redundant `from pathlib import Path` inline import at line
  1601 (it's already at module level). Pre-existing; not worth a separate fix.

### Verification

- `just`: green (2894 passed, 3 skipped, ruff clean, pylint 9.50/10)
- All VTs: VT-057-artifact-view, VT-057-sync-dryrun, VT-057-link-resolver,
  VT-057-from-backlog, VT-057-regression — passing
- Uncommitted work (Phase 1 + Phase 2 combined).

### Next: Phase 3 (Closure)

Verify all exit criteria, update backlog items (close ISSUE-026, -034; partially
close ISSUE-043, ISSUE-009), update delta docs, run close-change.
