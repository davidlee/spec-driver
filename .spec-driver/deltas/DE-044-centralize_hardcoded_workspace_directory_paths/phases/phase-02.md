---
id: IP-044.PHASE-02
slug: "044-centralize_hardcoded_workspace_directory_paths-phase-02"
name: "P02: Production code"
created: "2026-03-05"
updated: "2026-03-21"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-044.PHASE-02
plan: IP-044
delta: DE-044
objective: >-
  Replace all hardcoded workspace directory strings in production code with
  constants and helpers from core/paths.py.
entrance_criteria:
  - P01 complete — constants and helpers exist and are tested
exit_criteria:
  - All production .py files use constants/helpers for workspace paths
  - just test passes (2571+ tests, zero failures)
  - just lint clean
  - just pylint does not regress
verification:
  tests:
    - VT-044-regression
  evidence: []
tasks:
  - id: "2.1"
    summary: Update registries
  - id: "2.2"
    summary: Update workspace.py
  - id: "2.3"
    summary: Update install.py
  - id: "2.4"
    summary: Update CLI commands
  - id: "2.5"
    summary: Update remaining production scripts
  - id: "2.6"
    summary: Lint and full test suite verification
risks:
  - description: Missed import causes runtime NameError
    mitigation: Run full test suite after each file group
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-044.PHASE-02
```

# Phase 2 - Production code

## 1. Objective

Replace all hardcoded workspace directory path strings in production (non-test)
Python files with imports from `core/paths.py`. No behaviour change — only
import + reference swap.

## 2. Links & References

- **Delta**: [DE-044](../DE-044.md)
- **Design Revision**: [DR-044 §4.2–4.5](../DR-044.md)
- **Phase 1**: [phase-01.md](./phase-01.md) — constants and helpers now available

## 3. Entrance Criteria

- [x] P01 complete — constants and helpers exist in `core/paths.py`

## 4. Exit Criteria / Done When

- [x] All registries use path helpers
- [x] `workspace.py` uses path helpers
- [x] `install.py` uses path constants
- [x] CLI commands use path helpers/constants
- [x] Other production scripts use path helpers/constants
- [x] `just test` passes (2606 passed)
- [x] `just lint` + `just pylint` clean (no regression)

## 5. Verification

- `just test` after each task group
- `just lint` after each file
- Final: `rg '"specify"' --type py -g '!*_test.py'` should show zero path-construction hits (same for `"change/"`, `"backlog"`, `"memory/"`)

## 6. Assumptions & STOP Conditions

- Assumptions: all call sites pass an explicit `root` (no auto-discovery changes needed)
- STOP when: a registry constructor signature needs changing (would ripple to callers)

## 7. Tasks & Progress

| Status | ID  | Description              | Parallel? | Notes                                                                                                                                                 |
| ------ | --- | ------------------------ | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| [x]    | 2.1 | Update registries        | —         | 7 registries: specs, decisions, policies, standards, changes, backlog, memory                                                                         |
| [x]    | 2.2 | Update `workspace.py`    | —         | sync_requirements() path refs → helpers                                                                                                               |
| [x]    | 2.3 | Update `install.py`      | [P]       | Directory list + backlog/memory refs → constants                                                                                                      |
| [x]    | 2.4 | Update CLI commands      | —         | sync.py, common.py, list.py, resolve.py                                                                                                               |
| [x]    | 2.5 | Update remaining scripts | —         | creation.py, executor.py, specs/creation.py, mirror.py, list_specs.py, requirements.py, complete_delta.py, sync_specs.py, validate_revision_blocks.py |
| [x]    | 2.6 | Lint and full test suite | —         | 2606 passed, ruff clean, pylint 9.56/10 (unchanged)                                                                                                   |

### Task Details

- **2.1 Registries** (7 files)
  - `specs/registry.py`: `"specify" / "tech"` → `get_tech_specs_dir(self.root)`, same for product
  - `decisions/registry.py`: `"specify" / "decisions"` → `get_decisions_dir(self.root)`
  - `policies/registry.py`: `"specify" / "policies"` → `get_policies_dir(self.root)`
  - `standards/registry.py`: `"specify" / "standards"` → `get_standards_dir(self.root)`
  - `changes/registry.py`: `"change"` → `get_changes_dir(self.root)`
  - `backlog/registry.py`: `"backlog"` → `get_backlog_dir(self.root)`
  - `memory/registry.py`: `"memory"` → `get_memory_dir(self.root)`

- **2.2 workspace.py**
  - `sync_requirements()`: 5 path references → helpers

- **2.3 install.py**
  - Directory list in `setup_workspace()` → constant-derived expressions
  - `backlog_file` path → `get_backlog_dir()`

- **2.4 CLI commands** (~10 files)
  - `cli/sync.py`, `cli/list.py`, `cli/common.py`, `cli/create.py`
  - Each: swap `root / "specify" / ...` or `root / "change" / ...` with helper

- **2.5 Remaining scripts**
  - `scripts/sync_specs.py`, `scripts/requirements.py`, `scripts/list_specs.py`
  - `scripts/complete_delta.py`, `scripts/validate_revision_blocks.py`
  - `scripts/lib/changes/creation.py`, `scripts/lib/specs/creation.py`
  - `scripts/lib/deletion/executor.py`, `scripts/lib/contracts/mirror.py`
  - Various `scripts/lib/` modules with path references

## 8. Risks & Mitigations

| Risk                                          | Mitigation                                | Status |
| --------------------------------------------- | ----------------------------------------- | ------ |
| Missed import → runtime NameError             | Run full test suite after each task group | open   |
| Subtle path difference (trailing slash, etc.) | Tests catch any path mismatch             | open   |

## 9. Decisions & Outcomes

- `install.py` pkg_memory refs (`package_root / "memory"`) intentionally left as-is — these are package directory lookups, not workspace paths
- `_KIND_TO_DIR` mapping in changes/registry.py kept — the ChangeRegistry composes `get_changes_dir(root) / subdir` rather than using per-kind helpers, which is clean since the mapping is local knowledge
- Fixed 3 test files (edit_test, show_test, view_test) that used ISSUE-003 (deleted fixture) — converted to mocked resolution or updated IDs

## 10. Findings / Research Notes

- ~25 production files had hardcoded workspace path strings
- No import cycle issues — paths.py only depends on repo.py
- No runtime NameErrors — full test suite green after each task group

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence: `just` passes (2606 tests, ruff clean, pylint 9.56/10)
- [x] Grep verification: zero path-construction hits in production code
- [ ] Hand-off notes to P03 (test fixtures)
