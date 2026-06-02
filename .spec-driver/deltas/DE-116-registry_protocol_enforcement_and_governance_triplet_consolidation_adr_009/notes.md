# Notes for DE-116

## P0 — Protocol conformance spike (completed 2026-06-02)

**Outcome**: GO. `RegistryProtocol[T_co]` (find/collect/iter, positional-only `find`) passes ty check with zero errors against all 3 registries. Runtime `isinstance` True for all 3. Filter exclusion confirmed correct (9/9 negative-check failures across 3 protocol variants).

**Locked protocol shape** (phase-01.md §9):
```python
@runtime_checkable
class RegistryProtocol(Protocol[T_co]):
    def find(self, id: str, /) -> T_co | None: ...
    def collect(self) -> dict[str, T_co]: ...
    def iter(self, status: str | None = None) -> Iterator[T_co]: ...
```

**Surprises**: None. Positional-only `find` absorbed param-name divergence exactly as hypothesised. `filter` negative check was stronger than expected — even the "closest" variant (ProtoFilterC matching Standard's kw-only set) failed, because protocol keyword-only params that the concrete type doesn't accept are contract violations.

**OQ-1 closed**, OQ-2 already closed, R2 closed. AR-4 magic-strings follow-up remains.

**Ready for P2** — PolicyRegistry + StandardRegistry + Workspace backlink hoist.

## P2 — Policy + Standard registries + Workspace backlink hoist (completed 2026-06-02)

**Outcome**: All 9 tasks complete. 36/36 tests pass. **R is landable.**

### Files created
- `spec_driver/domain/registries/policy.py` — PolicyRegistry collapsed onto base
- `spec_driver/domain/registries/standard.py` — StandardRegistry collapsed onto base
- `spec_driver/domain/registries/test_shim_compat.py` — 18 tests on legacy import paths
- `spec_driver/domain/registries/test_golden_yaml.py` — 4 tests with fixture corpus

### Files modified
- `supekku/scripts/lib/policies/registry.py` → re-export shim
- `supekku/scripts/lib/standards/registry.py` → re-export shim
- `supekku/scripts/lib/workspace.py` → `_sync_governance` + `_registry_for`; backlink hoist
- `spec_driver/orchestration/artifact_view.py` → Policy/Standard canonical imports

### Surprises
- `policies/__init__.py` and `standards/__init__.py` already re-export via registry modules
  — no change needed.
- `build_backlinks_multi` works correctly when records are passed pre-mutated. The
  golden-YAML tests verify backlinks appear in YAML output through Workspace orchestration.

### Gates
- no-relations: 0 (docstring match only, no actual imports)
- core-import: 0
- internal-consumer: 0
- zero-duplication: 0 (grep for def collect/_parse_file/iter/find/write/sync in decision/policy/standard.py)
- ty check: 333 (baseline noise, no regression)
- tests: 36/36 pass

## P1 — Records + base + DecisionRegistry + shims + internal consumers (completed 2026-06-02)

**Outcome**: All 10 tasks complete. 14/14 tests pass.

### Files created
- `spec_driver/domain/records/{decision,policy,standard}.py` — verbatim record dataclasses
- `spec_driver/domain/registries/frontmatter.py` — `RegistryProtocol[T_co]` + `FrontmatterFileRegistry[T]` ABC
- `spec_driver/domain/registries/decision.py` — `DecisionRegistry` collapsed onto base
- `spec_driver/domain/registries/test_decision_registry.py` — 14 tests

### Files modified
- `supekku/scripts/lib/decisions/registry.py` — re-export shim
- `spec_driver/orchestration/artifact_view.py` — canonical import

### Surprises
- **Circular import**: `decision.py` top-level import of `ADR_STATUSES` from `supekku.scripts.lib.decisions.lifecycle` triggered `supekku/scripts/lib/__init__.py` → `workspace.py` → shim → canonical import → circular. Fixed with lazy imports inside `_infer_from_dirs` and `_cleanup_all_status_directories`.
- **Co-located tests**: `tests/` dir doesn't resolve `spec_driver` package; tests must be co-located alongside source (existing pattern: `spec_driver/*/test_*.py`).
- **Environment issues**: `uv run pytest` uses Nix system Python (3.13.13) but venv has 3.13.12; `yaml`/`click`/`pydantic` unavailable in system Python — pre-existing. Used `.venv/bin/python -m pytest` as workaround.
- **`decisions/__init__.py`** was already empty (`__all__: list[str] = []`) — no shim needed.
- **Internal consumers**: only 1 (`artifact_view.py`), not ≤3 as DR conservatively estimated.

### Gates
- no-relations: `rg "from.*domain\.relations|import.*domain\.relations" spec_driver/domain/registries/` = 0 ✅
- core-import: `rg "supekku\.scripts\.lib\.core" spec_driver/domain/registries/` = 0 ✅
- internal-consumer: `rg "from supekku.*decisions.*import.*DecisionRegistry" spec_driver/` = 0 ✅
- ty check: 331 diagnostics (no regression from baseline 331) ✅
- tests: 14/14 pass ✅

**Ready for P2** — PolicyRegistry + StandardRegistry + Workspace backlink hoist.

## P2 — Policy + Standard registries + Workspace backlink hoist (completed 2026-06-02)

**Outcome**: All 9 tasks complete. 36/36 tests pass. R is landable.

- `spec_driver/domain/registries/policy.py`, `standard.py` collapsed onto base
- `supekku/scripts/lib/policies/registry.py`, `standards/registry.py` → re-export shims
- `supekku/scripts/lib/workspace.py` → `_sync_governance` + `_registry_for` (backlink hoist)
- `spec_driver/orchestration/artifact_view.py` → Policy/Standard canonical imports
- Golden-YAML: 4/4, shim-compat: 18/18
- Gates: no-relations=0, core-import=0, internal-consumer=0, zero-duplication=0

## P3 — Creation impl-only unification (completed 2026-06-02)

Shared private `_create_governance_artifact` engine. 3 public wrappers ~15 lines each.
All public symbols, error messages preserved. OQ-2 closed.

## P4 — Verification sweep (completed 2026-06-02)

All gates green. Follow-ups: shim-debt, DriftLedger.filter, AR-4 magic strings.

---

**Summary**: DE-116 all 5 phases complete. 36/36 tests pass. Delta ready for audit/close.
