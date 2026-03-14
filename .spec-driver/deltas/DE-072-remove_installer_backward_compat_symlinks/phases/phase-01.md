---
id: IP-072.PHASE-01
slug: 072-remove_installer_backward_compat_symlinks-phase-01
name: IP-072 Phase 01
created: "2026-03-08"
updated: "2026-03-08"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-072.PHASE-01
plan: IP-072
delta: DE-072
objective: >-
  Remove installer-created compatibility symlinks and align installer tests and
  output with canonical-only workspace creation, including ADR reconciliation.
entrance_criteria:
  - DE-072, DR-072, and IP-072 reviewed.
  - Affected installer code and tests identified.
exit_criteria:
  - Installer code no longer creates compatibility symlinks.
  - Installer tests verify the new layout expectations.
  - ADR-006 no longer describes installer-created compatibility symlinks as the default install behavior.
  - Targeted verification for touched files passes.
verification:
  tests:
    - pytest supekku/scripts/lib/install_test.py
    - just pylint-files supekku/scripts/install.py supekku/scripts/lib/install_test.py
  evidence:
    - "`uv run pytest supekku/scripts/lib/install_test.py` passed."
    - "`just pylint-files supekku/scripts/install.py supekku/scripts/lib/install_test.py` reported only pre-existing warnings."
tasks:
  - id: 1.1
    title: Remove compatibility symlink creation from installer flow.
    status: done
  - id: 1.2
    title: Update installer tests and output messaging for canonical-only layout.
    status: done
  - id: 1.3
    title: Reconcile ADR-006 with the new installer behavior.
    status: done
  - id: 1.4
    title: Run targeted verification and capture outcomes.
    status: done
risks:
  - Installer tests may still assume legacy root paths are created on fresh install.
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-072.PHASE-01
```

# Phase 1 - Remove installer compatibility symlinks

## 1. Objective

Remove installer-created compatibility symlinks, update verification, and reconcile ADR-006 so fresh installs only create the canonical `.spec-driver/` workspace layout.

## 2. Links & References

- **Delta**: DE-072
- **Design Revision Sections**: Sections 2-5 of [DR-072](../DR-072.md)
- **Specs / PRODs**: SPEC-129.FR-001
- **Support Docs**: ADR-006, `supekku/scripts/install.py`, `supekku/scripts/lib/install_test.py`

## 3. Entrance Criteria

- [x] DE/DR/IP reviewed
- [x] Installer code path identified
- [x] Installer test module identified

## 4. Exit Criteria / Done When

- [x] Installer no longer creates `specify/`, `change/`, `backlog/`, or `memory/` compatibility paths during initialization
- [x] Installer output/messages no longer claim those paths are created
- [x] ADR-006 matches the new installer behavior
- [x] Targeted pytest and touched-file pylint verification pass

## 5. Verification

- Tests to run: `pytest supekku/scripts/lib/install_test.py`
- Tooling/commands: `just pylint-files supekku/scripts/install.py supekku/scripts/lib/install_test.py`
- Evidence to capture: passing local test and pylint output for the touched files

## 6. Assumptions & STOP Conditions

- Assumptions: Removing installer-created compatibility views is intentionally limited to fresh-install behavior.
- STOP when: the change appears to require revising broader path-resolution behavior or doctrine beyond installer code/tests.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description                                                                | Parallel? | Notes                                                      |
| ------ | --- | -------------------------------------------------------------------------- | --------- | ---------------------------------------------------------- |
| [x]    | 1.1 | Remove compatibility symlink creation from installer flow                  | [ ]       | `supekku/scripts/install.py`                               |
| [x]    | 1.2 | Update installer tests and output messaging to match canonical-only layout | [ ]       | `supekku/scripts/lib/install_test.py` and installer output |
| [x]    | 1.3 | Reconcile ADR-006 with the new installer default                           | [ ]       | Decision record text only                                  |
| [x]    | 1.4 | Run targeted verification and record outcomes                              | [ ]       | pytest + pylint                                            |

### Task Details

- **1.1 Description**
  - **Design / Approach**: Delete the dedicated compatibility helper from the initialization flow rather than adding a new flag.
  - **Files / Components**: `supekku/scripts/install.py`
  - **Testing**: Fresh install assertions should show no root-level compatibility paths are created.
  - **Observations & AI Notes**: Symlink creation is currently isolated in `_create_compat_symlinks()`.

- **1.2 Description**
  - **Design / Approach**: Update existing installer tests and any install-time messaging that mentions created compatibility paths.
  - **Files / Components**: `supekku/scripts/lib/install_test.py`, `supekku/scripts/install.py`
  - **Testing**: Adjust expected filesystem state and messages in affected tests.

- **1.3 Description**
  - **Design / Approach**: Update the ADR language that currently presents compatibility symlinks as installer-provided default behavior.
  - **Files / Components**: `specify/decisions/ADR-006...` canonical path via `.spec-driver/decisions/...`
  - **Testing**: Documentation consistency only.

- **1.4 Description**
  - **Design / Approach**: Run targeted pytest and touched-file pylint, then record results in notes if scope changes.
  - **Files / Components**: touched installer files
  - **Testing**: authoritative local verification for this phase

## 8. Risks & Mitigations

| Risk                                    | Mitigation                                                | Status |
| --------------------------------------- | --------------------------------------------------------- | ------ |
| Tests encode old compatibility behavior | Update assertions in the same patch and verify explicitly | open   |

## 9. Decisions & Outcomes

- `2026-03-08` - Keep the delta scoped to installer behavior and fresh-install verification only.
- `2026-03-08` - Treat ADR-006 reconciliation as part of the same delta because the code change alters documented default installer behavior.

## 10. Findings / Research Notes

- Compatibility symlink creation is centralized in `_create_compat_symlinks()` and called once from `initialize_workspace()`.
- Installer tests live in `supekku/scripts/lib/install_test.py`, not beside the script module.
- Verification: `uv run pytest supekku/scripts/lib/install_test.py` passed.
- Verification: `just pylint-files supekku/scripts/install.py supekku/scripts/lib/install_test.py` reported only pre-existing warnings and no new undefined-name regressions after the patch.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
