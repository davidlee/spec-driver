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

## 2026-03-24 — Post-pilot design reconciliation

- Extended the delta with Phase 4 (`IP-125-P04`) instead of closing after the
  pilot.
- Recorded the explicit boundary decision: orchestration owns cross-registry
  source collection; `domain.relations` computes on pre-collected data; registries
  remain local authorities.
- Reconciled the docs so Phase 3 no longer overclaims that sibling-registry
  imports were removed; the computation moved, but collection debt remains.
- Marked re-export shims and legacy-core imports as transition debt that needs
  retirement criteria before broader registry migration continues.
