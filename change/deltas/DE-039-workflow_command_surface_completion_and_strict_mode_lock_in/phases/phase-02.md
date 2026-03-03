---
id: IP-039.PHASE-02
slug: 039-workflow_command_surface_completion_and_strict_mode_lock_in-phase-02
name: IP-039 Phase 02
created: '2026-03-04'
updated: '2026-03-04'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-039.PHASE-02
plan: IP-039
delta: DE-039
objective: >-
  Add first-class `create audit` and `complete revision` CLI commands with
  lifecycle-consistent semantics, keeping CLI thin and logic in scripts/lib.
entrance_criteria:
  - Phase 1 complete (non-interactive completion + coverage messaging verified)
  - Audit template and metadata schema already exist
  - ChangeRegistry already handles audit kind
exit_criteria:
  - `uv run spec-driver create audit "title" --spec SPEC-XXX` creates AUD-NNN bundle
  - `uv run spec-driver complete revision RE-NNN` transitions status to completed
  - Command tests pass for both new flows
  - Lifecycle semantics match existing change artifact patterns
verification:
  tests:
    - uv run pytest -q supekku/scripts/lib/changes/creation_test.py -k audit
    - uv run pytest -q supekku/cli/create_test.py -k audit
    - uv run pytest -q supekku/cli/complete_test.py -k revision
  evidence:
    - VT-039-003
tasks:
  - id: 2.1
    title: Add create_audit() domain function in changes/creation.py
    status: done
  - id: 2.2
    title: Add `create audit` CLI command in cli/create.py
    status: done
  - id: 2.3
    title: Add complete_revision() domain function
    status: done
  - id: 2.4
    title: Add `complete revision` CLI command in cli/complete.py
    status: done
  - id: 2.5
    title: Write tests for create audit and complete revision
    status: done
  - id: 2.6
    title: Run verification, lint, update evidence
    status: done
risks:
  - risk: Audit template placeholder `{{ audit_verification_block }}` may need a renderer.
    mitigation: Check if render function exists; if not, render empty string or stub block.
  - risk: complete_revision frontmatter update diverges from delta pattern.
    mitigation: Reuse or extract shared frontmatter status update logic.
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-039.PHASE-02
```

# Phase 02 — Command Surface Completion

## 1. Objective
Add first-class `create audit` and `complete revision` CLI commands so these
lifecycle flows are discoverable and executable without ad-hoc file scaffolding.

## 2. Links & References
- **Delta**: DE-039
- **Design Revision**: DR-039 §4 (code impact table: `cli/create.py`, `cli/complete.py`)
- **Specs / PRODs**:
  - PROD-016.FR-010 — first-class create/complete command coverage
- **Existing Infrastructure**:
  - Audit template: `supekku/templates/audit.md`
  - Audit metadata schema: `supekku/scripts/lib/core/frontmatter_metadata/audit.py`
  - ChangeRegistry audit support: `supekku/scripts/lib/changes/registry.py` (kind=audit, prefix=AUD-, dir=change/audits/)
  - Change lifecycle: `supekku/scripts/lib/changes/lifecycle.py`
  - Revision creation pattern: `supekku/scripts/lib/changes/creation.py:73-140`

## 3. Entrance Criteria
- [x] Phase 1 complete — commit `aee0446`
- [x] Audit template exists at `supekku/templates/audit.md`
- [x] ChangeRegistry already handles `kind="audit"` with `AUD-` prefix

## 4. Exit Criteria / Done When
- [ ] `create audit` command creates `AUD-NNN` directory under `change/audits/`
- [ ] `complete revision` command transitions revision status to `completed`
- [ ] Tests pass for both command flows
- [ ] `just lint` and `just pylint` clean on changed files

## 5. Verification
- `uv run pytest -q` on new/updated test files
- `uv run ruff check` on all changed files
- `uv run pylint --indent-string "  "` on new modules
- Evidence: VT-039-003 test output

## 6. Assumptions & STOP Conditions
- Assumptions: no new lifecycle statuses needed; `completed` is the target status for both.
- STOP when: audit verification block rendering requires substantial new infrastructure (escalate).

## 7. Tasks & Progress
*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 2.1 | Add `create_audit()` in `changes/creation.py` | [x] | Follows `create_revision()` pattern; renders `audit_verification_block=""` |
| [x] | 2.2 | Add `create audit` CLI command in `cli/create.py` | [ ] | Thin: title + --spec/--prod/--code-scope → create_audit() |
| [x] | 2.3 | Add `complete_revision()` domain function | [x] | In `completion.py`; extracted `_update_artifact_frontmatter_status()` helper |
| [x] | 2.4 | Add `complete revision` CLI in `cli/complete.py` | [ ] | Thin: revision_id + --force → complete_revision_impl() |
| [x] | 2.5 | Write tests for both flows | [ ] | 16 new tests: 4 audit creation, 7 complete_revision domain, 5 CLI |
| [x] | 2.6 | Run verification, lint, update evidence | [ ] | 2226 pass, 0 fail; ruff clean; pylint 9.82/10 (no new warnings) |

### Task Details

- **2.1 — Add `create_audit()` in `changes/creation.py`**
  - **Pattern**: Follow `create_revision()` (lines 73–140). Same ID allocation via `_next_identifier(base_dir, "AUD")`.
  - **Directory**: `change/audits/AUD-NNN-slug/`
  - **Frontmatter fields** (from `supekku/scripts/lib/core/frontmatter_metadata/audit.py`):
    - `id`, `slug`, `name`, `created`, `updated`, `status: draft`, `kind: audit`
    - `spec_refs` (list), `prod_refs` (list), `code_scope` (list) — from CLI args
    - `audit_window`, `findings`, `patch_level`, `next_actions` — leave empty/default
  - **Template**: Load `audit.md` via `_get_template_path()`, render with Jinja2.
  - **`{{ audit_verification_block }}`**: Render as empty string initially (or a stub coverage block if `render_verification_coverage_block` can be reused with audit subject).
  - **Return**: `ChangeArtifactCreated(artifact_id="AUD-NNN", ...)`
  - **Export**: Add `create_audit` to `__all__`.

- **2.2 — Add `create audit` CLI command in `cli/create.py`**
  - **Signature**: `@app.command("audit")` with args:
    - `title: str` (positional) — audit title/name
    - `--spec` (repeatable) — spec refs
    - `--prod` (repeatable) — prod refs
    - `--code-scope` (repeatable) — code scope globs
  - **Body**: Call `create_audit(title, spec_refs=specs, prod_refs=prods, code_scope=code_scope)`, print result.
  - **Import**: Add `create_audit` to the import from `changes.creation`.
  - **Keep CLI thin** — no business logic, just arg parsing → domain call → output.

- **2.3 — Add `complete_revision()` domain function**
  - **Location**: New function in a suitable module. Options:
    - Add to `supekku/scripts/lib/changes/completion.py` (already has completion logic), OR
    - Create thin `supekku/scripts/complete_revision.py` script (mirrors `complete_delta.py` pattern)
  - **Recommended**: Add `complete_revision(revision_id, *, force=False) -> int` to `completion.py`.
  - **Logic**:
    1. Find revision file via ChangeRegistry (`kind="revision"`).
    2. Read frontmatter, validate status allows completion (`draft` or `in-progress`).
    3. Update frontmatter `status` to `completed` + `updated` to today.
    4. Write back. Sync registry.
  - **Reuse**: The frontmatter status update pattern in `complete_delta.py:update_delta_frontmatter()` (lines 191–224) can be extracted or duplicated for revision. Keep it simple — a parallel function is fine for now; extract shared helper only if a third artifact type needs it.

- **2.4 — Add `complete revision` CLI command in `cli/complete.py`**
  - **Signature**: `@app.command("revision")` with args:
    - `revision_id: str` (positional) — e.g., `RE-015`
    - `--force / -f` — skip prompts
  - **Body**: Call domain function, print result.
  - **Keep CLI thin.**

- **2.5 — Write tests**
  - **`create_audit` tests** (in `supekku/scripts/lib/changes/creation_test.py` or new file):
    - Creates `AUD-NNN` directory and file with correct frontmatter
    - Handles spec_refs, prod_refs, code_scope args
    - ID auto-increments correctly
  - **`complete_revision` tests**:
    - Transitions draft → completed
    - Rejects already-completed revision (or idempotent)
    - Revision not found → error
  - **CLI tests** (in `supekku/cli/create_test.py` and `supekku/cli/complete_test.py`):
    - Smoke tests via typer test runner

- **2.6 — Verification**
  - Run `just lint` + `just pylint` on all changed files.
  - Run `just test` for full suite.
  - Update VT-039-003 status to `verified` in IP-039.
  - Update this phase sheet with evidence and task notes.

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| Audit template placeholder needs block renderer | Render empty string — no infrastructure needed | Resolved |
| Frontmatter update duplication across delta/revision | Extracted `_update_artifact_frontmatter_status()` in `completion.py` — reusable if third artifact type needs it | Resolved |

## 9. Decisions & Outcomes
- `audit_verification_block` rendered as empty string — sufficient for now; can be enhanced later.
- `complete_revision()` placed in `completion.py` alongside `create_completion_revision()`.
- Extracted `_update_artifact_frontmatter_status()` as a reusable helper (updates both `status` and `updated` date). Could replace `update_delta_frontmatter()` in `complete_delta.py` in a future cleanup pass.
- `complete_revision` is idempotent: already-completed revisions return success.

## 10. Findings / Research Notes
- `create_revision()` at `creation.py:73-140` is the canonical pattern for `create_audit()`.
- Audit statuses in template include `in-review` which is non-standard vs lifecycle.py — use `draft` as initial status regardless.
- `complete_delta.py:update_delta_frontmatter()` is the pattern for frontmatter status transition.
- `_update_artifact_frontmatter_status()` is strictly better: also updates the `updated:` field.

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied
- [x] Verification evidence stored (2226 pass, ruff clean, pylint 9.82)
- [ ] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
