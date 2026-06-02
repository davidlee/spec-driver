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

**Ready for P1** — records + base + DecisionRegistry + shims.

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
