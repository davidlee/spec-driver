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
