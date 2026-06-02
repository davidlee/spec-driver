---
id: IP-116-P01
slug: "116-registry_protocol_enforcement_and_governance_triplet_consolidation_adr_009-phase-01"
name: IP-116 Phase 0 — Protocol conformance spike
created: "2026-06-02"
updated: "2026-06-02"
status: completed
kind: phase
plan: IP-116
delta: DE-116
---

# Phase 0 — Protocol conformance spike

## 1. Objective

De-risk the migration before any production code moves. Prove that a `RegistryProtocol[T]`
covering the ADR-009 **read surface (`find`/`collect`/`iter` only)** is satisfiable by the three
existing governance registries (`DecisionRegistry`, `PolicyRegistry`, `StandardRegistry`) under both
`uv run ty check` (signature conformance — the real gate) and runtime `isinstance` (method presence
— AR-3). Lock the exact protocol signature shape, and confirm `filter`'s exclusion from the typed
generic is correct in practice (ER-1). **Output is a go / documented-fallback decision (OQ-1); no
production code lands this phase.**

## 2. Links & References

- **Delta**: DE-116
- **Design Revision Sections**: DR-116 §3 (Architecture Intent — `RegistryProtocol` = find/collect/iter,
  `filter` excluded), §4 (base-class sketch, `@runtime_checkable class RegistryProtocol(Protocol[T_co])`),
  §5 (verification — VA-ty / VT-runtime-protocol; phase-0 spike paragraph), §8 (OQ-1),
  §11 AR-3 (`runtime_checkable` = presence only), §12 ER-1 (`filter` is a type trap).
- **Specs**: SPEC-117 (decisions), SPEC-126 (policies), SPEC-127 (standards).
- **Governance**: ADR-009 §1 (`iter` positional-or-keyword), §5 (`filter` params stay domain-specific),
  §6 (Protocol formalisation trigger — names DE-116).
- **Support Docs**: `mem.fact.architecture.import-linter-supekku-blindspot`.

## 3. Entrance Criteria

- [ ] DR-116 review-integrated (internal AR-1..6 + external codex ER-1..7) — done.
- [ ] `just check` green on the DE-116 branch baseline.
- [ ] Current read-surface signatures catalogued (done — see §10 Findings).

## 4. Exit Criteria / Done When

- [ ] A throwaway `RegistryProtocol[T_co]` (`find`/`collect`/`iter`, `@runtime_checkable`) is type-checked
      against all 3 current registries with `uv run ty check` reporting **zero** conformance errors.
- [ ] `isinstance(reg, RegistryProtocol)` returns `True` at runtime for one instance of each registry.
- [ ] The `find` parameter-name divergence (`decision_id`/`policy_id`/`standard_id`) is resolved in the
      locked protocol shape — confirmed by ty (expected: declare `find(self, id: str, /)` positional-only;
      if ty rejects positional-only structural match, document the fallback).
- [ ] `filter` is confirmed **excluded** from the typed protocol — a spike check that adding it with any
      single generic signature produces ty errors against the 3 keyword-only `filter` impls (proves ER-1).
- [ ] **OQ-1 resolved**: recorded in §9 as either GO (locked signatures pasted) or FALLBACK
      (find/collect/iter strict + `filter` existence-only) with the ty evidence.
- [ ] Spike code is **deleted** (or quarantined under a clearly-marked throwaway path); no production
      module imports it.

## 5. Verification

- `uv run ty check` on the spike module + the 3 registries — **zero** protocol-conformance errors (VA-ty).
- A tiny runtime assertion script: `assert isinstance(DecisionRegistry(), RegistryProtocol)` (and Policy,
  Standard) — exits 0 (VT-runtime-protocol; presence only, AR-3).
- Negative check: a variant protocol that *includes* `filter` fails ty — captured as evidence for ER-1.
- Evidence to capture: the locked `RegistryProtocol` signature block + `ty check` output snippet, pasted
  into §9 / §10. No `just check` regression expected (no production change).

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - `collect(self) -> dict[str, T]` and `iter(self, status: str | None = None) -> Iterator[T]` are
    already uniform across all 3 registries (verified — §10).
  - The only read-surface divergence is `find`'s parameter name; positional-only `/` in the protocol
    resolves it without touching registry signatures.
- **STOP when**:
  - ty rejects the find/collect/iter protocol even with positional-only params → STOP, escalate via
    `/consult`; the typed-protocol premise (DEC-116-1) needs revisiting before P1.
  - Resolving `find` would require renaming `decision_id`/`policy_id`/`standard_id` across registries
    (a public-ish signature change) → STOP and confirm scope with user before proceeding.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [ ] | 0.1 | Draft throwaway `RegistryProtocol[T_co]` (find/collect/iter, `@runtime_checkable`) | [ ] | positional-only `find(self, id, /)` |
| [ ] | 0.2 | `ty check` the protocol against the 3 current registries; iterate signatures until zero errors | [ ] | the real conformance gate |
| [ ] | 0.3 | Runtime `isinstance` assertion for each registry | [P] | presence only (AR-3) |
| [ ] | 0.4 | Negative check: protocol-with-`filter` fails ty (evidence for ER-1) | [P] | confirms filter exclusion |
| [x] | 0.5 | Record OQ-1 outcome (GO / fallback) + paste locked signatures into §9/§10 | [ ] | feeds P1 base-class shape |
| [x] | 0.6 | Delete / quarantine spike code | [ ] | no production import |

### Task Details

- **0.1 Draft protocol**
  - **Design / Approach**: Per DR §4 sketch. `T_co = TypeVar("T_co", covariant=True)`; `find(self, id: str, /) -> T_co | None`, `collect(self) -> dict[str, T_co]`, `iter(self, status: str | None = None) -> Iterator[T_co]`. `@runtime_checkable`. Positional-only `/` on `find` is the hypothesis for absorbing the `decision_id`/`policy_id`/`standard_id` name divergence.
  - **Files / Components**: one throwaway module (e.g. `/tmp` or a clearly-marked `_spike_*.py` under the delta — NOT under `spec_driver/`).
  - **Testing**: n/a (spike).
- **0.2 ty conformance**
  - **Approach**: `uv run ty check <spike module>`. If `find` rejected, try positional-only; if still rejected, capture the exact ty diagnostic and route to STOP/§9. Do not mutate registry signatures without hitting the STOP gate.
  - **Observations & AI Notes**: ty 0.0.38 in this repo.
- **0.4 filter negative check**
  - **Approach**: add `filter(self, *args, **kwargs)` (or any single signature) to a protocol variant; expect ty errors against the 3 keyword-only `filter` impls. This *confirms* the §3/ER-1 decision to exclude `filter` — it is not an attempt to make it conform.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| R2 — find/collect/iter signatures fail strict conformance | This phase exists to catch it pre-migration; documented fallback = find/collect/iter strict only, filter existence-only | **closed** — GO, zero ty errors |
| `find` resolution needs registry param renames (scope creep) | STOP condition §6; confirm with user before any rename | open |

## 9. Decisions & Outcomes

- `2026-06-02` — Phase authored. OQ-1 to be resolved by spike (GO vs fallback). Hypothesis: positional-only
  `find(self, id, /)` makes all 3 registries conform under ty; `filter` stays excluded (ER-1).
- _(record GO / fallback + locked signature block here on completion)_

## 10. Findings / Research Notes

Read-surface signatures in the **current** (pre-migration) registries:

| Method | DecisionRegistry | PolicyRegistry | StandardRegistry | Uniform? |
| --- | --- | --- | --- | --- |
| `collect` | `collect(self) -> dict[str, DecisionRecord]` | `dict[str, PolicyRecord]` | `dict[str, StandardRecord]` | ✅ (modulo T) |
| `iter` | `iter(self, status: str \| None = None)` | same | same | ✅ |
| `find` | `find(self, decision_id: str)` | `find(self, policy_id: str)` | `find(self, standard_id: str)` | ⚠ param name diverges |
| `filter` | keyword-only, per-registry fields | keyword-only | keyword-only | ✗ excluded (ER-1) |

Source: `supekku/scripts/lib/{decisions,policies,standards}/registry.py`. The `find` param-name
divergence is the single real conformance question for the typed read surface; `filter`'s exclusion is
already a settled design fact (DR §3, ER-1).

### Spike results (2026-06-02)

- **ty check (find/collect/iter)**: `All checks passed!` — zero protocol-conformance errors against
  all 3 registries with positional-only `find(self, id, /)`.
- **isinstance**: All 3 registries return `True` (method presence, AR-3).
- **filter negative check**: 9/9 diagnostic errors across 3 protocol variants — no single generic
  `filter` signature can structurally satisfy all 3 registries. Confirms the ER-1 decision to
  exclude `filter` from the typed generic; `filter` is asserted by existence test only.

Spike artefacts: `phases/_spike_protocol_conformance.py`, `phases/_spike_filter_negative.py` (to be deleted in task 0.6).

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied (ty zero-errors + isinstance true + OQ-1 recorded)
- [x] Verification evidence stored (locked signatures + ty output in §9/§10)
- [x] IP-116 update not needed (GO path, no fallback — DEC-116-1 unchanged, R2 closed)
- [x] Spike code deleted; hand-off note to P1 (base-class signature shape locked)
