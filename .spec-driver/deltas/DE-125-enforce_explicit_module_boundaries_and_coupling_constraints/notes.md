# Notes for DE-125

## 2026-03-23

- Reconciled `DE-125`, `DR-125`, and `IP-125` with current repo reality.
- Replaced the stale "create `spec_driver/` and add import-linter" narrative with
  the narrower thesis that actually matters now: domain-internal dependency
  direction.
- Added `phases/phase-01.md` so the delta has a real active phase instead of an
  orphan plan entry.
- Identified the main architectural seam: registries should be local authorities,
  while cross-artifact traversal belongs in `relations` or orchestration.
- Chose first migration pilots from the current graph:
  `supekku/scripts/lib/relations/query.py` and
  `supekku/scripts/lib/relations/manager.py`.
- Chose the first governance seam to extract before any registry move:
  policy backlink computation currently embedded in `PolicyRegistry`.
- Explicitly deferred `requirements.registry`, `policies.registry`, and
  `validation.validator` as too coupled for first-wave migration.
- Created `phases/phase-02.md` for verification and seam extraction.
- Ran `spec-driver validate` after the doc updates. Current output is back to the
  repo's pre-existing warning baseline; no new DE-125-specific validation issues
  remain.
- Work remains uncommitted.

## 2026-03-24 — Phase 2 execution

- **Task 2.1**: Added `Domain Internal Layers` contract to `pyproject.toml`.
  Created package stubs for all five domain sub-areas (`lifecycle`, `records`,
  `registries`, `relations`, `validation`). `uvx import-linter lint` → 2 kept,
  0 broken.
- **Task 2.2**: Confirmed all three relations modules (`query.py`, `manager.py`,
  `graph.py`) have clean dependency profiles — only stdlib or `core.*` imports,
  no sibling-registry coupling. Identified consumers that will need re-export
  shims: `validation/validator.py`, `requirements/sync.py`, `changes/artifacts.py`,
  `formatters/*`.
- **Task 2.3**: Specified backlink seam: generic `build_backlinks()` function in
  `spec_driver/domain/relations/backlinks.py`. Both `PolicyRegistry` and
  `StandardsRegistry` exhibit the same pattern of lazy-importing sibling
  registries for backlink computation. The generic helper accepts pre-collected
  source data, eliminating the cross-registry import entirely.
- **Task 2.4**: Requirements confirmed too coupled (6 sibling-registry imports
  across registry, sync, parser). Validator is a top consumer. Both deferred
  until relations and backlink seams are landed.
- **Task 2.5**: Created Phase 3 sheet (IP-125-P03) for the actual code-moving
  and backlink extraction work.

## 2026-03-24 — Phase 3 execution

- Moved `query.py` (pure, no changes), `manager.py` (keeps legacy core imports),
  and `graph.py` (split: pure graph model moved, workspace collection stays) to
  `spec_driver/domain/relations/`.
- Created re-export shims in `supekku/scripts/lib/relations/` — all consumers
  unaffected.
- Implemented `build_backlinks()` and `build_backlinks_multi()` in
  `spec_driver/domain/relations/backlinks.py` with 11 tests.
- Refactored `PolicyRegistry._build_backlinks` to use `build_backlinks()`.
- Refactored `StandardsRegistry._build_backlinks` to use `build_backlinks_multi()`.
- Key decision: `graph.py` split because workspace artifact collection is
  orchestration-level, not domain relations. The pure graph model and query
  functions moved; `build_reference_graph(workspace)` stays in legacy.
- Registries still lazy-import sibling registries for data collection — the
  backlink *computation* is generic but *source collection* remains a registry
  concern until orchestration owns sync.
- 4656 tests passed, 2 import-linter contracts kept, ruff clean.

## 2026-03-24 — Architectural verdict (post-Phase 3)

### What proved out

- **Domain Internal Layers contract** is the most durable outcome. Machine-enforced
  in CI, catches wrong-direction imports immediately.
- **`query.py`** is the ideal domain module: pure stdlib, protocol-based, moved
  verbatim. Validates that the layer model works when code is genuinely decoupled.
- **`build_backlinks()`** is a real design improvement. Duplicated 30-line methods
  replaced by 3-line calls to a generic, testable helper.

### What's uncomfortable

- **Registries still lazy-import sibling registries for data collection.**
  `PolicyRegistry._build_backlinks` still does
  `from supekku.scripts.lib.decisions.registry import DecisionRegistry`. We
  extracted computation but not collection. The lateral coupling is narrower but
  present.
- **Domain imports legacy core.** `manager.py` and `graph.py` import from
  `supekku.scripts.lib.core.*`. The contract says domain is above core, but the
  actual import path goes upward into the legacy tree. Resolves when core migrates,
  but architecturally backwards until then.
- **`graph.py` had to be split** — unplanned. Workspace artifact collection is
  orchestration glue, not domain. The split was correct but revealed the module
  was doing two jobs.
- **Re-export shims are debt.** 77 lines of forwarding code that must eventually
  be removed, not maintained.

### Open questions

1. **Who owns backlink data collection?** Registries currently collect source
   data from sibling registries, then pass it to the generic helper. Should
   `sync()` stay on registries, or should orchestration compose registries and
   pass cross-registry data down? This is the boundary question that blocks
   further registry migration.
2. **When does core migrate?** Domain modules importing legacy core paths is
   tolerable but architecturally backwards. Core migration would make the
   contract honest.
3. **Should graph workspace collection move to orchestration now?** The 126-line
   legacy `graph.py` is orchestration glue with no clear home.

### Follow-up actions

- The delta has completed its planned phases (P01–P03). Decide whether to close
  it here or extend with phases for the orchestration boundary question.
- Consider scoping the core migration as a separate delta — it's prerequisite
  infrastructure, not domain-specific.
- Re-export shims should be tracked for eventual removal (flag-day or gradual
  consumer migration).

### Commits

- `1a0d467b` — Phase 2: contract + seam specification
- `7ca724c3` — Phase 3: relations move + backlink extraction
- `ac2ff223` — Phase 3 docs complete
- All `.spec-driver` changes committed promptly alongside code per doctrine.

## 2026-03-24 — Phase 4 execution

- **Task 4.1** (mini-DR): Option A selected — Workspace passes pre-collected
  sources down. See phase-04.md §10 for full analysis.
- **Task 4.2**: Refactored `PolicyRegistry` and `StandardsRegistry` to accept
  `decision_sources` / `policy_sources` kwargs. `None` means skip, never
  fallback. `Workspace.sync_policies()` and `Workspace.sync_standards()` now
  collect sibling records and pass them down. Lazy sibling-registry imports
  eliminated from both registries.
- **Task 4.3**: Graph collection seam documented. Target:
  `spec_driver/orchestration/graph.py`. Two callers (`validator.py`,
  `cli/show.py`). Move is a separate mechanical patch.
- **Task 4.4**: 4 re-export shims inventoried with consumer counts (0, 10, 2, 2).
  Retirement sequence defined: `__init__` → `manager` → `query` → `graph`.
  Policy: shims must not gain new logic; new code imports canonical paths only.
- **Task 4.5**: 3 legacy-core imports documented (`Relation`, `spec_utils`,
  `artifact_ids`). Prerequisite is core migration — a separate delta since those
  modules are shared infrastructure.
- 4656 tests passed, 2 import-linter contracts kept, ruff clean.

### Commits

- `f2f5fcde` — Task 4.1 mini-DR
- `8cf45921` — Phase 4 consistency tightening
- `01b4cf2c` — Task 4.2 registry refactor

## 2026-03-24 — Post-Phase 4 architectural reflection

### Scale of remaining work

- 203 non-test modules in `supekku/scripts/lib/`, 10 in `spec_driver/domain/`.
- Moving modules one-by-one is not viable at this ratio. Next deltas should
  target moves that unlock disproportionate value.

### Highest-leverage next moves (ranked)

1. **Audit `core/` for misplaced modules.**
   - `core/artifact_view.py` imports 11 registries — it's an integration hub,
     not core infrastructure.
   - `core/enums.py` imports from `backlog`, `blocks`, `changes`, `decisions`,
     `drift` — also not core.
   - Together they account for 38 cross-area imports from `core/`. Until these
     are reclassified, `spec_driver.core` (bottom of the outer layer contract)
     can't migrate honestly.
   - **Recommendation**: scope a delta to audit and reclassify `core/`.

2. **Split `changes/lifecycle.py` into `domain.lifecycle`.**
   - Small module, defines status constants and transitions. Natural first
     inhabitant of `spec_driver.domain.lifecycle`.
   - Would establish the lifecycle sub-area alongside the existing relations work.

3. **Move `Workspace` to `spec_driver.orchestration`.**
   - Already the composition root for all registries and sync ordering. DE-125
     Phase 4 proved it owns cross-registry data flow.
   - Would give the orchestration layer a real module beyond `operations.py`.

4. **Do not touch `formatters/`, `requirements/`, `validation/` yet.**
   - High-coupling consumers; depend on everything else moving first.

### `changes/` coupling hotspot

- 31 cross-area imports (largest in the codebase, excluding core).
- Mixes lifecycle definitions (domain), completion workflows (orchestration),
  registry operations (domain.registries), artifact creation (orchestration).
- Decomposing `changes/` would unblock registry migration for the entire change
  artifact family. But it's a 16-module split, not a quick extract.

### Verification status

- All 4656 tests pass.
- Both import-linter contracts kept.
- `spec-driver validate` passes.
- ruff clean.

### Commits (all phases)

- `1a0d467b` — Phase 2: contract + seam specification
- `7ca724c3` — Phase 3: relations move + backlink extraction
- `ac2ff223` — Phase 3 docs complete
- `10324cff` — Architectural verdict notes + domain migration memory
- `f2f5fcde` — Task 4.1 mini-DR
- `8cf45921` — Phase 4 consistency tightening
- `01b4cf2c` — Task 4.2 registry refactor
- `a400671b` — Phase 4 complete
- `807a050f` — Final notes + core-misplaced-modules memory

All `.spec-driver` changes committed promptly alongside code per doctrine.

## 2026-03-24 — Closure decision

DE-125 closes as a successful pilot. Its findings justify the next delta rather
than stretching into a general migration umbrella.

### Three rules for future migration deltas

1. **Treat core/ as a classification problem before a migration problem.** Files
   like `artifact_view.py` and `enums.py` make the outer layer contract look
   valid while remaining false in practice. Reclassify first, move second.
2. **Optimise for moves that reduce graph centrality, not module count.** 203
   legacy modules exist. Target high-centrality coupling nodes, not leaf modules.
3. **Use Workspace as the canonical orchestration root unless evidence says
   otherwise.** Phase 4 proved it already owns sync ordering and cross-registry
   composition.

### Recommended next delta

Scope a core/ audit delta: reclassify `artifact_view.py` (11 registry imports)
and `enums.py` (5 cross-area imports) so that `spec_driver.core` can migrate
honestly. This is the single highest-leverage prerequisite for all further
migration work.

### Memories captured at closure

- `mem.pattern.architecture.domain-migration` — tactical migration recipe
- `mem.fact.architecture.core-misplaced-modules` — core audit prerequisite
- `mem.pattern.architecture.migration-principles` — strategic rules
