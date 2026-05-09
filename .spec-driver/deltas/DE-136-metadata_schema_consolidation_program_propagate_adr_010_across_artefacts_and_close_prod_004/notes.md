# Notes for DE-136

## Phase 1 — Placement-table review (Task 1.1)

Sampled artefacts (representative of each kind):

- Delta: DE-129, DE-130, DE-131, DE-132 (recent), DE-136 (this delta)
- Spec (tech): SPEC-114, SPEC-116
- Spec (product): PROD-004
- Audit: AUD-021, AUD-022, AUD-024, AUD-012 (older w/ outcome:pass)
- Revision: RE-040

### Findings vs DR-136 placement tables

#### F-A: PROD vs SPEC scope under DR-136 §7 (potential DR amendment)

**Observation.** DR-136 §7 ("Per-artefact: Spec") is keyed on tech-spec shape:
- `category: unit|assembly` (strict)
- `c4_level: system|container|component|code|interaction` (strict)
- `concerns`/`hypotheses`/`decisions` → blocks

PROD has a separate `PROD_FRONTMATTER_METADATA` (`supekku/scripts/lib/core/frontmatter_metadata/prod.py`) with:
- `category` (freeform string, not enum) — collides on field name with SPEC's enum
- no `c4_level`
- `hypotheses` (list-of-objects: id/statement/status) — same field name, same shape class as SPEC's
- `decisions` (list-of-objects: id/summary)
- `problems`, `value_proposition`, `scope`, `guiding_principles`, `assumptions`, `product_requirements`

DE-136 itself names PROD-004, PROD-006, PROD-010 in `applies_to.specs`; PROD-004 is the close target.

**Implication.** The "spec child delta" (Phase 1 task 1.5) cannot inherit DR-136 §7 cleanly without an explicit PROD treatment. Two ergonomically clean options:

- **Option A** — DR amendment: split §7 into §7a (tech spec) and §7b (PROD). PROD gets its own placement table covering `hypotheses`/`decisions`/`product_requirements` → blocks, `category` (freeform) decision (keep FM? CUT?), no `c4_level`.
- **Option B** — single combined spec child delta scope; child delta authors a placement sub-table for PROD as part of their DR.

**Recommendation.** Option B (carry into spec child delta). PROD's metadata divergence is real but tractable as a child-delta scoping decision, not an umbrella structural conflict. Spec child delta DR must call out PROD coverage explicitly. Record as `OQ-PROD-SPEC-SPLIT` for the spec child delta to resolve.

**Status.** Not STOP-blocking; flag for spec child delta scope notes.

#### F-B: `relations[].nature` vs `relations[].annotation` corpus drift

**Observation.** DE-129 uses `relations[].annotation` (and `context_inputs[].annotation`); DE-136 uses `relations[].nature`. Both validate today. DR-136 §4 universal cuts and §6 delta placement do not address this.

**Implication.** Universal `relations` field shape is BASE-level (used by all kinds). Picking one canonical name is a cross-cutting concern, not a per-artefact concern. The cross-cutting child delta (5.2 alias autocorrect) is the natural home: add a permanent alias `nature → annotation` (or vice-versa) in `RELATIONS_SCHEMA`'s field metadata, and let `validate --fix` normalise.

**Recommendation.** Cross-cutting child delta scope-note: include the BASE relations item-key alias decision in 5.2 deliverable. Pick canonical based on dominant usage (suspect `annotation`). Adversarial review's DEC-016 notes touch on relations-shape but at the typed-by-key vs array-of-objects level (different concern, deferred).

**Status.** Not STOP-blocking; flag for cross-cutting child delta scope notes.

#### F-C: Audit `audit_window` optional in current corpus

**Observation.** AUD-024 has no `audit_window`. DR-136 §9.1 lists it as FM but doesn't say required/optional. AUD-012 (referenced in §9.3 as the strict-mode failure case for `outcome: pass`) — kept as the exemplar.

**Implication.** Audit child delta needs to decide: keep optional, or make required. If required, AUD-024 and others fail strict mode → drift entries. Likely keep optional unless audit kind metadata says otherwise.

**Status.** Not STOP-blocking; flag for audit child delta scope notes.

#### F-D: Per-finding `outcome` vs artefact-level audit `outcome`

**Observation.** DR §9.3 says "outcome enum strictly enforced (aligned | drift | risk); AUD-012's `outcome: pass` becomes strict-mode error." Sampled audits (AUD-024) have **per-finding** `outcome` but no visible artefact-level `outcome`. Need to confirm whether the AUD-012 reference is per-finding or artefact-level.

**Implication.** Audit child delta must ground §9.3's "outcome" in the actual frontmatter shape — likely per-finding, since findings move to a block per §9.1. If per-finding, the strict enum lives in `supekku:audit.findings@v1` block schema, not FM.

**Status.** Not STOP-blocking; flag for audit child delta scope notes.

### DR amendment triggers

None require immediate `/draft-design-revision` per the Phase 1 STOP gate. All four findings translate to scope-notes carried by the relevant child delta. F-A is the closest to a DR amendment trigger; the recommendation defers it to spec child delta authoring.

## Phase 1 — Child delta map (Task 1.9)

_Populated after tasks 1.3–1.8._

| Child delta ID | Scope summary | DR-136 § anchor | Sequence position | Entry phase |
|---|---|---|---|---|
| DE-118 | Block validator unification | §11.1 boundary | 1 (existing) | Phase 2 |
| (TBD) | Cross-cutting infrastructure (Y/Z/X + validate file + validate --kind + skill tuning + admin migrate orchestrator) | §5 | 2 | Phase 2 |
| (TBD) | Delta per-artefact propagation | §6 | 3 | Phase 3 |
| (TBD) | Spec per-artefact propagation (incl. PROD per F-A) | §7 | 4 | Phase 3 |
| (TBD) | Requirements-in-spec block-ification | §8 | 5 | Phase 3 |
| (TBD) | Audit per-artefact propagation | §9 | 6 | Phase 3 |
| (TBD) | Revision per-artefact propagation + REVISION_FRONTMATTER_METADATA | §10 | 7 | Phase 3 |

Inherited scope-notes (F-A..F-D) propagated into each child delta on creation.
