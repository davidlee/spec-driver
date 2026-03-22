---
id: IP-125-P01
slug: "125-enforce_explicit_module_boundaries_and_coupling_constraints-phase-01"
name: Reconcile architecture contracts and pilot scope
created: "2026-03-23"
updated: "2026-03-23"
status: completed
kind: phase
plan: IP-125
delta: DE-125
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-125-P01
plan: IP-125
delta: DE-125
objective: >-
  Reconcile the governing artefacts for DE-125, define the internal domain
  contract ordering, and identify the first migration seams that must exist
  before code-moving work begins.
entrance_criteria:
  - Initial appraisal completed
  - Current package and verification reality inspected
  - Need for domain-internal contracts confirmed
exit_criteria:
  - DE-125 no longer claims work already landed elsewhere
  - DR-125 defines the domain ordering and registry/relations split
  - IP-125 contains real phases, gates, and verification work
  - First pilot migration targets are named from the import graph
verification:
  tests: []
  evidence:
    - spec-driver validate
tasks:
  - Rewrite DE-125 around current repo reality
  - Rewrite DR-125 around domain-internal contracts
  - Replace template IP-125 with real phases and gates
  - Identify first pilot migration targets and verification additions
risks:
  - Domain remains too coarse to stop lateral coupling
  - Pilot selection drifts back to rename convenience
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-125-P01
files:
  references:
    - .spec-driver/deltas/DE-125-enforce_explicit_module_boundaries_and_coupling_constraints/DE-125.md
    - .spec-driver/deltas/DE-125-enforce_explicit_module_boundaries_and_coupling_constraints/DR-125.md
    - .spec-driver/deltas/DE-125-enforce_explicit_module_boundaries_and_coupling_constraints/IP-125.md
    - .spec-driver/policies/POL-003-module-boundaries.md
    - pyproject.toml
  context:
    - supekku/scripts/lib/requirements/registry.py
    - supekku/scripts/lib/policies/registry.py
    - supekku/scripts/lib/validation/validator.py
entrance_criteria:
  - item: "Initial appraisal completed"
    completed: true
  - item: "Current package and verification reality inspected"
    completed: true
  - item: "Need for domain-internal contracts confirmed"
    completed: true
exit_criteria:
  - item: "DE-125 no longer claims work already landed elsewhere"
    completed: true
  - item: "DR-125 defines the domain ordering and registry/relations split"
    completed: true
  - item: "IP-125 contains real phases, gates, and verification work"
    completed: true
  - item: "First pilot migration targets are named from the import graph"
    completed: true
tasks:
  - id: "1"
    description: "Rewrite DE-125 around current repo reality"
    status: completed
  - id: "2"
    description: "Rewrite DR-125 around domain-internal contracts"
    status: completed
  - id: "3"
    description: "Replace template IP-125 with real phases and gates"
    status: completed
  - id: "4"
    description: "Identify first pilot migration targets and verification additions"
    status: completed
```

# Phase 1 — Reconcile architecture contracts and pilot scope

## 1. Objective

Make DE-125 executable again by aligning the delta, design revision, plan, and
policy with current repo reality. Define the internal `domain` contract that is
supposed to tackle lateral coupling, and identify the first migration seams that
must exist before broader file moves.

## 2. Links & References

- **Delta**: [DE-125](../DE-125.md)
- **Design Revision**: [DR-125](../DR-125.md)
- **Implementation Plan**: [IP-125](../IP-125.md)
- **Policy**: [POL-003](../../../policies/POL-003-module-boundaries.md)
- **Current enforcement**: `/workspace/spec-driver/pyproject.toml`
- **Legacy import surface**: `supekku/scripts/lib/{requirements,backlog,specs,policies,decisions,relations,validation}`

## 3. Entrance Criteria

- [x] Initial appraisal completed
- [x] Repo reality sampled (`spec_driver/` exists, top-level `import-linter` exists)
- [x] Need for domain-internal contracts confirmed

## 4. Exit Criteria / Done When

- [x] DE-125 no longer claims work that has already landed elsewhere
- [x] DR-125 defines the internal `domain` ordering and registry/relations split
- [x] IP-125 contains real phases, gates, and verification work
- [x] First pilot migration targets named from the current import graph
- [x] Verification additions scoped for implementation (`import-linter`,
  test-layout reconciliation, targeted checks)

## 5. Verification

- Inspect current layer config: `rg -n "\\[tool.importlinter\\]|import-linter" pyproject.toml`
- Inspect current package layout: `find spec_driver -maxdepth 3 -type d | sort`
- Inspect legacy coupling hotspots:
  `rg -n "from supekku\\.scripts\\.lib\\.(specs|requirements|backlog|policies|decisions|relations|validation)" supekku/scripts/lib`
- Validate structured docs after updates: `spec-driver validate`

## 6. Assumptions & STOP Conditions

- **Assumption**: The first code-moving slice should follow seam extraction, not
  precede it.
- **Assumption**: Some current legacy modules described as "domain" will be
  reclassified into orchestration or core once inspected more closely.
- **STOP**: If the intended domain order cannot describe the first pilot modules
  without exceptions, revise DR-125 before implementation.
- **STOP**: If `POL-003` needs a materially different boundary model than DR-125,
  reconcile policy and design before proceeding.

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 1.1 | Re-appraise DE-125 against repo reality | — | Found stale sequencing and template IP |
| [x] | 1.2 | Rewrite DE-125 around the real thesis | — | Focus on domain-internal contracts |
| [x] | 1.3 | Rewrite DR-125 with explicit domain ordering | — | Registry rule and mapping guidance added |
| [x] | 1.4 | Replace template IP with executable phases | — | Added gates and verification |
| [x] | 1.5 | Name first pilot migration targets | — | `relations.query` and `relations.manager`; policy backlinks as seam extraction |
| [x] | 1.6 | Scope verification additions | — | `just lint-imports` plus targeted relations/governance tests |
| [x] | 1.7 | Prepare Phase 2 sheet once 1.5 and 1.6 are stable | — | `spec-driver create phase` created `IP-125-P02` |

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Domain remains a free-form package | Keep explicit internal ordering and STOP on exceptions | open |
| Policy, DR, and IP drift again | Treat doc reconciliation as a tracked phase with exit criteria | mitigated |
| Pilot selection is driven by rename convenience | Require import-graph evidence before Phase 2 | open |

## 9. Decisions & Outcomes

- 2026-03-23 — DE-125 reframed: top-level layering is necessary but insufficient.
- 2026-03-23 — `domain` will be treated as ordered internal contracts rather than
  a single package bucket.
- 2026-03-23 — DE-124 remains parallel work against the orchestration facade.

## 10. Findings / Research Notes

- The repo already contains `spec_driver/` package roots and one top-level
  `import-linter` contract.
- `IP-125` was previously a raw template and did not describe executable work.
- Legacy sibling-registry imports remain the main coupling risk.
- Lowest-coupling first pilots are the `relations` helpers, not the registries.
- `PolicyRegistry` backlink building is the first concrete seam-extraction target
  before migrating governance registries.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [ ] Notes updated with final phase findings
- [x] Next phase sheet created only when pilot targets and verification scope are concrete
