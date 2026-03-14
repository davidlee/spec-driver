---
id: SPEC-151
slug: supekku-scripts-lib-skills
name: supekku/scripts/lib/skills Specification
created: '2026-03-07'
updated: '2026-03-09'
status: draft
kind: spec
category: unit
c4_level: code
responsibilities:
- Define the skill subsystem boundary between packaged skill sources, installed skill copies, and the supporting sync/install
  library.
- Keep routing and execution guidance procedural in packaged skills rather than duplicating it across generated docs or ad
  hoc prose.
- Preserve the source-of-truth split where `supekku/skills/**` is edited and `.spec-driver/skills/**` is derived via sync.
- Support reuse of existing spec-driver entity commands from skills instead of proliferating parallel creation workflows.
aliases: []
packages: [supekku/scripts/lib/skills]
sources:
- language: python
  identifier: supekku/scripts/lib/skills
  module: supekku.scripts.lib.skills
  variants:
  - name: api
    path: contracts/api.md
  - name: implementation
    path: contracts/implementation.md
  - name: tests
    path: contracts/tests.md
- language: markdown
  identifier: supekku/skills
  variants:
  - name: packaged-skills
    path: /home/david/dev/spec-driver/supekku/skills
  - name: installed-skills
    path: /home/david/dev/spec-driver/.spec-driver/skills
---

# SPEC-151 – supekku/scripts/lib/skills

```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: SPEC-151
requirements:
  primary:
    - SPEC-151.FR-001
    - SPEC-151.FR-002
    - SPEC-151.FR-003
    - SPEC-151.FR-004
    - SPEC-151.NF-001
  collaborators:
    - PROD-011
    - PROD-001
    - PROD-002
interactions:
  - with: ADR-004
    nature: Skill guidance must reinforce the canonical workflow loop instead of competing with it
  - with: ADR-005
    nature: Skills are the canonical procedural layer; generated docs are projections
  - with: ADR-008
    nature: Audit and revision guidance must force explicit reconciliation rather than silent overwrite
```

```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: SPEC-151
capabilities:
  - id: packaged-skill-authority
    name: Packaged Skill Authority
    responsibilities:
      - Treat `supekku/skills/**` as the editable source of truth for packaged skills
      - Treat `.spec-driver/skills/**` as an installed, derived copy refreshed by sync
      - Keep procedural guidance in skills rather than scattering it through generated docs
    requirements:
      - SPEC-151.FR-001
      - SPEC-151.FR-002
    summary: >-
      The subsystem owns how procedural guidance is authored, stored, and
      projected into a workspace. Skill content is edited in the package source
      tree and synchronized into the installed workspace copy without creating
      a competing second handbook.
    success_criteria:
      - Editing the packaged skill source changes the installed copy after sync
      - Installed copies are treated as derived, not hand-maintained
      - Skill guidance remains the canonical procedural layer for agent work

  - id: workflow-routing-and-authorship-guidance
    name: Workflow Routing and Authorship Guidance
    responsibilities:
      - Provide narrow, composable skills for routing, execution, audit, and revision work
      - Bias audit findings back into authoritative specs through explicit branch criteria
      - Reuse existing spec-driver commands when revision work justifies a new spec boundary
    requirements:
      - SPEC-151.FR-003
      - SPEC-151.FR-004
    summary: >-
      The skills subsystem defines reusable procedures for choosing the right
      workflow, executing delta phases, reconciling audits, and shaping
      revisions. Audit-driven authorship must prefer existing spec patches,
      escalate to revision when authority moves, and use normal spec creation
      commands only as a revision-led fallback.
    success_criteria:
      - Audit guidance teaches `spec_patch -> revision -> revision-led new spec`
      - Revision guidance distinguishes simple patching from authority movement
      - No dedicated parallel spec-authoring workflow is required for the rare new-spec case
```

## 1. Intent & Summary

`SPEC-151` defines the skills subsystem boundary for spec-driver. That boundary
includes both the Python support library that installs and syncs skills and the
packaged skill corpus that carries the canonical procedural guidance.

The subsystem is responsible for keeping those layers coherent:

- packaged skills in `supekku/skills/**` are the editable source
- installed skills in `.spec-driver/skills/**` are derived workspace copies
- generated agent docs and hooks project local context but do not replace skill authority

For authorship-heavy workflow, the subsystem must reinforce the canonical loop
from `ADR-004`: audit findings are reconciled back into authoritative specs via
explicit procedures, not left as narrative drift.

## 2. Functional Requirements

### SPEC-151.FR-001 — Source and installed skill copies remain distinct

The subsystem SHALL treat `supekku/skills/**` as the packaged source of truth
and `.spec-driver/skills/**` as a synchronized installed copy.

### SPEC-151.FR-002 — Sync/install preserve packaged-skill authority

The supporting library SHALL install, refresh, and expose allowlisted skills
without requiring manual duplication or encouraging direct edits to the
installed copies.

### SPEC-151.FR-003 — Skills provide the canonical procedural workflow layer

The packaged skill corpus SHALL own routing, execution, audit, and revision
procedures for agent work, while generated docs remain routing/projection aids.

### SPEC-151.FR-004 — Audit-to-spec authorship reuses existing creation paths

Audit and revision skills SHALL teach the explicit branch order of existing
spec patch, revision, and revision-led new spec creation, reusing normal
`spec-driver create spec` workflows instead of introducing a competing
spec-authoring path.

## 3. Non-Functional Requirements

### SPEC-151.NF-001 — Guidance layers avoid sprawl and competing truths

The subsystem SHOULD minimize duplicate procedural guidance, keep packaged and
installed skill copies aligned, and avoid workflow surfaces that compete with
the canonical skill layer.

## 4. Verification

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: SPEC-151
entries:
  - artefact: VA-083-002
    kind: VA
    requirement: SPEC-151.FR-003
    status: verified
    notes: Authorship-skill gap review — no remaining gaps; audit→revision→spec-driver chain coherent.
  - artefact: VA-083-003
    kind: VA
    requirement: SPEC-151.FR-004
    status: verified
    notes: Worked examples for spec_patch, revision, and revision-led new spec — all teachable.
```
