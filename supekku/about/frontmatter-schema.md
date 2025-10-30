---
id: NOTE-spec-frontmatter-schema
slug: spec-frontmatter-schema
name: Spec Frontmatter Schema
created: 2024-06-08
updated: 2024-06-08
status: draft
kind: note
aliases:
  - Spec Schema
  - Frontmatter Schema for Specs
---

# Spec Frontmatter Schema

This note proposes a shared YAML frontmatter contract for every structured artefact (specifications, requirements, plans, revisions, etc.). It follows Obsidian conventions so agents, editors, and graph tooling can parse relationships without brittle heuristics.

## Base Fields (all artefacts)

```yaml
---
id: SPEC-001
name: Records, Fields, and Schemas Specification
slug: spec-records-fields-schemas
kind: spec|contract|design_doc|design_revision|requirement|verification|delta|feature|plan|phase|task|research|audit|regression|revision|poc|issue|problem|investigation|standard/policy|standard/technical|adr|risk
status: draft|approved|active|superseded|archived
lifecycle: discovery|design|implementation|verification|maintenance
created: 2024-05-24
updated: 2024-06-08
version: 2
owners:
  - david
auditers:
  - vice-bot
source: doc/specify/tech/SPEC-101.md
summary: >-
  High-level intent statement (1–2 sentences) explaining why this artefact exists.
tags:
  - spec
relations: []
---
```

**Field notes**
- `id` is globally unique. Prefix indicates artefact family (`SPEC-`, `FR-`, `NF-`, `VT-`, `RE-`, `DE-`, `FE-`, etc.).
- `slug` supports file moves: links can resolve `obsidian://vice/spec-records-fields-schemas` style IDs.
- `kind` identifies the document family (spec, requirement, plan, etc.); use `c4_level` metadata for C4 granularity when needed.
- `status` tracks approval state; pair with `lifecycle` to signal where the work currently sits.
- `created` and `updated` follow ISO dates for deterministic parsing.
- `owners` and `auditers` are arrays to support shared responsibility.
- `source` stores canonical path for syncing across folders.
- `summary` keeps a canonical overview for search and agents.
- `tags` are optional but provide a loose discovery surface without inventing new enumerations.
- `relations` is always present, even when empty, to simplify parsing.
- Non-functional requirement IDs use `NF-` so the `FR-`/`NF-` pair stays visually aligned.
- Qualities (e.g. ISO25010 dimensions) stay in the body text alongside the requirements they justify—frontmatter does not attempt to encode them.

## Relationship Taxonomy

Relationship edges are expressed as objects in the `relations` array. Each item has:

```yaml
relations:
  - type: implements
    target: FR-102
    via: VT-102
    annotation: Aligns with authentication requirement
  - type: depends_on
    target: SPEC-004
    strength: strong|weak
  - type: collaborates_with
    target: SPEC-011
  - type: verifies
    target: FR-201
    method: automated|manual|agent
  - type: supersedes
    target: SPEC-001
    effective: 2024-06-01
```

**Supported relation types**
- `implements`: Artefact fulfils a requirement or higher-level spec.
- `verifies`: Artefact provides evidence for a requirement/spec (tests, monitoring, manual checks).
- `depends_on`: Implementation correctness depends on another artefact.
- `collaborates_with`: Peer systems/components with defined interactions.
- `provides_for`: Requirement maps to a feature, plan, or delta delivering the value.
- `supersedes` / `superseded_by`: Track intentional evolution.
- `relates_to`: Looser association for discovery; agents should down-rank these.
- `blocks` / `blocked_by`: Delivery sequencing.
- `decomposes`: Child artefact elaborates the parent (e.g., component spec decomposing a container spec).
- `tracked_by`: Points to issues, regressions, or investigations.

All relation objects accept optional metadata fields (`via`, `method`, `annotation`, `strength`, `effective`). Agents should preserve unknown keys for forward compatibility.

## Product Specifications (`kind: prod`)

```yaml
scope: >-
  Statement of user or market intent.
problems:
  - PROB-012
value_proposition: >-
  Why solving this matters.
guiding_principles:
  - Resolve user pain without sacrificing offline mode.
assumptions:
  - Users are comfortable with 5s sync delays.
hypotheses:
  - id: PROD-020.HYP-01
    statement: Improving sync speed will reduce churn.
    status: proposed|validated|invalid
decisions:
  - id: PROD-020.DEC-01
    summary: Prioritise sync speed over new features this quarter.
product_requirements:
  - code: PROD-020.FR-01
    statement: Sync completes within 5s.
  - code: PROD-020.NF-01
    statement: Sync success rate ≥ 99%.
verification_strategy:
  - research: UX-023
  - metric: sync_latency_p99
```

Product specs mirror tech specs but focus on user outcomes. They link problem statements, product requirements, guiding principles, and hypotheses/decisions so downstream deltas and design revisions honour the intended experience.

## Specifications (`kind: spec`)

```yaml
c4_level: system|container|component|code|interaction (optional)
scope: >-
  Statement of boundaries and responsibilities.
concerns:
  - name: content synchronisation
    description: Maintain canonical content binding state
responsibilities:
  - canonical content binding lifecycle
  - expose schema enforcement operations to other containers
guiding_principles:
  - Maintain block identity end-to-end.
assumptions:
  - Agents will reconcile markdown without manual edits.
hypotheses:
  - id: SPEC-101.HYP-01
    statement: Rich diffing will reduce merge conflicts.
    status: proposed|validated|invalid
decisions:
  - id: SPEC-101.DEC-01
    summary: Adopt optimistic locking for schema updates.
    rationale: Based on RC-010 findings.
constraints:
  - Must preserve block UUIDs during edits
verification_strategy:
  - type: VT-210
    description: End-to-end sync tests remain green
sources:
  - language: go
    identifier: internal/application/services/git
    variants:
      - name: public
        path: contracts/go/git-service-public.md
      - name: internal
        path: contracts/go/git-service-internal.md
  - language: python
    identifier: supekku/scripts/lib/workspace.py
    module: supekku.scripts.lib.workspace
    variants:
      - name: api
        path: contracts/python/workspace-api.md
      - name: implementation
        path: contracts/python/workspace-implementation.md
packages:
  - internal/application/services/git  # Legacy field for Go compatibility
```

**Multi-language source tracking**
- `sources` field enables tracking multiple implementation languages per specification
- Each source entry specifies `language`, `identifier`, and documentation `variants`
- Supported languages: `go`, `python`, `typescript` (stub)
- For Python sources, optional `module` field provides dotted module name
- `variants` define different documentation perspectives (public/internal for Go, api/implementation/tests for Python)
- Generated documentation files are stored under `contracts/{language}/`
- `packages` field maintained for backwards compatibility with Go-only specs

**Concerns vs responsibilities**
- *Concerns* describe the enduring problem space or quality dimensions the artefact must watch: the stuff that keeps its owners awake at night.
- *Responsibilities* are the explicit services or behaviours the artefact promises to deliver. They are actionable commitments that produce value or enforce constraints.
- `guiding_principles` articulate enduring heuristics that shape solutions.
- `assumptions` note beliefs that need validation; `hypotheses` and `decisions` track the evolution of those beliefs.

Specifications continue to hold detailed requirements and verification notes inside the document body. Frontmatter only advertises the existence of related artefacts (via `relations`) or critical guard rails (`constraints`).
## Requirements (`kind: requirement|standard/*`)

```yaml
requirement_kind: functional|non-functional|policy|standard
rfc2119_level: must|should|may
value_driver: user-capability|operational-excellence|compliance|experience
acceptance_criteria:
  - Given...
  - When...
  - Then...
verification_refs:
  - VT-210
  - VH-044
```

Lifecycle metadata such as `status`, `introduced`, `implemented_by`, and `verified_by` is managed in the generated requirements registry (`supekku/registry/requirements.yaml`). Those fields are derived from specs, deltas, revisions, and audits rather than stored directly in requirement frontmatter.

## Verification Artefacts (`kind: verification`)

```yaml
verification_kind: automated|agent|manual
covers:
  - FR-102
  - NF-020
procedure: >-
  Outline of steps or tooling.
```

## Deltas (`kind: delta`)

```yaml
applies_to:
  specs:
    - SPEC-101
    - SPEC-102
  prod:
    - PROD-020
  requirements:
    - SPEC-101.FR-01
    - PROD-020.NF-03
context_inputs:
  - type: research
    id: RC-010
  - type: decision
    id: SPEC-101.DEC-02
outcome_summary: >-
  Declarative description of the target state after applying the delta.
risk_register:
  - id: RISK-DC-001
    title: Schema migration might lose historical block IDs
    exposure: change
    likelihood: medium
    impact: high
    mitigation: Add dry-run checksum validation before applying events
```

Deltas are the declarative change bundles that reconcile code with PROD/SPEC truths. `applies_to` enumerates the declarative inputs the delta aligns, `context_inputs` captures supporting research or decisions, `outcome_summary` states the target end-state, and `risk_register` records change risks.

## Design Revisions (`kind: design_revision`)

```yaml
delta_ref: DE-021
source_context:
  - type: research
    id: RC-010
  - type: hypothesis
    id: PROD-020.HYP-03
code_impacts:
  - path: internal/content/reconciler.go
    current_state: >-
      Summary of the existing behaviour the delta will adjust.
    target_state: >-
      Declarative description of the intended behaviour/design.
  - path: internal/content/schema_repo.go
    current_state: >-
      Current data access strategy.
    target_state: >-
      New transaction boundaries.
verification_alignment:
  - verification: VT-210
    impact: regression
  - verification: VA-044
    impact: new
design_decisions:
  - id: SPEC-101.DEC-04
    summary: Adopt optimistic locking for schema updates.
open_questions:
  - description: Do we need a background repair job?
    owner: david
    due: 2024-06-12
```

Design Revisions translate a delta into concrete design adjustments: they are declarative maps from current to target system behaviour, not execution checklists. `delta_ref` anchors the revision to its delta. `source_context` mirrors the delta’s chosen inputs for traceability. `code_impacts` list affected code areas with paired current/target state summaries to guide implementation agents. `verification_alignment` records how existing tests or audits must change. `design_decisions` and `open_questions` expose trade-offs still under discussion.

## Problem Statements (`kind: problem`)

```yaml
id: PROB-012
status: captured|validated|in-progress|resolved|retired
problem_statement: >-
  Crisp description of the pain or gap.
context:
  - type: research
    id: UX-023
  - type: metric
    id: sync_latency_p99
success_criteria:
  - Users report sync completes within 5s in interviews.
  - P99 latency < 7s for two consecutive releases.
related_requirements:
  - PROD-005.FR-02
  - SPEC-101.NF-01
```

Problem statements define the undesirable state we are trying to change. They link evidence (`context`), affected requirements, and measurable success criteria so product and technical changes stay grounded.

## Issues and Ideas (`kind: issue`)

```yaml
status: open|triaged|in-progress|blocked|resolved|retired
categories:
  - regression
  - verification_gap
severity: p1|p2|p3|p4
impact: user|systemic|process
problem_refs:
  - PROB-012
related_requirements:
  - SPEC-101.FR-01
  - PROD-005.NF-02
affected_verifications:
  - VT-210
  - VA-044
linked_deltas:
  - DE-021
```

Issues capture actionable backlog entries. Use `categories` to signal the flavour (`regression`, `process_gap`, `idea`, etc.) and relate them to problems, requirements, verifications, and eventual deltas/design revisions.

## Audits (`kind: audit`)

```yaml
spec_refs:
  - SPEC-101
prod_refs:
  - PROD-020
code_scope:
  - internal/content/**
  - cmd/vice/*
audit_window:
  start: 2024-06-01
  end: 2024-06-08
summary: >-
  Snapshot of how the inspected code aligns with referenced PROD/SPEC artefacts.
findings:
  - id: FIND-001
    description: Content reconciler deviates from SPEC-101 responsibility.
    outcome: drift|aligned|risk
    linked_issue: ISSUE-018
    linked_delta: DE-021
patch_level:
  - artefact: SPEC-101
    status: aligned|divergent|unknown
    notes: Implementation matches responsibilities except for schema validation.
verification_status:
  - verification: VT-210
    result: pass|fail|missing
    notes: Needs new scenario covering strict mode.
next_actions:
  - type: delta
    id: DE-021
  - type: issue
    id: ISSUE-052
```

Audits (or patch-level reports) capture the outcome of comparing reality against PROD/SPEC truths. They document scope, relevant artefacts, findings, and recommended next actions so drift feeds directly into the backlog/delta pipeline.

## Risk Artefacts (`kind: risk`)

```yaml
risk_kind: systemic|operational|delivery
status: identified|mitigating|retired
likelihood: low|medium|high
impact: low|medium|high
origin: ADR-012
controls:
  - TS-015
relations:
  - type: threatens
    target: SPEC-004
```

Use standalone risk docs for "lurking" hazards or cross-cutting concerns. Link them from specs, ADRs, or issues with `relations` (`tracked_by`, `threatens`, etc.).

## Implementation Plans (`kind: plan|phase|task`)

```yaml
objective: >-
  Qualitative goal for the plan or phase.
entrance_criteria:
  - SPEC-101 status == approved
exit_criteria:
  - VT-210 executed
```

Frontmatter can reference requirements or verifications when they act as gating conditions (`relations` or inline criteria), but narrative explanations stay in the body.

## Obsidian Compatibility

- YAML frontmatter is delimited with `---` blocks; keep keys lowercase with hyphen separators for readability.
- `aliases` enables Obsidian's alternate title rendering and search.
- Arrays use standard YAML sequences (`- item`). Obsidian accepts inline lists, but multiline sequences are more legible.
- Tags can stay in frontmatter (`tags:`) or inline (`#spec`); pick one strategy per artefact. This schema keeps tags in frontmatter for machine parsing.

## Next Tasks

1. Retrofit additional specifications and requirements with the revised frontmatter, keeping qualities and verification prose inside bodies where appropriate.
2. Update agent prompts to treat `relations` and `risk_register` entries as first-class context sources.
3. Draft a coarse-grained relationship map (D2 or ERD) covering specs, requirements, verifications, deltas, risks, and plans to validate the mental model.
