---
id: IMPR-019
name: handover and review orchestration
created: "2026-03-21"
updated: "2026-03-21"
status: in-progress
kind: improvement
---

# Engineering Brief: Workflow Orchestration and Persistent Review for spec-driver

## Objective

Design a workflow/orchestration layer for spec-driver that reduces manual handover work and repeated review bootstrap cost, while preserving the existing artifact model and operator-facing workflow.

The intent is **not** to replace DE/IP/phases/notes with a new system. The intent is to add a small machine-readable control plane that allows the CLI to:

* detect workflow state reliably
* emit structured handovers at phase boundaries
* support persistent reviewer sessions across multiple rounds
* recover cleanly from agent/session death
* amortize reviewer bootstrap effort rather than paying it repeatedly
* remain flexible enough for different users, agents, and workflow preferences

## Non-goals

Do not design:

* a general-purpose workflow engine unrelated to spec-driver artifacts
* a transcript-centric agent memory system
* a subagent framework that assumes fresh agents for every review round
* a breaking redesign of DE/IP/phase schemas
* a system that requires operators to abandon readable markdown artifacts

## Existing surfaces to preserve

The design must respect the current workflow-facing artifacts and their roles:

* `DE-*.md` as design/intent authority
* `IP-*.md` as implementation/phase/verification authority
* `phases/*.md` as per-phase execution records and natural handover boundaries
* `notes.md` as human-readable execution narrative and onboarding surface
* continuation skill behavior as the current transition mechanism to update notes and emit next-step guidance

The new functionality should be **additive**, not substitutive.

## Core problem decomposition

There are two related but distinct problems:

### 1. Handover resilience

This is the problem of making phase transitions and agent-to-agent continuation reliable and machine-readable.

Structured handoff solves:

* operator copy-paste burden
* deterministic next-agent priming
* lifecycle automation
* recovery from session loss

### 2. Review bootstrap amortization

This is the problem of avoiding repeated expensive reviewer setup.

Persistent reviewer support must solve:

* reusing prior artifact understanding
* preserving reviewed dependency surfaces
* preserving invariants and prior findings
* resuming productive review without cold-starting each round

Structured handoff alone does **not** solve this second problem.

## Design principles

### Additive change only

Prefer new sibling artifacts and optional bridge sections over mutation of existing schemas.

### Human-readable where humans read

Keep prose workflow artifacts readable and useful.

### Separate machine state from prose

Operational state should live in dedicated `.yaml` files where possible.

### File-based control plane

The orchestration layer should be driven by predictable files that are easy to validate, inspect, and watch with fs events.

### Phase boundaries are the natural workflow boundary

Phase completion or transition should be the default trigger for handoff emission and orchestration behavior.

### Persistent review is artifact-attached

A reviewer session should conceptually belong to the artifact under review, not to a single review invocation.

### Rebuildable state over process-only state

A live session is an optimization. Durable workflow/review state on disk is the real source of continuity.

## Format and artifact constraints

### Preferred formats

* YAML for workflow state and handoff artifacts
* TOML for user/config policy in `.spec-driver/workflow.toml`
* markdown with fenced YAML only where prose and machine-readable state need to coexist

### Preferred placement

Use a dedicated workflow directory inside the delta bundle for machine-facing artifacts.

Reasoning:

* easier file watching
* atomic file rewrites
* easier schema validation
* avoids brittle parsing of mutable markdown
* clearer ownership boundaries

## Key invariants to preserve

The scoped design must preserve the following:

### Artifact authority invariant

DE/IP/phases remain the authoritative design/planning/execution artifacts. Workflow files must not silently supersede them semantically.

### Readability invariant

Operators must still be able to understand task status from ordinary project artifacts without reading opaque machine state.

### Determinism invariant

The CLI should be able to determine current workflow state from the control-plane files without scraping freeform prose.

### Recovery invariant

Loss of a live agent/session must not destroy the ability to continue the workflow with bounded re-bootstrap cost.

### Review continuity invariant

Multi-round review must preserve findings, invariants, and prior understanding across rounds.

### Bounded-context invariant

The design must avoid transcript replay as the primary continuity mechanism.

### Compatibility invariant

Existing deltas should remain usable without mandatory migration of DE/IP schemas.

## Proposed architectural direction

The orchestration design should be built around three layers:

### 1. Existing markdown workflow artifacts

These remain the primary human-facing workflow surfaces.

### 2. Workflow control-plane artifacts

New YAML files under `workflow/` provide machine-readable orchestration state.

### 3. CLI orchestration commands

New spec-driver commands manage:

* handoff emission
* reviewer priming
* reviewer resumption
* approval/change-request transitions
* session reconciliation/status

## Reviewer persistence model

The design should support two-tier persistence:

### Tier 1: live session persistence

A tmux/jail-backed reviewer session may remain alive across multiple rounds.

### Tier 2: artifact persistence

Reviewer understanding must also be persisted in structured files so that:

* reviewer sessions can be recreated
* prior review work is not lost
* the CLI can reason about review state without scraping transcripts

Tier 2 is the critical requirement.

## Required conceptual separation

The design should clearly distinguish these artifact types:

### Workflow state

Current orchestration truth: current phase, active role, workflow status, pointers.

### Handoff state

Most recent phase-boundary transition payload.

### Review bootstrap cache

Persisted understanding required to make review efficient.

### Review findings ledger

Stable findings across review rounds, with identifiers and statuses.

### Runtime session map

Ephemeral mapping of roles to tmux/jail sessions.

These should not be collapsed into one monolithic file.

## Tradeoffs to handle explicitly

The local agent should scope and design with the following tradeoffs in mind.

### File separation vs embedded state

Separate YAML files are better for automation, validation, and event watching.
Embedded YAML in markdown is better where the state exists mainly to help humans navigate related machine artifacts.

The expected design bias is:

* separate files for operational state
* embedded bridge blocks only where they improve usability

### Reviewer warmth vs cache staleness

A persistent reviewer is efficient only if its cached understanding remains valid.
The design should include invalidation/reprime conditions such as:

* major scope drift
* dependency surface expansion
* rebase or substantial code movement
* phase boundary crossing into materially different territory

### Strict schema vs operator flexibility

Machine-facing workflow artifacts should be strictly schema-validated.
Human prose should remain flexible.

### Minimalism vs usefulness

The control plane should stay small, but it must contain enough state to support:

* deterministic continuation
* review continuity
* recovery
* status display
* event-driven orchestration

## Expected outputs from the local agent

The local agent should scope and design:

### 1. Artifact schemas

Define and validate the new workflow artifacts, minimally:

* workflow state
* current handoff
* review index / bootstrap cache
* review findings
* session map

### 2. CLI surface

Propose command semantics for:

* handoff emission
* review priming
* review resumption
* review approval / request changes
* workflow status

### 3. Continuation skill refit

Describe how continuation should evolve from:

* updating notes and printing a prompt

to:

* updating notes
* writing structured handoff state
* optionally rendering a continuation prompt from structured state

### 4. Optional bridge sections

Propose any minimal fenced YAML bridge sections in:

* `notes.md`
* phase sheets

only where they add clear value.

### 5. Lifecycle/invalidation rules

Define when reviewer state is:

* warm
* stale
* invalid
* reusable

### 6. Migration/compatibility strategy

Explain how to introduce the new functionality without breaking existing workflows or requiring immediate artifact migration.

## Evaluation criteria

A good design should satisfy these tests:

* Can a phase completion emit a structured handoff without requiring operator copy-paste?
* Can the CLI resume the correct next role deterministically?
* Can a reviewer be resumed for round 3 without reconstructing rounds 1 and 2 from transcripts?
* Can a dead reviewer session be recreated without a true cold start?
* Can status be inspected from a small set of predictable files?
* Are DE/IP/phase schemas left largely untouched?
* Does `notes.md` remain readable and useful?

## Implementation posture

The requested work is **scoping and design**, not a broad speculative redesign.

The local agent should:

* work from the current spec-driver artifact model
* prefer the smallest viable additive design
* identify where exact schema hooks belong
* make explicit any assumptions about existing CLI/skill infrastructure
* call out any places where continuation, notes structure, or phase conventions impose constraints

## Final design heuristic

The system should feel like:

* existing spec-driver workflow artifacts remain central
* the CLI gains enough structured state to automate transitions
* reviewer persistence becomes genuinely economical, not merely recoverable
* the control plane is visible, inspectable, and easy to reason about

It should **not** feel like a second workflow system bolted on beside the first.

---

see also: `./schema.md`
