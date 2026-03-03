# SpecDriver Workflow Map (Primitives + Ceremony Modes)

Spec-driver is a set of loosely connected primitives. You can activate more of
the “full system” as a project matures, without declaring "process bankruptcy".

This document describes:
- the **full system** (what exists, end-to-end)
- three illustrative **ceremony modes** (Pioneer / Settler / Town Planner)
- allowable **permutations** (what sequences are valid)
- the **closure contract** (what must be updated when work completes)

The aim is that an agent can read this once and then operate without forensic
repo archaeology.

## 1. The Full System (end-to-end)

Layers (loosely ordered):

1) **Policy layer** (intent, governance)
   - ADRs (architectural decisions)
   - Standards and policies (when adopted)

2) **Backlog layer** (work intake)
   - Issues / Improvements / Problems / Risks
   - Kanban cards (e.g. `T123-something.md`) for operational expediency

3) **Specifications layer** (evergreen intent + constraints)
   - Product specs (PROD-*)
   - Tech specs (SPEC-*) — includes unit vs assembly classification
   - Requirements may live as:
     - requirements embedded inline in a spec header file
     - discrete requirement files inside a spec bundle, or
     - backlog items (issue/improvement/etc) with their own lifecycle

4) **Delivery layer** (change execution)
   - Deltas (DE-*) describing an intended change, scope, and verification strategy
   - Design revisions (DR-*) when design needs its own record
   - Implementation plans / phases (IP-*) when execution is non-trivial

5) **Evidence layer** (what happened / what is true)
   - Audits and verification artefacts
   - Contracts corpus (generated from code) as observed truth (see §3)

Kanban cards are an escape hatch: they’re a valid change-capture mechanism when
ceremony is intentionally kept low.

## 2. Ceremony Modes (canonical forms)

These are defaults for agent workflows and documentation, not hard constraints.
People can always do what they want.

### 2.1 Pioneer (low ceremony)

Goal: ship and learn. Capture change, but avoid process overhead.

Activated primitives:
- Kanban cards (`T123-*.md`) for most work (manual lifecycle; links are often just markdown)
- ADRs as MVP policy (when a decision matters)
- Optional specs (usually assembly specs only, when helpful)

Typical flow:
- Card → implement → (optional) add an ADR → done

Notes:
- Deltas/IPs are intentionally not the default here.
- Backlog metadata linkage is optional and often manual.

### 2.2 Settler (medium ceremony, default)

Goal: delta-first delivery with selective evergreen specs and flexible evidence capture.

Activated primitives:
- Backlog items (issues/improvements/problems/risks) for intake
- Deltas for intentional work and repeatable closure
- Specs (assembly specs are the typical first target; unit specs optional/derived)
- Audits for discovery/backfill or conformance (both allowed; discovery/backfill is common in legacy work)

Typical flows:
- Backlog item → Delta → (optional) DR → (optional) IP/phases → implement → closure updates (see §4)
- Audit (discovery/backfill) → spec/req updates → follow-up delta(s) as needed

Notes:
- Deltas do not “link to cards”. Cards are typically used *instead of* the
  delta→IP flow.
- When a project reaches for deltas, it will usually have adopted more of the
  policy layer (standards/policies), but it’s not mandatory.

### 2.3 Town Planner (high ceremony)

Goal: predictable governance + evidence discipline + long-lived evergreen specs.

Activated primitives:
- Full policy layer (ADRs + standards + policies)
- Specs and requirement files as the main source of intent
- Revisions for coordinated spec changes
- Deltas/IP/phases as the primary delivery mechanism
- Audits that may project evidence back into coverage (skill-dependent)

Typical flows:
- Revision → spec/req updates → delta(s) → DR → IP/phases → implementation → audit/conformance → closure updates

## 3. Truth model (contracts vs specs)

- Generated contracts (e.g. `.contracts/**`) are the canonical record of
  **observed truth** (“what the code exposes”).
- Specs express **intent and constraints**; they should not become competing
  “authoritative copies” of signatures/types when those can be generated from
  code.
- Assembly specs can constrain interfaces (compat/invariants/expected shapes),
  but those constraints should be framed as requirements that can be validated
  against observed contracts/code.

## 4. Closure contract (what gets updated when work is done)

When a delta (or equivalent work item) is completed, update the owning
record(s) for the requirements/work-items it targets.

Key rule: **closure updates the owning record**, which depends on where the
requirement lives.

Examples:
- If the change is “close an Issue”: update the Issue
  frontmatter/status/evidence.
- If the change is “deliver an Improvement”: update the Improvement
  frontmatter/status/evidence.
- If the change is “implement a requirement file inside a spec bundle”: update
  that requirement file (and any verification refs).
- If the change touches a spec’s coverage/evidence block by convention: update
  that block consistently (where used).

In Pioneer mode, this may be entirely manual and recorded in card markdown (if
there even is a relevant backlog item). In Settler/Town Planner modes, agent
workflows should prefer structured updates (frontmatter + coverage blocks)
where the project has adopted them.

### 4.1 Coverage prerequisite for `complete delta`

Before running `uv run spec-driver complete delta DE-XXX`, each requirement in
`delta.applies_to.requirements` must be present in the parent spec
`supekku:verification.coverage@v1` block with `status: verified`.

If coverage is missing or not verified, completion hard-fails unless bypassed
with `--force` (or disabled globally via `SPEC_DRIVER_ENFORCE_COVERAGE=false`,
non-canonical path).

## 5. Allowable permutations (non-exhaustive)

Valid sequences (choose based on ceremony):
- Card → implementation → done (YOLO)
- Card → design doc -> implementation plan → done (BYO conventions for design
  docs & plans)
- Backlog item → delta → implementation → closure updates (Settler/Town
  Planner)
- Spec/requirement update → delta → implementation → closure updates
  (Settler/Town Planner - 'eager specifications')
- Revision → spec/req updates → delta(s) → implementation → closure updates
  (Town Planner - 'accurate specifications')
- Audit (discovery/backfill) → spec/req updates (common in legacy Settler)
- Audit (conformance) → evidence/coverage updates (Town Planner default;
  allowed anywhere via skill choice)

## 6. Agent entry checklist (token-cheap)

If you’re an agent starting work:

1) Identify which ceremony mode the repo/project is operating in right now (Pioneer/Settler/Town Planner).
2) Identify the owning record for the work:
   - card? backlog item? spec requirement file? revision?
3) Prefer closing work by updating the owning record (frontmatter/status/evidence) rather than writing “floating” narrative.
4) If generating contracts/syncing, treat contracts as observed truth and specs as intent/constraints.

## 7. Skills and command suites (future direction)

This repo should expose provider-neutral, composable skills that map to the
primitives above (create/clarify/complete delta, run audit, backfill specs,
next phase). Provider-specific command wrappers (Claude/Codex/etc.) should be
thin adapters over those canonical skills.
