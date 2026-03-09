---
id: IP-086.PHASE-03
slug: 086-memory_verification_primitive_sha_stamped_attestation_for_staleness_tracking-phase-03
name: 'IP-086 Phase 03: Skills and cleanup'
created: '2026-03-10'
updated: '2026-03-10'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-086.PHASE-03
plan: IP-086
delta: DE-086
objective: >-
  Update memory skills with confidence calibration and staleness awareness,
  validate backward compatibility, sweep verification coverage, and create
  backlog item for list.py factoring.
entrance_criteria:
  - Phase 02 complete (CLI + staleness tested and committed)
exit_criteria:
  - /capturing-memory skill includes confidence calibration guidance per DR §5.9
  - /retrieving-memory skill surfaces staleness qualitatively per DR §5.9
  - /reviewing-memory skill uses list --stale as default review queue per DR §5.9
  - Existing memories without verified_sha or confidence load and display correctly
  - list memories (without --stale) still works normally
  - just passes (tests + ruff + pylint report)
  - IP-086 verification coverage entries updated to reflect actual state
  - Backlog item created for list.py factoring review
verification:
  tests:
    - VA-skill-integration
    - VA-backward-compat
  evidence: []
tasks:
  - id: '3.1'
    description: Update /capturing-memory with confidence calibration guidance
  - id: '3.2'
    description: Update /retrieving-memory with staleness qualitative surfacing
  - id: '3.3'
    description: Update /reviewing-memory to use list --stale as review queue
  - id: '3.4'
    description: Validate backward compatibility
  - id: '3.5'
    description: Update IP-086 verification coverage entries
  - id: '3.6'
    description: Create backlog item for list.py factoring
  - id: '3.7'
    description: Final verification sweep (just passes)
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-086.PHASE-03
```

# Phase 03 — Skills and Cleanup

## 1. Objective
Update memory skills with DE-086 awareness (confidence calibration, staleness surfacing, stale-first review queue). Validate backward compatibility. Sweep verification coverage to reflect actual state. Create backlog items for deferred work.

## 2. Links & References
- **Delta**: [DE-086](../DE-086.md)
- **Design Revision**: [DR-086](../DR-086.md) §5.9 (skill integration)
- **Specs**: SPEC-132 (memory), SPEC-110 (CLI)
- **Phase 02 notes**: [notes.md](../notes.md)

## 3. Entrance Criteria
- [x] Phase 02 complete (CLI + staleness tested and committed)

## 4. Exit Criteria / Done When
- [x] `/capturing-memory` includes confidence calibration guidance (low/medium/high definitions, default medium, require justification for high)
- [x] `/retrieving-memory` surfaces staleness qualitatively when presenting memories
- [x] `/reviewing-memory` uses `list memories --stale` output as default review queue; prioritizes tier 1
- [x] Existing memories without `verified_sha` or `confidence` load and display correctly (VA-backward-compat)
- [x] `list memories` (without `--stale`) still works normally
- [x] `just` passes (tests + ruff + pylint report)
- [x] IP-086 verification coverage entries updated to reflect actual state
- [x] Backlog item created for list.py factoring review (ISSUE-048)

## 5. Verification
- Run: `just` (full suite)
- Agent review of skill changes (VA-skill-integration)
- Manual test: `uv run spec-driver list memories` with existing memories (VA-backward-compat)

## 6. Assumptions & STOP Conditions
- Skills source is `supekku/skills/`, installed copies are derived via sync
- After editing source skills, run `uv run spec-driver sync --skills` to update installed copies
- STOP if skill changes would require schema or CLI code changes (scope creep)

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 3.1 | Update `/capturing-memory` with confidence calibration | [P] | DR §5.9 — added after step 3 |
| [x] | 3.2 | Update `/retrieving-memory` with staleness surfacing | [P] | DR §5.9 — added to output discipline |
| [x] | 3.3 | Update `/reviewing-memory` with stale-first queue | [P] | DR §5.9 — replaced step 1 |
| [x] | 3.4 | Validate backward compatibility | — | VA-backward-compat: passed |
| [x] | 3.5 | Update IP-086 verification coverage entries | — | All entries now verified |
| [x] | 3.6 | Create backlog item for list.py factoring | — | ISSUE-048 |
| [x] | 3.7 | Final verification sweep | — | 3773 passed, ruff clean, pylint 9.72 |

### Task Details

- **3.1 Update `/capturing-memory`**
  - **Files**: `supekku/skills/capturing-memory/SKILL.md`
  - **Design**: DR §5.9 — add confidence calibration guidance after step 3 (create the record). Define low/medium/high. Default medium. Require justification for high. Reinforce: creation is authoring, not verification.

- **3.2 Update `/retrieving-memory`**
  - **Files**: `supekku/skills/retrieving-memory/SKILL.md`
  - **Design**: DR §5.9 — add staleness qualitative surfacing to output discipline section. Use language like "not attested", "many commits since attestation", "recently attested, scope is quiet". No numeric thresholds.

- **3.3 Update `/reviewing-memory`**
  - **Files**: `supekku/skills/reviewing-memory/SKILL.md`
  - **Design**: DR §5.9 — update step 1 to use `list memories --stale` as default review queue. Prioritize tier 1 (scoped+attested+high commit count). Flag unscoped for manual review by age.

- **3.4 Validate backward compatibility**
  - Run `uv run spec-driver list memories` and confirm existing memories (many without `verified_sha` or `confidence`) load and display correctly.
  - Run `uv run spec-driver show memory <id>` for a memory without those fields.

- **3.5 Update IP-086 verification coverage**
  - Update VT-memory-verified-sha, VT-frontmatter-writer, VT-confidence-required from `planned` to `verified` (Phase 01 coverage).
  - Update VA-skill-integration and VA-backward-compat after tasks 3.1–3.4.

- **3.6 Create backlog item for list.py factoring**
  - `spec-driver create issue "..." --tag cli,refactoring`

- **3.7 Final verification sweep**
  - Run `just` and confirm full pass.

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| Skill sync overwrites installed copies | Edit source in supekku/skills/, sync after | Known pattern |

## 9. Decisions & Outcomes

## 10. Findings / Research Notes

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied
- [x] Verification evidence: 3773 passed, 0 failed; ruff clean; pylint 9.72/10
- [x] IP-086 verification coverage all `verified`
- [ ] Hand-off to audit
