---
name: audit-change
description: Canonical reconciliation runsheet for AUD artefacts. Create or update the audit, disposition every finding, reconcile specs/contracts, and hand off to closure only when audit state supports it.
---

You are running the canonical audit reconciliation loop.

Inputs:

- Delta/phase outputs, relevant specs, contracts, and verification artifacts.
- Owning delta/phase/DR context when this is post-implementation conformance work.
- Ceremony/policy posture from generated agent docs.

Process:

1. Determine audit mode and owner:
   - `conformance` for post-implementation audit tied to a delta
   - `discovery` for backfill or existing-code investigation
   - identify the owning `DE-XXX` when this audit belongs to delta work
2. Create or update the `AUD-*` artefact before treating the audit as closure-grade work:
   - if no audit exists yet, create one with the real CLI surface:
     - `uv run spec-driver create audit "<title>" --mode conformance --delta DE-XXX ...`
     - `uv run spec-driver create audit "<title>" --mode discovery ...`
   - use `--spec`, `--prod`, and `--code-scope` so the audit scope is explicit
   - for qualifying delta work, standalone `AUD-*` is required; do not treat loose notes as a substitute
3. Move the audit through the canonical lifecycle:
   - `draft` while scaffolding scope/evidence
   - `in-progress` while findings and reconciliation are underway
   - `completed` only after every finding has a valid disposition and the required reconciliation artefacts exist
4. Gather evidence:
   - run the tests/checks required by the delta, phase sheet, specs, and verification plan
   - inspect generated contracts or observed behavior where relevant
   - update verification coverage blocks using valid statuses only:
     - `planned`, `in-progress`, `verified`, `failed`, `blocked`
5. Record findings in the audit artefact, not just in prose:
   - every finding needs an `outcome`
   - every finding also needs a machine-checkable inline `disposition`
   - use structured refs and optional `drift_refs` where needed
6. Disposition every finding explicitly:
   - `aligned` when the observed behavior is already correct and no follow-up is needed
   - `spec_patch` or `revision` when authoritative specs must be reconciled now
   - `follow_up_delta` or `follow_up_backlog` when owned future work is the correct route
   - `tolerated_drift` only when posture allows explicit unresolved drift with rationale
   - do not leave closure-grade findings undispositioned
7. Route every non-aligned finding back into authoritative specs in this order:
   - choose `spec_patch` when the current owning spec is still the right authority surface and the fix stays inside that scope
   - choose `revision` when authority, requirement ownership, or cross-spec lineage must move, or when a simple patch would hide why the truth changed
   - create a new spec only inside the `revision` branch when revision analysis shows no existing spec can own the reconciled truth cleanly without overlap or competing truths
   - keep "new spec" out of the audit disposition vocabulary; the audit still records `revision`, and the revision explains why a new spec boundary is justified
8. Resist easy escapes before routing a finding away from immediate reconciliation:
   - do not pick `follow_up_*` just because spec authorship feels large or inconvenient
   - do not pick `revision` when an in-scope spec patch is sufficient
   - do not create a new spec because the existing spec is messy; create one only when the authority boundary itself is wrong
   - if the correct route is ambiguous after reading the owning specs and revision context, stop and `/consult`
9. Reconcile before closure handoff:
   - patch owning specs when audit evidence shows they are wrong or stale
   - create revisions when authority must move or when the audit justifies a new spec boundary
   - when revision work justifies a new spec, reuse the existing `spec-driver create spec` path and update the legacy specs/revision links so authority is explicit
   - create follow-up deltas or backlog items only when immediate reconciliation is not the right path
   - keep the audit as the closure-grade record; optional drift-ledger linkage does not replace disposition
10. Run the repository reconciliation commands:

- `uv run spec-driver sync`
- `uv run spec-driver validate`

11. Decide the handoff:

- if this is qualifying conformance work and any blocking finding remains unresolved, do not hand off to `/close-change`
- if findings route to follow-up work or tolerated drift with material tradeoffs, `/consult` before normalizing around them
- hand off to `/close-change` only after the audit artefact, owning specs, and follow-up refs tell a coherent closure story

Outcomes:

- Audit evidence is recorded in a canonical `AUD-*` artefact.
- Every finding ends with an explicit, machine-checkable disposition.
- Specs/contracts/follow-up artefacts are reconciled before closure handoff, with an explicit preference order of `spec_patch -> revision -> revision-led new spec`.
- `/close-change` receives work that is actually audit-ready rather than merely test-complete.
