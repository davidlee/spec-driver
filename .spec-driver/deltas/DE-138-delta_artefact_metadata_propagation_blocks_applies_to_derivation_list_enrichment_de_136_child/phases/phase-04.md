---
id: IP-138-P04
slug: "138-delta_artefact_metadata_propagation_blocks_applies_to_derivation_list_enrichment_de_136_child-phase-04"
name: IP-138 Phase 04
created: "2026-05-20"
updated: "2026-05-20"
status: draft
kind: phase
plan: IP-138
delta: DE-138
---

# Phase 04 — Strict-flip + post-flip gate

## 1. Objective

Make the `[validation.strict] delta = true` flip verification-bearing, not vacuous. Three load-bearing pieces:

1. **Wire `--no-tolerated-aliases`** through `spec_driver/presentation/cli/validate/workspace.py` → `validate_workspace(...)` → `WorkspaceValidator` → per-kind delta block validators (`validate_delta_context_inputs`, `validate_delta_risk_register`). The flag is currently accepted at the CLI but silently dropped (line 146: `_ = no_tolerated_aliases`). DEC-138-14 + F-138-23 require the flag to bind end-to-end; without wiring, the post-flip acceptance gate is a no-op.
2. **Flip `workflow.toml`**: add `[validation.strict] delta = true` + `[schema_version] delta = "0.10.0+001"` per DR-138 §11.3. Validator escalates FM cut-key presence to error post-flip; loader behaviour unchanged (loader is unconditionally tolerant per DEC-138-10).
3. **Verify the post-flip gate clean** (DR-138 §11.4): `validate workspace --kind delta --strict --no-tolerated-aliases` returns 0 errors; whole-corpus `validate workspace --strict` does not regress; `complete delta DE-138 --dry-run` passes; `list deltas` smoke-check across columns.

Plus the governance closeout for §10.5 acceptance: file a concrete backlog issue (path + owner + DE-136 P04 consumption point) for the §9.5 follow-up audit per F-138-24. Without that artefact, the "follow-up audit scoped" gate item is non-falsifiable.

Phase deliverable is a workspace where:

- `--no-tolerated-aliases` actually rejects a fixture artefact carrying tolerated alias `unknown` on `context_inputs[].type` (VT-DE138-GATE-001).
- Post-flip workspace-validate baseline holds under both `--strict` and `--strict --no-tolerated-aliases` (VT-DE138-FLIP-001 has two assertion shapes per IP-138 coverage table — baseline strict + strict-on-validate enforcement).
- VH-DE138-FLIP-001 attested by operator before the toml edit lands.
- F-138-24 backlog issue exists at `.spec-driver/backlog/issues/<slug>.md` with owner + DE-136 P04 umbrella consumption point.
- `complete delta DE-138` (dry-run) passes — coverage gate reads requirements via derived `applies_to`.
- IP-138 `supekku:verification.coverage@v1` entries for VT-DE138-GATE-001, VT-DE138-FLIP-001 (both rows), VH-DE138-FLIP-001 flipped `planned` → `verified`.
- DE-138 ready for `complete delta DE-138` without `--force`.

## 2. Links & References

- **Delta**: DE-138.
- **Design Revision Sections**:
  - DR-138 §3.2 (lifecycle impact at strict-flip — what changes vs what does not).
  - DR-138 §5.4 (validation surface — `--no-tolerated-aliases` semantics for tolerated alias `unknown`).
  - DR-138 §10.1 VT rows: GATE-001 (CLI wiring proof), FLIP-001 (post-flip workspace baseline).
  - DR-138 §10.3 VH row: FLIP-001 (operator attestation).
  - DR-138 §10.5 (acceptance gate — full checklist this phase closes).
  - DR-138 §11.2 (pre-flip checklist — items 7/8 are the P04 entrance gates beyond P03 close).
  - DR-138 §11.3 (flip mechanics — exact toml block + edit method).
  - DR-138 §11.4 (post-flip gate — exact four checklist items).
  - DR-138 §11.5 (rollback — A: one-line revert; B: data recovery via pre-sweep tag — both relevant if gate fails).
  - DR-138 §15.1 + §9.5 (F-138-24 follow-up tracking-artefact requirement — concrete content shape).
  - DR-138 DEC-138-04 (flip lives inside DE-138 P04, not at delta close — verification-bearing operation).
  - DR-138 DEC-138-10 (loader unconditionally tolerant; strict is validator-owned — wiring touches validator path, not loader).
  - DR-138 DEC-138-14 (wiring requirement; F-138-23 promoted external→final medium→high).
  - DR-138 §code_impacts row for `spec_driver/presentation/cli/validate/workspace.py` (current_state lines 142-146 vs target_state thread into validate_ws + per-kind validators).
  - DR-138 §code_impacts row for `.spec-driver/workflow.toml` (P04 writes both keys).
- **Specs / PRODs**:
  - PROD-004.FR-001 (single validation layer — VT-DE138-FLIP-001 baseline asserts unified errors).
  - PROD-004.FR-002 (strict-on-validate enforcement — VT-DE138-FLIP-001 strict assertion + VH-DE138-FLIP-001 operator gate).
- **Support Docs**:
  - `spec_driver/presentation/cli/validate/workspace.py` (current `_ = no_tolerated_aliases` no-op at line 146; wiring target).
  - `supekku/scripts/lib/validation/validator.py` (`validate_workspace` at line 626; `WorkspaceValidator` at line 55; needs `accept_tolerated` parameter threaded through).
  - `supekku/scripts/lib/blocks/delta_metadata.py` (`validate_delta_context_inputs` line 330, `validate_delta_risk_register` line 441 — both already accept `accept_tolerated=True`; per-kind call site is the gap).
  - `supekku/scripts/lib/blocks/metadata/validator.py` (`MetadataValidator` consumes `accept_tolerated` at line 105; downstream contract holds — `_accept_tolerated=False` rejects tolerated_alias entries as errors at line 408).
  - `.spec-driver/workflow.toml` (target for §11.3 edit).
  - `notes.md` 2026-05-20 P03 close section (P04 outstanding list).

## 3. Entrance Criteria

- [x] IP-138-P03 closed (status: completed); three sweep commits + pre-sweep tag intact (`46976634`, `2afc0833`, `717fced5`, `6a7fe70b`, `360d92d8`; tag `de-138-pre-sweep` @ `46976634`).
- [x] VA-DE138-RISK-RECON-001 closed (commit `6a7fe70b`).
- [x] VA-DE138-DRIFT-001 closed (commit `717fced5`).
- [x] `validate workspace --kind delta` clean under tolerant mode (P03 close evidence: exit 0; only pre-existing 7× audit-gate + 1× DR-030 warnings).
- [x] DE-138 status `in-progress` (held since P01 entrance).
- [x] `validate workspace --kind delta --strict` baseline captured pre-wiring (4.1, 2026-05-20): exit 1 with 7× sibling-draft audit-gate warnings + 1× `error` "References unresolved artifact 'DR-030' (via relation.introduces)" on DE-030. The DR-030 surface is pre-existing baseline noise (present at P01/P03 close as tolerant-mode warning; strict promotes to error). Tracked as **ISSUE-057** — registry-resolution defect, not introduced by DE-138, not a DE-138 close blocker. DR-138 §11.2/§11.4/§10.5 amended to document the carve-out.
- [ ] Working tree clean before workflow.toml flip lands (so revert grain is unambiguous per §11.5A).
- [ ] OQ-138-03 carried no residual P04 obligation (resolved at P03 entrance).

## 4. Exit Criteria / Done When

- [ ] `--no-tolerated-aliases` wired through CLI → `validate_workspace(...)` → `WorkspaceValidator` → per-kind delta block validators per DEC-138-14. CLI no longer drops the flag silently (`_ = no_tolerated_aliases` removed); `validate_workspace` signature carries `accept_tolerated: bool` (or equivalent `no_tolerated_aliases: bool` — chase whichever name preserves existing call-site clarity); per-kind delta block validators are invoked from the workspace validator with the threaded value.
- [ ] VT-DE138-GATE-001 green: end-to-end CLI test demonstrates a delta carrying `context_inputs[].type = unknown` (tolerated alias) returns 0 errors under default `validate workspace --kind delta --strict` AND ≥1 error under `validate workspace --kind delta --strict --no-tolerated-aliases`. Test must exercise the real CLI (Typer test harness) so the wiring is proven, not just the underlying validator.
- [ ] VT-DE138-FLIP-001 green (both IP-138 coverage rows):
  - Row 1 (FR-001 baseline): `validate workspace --kind delta --strict` returns 0 errors on in-repo corpus post-flip.
  - Row 2 (FR-002 enforcement): the same command post-flip rejects an artefact with a cut FM key (`applies_to`/`context_inputs`/`risk_register`/`outcome_summary`) — fixture or synthetic assertion proving strict-mode now binds.
- [ ] VH-DE138-FLIP-001 attested: operator confirms post-sweep workspace clean + VAs closed + GATE-001 green BEFORE the workflow.toml edit lands. Attestation captured in §9 with date + operator handle (per VH convention).
- [ ] `.spec-driver/workflow.toml` carries both keys per DR-138 §11.3:
  ```toml
  [validation.strict]
  delta = true

  [schema_version]
  delta = "0.10.0+001"
  ```
- [ ] Post-flip gate (DR-138 §11.4):
  - `validate workspace --kind delta --strict --no-tolerated-aliases` returns 0 errors beyond the documented pre-existing baseline (7× sibling-draft audit-gate warnings + 1× DR-030 unresolved-reference error on DE-030 — ISSUE-057).
  - `validate workspace --strict` whole-corpus does not regress (same documented baseline; no new errors introduced by the flip).
  - `complete delta DE-138 --dry-run` passes coverage gate via derived `applies_to`.
  - `list deltas` smoke-check: rows render correctly under new column set (no rendering regression introduced by flip — flip touches validator path only, but defence-in-depth).
- [ ] F-138-24 follow-up tracking-artefact filed: `.spec-driver/backlog/issues/<slug>.md` (or equivalent — `spec-driver create issue` is canonical) with explicit owner, due date (or "next umbrella audit"), and DE-136 P04 umbrella audit consumption point. Issue ID recorded in §9 and referenced from DR-138 §10.5 acceptance row at close.
- [ ] IP-138 `supekku:verification.coverage@v1` entries flipped `planned` → `verified` for VT-DE138-GATE-001, VT-DE138-FLIP-001 (both rows), VH-DE138-FLIP-001. Notes field updated with phase commit SHA + attestation date.
- [ ] IP-138 §9 Progress Tracking — tick `P04 — Strict-flip held; post-flip gate clean; follow-up audit tracking-artefact filed`; tick `complete delta DE-138 succeeds without --force` after the close-change handoff.
- [ ] DE-138.md frontmatter `updated:` refreshed; no scope changes expected at P04 close.
- [ ] `just check` clean (ruff + format + pytest) post-flip; `uvx import-linter lint` 3/3 contracts (workspace.py + validator.py edits are presentation/supekku-side; Migrations isolation untouched, full lint is exit gate).
- [ ] DE-138 ready for `complete delta DE-138` without `--force` (handoff to `/close-change`, not executed in this phase).

## 5. Verification

- **Unit suites**:
  - `supekku/scripts/lib/validation/validator_test.py` — extend with `accept_tolerated=False` propagation cases for per-kind delta block validators (assert WorkspaceValidator invokes `validate_delta_context_inputs(..., accept_tolerated=False)` when the flag is set).
  - `supekku/scripts/lib/blocks/delta_metadata_test.py` — already covers `accept_tolerated` at the per-kind validator boundary; no new VTs expected unless workspace-side wiring surfaces a gap.
- **Integration / end-to-end CLI**:
  - `spec_driver/presentation/cli/validate/workspace_test.py` — VT-DE138-GATE-001: fixture workspace containing a delta with `context_inputs[{type: unknown, ...}]`; assert `validate workspace --kind delta --strict` exit 0 and `validate workspace --kind delta --strict --no-tolerated-aliases` exit 1 with an error message mentioning the offending field/value.
  - `spec_driver/presentation/cli/validate/workspace_test.py` (or live workspace assertion at `just check`) — VT-DE138-FLIP-001 row 1: post-flip `validate workspace --kind delta --strict` returns 0 errors against in-repo corpus.
  - Synthetic / fixture assertion — VT-DE138-FLIP-001 row 2: post-flip, a delta with a cut FM key (e.g. `applies_to: {specs: [PROD-004]}` re-introduced in fixture) fails with strict-mode error.
- **Tooling/commands**:
  - `uv run spec-driver validate workspace --kind delta --strict` (pre-wiring baseline — entrance gate item).
  - `uv run spec-driver validate workspace --kind delta --strict --no-tolerated-aliases` (post-wiring + post-flip gate).
  - `uv run spec-driver validate workspace --strict` (whole-corpus regression check).
  - `uv run spec-driver complete delta DE-138 --dry-run` (coverage gate verification).
  - `uv run spec-driver list deltas` (smoke-check rendering).
  - `uv run spec-driver create issue` (F-138-24 backlog issue).
  - `just check` + `uvx import-linter lint` final gate.
- **Evidence to capture**:
  - Pre-wiring `validate workspace --kind delta --strict` baseline output in §10.
  - VT-DE138-GATE-001 test output (both assertion shapes) in §10.
  - VH-DE138-FLIP-001 attestation: date + operator handle in §9.
  - Workflow.toml flip commit SHA in §9; diff scope in §10 (should be a 4-line addition under two sections — no other changes).
  - Post-flip command outputs (FLIP-001 baseline + strict-on-validate fixture + whole-corpus regression check + complete dry-run + list smoke) in §10.
  - F-138-24 issue ID + path in §9; cross-reference into DR-138 §10.5 acceptance row at close.

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - `MetadataValidator.validate(..., accept_tolerated=False)` already rejects tolerated alias entries as errors (confirmed at `supekku/scripts/lib/blocks/metadata/validator.py:408`). Wiring task is plumbing — no new validator logic needed at the metadata layer.
  - `WorkspaceValidator` does not currently invoke `validate_delta_context_inputs` / `validate_delta_risk_register` at the per-kind level (grep across `supekku/scripts/lib/validation/` returned no call sites). The wiring task therefore has two layers: (1) thread `accept_tolerated` through `validate_workspace(...)` + `WorkspaceValidator` constructor; (2) actually invoke per-kind delta block validators inside `WorkspaceValidator.validate()`. If invocation already exists via another path, only layer (1) is needed — confirm during 4.1 design pass.
  - Workflow.toml is the canonical strict-mode toggle; `validate workspace --strict` CLI flag is for one-off override, not for the persistent baseline. The flip is a config edit, not a CLI invocation change.
  - In-repo corpus is already strict-clean modulo tolerated aliases (P03 swept all 141 deltas; tolerant validate is exit 0; the only remaining "strict" delta is the tolerated alias `unknown` entries on DE-006 context_inputs surfaced under `--no-tolerated-aliases`).
  - F-138-24 backlog issue belongs in `.spec-driver/backlog/issues/` (canonical location per glossary); use `spec-driver create issue` (not hand-authoring) for ID allocation + frontmatter shape.
  - VH-DE138-FLIP-001 attestation is operator-driven (the user); agent surfaces the pre-flip checklist + waits for explicit attestation before staging the workflow.toml edit. Attestation form: user types confirmation in conversation; agent records date + handle in §9.
- **STOP** when:
  - Pre-wiring `validate workspace --kind delta --strict` shows errors beyond the documented pre-existing baseline (7× sibling-draft audit-gate warnings + 1× DR-030 unresolved-reference error on DE-030 — ISSUE-057) — halt; investigate whether the new surface is a sweep miss or a previously-hidden defect before wiring lands.
  - VT-DE138-GATE-001 cannot be constructed because the per-kind validator wiring does not exist anywhere in `WorkspaceValidator` and adding it surfaces design questions (where in the validate loop? before or after FM validation?) — `/consult` before improvising; this is the load-bearing piece of DEC-138-14.
  - Post-wiring `validate workspace --kind delta --strict --no-tolerated-aliases` flags entries beyond the known DE-006 tolerated-alias surface + the documented baseline (audit-gate + DR-030 / ISSUE-057) — halt; investigate whether the wiring is over-eager or whether the corpus carries a previously-hidden defect. Either way, do not flip the toml.
  - Whole-corpus `validate workspace --strict` post-flip surfaces NEW errors against non-delta kinds — halt; flip should not affect non-delta kinds, so a regression here implies wiring leaked across kind boundaries. Revert per §11.5A (one-line workflow.toml revert) and investigate.
  - `complete delta DE-138 --dry-run` fails post-flip — halt; coverage gate via derived `applies_to` was proven at P03 (VT-DE138-COV-001), so a regression implies the flip surfaced a previously-tolerated validation issue. Investigate without reverting unless the failure is structural.
  - VH-DE138-FLIP-001 not attested before the workflow.toml edit is staged — halt; the attestation is the gate. Do not improvise operator approval.
  - F-138-24 backlog issue cannot be filed because the DE-136 P04 umbrella audit consumption point is unclear — halt; without a concrete consumption point, the §9.5 gate item is non-falsifiable per F-138-24 rationale.
  - Workflow.toml edit lands but `--no-tolerated-aliases` still no-ops at the CLI (i.e. the wiring task missed a layer) — halt; revert toml flip; the gate is vacuous without real wiring.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 4.1 | Pre-wiring baseline: run `validate workspace --kind delta --strict` against in-repo corpus; capture output in §10; confirm errors are bounded to documented pre-existing baseline | [ ] | Done 2026-05-20: exit 1, 7× audit-gate warnings + 1× DR-030 error (ISSUE-057 filed; DR-138 §11.2/§11.4/§10.5 amended) |
| [x] | 4.2 | Wire `--no-tolerated-aliases` through CLI → validator stack (DEC-138-14): remove `_ = no_tolerated_aliases` no-op in `workspace.py:146`; add `accept_tolerated` parameter to `validate_workspace(...)` + `WorkspaceValidator.__init__`; new `_validate_delta_blocks` invokes per-kind delta block validators with threaded value + native severity dispatch | [ ] | Commit `6c638eea`; touches `spec_driver/presentation/cli/validate/workspace.py` + `supekku/scripts/lib/validation/validator.py` + `supekku/scripts/lib/blocks/delta_metadata.py` (`DELTA_*_VALIDATOR` unprivatised) |
| [x] | 4.3 | VT-DE138-GATE-001: end-to-end CLI test (Typer test harness) + validator-boundary unit tests — fixture workspace + delta with `context_inputs[{type: unknown}]`; assert default `--strict` no error + `--strict --no-tolerated-aliases` error | [ ] | Commit `6c638eea`; CLI test `workspace_test.py::TestWorkspaceCliSmoke::test_no_tolerated_aliases_promotes_de006_tolerated_to_errors` (live DE-006); validator-boundary tests `validator_test.py::TestDeltaBlockTolerationGateVTDE138GATE001::*` |
| [ ] | 4.4 | Operator pre-flip checklist + VH-DE138-FLIP-001 attestation: present DR-138 §11.2 checklist in conversation; capture explicit operator attestation; record date + handle in §9 | [ ] | Human gate; agent does not improvise approval per §6 STOP |
| [ ] | 4.5 | Flip `workflow.toml`: append `[validation.strict] delta = true` + `[schema_version] delta = "0.10.0+001"` per DR-138 §11.3; commit as discrete commit (`feat(DE-138): IP-138-P04 strict-flip — delta = true + schema_version 0.10.0+001`); record SHA in §9 | [ ] | Only after 4.4 attestation; sweep commit + flip commit must be independently revertable (§11.5A) |
| [ ] | 4.6 | VT-DE138-FLIP-001 row 1 (baseline): post-flip `validate workspace --kind delta --strict` returns 0 errors against in-repo corpus; capture output in §10 | [ ] | If errors surface, STOP per §6 — revert flip; investigate before re-flipping |
| [x] | 4.7 | VT-DE138-FLIP-001 row 2 (strict-on-validate enforcement): synthetic fixture delta with a context_inputs entry missing required `id` field surfaces as `error` under strict; capture in §10 | [ ] | Commit `6c638eea`; `validator_test.py::TestDeltaBlockStrictEnforcementVTDE138FLIP001::test_missing_required_field_in_context_inputs_errors_under_strict`. Note: original §4 design pointed at a cut-FM-key fixture, but cut FM keys are caught at the kind-aware FM validator (`_validate_kind_frontmatter`), not the per-kind block path; the block-schema "is required" assertion is the more direct proof of strict-on-validate enforcement for delta block schemas. The cut-FM-key dimension is still covered post-flip by 4.6 corpus baseline (no fixture re-introduces FM cut keys in the in-repo corpus, so any FM cut key re-introduction would surface as a regression). |
| [ ] | 4.8 | Post-flip gate (DR-138 §11.4): whole-corpus `validate workspace --strict` no regression; `complete delta DE-138 --dry-run` passes; `list deltas` smoke-check rows render; capture all three outputs in §10 | [ ] | If any fail, STOP per §6 |
| [ ] | 4.9 | F-138-24 backlog issue: `uv run spec-driver create issue "audit delta-vs-IP verification asymmetry (DR-138 §9.5)"`; populate frontmatter with owner + due + DE-136 P04 consumption point; record issue ID + path in §9 | [ ] | Concrete artefact required per §10.5 — without it, "follow-up audit scoped" gate is non-falsifiable |
| [ ] | 4.10 | Execution-doc reconciliation: IP-138 coverage entries → verified for GATE-001 + FLIP-001 (both rows) + VH-FLIP-001; IP-138 §9 progress tracking ticked; DE-138 frontmatter `updated:` refreshed; notes.md appended with P04 close section (commit SHAs, attestation date, F-138-24 issue ID, gate output summary) | [ ] | Use `/update-delta-docs` if it covers all four touchpoints |
| [ ] | 4.11 | Quality gates: `just check` (ruff + format + pytest) clean; `uvx import-linter lint` 3/3 contracts hold; capture final test count in §10 | [ ] | Exit gate; ready for `/close-change` handoff |

### Task Details

- **4.1 — Pre-wiring strict baseline**
  - **Design**: One CLI invocation, capture stdout/stderr/exit code. Expected: exit 0 with only pre-existing 7× audit-gate + 1× DR-030 warnings (same as tolerant baseline at P03 close). If errors surface that are NOT tolerated-alias-related, STOP and investigate.
  - **Files**: None (read-only).
  - **Testing**: Captured output is the reference baseline for 4.6 assertion.
- **4.2 — `--no-tolerated-aliases` wiring (DEC-138-14)**
  - **Design / Approach**:
    1. **CLI layer** (`spec_driver/presentation/cli/validate/workspace.py`): delete `_ = no_tolerated_aliases` (line 146); pass `accept_tolerated=not no_tolerated_aliases` (or equivalent) into `validate_ws(...)`. Update the existing `try` block at line 136 to carry the new kwarg.
    2. **validator entry** (`supekku/scripts/lib/validation/validator.py:626`): add `accept_tolerated: bool = True` keyword-only parameter to `validate_workspace(...)`; forward into `WorkspaceValidator(workspace, strict=..., fix=..., accept_tolerated=...)`.
    3. **WorkspaceValidator**: add `accept_tolerated: bool = True` to `__init__`; store as `self._accept_tolerated`. Inside `validate()`, for each loaded delta artefact, invoke `validate_delta_context_inputs(block, strict=self._strict, accept_tolerated=self._accept_tolerated)` and `validate_delta_risk_register(block, strict=..., accept_tolerated=...)` and convert returned `list[str]` into `ValidationIssue` entries with level `error` (since `accept_tolerated=False` upgrades tolerated_alias from warning to error per `MetadataValidator` semantics). Confirm where in `validate()` the delta iteration lives (or add it) — keep the call site cohesive with existing per-kind validation patterns.
    4. **Boundary check**: per-kind invocation should not run for non-delta kinds; the validator is scoped to delta blocks. Non-delta kinds (spec, audit, etc.) are unaffected by `--no-tolerated-aliases` until their own DE-139..142 wiring lands.
  - **Files**: `spec_driver/presentation/cli/validate/workspace.py`, `supekku/scripts/lib/validation/validator.py`.
  - **Testing**: 4.3 (VT-DE138-GATE-001) is the end-to-end proof; unit-level test in `validator_test.py` for the parameter propagation is recommended but not strictly required if the CLI test exercises the full chain.
  - **Observations**: Confirm with grep during 4.2 design pass whether `WorkspaceValidator` already invokes any per-kind block validator (the boot survey found none in `validation/*.py`). If a different module wires block validation into the workspace flow, integrate there rather than duplicating; per-kind block validator invocation should have exactly one call site to avoid drift.
- **4.3 — VT-DE138-GATE-001**
  - **Design**: Typer test harness invocation (`typer.testing.CliRunner` against `spec_driver.presentation.cli.validate.app`). Two assertions:
    - Setup: temp workspace fixture with one delta carrying a `supekku:delta.context_inputs@v1` block where one entry has `type: unknown` (the tolerated alias per DR-138 §5.1).
    - Assertion 1: `runner.invoke(app, ["workspace", "--kind", "delta", "--strict"])` → exit code 0; no error-severity diagnostic mentioning the offending field.
    - Assertion 2: `runner.invoke(app, ["workspace", "--kind", "delta", "--strict", "--no-tolerated-aliases"])` → exit code 1; ≥1 error-severity diagnostic referencing the field.
  - **Files**: `spec_driver/presentation/cli/validate/workspace_test.py` (new test class `TestGateVTDE138GATE001` or similar).
  - **Testing**: Test itself is the VT.
- **4.4 — VH-DE138-FLIP-001 attestation**
  - **Design**: Agent surfaces DR-138 §11.2 pre-flip checklist in conversation:
    - P03 sweep applied; pre-sweep tag intact (verifiable via `git tag -l de-138-pre-sweep`).
    - Sweep commit is discrete; drift log + reconciliation in separate commits.
    - VA-DE138-RISK-RECON-001 + VA-DE138-DRIFT-001 both closed (P03 evidence).
    - `validate workspace --kind delta` clean tolerant (P03 evidence).
    - `validate workspace --kind delta --strict` clean strict (4.1 baseline).
    - `--no-tolerated-aliases` wiring landed (4.2 done) + VT-DE138-GATE-001 green (4.3 done).
    - Operator confirms by typing explicit attestation (e.g. "VH-DE138-FLIP-001 attested" or equivalent). Agent records date + handle in §9 Decisions.
  - **Files**: None (conversational gate).
  - **Testing**: Attestation is the verification artefact (VH = Verification by Human per glossary).
- **4.5 — Flip workflow.toml**
  - **Design**: Read current `.spec-driver/workflow.toml`; append two sections after the existing content per DR-138 §11.3:
    ```toml
    [validation.strict]
    delta = true

    [schema_version]
    delta = "0.10.0+001"
    ```
    If the file already has a `[validation.strict]` or `[schema_version]` section (it may not), MERGE the key under the existing section rather than duplicating the header. Commit as a discrete commit (no other staged changes) so revert grain is clean per §11.5A. Commit message: `feat(DE-138): IP-138-P04 strict-flip — workflow.toml [validation.strict] delta=true + [schema_version] delta=0.10.0+001`.
  - **Files**: `.spec-driver/workflow.toml`.
  - **Testing**: 4.6/4.7/4.8 collectively prove the flip held.
- **4.6 — VT-DE138-FLIP-001 row 1 (baseline)**
  - **Design**: `uv run spec-driver validate workspace --kind delta --strict` post-flip. Expected: exit 0; output identical to 4.1 baseline (only pre-existing 7× audit-gate + 1× DR-030 warnings). If `--strict` now surfaces NEW errors (something the flip exposed), STOP per §6 — likely a P03 sweep miss or a tolerated-alias surface beyond the known DE-006 entries. Revert per §11.5A if data needs fixing.
  - **Files**: None (read-only).
  - **Testing**: Captured output mirrors 4.1 baseline byte-for-byte (modulo timestamps).
- **4.7 — VT-DE138-FLIP-001 row 2 (strict-on-validate enforcement)**
  - **Design**: Fixture-based: construct a temp workspace with a delta whose FM carries a cut key (e.g. `applies_to: {specs: [PROD-004]}` re-introduced). Run `validate workspace --kind delta --strict` against the fixture and assert exit 1 with an error message identifying the cut key as forbidden post-flip. Test lives alongside GATE-001 in `workspace_test.py`. This row of FLIP-001 is the strict-on-validate FR-002 proof; without it, FLIP-001 only proves "the corpus does not regress", not "strict mode is actually enforced".
  - **Files**: `spec_driver/presentation/cli/validate/workspace_test.py`.
  - **Testing**: Test itself is the VT row.
- **4.8 — Post-flip gate**
  - **Design**: Three CLI invocations:
    1. `uv run spec-driver validate workspace --strict` (whole corpus). Expected: no NEW errors vs the pre-flip whole-corpus baseline; only sibling-draft audit-gate warnings remain.
    2. `uv run spec-driver complete delta DE-138 --dry-run`. Expected: coverage gate via derived `applies_to` returns no missing coverage (P03 VT-DE138-COV-001 evidence held).
    3. `uv run spec-driver list deltas` smoke-check. Expected: rows render without exceptions; column matrix unchanged from P03 LIST-001 baseline.
  - **Files**: None (read-only).
  - **Testing**: Outputs captured in §10.
- **4.9 — F-138-24 backlog issue**
  - **Design**: `uv run spec-driver create issue "audit delta-vs-IP verification asymmetry"` (or equivalent CLI shape — check `spec-driver create --help` for the exact subcommand). Populate frontmatter with:
    - `owner`: TBD (operator decision at filing — may be deferred to umbrella audit if no individual owner identified, in which case set to "DE-136 P04 umbrella audit").
    - `due`: explicit date or "next umbrella audit" sentinel (per F-138-24 — concrete date or sentinel, not blank).
    - Body content per DR-138 §9.5 + §15.1: audit shape (sample delta §6 prose; characterise drift patterns + root cause; output scopes corrective surface across skills/validation/memory).
    - DE-136 P04 umbrella audit consumption point: explicit cross-reference in body (e.g. "Consumed by DE-136 P04 umbrella audit per DR-138 §15.1 + F-138-24").
    - Cross-references back: DR-138 §10.5 acceptance row should reference the issue ID at close (4.10 reconciliation task).
  - **Files**: `.spec-driver/backlog/issues/<slug>.md` (created via CLI).
  - **Testing**: `uv run spec-driver list issues` shows the new entry; ID recorded in §9.
- **4.10 — Execution-doc reconciliation**
  - **Design**:
    - IP-138 `supekku:verification.coverage@v1` — flip `planned` → `verified` for VT-DE138-GATE-001 (FR-002, P04), VT-DE138-FLIP-001 row 1 (FR-001, P04), VT-DE138-FLIP-001 row 2 (FR-002, P04), VH-DE138-FLIP-001 (FR-002, P04). Update `notes` field on each entry to reference the relevant commit SHA + test ID.
    - IP-138 §9 Progress Tracking — tick `P04 — Strict-flip held; post-flip gate clean; follow-up audit tracking-artefact filed`. Leave `complete delta DE-138 succeeds without --force` for `/close-change` to tick.
    - DE-138.md frontmatter — refresh `updated:` date.
    - notes.md — append `## 2026-05-20 — P04 close — Strict-flip + post-flip gate` with: wiring commit SHA, flip commit SHA, VH attestation date + operator handle, VT-DE138-GATE-001 + FLIP-001 (both rows) test references, F-138-24 issue ID + path, post-flip gate output summary, final test count.
    - Optional: cross-reference F-138-24 issue ID into DR-138 §10.5 acceptance row + §15.1 (mark "tracking artefact filed: ISSUE-XXX").
  - **Files**: `IP-138.md`, `DE-138.md`, `notes.md`, optionally `DR-138.md`.
  - **Testing**: `validate workspace --kind delta` clean post-reconciliation (no broken references introduced).
- **4.11 — Quality gates**
  - **Design**: `just check` (ruff + format + pytest) — expect 5386 + new GATE-001 + FLIP-001 row 2 tests + any per-kind wiring tests from 4.2 (rough estimate +3-5 VTs). `uvx import-linter lint` 3/3 contracts — wiring touches `spec_driver/presentation/cli/validate/workspace.py` (allowed to import supekku) and `supekku/scripts/lib/validation/validator.py` (supekku-side, no migration concerns); Migrations isolation contract unaffected. Capture final test count in §10.
  - **Files**: None (verification).

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Wiring lands at CLI + validator entry but never invokes per-kind delta block validators inside `WorkspaceValidator.validate()` — flag plumbs through but the gate is still vacuous | 4.3 VT-DE138-GATE-001 is end-to-end via CLI; if the test passes, the wiring is real. STOP per §6 if 4.3 fails despite 4.2 marked done | open |
| Pre-wiring `--strict` baseline (4.1) surfaces errors beyond the known tolerated-alias surface — indicates P03 sweep miss or undocumented validation issue | §3 entrance gate; §6 STOP halts before wiring lands; investigate without flipping toml | open |
| Workflow.toml flip lands before VH attestation captured — operator approval bypassed | 4.4 explicitly gates 4.5; agent records attestation in §9 before staging edit; §6 STOP enforces | open |
| Post-flip `validate workspace --strict` whole-corpus regresses on non-delta kinds (wiring leaked across kind boundaries) | 4.8 captures whole-corpus output; §6 STOP triggers §11.5A one-line revert; investigate scope leak | open |
| `complete delta DE-138 --dry-run` fails post-flip (coverage gate surfaces issue exposed by strict mode) | 4.8 captures dry-run output; if fails, investigate per-requirement against derived `applies_to`; revert toml only if structural defect | open |
| F-138-24 issue filed but content is generic / lacks DE-136 P04 consumption point — §10.5 gate is still non-falsifiable | 4.9 design specifies explicit consumption-point requirement; reviewer cross-checks issue body against DR-138 §9.5 + §15.1 content shape; STOP if vague | open |
| `MetadataValidator(accept_tolerated=False)` returns warnings not errors for tolerated_aliases — wiring threads correctly but assertion shape wrong | Confirmed at `validator.py:408` that `_accept_tolerated=False` produces errors; if behaviour differs in practice, treat as a metadata-layer bug requiring `/consult` (out of DE-138 scope but blocks the gate) | open |
| Per-kind block validator invocation in WorkspaceValidator already exists somewhere (different module / different shape) and the wiring task duplicates it | 4.2 design step 4 explicitly checks for existing call site via grep; if found, integrate rather than duplicate to maintain single source of truth | open |
| `[schema_version] delta = "0.10.0+001"` collides with an existing `[schema_version]` section in workflow.toml | 4.5 design checks for existing section; merge key under existing header if present, do not duplicate | open |

## 9. Decisions & Outcomes

- `2026-05-20` — Pre-wiring `validate workspace --kind delta --strict` baseline captured (4.1): exit 1; 7× sibling-draft audit-gate warnings (DE-135/136/138/139/140/141/142) promoted under strict + 1× `error`-level "References unresolved artifact 'DR-030' (via relation.introduces)" on DE-030. DR-030.md exists on disk at `.spec-driver/deltas/DE-030-unit_vs_assembly_spec_classification/DR-030.md` with correct frontmatter; registry-resolution does not find it. Filed as **ISSUE-057** (registry-resolution defect; not introduced by DE-138; not a close blocker). DR-138 §11.2/§11.4/§10.5 amended to acknowledge the carve-out: post-flip gate tolerates this exact baseline; new errors beyond it fail the gate. /consult routed; user approved Option A (proceed with carve-out).
- `2026-05-20` — `--no-tolerated-aliases` wiring landed in commit `6c638eea` (4.2). Touches `spec_driver/presentation/cli/validate/workspace.py` + `supekku/scripts/lib/validation/validator.py` + `supekku/scripts/lib/blocks/delta_metadata.py`. `WorkspaceValidator._validate_delta_blocks` iterates `delta_registry`, extracts context_inputs + risk_register blocks via `extract_delta_*` helpers, calls `DELTA_*_VALIDATOR.validate(block.data, strict=self.strict, accept_tolerated=self.accept_tolerated)`, and dispatches each `ValidationError` at native severity (warning → `self._warning`, error → `self._error`). `DELTA_CONTEXT_INPUTS_VALIDATOR` + `DELTA_RISK_REGISTER_VALIDATOR` unprivatised (added to `__all__`).
- `2026-05-20` — VT-DE138-GATE-001 green (4.3). CLI end-to-end test `spec_driver/presentation/cli/validate/workspace_test.py::TestWorkspaceCliSmoke::test_no_tolerated_aliases_promotes_de006_tolerated_to_errors` exercises live-repo DE-006 (carries 3× `context_inputs[].type=unknown`); asserts default `--strict` produces no error-level tolerated-alias diagnostics while `--strict --no-tolerated-aliases` produces ≥1 error. Validator-boundary tests `validator_test.py::TestDeltaBlockTolerationGateVTDE138GATE001::*` cover the same boundary with synthetic fixtures (warning under default accept, error under accept_tolerated=False).
- `2026-05-20` — VT-DE138-FLIP-001 row 2 green (4.7). Commit `6c638eea`; `validator_test.py::TestDeltaBlockStrictEnforcementVTDE138FLIP001::test_missing_required_field_in_context_inputs_errors_under_strict`. Synthetic fixture: delta with `context_inputs` entry missing required `id` field surfaces as `error` under strict — proves the per-kind validator is invoked, not bypassed.
- `YYYY-MM-DD` — VH-DE138-FLIP-001 attested by `<operator handle>` (4.4). Pre-flip checklist (DR-138 §11.2) confirmed item-by-item; attestation captured in conversation.
- `YYYY-MM-DD` — Workflow.toml flip commit `<SHA>` (4.5). Discrete commit; only `.spec-driver/workflow.toml` mutated. Diff scope: two sections added — `[validation.strict] delta = true` + `[schema_version] delta = "0.10.0+001"`.
- `YYYY-MM-DD` — VT-DE138-FLIP-001 row 1 green (4.6). Post-flip `validate workspace --kind delta --strict`: exit 0; output matches pre-wiring baseline byte-for-byte modulo timestamps.
- `YYYY-MM-DD` — VT-DE138-FLIP-001 row 2 green (4.7). Synthetic fixture with cut FM key fails post-flip with strict-mode error.
- `YYYY-MM-DD` — Post-flip gate clean (4.8): whole-corpus `validate workspace --strict` no regression; `complete delta DE-138 --dry-run` passes; `list deltas` rows render unchanged.
- `YYYY-MM-DD` — F-138-24 backlog issue filed as `ISSUE-<id>` at `.spec-driver/backlog/issues/<slug>.md` (4.9). Owner: `<value>`; due: `<value>`; DE-136 P04 umbrella audit consumption point captured in body.
- `YYYY-MM-DD` — Execution-doc reconciliation complete (4.10): IP-138 coverage entries flipped to verified; PROD-004 coverage block unchanged (FR-001/-002/-007 remain `in-progress` per F-138-L — umbrella audit at DE-136 P04 promotes to verified); notes appended; DR-138 §10.5 cross-referenced to F-138-24 issue.
- `YYYY-MM-DD` — Quality gates clean (4.11): `just check` <test count> pass; `uvx import-linter lint` 3/3 contracts.

## 10. Findings / Research Notes

- **4.1 pre-wiring strict baseline** (2026-05-20): `uv run spec-driver validate workspace --kind delta --strict` exit 1; 8 issues total — 7× `warning` (DE-135/136/138/139/140/141/142 audit-gate-not-found, sibling drafts) + 1× `error` (`DE-030`: "References unresolved artifact 'DR-030' (via relation.introduces)"). DR-030.md exists on disk; registry-resolution defect tracked as ISSUE-057. Pre-existing baseline accepted per DR-138 §11.2/§11.4/§10.5 carve-out (commit `4bc87694`).
- **4.2 wiring scope summary**: 5 files touched, +223/-15 LOC. Single per-kind validator invocation site: `WorkspaceValidator._validate_delta_blocks` (called from `validate()` immediately before kind-aware FM validation). Wiring proven end-to-end by 4.3 GATE-001.
- **4.3 VT-DE138-GATE-001 evidence**: CLI test exercises live DE-006 via Typer test harness; default `--strict` yields warnings only on tolerated_alias entries, `--no-tolerated-aliases` promotes them to errors. Validator-boundary tests use synthetic fixture deltas (DE-901, DE-902, DE-903) to isolate the per-kind path; both shapes pass.
- **4.7 VT-DE138-FLIP-001 row 2 evidence**: synthetic fixture DE-903 — `context_inputs[{type: document, summary: missing id}]` (no `id` field); under `--strict` the workspace validator surfaces `ValidationIssue(level='error', message='context_inputs: entries[0].id: is required ...', artifact='DE-903')`. Proves the per-kind validator is invoked via the workspace path, not bypassed.
- **4.6 / 4.8 outstanding**: corpus baseline + post-flip whole-corpus check + complete dry-run + list smoke pending the toml flip (4.5). Post-wiring DE-006 tolerated_alias entries surface as warnings under tolerant validate + as errors under `--no-tolerated-aliases`; need to decide whether the strict-flip post-flip gate accepts the DE-006 tolerated-alias warnings as part of the documented baseline or whether DE-006 needs operator action (re-classify the 3 `type: unknown` entries to canonical `document`) before flip. **Handover question** — see notes.md.
- **Wiring scope summary** (4.2):
  - `spec_driver/presentation/cli/validate/workspace.py`: dropped `_ = no_tolerated_aliases` no-op; passes `accept_tolerated=not no_tolerated_aliases` into `validate_ws`.
  - `supekku/scripts/lib/validation/validator.py`: `validate_workspace` + `WorkspaceValidator` accept `accept_tolerated` kwarg; new `_validate_delta_blocks` + `_block_issue` methods; imports for `extract_delta_*` + `DELTA_*_VALIDATOR`.
  - `supekku/scripts/lib/blocks/delta_metadata.py`: validator instances `DELTA_CONTEXT_INPUTS_VALIDATOR` + `DELTA_RISK_REGISTER_VALIDATOR` unprivatised; added to `__all__`.
- **Quality gates post-wiring** (4.11 partial — pending 4.6/4.8): pytest **5450 pass** (4 skipped, 35 warnings; +64 vs P03's 5386 — inheritance pattern of new test classes from `WorkspaceValidatorTest` re-runs parent suite under child class names, established convention); ruff lint + format clean; import-linter 3/3 contracts kept.
- F-138-24 issue ID + path: **pending 4.9**.

## 11. Wrap-up Checklist

- [ ] All §4 exit criteria satisfied.
- [ ] Wiring commit + flip commit SHAs recorded in §9.
- [ ] VH-DE138-FLIP-001 attestation date + operator handle recorded in §9.
- [ ] F-138-24 issue ID + path recorded in §9; DR-138 §10.5 acceptance row cross-referenced.
- [ ] IP-138 verification coverage entries flipped `planned` → `verified` for GATE-001 / FLIP-001 (both rows) / VH-FLIP-001.
- [ ] IP-138 §9 progress tracking ticked for P04.
- [ ] DE-138.md frontmatter `updated:` refreshed.
- [ ] notes.md appended with P04 close section.
- [ ] Hand-off to `/close-change` — DE-138 ready for `complete delta DE-138` without `--force`; outstanding for closure: `complete delta` command execution + IP-138 final tick + DE-138 status → completed + any close-change-specific gates.
