---
id: IP-142-P04
slug: "142-revision_artefact_metadata_propagation_revision_frontmatter_metadata_change_block_enrichment_applies_to_derivation_de_136_child-phase-04"
name: IP-142 Phase 04 — patterns + migration + sweep + flip
created: "2026-05-29"
updated: "2026-05-29"
status: draft  # one of: completed | deferred | draft | in-progress | pending
kind: phase  # one of: audit | delta | design_revision | issue | memory | phase | plan | policy | problem | prod | requirement | risk | spec | standard | task | verification
plan: IP-142
delta: DE-142
---

# Phase 4 — patterns + migration + sweep + strict flip

## 1. Objective

Bring `kind:revision` to strict-validatable parity and flip the gate. Four
groups, in order:

- **A. Broaden ID patterns** (application code) — the SPEC-only `requirement_id`
  regex rejects 97 legitimate corpus refs (`PROD-*`/`ISSUE-*` containers, `NF-`
  token). Hoist two shared constants and reuse across the revision + verification
  blocks (DEC-142-08).
- **B. Migration step** `v0_10_0_005_revision_metadata` — cut universal + hand-rolled
  FM keys; synthesise a faithful `modify` block for FM-only records (no `move`, no
  `lifecycle`, **no drift** — DEC-142-09/10).
- **C. Template** — verify `supekku/templates/revision.md` is already narrow + block-canonical.
- **D. Sweep + flip** — migrate, strict-validate (VA-142-CORPUS-001), then manually
  set `[validation.strict].revision = true` (DEC-142-11).

## 2. Links & References

- **Design Revision Sections**: DR-142 §8 (migration + §8.0 pattern broadening), §8.1
  (flip sequence), §12 (DEC-142-08..11), §13 (residuals R-142-01/02 resolved/dissolved).
- **Specs / PRODs**: PROD-004.FR-001/FR-002.
- **Decisions (notes.md session 6)**: DEC-CONSULT-04/03/05/07 → DEC-142-08/09/10/11.
- **Precedent (mirror exactly)**:
  - `spec_driver/migrations/v0_10_0_004_audit_findings/{migration,migration_test}.py` —
    the step shape (`_transform`, `_emit_*_block`, `_append_block`, `applies_to/preview/apply`).
  - `spec_driver/migrations/_protocol.py` (`BaseMigrationStep`, `StepPreview`, `StepResult`),
    `_helpers.py` (`atomic_write`, `split_frontmatter`).
  - `blocks/verification_metadata.py:22` (`REQUIREMENT_ID_PATTERN` — the partial constant to fix+share).
  - `core/git.py:12` (`SHA_HEX_PATTERN`) — domain-local pattern-constant placement precedent (STD-003).
- **Backlog**: ISSUE-061 (generic-orchestrator drift-write gap — DEC-142-10, out of scope here).

## 3. Entrance Criteria

- [x] P01–P03 complete (engine rules, FM class, applies_to deriver, list enrichment).
- [x] P04 consult complete; DEC-142-08..11 ratified + recorded (DR-142 §8/§12, notes.md session 6).
- [x] Corpus facts verified: 42 revisions (27 block-bearing, 15 FM-only); all carry
      `aliases` + most carry `source_specs`/`destination_specs`/`requirements`; zero `move`
      blocks; zero populated `origin[]`; `lifecycle` optional.

## 4. Exit Criteria / Done When

- [ ] **A**: `REQUIREMENT_ID_PATTERN` + `SPEC_ID_PATTERN` live in one shared module (STD-003);
      revision_metadata.py's 7 hardcoded copies + verification_metadata.py's local copy both
      reuse them. VT-142-PATTERN-001 passes. Existing block-validator + verification suites green.
- [ ] **B**: `v0_10_0_005_revision_metadata/{__init__.py,migration.py,migration_test.py}` exist;
      auto-discovered by `admin migrate revision`. VT-142-MIGRATE-001/002/003/004 pass.
      Isolation honoured (stdlib + `_helpers` + `_protocol` + pyyaml only).
- [ ] **C**: a freshly `create revision`'d artefact validates `--strict` clean; template confirmed
      narrow + block-canonical (no FM cut needed, or minimal touch documented).
- [ ] **D**: `admin migrate revision` applied to the repo corpus; `validate --kind revision
      --strict` clean (VA-142-CORPUS-001), `--no-tolerated-aliases` clean; `[validation.strict].revision
      = true` set manually in `workflow.toml`. Any residual dispositioned + documented.
- [ ] Full `pytest supekku` green (modulo the 2 known width-wrap pre-existing failures);
      `just` (ruff/ty/pylint) clean — no new message types.
- [ ] DR-142/IP-142 coverage updated (VT-142-PATTERN/MIGRATE → verified, VA-142-CORPUS-001
      dispositioned); IP §9 P04 checked.

## 5. Verification

- **VT-142-PATTERN-001** (`blocks/metadata/patterns_test.py` or co-located): the broadened
  constants accept `SPEC-122.FR-003`, `PROD-007.NF-001`, `ISSUE-016.FR-016.001`,
  `PROD-014` (spec form); reject `XYZ-1.foo`, `SPEC-1.FR-1` (too-few digits), empty.
- **VT-142-MIGRATE-001**: record with FM `lifecycle`/`aliases`/`auditers`/`source` +
  `source_specs`/`destination_specs`/`requirements` → all cut; non-cut keys preserved.
- **VT-142-MIGRATE-002** (revised, DEC-142-09): FM-only record → synthesised
  `supekku:revision.change@v1` block with `specs[].action: updated`, `requirements[].action:
  modify`, `kind` derived from the `FR`/`NF` token, `destination.spec` = the requirement's
  container, **no `lifecycle`, no `origin`**; `StepResult.drift_entries == []`.
- **VT-142-MIGRATE-003**: record with an existing block + hand-rolled FM keys → block
  untouched (wins); FM keys cut; no synthesis; no drift.
- **VT-142-MIGRATE-004**: re-running on a migrated record (block present + keys already cut)
  → `applies_to` False / `changed=False` → skipped, byte-identical.
- **VA-142-CORPUS-001**: after `admin migrate revision` on the live corpus,
  `validate --kind revision --strict` reports clean (expected zero residual post-broadening);
  capture the command output as evidence. Any residual → manual disposition note in §9.
- Pin terminal width on any CLI-output assertions (suite is width-brittle).

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - Broadening is a pure relaxation: no previously-valid block becomes invalid. A pre-existing
    test that asserted *rejection* of `PROD-`/`NF-` encoded the bug → update it to assert acceptance.
  - Synthesis `kind`: `.FR-` → `functional`, `.NF-`/`.NFR-` → `non-functional` (frozen-local
    token heuristic). `destination.spec` = the requirement_id's container prefix (always the
    in-place `modify` target); for records with `source_specs`/`destination_specs` but no FM
    `requirements`, synthesise `specs[]` only with empty `requirements: []`.
  - The migration step holds **frozen-local copies** of the block marker/schema/version and the
    cut-key list (DEC-138-12 forbids supekku imports). The broadened *patterns* are NOT imported
    by the step — they are application-code validation, exercised post-migration by the orchestrator.
  - Template `supekku/templates/revision.md` is already narrow (verified: base FM +
    `{{ revision_change_block }}`); body §1 Source/Destination prose is narrative duplication →
    `--prune-duplicates` scope (DR §9, out).
- **STOP when**:
  - Post-migration `--strict` shows residual errors that broadened patterns do NOT explain —
    e.g. a genuine `modify` block missing `destination`, or a hand-authored `move` missing
    `origin`. `/consult` before mass hand-fixing or reclassifying as drift (DEC-142-10 assumed
    ~0 residual).
  - STD-003 dictates a shared-pattern home other than `blocks/metadata/patterns.py` → follow STD-003.
  - Auto-discovery does not pick up `v0_10_0_005` (registry edit unexpectedly required) → investigate
    before forcing.
  - The synthesis emitter would need a supekku import to be correct (isolation breach) → stop.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description | Parallel? | Notes |
| ------ | --- | ----------- | --------- | ----- |
| [ ] | 4.1 | RED: VT-142-PATTERN-001 — broadened constants accept PROD/ISSUE/NF + dotted suffix, reject garbage | [ ] | new/colocated test |
| [ ] | 4.2 | GREEN: shared `REQUIREMENT_ID_PATTERN` + `SPEC_ID_PATTERN` (STD-003 home); reuse in revision_metadata (7×) + verification_metadata | [ ] | collapses dup; fixes NF gap |
| [ ] | 4.3 | Regression: block-validator + verification suites green; fix any test that encoded the SPEC-only bug | [P] | relaxation only |
| [ ] | 4.4 | RED: `v005/migration_test.py` — VT-142-MIGRATE-001/002/003/004 | [ ] | fixtures from RE-042 (block) + RE-015/RE-040 (FM-only) shapes |
| [ ] | 4.5 | GREEN: `v005/{migration.py,__init__.py}` — cut keys + synthesise modify block (no move/lifecycle/drift); idempotent; block-wins | [ ] | mirror v004; isolation strict |
| [ ] | 4.6 | Confirm folder auto-discovery (`admin migrate revision --dry-run` lists the step); no registry edit | [ ] | folder-based `_discover_steps` |
| [ ] | 4.7 | Template: confirm fresh `create revision` validates `--strict`; minimal touch if needed | [P] | template already narrow |
| [ ] | 4.8 | Sweep: tolerant baseline → `migrate --dry-run` → `migrate` → `--strict` (VA-142-CORPUS-001) → `--no-tolerated-aliases`; disposition residual | [ ] | capture evidence |
| [ ] | 4.9 | MANUAL flip `[validation.strict].revision = true` in `workflow.toml` (DEC-142-11) | [ ] | after VA disposition |
| [ ] | 4.10 | Verify: full `pytest supekku` + `just` clean; update DR/IP coverage; IP §9 P04 | [ ] | no new pylint message types |

### Task Details

- **4.2 Shared ID-pattern constants**
  - **Design / Approach**: new `supekku/scripts/lib/blocks/metadata/patterns.py` (sibling to
    `schema.py`) holding `REQUIREMENT_ID_PATTERN = r"^(SPEC|PROD|ISSUE)-\d{3,}(?:-[A-Z0-9]+)*\.(FR|NF|NFR)-[A-Z0-9.-]+$"`
    and `SPEC_ID_PATTERN = r"^(SPEC|PROD|ISSUE)-\d{3,}(?:-[A-Z0-9]+)*$"`. Confirm placement
    against STD-003 first.
  - **Files**: `blocks/metadata/patterns.py` (NEW), `blocks/revision_metadata.py` (replace 7
    hardcoded regexes at :99/:109/:119/:129/:206/:275 and the two `SPEC_ID_PATTERN` sites
    :74/:269/:289), `blocks/verification_metadata.py:22` (replace local constant, drop the dup).
  - **Testing**: VT-142-PATTERN-001 + existing verification/revision block tests stay green.

- **4.5 Migration step**
  - **Design / Approach**: `RevisionMetadataStep(BaseMigrationStep)`, `applies_to_kind="revision"`.
    `_transform(text)`: split FM; cut keys `{lifecycle, aliases, auditers, source, source_specs,
    destination_specs, requirements}`; if FM-only (had scope keys, no block) synthesise the block
    via a frozen-local `_emit_revision_change_block(...)` and `_append_block`; if block present →
    just cut keys. `apply()` returns `drift_entries=[]` always (DEC-142-10).
  - **Files**: `spec_driver/migrations/v0_10_0_005_revision_metadata/{__init__.py,migration.py,migration_test.py}` (NEW).
  - **Testing**: VT-142-MIGRATE-001..004.

- **4.8 Sweep (DR §8.1 order)**
  - `uv run spec-driver validate --kind revision` (tolerant baseline)
  - `uv run spec-driver admin migrate revision --dry-run` (preview)
  - `uv run spec-driver admin migrate revision` (apply)
  - `uv run spec-driver validate --kind revision --strict` → **VA-142-CORPUS-001** (expect clean)
  - manual disposition of residual (expected none); `--strict --no-tolerated-aliases` final gate.
  - **Commit** the migrated corpus + code together or separately (repo doctrine: small commits).

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| ---- | ---------- | ------ |
| Broadening relaxes the *verification* block too | Same ID universe; VT-142-PATTERN-001 confirms garbage still rejected; intended reuse | design |
| Synthesis mis-derives `kind` from an odd ID token | `.FR-`→functional, `.NF-`/`.NFR-`→non-functional; default + flag on unknown token | design |
| Idempotence regression (double-migrate corrupts) | VT-142-MIGRATE-004 byte-identical guard; `applies_to` gates on FM-key presence | design |
| Residual strict errors after migrate (R-142-01 leftovers) | Expected ~0 after broadening; if >handful → STOP + /consult, do not mass-drift | design |
| Migration step accidentally imports supekku (isolation breach) | Frozen-local block constants + cut-list; import only `_helpers`/`_protocol`/yaml (DEC-138-12) | design |
| `--prune-duplicates` body prose left in place reads as duplication | Out of scope (DR §9); umbrella close asks only "no NEW structural duplication" | accepted |

## 9. Decisions & Outcomes

- `2026-05-29` — **DEC-142-08 (broaden patterns)**, **DEC-142-09 (modify + omit lifecycle, no
  `unknown`)**, **DEC-142-10 (no auto-drift; ISSUE-061)**, **DEC-142-11 (manual flip)** — ratified
  at P04 consult; see DR-142 §8/§12 + notes.md session 6 for evidence and rationale.

## 10. Findings / Research Notes

- **Pattern violators (verified)**: 97 refs across ~24 records — `PROD-*` (17 families),
  `ISSUE-016`, `SPEC-110/122`; `NF-` token (99 NF reqs repo-wide vs 437 FR). Sibling delta
  relationships block has NO ID patterns. `verification_metadata.REQUIREMENT_ID_PATTERN`
  already broadened prefix to `(SPEC|PROD)` but still misses `NF`/`ISSUE` — fix it in the share.
- **Migration isolation (DEC-138-12)**: v004 holds frozen-local `_MARKER`/`_SCHEMA`/`_VERSION` +
  `_VALID_OUTCOMES`; imports only `_helpers`/`_protocol`/yaml. v005 mirrors this.
- **Discovery**: `_discover_steps` iterates `migrations/` dirs (sorted), imports module-level
  `step`. Folder creation = registration; no `_registry` edit. v001–v004 exist; v005 next.
- **Template**: `supekku/templates/revision.md` FM is already narrow (id/name/slug/kind/status/
  created/updated) with `{{ revision_change_block }}`; no hand-rolled scope keys. Body §1
  Source/Destination/Requirements prose remains (narrative dup → `--prune-duplicates`, out).
- **Drift**: `StepResult.drift_entries` is a `list[Path]` the orchestrator logs but never
  materialises to DL files (ISSUE-061). v005 returns `[]` regardless — faithful synthesis isn't drift.

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored (§5 / §9) — VA-142-CORPUS-001 output captured
- [ ] DR-142/IP-142 coverage updated; IP §9 P04 checked
- [ ] `[validation.strict].revision = true` confirmed in `workflow.toml`
- [ ] Hand-off: DE-142 ready to close (audit deferred to DE-136 umbrella, VA-DE136-CLOSE-001);
      then DE-136 P03 tasks 3.9–3.11 (flip confirm, baseline) → DE-136 P04 umbrella close
