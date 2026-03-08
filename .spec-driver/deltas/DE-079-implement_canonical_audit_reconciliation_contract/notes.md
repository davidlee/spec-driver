# Notes for DE-079

## 2026-03-09

### Delta scoping and DR drafting

- Created DE-079 from DR-055 audit-loop design (DEC-055-011 through DEC-055-015).
- Drafted DR-079 with section-by-section design triage and adversarial review.
- 11 design decisions accepted, 0 open questions.
- Key decisions:
  - DEC-079-001: inline per-finding disposition with structured refs and drift_refs
  - DEC-079-002: canonical change lifecycle statuses (draft → in-progress → completed)
  - DEC-079-003: audit_gate: auto | required | exempt on delta frontmatter
  - DEC-079-004: remove patch_level and next_actions entirely (only 2 existing audits)
  - DEC-079-005: closure_effect derived, never stored
  - DEC-079-006: conformance + tolerated_drift defaults to block
  - DEC-079-007: status routes, kind classifies
  - DEC-079-008: multi-audit union with collision warning
  - DEC-079-009: outcome × kind validity enforced
  - DEC-079-010: audit_gate is top-level frontmatter
  - DEC-079-011: audit_check.py as separate module

### Phase planning

- IP-079 planned with 4 phases:
  1. Schema foundation (metadata, template, creation, deprecated field removal)
  2. Audit gating module (audit_check.py + complete_delta integration)
  3. Validation rules
  4. Skill rewrite (audit-change)
- Phase 1 sheet created with detailed task breakdown.

### Phase 1 execution — complete

#### All tasks completed
- **1.1 Disposition constants**: defined in `audit.py` — `DISPOSITION_STATUS_*`, `DISPOSITION_KIND_*`, `FINDING_OUTCOME_*`, `AUDIT_MODE_*`, validity matrices `VALID_STATUS_KIND_PAIRS` and `VALID_OUTCOME_KINDS`.
- **1.2 Audit frontmatter schema**: rewrote `audit.py` — added `mode`, `delta_ref`, `disposition` sub-schema per finding (with `refs`, `drift_refs`, `rationale`, `closure_override`). Removed `patch_level` and `next_actions` entirely.
- **1.3 Delta frontmatter schema**: added `audit_gate` (enum: auto|required|exempt) and `audit_gate_rationale` to `delta.py`. Constants: `AUDIT_GATE_AUTO`, `AUDIT_GATE_REQUIRED`, `AUDIT_GATE_EXEMPT`.
- **1.4 Audit template**: updated `supekku/templates/audit.md` with `mode`, `delta_ref`, disposition structure. Removed deprecated fields.
- **1.5 create_audit**: extended with `mode` and `delta_ref` parameters in both `creation.py` and CLI (`create.py`).
- **1.6 Edit existing audits**: AUD-001 — removed `patch_level` and `next_actions`, changed `status: complete` → `completed`, added `mode: discovery`. AUD-002 — changed `status: complete` → `completed`, added `mode: discovery`.
- **1.7 Tests**: rewrote `audit_test.py` — 25 tests covering valid/invalid disposition, mode, delta_ref, structured refs, closure_override. All pass.

#### Verification status
- `just check` passes: ruff clean, 3526 tests pass, pylint 9.71/10
- `just pylint-files` on touched files: 9.71/10 (21 messages; baseline was 9.73/10 with 16 messages — delta is structural: duplicate-code from FieldMetadata pattern, too-many-arguments on CLI command shape, too-many-public-methods on test class)

#### Commits
- `78725dd` docs(DE-055): audit-loop design — disposition contract, drift-ledger compatibility
- `238f939` docs(DE-079): scope delta and draft DR for canonical audit reconciliation contract
- `6a43e7f` docs(DE-079): IP and phase 1 — schema foundation plan
- Code + artefact changes pending commit.

#### Observations
- `FieldMetadata` handles nested objects in arrays well — the `disposition` sub-schema within `findings` items works cleanly. No depth issues.
- The existing dual-validation pattern (`_validate_both`) in test files tests against both old and new validators. The old `validate_frontmatter` function is permissive enough that it doesn't reject unknown fields, so removing `patch_level`/`next_actions` from the new schema doesn't break old-validator compat.
- Pre-existing Pyright diagnostics in `creation.py` and `create.py` are unrelated to this work.

#### Phase 1 → Phase 2 handoff
- Phase 2 is audit_check.py + complete_delta integration (see IP-079).
- All schema foundations are in place for phase 2 to consume.
