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

## Phase 1 — DE-118 alignment with §11 boundary (Task 1.2)

**Verdict: aligned.** DE-118 lives entirely in application code (`validation/`, `core/frontmatter_metadata/`, `blocks/`); does not introduce `migrations/` package code. DR-136 §11.1's boundary (migration steps may not import `validation/`) is not violated because DE-118 produces no migration steps.

### Coordination notes (Phase 2 entrance, not Phase 1 rework)

- **F-E (Phase 2 entrance task): `MetadataValidator` strict-mode parameterisation.** DE-118 Phase 1 lands "unknown-key rejection on `MetadataValidator`" as a hard rule. DR-136 §5.2 (cross-cutting deliverable Z) requires `MetadataValidator.validate(strict: bool=False)` — loaders pass `strict=False`, `validate` CLI passes `strict=True`. If DE-118 lands unknown-key rejection unconditionally, loaders against unmigrated legacy artefacts may fail before per-artefact migrations run. Phase 2 entrance task: confirm DE-118 lands rejection behind a strict flag (or a permissive default) compatible with DR-136 §5.2's tolerant-on-read mode. If DE-118 closes with unconditional rejection, the cross-cutting child delta must restore the strict flag before per-kind sweeps begin.

- **F-F (coordination, not blocking): `REVISION_CHANGE_METADATA` ownership.** DE-118 Phase 2 introduces `REVISION_CHANGE_METADATA` as the vehicle for retiring `RevisionBlockValidator`. DR-136 §10.2 (revision child delta) further enriches the same schema with `action` enum + conditional rules. Treat as additive: revision child delta extends, does not redefine. No re-work required in DE-118.

### Outcome

DE-118 stays in scope as drafted. F-E surfaces as a Phase 2 entrance check; F-F is a downstream coordination handoff. Neither blocks Phase 1 progression.

## Phase 1 — Child delta map (Task 1.9)

| Child delta ID | Scope summary | DR-136 § anchor | Sequence position | Entry phase | Inherited scope-notes |
|---|---|---|---|---|---|
| **DE-118** | Block validator unification — single `MetadataValidator` layer | §11.1 boundary | 1 (existing draft) | Phase 2 | F-E (Phase 2 entrance check on strict-mode parameterisation), F-F (REVISION_CHANGE_METADATA shared additively with DE-142) |
| **DE-137** | Cross-cutting infrastructure: Y/Z/X + `validate file` + `validate --kind` + skill tuning + `admin migrate` orchestrator + `workflow.toml` schema | §5 + §11 | 2 | Phase 2 | F-B (relations `nature`/`annotation` alias in deliverable Z), F-E (restore strict flag if DE-118 lands rejection unconditionally) |
| **DE-138** | Delta-kind metadata propagation: blocks for `context_inputs`/`risk_register`, `applies_to` derivation, `list deltas` enrichment, `v02_delta_blocks.py` | §6 | 3 | Phase 3 | — (first per-artefact precedent; sets pattern siblings inherit) |
| **DE-139** | Spec-kind metadata propagation: tech SPEC + PROD blocks, taxonomy strict, `list specs` enrichment, `v03_spec_blocks.py` | §7 + F-A PROD extension | 4 | Phase 3 | F-A (PROD placement sub-table authored in DR-139 — PROD coverage is delta's responsibility, not umbrella's) |
| **DE-140** | Requirements-in-spec block-ification: retire regex parser via `supekku:spec.requirements@v1`, interactive `admin migrate-requirements`, `v04_spec_requirements.py` | §8 | 5 | Phase 3 | — |
| **DE-141** | Audit-kind metadata propagation: `findings` → block, per-finding strict outcome enum, `list audits` enrichment, `v05_audit_findings.py` | §9 | 6 | Phase 3 | F-C (`audit_window` stays optional), F-D (per-finding outcome enum lives in block, not FM) |
| **DE-142** | Revision-kind metadata propagation: NEW `REVISION_FRONTMATTER_METADATA`, `supekku:revision.change@v1` action enum + conditional rules, `applies_to` derivation, `v06_revision_metadata.py` | §10 | 7 | Phase 3 | — (last; benefits from four precedents; F-F coordination with DE-118 noted in DE-118's inheritance) |

**Sequence verified against DR-136 DEC-004**: DE-118 → DE-137 (cross-cutting) → DE-138 (delta) → DE-139 (spec, incl. PROD) → DE-140 (reqs-in-spec) → DE-141 (audit) → DE-142 (revision) → DE-136 close.

**No deviation from DEC-004.** All seven child deltas drafted as `status: draft` with `relates_to: DE-136`; full DR/IP/phase authoring is each child's own work when it enters its assigned DE-136 phase.

**Validation baseline (Phase 1 task 1.10 evidence)**: `uv run spec-driver validate` reports only audit-gate warnings on draft deltas (DE-135, DE-136, DE-137..DE-142). No new errors. Matches phase-sheet expectation.
