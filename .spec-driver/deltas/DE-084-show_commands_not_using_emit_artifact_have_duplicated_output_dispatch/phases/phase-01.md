---
id: IP-084.PHASE-01
slug: migrate-show-requirement-and-card
name: Migrate show requirement and show card to emit_artifact
created: '2026-03-09'
updated: '2026-03-09'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-084.PHASE-01
plan: IP-084
delta: DE-084
objective: >-
  Migrate show requirement and show card to emit_artifact, eliminating the last
  two inline output dispatch blocks in cli/show.py.
entrance_criteria:
  - DE-084 accepted
exit_criteria:
  - Zero inline sum([json_output...]) checks in cli/show.py
  - All existing show_test.py tests pass
  - just lint clean
  - just pylint-files on touched files clean
verification:
  tests:
    - show_test.py (existing suite)
  evidence:
    - VA-084-01
tasks:
  - id: '1.1'
    description: Migrate show requirement to emit_artifact
  - id: '1.2'
    description: Migrate show card to emit_artifact
  - id: '1.3'
    description: Verify and lint
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-084.PHASE-01
```

# Phase 1 – Migrate show requirement and show card

## Done When
- [x] Zero `sum([json_output, ...])` or `bool_flags = sum(...)` in `cli/show.py`
- [x] `just test` passes (3610 passed)
- [x] `just lint` clean

## Tasks

| Status | ID | Description | Notes |
| --- | --- | --- | --- |
| [x] | 1.1 | Migrate `show spec` | `resolve_artifact` + `emit_artifact`; `to_dict(repo_root)` in json_fn closure |
| [x] | 1.2 | Migrate `show delta` | `resolve_artifact` + `emit_artifact`; `format_delta_details_json` in json_fn |
| [x] | 1.3 | Migrate `show requirement` | `resolve_artifact` + `emit_artifact`; added `content_type` param |
| [x] | 1.4 | Migrate `show adr` | `resolve_artifact` + `emit_artifact`; `to_dict(repo_root)` |
| [x] | 1.5 | Migrate `show policy` | `resolve_artifact` + `emit_artifact` |
| [x] | 1.6 | Migrate `show standard` | `resolve_artifact` + `emit_artifact` |
| [x] | 1.7 | Migrate `show card` | Manual `CardRegistry.resolve_card` (for `--anywhere`), then `emit_artifact`; added `content_type` param |
| [x] | 1.8 | Verify: tests, lint, grep for remaining inline dispatch | 3610 passed, 0 inline dispatch remaining |
