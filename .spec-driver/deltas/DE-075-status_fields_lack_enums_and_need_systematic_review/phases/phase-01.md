---
id: IP-075.PHASE-01
slug: 075-status_fields_lack_enums_and_need_systematic_review-phase-01
name: 'IP-075 Phase 01: define constants and register enums'
created: '2026-03-09'
updated: '2026-03-09'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-075.PHASE-01
plan: IP-075
delta: DE-075
objective: >-
  Define status frozensets for all governance artifact types (specs, ADRs,
  policies, standards, memories), unify backlog statuses, and register
  all new paths in ENUM_REGISTRY.
entrance_criteria:
  - DR-075 decisions accepted
exit_criteria:
  - lifecycle.py exists for specs, decisions, policies, standards, memory
  - backlog/models.py updated with unified BACKLOG_STATUSES
  - ENUM_REGISTRY has entries for spec, adr, policy, standard, memory status
  - All unit tests passing
  - Linters clean
verification:
  tests:
    - VT-075-01
    - VT-075-02
  evidence: []
tasks:
  - id: "1.1"
    description: Create specs/lifecycle.py with SPEC_STATUSES
  - id: "1.2"
    description: Create decisions/lifecycle.py with ADR_STATUSES
  - id: "1.3"
    description: Create policies/lifecycle.py with POLICY_STATUSES
  - id: "1.4"
    description: Create standards/lifecycle.py with STANDARD_STATUSES
  - id: "1.5"
    description: Create memory/lifecycle.py with MEMORY_STATUSES
  - id: "1.6"
    description: Unify backlog statuses in backlog/models.py
  - id: "1.7"
    description: Register all new paths in core/enums.py
  - id: "1.8"
    description: Update decisions/registry.py to reference ADR_STATUSES
  - id: "1.9"
    description: Write unit tests for all new constants and registry entries
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-075.PHASE-01
```

# Phase 1 — Define constants and register enums

## 1. Objective

Create lifecycle.py modules for five governance artifact types, unify backlog statuses, and register everything in ENUM_REGISTRY. Pure code + tests — no migration or theme changes yet.

## 2. Links & References

- **Delta**: DE-075
- **Design Revision**: DR-075 — DEC-075-01 through DEC-075-06
- **Existing patterns**: `changes/lifecycle.py`, `requirements/lifecycle.py`, `backlog/models.py`

## 3. Entrance Criteria

- [x] DR-075 decisions accepted

## 4. Exit Criteria / Done When

- [ ] `specs/lifecycle.py` — `SPEC_STATUSES`
- [ ] `decisions/lifecycle.py` — `ADR_STATUSES`
- [ ] `policies/lifecycle.py` — `POLICY_STATUSES`
- [ ] `standards/lifecycle.py` — `STANDARD_STATUSES`
- [ ] `memory/lifecycle.py` — `MEMORY_STATUSES`
- [ ] `backlog/models.py` — unified `BACKLOG_STATUSES`, `RISK_EXTRA_STATUSES`, `RISK_STATUSES`
- [ ] `core/enums.py` — 5 new registry entries + backlog entries updated
- [ ] `decisions/registry.py` — references `ADR_STATUSES` constant
- [ ] Unit tests for all of the above
- [ ] `just check` passes

## 5. Verification

- `just test` — all new test files pass
- `just lint` — zero warnings on touched files
- `just pylint-files <touched files>` — no regressions

## 6. Assumptions & STOP Conditions

- Assumes no other in-flight work modifies these files (check git status before starting)
- STOP if: on-disk scan reveals status values not covered by DR-075 survey

## 7. Tasks & Progress

| Status | ID  | Description                                              | Parallel? | Notes                             |
| ------ | --- | -------------------------------------------------------- | --------- | --------------------------------- |
| [ ]    | 1.1 | Create `specs/lifecycle.py` with `SPEC_STATUSES`         | [P]       | DEC-075-01                        |
| [ ]    | 1.2 | Create `decisions/lifecycle.py` with `ADR_STATUSES`      | [P]       | DEC-075-04                        |
| [ ]    | 1.3 | Create `policies/lifecycle.py` with `POLICY_STATUSES`    | [P]       | DEC-075-02                        |
| [ ]    | 1.4 | Create `standards/lifecycle.py` with `STANDARD_STATUSES` | [P]       | DEC-075-02                        |
| [ ]    | 1.5 | Create `memory/lifecycle.py` with `MEMORY_STATUSES`      | [P]       | DEC-075-03                        |
| [ ]    | 1.6 | Unify backlog statuses in `backlog/models.py`            | [ ]       | DEC-075-05; update dependent code |
| [ ]    | 1.7 | Register new paths in `core/enums.py`                    | [ ]       | Depends on 1.1–1.6                |
| [ ]    | 1.8 | Update `decisions/registry.py` to use `ADR_STATUSES`     | [ ]       | Depends on 1.2                    |
| [ ]    | 1.9 | Write unit tests                                         | [ ]       | Depends on 1.1–1.8                |
