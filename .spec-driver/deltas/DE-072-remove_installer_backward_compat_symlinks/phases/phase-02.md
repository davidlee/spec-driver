---
id: IP-072.PHASE-02
slug: "072-remove_installer_backward_compat_symlinks-phase-02"
name: IP-072 Phase 02
created: "2026-03-08"
updated: "2026-03-08"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-072.PHASE-02
plan: IP-072
delta: DE-072
objective: >-
  Externalize the lazy-created kanban template into a packaged asset at
  `supekku/templates/kanban/template.md` and source `kanban/template.md` from it.
entrance_criteria:
  - Phase 1 complete.
  - Current root `kanban/template.md` content reviewed.
exit_criteria:
  - Packaged kanban template asset exists under `supekku/templates/kanban/template.md`.
  - `CardRegistry` lazy template creation reads from the packaged asset instead of an inline constant.
  - Targeted card registry pytest coverage passes.
verification:
  tests:
    - uv run pytest supekku/scripts/lib/cards/registry_test.py
    - just pylint-files supekku/scripts/lib/cards/registry.py supekku/scripts/lib/cards/registry_test.py
  evidence:
    - '`uv run pytest supekku/scripts/lib/cards/registry_test.py` passed.'
    - '`just pylint-files supekku/scripts/lib/cards/registry.py supekku/scripts/lib/cards/registry_test.py` reported only pre-existing warnings in the longstanding test module.'
tasks:
  - id: 2.1
    title: Add packaged kanban template asset from the current repo-root template content.
    status: done
  - id: 2.2
    title: Switch lazy card-template creation to read the packaged asset.
    status: done
  - id: 2.3
    title: Update targeted tests to verify the packaged template source.
    status: done
  - id: 2.4
    title: Run targeted verification and capture outcomes.
    status: done
risks:
  - Package template location could accidentally be copied by install if template copy rules widen in future.
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-072.PHASE-02
```

# Phase 2 - Externalize kanban default template

## 1. Objective

Move the lazy-created kanban template out of Python code and into a packaged asset at `supekku/templates/kanban/template.md`, without changing install behavior.

## 2. Links & References

- **Delta**: DE-072
- **Design Revision Sections**: DR-072 sections 2-5
- **Specs / PRODs**: SPEC-129.FR-001
- **Support Docs**: `kanban/template.md`, `supekku/scripts/lib/cards/registry.py`, `supekku/scripts/lib/cards/registry_test.py`

## 3. Entrance Criteria

- [x] Phase 1 complete
- [x] Current root `kanban/template.md` reviewed

## 4. Exit Criteria / Done When

- [x] Packaged template asset added under `supekku/templates/kanban/template.md`
- [x] Lazy template creation uses the packaged asset instead of inline content
- [x] Targeted card registry pytest coverage passes

## 5. Verification

- Tests to run: `uv run pytest supekku/scripts/lib/cards/registry_test.py`
- Tooling/commands: `just pylint-files supekku/scripts/lib/cards/registry.py supekku/scripts/lib/cards/registry_test.py`
- Evidence to capture: passing targeted pytest; touched-file pylint with no new warnings introduced by this change

## 6. Assumptions & STOP Conditions

- Assumptions: `supekku/templates/**` subdirectories are not copied by the installer’s current `pattern="*.md"` behavior.
- STOP when: template asset placement starts to imply an install-time kanban bootstrap change.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description                                                                    | Parallel? | Notes                                        |
| ------ | --- | ------------------------------------------------------------------------------ | --------- | -------------------------------------------- |
| [x]    | 2.1 | Add packaged kanban template asset from the current repo-root template content | [ ]       | `supekku/templates/kanban/template.md`       |
| [x]    | 2.2 | Switch lazy card-template creation to read the packaged asset                  | [ ]       | `supekku/scripts/lib/cards/registry.py`      |
| [x]    | 2.3 | Update targeted tests to verify the packaged template source                   | [ ]       | `supekku/scripts/lib/cards/registry_test.py` |
| [x]    | 2.4 | Run targeted verification and record outcomes                                  | [ ]       | pytest + pylint                              |

### Task Details

- **2.1 Description**
  - **Design / Approach**: Copy the richer current `kanban/template.md` structure into a packaged asset so lazy creation has an explicit file-based source of truth.
  - **Files / Components**: `supekku/templates/kanban/template.md`
  - **Testing**: Asset contents are compared indirectly through the card registry test.

- **2.2 Description**
  - **Design / Approach**: Remove the inline default template constant and read the packaged asset when `kanban/template.md` is missing.
  - **Files / Components**: `supekku/scripts/lib/cards/registry.py`
  - **Testing**: Existing card creation tests plus packaged-template-source assertion.

- **2.3 Description**
  - **Design / Approach**: Strengthen the auto-create test to compare the created template against the packaged asset.
  - **Files / Components**: `supekku/scripts/lib/cards/registry_test.py`
  - **Testing**: `uv run pytest supekku/scripts/lib/cards/registry_test.py`

- **2.4 Description**
  - **Design / Approach**: Run targeted tests and touched-file pylint to verify the new asset-based fallback path.
  - **Files / Components**: touched card-registry files
  - **Testing**: pytest + pylint

## 8. Risks & Mitigations

| Risk                                                                             | Mitigation                                                                                      | Status   |
| -------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- | -------- |
| Future installer copy rules might start including nested package template assets | Keep installer behavior unchanged and rely on current `pattern="*.md"` root-only copy semantics | accepted |

## 9. Decisions & Outcomes

- `2026-03-08` - Externalize the lazy kanban template to a packaged asset, but do not make install create `kanban/` or copy the template proactively.

## 10. Findings / Research Notes

- Current root `kanban/template.md` already carries the richer structure we want as the packaged default.
- `CardRegistry._create_default_template()` was the only code path creating `kanban/template.md`.
- Verification: `uv run pytest supekku/scripts/lib/cards/registry_test.py` passed.
- Verification: `just pylint-files supekku/scripts/lib/cards/registry.py supekku/scripts/lib/cards/registry_test.py` reported only pre-existing warnings in the longstanding test module.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
