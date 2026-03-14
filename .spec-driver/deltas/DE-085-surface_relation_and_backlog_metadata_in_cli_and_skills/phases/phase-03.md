---
id: IP-085.PHASE-03
slug: 085-surface_relation_and_backlog_metadata_in_cli_and_skills-phase-03
name: "Skills and verification"
created: "2026-03-09"
updated: "2026-03-09"
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-085.PHASE-03
plan: IP-085
delta: DE-085
objective: >-
  Update scope-delta skill to guide consistent metadata population when
  creating deltas from backlog items. Execute VA-085-001 agent verification.
  Update IP-085 verification coverage entries. Reconcile artefacts for closure.
entrance_criteria:
  - Phase 2 complete (CLI flags, formatters, --from-backlog enhancement)
exit_criteria:
  - scope-delta skill updated with context_inputs/relations guidance per DR-085 §5.9
  - VA-085-001 agent verification executed and documented
  - IP-085 verification.coverage entries updated to verified
  - IP-085 active phase reference updated
  - just check green
  - Delta ready for audit/closure via /close-change
verification:
  tests: []
  evidence:
    - VA-085-001
tasks:
  - id: T01
    summary: Update scope-delta skill with backlog metadata guidance
  - id: T02
    summary: Execute VA-085-001 agent verification
  - id: T03
    summary: Update IP-085 verification coverage entries
  - id: T04
    summary: Reconcile IP-085 and DE-085 artefacts for closure
  - id: T05
    summary: Run just check to confirm green
risks:
  - id: R1
    description: VA-085-001 scope unclear — manual walkthrough vs automated
    mitigation: Define as documented agent analysis; dry-run create delta --from-backlog and inspect output
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-085.PHASE-03
```

# Phase 3 — Skills and verification

## 1. Objective

Update the `scope-delta` skill to instruct agents to populate `context_inputs` and `relations` when creating deltas from backlog items (DR-085 §5.9). Execute VA-085-001 agent verification. Update all IP-085 verification coverage from `planned` to `verified`. Reconcile artefacts so the delta is ready for `/close-change`.

## 2. Links & References

- **Delta**: [DE-085](../DE-085.md) §3.6 (skills)
- **Design Revision**: [DR-085](../DR-085.md) §5.9 (skill updates)
- **Plan**: [IP-085](../IP-085.md) §4, §6, verification.coverage block
- **Phase 2 outputs**: CLI flags, formatters, `--from-backlog` enhancement — all committed

## 3. Entrance Criteria

- [x] Phase 2 complete — all exit criteria met, committed, `just check` green (3697 pass)

## 4. Exit Criteria / Done When

- [x] `scope-delta` SKILL.md updated with explicit `context_inputs`/`relations` guidance
- [x] VA-085-001 executed: `create delta --from-backlog IMPR-012` confirms metadata populated
- [x] IP-085 `verification.coverage` entries updated from `planned` to `verified`
- [x] IP-085 `status` updated, active phase reference updated to Phase 3
- [x] Phase 2 hand-off note completed
- [x] `just check` green (3697 pass)
- [x] Delta ready for `/close-change`

## 5. Verification

- VA-085-001: Agent analysis — run `create delta --from-backlog` with a real backlog item, inspect frontmatter for `context_inputs` and `relations` presence, document result
- `just check` — full suite (no code changes expected, but confirm green after artefact updates)

## 6. Assumptions & STOP Conditions

- **Assumption**: No code changes needed — Phase 3 is skill update + verification + artefact reconciliation only.
- **Assumption**: VA-085-001 is a documented agent analysis (dry-run + inspection), not an automated test.
- **STOP if**: VA-085-001 reveals that `--from-backlog` metadata population is broken or incomplete — revert to code fix before continuing.

## 7. Tasks & Progress

| Status | ID  | Description                         | Parallel? | Notes                                                     |
| ------ | --- | ----------------------------------- | --------- | --------------------------------------------------------- |
| [x]    | T01 | Update `scope-delta` SKILL.md       |           | Done — added backlog metadata guidance                    |
| [x]    | T02 | Execute VA-085-001                  |           | PASS — IMPR-012 test confirmed context_inputs + relations |
| [x]    | T03 | Update IP-085 verification coverage |           | Done — all 8 entries `planned` → `verified`               |
| [x]    | T04 | Reconcile IP-085 / DE-085 artefacts |           | Done — phase refs, progress, hand-off                     |
| [x]    | T05 | Run `just check`                    |           | 3697 pass, 0 fail                                         |

### Task Details

- **T01 — Update `scope-delta` SKILL.md**
  - **File**: `.spec-driver/skills/scope-delta/SKILL.md`
  - **Design**: DR-085 §5.9
  - **Change**: Add explicit instruction in step 3 (create delta from backlog item) to note that `--from-backlog` now auto-populates `context_inputs` and `relations`. Add guidance for manual delta creation to populate both fields when the delta is motivated by a backlog item.
  - **Content** (per DR-085 §5.9):
    > When creating a delta from a backlog item (or motivated by one), ensure:
    >
    > - `context_inputs` includes `type: issue` (or appropriate type) with the backlog item ID
    > - `relations` includes `type: relates_to` (or more specific type) with the backlog item ID as target
    > - `applies_to.requirements` includes any requirement IDs from the backlog item
    >   Note: `create delta --from-backlog` auto-populates `context_inputs` and `relations`.

- **T02 — Execute VA-085-001**
  - **Approach**: Run `uv run spec-driver create delta --from-backlog` with a test backlog item. Inspect the generated frontmatter. Verify `context_inputs` and `relations` are present and correct. Document findings in this phase sheet §9.
  - **Pass criteria**: Frontmatter contains both `context_inputs` and `relations` entries referencing the source backlog item.

- **T03 — Update IP-085 verification coverage**
  - **File**: `IP-085.md` — `verification.coverage` block
  - **Change**: Update each VT/VA entry `status` from `planned` to `verified` (VT-085-001 through VT-085-007 verified by passing tests; VA-085-001 verified by T02 result).

- **T04 — Reconcile IP-085 / DE-085 artefacts**
  - Update IP-085 §5 active phase reference to Phase 3
  - Update IP-085 §9 progress — mark Phase 3 complete
  - Update phase-02.md §11 hand-off note
  - Ensure DE-085 is ready for `/close-change`

- **T05 — `just check`**
  - Confirm full suite still green after any changes.

## 8. Risks & Mitigations

| Risk                                   | Mitigation                                        | Status   |
| -------------------------------------- | ------------------------------------------------- | -------- |
| R1: VA-085-001 scope ambiguity         | Defined as dry-run + inspection, documented in §9 | Resolved |
| R2: --from-backlog broken in edge case | Test with real backlog item; STOP if failure      | Open     |

## 9. Decisions & Outcomes

- 2026-03-09: VA-085-001 defined as agent-executed dry-run + inspection (not automated test). Created DE-086 from `--from-backlog IMPR-012`, confirmed frontmatter contains `relations: [{type: relates_to, target: IMPR-012}]` and `context_inputs: [{type: issue, id: IMPR-012}]`. Test delta cleaned up after verification. **PASS.**

## 10. Findings / Research Notes

- VA-085-001 evidence: `create delta --from-backlog IMPR-012` produced DE-086 with correct `context_inputs` (line 14-15) and `relations` (line 11-13) in frontmatter. No `--dry-run` flag exists on `create delta`, so verification required creating and deleting a real delta.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored (VA-085-001 in §9/§10)
- [x] Notes updated with findings
- [x] Delta ready for /close-change
