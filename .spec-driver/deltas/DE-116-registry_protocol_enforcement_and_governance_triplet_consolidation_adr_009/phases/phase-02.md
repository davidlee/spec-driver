---
id: IP-116-P02
slug: "116-registry_protocol_enforcement_and_governance_triplet_consolidation_adr_009-phase-02"
name: IP-116 Phase 1 — Records + base + DecisionRegistry + shims + internal consumers
created: "2026-06-02"
updated: "2026-06-02"
status: completed
kind: phase
plan: IP-116
delta: DE-116
---

# Phase 1 — Records + base + DecisionRegistry + shims + internal consumers

## 1. Objective

Migrate all 3 record dataclasses into `spec_driver/domain/records/`, land the
`RegistryProtocol[T_co]` + `FrontmatterFileRegistry[T]` ABC in
`spec_driver/domain/registries/frontmatter.py`, collapse `DecisionRegistry`
onto the base, create legacy re-export shims for the decision module, and
migrate `spec_driver`-internal consumers to canonical paths. **Policy and
Standard registries remain on supekku paths this phase; P2 migrates them.**

## 2. Links & References

- **Delta**: DE-116 (scope §3, approach P1, verification §6)
- **Design Revision**: DR-116 §4 (code impact table, base-class sketch, Workspace sketch)
- **Specs**: SPEC-117 (decisions)
- **Governance**: ADR-009 §6 (Protocol vehicle — DE-116), ADR-002 (no backlinks in frontmatter),
  POL-003 (module boundaries), ER-6 (import `spec_driver.core.*`, not supekku core)
- **Predecessor**: P0 (`phase-01.md`) — protocol shape locked (GO), OQ-1 resolved.

## 3. Entrance Criteria

- [x] P0 complete — `RegistryProtocol` shape locked (find/collect/iter, positional-only `find`).
- [x] `uv run ty check` baseline green on DE-116 branch.
- [ ] Existing decision registry tests passing (regression baseline).

## 4. Exit Criteria / Done When

- [x] 3 record dataclasses live in `spec_driver/domain/records/{decision,policy,standard}.py` —
      verbatim move, `to_dict` preserved, no logic change.
- [x] `spec_driver/domain/registries/frontmatter.py` exists with `RegistryProtocol[T_co]`
      (locked P0 shape) + `FrontmatterFileRegistry[T]` ABC. Imports only `spec_driver.core.*`
      and stdlib — **zero** `supekku.*` imports, zero `domain.relations` imports.
- [x] `spec_driver/domain/registries/decision.py` exists — `DecisionRegistry` subclassed from
      the base; defines only `_build_record`, `_artifact_dir`, `_resolve_status` (ADR symlink
      inference), `filter`, class attrs (`_prefix`, `_yaml_root_key`), and
      `sync_with_symlinks`/symlink helpers. **No duplicated** `collect`/`_parse_file`/`iter`/
      `find`/`write`/`sync` method bodies; **no `load()` classmethod**.
- [x] `supekku/scripts/lib/decisions/registry.py` is a **re-export shim** — all public names
      (`DecisionRecord`, `DecisionRegistry`, `__all__`) forwarded from canonical paths.
- [x] `supekku/scripts/lib/decisions/__init__.py` was already empty — no change needed.
- [x] `spec_driver/orchestration/artifact_view.py` imports `DecisionRegistry` from
      `spec_driver.domain.registries.decision` (canonical path), not `supekku.*`.
- [x] `uv run ty check` — `RegistryProtocol` conformance green (regression: 331 → 331 diags).
- [x] Decision registry tests (14/14) all pass at `spec_driver/domain/registries/test_decision_registry.py`.

## 5. Verification

- **VA-ty-protocol-conformance**: `uv run ty check` — `DecisionRegistry` structurally satisfies
  `RegistryProtocol[DecisionRecord]` (P0 locked shape; re-verified post-migration).
- **VT-registry-suites**: decision tests moved alongside code; all green.
- **VA-no-relations gate**: `rg "domain\.relations" spec_driver/domain/registries` = 0.
- **VA-core-import gate**: `rg "supekku\.scripts\.lib\.core" spec_driver/domain/records spec_driver/domain/registries` = 0.
- **VA-internal-consumer gate**: `rg "from supekku.*decisions.*import.*DecisionRegistry" spec_driver/` = 0 (non-shim paths).
- **Shim smoke test** (manual): `from supekku.scripts.lib.decisions.registry import DecisionRegistry, DecisionRecord` succeeds.

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - `load_markdown_file` and `extract_h1_title` from `spec_driver.core.spec_utils` are drop-in
    compatible with the supekku-core versions (same signatures, same semantics). They import
    `yaml`/`frontmatter` from `spec_driver.core.yaml_emit`/`frontmatter_schema` — the base class
    will import through `spec_driver.core.spec_utils`.
  - `find_repo_root`, `get_decisions_dir`, `get_registry_dir` from `spec_driver.core` match the
    supekku-core equivalents in behaviour.
  - `parse_date` from `spec_driver.core.dates` is the same implementation.
  - `DecisionRegistry.filter` drops `self`-param divergence: the current `filter(self, ...)` form
    passes through `_build_record` fine; `_filter` helper on the base covers common kw-only params
    (tag/spec/delta/requirement). Per-registry extras (policy/standard) are handled in
    `DecisionRegistry.filter` override that calls `_filter`.
- **STOP when**:
  - `FrontmatterFileRegistry` cannot express Decision's `_resolve_status` override cleanly
    (symlink-dir short-circuit per AR-1) — stop and re-design.
  - `DecisionRegistry.sync_with_symlinks` or `rebuild_status_symlinks` cannot be preserved
    through composition (they depend on `ADR_STATUSES` from `lifecycle`).
  - Shim breaks any consumer that existing tests exercise.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description | Parallel? | Notes |
| ------ | --- | --- | --- | --- |
| [x]    | 1.1 | Create `spec_driver/domain/records/decision.py` — DecisionRecord dataclass | [P] | verbatim move; `to_dict` kept |
| [x]    | 1.2 | Create `spec_driver/domain/records/policy.py` — PolicyRecord dataclass | [P] | verbatim move; `to_dict` kept |
| [x]    | 1.3 | Create `spec_driver/domain/records/standard.py` — StandardRecord dataclass | [P] | verbatim move; `to_dict` kept |
| [x]    | 1.4 | Create `spec_driver/domain/registries/frontmatter.py` — `RegistryProtocol` + `FrontmatterFileRegistry` ABC | [ ] | Per DR §4 sketch; imports `spec_driver.core.*` only |
| [x]    | 1.5 | Create `spec_driver/domain/registries/decision.py` — `DecisionRegistry` onto base | [ ] | `_build_record`, `_artifact_dir`, `_resolve_status` override, `filter`, symlink methods |
| [x]    | 1.6 | Shim `supekku/scripts/lib/decisions/registry.py` → re-export from canonical | [ ] | forward all public names |
| [x]    | 1.7 | Shim `supekku/scripts/lib/decisions/__init__.py` → re-export | [ ] | __init__.py was already empty — no change needed |
| [x]    | 1.8 | Migrate `spec_driver/orchestration/artifact_view.py` — import from canonical | [ ] | 1 line change |
| [x]    | 1.9 | Create/migrate decision registry tests to canonical path | [ ] | `spec_driver/domain/registries/test_decision_registry.py` |
| [x]    | 1.10 | Full suite: `uv run ty check` + `uv run pytest` green | [ ] | regression gate: ty 333→331 (-2 from cleaner imports), 14/14 test pass |

### Task Details

- **1.1–1.3 Record dataclasses**
  - **Design / Approach**: Move the `@dataclass` block + `to_dict()` verbatim from each
    `supekku/scripts/lib/{decisions,policies,standards}/registry.py` into
    `spec_driver/domain/records/{decision,policy,standard}.py`. Zero logic change. Add
    `from __future__ import annotations` and the necessary stdlib/typing imports.
  - **Files / Components**: `spec_driver/domain/records/` (new files).
  - **Testing**: existing tests exercise these via registry imports; no standalone record tests
    needed.

- **1.4 FrontmatterFileRegistry ABC**
  - **Design / Approach**: Follow DR §4 base-class sketch exactly. Key details:
    * `RegistryProtocol[T_co]` — find/collect/iter, `@runtime_checkable`, positional-only `find`
      (from P0 locked shape).
    * `FrontmatterFileRegistry(ABC, Generic[T])` — template method ABC.
    * Constructor: `root: Path | None = None` keyword-only, stores `self.root` via
      `find_repo_root(root)`, `self.directory = self._artifact_dir(self.root)`,
      `self.output_path = get_registry_dir(self.root) / f"{self._yaml_root_key}.yaml"`.
    * `collect()` — globs `f'{self._prefix}-*.md'` in `self.directory`, calls `_parse_file`
      per file, keys by `record.id`.
    * `_parse_file(path)` — uses `load_markdown_file`, regex-matches prefix+digits,
      resolves id/title/status via `_resolve_status`/`_build_record`.
    * `_resolve_status(fm, path)` — base: `(fm.get('status') or '').lower() or 'draft'`.
      Decision MUST override with short-circuit (AR-1): check `status` in fm first; if present
      return it; else `_infer_from_dirs(path)`; else `'draft'`. Do NOT call
      `super()._resolve_status()` — the base default (`'draft'`) would prevent dir inference.
    * `_matches_common(r, *, tag, spec, delta, requirement)` — shared filter predicate.
    * `_filter(*, common: dict, extra: dict)` — `[r for r in iter if _matches_common + per-field]`.
    * `write(path, *, records=None)` — PURE YAML dump (no backlinks). Sorted by id.
    * `sync()` — `self.write(records=self.collect())`. No backlinks.
    * Abstract: `_artifact_dir`, `_build_record`. Class attrs: `_prefix`, `_yaml_root_key`.
    * Optional: `backlink_inputs: list[tuple[str, str]] = []` (declarative, consumed by
      Workspace in P2).
    * Imports: `spec_driver.core.{dates,paths,repo,spec_utils}` + stdlib only. ZERO
      `supekku.*`, ZERO `domain.relations`.
  - **Files / Components**: `spec_driver/domain/registries/frontmatter.py` (new).
  - **Testing**: covered indirectly by decision registry tests in 1.9.

- **1.5 DecisionRegistry onto base**
  - **Design / Approach**: Subclass `FrontmatterFileRegistry[DecisionRecord]`. Class attrs:
    `_prefix = "ADR"`, `_yaml_root_key = "decisions"`. Defines:
    * `_artifact_dir(root)` → `get_decisions_dir(root)`
    * `_build_record(fm, content, *, record_id, title, status, path)` → `DecisionRecord(...)`
    * `_resolve_status(fm, path)` — short-circuit override per AR-1 (see 1.4 notes).
    * `_infer_from_dirs(path)` — scans `ADR_STATUSES` dirs for symlink presence.
    * `filter(self, *, tag, spec, delta, requirement, policy, standard)` — calls
      `self._filter(common={...}, extra={'policies': policy, 'standards': standard})`.
    * `sync_with_symlinks()` — `self.collect(); self.write(); self.rebuild_status_symlinks()`.
    * `_cleanup_all_status_directories(decisions_dir)`, `_rebuild_status_directory(status_dir, decisions)`.
    * **Does NOT define**: `collect`, `_parse_file`, `iter`, `find`, `write`, `sync` — all
      inherited from base. **No `load()` classmethod** — base constructor handles init.
    * `backlink_inputs` stays `[]` (ADR has no backlinks).
  - **Files / Components**: `spec_driver/domain/registries/decision.py` (new).
  - **Testing**: see 1.9.

- **1.6–1.7 Decision shims**
  - **Design / Approach**: `supekku/scripts/lib/decisions/registry.py` becomes:
    ```python
    """Re-export shim → spec_driver.domain.records.decision / spec_driver.domain.registries.decision.
    DO NOT add new code here."""
    from spec_driver.domain.records.decision import DecisionRecord
    from spec_driver.domain.registries.decision import DecisionRegistry
    __all__ = ["DecisionRecord", "DecisionRegistry"]
    ```
    `supekku/scripts/lib/decisions/__init__.py` imports from the shimmed registry or directly.
    Check current `__init__.py` before editing — it may already re-export.
  - **Files / Components**: `supekku/scripts/lib/decisions/registry.py`, `__init__.py`.
  - **Testing**: shim smoke (import works, isinstance works). Dedicated shim-compat suite in P2.

- **1.8 Internal consumer migration**
  - **Design / Approach**: In `spec_driver/orchestration/artifact_view.py` lines 394–396, replace:
    ```python
    from supekku.scripts.lib.decisions.registry import DecisionRegistry
    return DecisionRegistry(root=root)
    ```
    with:
    ```python
    from spec_driver.domain.registries.decision import DecisionRegistry
    return DecisionRegistry(root=root)
    ```
  - **Files / Components**: `spec_driver/orchestration/artifact_view.py`.
  - **Testing**: existing tests that exercise artifact_view.

- **1.9 Decision registry tests**
  - **Design / Approach**: Create `tests/domain/registries/test_decision_registry.py`. Port any
    existing decision registry tests from the legacy test suite. Test:
    * `collect()` — finds ADR-*.md files, returns dict keyed by id.
    * `find(decision_id)` — lookup by ID, None for missing.
    * `iter(status=...)` — status filtering.
    * `filter(tag=..., spec=...)` — multi-criteria filter.
    * `write()` — produces valid YAML at output path.
    * `sync()` — write after collect.
    * ADR symlink status inference from directory structure.
    * `RegistryProtocol` conformance: `isinstance(DecisionRegistry(), RegistryProtocol)` → True.
  - **Files / Components**: `tests/domain/registries/test_decision_registry.py` (new).
  - **Observations & AI Notes**: P2 adds `VT-shim-compat` suite on legacy paths (ER-3).

- **1.10 Full suite**
  - **Approach**: `uv run ty check` + `uv run pytest` from repo root.
  - **Acceptance**: zero new failures. Baseline ty noise (331 diagnostics) tolerated.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| `load_markdown_file` via `spec_driver.core.spec_utils` differs from supekku-core | Verify signatures match; `spec_utils` import chain includes `yaml_emit`/`frontmatter_schema` which `frontmatter.py` must not depend on transitively — the import-linter gate catches this | open |
| `DecisionRegistry._resolve_status` override can't express AR-1 short-circuit cleanly | Base default (`'draft'`) must not block dir inference; design the override to skip `super()` (already in sketch) | open |
| `sync_with_symlinks` depends on `ADR_STATUSES` from `supekku.scripts.lib.decisions.lifecycle` | Import the constant from its current location; not migrating lifecycle this delta | open |
| Shim breaks `supekku/scripts/lib/workspace.py` DecisionRegistry import | Workspace imports from `supekku.scripts.lib.decisions.registry` which is now a shim → transparent; no change needed | open |

## 9. Decisions & Outcomes

- `2026-06-02` — Phase authored. Record dataclasses moved verbatim (no refactor). Decision-only
  migration this phase; Policy/Standard in P2.

## 10. Findings / Research Notes

- **Current state**: `spec_driver/domain/records/__init__.py` and `spec_driver/domain/registries/__init__.py`
  are empty files. New record modules go alongside them.
- **`artifact_view.py`**: Only one spec_driver-internal consumer of decision registry imports
  (lines 394–396). The ≤3 count in DR §4 was a conservative estimate; reality is 1.
- **Workspace**: `supekku/scripts/lib/workspace.py` lines 100–110 import `DecisionRegistry`
  from `supekku.scripts.lib.decisions.registry` (now the shim path). Shim makes this transparent.
- **ADR_STATUSES**: import from `supekku.scripts.lib.decisions.lifecycle` — kept as-is this delta.
- **Policy/Standard records** (tasks 1.2/1.3): created now so the base can import them, but their
  registries stay in supekku until P2.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] IP-116 progress updated (P1 ticked)
- [ ] Hand-off notes to P2 (Policy/Standard + backlink hoist)
