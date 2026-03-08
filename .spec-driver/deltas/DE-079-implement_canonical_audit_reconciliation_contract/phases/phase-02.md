---
id: IP-079.PHASE-02
slug: 079-implement_canonical_audit_reconciliation_contract-phase-02
name: "IP-079 Phase 02 — Audit gating module"
created: '2026-03-09'
updated: '2026-03-09'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-079.PHASE-02
plan: IP-079
delta: DE-079
objective: >-
  Build audit_check.py module with gate resolution, finding collection,
  closure-effect derivation, and multi-audit union. Wire into complete_delta.py
  as a pre-check for qualifying deltas.
entrance_criteria:
  - Phase 1 complete — audit/delta schema foundation landed and committed
exit_criteria:
  - audit_check.py exists with resolve_audit_gate, collect_gating_findings, derive_closure_effect, check_audit_completeness
  - complete_delta.py calls audit completeness check after coverage check
  - Qualifying deltas blocked without reconciled conformance audit (unless --force)
  - Discovery audits warn but do not block
  - Multi-audit union collects findings across multiple AUD artefacts for same delta
  - Finding ID collisions across audits produce warnings
  - VT-079-002 tests pass (closure-effect derivation)
  - VT-079-003 tests pass (audit_gate resolution)
  - VT-079-004 tests pass (complete_delta integration)
  - Both linters clean on all touched files
verification:
  tests:
    - VT-079-002
    - VT-079-003
    - VT-079-004
  evidence:
    - VA-079-002
tasks:
  - id: "2.1"
    description: Implement resolve_audit_gate
  - id: "2.2"
    description: Implement collect_gating_findings
  - id: "2.3"
    description: Implement derive_closure_effect
  - id: "2.4"
    description: Implement check_audit_completeness (top-level orchestrator)
  - id: "2.5"
    description: Wire audit check into complete_delta.py
  - id: "2.6"
    description: Write VT-079-002 tests (closure-effect derivation)
  - id: "2.7"
    description: Write VT-079-003 tests (audit_gate resolution)
  - id: "2.8"
    description: Write VT-079-004 tests (complete_delta integration)
risks:
  - description: complete_delta.py already complex — adding audit check may degrade readability
    mitigation: Separate module (DEC-079-011) keeps complete_delta thin; only import + call
  - description: ChangeArtifact dataclass does not expose audit-specific frontmatter
    mitigation: Read raw frontmatter via load_markdown_file for audit files
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-079.PHASE-02
```

# Phase 2 — Audit Gating Module

## 1. Objective

Build `audit_check.py` following the `coverage_check.py` pattern: a self-contained module that resolves audit gates, collects gating findings from conformance audits, derives closure effects, and reports audit completeness. Wire it into `complete_delta.py` as a pre-check.

## 2. Links & References
- **Delta**: DE-079
- **Design Revision**: DR-079 §3 (State Transitions / Lifecycle Impact), §4 (closure-effect derivation rules)
- **Design Decisions**: DEC-079-003 (audit_gate), DEC-079-005 (closure_effect derived), DEC-079-006 (tolerated_drift blocks), DEC-079-008 (multi-audit union), DEC-079-011 (separate module)
- **Specs**: SPEC-116, PROD-008, PROD-011
- **Pattern**: `supekku/scripts/lib/changes/coverage_check.py` — structural pattern for the new module

## 3. Entrance Criteria
- [x] Phase 1 complete — audit/delta schema foundation committed

## 4. Exit Criteria / Done When
- [ ] `audit_check.py` exists at `supekku/scripts/lib/changes/audit_check.py`
- [ ] `resolve_audit_gate(delta) -> str` — resolves `auto` to `required`/`non-gating` based on `applies_to.requirements`
- [ ] `collect_gating_findings(delta_id, audit_registry) -> list[Finding]` — collects findings from all completed conformance audits with matching `delta_ref`
- [ ] `derive_closure_effect(mode, outcome, status, kind, closure_override) -> str` — returns `block`/`warn`/`none`
- [ ] `check_audit_completeness(delta_id, workspace) -> AuditCheckResult` — top-level orchestrator
- [ ] `complete_delta.py` calls `check_audit_completeness` after coverage check, blocks on `block` findings
- [ ] `--force` bypasses audit check (same pattern as coverage bypass)
- [ ] Discovery audits produce `warn` for pending findings, not `block`
- [ ] Multi-audit union: multiple AUD artefacts with same `delta_ref` contribute findings
- [ ] Finding ID collisions across audits produce a warning
- [ ] VT-079-002: closure-effect derivation tests pass
- [ ] VT-079-003: audit_gate resolution tests pass
- [ ] VT-079-004: complete_delta integration tests pass
- [ ] `just lint` clean
- [ ] `just pylint-files` clean on touched files

## 5. Verification
- `uv run pytest supekku/scripts/lib/changes/audit_check_test.py -v`
- `uv run pytest supekku/scripts/complete_delta_test.py -v` (if integration tests added there)
- `just lint`
- `just pylint-files supekku/scripts/lib/changes/audit_check.py supekku/scripts/complete_delta.py`

## 6. Assumptions & STOP Conditions
- Assumptions:
  - Audit frontmatter (mode, delta_ref, findings) is accessible via `load_markdown_file` on audit artifact paths
  - `ChangeRegistry(kind="audit")` collects all AUD artefacts; filtering by `delta_ref` is done in `collect_gating_findings`
  - The `--force` flag in `complete_delta` already bypasses coverage; same pattern applies to audit check
- STOP when:
  - `ChangeArtifact` does not reliably expose `path` for re-reading raw frontmatter
  - Audit frontmatter shape differs materially from what phase 1 schema defines

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [ ] | 2.1 | Implement resolve_audit_gate | [P] | Pure function, independent |
| [ ] | 2.2 | Implement collect_gating_findings | [ ] | Needs audit registry access |
| [ ] | 2.3 | Implement derive_closure_effect | [P] | Pure function, independent |
| [ ] | 2.4 | Implement check_audit_completeness | [ ] | Depends on 2.1, 2.2, 2.3 |
| [ ] | 2.5 | Wire audit check into complete_delta.py | [ ] | Depends on 2.4 |
| [ ] | 2.6 | Write VT-079-002 tests (closure-effect) | [P] | Can write alongside 2.3 |
| [ ] | 2.7 | Write VT-079-003 tests (gate resolution) | [P] | Can write alongside 2.1 |
| [ ] | 2.8 | Write VT-079-004 tests (integration) | [ ] | Depends on 2.5 |

### Task Details

- **2.1 resolve_audit_gate**
  - **Files**: `supekku/scripts/lib/changes/audit_check.py`
  - **What**: Takes a delta's `audit_gate` field (default: `auto`) and `applies_to.requirements` list. Returns `"required"` or `"non-gating"` (for `auto` resolution) or the explicit value.
  - **Logic**:
    - `auto` + non-empty requirements → `required`
    - `auto` + empty requirements → `non-gating`
    - `required` → `required`
    - `exempt` → `exempt` (caller checks for rationale)

- **2.2 collect_gating_findings**
  - **Files**: `supekku/scripts/lib/changes/audit_check.py`
  - **What**: Given a `delta_id`, find all AUD artefacts where `delta_ref == delta_id` and `mode == conformance` and `status == completed`. Union their findings. Warn on finding ID collisions.
  - **Approach**: Use `ChangeRegistry(kind="audit").collect()` to get all audits, filter by reading raw frontmatter from each audit's `path`.

- **2.3 derive_closure_effect**
  - **Files**: `supekku/scripts/lib/changes/audit_check.py`
  - **What**: Pure function implementing DR-079 §4 closure-effect derivation rules. Returns `"block"`, `"warn"`, or `"none"`.
  - **Rules** (from DR-079):
    - conformance + pending → block
    - conformance + reconciled → none
    - conformance + tolerated_drift + accepted → block (DEC-079-006)
    - conformance + accepted + follow_up kind + valid owned ref → warn
    - conformance + accepted + follow_up kind + no valid ref → block
    - discovery + pending → warn
    - discovery + reconciled/accepted → none
  - `closure_override` can relax block→warn or block→none (never escalate)

- **2.4 check_audit_completeness**
  - **Files**: `supekku/scripts/lib/changes/audit_check.py`
  - **What**: Top-level function: resolve gate → if non-gating/exempt return pass → collect findings → derive effects → return result with blocking/warning findings.
  - **Returns**: Dataclass with `is_complete`, `blocking_findings`, `warning_findings`, `gate_resolution`, `audits_found`.

- **2.5 Wire into complete_delta.py**
  - **Files**: `supekku/scripts/complete_delta.py`
  - **What**: After coverage check passes, call `check_audit_completeness`. If blocking findings exist and not `--force`, display error and return 1. If warnings, display them and continue.
  - **Pattern**: Mirror the coverage check integration (lines 490–505 of complete_delta.py).

- **2.6–2.8 Tests**
  - **2.6 VT-079-002**: Test `derive_closure_effect` exhaustively across conformance/discovery modes, all status×kind combinations, closure_override relaxation.
  - **2.7 VT-079-003**: Test `resolve_audit_gate` with auto+reqs, auto+no-reqs, required, exempt.
  - **2.8 VT-079-004**: Integration tests for `check_audit_completeness` and/or `complete_delta` with audit gating.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| complete_delta.py complexity | Separate module; only import+call in complete_delta | open |
| ChangeArtifact missing audit fields | Read raw frontmatter via load_markdown_file | open |
| Multi-audit union edge cases | Test with 0, 1, 2+ audits; test ID collisions | open |

## 9. Decisions & Outcomes
- Design decisions governing this phase: DEC-079-003, DEC-079-005, DEC-079-006, DEC-079-008, DEC-079-011

## 10. Findings / Research Notes
- `ChangeArtifact` exposes `path` reliably — confirmed in `artifacts.py:34`
- `ChangeRegistry(kind="audit").collect()` returns all AUD artefacts — confirmed in `registry.py:44–93`
- `complete_delta.py` coverage check pattern at lines 490–505 is the structural template for audit check integration
- Delta frontmatter `audit_gate` is not on `ChangeArtifact` dataclass — will need to read raw frontmatter from delta path too (same as audit)

## 11. Wrap-up Checklist
- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Notes updated
- [ ] Hand-off notes to phase 3 (validation rules)
