---
id: PROD-009
slug: requirement-lifecycle-semantics
name: Requirement Lifecycle Semantics
created: '2025-11-03'
updated: '2025-11-03'
status: draft
kind: prod
aliases: []
relations: []
guiding_principles:
  - Requirements always carry an explicit lifecycle status even before evidence exists.
  - Later evidence overlays earlier declarations but never silently discards them.
  - Validation should guide teams back to coherence with warnings before blocking work.
assumptions:
  - Some legacy requirements will be asserted without receipts.
  - Delta and audit metadata include timestamps we can compare reliably.
  - Teams will capture priority/category metadata to drive backlogs.
---

# PROD-009 – Requirement Lifecycle Semantics

```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: PROD-009
requirements:
  primary:
    - PROD-009.FR-001
    - PROD-009.FR-002
    - PROD-009.FR-003
    - PROD-009.NF-001
  collaborators:
    - PROD-008.FR-001
    - PROD-008.FR-002
    - SPEC-122.FR-003
interactions:
  - type: aligns_with
    spec: PROD-008
    summary: Lifecycle semantics build on the coverage contract defined in PROD-008.
  - type: depends_on
    spec: SPEC-122
    summary: Requires registry lifecycle infrastructure to project effective status.
```

```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: PROD-009
capabilities:
  - id: lifecycle-semantics
    name: Lifecycle Semantics and Evidence Overlay
    responsibilities:
      - lifecycle-baseline-status
      - lifecycle-evidence-overlay
      - lifecycle-discrepancy-guidance
    requirements:
      - PROD-009.FR-001
      - PROD-009.FR-002
      - PROD-009.FR-003
      - PROD-009.NF-001
    summary: >-
      Defines how baseline statuses declared in specs combine with evidence from
      deltas and audits, and how the tooling guides teams back to coherence when
      those signals diverge.
    success_criteria:
      - Legacy assertions, delta completions, and audits appear with clear provenance.
      - Registry projections always reflect the most recent authoritative signal.
      - Validation surfaces actionable warnings whenever overlays disagree.
```

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: PROD-009
entries:
  - artefact: VH-330
    kind: VH
    requirement: PROD-009.FR-001
    status: planned
    notes: Stakeholder workshop validating lifecycle state vocabulary and baseline statuses.
  - artefact: VA-421
    kind: VA
    requirement: PROD-009.FR-002
    status: planned
    notes: Dry-run of overlay precedence scenarios across spec, delta, and audit inputs.
  - artefact: VT-940
    kind: VT
    requirement: PROD-009.FR-003
    status: planned
    notes: Automated validator tests exercising discrepancy warnings and severity rules.
```

## 1. Intent & Summary
- **Problem / Purpose**: Teams need to declare current reality for legacy systems without receipts while still trusting future overlays from deltas and audits.
- **Value Signals**: Every requirement shows an explicit lifecycle status with provenance; discrepancies between artefacts raise actionable warnings instead of silently drifting.
- **Guiding Principles**: Specs own the baseline, evidence overlays never delete history, and validation shepherds humans back to coherence.
- **Change History**: Drafted alongside PROD-008 lifecycle contract (2025-11-03);
  implementation tracked via DE-007.

## 2. Stakeholders & Journeys
- **Personas / Actors**:
  - *Spec authors / system owners* asserting existing behaviour.
  - *Implementation agents* closing deltas and updating evidence.
  - *Auditors / reviewers* capturing observational truth.
  - *Product owners* prioritising unimplemented requirements.
- **Primary Journeys / Flows**:
  1. **Baseline assertion** – Given a requirement exists in production, when the author marks it `status: asserted` in the spec coverage block, then the registry reports it as “asserted (spec)” instead of “unknown”.
  2. **Evidence overlay** – Given a delta closes, when it records coverage `status: verified` with timestamp, then the registry effective status becomes “verified (delta)” unless a fresher audit disagrees.
  3. **Observation drift** – Given an audit records `status: failed` after that delta, when validation runs, then it raises a warning and treats the audit status as authoritative until remediation.
  4. **Prioritised backlog** – Given an unimplemented requirement, when priority/category metadata is set, then list and reporting features surface it for planning.
- **Edge Cases & Non-goals**:
  - Do not attempt automatic conflict resolution; humans must reconcile.
  - Experiments or spikes outside the registry remain out of scope.
  - Simultaneous updates within a narrow window trigger review warnings rather than hard choices.

## 3. Responsibilities & Requirements

### Capability Overview
The lifecycle-semantics capability ensures every requirement has a baseline status, overlays that respect recency and evidence strength, provenance for the effective state, and guidance whenever states diverge.

### Functional Requirements
- **FR-001**: Specs MUST allow authors to declare baseline lifecycle statuses (`planned`, `asserted`, `legacy_verified`, `deprecated`) directly in coverage entries.
  *Verification*: VH-330 – Stakeholder walkthrough confirming spec-driven status updates.
- **FR-002**: The lifecycle engine MUST overlay statuses from deltas and audits using timestamp precedence, preferring audits over deltas when recorded at the same time.
  *Verification*: VA-421 – Validation dry run covering precedence scenarios.
- **FR-003**: Validation MUST emit corrective warnings when overlays disagree and keep humans informed until a new delta or audit resolves the conflict.
  *Verification*: VT-940 – Automated validator tests exercising discrepancy rules.

### Non-Functional Requirements
- **NF-001**: Lifecycle projections MUST expose provenance (source artefact, timestamp, actor) for the effective status.
  *Measurement*: VT-940 – Snapshot inspection confirms provenance fields present.
- **NF-002**: Warning messages SHOULD be actionable within one hop (point to artefacts and remediation) and default to warning severity rather than errors.
  *Measurement*: VA-421 – Expert review of warning copy across conflict scenarios.

### Success Metrics / Signals
- ≥95% of tracked requirements carry explicit baseline statuses post-adoption.
- ≤10% of lifecycle warnings stay unresolved longer than one business day.
- Agent satisfaction survey reports ≥4/5 clarity on lifecycle provenance and warnings.

## 4. Solution Outline
- **User Experience / Outcomes**: Spec editors declare baseline state; delta completion and audit ingestion update overlays; UI/CLI displays “verified (audit AUD-021 · 2025-11-01)” vs “asserted (spec PROD-009 · 2025-11-03)” so humans understand context.
- **Status Model**: Baseline statuses from spec; delta statuses (`in-progress`, `implemented`, `verified`); audit statuses (`verified`, `failed`, `blocked`). Effective status = newest timestamp; if timestamps match, audits outrank deltas; otherwise delta outranks older audit.
- **Metadata & Priorities**: Coverage entries may include optional `priority`, `category`, and `sequence` fields; registry and reporting surface them for backlog work.
- **Warning Heuristics**: Spec asserts verified with no evidence for 30 days → warning; delta verified but newer audit failed → warning until remediation; coverage missing for referenced requirement → error (enforced by DE-007).

## 5. Behaviour & Scenarios
- **Primary Flows**:
  - *Baseline declaration*: Author updates coverage → registry records `asserted (spec)` → no warnings unless conflicting overlays arrive.
  - *Delta overlay*: Delta completion updates coverage `verified (delta)` → validation clears related warnings.
  - *Audit overlay*: Audit reports `failed` → effective status becomes `failed (audit)` → warning referencing delta and audit.
  - *Resolution*: New delta brings behaviour back → status returns to `verified (delta)` → warning cleared.
- **Error Handling / Guards**: Simultaneous updates (within 5 minutes) keep both entries, choose deterministic winner, emit review warning; missing priority metadata yields informational notice only.

## 6. Quality & Verification
- **Testing Strategy**: Extend registry tests for overlay precedence and provenance (VT-940); CLI integration tests for warning messaging (VA-421); manual workshop confirms lifecycle matrix (VH-330).
- **Research / Validation**: Interview three teams tackling legacy systems to confirm workflow clarity; capture insights in backlog entry.
- **Observability & Analysis**: Track count and age of lifecycle warnings in validation dashboards; alert if unresolved warnings >24h.
- **Security & Compliance**: Provenance metadata must not leak sensitive audit details—only IDs, timestamps, and outcome summaries.
- **Acceptance Gates**: Lifecycle projections expose provenance, warnings exercised end-to-end, documentation updated for agents.

## 7. Backlog Hooks & Dependencies
- **Related Specs / PROD**: PROD-008 (coverage contract), SPEC-122 (requirements registry).
- **Risks & Mitigations**:
  - *RISK-LIFE-001*: Teams ignore warnings → Add severity levels and dashboards (ISSUE-420).
  - *RISK-LIFE-002*: Legacy assertions never receive evidence → Schedule quarterly review ritual (PROB-140).
- **Known Gaps / Debt**: ISSUE-421 – UI surfacing of lifecycle provenance; ISSUE-422 – Optional custom precedence rules per requirement.
- **Open Decisions / Questions**:
  - Should we introduce an `acknowledged_drift` status for long-running gaps? *(Owner: lifecycle-team, Due: 2025-11-14)*
  - Do we allow per-requirement override of precedence rules? *(Owner: product, Due: 2025-11-21)*


## Appendices (Optional)
- Glossary, detailed research, extended API examples, migration history, etc.
