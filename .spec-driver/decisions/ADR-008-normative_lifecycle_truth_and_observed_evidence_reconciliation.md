---
id: ADR-008
title: "ADR-008: normative lifecycle truth and observed evidence reconciliation"
status: accepted
created: "2026-03-06"
updated: "2026-03-06"
reviewed: "2026-03-06"
owners: []
supersedes: []
superseded_by: []
policies: []
specs:
  - PROD-008
  - PROD-009
requirements: []
deltas:
  - DE-047
revisions: []
audits: []
related_decisions:
  - ADR-004
related_policies: []
tags:
  - lifecycle
  - requirements
  - architecture
summary: "Specs own normative lifecycle truth; audits, deltas, and contracts contribute observed evidence overlays; drift is reconciled explicitly rather than silently by timestamp precedence."
---

# ADR-008: normative lifecycle truth and observed evidence reconciliation

## Context

The current corpus disagrees on three lifecycle questions already recorded in
`DL-047`:

- do specs remain authoritative for requirement lifecycle, or can newer
  evidence silently override them?
- is the requirements registry authoritative, or a derived projection?
- what do baseline statuses such as `asserted` and `legacy_verified` mean?

This ADR settles those questions and aligns lifecycle doctrine with `ADR-004`:
observation precedes reconciliation, and specs remain authoritative by explicit
reconciliation rather than silent overwrite.

## Decision

### 1. Specs own normative lifecycle truth

Specs are the authoritative record of normative requirement lifecycle truth:
what is accepted, intended, planned, active, or retired.

This includes the requirement definition plus its lifecycle and coverage claims
in the owning spec.

### 2. Evidence overlays record observed truth

Audits, deltas, plans, contracts, and related evidence sources record observed
truth: what implementation and verification artefacts indicate is currently the
case.

Observed truth may disagree with the spec. That disagreement is drift, not an
automatic replacement of spec truth.

### 3. Drift is resolved explicitly, never by timestamp precedence

When normative truth and observed truth diverge, the system must surface the
conflict explicitly.

Drift is resolved through explicit human-directed reconciliation:

- revise the spec
- create or apply a revision
- create follow-up change work
- accept or document a governance decision

The system must not silently decide that the newest evidence "wins", whether by
timestamp, artefact kind, or overlay priority.

### 4. New evidence triggers reconciliation; it does not rewrite authority

New evidence is a prompt to reconcile authoritative records, not a mechanism for
changing them by implication.

This follows `ADR-004`:

- audits and contracts show what is
- revisions describe what must change in the documentary record
- specs become authoritative again once reconciled

### 5. The requirements registry is derived, not authoritative

The requirements registry is a derived view that aggregates:

- normative data from specs
- observed evidence from deltas, plans, audits, and related artefacts

Its job is to present a computed snapshot, provenance, warnings, and traceability.
It is not itself an authoritative source of lifecycle truth.

Manual edits to the registry are therefore non-canonical and must not become the
governing lifecycle path.

### 6. `asserted` and `legacy_verified` are formal baseline states

These statuses exist to model legacy and transitional reality without collapsing
normative and observed truth.

- `asserted`: a normative claim recorded in the spec without supporting
  verification evidence yet. It means "we state this is true/required, but do
  not currently have receipts in the system."
- `legacy_verified`: grandfathered observed truth accepted as verified from
  before the current evidence system existed. It means "treated as verified,
  but the original verification provenance predates or sits outside the current
  machinery."

Neither status means "newest evidence wins". They are explicit semantic states
that must be shown as such.

## Consequences

### Positive

- Preserves `PROD-008`'s core rule that specs remain authoritative.
- Keeps observed evidence useful without turning it into a silent competing truth source.
- Makes lifecycle drift actionable instead of implicit.
- Clarifies the role of the requirements registry as a projection layer.
- Gives `asserted` and `legacy_verified` precise semantics for revisions and UI/CLI output.

### Negative

- Lifecycle UIs and registries become more nuanced because they must show both normative and observed states when they differ.
- Some previously simpler "effective status" language in `PROD-009` becomes explicit drift/reconciliation logic instead.
- More disagreements will surface as warnings or follow-up work instead of being auto-resolved by precedence rules.

### Neutral

- This ADR does not forbid computed summaries or effective-status projections; it limits their authority.
- This ADR does not require every observed mismatch to block work immediately; governance decides how hard to gate on drift.
- Existing implementation details may remain temporarily more permissive than this ADR until follow-up revisions and code changes land.

## Verification

- Specs remain the authoritative home for lifecycle state in revised product docs.
- Registry and CLI views present lifecycle as a derived projection with provenance, not as an independent authority source.
- Validation surfaces disagreements between spec claims and observed evidence instead of silently applying timestamp precedence.
- `asserted` and `legacy_verified` are explicitly defined in follow-up revisions to `PROD-009`.
- Follow-up revisions reconcile `PROD-008` and `PROD-009` to this doctrine.

## References

- `drift/DL-047-spec-corpus-reconciliation.md`
- `specify/decisions/ADR-004-canonical_workflow_loop.md`
- `specify/product/PROD-008/PROD-008.md`
- `specify/product/PROD-009/PROD-009.md`
- `.spec-driver/about/lifecycle.md`
