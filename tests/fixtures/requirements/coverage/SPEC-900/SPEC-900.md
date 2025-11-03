---
id: SPEC-900
slug: test-coverage-spec
name: Test Coverage Spec
status: draft
kind: spec
---

# SPEC-900 – Test Coverage Spec

## Requirements

- FR-001: Sample verified requirement
- FR-002: Sample in-progress requirement
- FR-003: Sample planned requirement

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: SPEC-900
entries:
  - artefact: VT-900
    kind: VT
    requirement: SPEC-900.FR-001
    status: verified
    notes: Fully verified test case
  - artefact: VT-901
    kind: VT
    requirement: SPEC-900.FR-002
    status: in-progress
    notes: Test in progress
  - artefact: VT-902
    kind: VT
    requirement: SPEC-900.FR-003
    status: planned
    notes: Planned test case
```
