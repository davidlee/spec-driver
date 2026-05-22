---
id: IP-139-P04
slug: "139-spec_artefact_metadata_propagation_prod_spec_blocks_taxonomy_strict_list_enrichment_de_136_child-phase-04"
name: IP-139 Phase 04
created: "2026-05-22"
updated: "2026-05-22"
status: draft  # one of: completed | deferred | draft | in-progress | pending
kind: phase  # one of: audit | delta | design_revision | issue | memory | phase | plan | policy | problem | prod | requirement | risk | spec | standard | task | verification
plan: IP-139
delta: DE-139
---

# Phase 04 — Strict flip + close

## 1. Objective

Flip `[validation.strict] spec = true` in `workflow.toml`, verify post-flip
gate is clean, write VT-DE139-FLIP-001 enforcement test, update IP/verification
coverage, and close DE-139.

## 2. Links & References

- **Delta**: DE-139
- **DR sections**: DR-139 §3 (strict-flip gate), DR-136 §11.3/§11.4 (flip mechanics + post-flip gate)
- **Design decisions**: DEC-139-08 (taxonomy strict), DEC-139-11 (loader tolerant until strict-flip)
- **Precedent**: DE-138 P04 (delta strict-flip — identical pattern)
- **Specs**: PROD-004 (FR-001/-002), SPEC-114, SPEC-116

## 3. Entrance Criteria

- [x] P03 complete — migration steps landed, sweep clean, template updated
- [x] 5549 tests passing, lint clean
- [x] `complete delta DE-139 --dry-run` passes
- [x] Pre-flip baseline captured: `validate workspace --kind spec --strict` returns 1 warning (PROD-004.FR-007 status mismatch — pre-existing, not DE-139 scope)
- [x] Pre-flip baseline: `validate workspace --strict` whole-corpus = 7× audit-gate warnings + 1× DR-030 error (matches DE-138 baseline exactly)

## 4. Exit Criteria / Done When

- [x] `[validation.strict] spec = true` + `[schema_version] spec = "0.10.0+003"` in workflow.toml
- [x] VT-DE139-FLIP-001: strict-on-validate enforcement test passing
- [x] Post-flip `validate workspace --kind spec --strict` ≤ pre-flip baseline (no new issues)
- [x] Post-flip `validate workspace --strict` whole-corpus — no regression
- [x] `complete delta DE-139 --dry-run` passes
- [x] IP-139 verification coverage entries updated to `status: verified`
- [x] IP-139 progress tracking updated (P03 + P04 checked)
- [ ] `spec-driver complete delta DE-139` succeeds
- [x] `list specs` smoke-check

## 5. Verification

- VT-DE139-FLIP-001: strict-mode enforcement test
  - Row 1 (baseline): post-flip `validate workspace --kind spec --strict` returns ≤ pre-flip baseline
  - Row 2 (enforcement): synthetic fixture — spec with a cut FM key (e.g. `packages:`) errors under strict mode
- Commands:
  - `just test` — full suite
  - `just lint` — ruff
  - `uv run spec-driver validate workspace --kind spec --strict`
  - `uv run spec-driver validate workspace --strict`
  - `uv run spec-driver complete delta DE-139 --dry-run`
  - `uv run spec-driver list specs`

## 6. Assumptions & STOP Conditions

- Assumptions:
  - `workflow.toml` `[validation.strict]` section already exists (from DE-138 delta flip); merge spec key under it
  - `[schema_version]` section already exists; merge spec key under it
  - Schema version `0.10.0+003` reflects last migration (`v0_10_0_003_prod_blocks`)
  - Strict-mode for spec kind uses same validator paths as delta kind (MetadataValidator strict-mode from DE-137)
  - Loader remains unconditionally tolerant (DEC-139-11); only validator escalates under strict
- STOP when:
  - Post-flip `validate workspace --kind spec --strict` surfaces NEW errors beyond the 1 known FR-007 warning
  - Whole-corpus `validate workspace --strict` regresses on non-spec kinds (wiring leaked across kind boundaries)

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description | Parallel? | Notes |
| ------ | --- | ----------- | --------- | ----- |
| [x] | 4.1 | Capture pre-flip baseline | [ ] | Entrance criteria |
| [x] | 4.2 | Write VT-DE139-FLIP-001 enforcement test + wire _validate_spec_blocks | [ ] | 5580 tests |
| [x] | 4.3 | Flip workflow.toml: spec strict + schema version | [ ] | spec=true, 0.10.0+003 |
| [x] | 4.4 | Post-flip baseline verification (FLIP-001 row 1) | [ ] | 1 warning (FR-007) |
| [x] | 4.5 | Post-flip gate: whole-corpus + dry-run + list smoke | [ ] | All pass |
| [x] | 4.6 | Update IP-139 verification coverage + progress | [ ] | All verified |
| [x] | 4.7 | Update notes.md | [ ] | ✓ |
| [ ] | 4.8 | `spec-driver complete delta DE-139` | [ ] | |

### Task Details

- **4.1 Capture pre-flip baseline**
  - Already captured during entrance criteria assessment:
    - `validate workspace --kind spec --strict`: 1 warning (PROD-004.FR-007)
    - `validate workspace --strict`: 7× audit-gate + 1× DR-030 error
    - `complete delta DE-139 --dry-run`: passes

- **4.2 Write VT-DE139-FLIP-001 enforcement test**
  - **Files**: near `spec_driver/presentation/cli/validate/workspace_test.py` or `supekku/scripts/lib/validation/`
  - **Design**: Fixture-based. Construct temp workspace with a spec carrying a cut FM key (e.g. `packages: [foo]`). Run validation under strict mode. Assert error surfaces identifying the cut key. Follows DE-138 P04 task 4.7 pattern (block-schema enforcement, not FM-key enforcement — adapt to whichever path applies for spec kind).

- **4.3 Flip workflow.toml**
  - **Files**: `.spec-driver/workflow.toml`
  - **Changes**: Add `spec = true` under `[validation.strict]`. Add `spec = "0.10.0+003"` under `[schema_version]`.
  - **Commit**: Discrete commit — only workflow.toml mutated. Message: `feat(DE-139): strict-flip — [validation.strict] spec=true + schema_version 0.10.0+003`.

- **4.4 Post-flip baseline (FLIP-001 row 1)**
  - `uv run spec-driver validate workspace --kind spec --strict` — expect ≤ pre-flip baseline (1 warning)
  - If NEW errors appear, STOP per §6.

- **4.5 Post-flip gate**
  - `uv run spec-driver validate workspace --strict` — no regression
  - `uv run spec-driver complete delta DE-139 --dry-run` — passes
  - `uv run spec-driver list specs` — rows render correctly

- **4.6 Update IP-139 verification coverage + progress**
  - Mark VT-DE139-FLIP-001 as `status: verified`
  - Mark VT-DE139-TAXONOMY-001/002, VT-DE139-BLOCKS-001 as `status: verified` (P01, deferred update)
  - Update P03/P04 progress checkboxes

- **4.7 Update notes.md**
  - P04 section with flip details, evidence, surprises

- **4.8 Close delta**
  - `uv run spec-driver complete delta DE-139`
  - Verify succeeded without `--force`

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| ---- | ---------- | ------ |
| Post-flip validation surfaces unexpected errors from spec kind | Pre-flip baseline already captured and clean; STOP gate protects | open |
| Strict-flip affects non-spec kinds (kind boundary leak) | Whole-corpus check (4.5) detects regression; revert is one-line workflow.toml edit | open |
| VT-DE139-FLIP-001 enforcement test targets wrong validation path | Review DE-138 P04 task 4.7 for applicable pattern; adapt to spec kind validator path | open |

## 9. Decisions & Outcomes

- `2026-05-22` — Pre-flip baseline captured: 1 warning (FR-007 status) for spec kind; 9 issues whole-corpus (all pre-existing)
- `2026-05-22` — Schema version `0.10.0+003` chosen to match last applied migration (`v0_10_0_003_prod_blocks`)

## 10. Findings / Research Notes

- DE-138 P04 pattern: baseline → enforcement test → flip → post-flip verify → close
- PROD-004.FR-007 warning is pre-existing (coverage evidence exists but FR status is `in-progress`); not blocking
- DR-030 error is pre-existing (ISSUE-057); not blocking

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
