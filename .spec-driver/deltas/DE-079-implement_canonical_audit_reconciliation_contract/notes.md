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

### Phase 2 execution — complete

#### All tasks completed

- **2.1 resolve_audit_gate**: pure function resolving `auto`/`required`/`exempt` to effective gate value. 9 tests.
- **2.2 collect_gating_findings**: collects findings from completed conformance audits matching `delta_ref`. Multi-audit union with collision detection (DEC-079-008). 7 tests.
- **2.3 derive_closure_effect**: pure function implementing DR-079 closure-effect derivation rules. Conformance: pending→block, reconciled→none, tolerated_drift→block (DEC-079-006), follow-up+ref→warn, follow-up-no-ref→block. Discovery: pending→warn, others→none. closure_override can relax but never escalate. 15 tests.
- **2.4 check_audit_completeness**: top-level orchestrator: resolve gate → collect findings → derive effects → return result. 7 tests.
- **2.5 Wire into complete_delta.py**: added audit check after coverage check; blocks on blocking findings, displays warnings for non-blocking ones. `--force` bypasses. Updated existing test mock.
- **2.6–2.8 Tests**: 46 tests in audit_check_test.py (VT-079-002, -003, -004), plus 13 in complete_delta_test.py.

#### Verification status

- `just check` passes: ruff clean, 3573 tests pass, pylint 9.72/10
- `just pylint-files` on touched files: 9.89/10

#### Observations

- `ChangeArtifact` exposes `path` reliably for raw frontmatter re-reading.
- `audit_gate` is not on `ChangeArtifact` dataclass — read from raw delta frontmatter. This is fine since only the audit check path needs it.
- `complete_delta.py` complexity grew slightly (too-many-statements: 57/50) but the audit check call is just 6 lines. The bulk of complexity is pre-existing.

#### Phase 2 → Phase 3 handoff

- Phase 3 is validation rules: audit-specific rules in validator.py — missing audits, undispositioned findings, invalid pairs, finding ID collisions, closure_override without rationale.

### Phase 3 execution — complete

#### All tasks completed

- **3.1 \_validate_audit_disposition**: validates each completed audit's findings for: missing disposition (warning), invalid status×kind (error), invalid outcome×kind (error), closure_override without rationale (error). Only completed audits are checked — drafts are skipped.
- **3.2 \_validate_audit_gate_coverage**: for each delta, resolves audit_gate via `resolve_audit_gate`. If required and no completed conformance audit exists → warning. Finding ID collisions across multi-audit union → warning. Refactored into 3 methods (`_validate_audit_gate_coverage`, `_build_conformance_audit_index`, `_check_finding_id_collisions`) to satisfy pylint complexity limits.
- **3.3 Tests**: 11 new tests covering all 6 validation rules + positive/negative/skip cases. 2 existing tests updated (assertions now filter audit gate warnings that fire on deltas with requirements but no conformance audit).

#### Verification status

- `just check` passes: ruff clean, 3583 tests pass (30 in validator_test.py), pylint 9.72/10
- `just pylint-files` on touched files: 9.92/10 (5 messages, all pre-existing/structural)

#### Adaptations

- Existing tests `test_validator_reports_missing_relation_targets` and `test_validator_checks_change_relations` needed assertion updates — they create deltas with requirements, which now triggers the audit gate warning. Fixed by filtering to error-level or excluding audit gate messages.
- `_validate_audit_gate_coverage` initially had McCabe 12 and 18 locals — extracted `_build_conformance_audit_index` and `_check_finding_id_collisions` helpers to resolve.

#### Imports / reuse

- Reuses `resolve_audit_gate` from `audit_check.py` (not duplicated)
- Reuses `VALID_STATUS_KIND_PAIRS`, `VALID_OUTCOME_KINDS`, `AUDIT_MODE_CONFORMANCE` from `audit.py`
- Uses `load_markdown_file` directly (not the private `_load_audit_frontmatter` from audit_check.py)

#### Commits

- Uncommitted — code + .spec-driver changes ready to commit together.

#### Phase 3 → Phase 4 handoff

- Phase 4 is skill rewrite: `audit-change` as canonical reconciliation runsheet.

### Phase 4 execution — complete

#### All tasks completed

- **4.1 audit-change rewrite**: rewrote `supekku/skills/audit-change/SKILL.md` from advisory audit guidance into the canonical reconciliation runsheet.
  - description now states that the skill is the canonical `AUD-*` runsheet
  - requires creating or updating an `AUD-*` artefact before treating the audit as closure-grade work
  - anchors to the real CLI surface: `spec-driver create audit --mode ... --delta ...`
  - requires per-finding machine-checkable disposition
  - requires reconciliation before `/close-change`
- **4.2 Generated skill refresh**: refreshed `.spec-driver/skills/audit-change/SKILL.md` and `.spec-driver/AGENTS.md` using the current workspace flow:
  - `uv run spec-driver install -y .`
  - confirmed the generated skill copy matches the packaged skill
  - confirmed `AGENTS.md` exposes the stronger audit-change description
- **4.3 Verification**: `just check` passes after the skill rewrite.

#### Verification status

- `just check` passes: ruff clean, 3583 tests pass, pylint 9.72/10
- `AGENTS.md` entry now reads:
  - `Canonical reconciliation runsheet for AUD artefacts. Create or update the audit, disposition every finding, reconcile specs/contracts, and hand off to closure only when audit state supports it.`

#### Observations

- The dedicated historical skill-sync command is gone in this CLI; the supported workspace refresh flow for generated skill copies in this repo is currently `uv run spec-driver install -y .`.
- That install emitted a warning about `audit-check` being allowlisted but missing:
  - `.spec-driver/skills.allowlist` contains `audit-check`
  - no packaged `audit-check` skill exists
  - the warning is workspace state and unrelated to the phase-4 rewrite itself

#### Phase 4 closure

- DE-079 phase 4 is complete.
- Commit: `1d263ad` — `feat(DE-079): phase 4 audit-change runsheet`
