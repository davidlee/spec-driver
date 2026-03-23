---
id: IP-125-P04
slug: "125-enforce_explicit_module_boundaries_and_coupling_constraints-phase-04"
name: Orchestration ownership and shim retirement
created: "2026-03-24"
updated: "2026-03-24"
status: completed
kind: phase
plan: IP-125
delta: DE-125
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-125-P04
plan: IP-125
delta: DE-125
objective: >-
  Move cross-registry source collection out of registries and into orchestration,
  then define retirement criteria for re-export shims and legacy-core imports
  before broader registry migration.
entrance_criteria:
  - Phase 3 completed with relations pilots and backlink helper extraction
  - Post-pilot architectural verdict recorded in DE-125 notes
  - Domain Internal Layers contract passing in import-linter
exit_criteria:
  - Workspace.sync_policies() and Workspace.sync_standards() pass decision_sources / policy_sources to registries
  - Registry backlink methods treat None as skip — no fallback to sibling instantiation
  - Workspace graph collection has a documented orchestration home or tracked owning seam (actual move is a separate patch)
  - Shim retirement criteria are documented for legacy relations re-exports
  - Legacy-core import retirement criteria are documented for migrated domain modules
verification:
  tests:
    - uvx import-linter lint
    - uv run pytest supekku/scripts/lib/policies/registry_test.py -v
    - uv run pytest supekku/scripts/lib/standards/registry_test.py -v
    - uv run pytest spec_driver/domain/relations/ -v
    - uv run spec-driver validate
  evidence:
    - import-linter output for both contracts
    - pytest output for relations and affected registries
    - updated DE/DR/IP/phase notes showing debt retirement criteria
tasks:
  - Define the orchestration entrypoint that collects backlink source data
  - Refactor registry backlink methods to consume pre-collected sources only
  - Re-home workspace graph collection under orchestration or document the explicit seam
  - Document shim retirement criteria for legacy relations re-export modules
  - Document legacy-core import retirement criteria for migrated domain modules
risks:
  - Orchestration entrypoint choice may overlap with DE-124 facade work
  - Registry tests may assume internal collection responsibilities that now move outward
  - Shim retirement may reveal hidden legacy consumers not covered by pilot tests
```

# Phase 4 — Orchestration ownership and shim retirement

## 1. Objective

Resolve the main architectural gap exposed by Phase 3: relation helpers are now
pure, but registries still collect cross-registry source data themselves. This
phase moves that composition responsibility into orchestration, then turns the
remaining shims and legacy-core imports into explicit closure criteria instead
of vague future cleanup.

## 2. Links & References

- **Delta**: [DE-125](../DE-125.md)
- **Design Revision**: [DR-125](../DR-125.md) §3.3, §3.4, §3.5, §5.2
- **Implementation Plan**: [IP-125](../IP-125.md)
- **Prior Phase**: [phase-03.md](./phase-03.md)
- **Research Notes**: [notes.md](../notes.md)

## 3. Entrance Criteria

- [x] Phase 3 completed with relations pilots and backlink helper extraction
- [x] Post-pilot architectural verdict recorded in `notes.md`
- [x] Domain Internal Layers contract passing in import-linter

## 4. Exit Criteria / Done When

- [x] `Workspace.sync_policies()` and `Workspace.sync_standards()` collect sibling records and pass them as `decision_sources` / `policy_sources`
- [x] Registry backlink methods treat `None` as "skip backlink population" — no fallback to sibling instantiation
- [x] Workspace graph collection has an explicit orchestration home or a tracked owning seam (documented; move is a separate patch)
- [x] Shim retirement criteria are documented for legacy relations re-export modules
- [x] Legacy-core import retirement criteria are documented for migrated domain modules

## 5. Verification

- `uvx import-linter lint`
- `uv run pytest supekku/scripts/lib/policies/registry_test.py -v`
- `uv run pytest supekku/scripts/lib/standards/registry_test.py -v`
- `uv run pytest spec_driver/domain/relations/ -v`
- `uv run spec-driver validate`

## 6. Assumptions & STOP Conditions

- **Assumption**: the backlink source-collection boundary can move without
  changing user-facing CLI behaviour.
- **Assumption**: DE-124 can continue consuming orchestration surfaces while
  this delta sharpens internal ownership.
- **STOP**: if the orchestration entrypoint choice would force a public facade
  redesign owned by DE-124, coordinate and narrow the seam before proceeding.
- **STOP**: if hidden consumers require the shims for non-trivial behaviour,
  document the dependency and defer removal rather than expanding shim logic.

## 7. Tasks & Progress

| Status | ID  | Description                                                       | Notes |
| ------ | --- | ----------------------------------------------------------------- | ----- |
| [x]    | 4.1 | Define the orchestration entrypoint for backlink source collection | Option A: Workspace passes source records down. See §10 mini-DR |
| [x]    | 4.2 | Refactor registry backlink methods to accept pre-collected sources | Done — lazy sibling imports eliminated. `01b4cf2c` |
| [x]    | 4.3 | Re-home workspace graph collection or record the owning seam       | Seam documented: target is `spec_driver/orchestration/graph.py`. Move is a separate patch. |
| [x]    | 4.4 | Document shim retirement criteria                                  | 4 shims inventoried with consumer counts and retirement sequence. See §10. |
| [x]    | 4.5 | Document legacy-core import retirement criteria                    | 3 legacy-core imports documented. Prerequisite: core migration (separate delta). See §10. |

### Task Details

- **4.1 Orchestration entrypoint**
  - Decide which orchestration surface collects policy/standard/decision sources
    before calling `spec_driver.domain.relations.backlinks`.
  - Keep registries as local authorities rather than workflow coordinators.

- **4.2 Registry refactor**
  - Orchestration entrypoints: `Workspace.sync_policies()` and
    `Workspace.sync_standards()` collect sibling records and pass them down.
  - `PolicyRegistry.sync(*, decision_sources=None)` and
    `StandardsRegistry.sync(*, decision_sources=None, policy_sources=None)`
    accept optional pre-collected source dicts.
  - `_build_backlinks` becomes a pure function of its inputs — no lazy imports.
  - Semantic rule: `None` means "skip backlink population", not "fall back to
    sibling registry collection". Registries must never instantiate siblings.
  - Remove lazy sibling-registry imports from both registries.

- **4.3 Graph collection ownership**
  - Revisit the Phase 3 `graph.py` split.
  - Either move workspace-wide artifact collection under orchestration or make
    the remaining seam explicit so later migration does not guess.
  - **Scope**: document the owning seam and target location in this phase; the
    actual move is a separate patch (or follow-on phase) since graph collection
    touches more registries than backlinks and needs its own verification.

- **4.4–4.5 Debt retirement**
  - Record the conditions under which shims can be deleted.
  - Record the conditions under which migrated domain modules can stop importing
    `supekku.scripts.lib.core.*`.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| ---- | ---------- | ------ |
| Orchestration boundary overlaps DE-124 work | Keep the change internal and coordinate on facade ownership only if needed | open |
| Registry tests encode old ownership assumptions | Refactor tests with the ownership move rather than preserving misleading patterns | open |
| Shims linger indefinitely | Define deletion criteria in this phase rather than after broader migration | open |

## 9. Decisions & Outcomes

- `2026-03-24` — Phase 4 opened because the pilot proved the helper extraction
  pattern but left the composition boundary unresolved.
- `2026-03-24` — **Task 4.1 decision: Option A.** `Workspace.sync_policies()` and
  `Workspace.sync_standards()` pass `decision_sources` / `policy_sources` to
  registry sync methods. `None` means skip backlink population, never fallback.
  Rationale: Workspace already orchestrates sync order; this makes the data
  dependency explicit with minimal new abstraction. See §10 mini-DR.

## 10. Findings / Research Notes

- Phase 3 showed that the unresolved design question is ownership of
  cross-registry source collection, not whether pure relation helpers work.
- Re-export shims and legacy-core imports are now treated as explicit migration
  debt with required retirement criteria.

### 4.1 Mini-DR: Orchestration entrypoint for backlink source collection

#### Current state

Call chain today:

```
Workspace.sync_policies()
  → PolicyRegistry.sync()
    → PolicyRegistry.write()
      → PolicyRegistry._build_backlinks(policies)
        → lazy import DecisionRegistry          ← lateral coupling
        → DecisionRegistry(root).collect()      ← sibling instantiation
        → build_backlinks(policies, ...)        ← generic helper (Phase 3)
```

`StandardsRegistry` is identical but worse — two sibling imports
(DecisionRegistry + PolicyRegistry).

The problem: registries are local authorities (DR-125 §3.3) but they
instantiate sibling registries to collect cross-registry source data. The
computation is now generic (Phase 3), but the collection responsibility is
misplaced.

#### Design options

**Option A: Workspace.sync_policies/standards passes sources down.**

```python
# Workspace
def sync_policies(self) -> None:
    decisions = self.decisions.collect()
    self.policies.sync(decision_sources=decisions)

def sync_standards(self) -> None:
    decisions = self.decisions.collect()
    policies = self.policies.collect()
    self.standards.sync(
        decision_sources=decisions,
        policy_sources=policies,
    )
```

Registry `sync()` / `write()` accepts pre-collected source dicts instead of
instantiating siblings. `_build_backlinks` becomes a pure function of its inputs.
`None` means "skip backlink population" — registries must never fall back to
sibling instantiation.

- **Pro**: minimal change, Workspace already knows the sync order, registries
  become truly local.
- **Pro**: `sync_all_registries()` already syncs decisions before policies before
  standards — the ordering is correct for dependency injection.
- **Con**: `PolicyRegistry.sync()` gains a parameter, so direct callers outside
  Workspace (CLI commands that instantiate a registry directly) must either
  pass sources or accept no backlinks.
- **Con**: incremental — doesn't establish a general orchestration pattern beyond
  backlinks.

**Option B: Dedicated sync orchestration service.**

A new `spec_driver.orchestration.sync` module that composes registries:

```python
def sync_governance(workspace: Workspace) -> None:
    decisions = workspace.decisions.collect()
    policies = workspace.policies.collect()
    workspace.policies.write_with_backlinks(
        build_backlinks(..., decisions)
    )
    workspace.standards.write_with_backlinks(
        build_backlinks_multi(..., decisions, policies)
    )
```

- **Pro**: clean separation, registries stay entirely local.
- **Pro**: generalises to future cross-registry concerns.
- **Con**: new module, new abstraction, more moving parts for a problem
  currently scoped to two registries.
- **Con**: Workspace already does this job — adding a parallel orchestrator
  creates ownership ambiguity.

**Option C: Workspace composes, registries accept a backlink builder callback.**

```python
# Registry
def sync(self, backlink_fn: Callable | None = None) -> None:
    records = self.collect()
    if backlink_fn:
        backlink_fn(records)
    self.write_records(records)
```

- **Pro**: registries are agnostic about backlink sources.
- **Con**: callback indirection obscures what's happening.
- **Con**: over-generalised for a two-registry problem.

#### Recommendation: Option A

**Workspace.sync_policies/sync_standards passes pre-collected source records.**

Rationale:

1. **Workspace already orchestrates sync order.** `sync_all_registries()` syncs
   decisions → policies → standards → requirements. The dependency graph is
   already encoded there. Making it pass data forward is the minimal expression
   of orchestration ownership.

2. **Registries stay local.** `_build_backlinks` receives source data as
   arguments instead of instantiating siblings. The lazy import hack disappears.

3. **Scope matches the problem.** This is a two-registry issue today. A
   dedicated orchestration service (Option B) would be premature until more
   cross-registry concerns emerge.

4. **Backward compatibility is manageable.** CLI callers that construct a
   `PolicyRegistry` directly and call `sync()` get no backlinks — which is
   already the behaviour when the decisions directory doesn't exist. Make
   the parameter optional with a default of `None` (no backlinks).

#### Interface sketch

Canonical parameter name: `decision_sources` / `policy_sources` (matches the
backlinks API which consumes source iterables).

```python
# PolicyRegistry
def _build_backlinks(
    self,
    policies: dict[str, PolicyRecord],
    decision_sources: dict[str, DecisionRecord] | None = None,
) -> None:
    if decision_sources is None:
        return  # None = skip, not fallback
    build_backlinks(
        policies,
        ((d.id, d.policies) for d in decision_sources.values()),
        "decisions",
    )

def write(self, path=None, *, decision_sources=None) -> None:
    policies = self.collect()
    self._build_backlinks(policies, decision_sources)
    ...

def sync(self, *, decision_sources=None) -> None:
    self.write(decision_sources=decision_sources)

# Workspace
def sync_policies(self) -> None:
    self.policies.sync(decision_sources=self.decisions.collect())
```

`StandardsRegistry` is analogous but accepts both `decision_sources` and
`policy_sources`.

#### Impact on graph collection (task 4.3)

The same pattern applies to `build_reference_graph()` in legacy `graph.py`.
`_collect_all_artifacts()` instantiates `BacklogRegistry`, `MemoryRegistry`,
`DriftLedgerRegistry`. Under Option A, `Workspace` would pass collected
artifacts to the graph builder rather than having the graph builder reach into
registries. This can be deferred — `build_reference_graph_from_artifacts()`
already accepts pre-collected triples; the remaining orchestration glue
(`build_reference_graph(workspace)`) just needs its caller to pre-collect
instead.

#### Risks

- CLI commands that call `registry.sync()` without Workspace will get no
  backlinks. This is acceptable — direct registry use is a power-user path,
  and the fallback (empty backlinks) is already the behaviour when sibling
  registries are absent.
- `sync_all_registries()` ordering becomes load-bearing for correctness. It
  already is in practice, but the data dependency makes it explicit.

#### Decision

Proceed with **Option A** for task 4.2 implementation.

### 4.3 Graph collection owning seam

#### Current state

Legacy `supekku/scripts/lib/relations/graph.py` retains four functions after the
Phase 3 split:

| Function | Responsibility | Layer |
|----------|---------------|-------|
| `build_reference_graph(workspace)` | Entry point — delegates to collectors | orchestration |
| `_collect_all_artifacts(workspace)` | Composes workspace + standalone registries | orchestration |
| `_collect_workspace_artifacts(workspace, out)` | Walks Workspace properties | orchestration |
| `_collect_standalone_registry_artifacts(root, out)` | Instantiates Backlog/Memory/Drift registries | orchestration |

Two callers: `supekku/scripts/lib/validation/validator.py` and `supekku/cli/show.py`.
Both pass a `Workspace` instance.

#### Target location

`spec_driver/orchestration/graph.py` — workspace-dependent artifact collection
belongs in orchestration because it composes multiple registries and the
Workspace facade to produce a complete artifact set.

The pure graph model (`GraphEdge`, `ReferenceGraph`,
`build_reference_graph_from_artifacts`, query functions) already lives in
`spec_driver/domain/relations/graph.py`.

#### Scope

**This phase**: document the seam and target. **Separate patch**: execute the
move once orchestration has a clearer module structure (or as part of the next
migration wave). The move is mechanical — the function signatures are already
clean and the pure core is already extracted.

### 4.4 Shim retirement criteria

#### Shim inventory

| Shim file | Re-exports from | Consumer count |
|-----------|----------------|---------------|
| `supekku/scripts/lib/relations/__init__.py` | `spec_driver.domain.relations.query` | 0 (no direct `__init__` consumers found) |
| `supekku/scripts/lib/relations/query.py` | `spec_driver.domain.relations.query` | 10 sites (CLI, TUI, formatters, list commands) |
| `supekku/scripts/lib/relations/manager.py` | `spec_driver.domain.relations.manager` | 2 sites (`requirements/sync.py`, `changes/artifacts.py`) |
| `supekku/scripts/lib/relations/graph.py` | `spec_driver.domain.relations.graph` + workspace collection | 2 sites (`validator.py`, `cli/show.py`) |

#### Retirement conditions

A shim can be deleted when:

1. **All consumers import from the canonical location** (`spec_driver.domain.relations.*`).
2. **No test imports the shim path** — grep confirms zero references to the
   legacy import path.
3. **`import-linter lint` passes** after deletion.
4. **Full test suite passes** after deletion.

#### Retirement sequence

1. **`__init__.py`** — can be retired first (no direct consumers beyond the
   shim modules themselves).
2. **`manager.py`** — only 2 consumers, both in `scripts/lib/` domain code that
   will eventually migrate.
3. **`query.py`** — 10 consumers across CLI, TUI, and formatters. Retire after
   those layers are updated or migrated.
4. **`graph.py`** — last, because it contains workspace collection functions
   (task 4.3) that must move to orchestration first.

#### Policy

- Shims must not gain new logic. They are forwarding-only.
- New code must import from `spec_driver.domain.relations.*`, never from shims.
- Each shim file's docstring already states the canonical location.

### 4.5 Legacy-core import retirement criteria

#### Current legacy-core imports in domain modules

| Domain module | Legacy import | Needed from core |
|--------------|--------------|-----------------|
| `spec_driver/domain/relations/manager.py` | `supekku.scripts.lib.core.frontmatter_schema.Relation` | Pydantic model |
| `spec_driver/domain/relations/manager.py` | `supekku.scripts.lib.core.spec_utils.{dump,load}_markdown_file` | File I/O helpers |
| `spec_driver/domain/relations/graph.py` | `supekku.scripts.lib.core.artifact_ids.normalize_artifact_id` | ID normalisation |

#### Retirement conditions

A legacy-core import can be replaced when:

1. **The core module is available at `spec_driver.core.*`** — either moved or
   re-exported.
2. **The domain module's import is updated** to the new path.
3. **`import-linter lint` passes** — confirms the layering is correct.
4. **Tests pass** for the affected module.

#### Prerequisite

Core migration (moving `frontmatter_schema`, `spec_utils`, `artifact_ids` to
`spec_driver.core`) is a prerequisite. This is a separate delta — these are
shared infrastructure modules used across the entire codebase, not just by
domain/relations.

#### Policy

- Domain modules may import from legacy core paths until core migrates.
- This is tolerable because core is architecturally below domain — the
  dependency direction is correct even though the package path is legacy.
- New domain modules should prefer `spec_driver.core.*` when available.

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
