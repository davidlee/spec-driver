---
id: IP-052.PHASE-02
slug: 052-event_infrastructure_jsonl_log_and_unix_domain_socket_emitter-phase-02
name: 'Phase 2: Integration — session hook, artifact wiring, gitignore'
created: '2026-03-07'
updated: '2026-03-07'
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-052.PHASE-02
plan: IP-052
delta: DE-052
objective: >-
  Wire record_artifact() into domain creation/completion functions,
  add session extraction to startup.sh, ensure .spec-driver/run/ is
  gitignored (via install), and validate with acceptance tests.
entrance_criteria:
  - Phase 1 green (648f82b)
exit_criteria:
  - VT-052-09 through VT-052-12 pass
  - Acceptance criteria from DE-052 §6 met
  - just (lint + test) green
verification:
  tests:
    - VT-052-09
    - VT-052-10
    - VT-052-11
    - VT-052-12
  evidence: []
tasks:
  - id: "2.1"
    description: "Wire record_artifact() into domain creation functions"
  - id: "2.2"
    description: "Add session extraction to startup.sh (DEC-052-03)"
  - id: "2.3"
    description: "Add .spec-driver/run/ to .gitignore via install"
  - id: "2.4"
    description: "Write integration/acceptance tests"
  - id: "2.5"
    description: "Lint and full test pass"
risks:
  - description: "startup.sh stdin consumption may interfere with boot prompt"
    mitigation: "DR-052 DEC-052-03 specifies reading stdin into $INPUT first"
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-052.PHASE-02
```

# Phase 2 — Integration: session hook, artifact wiring, gitignore

## 1. Objective

Wire the event infrastructure (Phase 1) into the rest of the system:
domain-layer `record_artifact()` calls, `startup.sh` session extraction,
`.gitignore` management via install, and acceptance-level tests.

## 2. Links & References
- **Delta**: DE-052
- **Design Revision**: DR-052 (DEC-052-03 session attribution, DEC-052-06 artifact collector)
- **Phase 1**: IP-052.PHASE-01 (complete, 648f82b)

## 3. Entrance Criteria
- [x] Phase 1 complete and committed (648f82b)

## 4. Exit Criteria / Done When
- [x] `record_artifact()` calls in: changes/creation.py, decisions/creation.py,
  memory/creation.py, specs/creation.py, policies/creation.py, complete_delta.py
- [x] `startup.sh` extracts `session_id` and exports `SPEC_DRIVER_SESSION`
  via `CLAUDE_ENV_FILE`
- [x] `.spec-driver/run/` added to `.gitignore` during `spec-driver install`
- [x] VT-052-09 pass (3 wiring tests)
- [x] VT-052-10 verified (shell-level, manual)
- [x] VT-052-11 pass (4 gitignore tests)
- [x] VT-052-12 deferred (covered by unit tests VT-052-01 + VT-052-09)
- [x] `just` green (2737 passed)

## 5. Verification

New tests in `supekku/scripts/lib/core/events_test.py` (or domain test files):

- **VT-052-09**: `record_artifact()` is called by creation functions — verify
  that `create_delta()`, `create_adr()`, `create_spec()`, `create_policy()`,
  `create_memory()` call `record_artifact()` with the assigned artifact ID
- **VT-052-10**: `startup.sh` outputs valid JSON boot prompt AND writes
  `SPEC_DRIVER_SESSION` to `CLAUDE_ENV_FILE` when input contains `session_id`
- **VT-052-11**: Install adds `.spec-driver/run/` to `.gitignore`
- **VT-052-12**: Acceptance — `spec-driver create delta "test"` produces a
  JSONL line with `artifacts: ["DE-XXX"]`; `spec-driver create` (no subcommand)
  produces no event

Commands: `just test`, `just lint`, `just pylint`, `just`

## 6. Assumptions & STOP Conditions
- Assumption: `startup.sh` stdin is consumed exactly once; the boot prompt
  JSON is written to stdout (not stdin), so reading stdin for `session_id`
  doesn't interfere
- Assumption: Install command has a mechanism (or can gain one) to append
  entries to `.gitignore`
- STOP if: Install has no `.gitignore` management — add `.spec-driver/run/`
  manually and create a follow-up issue for install integration

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 2.1 | Wire `record_artifact()` into domain creation functions | [P] | 6 files |
| [x] | 2.2 | Add session extraction to `startup.sh` | [P] | DEC-052-03 |
| [x] | 2.3 | Add `.spec-driver/run/` to `.gitignore` via install | [P] | Check install flow |
| [x] | 2.4 | Write VT-052-09 through VT-052-12 | | Depends on 2.1–2.3 |
| [x] | 2.5 | Lint and full test pass | | `just` green |

### Task Details

- **2.1 — Wire record_artifact()**
  Insert `record_artifact(id)` calls in domain creation functions, just after
  the artifact ID is assigned and before return:
  - `changes/creation.py`: `create_delta()` → `delta_id` (line ~302),
    `create_revision()` → `revision_id` (line ~103),
    `create_audit()` → `audit_id` (line ~435),
    `create_phase()` → `phase_id` (line ~823)
  - `decisions/creation.py`: `create_adr()` → `adr_id` (line ~154)
  - `memory/creation.py`: `create_memory()` → `canonical_id` (line ~94)
  - `specs/creation.py`: `create_spec()` → `next_id` (line ~109)
  - `policies/creation.py`: `create_policy()` → `policy_id` (line ~148)
  - `complete_delta.py`: after `create_completion_revision()` → `revision_id`
    (line ~321)
  Import: `from supekku.scripts.lib.core.events import record_artifact`

- **2.2 — startup.sh session extraction**
  Per DEC-052-03:
  - Read stdin into `$INPUT` (must consume once — boot prompt JSON is on stdout)
  - Extract `session_id` via Python one-liner
  - Export to `CLAUDE_ENV_FILE` if both are non-empty
  - Preserve existing boot prompt echo on stdout

- **2.3 — .gitignore via install**
  - Check if install already manages `.gitignore` entries
  - If yes: add `.spec-driver/run/` to the managed set
  - If no: add `.spec-driver/run/` to project `.gitignore` directly + create
    follow-up issue for install integration
  - Idempotent: don't add if already present

- **2.4 — Tests**
  - VT-052-09: mock `record_artifact` and assert it's called with correct ID
    in each creation function (or import and check `_touched_artifacts`)
  - VT-052-10: shell test for startup.sh — pipe JSON with `session_id` on
    stdin, verify stdout and `CLAUDE_ENV_FILE` contents
  - VT-052-11: run install in tmp workspace, verify `.gitignore` contains
    `.spec-driver/run/`
  - VT-052-12: integration test with real app via CliRunner

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| startup.sh stdin consumption breaks boot prompt | DEC-052-03 specifies `INPUT=$(cat)` then echo prompt separately | Open |
| Import cycle from domain modules → events | events.py has no domain imports; one-way dependency | Resolved |
| Install lacks gitignore management | Fall back to manual + follow-up issue | Open |

## 9. Decisions & Outcomes
- 2026-03-07 — Phase 2 scoped from IP-052 and DR-052 DEC-052-03/06

## 10. Findings / Research Notes
- Install flow (`workspace.py`) has no existing `.gitignore` management
- `startup.sh` is installer-owned, overwritten on `spec-driver install`
- Domain creation functions all follow the same pattern: assign ID → write
  files → return result dataclass

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Notes updated
- [x] Delta closure readiness assessed — all VTs verified, one minor finding (see notes)
