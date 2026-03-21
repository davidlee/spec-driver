---
id: IP-097.PHASE-02
slug: "097-cli-and-validation-integration"
name: "Phase 2: CLI and validation integration"
created: "2026-03-15"
updated: "2026-03-21"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-097.PHASE-02
plan: IP-097
delta: DE-097
objective: >-
  Wire phase-1 domain functions into CLI and validation. Add show relations
  command, integrate unresolved reference validation into WorkspaceValidator,
  and surface findings through diagnostics pipeline.
entrance_criteria:
  - Phase 1 complete (all domain tests pass)
exit_criteria:
  - show relations command works with forward/inverse/both directions
  - unresolved references surface as warnings (or errors with --strict)
  - diagnostics pipeline surfaces new validation findings
  - all new CLI tests pass
  - lint clean
verification:
  tests:
    - VT-097-show-relations
    - VT-097-unresolved
  evidence: []
tasks:
  - id: "2.1"
    description: "show relations CLI command"
    status: todo
  - id: "2.2"
    description: "Unresolved ref validation in WorkspaceValidator"
    status: todo
  - id: "2.3"
    description: "Tests for 2.1-2.2"
    status: todo
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-097.PHASE-02
```

# Phase 2 — CLI and validation integration

## 1. Objective

Wire phase-1 domain layer into user-facing surfaces: `show relations <ID>` command and unresolved reference validation via `WorkspaceValidator` / diagnostics.

## 2. Links & References

- **Delta**: DE-097
- **Design Revision**: DR-097 §4.3 (show.py), §4.4 (validator.py), §4.5 (refs.py)
- **Phase 1 output**: `relations/graph.py`, `core/artifact_ids.py`

## 3. Entrance Criteria

- [ ] Phase 1 complete — all domain tests pass

## 4. Exit Criteria / Done When

- [ ] `show relations <ID>` displays forward/inverse references grouped by type
- [ ] `--direction forward|inverse|both` works correctly
- [ ] Unknown ID warns but still shows inverse edges if any
- [ ] Unresolved frontmatter refs produce warnings in `WorkspaceValidator`
- [ ] `--strict` mode produces errors for unresolved refs
- [ ] Findings surface through `diagnostics/checks/refs.py` (no structural change needed)
- [ ] All tests pass, lint clean

## 5. Verification

- `pytest supekku/cli/show_test.py` (extended)
- `pytest supekku/scripts/lib/validation/validator_test.py` (extended)
- `pylint` on modified files

## 7. Tasks & Progress

| Status | ID  | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 2.1 | `show relations` command in `cli/show.py` | [P] | Independent of 2.2 |
| [ ] | 2.2 | `_validate_unresolved_references` in `WorkspaceValidator` | [P] | Independent of 2.1 |
| [ ] | 2.3 | Tests for 2.1–2.2 | | TDD with each task |

### Task Details

- **2.1 show relations command**
  - **Files**: `supekku/cli/show.py`
  - **Approach**: Add `@app.command("relations")` with `artifact_id` positional arg, `--direction` option (default "both"), `--root` option. Build workspace, call `build_reference_graph`, then `query_neighbourhood`. Format output grouped by kind. Handle unknown IDs: try normalization, warn, still show inverse edges.
  - **Output format**: Per DR-097 §4.3 — grouped forward/inverse sections with relation type, target ID, and kind.

- **2.2 Unresolved ref validation**
  - **Files**: `supekku/scripts/lib/validation/validator.py`
  - **Approach**: Add `_validate_unresolved_references` method. Import `build_reference_graph` and `find_unresolved_references`. For each unresolved edge, emit `_warning` (or `_error` in strict mode). Call from `validate()` method.
  - **Note**: `diagnostics/checks/refs.py` already delegates to `validate_workspace` — new findings automatically surface. No changes needed there.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|-----------|--------|
| Graph build performance in validation (runs on every `doctor`) | Acceptable at current scale; monitor | open |

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Notes updated
- [ ] Hand-off notes to phase 3
