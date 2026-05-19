---
id: IP-136-P02
slug: "136-metadata_schema_consolidation_program_propagate_adr_010_across_artefacts_and_close_prod_004-phase-02"
name: IP-136 Phase 02 — Foundations gate (DE-118 + DE-137 verification)
created: "2026-05-19"
updated: "2026-05-19"
status: draft
kind: phase
plan: IP-136
delta: DE-136
---

# Phase 2 — Foundations gate (DE-118 + DE-137 verification)

## 1. Objective

Confirm the foundations program tier landed: both child deltas DE-118 (block validator unification) and DE-137 (cross-cutting infrastructure) closed, and their cross-cutting outputs operational end-to-end. This phase is synthesis/gate work — no new implementation; it verifies the foundations are ready for Phase 3's per-artefact propagation sequence (DE-138 → DE-142).

The F-E entrance check (DE-118 strict-mode parameterisation vs DR-136 §5.2 tolerant-on-read posture) is the primary risk surface; this phase resolves whether DE-137 already restored the strict flag or whether a follow-up is required before Phase 3 begins.

## 2. Links & References

- **Delta**: DE-136
- **Design Revision Sections**:
  - DR-136 §3 (architecture intent — validation layer split strict/tolerant)
  - DR-136 §5 (cross-cutting deliverables Y/Z/X + `validate file` + `validate --kind` + skill tuning + `admin migrate`)
  - DR-136 §11.1 (architectural separation: `validation/` ↔ `migrations/` boundary)
  - DR-136 §13.1 (verification roll-up acceptance)
- **Specs / PRODs**: PROD-004.FR-001..FR-007, PROD-004.NF-001 (rolled up to umbrella audit VA-DE136-CLOSE-001 at Phase 4; spot-checked here)
- **Support Docs**:
  - DE-118 close: `.spec-driver/deltas/DE-118-*/`
  - DE-137 close: `.spec-driver/deltas/DE-137-*/` (RE-041 — DE-137 completion revision)
  - `notes.md` Phase 1 child-delta map + coordination notes (F-E, F-F)
  - AUD-026 (DE-137 conformance audit) for cross-cutting deliverable evidence

## 3. Entrance Criteria

- [x] Phase 1 completed (2026-05-09; child deltas DE-137..DE-142 drafted)
- [x] DE-118 `completed`
- [x] DE-137 `completed` (closure committed 2026-05-19, RE-041 + AUD-026 attached)
- [ ] DE-136 transitioned to `in-progress` (already in-progress from Phase 1 — confirm at phase entry)

## 4. Exit Criteria / Done When

- [ ] DE-118 and DE-137 both `completed` (state-check; already true at entry)
- [ ] F-E resolved: `MetadataValidator.validate(strict: bool)` parameterisation present; loaders default tolerant, `validate` CLI passes strict per DR-136 §5.2. If DE-118 left rejection unconditional and DE-137 did not restore it, this is the blocker and a follow-up child task/issue is required before Phase 3.
- [ ] DR-136 §5 cross-cutting deliverables operational (smoke-check):
  - [ ] `spec-driver schema enums` (X) — lists kinds with controlled-vocab fields; per-kind and per-field forms return canonical + aliases
  - [ ] `spec-driver validate file <path>` (§5.4) — single-file validation returns `path:line:col: severity: message` and non-zero exit on error
  - [ ] `spec-driver validate --kind <kind>` (§5.4a) — per-kind sweep filter composes with `--strict`, `--fix`, `--no-tolerated-aliases`
  - [ ] `spec-driver admin regenerate-templates` (Y) — idempotent run preserves enum-comment hints in template frontmatter
  - [ ] `spec-driver validate templates` — passes on current corpus
  - [ ] `spec-driver admin migrate --check` / `--list` (§5.6) — orchestrator surfaces pending vs applied migrations per kind
  - [ ] Skill gates (§5.5) — `execute-phase`, `close-change`, `audit-change`, `notes`, `update-delta-docs` carry the verbatim `validate`/`sync` insertion targets
- [ ] `workflow.toml` schema additions present and operational: `[validation.strict]` per-kind flags + `[schema_version]` per-kind state
- [ ] New-install strict-on default verified (DR-136 §11.3) — fresh `spec-driver install` writes strict-mode on per kind in the new `workflow.toml`
- [ ] No new design questions raised that block Phase 3 entry; any gaps surfaced are recorded as scope-notes against the relevant per-artefact child delta (DE-138..DE-142) or filed as ISSUE-*
- [ ] Phase 2 evidence captured in §10; IP-136 §9 Phase 2 row marked complete; phase status `completed`

## 5. Verification

- **Tooling/commands** (one pass; failures are exit-criteria blockers):
  - `uv run spec-driver show delta DE-118` / `DE-137` — confirm `status: completed`
  - `uv run spec-driver schema enums` and `… schema enums delta` and `… schema enums delta.status`
  - `uv run spec-driver validate file .spec-driver/deltas/DE-136-*/DE-136.md`
  - `uv run spec-driver validate --kind delta`
  - `uv run spec-driver validate --kind delta --strict`
  - `uv run spec-driver admin regenerate-templates` (followed by a re-run to confirm idempotence; inspect template frontmatter retains `# one of: …` enum hints)
  - `uv run spec-driver validate templates`
  - `uv run spec-driver admin migrate --check` and `… --list`
  - `uv run spec-driver validate --strict` (workspace baseline — expect only audit-gate warnings on remaining draft child deltas DE-138..DE-142)
  - F-E source check: `grep -n "def validate" supekku/scripts/lib/validation/*.py` (or equivalent) to confirm strict-mode parameter exists and tolerant-on-read default in loader paths
  - Skill-gate text check: read `.claude/skills/{execute-phase,close-change,audit-change,notes,update-delta-docs}/SKILL.md` and confirm DR-136 §5.5 insertion targets present
  - `workflow.toml` check: `grep -n "validation.strict\|schema_version" workflow.toml` confirms blocks; fresh `spec-driver install` to a temp dir confirms strict-on default for new installs
- **Evidence to capture** (§10):
  - Resolution of F-E (one of: strict flag present from DE-118; restored in DE-137; outstanding → blocker)
  - Command output snippets demonstrating each §5 deliverable functioning
  - Confirmation that AUD-026 covered the deliverables this phase re-checks (avoid duplicate audit work)
- **Tests**: no new VT/VA created in Phase 2. VTs for cross-cutting deliverables live in DE-137 (VT-CC-001..VT-CC-027 per AUD-026); program-level VA-DE136-CLOSE-001 fires in Phase 4.

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - DE-137 closure already exercised the §5 deliverables (AUD-026 conformance audit reconciled). Phase 2's smoke-checks are confirmation, not re-litigation.
  - DE-118 closed cleanly — its `MetadataValidator` posture is the only DE-118 surface relevant to this phase (F-E).
  - No per-artefact child delta (DE-138..DE-142) has begun substantive work yet; Phase 3 entry transitions them into execution sequence.
- **STOP when**:
  - F-E resolves to "DE-118 lands unconditional rejection AND DE-137 did not restore the strict flag" — pause; file as a blocker (issue + follow-up delta or DE-137 reopening) before Phase 3.
  - A §5 deliverable smoke-check fails in a way AUD-026 did not anticipate — file ISSUE-*, raise via `/consult` before continuing.
  - `workflow.toml` strict-mode schema additions are missing or incompatible with DR-136 §11.3 — pause; route to `/consult`.
  - Any skill-gate insertion target (§5.5) is missing — file as a DE-137 follow-up rather than absorbing here.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description                                                                       | Parallel? | Notes |
| ------ | --- | --------------------------------------------------------------------------------- | --------- | ----- |
| [ ]    | 2.1 | State-check DE-118 + DE-137 closed; transition DE-136 to in-progress confirmed   | [ ]       | Read-only |
| [ ]    | 2.2 | Resolve F-E: strict-mode parameterisation present and correctly defaulted        | [ ]       | Highest-risk task |
| [ ]    | 2.3 | Smoke-check DR-136 §5.3 (`schema enums`) end-to-end                              | [P]       | |
| [ ]    | 2.4 | Smoke-check DR-136 §5.4 (`validate file`) end-to-end                             | [P]       | |
| [ ]    | 2.5 | Smoke-check DR-136 §5.4a (`validate --kind`) composes with strict/fix flags     | [P]       | |
| [ ]    | 2.6 | Smoke-check DR-136 §5.1 (template regen + `validate templates`) idempotent      | [P]       | |
| [ ]    | 2.7 | Smoke-check DR-136 §5.6 (`admin migrate --check`/`--list`)                       | [P]       | |
| [ ]    | 2.8 | Confirm DR-136 §5.5 skill-gate insertions present verbatim                       | [P]       | |
| [ ]    | 2.9 | Confirm `workflow.toml` `[validation.strict]` + `[schema_version]` blocks + new-install strict-on default | [ ] | DR-136 §11.3 |
| [ ]    | 2.10 | Workspace `validate --strict` baseline matches expectation (audit-gate warnings only on draft children DE-138..DE-142) | [ ] | Fail-loud if new errors |
| [ ]    | 2.11 | Phase wrap: capture evidence in §10, update IP-136 §9, transition phase to `completed` | [ ] | Hand-off to Phase 3 |

### Task Details

- **2.1 State-check + delta status**
  - **Design / Approach**: `show delta DE-118`, `show delta DE-137`; both `completed`. Confirm DE-136 status is `in-progress` (carried from Phase 1).
  - **Testing**: state read-out only.

- **2.2 Resolve F-E (highest-risk)**
  - **Design / Approach**: Read `MetadataValidator` source; locate `validate(...)`. Confirm a `strict: bool=False` (or equivalent) parameter exists, loaders pass `strict=False`, and the `validate` CLI passes `strict=True`. Cross-reference DE-118 close notes and DE-137 close notes / AUD-026 to identify which delta landed the parameterisation.
  - **Files / Components**: `supekku/scripts/lib/validation/`, `supekku/scripts/lib/core/frontmatter_metadata/`, DE-118 and DE-137 phase sheets.
  - **Testing**: run `validate --strict` and `validate` (tolerant) on a fixture with a known alias — strict should flag, tolerant should normalise silently.
  - **STOP**: if neither delta parameterised strict-mode, halt and `/consult`.

- **2.3–2.8 Cross-cutting deliverable smoke-checks (parallelisable)**
  - **Design / Approach**: Per deliverable, run the verification command from §5; capture stdout snippet + non-zero behaviour where expected. Cross-reference AUD-026 to confirm each was covered by its VT-CC-* test; smoke-check is to verify operational rather than re-run the conformance test.
  - **Files / Components**: invocations only.
  - **Testing**: command output; no code changes.

- **2.9 `workflow.toml` schema + new-install default**
  - **Design / Approach**: Grep project `workflow.toml` for the two blocks. For new-install default, run `spec-driver install` into a tempdir (or inspect the installer template) and confirm strict-on per kind. DR-136 §11.3 names this as the consumer-repo migration boundary.
  - **Files / Components**: `workflow.toml`, installer templates under `supekku/templates/` and install path.
  - **Testing**: tempdir install + diff against current project `workflow.toml`.

- **2.10 Workspace baseline**
  - **Design / Approach**: `uv run spec-driver validate --strict` from repo root. Expected: only audit-gate warnings on draft child deltas DE-138..DE-142. Any new error class is a blocker.
  - **Testing**: command output saved as evidence.

- **2.11 Phase wrap**
  - **Design / Approach**: write §10 evidence, update IP-136 §9 row for Phase 2, transition phase status to `completed`, write a brief hand-off note for Phase 3 (which child delta enters first per DEC-004 sequence: DE-138).
  - **Files / Components**: this file, `IP-136.md`, `notes.md` (optional cross-link).
  - **Testing**: `uv run spec-driver validate file phases/phase-02.md` per `/execute-phase` skill gate.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| ---- | ---------- | ------ |
| F-E unresolved: DE-118 + DE-137 both shipped without restoring tolerant-on-read default; loaders break against unmigrated DE-138..DE-142 fixtures at Phase 3 start | Task 2.2 is the explicit gate; STOP routes to `/consult` and a follow-up. Phase 3 cannot enter until resolved. | open |
| AUD-026 missed a §5 deliverable surface; smoke-check uncovers a gap | File ISSUE-* + DE-137 follow-up; do not absorb fix into Phase 2 | open |
| `workflow.toml` schema additions land project-side but not in installer template (new-install regression) | Task 2.9 splits in-repo vs new-install checks; new-install default verified in tempdir | open |
| Skill-gate insertions drifted from DR-136 §5.5 verbatim text during DE-137 close | Task 2.8 compares verbatim insertion targets to skill SKILL.md content | open |

## 9. Decisions & Outcomes

- `2026-05-19` — Phase 2 is synthesis/gate work, not implementation. AUD-026 (DE-137 conformance audit) is the primary evidence source; smoke-checks confirm operational state, not re-run conformance tests.

## 10. Findings / Research Notes

- _(Evidence captured at task completion: F-E resolution, command snippets per §5 deliverable, `workflow.toml` and new-install verification, baseline `validate --strict` output.)_

## 11. Wrap-up Checklist

- [ ] Exit criteria (§4) satisfied
- [ ] Verification evidence (§10) stored
- [ ] IP-136 §9 Phase 2 row marked complete
- [ ] F-E resolution documented (one of: present from DE-118 / restored in DE-137 / open blocker filed)
- [ ] Hand-off note for Phase 3: DE-138 (delta per-artefact propagation) enters first per DR-136 DEC-004; carries no inherited scope-notes; sets precedent for siblings
- [ ] `uv run spec-driver validate file phases/phase-02.md` clean
