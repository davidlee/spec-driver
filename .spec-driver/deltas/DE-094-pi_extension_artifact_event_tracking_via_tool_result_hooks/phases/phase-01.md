---
id: IP-094.PHASE-01
slug: 094-pi_extension_artifact_event_tracking_via_tool_result_hooks-phase-01
name: "IP-094 Phase 01: implement extension and tests"
created: "2026-03-14"
updated: "2026-03-14"
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-094.PHASE-01
plan: IP-094
delta: DE-094
objective: >-
  Implement spec-driver-artifact-events.ts pi extension and accompanying tests.
entrance_criteria:
  - DR-094 accepted
  - pi extension install pipeline working (DE-093)
exit_criteria:
  - Extension classifies all artifact patterns correctly
  - Events emitted to JSONL and Unix socket
  - Tests pass, lint clean
verification:
  tests:
    - Classification unit tests (port from artifact_event_test.py)
    - Event schema tests
    - JSONL append tests
  evidence: []
tasks:
  - id: T1
    description: Write spec-driver-artifact-events.ts
  - id: T2
    description: Write tests
  - id: T3
    description: Lint and verify
risks: []
```

# Phase 01 — Implement extension and tests

## 1. Objective

Write `spec-driver-artifact-events.ts` and tests. Single deliverable: a pi
extension that observes `tool_result` events and emits v1 artifact events.

## 2. Links & References

- **Delta**: DE-094
- **Design Revision**: DR-094 (DEC-094-01, DEC-094-02, DEC-094-03)
- **Prior art**: `supekku/claude.hooks/artifact_event.py` + `artifact_event_test.py`
- **Memory**: `mem.artifact-pattern-sync`

## 3. Entrance Criteria

- [x] DR-094 complete
- [x] Install pipeline working (DE-093)

## 4. Exit Criteria

- [x] Extension installed to `.pi/extensions/` via `spec-driver install`
- [x] Classification matches all patterns from `artifact_event.py`
- [x] JSONL events written to `.spec-driver/run/events.jsonl`
- [x] Socket dropped — Node.js dgram lacks AF_UNIX; TUI log-tail fallback is automatic
- [x] Tests pass (29 TS + 103 Python install + 35 Python artifact_event)
- [x] Lint clean

## 5. Tasks

| Status | ID  | Description                                                  |
| ------ | --- | ------------------------------------------------------------ |
| [x]    | T1  | Write `supekku/pi.extensions/spec-driver-artifact-events.ts` |
| [x]    | T2  | Write tests for classification, event schema, JSONL write    |
| [x]    | T3  | Lint, format, verify full test suite                         |

### T1 — Extension implementation

**Files**: `supekku/pi.extensions/spec-driver-artifact-events.ts`

Structure:

- `ARTIFACT_PATTERNS` — regex array mirroring `_ARTIFACT_PATTERNS` from Python
  (with `// SYNC:` comment referencing `artifact_event.py`)
- `classifyPath(path: string)` — returns `[type, id | null]` or `null`
- `buildEvent(...)` — constructs v1 event dict
- `writeLog(event, runDir)` — `fs.appendFileSync` JSONL
- `sendSocket(event, runDir)` — `dgram` Unix datagram, fail-silent
- `tool_result` handler — wires it together for read/edit/write tools

Tool name → action mapping: `read → "read"`, `edit → "edit"`, `write → "write"`

Path relativization: `path.relative(ctx.cwd, event.input.path)`

### T2 — Tests

Test framework: need to determine what's available for TS in this project.
Options: vitest, jest, or inline assertion script run via `pi.exec`.
Fallback: if no TS test runner, test the logic by extracting pure functions
and testing via a small runner script.

Port from `artifact_event_test.py`:

- `TestClassifyPath` parametric cases (all artifact types)
- `TestNonArtifactPaths` (returns null)
- `TestBuildEvent` schema assertions

### T3 — Lint and verify

- Run project lint (`just check` or equivalent)
- Verify `spec-driver install` picks up the new file
- Run full test suite to confirm no regressions

## 6. Assumptions & STOP Conditions

- **Assumption**: Node.js `dgram` supports Unix datagram sockets
- **STOP**: If pi's `tool_result` event doesn't expose `input.path` for
  read/edit/write tools at runtime — verify against actual event shape
