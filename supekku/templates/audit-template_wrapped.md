---
id: TEMPLATE-audit
slug: audit-template
name: Audit Template
created: 2024-06-08
updated: 2024-06-08
status: draft
kind: guidance
aliases:
  - Audit Template
---

# Audit Template

Use this template when running an agent-assisted or manual review to compare code against PROD/SPEC truths.

```markdown
---
id: AUD-XXX
kind: audit
status: draft|in-review|complete
spec_refs:
  - SPEC-101
prod_refs:
  - PROD-020
code_scope:
  - internal/content/**
audit_window:
  start: 2024-06-01
  end: 2024-06-08
summary: >-
  Snapshot of how the inspected code aligns with referenced PROD/SPEC artefacts.
findings:
  - id: FIND-001
    description: Content reconciler skips schema enforcement.
    outcome: drift|aligned|risk
    linked_issue: ISSUE-018
    linked_delta: DE-021
patch_level:
  - artefact: SPEC-101
    status: divergent
    notes: Implementation missing strict mode path.
  - artefact: PROD-020
    status: aligned
next_actions:
  - type: delta
    id: DE-021
  - type: issue
    id: ISSUE-052
---

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: AUD-XXX
entries:
  - artefact: VT-210
    kind: VT|VA|VH
    requirement: SPEC-101.FR-001
    status: verified|failed|blocked
    notes: >-
      Capture audit evidence or link to failing scenario.
```

## Observations
- …

## Evidence
- Code references, logs, test results

## Recommendations
- …
```

**Workflow Notes**
- Kick these off after major merges, before releases, or when specs/product intents change.
- Every non-aligned finding should link to the backlog (issues/problems) or directly spawn a delta.
- Patch-level entries provide a quick “at a glance” view of alignment so you can assess drift over time.
- Update `supekku:verification.coverage@v1` entries as you gather VT/VA/VH evidence.
