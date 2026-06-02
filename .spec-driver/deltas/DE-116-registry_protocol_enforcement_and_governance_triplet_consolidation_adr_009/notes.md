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
