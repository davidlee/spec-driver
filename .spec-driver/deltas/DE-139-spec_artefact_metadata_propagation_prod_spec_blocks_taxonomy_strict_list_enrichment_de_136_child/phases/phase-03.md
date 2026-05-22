---
id: IP-139-P03
slug: "139-spec_artefact_metadata_propagation_prod_spec_blocks_taxonomy_strict_list_enrichment_de_136_child-phase-03"
name: IP-139 Phase 03
created: "2026-05-22"
updated: "2026-05-22"
status: draft  # one of: completed | deferred | draft | in-progress | pending
kind: phase  # one of: audit | delta | design_revision | issue | memory | phase | plan | policy | problem | prod | requirement | risk | spec | standard | task | verification
plan: IP-139
delta: DE-139
---

# Phase 03 — Migration + sweep + template

## 1. Objective

Land migration steps that cut deprecated FM fields from spec/prod artefacts,
emit block schemas where content existed, run the in-tree sweep, and update
the spec template to emit new blocks on creation.

## 2. Links & References

- **Delta**: DE-139
- **DR sections**: DR-139 §3.1 (SPEC field placement), §3.2 (PROD field placement), §4 (block schemas), §8 (code impacts)
- **Design decisions**: DEC-139-05 (packages cut), DEC-139-06 (scope→prose), DEC-139-07 (migration covers SPEC+PROD), DEC-139-10 (concerns block), DEC-139-11 (loader tolerant for cut FM)
- **Specs**: SPEC-114, SPEC-116
- **Prior art**: `v0_10_0_001_delta_blocks/` migration (pattern reference)

## 3. Entrance Criteria

- [x] P01 block schemas landed (concerns, hypotheses, decisions)
- [x] P01 FM field removals from model done
- [x] P01 taxonomy strict with unknown tolerance
- [x] P02 packages removal chain (model/index/CLI) complete
- [x] P02 list enrichment done
- [x] Block renderers exist: `render_spec_concerns_block`, `render_spec_hypotheses_block`, `render_spec_decisions_block`
- [x] 5066 tests passing, lint clean

## 4. Exit Criteria / Done When

- [x] `v0_10_0_002_spec_blocks` migration step lands, tests passing (33 tests)
- [x] `v0_10_0_003_prod_blocks` migration step lands, tests passing (18 tests)
- [x] In-tree sweep executed: 50 tech specs + 1 PROD spec processed
- [x] Post-sweep: zero specs with `packages:` in FM
- [x] Post-sweep: PROD-014 `scope:` moved to prose body (line 198)
- [x] Spec template emits concerns/hypotheses/decisions blocks on creation
- [x] Creation flow wired to render new blocks
- [x] All tests passing (5549), lint clean

## 5. Verification

- VT-DE139-MIG-001: spec migration — packages cut, category/c4_level defaulted, blocks emitted for non-empty concerns/hypotheses/decisions
- VT-DE139-MIG-002: prod migration — scope→prose, hypotheses/decisions→blocks, verification_strategy cut
- VT-DE139-CREATE-001: `spec-driver create spec` emits new block placeholders
- VT-DE139-TPL-001: template contains new block template variables
- VA-DE139-SWEEP-001: post-sweep validation (grep confirms zero legacy FM keys in tree)

Commands:
- `just test` — full suite
- `just lint` — ruff
- `just pylint-files <changed>` — pylint on touched files
- `grep -rl '^packages:' .spec-driver/tech/` — should return 0 post-sweep

## 6. Assumptions & STOP Conditions

- Assumptions:
  - Migration isolation contract (DEC-138-12) applies: step modules import only from `_protocol`, `_helpers`, stdlib, pyyaml
  - Protocol constraint (DEC-137-16): one `applies_to_kind` per step → two packages needed
  - 50 tech specs have only `packages:` as legacy FM field; 0 have concerns/hypotheses/decisions/verification_strategy/scope
  - 1 PROD (PROD-014) has `scope:` in FM; 0 PROD have hypotheses/decisions/verification_strategy
  - Block renderers are NOT imported by migration (isolation); migration emits raw YAML blocks
- STOP when: migration produces unexpected drift entries on >5 files

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID   | Description                                        | Parallel? | Notes |
| ------ | ---- | -------------------------------------------------- | --------- | ----- |
| [x]    | 3.1  | Create `v0_10_0_002_spec_blocks/` package          | [ ]       | ✓     |
| [x]    | 3.2  | Implement SpecBlocksStep.apply transform           | [ ]       | 33 tests |
| [x]    | 3.3  | Write VT-DE139-MIG-001 tests                       | [ ]       | 33 tests |
| [x]    | 3.4  | Create `v0_10_0_003_prod_blocks/` package          | [x]       | ✓     |
| [x]    | 3.5  | Implement ProdBlocksStep.apply transform           | [x]       | 18 tests |
| [x]    | 3.6  | Write VT-DE139-MIG-002 tests                       | [x]       | 18 tests |
| [x]    | 3.7  | Wire new blocks into spec template                 | [ ]       | 3 new vars |
| [x]    | 3.8  | Wire creation.py to render concerns/hypotheses/decisions blocks | [ ] | + backfill.py |
| [x]    | 3.9  | Write VT-DE139-CREATE-001 + VT-DE139-TPL-001 tests | [ ]       | 2 tests |
| [x]    | 3.10 | Run in-tree sweep (`spec-driver admin migrate`)    | [ ]       | 50 spec + 1 prod |
| [x]    | 3.11 | Post-sweep validation (VA-DE139-SWEEP-001)         | [ ]       | 0 legacy keys |
| [ ]    | 3.12 | Commit + update notes                              | [ ]       |       |

### Task Details

- **3.1 Create `v0_10_0_002_spec_blocks/` package**
  - **Files**: `spec_driver/migrations/v0_10_0_002_spec_blocks/__init__.py`
  - **Approach**: Mirror `v0_10_0_001_delta_blocks/` structure. Export `SpecBlocksStep` as `step`.

- **3.2 Implement SpecBlocksStep.apply transform**
  - **Files**: `spec_driver/migrations/v0_10_0_002_spec_blocks/migration.py`
  - **Design**: `applies_to_kind = "spec"`. Head-detect legacy keys: `packages`, `concerns`, `hypotheses`, `decisions`, `verification_strategy`, `scope`. Transform: strip cut keys from FM dict; if concerns/hypotheses/decisions had non-empty content, emit corresponding block in body (raw YAML, not via renderer imports). If scope had content, insert into prose body §1 (or append as paragraph). Default `category: unknown` and `c4_level: unknown` if missing. Use `_helpers.atomic_write` + `_helpers.split_frontmatter`.
  - **Drift**: emit drift entry for any non-empty cut field (not just packages).

- **3.3 Write VT-DE139-MIG-001 tests**
  - **Files**: `spec_driver/migrations/v0_10_0_002_spec_blocks/migration_test.py`
  - **Cases**: packages-only (typical), all-fields (synthetic), already-clean (skip), missing category/c4_level (defaults added), non-empty concerns→block emitted, idempotency.

- **3.4–3.6 PROD migration (parallel with 3.1–3.3)**
  - **Files**: `spec_driver/migrations/v0_10_0_003_prod_blocks/` — `__init__.py`, `migration.py`, `migration_test.py`
  - **Design**: `applies_to_kind = "prod"`. Cut: `hypotheses`, `decisions`, `verification_strategy`, `scope`. If scope non-empty, move to body prose. If hypotheses/decisions non-empty, emit blocks. Simpler than spec step (no packages, no category/c4_level defaults).

- **3.7 Wire new blocks into spec template**
  - **Files**: `supekku/templates/spec.md`
  - **Changes**: Add `{{ spec_concerns_block }}`, `{{ spec_hypotheses_block }}`, `{{ spec_decisions_block }}` after existing block placeholders. Add `category: unit` and `c4_level: code` to FM section.

- **3.8 Wire creation.py to render new blocks**
  - **Files**: `supekku/scripts/lib/specs/creation.py`
  - **Changes**: Import `render_spec_concerns_block`, `render_spec_hypotheses_block`, `render_spec_decisions_block`. Call them with empty defaults. Pass results to template render.

- **3.9 Write VT-DE139-CREATE-001 + VT-DE139-TPL-001 tests**
  - **Files**: near `supekku/scripts/lib/specs/creation_test.py` or `blocks/` tests
  - **Cases**: created spec file contains all 6 block placeholders; template raw text has all variables.

- **3.10 Run in-tree sweep**
  - **Command**: `uv run spec-driver admin migrate` (or equivalent)
  - **Scope**: 50 tech specs, 16 PROD specs
  - **Expected**: 50 specs touched (packages cut), 1 PROD touched (scope→prose), rest skipped

- **3.11 Post-sweep validation**
  - **Commands**: `grep -rl '^packages:' .spec-driver/tech/` (expect 0), `grep -rl '^scope:' .spec-driver/product/` (expect 0), `just test`, `just lint`

- **3.12 Commit + update notes**
  - Commit code + artefacts together per doctrine

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| ---- | ---------- | ------ |
| Migration breaks spec loading | P01 already removed fields from model; migration only touches FM text | open |
| Template variable not rendered | Test creation output explicitly (VT-DE139-CREATE-001) | open |
| Migration isolation violation | Follow DEC-138-12: no supekku imports, emit raw YAML strings | open |
| Scope→prose insertion misplaced | Detect existing §1 heading, insert after it; test with PROD-014 shape | open |

## 9. Decisions & Outcomes

- `2026-05-22` — Two migration packages (002 spec, 003 prod) per DEC-137-16 (one kind per step)
- `2026-05-22` — PROD step separate despite only 1 file — honors DEC-139-07, future-proofs

## 10. Findings / Research Notes

- 50/53 tech specs have `packages:` in FM; 0 have concerns/hypotheses/decisions/verification_strategy/scope
- 1/16 PROD specs has `scope:` (PROD-014); 0 have hypotheses/decisions/verification_strategy
- Block renderers exist in `blocks/relationships.py` (P01) but CANNOT be imported by migration (isolation contract)
- Migration must emit block YAML strings directly (same pattern as delta_blocks emitters)
- `backfill.py` passes block template vars as literal strings (legacy escape hatch); creation.py does real rendering

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to P04 (strict flip + close)
