---
id: IP-136-P02
slug: "136-metadata_schema_consolidation_program_propagate_adr_010_across_artefacts_and_close_prod_004-phase-02"
name: IP-136 Phase 02 — Foundations gate (DE-118 + DE-137 verification)
created: "2026-05-19"
updated: "2026-05-19"
status: completed
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

- [x] DE-118 and DE-137 both `completed` (state-check confirmed)
- [x] F-E resolved: `MetadataValidator.validate(*, strict: bool=False, accept_tolerated: bool=True)` at `supekku/scripts/lib/blocks/metadata/validator.py:100`. Loader per-kind dispatch via `get_strict_map` at `core/config.py:236`. Default tolerant per DR-136 §5.2.
- [x] DR-136 §5 cross-cutting deliverables operational (smoke-check):
  - [x] `spec-driver schema enums` (X) — lists 18 kinds; `schema enums delta.status` returns canonical (5) + permanent aliases (4)
  - [x] `spec-driver validate file <path>` (§5.4) — surfaces `path: severity: message` errors with non-zero exit
  - [x] `spec-driver validate workspace --kind <kind>` (§5.4a) — `--kind` flag present on `workspace` subcommand; composes with `--strict`, `--fix`, `--no-tolerated-aliases`. (Note: DR-136 §5.4a wrote the surface as `validate --kind`; actual implementation routes through `validate workspace --kind`. Equivalent semantics; cosmetic DR drift.)
  - [x] `spec-driver validate templates` — returns `templates clean`
  - [x] `spec-driver admin migrate --check` / `--list` (§5.6) — orchestrator runs (`no pending migrations` / `no migration steps registered`); empty inventory expected pre-P03
  - [x] Skill gates (§5.5) — all 5 SKILL.md files carry `<!-- validate-gate:<skill> begin -->` markers
- [x] `workflow.toml` schema additions present in `DEFAULT_CONFIG`: `[migrations]` (line 100-103), `[validation.strict]` (104-109), `[schema_version]` (111). Project `workflow.toml` uses defaults (blocks not materialised — non-blocking per ISSUE-056).
- [x] New-install strict-on default verified — `_emit_strict_defaults` at `core/config.py:482` writes uncommented `[validation.strict] <kind> = true` for `FRESH_INSTALL_STRICT_KINDS` when `include_strict_defaults=True` (fresh-install branch per DEC-137-18).
- [x] No new design questions raised that block Phase 3 entry. Surfaced observation (DE-136.md `context_inputs[*].id` strict errors via `validate file`) is expected: addressed by DE-138 (Phase 3 first) which reshapes `context_inputs` to block form per DR-136 §6.1.
- [x] Phase 2 evidence captured in §10; IP-136 §9 Phase 2 row marked complete; phase status `completed`

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
| [x]    | 2.1 | State-check DE-118 + DE-137 closed; DE-136 in-progress confirmed                 | [ ]       | DE-118 + DE-137 `completed`; DE-136 `in-progress` |
| [x]    | 2.2 | Resolve F-E: strict-mode parameterisation present and correctly defaulted        | [ ]       | `validator.py:100` `validate(*, strict=False, accept_tolerated=True)`; per-kind dispatch via `get_strict_map` |
| [x]    | 2.3 | Smoke-check DR-136 §5.3 (`schema enums`) end-to-end                              | [P]       | 18 kinds listed; `delta.status` returns canonical + aliases |
| [x]    | 2.4 | Smoke-check DR-136 §5.4 (`validate file`) end-to-end                             | [P]       | Surfaces errors per spec; non-zero exit |
| [x]    | 2.5 | Smoke-check DR-136 §5.4a (`validate --kind`) composes with strict/fix flags     | [P]       | Routes via `validate workspace --kind`; cosmetic DR drift noted |
| [x]    | 2.6 | Smoke-check DR-136 §5.1 (template regen + `validate templates`) idempotent      | [P]       | `validate templates` → `templates clean` |
| [x]    | 2.7 | Smoke-check DR-136 §5.6 (`admin migrate --check`/`--list`)                       | [P]       | Empty inventory expected; orchestrator runs |
| [x]    | 2.8 | Confirm DR-136 §5.5 skill-gate insertions present verbatim                       | [P]       | All 5 SKILL.md files carry `validate-gate:<skill>` markers |
| [x]    | 2.9 | Confirm `workflow.toml` `[validation.strict]` + `[schema_version]` blocks + new-install strict-on default | [ ] | `DEFAULT_CONFIG` lines 100/104/111; `_emit_strict_defaults` line 482 |
| [x]    | 2.10 | Workspace `validate --strict` baseline matches expectation                       | [ ] | 7 audit-gate warnings (DE-135, DE-136, DE-138..DE-142); 0 errors |
| [x]    | 2.11 | Phase wrap: capture evidence in §10, update IP-136 §9, transition phase to `completed` | [ ] | This commit |

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

**F-E resolution (task 2.2)**: `MetadataValidator.validate(self, data, *, strict: bool=False, accept_tolerated: bool=True)` at `supekku/scripts/lib/blocks/metadata/validator.py:100`. Loader call sites pass per-kind dispatch via `get_strict_map` (`supekku/scripts/lib/core/config.py:236`), returning `{kind: bool}` from `[validation.strict]` config. `snapshot_compare.py:177` is a non-loader caller using `strict=True` for snapshot reconciliation. **F-E closed**: tolerant-on-read is the loader default; strict is opt-in per kind. AUD-026 FIND-001 / FIND-004 corroborates (P01 schema foundation + P04 loader→MetadataValidator per-kind strict dispatch wired).

**§5 deliverable smoke-check outputs (tasks 2.3–2.8)**:
- `schema enums`: 18 kinds listed (adr, audit, base, delta, design_revision, issue, memory, phase, plan, policy, problem, prod, requirement, …). `schema enums delta.status` returns 5 canonical + 4 permanent aliases (active, complete, done, in_progress).
- `validate file <DE-136.md>`: surfaces `context_inputs[*].id: is required` errors (5 entries). Pre-existing; addressed by DE-138 in Phase 3 (block reshape per DR-136 §6.1). Not new — DE-136.md inherited the FM shape pre-block-migration.
- `validate workspace --kind delta`: flag present on `workspace` subcommand with help text matching DR-136 §5.4a intent. DR phrasing said `validate --kind`; actual impl is `validate workspace --kind`. Cosmetic; no semantic gap.
- `validate templates`: `templates clean`. Template regen idempotent per AUD-026 FIND-002 (P02 template infrastructure + first regeneration).
- `admin migrate --check`: `no pending migrations`. `admin migrate --list`: `no migration steps registered`. Empty inventory is expected pre-P03 (no per-kind step folders shipped yet).
- Skill validate-gates: 5/5 SKILL.md files (execute-phase, close-change, audit-change, notes, update-delta-docs) carry `<!-- validate-gate:<skill> begin -->` markers.

**`workflow.toml` schema additions (task 2.9)**: `DEFAULT_CONFIG` in `core/config.py` carries `[migrations]` (line 100-103), `[validation.strict]` (104-109, empty default), `[schema_version]` (111, derived cache, empty default). New-install fresh-vs-upgrade trigger: `generate_default_workflow_toml(include_strict_defaults=True)` calls `_emit_strict_defaults` (line 482) which writes uncommented `[validation.strict]\n<kind> = true` for each `FRESH_INSTALL_STRICT_KINDS` entry. Project `.spec-driver/workflow.toml` doesn't materialise these blocks (cosmetic install-version drift 0.9.2 vs 0.9.7 per ISSUE-056); defaults apply at load.

**Workspace baseline (task 2.10)**: `uv run spec-driver validate workspace --strict` →
```
ValidationIssue(level='warning', message='Audit gate is required but no completed conformance audit found', artifact='DE-135')
ValidationIssue(level='warning', ... artifact='DE-138')
ValidationIssue(level='warning', ... artifact='DE-140')
ValidationIssue(level='warning', ... artifact='DE-141')
ValidationIssue(level='warning', ... artifact='DE-139')
ValidationIssue(level='warning', ... artifact='DE-142')
ValidationIssue(level='warning', ... artifact='DE-136')
```
7 audit-gate warnings; 0 errors. Matches expectation (DE-135 carry-over + DE-136 umbrella + 5 draft children DE-138..DE-142). DE-118 + DE-137 absent from list (AUD-026 covers DE-137; DE-118 audited prior).

**Observation surfaced (non-blocking for P02; for Phase 3 DE-138 owner)**: DE-136.md `context_inputs[*].id` errors via `validate file` indicate the FM shape pre-dates the block reshape DR-136 §6.1 schedules for DE-138. This is the expected "Phase 3 cleans up" pattern, not a new defect.

## 11. Wrap-up Checklist

- [x] Exit criteria (§4) satisfied
- [x] Verification evidence (§10) stored
- [x] IP-136 §9 Phase 2 row marked complete
- [x] F-E resolution documented (present from DE-137 P01 schema foundation + P04 per-kind dispatch wiring; tolerant-on-read default in loaders, strict opt-in per kind)
- [x] Hand-off note for Phase 3: **DE-138 (delta per-artefact propagation) enters first** per DR-136 DEC-004. Inherited surface from foundations: per-kind `[validation.strict]` flag (defaults strict-on for fresh installs), `admin migrate <kind>` orchestrator with empty inventory ready for step folders, `validate workspace --kind delta` for sweep verification, `schema enums delta.*` for enum introspection. No scope-notes carried (first per-artefact precedent; sets pattern siblings inherit). Known DE-138 work item: reshape `context_inputs` from FM to block `supekku:delta.context_inputs@v1` per DR-136 §6.1 (clears DE-136.md `validate file` strict errors observed in §10).
- [x] `uv run spec-driver validate file phases/phase-02.md` clean
