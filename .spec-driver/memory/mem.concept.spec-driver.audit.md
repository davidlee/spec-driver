---
id: mem.concept.spec-driver.audit
name: Audits
kind: memory
status: active
memory_type: concept
updated: "2026-03-15"
verified: "2026-03-15"
confidence: high
tags: [spec-driver, audit, verification]
summary: Audits (AUD-*) compare implementation against specs. They reconcile realised behavior against intent and feed explicit spec reconciliation before closure.
priority:
  severity: medium
  weight: 6
provenance:
  sources:
    - kind: adr
      ref: ADR-004
    - kind: code
      ref: supekku/cli/create.py
    - kind: doc
      note: Retrospective (Audit-driven) workflow
      ref: supekku/about/lifecycle.md
    - kind: delta
      ref: DE-083
      note: Settled post-audit authorship branch criteria
---

# Audits

## Role in the Loop

The audit is the **verify** step of the [[mem.pattern.spec-driver.core-loop]].
In high-rigor flow, audits/contracts establish observed truth, then specs are
patched to match that observed truth before final closure.

## Two Modes

**Conformance audit** (typical in town-planner):

- Validates that implementation matches spec intent
- Produces `verifies` [[mem.concept.spec-driver.relations|relations]]
- Projects evidence back into [[mem.concept.spec-driver.verification|coverage]]
- Drives any required post-audit spec reconciliation

**Discovery/backfill audit** (typical in settler):

- Applied to existing code that predates spec-driver
- Discovers what the code actually does
- Feeds spec/requirement creation or updates
- May generate follow-up [[mem.concept.spec-driver.delta|deltas]]

## Where They Live

`change/audits/AUD-XXX/AUD-XXX.md`

Template: `.spec-driver/templates/audit-template.md`

## Post-Audit Authorship Path

When audit findings require spec reconciliation, the branch order is:

1. **Existing spec patch** (`spec_patch`) — the owning spec is still correct
   authority; update wording, coverage, or constraints in place.
2. **Revision** (`revision`) — authority, requirement ownership, or cross-spec
   lineage must change; create/update a revision to capture the movement.
3. **Revision-led new spec** — revision analysis proves no existing spec can own
   the reconciled truth cleanly; create a new spec via `spec-driver create spec`
   and update affected legacy specs. This is a sub-branch of revision, not a
   peer audit disposition.

New-spec creation is never a default — it requires explicit justification that
existing authority boundaries are insufficient. See DE-083 / DR-083 for the
full design rationale.

## Finding Disposition Schema

Each finding's `disposition` **must be a mapping**, not a plain string.
Required keys: `status`, `kind`. Optional: `refs`, `drift_refs`, `rationale`,
`closure_override`.

**Sharp edge**: writing `disposition: aligned` (a bare string) will crash
the validator. Always use the structured form:

```yaml
disposition:
  status: reconciled
  kind: aligned
```

### Valid `status` × `kind` pairs

| kind                | valid statuses          |
|---------------------|------------------------|
| `aligned`           | `reconciled`            |
| `spec_patch`        | `pending`, `reconciled` |
| `revision`          | `pending`, `reconciled` |
| `follow_up_delta`   | `pending`, `accepted`   |
| `follow_up_backlog` | `pending`, `accepted`   |
| `tolerated_drift`   | `accepted`              |

### Valid `outcome` → `kind` mapping

| outcome   | valid kinds                                                                    |
|-----------|--------------------------------------------------------------------------------|
| `aligned` | `aligned`                                                                      |
| `drift`   | `spec_patch`, `revision`, `follow_up_delta`, `follow_up_backlog`, `tolerated_drift` |
| `risk`    | `spec_patch`, `revision`, `follow_up_delta`, `follow_up_backlog`, `tolerated_drift` |

Authority: [[SPEC-116]], `supekku/scripts/lib/core/frontmatter_metadata/audit.py`

## Posture Variance

- **Pioneer**: audits are rare — feedback is informal
- **Settler**: both discovery and conformance audits are valid
- **Town Planner**: conformance audits are the default; evidence is mandatory
