---
id: IP-125-P04
slug: "125-enforce_explicit_module_boundaries_and_coupling_constraints-phase-04"
name: "Orchestration ownership and shim retirement"
created: "2026-03-24"
updated: "2026-03-24"
status: draft
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
  - An orchestration entrypoint owns backlink source collection across registries
  - Registries no longer instantiate sibling registries to collect backlink sources
  - Workspace graph collection has an explicit orchestration home or tracked owning seam
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

- [ ] An orchestration entrypoint owns backlink source collection across registries
- [ ] Registry backlink methods consume pre-collected sources and stop instantiating sibling registries
- [ ] Workspace graph collection has an explicit orchestration home or a tracked owning seam
- [ ] Shim retirement criteria are documented for legacy relations re-export modules
- [ ] Legacy-core import retirement criteria are documented for migrated domain modules

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
| [ ]    | 4.2 | Refactor registry backlink methods to accept pre-collected sources | Remove sibling-registry instantiation from registries |
| [ ]    | 4.3 | Re-home workspace graph collection or record the owning seam       | Finish the split started in Phase 3 |
| [ ]    | 4.4 | Document shim retirement criteria                                  | Legacy `supekku/scripts/lib/relations/*` re-exports |
| [ ]    | 4.5 | Document legacy-core import retirement criteria                    | `manager.py` and any other migrated domain modules |

### Task Details

- **4.1 Orchestration entrypoint**
  - Decide which orchestration surface collects policy/standard/decision sources
    before calling `spec_driver.domain.relations.backlinks`.
  - Keep registries as local authorities rather than workflow coordinators.

- **4.2 Registry refactor**
  - Change registry helper methods so they operate on supplied source records.
  - Remove lazy sibling-registry imports from steady-state backlink flows.

- **4.3 Graph collection ownership**
  - Revisit the Phase 3 `graph.py` split.
  - Either move workspace-wide artifact collection under orchestration or make
    the remaining seam explicit so later migration does not guess.

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
- `2026-03-24` — **Task 4.1 decision: Option A.** Workspace passes pre-collected
  source records to registry sync methods. Registries accept optional source data
  and stop instantiating sibling registries. Rationale: Workspace already
  orchestrates sync order; this makes the data dependency explicit with minimal
  new abstraction. See §10 mini-DR for full analysis.

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

Registry `sync()` / `write()` accepts pre-collected source records instead of
instantiating siblings. `_build_backlinks` becomes a pure function of its inputs.

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

```python
# PolicyRegistry
def _build_backlinks(
    self,
    policies: dict[str, PolicyRecord],
    decision_records: dict[str, Any] | None = None,
) -> None:
    if decision_records is None:
        return
    build_backlinks(
        policies,
        ((d.id, d.policies) for d in decision_records.values()),
        "decisions",
    )

def write(self, path=None, *, decision_records=None) -> None:
    policies = self.collect()
    self._build_backlinks(policies, decision_records)
    ...

def sync(self, *, decision_records=None) -> None:
    self.write(decision_records=decision_records)

# Workspace
def sync_policies(self) -> None:
    self.policies.sync(decision_records=self.decisions.collect())
```

`StandardsRegistry` is analogous but accepts both `decision_records` and
`policy_records`.

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

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
