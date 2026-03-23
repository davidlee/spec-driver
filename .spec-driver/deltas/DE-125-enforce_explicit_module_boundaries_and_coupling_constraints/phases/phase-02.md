---
id: IP-125-P02
slug: "125-enforce_explicit_module_boundaries_and_coupling_constraints-phase-02"
name: Verification and seam extraction
created: "2026-03-23"
updated: "2026-03-24"
status: completed
kind: phase
plan: IP-125
delta: DE-125
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-125-P02
plan: IP-125
delta: DE-125
objective: >-
  Draft the enforcement additions and extract the first sanctioned seams so the
  initial code-moving work can start with low-coupling relations helpers instead
  of jumping directly into high-coupling registries.
entrance_criteria:
  - Phase 1 completed with named pilot targets
  - Domain internal ordering defined in DR-125
  - Existing import-linter command confirmed (just lint-imports)
exit_criteria:
  - Domain Internal Layers contract drafted in pyproject.toml
  - First pilot move set is confirmed as relations-first
  - Policy backlink seam is specified outside PolicyRegistry
  - Targeted verification commands are attached to each seam
verification:
  tests:
    - relations.query tests
    - relations.manager tests
    - policy registry tests when backlink seam changes
  evidence:
    - just lint-imports output
    - targeted pytest output for selected seam work
tasks:
  - Draft Domain Internal Layers import-linter contract
  - Specify file-level target locations for relations pilots
  - Define the policy backlink seam outside PolicyRegistry
  - Confirm which requirements-registry responsibilities are deferred
risks:
  - Seams may still hide upward or sibling dependencies
  - Premature registry moves could collapse the intended ordering
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-125-P02
files:
  references:
    - pyproject.toml
    - .spec-driver/deltas/DE-125-enforce_explicit_module_boundaries_and_coupling_constraints/DR-125.md
    - .spec-driver/deltas/DE-125-enforce_explicit_module_boundaries_and_coupling_constraints/IP-125.md
  context:
    - supekku/scripts/lib/relations/query.py
    - supekku/scripts/lib/relations/manager.py
    - supekku/scripts/lib/policies/registry.py
    - supekku/scripts/lib/requirements/registry.py
entrance_criteria:
  - item: "Phase 1 completed with named pilot targets"
    completed: true
  - item: "Domain internal ordering defined in DR-125"
    completed: true
  - item: "Existing import-linter command confirmed (just lint-imports)"
    completed: true
exit_criteria:
  - item: "Domain Internal Layers contract drafted in pyproject.toml"
    completed: true
  - item: "First pilot move set is confirmed as relations-first"
    completed: true
  - item: "Policy backlink seam is specified outside PolicyRegistry"
    completed: true
  - item: "Targeted verification commands are attached to each seam"
    completed: true
tasks:
  - id: "1"
    description: "Draft Domain Internal Layers import-linter contract"
    status: completed
  - id: "2"
    description: "Specify file-level target locations for relations pilots"
    status: completed
  - id: "3"
    description: "Define the policy backlink seam outside PolicyRegistry"
    status: completed
  - id: "4"
    description: "Confirm which requirements-registry responsibilities are deferred"
    status: completed
```

# Phase 2 - Verification and seam extraction

## 1. Objective

Draft the enforceable contract additions and specify the first migration seams so
Phase 3 can move code without smuggling the old lateral-coupling pattern into
`spec_driver.domain`.

## 2. Links & References

- **Delta**: [DE-125](../DE-125.md)
- **Design Revision**: [DR-125](../DR-125.md) §3-7
- **Current contracts**: `/workspace/spec-driver/pyproject.toml`
- **Pilot modules**:
  - `supekku/scripts/lib/relations/query.py`
  - `supekku/scripts/lib/relations/manager.py`
- **Deferred high-coupling modules**:
  - `supekku/scripts/lib/requirements/registry.py`
  - `supekku/scripts/lib/policies/registry.py`
  - `supekku/scripts/lib/validation/validator.py`

## 3. Entrance Criteria

- [x] Phase 1 completed with named pilot targets
- [x] Domain-internal ordering recorded in DR-125
- [x] Existing import-linter command confirmed (`just lint-imports`)

## 4. Exit Criteria / Done When

- [x] `pyproject.toml` has a draft `Domain Internal Layers` contract ready to land
- [x] Relations-first pilot move set is confirmed with target paths under `spec_driver/domain/relations/`
- [x] Policy backlink logic has an agreed extraction seam outside `PolicyRegistry`
- [x] Requirements-registry and validator work are explicitly deferred until those seams exist

## 5. Verification

- Contract check: `just lint-imports`
- Current pilot tests:
  `uv run pytest supekku/scripts/lib/relations/query_test.py supekku/scripts/lib/relations/manager_test.py -v`
- Governance seam tests when backlink extraction starts:
  `uv run pytest supekku/scripts/lib/policies/registry_test.py -v`
- Deferred requirements seam tests:
  `uv run pytest supekku/scripts/lib/requirements/registry_test.py -v`
- Structured-doc validation: `spec-driver validate`

## 6. Assumptions & STOP Conditions

- **Assumption**: `relations.query` and `relations.manager` are the lowest-coupling
  movable units because they do not depend on sibling registries for their core behaviour.
- **Assumption**: policy backlinks can be represented as a relation/query seam
  rather than remaining embedded in `PolicyRegistry`.
- **STOP**: If `relations.manager` is shown to be generic frontmatter mutation
  infrastructure rather than domain relations logic, stop and reclassify it to
  `core` before moving it.
- **STOP**: If drafting the internal layer contract reveals that `requirements.sync`
  belongs in orchestration, revise DR-125 before Phase 3.

## 7. Tasks & Progress

| Status | ID  | Description                                                   | Parallel? | Notes                                                          |
| ------ | --- | ------------------------------------------------------------- | --------- | -------------------------------------------------------------- |
| [x]    | 2.1 | Draft `Domain Internal Layers` contract in `pyproject.toml`   | —         | Contract added, `import-linter lint` passes (2 kept, 0 broken) |
| [x]    | 2.2 | Specify exact target paths for relations pilots               | —         | See §10 findings. All three relations modules confirmed clean  |
| [x]    | 2.3 | Define policy backlink seam outside `PolicyRegistry`          | —         | Generic `build_backlinks()` in `domain/relations/backlinks.py` |
| [x]    | 2.4 | Record deferred scope for requirements registry and validator | —         | See §10 findings — 6 sibling-registry imports in requirements  |
| [x]    | 2.5 | Prepare Phase 3 sheet once 2.1-2.4 are stable                 | —         | IP-125-P03 created: relations move + backlink extraction       |

### Task Details

- **2.1 Draft `Domain Internal Layers` contract**
  - **Design / Approach**: add a second `import-linter` layers contract for
    `validation -> relations -> registries -> records -> lifecycle`.
  - **Files / Components**: `pyproject.toml`
  - **Testing**: `just lint-imports`

- **2.2 Specify exact target paths for relations pilots**
  - **Design / Approach**: move the pure reference-discovery helper first, then
    the frontmatter relation manager if it remains domain-classified.
  - **Files / Components**: `supekku/scripts/lib/relations/query.py`,
    `supekku/scripts/lib/relations/manager.py`, future `spec_driver/domain/relations/*`
  - **Testing**:
    `uv run pytest supekku/scripts/lib/relations/query_test.py supekku/scripts/lib/relations/manager_test.py -v`

- **2.3 Define policy backlink seam outside `PolicyRegistry`**
  - **Design / Approach**: extract backlink construction into a relation/query
    helper so governance registries stop reaching directly into one another.
  - **Files / Components**: `supekku/scripts/lib/policies/registry.py`,
    `supekku/scripts/lib/decisions/registry.py`, candidate `spec_driver/domain/relations/backlinks.py`
  - **Testing**: `uv run pytest supekku/scripts/lib/policies/registry_test.py -v`

- **2.4 Record deferred scope for requirements registry and validator**
  - **Design / Approach**: explicitly defer high-coupling modules until relation
    seams exist and orchestration/domain boundaries are clearer.
  - **Files / Components**: DE/IP/phase docs, `requirements/registry.py`,
    `validation/validator.py`
  - **Testing**: doc validation plus targeted requirements tests only when that
    seam begins

- **2.5 Prepare Phase 3 sheet**
  - **Design / Approach**: only after contracts and seams are stable enough to
    support actual file moves.

## 8. Risks & Mitigations

| Risk                                                                       | Mitigation                                                        | Status |
| -------------------------------------------------------------------------- | ----------------------------------------------------------------- | ------ |
| `relations.manager` is really shared infrastructure                        | Reclassify to `core` before moving                                | open   |
| Governance backlink extraction still leaves sibling registry reach-through | Make backlinks a dedicated relation/query seam                    | open   |
| Requirements sync still acts as an integration hub                         | Defer registry move until relation/orchestration split is clearer | open   |

## 9. Decisions & Outcomes

- `2026-03-23` - First migration pilots are `relations.query` and `relations.manager` because they have the lowest observed sibling-registry coupling.
- `2026-03-23` - `PolicyRegistry` is not a first pilot; backlink extraction is the first governance seam to resolve before moving that registry.

## 10. Findings / Research Notes

### 2.1 — Domain Internal Layers contract

Added to `pyproject.toml` as a second `import-linter` contract. The ordered layers
match DR-125 §3.2:

```
validation > relations > registries > records > lifecycle
```

Package stubs (`__init__.py`) created under `spec_driver/domain/` for all five
sub-areas so the contract is immediately enforceable.

`uvx import-linter lint` → 2 kept, 0 broken.

### 2.2 — Relations pilot import analysis

All three relations modules depend only downward:

| Module        | External imports                                    |
| ------------- | --------------------------------------------------- |
| `query.py`    | **none** — pure stdlib (protocols + dataclasses)    |
| `manager.py`  | `core.frontmatter_schema.Relation`, `core.spec_utils` |
| `graph.py`    | `core.artifact_ids`, `relations.query`              |

No sibling-registry imports. These are the cleanest pilot targets for the first
move into `spec_driver/domain/relations/`.

Confirmed consumers outside relations:
- `validation/validator.py` → `relations.graph` (lazy import)
- `requirements/sync.py` → `relations.manager.list_relations`
- `changes/artifacts.py` → `relations.manager.list_relations`
- `formatters/*` → `relations.query` types

All consumers import via fully-qualified paths, so re-export shims in the legacy
location will suffice during migration.

### 2.3 — Backlink seam specification

**Current pattern**: Both `PolicyRegistry._build_backlinks()` and
`StandardsRegistry._build_backlinks()` lazy-import sibling registries
(`DecisionRegistry`, `PolicyRegistry`) to walk forward references and compute
reverse maps. This is the exact lateral coupling DR-125 §5.2 identifies.

**Extraction target**: `spec_driver/domain/relations/backlinks.py`

**Proposed generic function**:

```python
def build_backlinks(
    targets: dict[str, T],
    sources: Iterable[tuple[str, Iterable[str]]],
    category: str,
    clear: bool = True,
) -> None:
```

Where `targets` are the records receiving backlinks, `sources` yield
`(source_id, referenced_target_ids)` pairs, and `category` is the backlink
bucket name (e.g. `"decisions"`, `"policies"`).

Each registry's `sync()` method would call this function instead of
instantiating sibling registries directly. The **caller** (orchestration or sync
command) is responsible for collecting source records and passing them in.

This moves the cross-registry traversal into `domain.relations` and removes the
lazy-import hack from both registries.

### 2.4 — Deferred scope: requirements and validator

**Requirements** (`requirements/registry.py`, `requirements/sync.py`,
`requirements/parser.py`): 6 sibling-registry imports across the package
(BacklogRegistry ×2, SpecRegistry ×4). The registry itself acts as a
cross-artifact integration hub. Not a safe first-wave target.

**Validator** (`validation/validator.py`): imports `relations.graph` (lazy).
Architecturally it's a top consumer that coordinates across multiple areas.
DR-125 places it at the top of the domain-internal order, which is correct, but
moving it requires the lower seams to exist first.

**Deferred until**: relations and backlink seams are landed and verified.

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
