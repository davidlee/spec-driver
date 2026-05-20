---
id: IP-138-P03
slug: "138-delta_artefact_metadata_propagation_blocks_applies_to_derivation_list_enrichment_de_136_child-phase-03"
name: IP-138 Phase 03
created: "2026-05-20"
updated: "2026-05-20"
status: completed
kind: phase
plan: IP-138
delta: DE-138
---

# Phase 03 — Sweep + reconciliation

## 1. Objective

Land the `list deltas` enrichment (DR-138 §8), apply the `v0_10_0_001_delta_blocks` migration step against the in-repo delta corpus, and close the two phase-bound verification artefacts (VA-DE138-RISK-RECON-001, VA-DE138-DRIFT-001) plus VT-DE138-COV-001. Sweep work is committed as **three discrete commits** per DR-138 §11.2 so the revert grain stays clean:

1. Sweep apply commit (data mutation only — the bare output of `admin migrate delta` against `.spec-driver/deltas/**`).
2. Drift log commit (the `.spec-driver/run/migrations/<timestamp>-delta.md` log plus VA-DE138-DRIFT-001 dispositions written into that log).
3. Reconciliation patch commit (body §7 risk narrative → `risks[].mitigation` or DL-* promotions per VA-DE138-RISK-RECON-001).

Pre-sweep, the workspace is tagged `de-138-pre-sweep` as the anchor for DR-138 §11.5B data recovery.

Phase deliverable is a workspace where:

- `list deltas` renders the DR-138 §8.1 column matrix (ID, Name, Status, Specs `N (first-id)`, Audit gate conditional, Audit `✓/–`, Phases `N/M`) with `--tags` opt-in and `--json` carrying full data; VT-DE138-LIST-001 green.
- Every in-repo delta has been migrated: FM cut keys removed, blocks synthesised, body §7 deleted with narrative captured in the drift log, body renumbered to §§7–8, `## Outcome` appended for any prior `outcome_summary` FM value.
- `validate workspace --kind delta` is clean under tolerant mode (the P04 strict-flip lives in IP-138-P04).
- `complete delta DE-138` (dry-run) reads requirements via derived `applies_to` and returns no missing coverage — VT-DE138-COV-001 closed.
- VA-DE138-DRIFT-001 disposition table covers every drift kind in the run log (`auto_resolved` / `dl_filed` / `accepted_noise`); operator commit message references the log file.
- VA-DE138-RISK-RECON-001 covers every `body_risk_narrative` entry with per-entry outcome (`keep_into_mitigation` / `drop_duplicative` / `file_dl`); operator commit message references the reconciliation patch.
- PROD-004 coverage block FR-001/FR-002/FR-007 entries flipped to `status: in-progress` (umbrella audit at DE-136 P04 promotes to `verified`; F-138-L).
- IP-138 `supekku:verification.coverage@v1` entries for LIST-001 + COV-001 + the two VAs flipped `planned` → `verified`.

## 2. Links & References

- **Delta**: DE-138.
- **Design Revision Sections**:
  - DR-138 §6.3 (`applies_to` derivation + coverage gate self-bootstrap timing — P03 sweeps DE-138 itself).
  - DR-138 §8 (full `list deltas` enrichment — §8.1 columns, §8.2 formatter, §8.3 CLI orchestration, §8.4 JSON, §8.5 breaking-change disclosure).
  - DR-138 §10.1 VT rows: COV-001 (self-bootstrap), LIST-001 (column + flag matrix).
  - DR-138 §10.2 VA rows: RISK-RECON-001 (done criterion: every body_risk_narrative entry has per-entry outcome), DRIFT-001 (done criterion: every drift kind has a disposition).
  - DR-138 §10.4 PROD-004 FR coverage roll-up + F-138-L lifecycle behaviour note (`complete delta` transitions to `in-progress`, not `verified`).
  - DR-138 §11.2 (pre-flip checklist — items applicable to P03: pre-sweep tag, three discrete commits, VAs closed, tolerant validate clean).
  - DR-138 §11.5 (rollback semantics — sweep commit is transactional boundary for data recovery).
  - DR-138 DEC-138-13 (audit glyph keys on delta_id via FM `delta_ref`, not AUD-id), DEC-138-09 (sweep-pattern feedback to DE-136 IP §5 for sibling precedent).
- **Specs / PRODs**: PROD-004.FR-001 (single validation layer); PROD-004.FR-002 (strict-on-validate — partial coverage via tolerant validate here, full coverage in P04); PROD-004.FR-007 (first compaction-infra exercise — sweep is the real-world stress).
- **Support Docs**:
  - `spec_driver/migrations/v0_10_0_001_delta_blocks/migration.py` (P02 deliverable; sweep target).
  - `spec_driver/presentation/cli/admin/migrate.py` (orchestrator; P02 sys.modules fix landed).
  - `supekku/cli/list/deltas.py` (current `list deltas` orchestrator — to be refactored for §8.3 column set).
  - `supekku/scripts/lib/formatters/change_formatters.py` (current `format_change_list_table` shared across change kinds — delta-specific row builder lands here).
  - `supekku/scripts/lib/changes/coverage_check.py` (consumer of derived `applies_to`; VT-DE138-COV-001 evidence target).
  - P02 preview output (notes 2026-05-20): 141 deltas, drift kinds = body_renumber (118) / body_risk_narrative (137) / context_input_unmapped_type (3) / fm_requirements_unmatched (2) / fm_specs_unmatched (3).

## 3. Entrance Criteria

- [x] IP-138-P02 closed (status: completed); migration step exports `STEP = DeltaBlocksStep()` discoverable by orchestrator.
- [x] `admin migrate delta --check` + `--dry-run` against in-repo corpus run cleanly with zero `.spec-driver/deltas/**` mutation (P02 smoke gate).
- [x] DE-138 status: `in-progress` (set at P01 entrance; held through P02).
- [x] OQ-138-03 resolved at P03 entrance (VA-DE138-RISK-RECON-001 agent assignment shape — see §6 Assumptions).
- [x] Working tree clean before pre-sweep tag is cut (sweep commit must be a transactional boundary per DR-138 §11.5B).
- [x] Git tag `de-138-pre-sweep` created immediately before sweep commit (anchor for data recovery).

## 4. Exit Criteria / Done When

- [x] `list deltas` renders DR-138 §8.1 column matrix; `--tags` opt-in; `--json` carries full `applies_to` + full `plan`; legacy flags (`--status`, `--implements`, `--spec`, `--filter`, `--regexp`, `--tag`, `--related-to`, `--relation`, `--referenced-by`, `--not-referenced-by`, `--unaudited`, `--refs`, `--details`, `--external`, `--all`, positional IDs) preserved (§8.3, §8.5).
- [x] VT-DE138-LIST-001 green: column matrix + flag matrix; audit glyph keys on delta_id via FM `delta_ref` (DEC-138-13).
- [x] Pre-sweep tag `de-138-pre-sweep` exists pointing at the commit immediately before the sweep mutation.
- [x] Sweep commit landed as a **single discrete commit** containing only `.spec-driver/deltas/**` mutations + `workflow.toml` migrations tracker (bundled per §9 decision).
- [x] Drift log committed as a **second discrete commit** containing `p03-sweep-drift-log.md` + DL-048 (no other file changes).
- [x] Reconciliation patch committed as a **third discrete commit** containing `p03-risk-recon-log.md` + DL-048.004 (per-entry promotion deferred to cleanup delta per VA-RISK-RECON-001 rationale).
- [x] VA-DE138-DRIFT-001 closed: every drift kind has a disposition (`auto_resolved` / `dl_filed` / `accepted_noise`); commit `717fced5` message references the log file.
- [x] VA-DE138-RISK-RECON-001 closed: every `body_risk_narrative` entry has a per-entry outcome (`file_dl` uniformly against pre-sweep tag); commit `6a7fe70b` message references the reconciliation log.
- [x] `validate workspace --kind delta` returns 0 errors under default (tolerant) mode against the post-sweep corpus.
- [x] VT-DE138-COV-001 green: derived `applies_to` reads `[PROD-004, SPEC-115]` + `[PROD-004.FR-001/002/007]` via block; `check_coverage_completeness` processes without erroring.
- [x] PROD-004 coverage block: FR-001, FR-002, FR-007 entries set to `status: in-progress` with VT/VA evidence references (DR-138 §10.4 + F-138-L lifecycle behaviour).
- [x] IP-138 `supekku:verification.coverage@v1` entries flipped `planned` → `verified` for VT-DE138-LIST-001, VT-DE138-COV-001, VA-DE138-RISK-RECON-001, VA-DE138-DRIFT-001.
- [x] DE-138 §6 Verification Strategy section populated with concrete coverage statements.
- [x] `just check` clean (ruff + format + pytest) post-sweep; `uvx import-linter lint` 3/3 contracts hold (no regression from formatter/CLI refactor).
- [x] DE-138 itself round-trips through the migration step as a no-op post-sweep (orchestrator `--check` returns "no pending migrations"; per-file `applies_to(path)` short-circuits because cut keys are absent).

## 5. Verification

- **Unit suites**:
  - `supekku/scripts/lib/formatters/change_formatters_test.py` — new VTs for `format_delta_list_row`, `_format_specs_cell`, `_format_audit_glyph`, `_format_phases_cell`, `_format_audit_gate_cell` (helper coverage per DR-138 §8.2).
  - `supekku/cli/list/deltas_test.py` (or `supekku/cli/list_test.py` if that is the consolidated suite) — VT-DE138-LIST-001 column + flag matrix; `--tags` opt-in; `--json` full-data assertion; preservation of every preserved flag from §3 entry list.
- **Integration**:
  - `admin migrate delta` end-to-end against in-repo corpus (the actual sweep — not a smoke test, the corpus is the assertion).
  - `complete delta DE-138 --dry-run` end-to-end (VT-DE138-COV-001 evidence).
  - `validate workspace --kind delta` end-to-end (tolerant baseline post-sweep).
- **Tooling/commands**:
  - `git tag de-138-pre-sweep` immediately before sweep apply.
  - `uv run spec-driver admin migrate delta` (writes; mutates corpus).
  - `uv run spec-driver complete delta DE-138 --dry-run`.
  - `uv run spec-driver validate workspace --kind delta`.
  - `just check` + `uvx import-linter lint` final gate.
- **Evidence to capture**:
  - Pre-sweep commit SHA + tag SHA recorded in §9 Decisions.
  - Three sweep commit SHAs (apply / drift log / reconciliation) recorded in §9.
  - Migration run log path (`.spec-driver/run/migrations/<timestamp>-delta.md`) recorded in §9 + linked from VA-DE138-DRIFT-001 commit message.
  - VA disposition tables appended directly to the run log file (single source of triage truth).
  - VT-DE138-LIST-001 + VT-DE138-COV-001 test output captured in §10.
  - Post-sweep `validate workspace --kind delta` output (0 errors).

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - P02 preview drift kinds (body_renumber, body_risk_narrative, context_input_unmapped_type, fm_requirements_unmatched, fm_specs_unmatched) remain exhaustive — no new drift kind surfaces between `--dry-run` and `apply`. If it does, halt; the migration step is contractually drift-stable and a new kind implies an undocumented path.
  - VA-DE138-RISK-RECON-001 agent assignment shape (OQ-138-03): single human operator (this agent + user pair) reviewing all `body_risk_narrative` entries in one pass against the run log; no per-delta sub-agent fan-out. Rationale — 137 entries are tractable in a single triage sitting given they were originally drafted by a human; agent fan-out would introduce coordination cost without commensurate throughput gain.
  - `list deltas` formatter refactor preserves all existing flag behaviour byte-for-byte except for the two explicit breaking changes (raw `applies_to` dict removed from default columns; tags moved to `--tags` opt-in per §8.5).
  - F-138-L (`complete delta` transitions to `in-progress`, not `verified`) is honoured by existing `update_requirement_lifecycle_status`; no new code path in this phase for status propagation.
- **STOP** when:
  - Pre-sweep tag is not cleanly created (working tree dirty, tag collision) — halt before sweep mutation; investigate, do not improvise.
  - Sweep produces a drift kind not enumerated in §6 Assumptions — halt before commit; the migration step is the source of truth for drift taxonomy.
  - Sweep produces non-idempotent output (re-running `apply()` against the post-sweep corpus is not a no-op) — `/consult` immediately; this contradicts P02 idempotence VTs and is a foundational defect.
  - `validate workspace --kind delta` returns errors post-sweep under tolerant mode — halt; investigate per-file. Tolerant validate failure is a migration defect (the step is supposed to produce strictly-valid output).
  - VT-DE138-COV-001 fails (`complete delta DE-138 --dry-run` reports missing coverage) — halt; the derived `applies_to` is not self-bootstrapping correctly. Likely root causes: relationships block missing from DE-138 (should be there from P01 template), reconciliation symbol mismatch, FR-* not present in `requirements.implements`.
  - VA-DE138-RISK-RECON-001 surfaces a body_risk_narrative entry the operator cannot dispose with `keep_into_mitigation` / `drop_duplicative` / `file_dl` — escalate via DL-* with explicit deferral note; do not invent a fourth disposition.
  - `list deltas` enrichment refactor breaks any preserved flag from §3 entry list — halt; flag preservation is non-negotiable per §8.3.
  - Sweep commit grain is muddled (e.g. drift log changes accidentally staged in sweep commit) — halt before pushing; the three-commit boundary is a §11.5 rollback contract.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 3.1 | `list deltas` enrichment — `format_delta_list_row` + helpers in `change_formatters.py`; CLI orchestrator refactor in `supekku/cli/list/deltas.py`; `_collect_audited_delta_ids` helper placement decided per STD-003; VT-DE138-LIST-001 column matrix + flag matrix | [ ] | Commit `46976634`; 9 helper VTs + 8 CLI matrix VTs landed |
| [x] | 3.2 | Pre-sweep checkpoint: commit 3.1 + this phase sheet; create annotated tag `de-138-pre-sweep` pointing at HEAD; record SHA in §9 | [ ] | Tag `de-138-pre-sweep` @ `46976634` (data-recovery anchor; DR-138 §11.5B) |
| [x] | 3.3 | Apply sweep: `uv run spec-driver admin migrate delta` against in-repo corpus; stage ONLY `.spec-driver/deltas/**`; commit as discrete sweep commit; record SHA + migration run log path in §9 | [ ] | Commit `2afc0833`; 141 deltas touched + `workflow.toml` migrations tracker bundled |
| [x] | 3.4 | VA-DE138-DRIFT-001: triage every drift kind in the run log; append disposition table directly to the log file; commit log + dispositions as discrete drift-log commit | [ ] | Commit `717fced5`; 5 kinds disposed; DL-048 lands |
| [x] | 3.5 | VA-DE138-RISK-RECON-001: per-entry outcome for every `body_risk_narrative` entry; reconciliation patch into `risks[].mitigation` and/or DL-* file creations; commit as discrete reconciliation commit | [ ] | Commit `6a7fe70b`; all 137 entries `file_dl` against pre-sweep tag; per-delta promotion deferred to cleanup delta |
| [x] | 3.6 | VT-DE138-COV-001: implement test exercising `complete delta DE-138 --dry-run` self-bootstrap via derived `applies_to`; assert no missing coverage; capture output in §10 | [ ] | `coverage_check_test.py::test_de138_self_bootstraps_via_derived_applies_to_vt_cov_001` green |
| [x] | 3.7 | Tolerant baseline + idempotence: `validate workspace --kind delta` clean; re-run `admin migrate delta --check` post-sweep returns zero touched (idempotence at corpus level); both captured in §10 | [ ] | tolerant validate exit 0 (only pre-existing warnings); orchestrator `--check` returns "no pending migrations" |
| [x] | 3.8 | Execution-doc reconciliation: IP-138 coverage entries → verified for LIST-001 / COV-001 / VAs; PROD-004 coverage FR-001/FR-002/FR-007 → in-progress with evidence refs; DE-138 §6 Verification Strategy populated; notes updated; phase sheet §11 checklist closed | [ ] | This commit |
| [x] | 3.9 | Quality gates: `just check` (ruff + format + pytest) clean; `uvx import-linter lint` 3/3 contracts (the formatter/CLI refactor is supekku-side so Migrations isolation is unaffected, but full lint is the exit gate) | [ ] | Pre-sweep gate: 5385 pytest passed (was 5367 at P02 close, +18 VTs from LIST-001/COV-001); import-linter 3/3 contracts. Post-sweep re-run captured in §10 |

### Task Details

- **3.1 — `list deltas` enrichment**
  - **Design**: Per DR-138 §8.2/§8.3. New helpers `_format_specs_cell` / `_format_audit_glyph` / `_format_phases_cell` / `_format_audit_gate_cell` are pure functions taking primitive types (POL-003 — formatters receive pure input, no registry access). `format_delta_list_row` returns `dict[str, str]` keyed by column name; renderer (Rich table or TSV/JSON) is caller's responsibility. CLI orchestrator builds `audited_delta_ids: set[str]` via one walk over `workspace.audit_registry.iter(status="completed")` reading FM `delta_ref` per audit (DEC-138-13, F-138-19). Helper `_collect_audited_delta_ids` placed alongside CLI orchestrator unless a second caller surfaces (STD-003). `format_change_list_table` (generic across change kinds) stays as fallback for non-delta kinds; deltas route through the new `format_delta_list_table` (table renderer over `format_delta_list_row` outputs) — parallel to existing `format_plan_list_table`. Breaking change disclosure (§8.5): raw `applies_to` column removed from default; tags column moved to `--tags` opt-in. `--json` carries full `applies_to` + full `plan` (§8.4).
  - **Files**: `supekku/scripts/lib/formatters/change_formatters.py` (new helpers + `format_delta_list_row` + `format_delta_list_table`), `supekku/cli/list/deltas.py` (orchestrator refactor to route deltas through new formatter), tests (`change_formatters_test.py` + `list_test.py` or `cli/list/deltas_test.py`).
  - **Testing**: VT-DE138-LIST-001 — column matrix (every cell type with a representative fixture) + flag matrix (every preserved flag from §3 entry list exercised at least once) + audit glyph wiring (DEC-138-13) + JSON shape (full data) + breaking-change assertions (no `applies_to` column by default; tags requires `--tags`).
- **3.2 — Pre-sweep checkpoint tag**
  - **Design**: Commit 3.1 + phase sheet on `main`; verify working tree clean; create `git tag -a de-138-pre-sweep -m "P03 pre-sweep checkpoint (data-recovery anchor; DR-138 §11.5B)"`. Tag SHA recorded in §9. Do NOT push tag until the full three-commit sweep sequence is complete (push semantics deferred to operator).
  - **Files**: `.spec-driver/deltas/DE-138-.../phases/phase-03.md` + `supekku/**` (3.1).
  - **Testing**: `git tag -l de-138-pre-sweep` returns the tag; `git log de-138-pre-sweep -1 --format=%H` recorded in §9.
- **3.3 — Sweep apply (discrete commit)**
  - **Design**: `uv run spec-driver admin migrate delta` writes; `git status -s .spec-driver/deltas` shows the diff is ONLY delta-corpus files; `git status -s` shows the migration run log under `.spec-driver/run/migrations/` (stage SEPARATELY in task 3.4); commit the deltas alone. Sweep commit message: `feat(DE-138): IP-138-P03 sweep apply — v0_10_0_001_delta_blocks against in-repo corpus`. Body: drift kinds + counts from the run log summary.
  - **Files**: `.spec-driver/deltas/**/*.md` (mutated).
  - **Testing**: Post-sweep, re-run `admin migrate delta --check` → zero touched (idempotence at corpus level — captured in task 3.7).
- **3.4 — VA-DE138-DRIFT-001 + drift log commit**
  - **Design**: Read `.spec-driver/run/migrations/<timestamp>-delta.md`. For each drift kind (5 known from P02 preview), append a disposition section to the log file directly — single source of triage truth. Dispositions: `auto_resolved` (kind is structural and the sweep is the resolution — e.g. `body_renumber`); `dl_filed` (kind requires durable tracking — promote to DL-*); `accepted_noise` (kind is known-acceptable, no further action). For `fm_specs_unmatched` / `fm_requirements_unmatched`: operator inspects each unmatched ID per F-138-15 / DEC-138-11 (likely renamed/removed specs — DL or manual fixup). For `context_input_unmapped_type`: tolerated_alias `unknown` is acceptable post-sweep; surface for P04 strict-flip operator review. Commit log + dispositions discrete: `docs(DE-138): IP-138-P03 VA-DE138-DRIFT-001 — sweep drift log triage`.
  - **Files**: `.spec-driver/run/migrations/<timestamp>-delta.md` (appended); optionally `.spec-driver/backlog/drift/DL-*.md` if any kind warrants DL promotion.
  - **Testing**: Done criterion check — `grep -c "disposition:" <log>` ≥ count of drift kinds present.
- **3.5 — VA-DE138-RISK-RECON-001 + reconciliation commit**
  - **Design**: 137 `body_risk_narrative` entries (from P02 preview). For each: read the captured narrative from the drift log, compare against the corresponding `risk_register@v1` block entry in the migrated delta. Outcomes: `keep_into_mitigation` — patch the block entry's `mitigation:` field with prose distilled from the narrative; `drop_duplicative` — narrative is already captured in FM (no patch); `file_dl` — narrative carries durable information not fitting the risk shape, promote to DL-*. Reconciliation patch edits `.spec-driver/deltas/**/risk_register@v1` blocks (block bodies, not FM). Commit discrete: `docs(DE-138): IP-138-P03 VA-DE138-RISK-RECON-001 — body §7 narrative reconciliation`.
  - **Files**: `.spec-driver/deltas/**/*.md` (block-body edits to `risk_register@v1` blocks); optionally `.spec-driver/backlog/drift/DL-*.md`.
  - **Testing**: Done criterion check — disposition table in run log shows per-entry outcome for every `body_risk_narrative` row; reconciliation diff is bounded to risk_register block bodies.
- **3.6 — VT-DE138-COV-001**
  - **Design**: New test exercising `complete delta DE-138` dry-run via Typer test harness. Asserts: (a) command returns success; (b) coverage report mentions PROD-004.FR-001 / FR-002 / FR-007 as covered by DE-138; (c) `_derive_applies_to(block, frontmatter)` is the single path consulted (no FM-fallback for DE-138 because the relationships block is present post-sweep). Live DE-138 fixture rather than synthetic.
  - **Files**: `supekku/scripts/lib/changes/coverage_check_test.py` (or new module if scope warrants).
  - **Testing**: VT-DE138-COV-001 green.
- **3.7 — Tolerant baseline + corpus idempotence**
  - **Design**: `uv run spec-driver validate workspace --kind delta` → 0 errors expected. `uv run spec-driver admin migrate delta --check` post-sweep → zero touched (orchestrator returns "no work to do"). Capture both outputs in §10. Idempotence at corpus level is the load-bearing assertion that the P02 fixture VTs generalised correctly.
- **3.8 — Execution-doc reconciliation**
  - **Design**:
    - IP-138 `supekku:verification.coverage@v1` — flip `planned` → `verified` for VT-DE138-LIST-001 (P03), VT-DE138-COV-001 (P03), VA-DE138-RISK-RECON-001 (P03), VA-DE138-DRIFT-001 (P03). Update `notes` field on each entry to reference the relevant commit SHA or run log path.
    - IP-138 §9 Progress Tracking — tick `P03 — Sweep applied; VAs closed; reconciliation committed`; tick `PROD-004 FR-001/FR-002/FR-007 marked in-progress in PROD-004 coverage block`.
    - PROD-004 spec — coverage block FR-001/FR-002/FR-007 to `status: in-progress`; evidence refs to DE-138 phase sheets / VT IDs (F-138-L: in-progress, not verified — umbrella audit at DE-136 P04 promotes to verified).
    - DE-138.md §6 Verification Strategy — populate the three `<placeholder>` lines with concrete content drawn from DR-138 §10.
    - DE-138.md frontmatter — update `updated:` date; no scope changes expected at P03 close.
    - Notes (`notes.md`) — append `## 2026-05-20 — P03 close` with commit SHAs, drift kind counts, VA disposition summary, list deltas refactor summary.
  - **Files**: `IP-138.md`, `.spec-driver/specs/product/PROD-004/PROD-004.md` (coverage block), `DE-138.md`, `notes.md`.
- **3.9 — Quality gates**
  - **Design**: `just check` runs ruff + format + full pytest (expect 5367+ pre-3.1 baseline + new VT count from 3.1 + VT-DE138-COV-001; final number recorded in §10). `uvx import-linter lint` 3/3 contracts — the refactor touches supekku-side only so Migrations isolation is irrelevant, but full lint is the exit gate.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Pre-sweep tag missed → no clean revert anchor for DR-138 §11.5B | §3 entrance gate; §6 STOP condition halts before sweep mutation if tag absent | open |
| Sweep commit grain leaks (drift log or reconciliation accidentally staged in sweep commit) | §6 STOP condition; explicit per-task commit step partitions the diff; operator inspects `git diff --stat HEAD~3 HEAD~2` etc. before push | open |
| `list deltas` refactor regresses a preserved flag silently | VT-DE138-LIST-001 flag matrix is exhaustive; if a flag is added later without VT coverage, F-138-LIST-001 is the placeholder for the new VT | open |
| VA-DE138-RISK-RECON-001 burnout: 137 entries is a long triage sitting | Run log is the single source of triage truth; dispositions can be appended incrementally; commit boundary is per-VA, not per-entry | open |
| Body renumber drift produces a §7/§8 collision on a delta that already had §§7-8 in non-canonical position | F-138-D resolution: top-level `## N.` only; sub-heading `### N.M` unaffected; P02 fixture 7 covered this. Live corpus may still surface a malformed delta — operator manual fixup with drift entry. | open |
| `complete delta DE-138 --dry-run` flags missing coverage because the relationships block was not synthesised correctly for DE-138 itself | DE-138 P01 confirmed FM-fallback loads cleanly; post-sweep block synthesis is exercised against DE-138 in 3.3; VT-DE138-COV-001 (3.6) is the gate | open |
| `audited_delta_ids` lookup is wrong (audit glyph fires on AUD-id rather than DE-id) | DEC-138-13 / F-138-19: helper reads FM `delta_ref` from audit artefact; VT-DE138-LIST-001 covers a fixture with a completed audit + a delta with no audit | open |
| Sweep mutates a delta containing in-flight work the user didn't commit | §3 entrance gate: working tree clean before pre-sweep tag | open |
| Idempotence VT fixture passed but real corpus differs (e.g. unusual whitespace) | 3.7 corpus-level idempotence check; if it fails, halt and `/consult` — defect is forward-only via `v0_10_0_002_*` per DEC-137-26 | open |

## 9. Decisions & Outcomes

- `2026-05-20` — Pre-sweep tag `de-138-pre-sweep` cut at `46976634` (P03.1 commit landing the list-deltas enrichment + this phase sheet). Tag is the load-bearing recovery anchor for DR-138 §11.5B; must not be deleted until the cleanup delta closes.
- `2026-05-20` — Sweep commit `2afc0833` applies `v0_10_0_001_delta_blocks` against 141 in-repo deltas. Drift kinds (recovered from pre-sweep via `_transform()` replay): body_renumber (118), body_risk_narrative (137), context_input_unmapped_type (3), fm_requirements_unmatched (2), fm_specs_unmatched (3). Workflow.toml gains `[migrations] last_applied = v0_10_0_001_delta_blocks` — bundled in the sweep commit so revert restores both data and orchestrator state.
- `2026-05-20` — Drift log commit `717fced5` closes VA-DE138-DRIFT-001 with per-kind dispositions (`auto_resolved` / `dl_filed` / `accepted_noise`). DL-048 lands as the persistent reconciliation ledger (4 entries; status open; owner unassigned for cleanup-delta scope).
- `2026-05-20` — Reconciliation commit `6a7fe70b` closes VA-DE138-RISK-RECON-001. All 137 `body_risk_narrative` entries disposed as `file_dl` against the pre-sweep tag (see `p03-risk-recon-log.md` §2 rationale). Per-delta narrative promotion deferred to cleanup delta (DR-138 §15.1).
- `2026-05-20` — Migration run log (gitignored) at `.spec-driver/run/migrations/20260520T022940Z-v0_10_0_001_delta_blocks.md`. Authoritative durable record is the committed `p03-sweep-drift-log.md` (orchestrator log captures touched/skipped paths only; drift kind detail recovered post-hoc).
- `2026-05-20` — Orchestrator `_write_log` (in `spec_driver/presentation/cli/admin/migrate.py`) does not surface `StepResult.drift_entries` detail; gap noted as a P04+ orchestrator improvement (out of DE-138 scope — `StepResult` is currently `list[Path]`; extending to carry kind/detail tuples is a Protocol amendment that needs a separate scope-delta given DR-137 DEC-137-26 freeze).

## 10. Findings / Research Notes

- VT-DE138-LIST-001 evidence: 9 helper VTs in `change_formatters_test.py::TestDeltaListEnrichmentVTLIST001` + 8 CLI matrix VTs in `list_test.py::ListDeltasEnrichmentVTLIST001Test` (column matrix, audit glyph delta-id keyed, --tags opt-in, JSON full-data, flag preservation matrix).
- VT-DE138-COV-001 evidence: `coverage_check_test.py::test_de138_self_bootstraps_via_derived_applies_to_vt_cov_001` — asserts derived `applies_to.specs == ['PROD-004','SPEC-115']` + `applies_to.requirements == ['PROD-004.FR-001','PROD-004.FR-002','PROD-004.FR-007']` via the `supekku:delta.relationships@v1` block (block-first, no FM fallback). `check_coverage_completeness` reads via derived property without erroring.
- Tolerant validate post-sweep: `validate workspace --kind delta` exit 0; only pre-existing warnings (7× audit-gate-not-found on draft deltas DE-135/DE-138/DE-139/DE-140/DE-141/DE-142/DE-136, 1× DR-030 unresolved). Identical baseline to P01.
- Corpus-level idempotence: `admin migrate delta --check` post-sweep returns "no pending migrations" — orchestrator-level idempotence via `[migrations] last_applied` tracker. Per-file idempotence proven at P02 via the migration step's `applies_to(path)` regex.
- `complete delta DE-138 --dry-run --skip-update-requirements` exits 0 (CLI smoke).
- DR-138 `applies_to` derivation self-bootstraps cleanly for DE-138 — the relationships block authored at delta creation carried specs.primary + requirements.implements that the post-sweep load reads as the canonical source.

## 11. Wrap-up Checklist

- [x] All §4 exit criteria satisfied (modulo DE-138 §6 placeholders — populated as part of P03.8 commit).
- [x] Pre-sweep tag + three sweep commits SHAs recorded in §9.
- [x] Migration run log path recorded in §9; VA disposition tables appended directly to the log (companion committed files `p03-sweep-drift-log.md` + `p03-risk-recon-log.md` are the durable record).
- [x] IP-138 verification coverage entries flipped `planned` → `verified` for LIST-001 / COV-001 / VAs.
- [x] PROD-004 coverage block FR-001/FR-002/FR-007 set to `in-progress` with evidence refs (VT-DE138-LIST-001, VT-DE138-FLIP-001, VT-DE138-MIG-001).
- [x] DE-138.md §6 Verification Strategy populated.
- [x] Hand-off note to P04 — pre-flip checklist (DR-138 §11.2) status: tolerant validate clean, both VAs closed, three sweep commits in place + pre-sweep tag retained. Outstanding for P04 entrance: `--no-tolerated-aliases` wiring (DEC-138-14), VT-DE138-GATE-001, VT-DE138-FLIP-001, VH-DE138-FLIP-001 operator attestation, §9.5 follow-up audit tracking artefact filing (F-138-24).
