---
id: ADR-004
title: 'ADR-004: canonical core workflow loop'
status: accepted
created: '2026-03-06'
updated: '2026-03-06'
reviewed: '2026-03-06'
owners: [david]
supersedes: []
superseded_by: []
policies: []
specs: [PROD-002, PROD-008, PROD-009, PROD-011, PROD-016]
requirements: []
deltas: [DE-047]
revisions: []
audits: []
related_decisions: [ADR-001, ADR-003]
related_policies: []
tags: [workflow, doctrine, lifecycle]
summary: Define the single canonical spec-driver workflow loop, distinguish supported variants from canon, and reject spec-first
  aspirational doctrine as the default for code-changing work.
---

# ADR-004: canonical core workflow loop

## Context

Spec-driver currently describes its workflow in several partially conflicting ways.
Some docs correctly describe a delta-first loop with audit and reconciliation.
Others imply a spec-first workflow in which specs are edited up front and code is
then brought into alignment. The result is persistent doctrinal murk.

Today the repo already contains the pieces of the intended answer:

- `.spec-driver/agents/workflow.md` defines the canonical default narrative as
  `delta -> DR -> IP -> phase sheet(s) -> implement -> audit -> revision -> patch specs -> close`
- `mem.pattern.spec-driver.core-loop` describes the full loop as
  `capture -> delta -> implement -> audit/contracts -> revision -> spec reconcile -> close`
- `PROD-008` states that specs and their coverage blocks are the authoritative
  long-lived record of requirement lifecycle state
- `.spec-driver/about/lifecycle.md` shows the current implemented system already
  distinguishes requirement lifecycle from coverage status and aggregates
  verification evidence from specs, deltas, plans, and audits into a derived registry
- `PROD-009` introduces an overlay model that can easily be read as “newest evidence wins”
- `PROD-011` overstates workflow plurality by presenting delta-first, spec-first,
  and backlog-first as supported peers
- `PROD-016` correctly frames ceremony/configuration as shaping posture and
  enforcement strength, not as defining multiple contradictory truths

We need one authoritative doctrine that:

- states the golden path clearly
- distinguishes canon from concessions
- explains how lifecycle/verification mitigates some aspirational-spec risk
- preserves flexibility around revisions without flattening the conceptual model
- gives DE-047 a single reference point for repo-wide reconciliation

This framework is intentionally heavy in one place to eliminate heavier waste elsewhere:

- repeated speculative research into a codebase before and during implementation
- specs written from a narrow design-time snapshot that becomes stale quickly
- duplicated agent effort re-learning system truth after code changes
- low-trust specifications that are too inaccurate to support architecture work

The trade is explicit:

- pay for structured change records once, during execution
- use contracts and audits to recover observed truth cheaply and deterministically
- reconcile specs from those findings
- reduce future research cost because the documentary record becomes trustworthy

Spec-driver therefore chooses heavier execution records over repeated rediscovery.

## Decision

### 1. Canonical loop

The canonical spec-driver loop for code-changing work is:

```text
[optional capture or revision trigger]
-> delta
   -> [recommended DR]
   -> [optional IP
       -> phase-01 (created just-in-time)
       -> implement phase-01
       -> phase-02..N (each created just-in-time and interleaved with execution)
       -> implement phase-02..N
      ]
   -> implement remaining non-phased work
-> generate contracts and/or audit
-> derive or refine revision(s) from findings
-> reconcile specs
-> close
```

Short form:

`delta-first implementation, observation, explicit reconciliation, closure`

This is the canonical doctrine for code-changing work.

### 2. Observation precedes reconciliation

For code-changing work, specs SHOULD NOT be edited aspirationally in advance to
describe future technical reality as if it already exists.

Instead:

- the delta declares and scopes intended change
- the DR is usually the main design-bearing artefact inside the delta bundle
- the IP and phase sheets shape execution when needed
- phase sheets are canonically created just-in-time and interleaved with execution,
  not all scaffolded up front
- implementation changes the system
- generated contracts and audits establish observed truth
- revision artefacts capture requirement/spec changes and reconciliation intent
- specs are updated to reflect the accepted reconciled outcome
- closure confirms owning records are coherent

This is the discipline that prevents drift into spec-first waterfall.

### 3. Specs remain authoritative, but authority is maintained by explicit reconciliation

Specs remain the durable authoritative record of accepted behaviour and
requirements. That authority is maintained by explicit reconciliation after
implementation and observation, not by premature assertion of future truth.

Observed truth does not silently replace spec truth. It triggers reconciliation:

- audits and contracts show what is
- revisions describe what must change in the documentary record
- specs become authoritative again once reconciled

### 4. Requirements lifecycle and verification partially mitigate aspirational-spec risk

Requirement lifecycle and verification coverage mitigate this risk, especially
for product-level work.

Coverage and lifecycle state can distinguish, at requirement granularity:

- what is merely `planned`
- what is currently `in-progress`
- what is `verified`
- what has drifted or failed verification

This allows a spec to contain already-satisfied, planned, and newly-asserted
requirements without pretending they are all equally implemented.

That mitigation is often sufficient for PROD specs, where intent and staged
delivery are part of the artefact's job.

It is weaker for TECH specs, where whole-system coherence, structure,
interfaces, and design consistency matter more than per-requirement granularity.
For TECH specs, aspirational editing is therefore more dangerous and generally
not advised.

### 5. Product and technical specs have different tolerance for forward intent

The canonical doctrine applies to both PROD and TECH specs, but not with equal strictness.

- **PROD specs** may reasonably carry more planned or newly-accepted intent
  before all implementation is complete, provided coverage/lifecycle clearly
  distinguishes planned from verified reality.
- **TECH specs** SHOULD usually be reconciled from observed implementation,
  contracts, and audit findings after code changes, because technical coherence
  is often a property of the whole design rather than a checklist of isolated
  requirements.

Any workflow description that does not distinguish these postures is incomplete.

### 6. Revisions are flexible inputs and reconciliation artefacts

Revisions are not tied to a single moment in the loop.

Valid patterns include:

- revision created first as an input to a delta, then held unmerged until later
- revision merged before delta execution when accepted intent must be recorded early
- additional revision(s) created or updated after audit/contracts findings
- one revision feeding several outcomes: spec updates, follow-up delta, backlog items,
  or further revision work

Doctrine does not require one revision timing pattern.
Doctrine requires explicit reconciliation and forbids misleadingly advancing
technical specs ahead of observed truth for ordinary code-changing work.

### 7. Supported variants are concessions, not co-equal canon

Spec-driver supports several valid workflow variants, but they are not doctrinally equal.

Supported variants:

- **Optional capture/backlog-first entry**
  `backlog item -> delta -> implement -> audit/contracts -> revision/spec reconcile -> close`
- **Revision-first**
  `revision -> delta -> implement -> audit/contracts -> reconcile -> close`
- **Reduced-ceremony delta flow**
  `delta -> implement -> reconcile -> close`
- **Kanban/card-only low-ceremony flow**
  `card -> implement -> done`

These are concessions for capture, governance, maturity, or low-ceremony work.
They do not redefine canon.

DRs, IPs, and phase sheets are not maturity badges. They are execution-shaping
artefacts. Their use should be driven primarily by significance, complexity, and
coordination risk. When deltas are active, those artefacts normally live inside
the delta bundle. When deltas are not active, equivalent design/planning records
may live elsewhere.

### 8. Spec-first aspirational doctrine is not canonical for code-changing work

The following is explicitly not canonical doctrine for code-changing work:

`spec -> delta -> implement -> done`

when that means:

- the spec is edited first to describe future technical reality
- implementation is framed as merely catching the code up to that edited spec
- the explicit observation and reconciliation steps are skipped or minimized

This may occasionally be tolerated for early ideation or product framing, but it
MUST NOT be taught as the default golden path, especially for TECH specs.

### 9. Ceremony shapes strictness, not truth

Ceremony mode, configuration, and skills govern:

- how much scaffolding is expected
- when DR/IP/phases/audits are recommended or required
- how strongly agents steer users back toward the canonical path

They do not create multiple truths about the workflow.
Configuration changes posture and enforcement strength. It does not create
multiple canonical doctrines.

### 10. Closure requires owning-record reconciliation

Work is not complete merely because code exists or tests pass.

Closure requires reconciliation of the owning records:

- revisions recorded where needed
- spec coverage/lifecycle updated
- delta completion aligned with reconciled state
- follow-up backlog or delta work created where unresolved drift remains

“Implemented now, fix the specs later” is drift, not closure.

## Consequences

### Positive

- Gives the repo one authoritative answer to “what is the golden path?”
- Distinguishes flexibility from doctrinal equivalence.
- Preserves legitimate lifecycle nuance for PROD specs without normalizing
  aspirational TECH-spec editing.
- Gives DE-047 a stable anchor for revising contradictory docs, memories, and specs.
- Makes revision timing flexible without making the conceptual model muddy.
- Reduces long-run research waste by making audits, contracts, revisions, phase
  notes, and commit history the main inputs to trustworthy spec maintenance.
- Produces more accurate and more useful specs for holistic architecture work,
  which in turn reduces the need for repeated exploratory research.

### Negative

- Some existing docs and product specs will need revision because they currently
  imply or teach spec-first sequencing.
- The doctrine is stricter than a simple linear workflow slogan.
- Users may find the difference between tolerated practice and canonical practice uncomfortable.

### Neutral

- This ADR does not require strict runtime enforcement today.
- This ADR does not forbid revision-first or low-ceremony workflows.
- This ADR establishes canon first; enforcement remains a separate concern for
  workflow config, skills, and command gates.
- The framework remains heavier than ad-hoc workflows during execution, by design.

## Verification

- `.spec-driver/agents/workflow.md` and related generated guidance describe the
  canonical loop in ADR-consistent terms.
- Core overview docs do not teach spec-first sequencing as the default for
  code-changing work.
- `PROD-008`, `PROD-009`, `PROD-011`, and `PROD-016` are revised to align with
  this doctrine and to distinguish canon from concession.
- DE-047 closure links the resulting REs/patches back to this ADR.

## References

- `drift/DL-047-spec-corpus-reconciliation.md`
- `.spec-driver/agents/workflow.md`
- `.spec-driver/about/lifecycle.md`
- `.spec-driver/about/README.md`
- `.spec-driver/about/glossary.md`
- `.spec-driver/about/processes.md`
- `specify/product/PROD-002/PROD-002.md`
- `specify/product/PROD-008/PROD-008.md`
- `specify/product/PROD-009/PROD-009.md`
- `specify/product/PROD-011/PROD-011.md`
- `specify/product/PROD-016/PROD-016.md`
- `specify/decisions/ADR-001-use-spec-driver-to-build-spec-driver.md`
- `specify/decisions/ADR-003-separate_unit_and_assembly_specs.md`
- `supekku/memories/mem.pattern.spec-driver.core-loop.md`
