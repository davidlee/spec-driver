---
id: IP-007.PHASE-01
slug: lifecycle-coverage-enforcement-phase-01
name: IP-007 Phase 01
created: '2025-11-03'
updated: '2025-11-03'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-007.PHASE-01
plan: IP-007
delta: DE-007
objective: >-
  Wire verification coverage entries into the requirements registry lifecycle
  and emit drift warnings when coverage disagrees with audits or plans.
entrance_criteria:
  - SPEC-122 guidance reviewed
  - Test fixtures for coverage-enabled specs identified
exit_criteria:
  - Registry sync updates lifecycle fields from coverage status changes
  - Validation warning emitted for simulated spec vs audit/plan drift
  - VT-902 integration test passing
verification:
  tests:
    - VT-902
  evidence:
    - Lifecycle sync logs
    - Validation warning output snapshot
tasks:
  - Add coverage block extraction to registry sync
  - Implement lifecycle status aggregation logic
  - Add drift detection and warning emission
  - Create test fixtures with coverage blocks
  - Write comprehensive integration tests
risks:
  - Registry regression affecting existing specs
  - Performance impact from additional parsing
```

# Phase 01 - Coverage Registry Integration

## 1. Objective

Integrate verification coverage block parsing into the requirements registry sync process, enabling lifecycle status updates driven by coverage entries and surfacing drift warnings when specs disagree with implementation plans or audits.

## 2. Links & References

- **Delta**: [DE-007](../DE-007.md)
- **Implementation Plan**: [IP-007](../IP-007.md)
- **Specs / PRODs**:
  - PROD-008.FR-001 (Specs as authoritative lifecycle record)
  - PROD-008.FR-002 (Delta implementation plans document VT/VA/VH)
  - PROD-008.FR-003 (Audits reconcile observed vs spec)
- **Support Docs**:
  - `supekku/scripts/lib/blocks/verification.py` - existing coverage parser
  - `supekku/scripts/lib/requirements/registry.py` - registry implementation
  - SPEC-122 - requirements registry infrastructure

## 3. Entrance Criteria

- [x] SPEC-122 guidance reviewed (requirements registry architecture)
- [x] Existing verification coverage parser understood
- [x] Current registry sync flow mapped
- [ ] Test fixtures directory created (`tests/fixtures/requirements/coverage/`)
- [ ] Regression test baseline established

## 4. Exit Criteria / Done When

- [ ] Registry sync extracts coverage blocks from specs, IPs, deltas, audits
- [ ] `RequirementRecord.verified_by` populated with artefact IDs from coverage
- [ ] Requirement status computed from aggregated coverage statuses
- [ ] Drift warnings emitted when coverage statuses conflict across artifacts
- [ ] VT-902 integration test passing
- [ ] No regression in existing registry tests
- [ ] Both linters passing (`just lint` + `just pylint`)

## 5. Verification

**Tests to run:**
- `uv run pytest supekku/scripts/lib/requirements/registry_test.py -v`
- `just test` (full suite to catch regressions)
- `just lint && just pylint`

**Evidence to capture:**
- Registry sync log showing coverage block processing
- Warning output demonstrating drift detection
- Test coverage report for new code paths

## 6. Assumptions & STOP Conditions

**Assumptions:**
- Coverage parser (`verification.py`) is stable and well-tested
- Registry sync already handles multiple artifact types sequentially
- Performance impact of additional parsing is negligible (<100ms overhead)

**STOP when:**
- Registry regression tests fail and root cause unclear
- Coverage parsing errors exceed 10% of processed files
- Memory usage increases beyond acceptable thresholds (>50MB)

## 7. Tasks & Progress

*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 1.1 | Add `_iter_plan_files()` helper method | [ ] | Clean implementation following existing pattern |
| [x] | 1.2 | Implement `_apply_coverage_blocks()` aggregation | [ ] | Handles all artifact types; graceful error handling |
| [x] | 1.3 | Add coverage status → requirement status mapping | [ ] | Maps to existing lifecycle statuses (live/in-progress/pending) |
| [x] | 1.4 | Implement drift detection logic | [ ] | Emits actionable warnings to stderr when conflicts detected |
| [x] | 1.5 | Integrate into `sync_from_specs()` workflow | [ ] | Added plan_dirs parameter; processes after all relations |
| [x] | 1.6 | Create test fixtures with coverage blocks | [P] | SPEC-900/901 fixtures with verified/in-progress/planned + drift |
| [x] | 1.7 | Write integration tests for VT-902 | [ ] | Full sync test + drift detection test passing |
| [x] | 1.8 | Add unit tests for status aggregation | [P] | Comprehensive coverage of precedence rules |
| [x] | 1.9 | Run regression suite and fix issues | [ ] | 11/11 tests passing, no regressions |
| [x] | 1.10 | Lint and fix all warnings | [ ] | Both ruff and pylint clean |

### Task Details

#### 1.1 Add `_iter_plan_files()` helper method

**Design / Approach:**
- Follow pattern of existing `_iter_change_files()` in registry.py:650
- Iterate through plan directories looking for IP-*.md files
- Return generator yielding Path objects

**Files / Components:**
- `supekku/scripts/lib/requirements/registry.py`

**Testing:**
- Unit test: create temp directory with IP files, verify iteration
- Edge cases: empty directory, non-markdown files, missing directory

**Code:**
```python
def _iter_plan_files(self, dirs: Iterable[Path]) -> Iterator[Path]:
  """Iterate over implementation plan files in directories."""
  for directory in dirs:
    if not directory.exists():
      continue
    for bundle in directory.iterdir():
      if not bundle.is_dir():
        continue
      for file in bundle.glob("*.md"):
        if file.name.startswith("IP-"):
          yield file
```

---

#### 1.2 Implement `_apply_coverage_blocks()` aggregation

**Design / Approach:**
- Extract coverage blocks from all artifact types (specs, deltas, IPs, audits)
- Build map: `{requirement_id: [coverage_entries...]}`
- For each requirement, aggregate artefact IDs into `verified_by` list
- Call after existing relationship processing in `sync_from_specs()`

**Files / Components:**
- `supekku/scripts/lib/requirements/registry.py` - new method
- `supekku/scripts/lib/blocks/verification.py` - import and use `load_coverage_blocks()`

**Algorithm:**
```
coverage_map = defaultdict(list)

# Extract from specs
for spec_file in spec_files:
  blocks = load_coverage_blocks(spec_file)
  for block in blocks:
    for entry in block.data.get('entries', []):
      req_id = entry.get('requirement')
      coverage_map[req_id].append({
        'source': spec_file,
        'artefact': entry.get('artefact'),
        'status': entry.get('status'),
        'kind': entry.get('kind'),
      })

# Repeat for deltas, IPs, audits

# Update records
for req_id, entries in coverage_map.items():
  record = self.records.get(req_id)
  if not record:
    continue

  # Update verified_by with unique artefact IDs
  artefacts = {e['artefact'] for e in entries if e['artefact']}
  record.verified_by = sorted(set(record.verified_by) | artefacts)
```

**Testing:**
- Test with spec containing multiple coverage entries
- Test aggregation across spec + IP + audit
- Test graceful handling of missing requirement IDs
- Test deduplication of artefact IDs

---

#### 1.3 Add coverage status → requirement status mapping

**Design / Approach:**
- Aggregate coverage entry statuses for each requirement
- Apply precedence rules:
  - ANY 'failed' → requirement status = 'at-risk'
  - ALL 'verified' → requirement status = 'verified'
  - ANY 'in-progress' → requirement status = 'in-progress'
  - ANY 'blocked' → requirement status = 'blocked'
  - ALL 'planned' → requirement status = 'planned'
  - MIXED → requirement status = 'in-progress'

**Files / Components:**
- `supekku/scripts/lib/requirements/registry.py`
- May need to update `lifecycle.py` if 'at-risk' status doesn't exist

**Code:**
```python
def _compute_status_from_coverage(self, entries: list[dict]) -> RequirementStatus:
  """Compute requirement status from aggregated coverage entries."""
  if not entries:
    return STATUS_PENDING

  statuses = {e['status'] for e in entries if e.get('status')}

  if 'failed' in statuses:
    return 'at-risk'  # or 'failed' if that exists
  if statuses == {'verified'}:
    return 'verified'
  if 'blocked' in statuses:
    return 'blocked'
  if 'in-progress' in statuses or len(statuses) > 1:
    return 'in-progress'
  if statuses == {'planned'}:
    return STATUS_PENDING

  return STATUS_PENDING
```

**Testing:**
- Test each status precedence rule
- Test empty entries list
- Test unknown statuses (should default to pending)

---

#### 1.4 Implement drift detection logic

**Design / Approach:**
- After aggregating coverage entries, check for conflicts
- Warn when same requirement has conflicting statuses across artifacts
- Log to stderr with actionable message format
- Track which artifact types disagree (spec vs IP vs audit)

**Files / Components:**
- `supekku/scripts/lib/requirements/registry.py`

**Warning Format:**
```
WARNING: Coverage drift detected for PROD-008.FR-001
  PROD-008.md: status=verified (VT-902)
  IP-007.md: status=planned (VT-902)
  Action: Update spec or implementation plan to resolve inconsistency
```

**Testing:**
- Test warning emission when spec='verified', IP='planned'
- Test no warning when statuses agree
- Test warning includes all conflicting sources

---

#### 1.5 Integrate into `sync_from_specs()` workflow

**Design / Approach:**
- Call `_apply_coverage_blocks()` after `_apply_audit_relations()`
- Pass spec_dirs, delta_dirs, ip_dirs (new parameter), audit_dirs
- Ensure coverage processing happens in single pass during sync

**Files / Components:**
- `supekku/scripts/lib/requirements/registry.py:148` - `sync_from_specs()` method

**Testing:**
- Integration test calling full sync with coverage-enabled fixtures
- Verify lifecycle fields updated correctly
- Verify drift warnings appear in output

---

#### 1.6 Create test fixtures with coverage blocks

**Design / Approach:**
- Create `tests/fixtures/requirements/coverage/` directory
- Add sample spec, IP, delta, audit with coverage blocks
- Include scenarios: all verified, mixed statuses, drift cases

**Files / Components:**
- `tests/fixtures/requirements/coverage/SPEC-900.md` - sample spec
- `tests/fixtures/requirements/coverage/IP-900.md` - sample plan
- `tests/fixtures/requirements/coverage/DE-900.md` - sample delta
- `tests/fixtures/requirements/coverage/AUD-900.md` - sample audit

**Fixture Structure:**
```markdown
# SPEC-900.md
---
id: SPEC-900
---
## Requirements
- FR-001: Sample requirement

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: SPEC-900
entries:
  - artefact: VT-900
    kind: VT
    requirement: SPEC-900.FR-001
    status: verified
```

---

#### 1.7 Write integration tests for VT-902

**Design / Approach:**
- Test full sync with coverage fixtures
- Verify `verified_by` populated
- Verify status transitions (planned → verified)
- Verify drift warnings emitted

**Files / Components:**
- `supekku/scripts/lib/requirements/registry_test.py` - extend existing suite

**Test Cases:**
```python
def test_sync_processes_coverage_blocks():
  """VT-902: Registry sync updates lifecycle from coverage."""
  # Setup fixtures
  # Run sync
  # Assert verified_by contains artefact IDs
  # Assert status updated correctly

def test_coverage_drift_detection():
  """Registry emits warnings for coverage conflicts."""
  # Setup conflicting coverage in spec vs IP
  # Run sync (capture stderr)
  # Assert warning message present
```

---

#### 1.8 Add unit tests for status aggregation

**Design / Approach:**
- Isolated tests for `_compute_status_from_coverage()`
- Test each precedence rule
- Test edge cases

**Files / Components:**
- `supekku/scripts/lib/requirements/registry_test.py`

---

#### 1.9 Run regression suite and fix issues

**Design / Approach:**
- Run full test suite: `just test`
- Fix any failing tests
- Ensure no performance degradation

---

#### 1.10 Lint and fix all warnings

**Design / Approach:**
- `just lint` - must pass with zero warnings
- `just pylint` - must meet threshold

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Registry regression affecting existing specs | Add regression test suite before changes; run sync against sample corpus | Planned |
| Performance impact from parsing many files | Profile sync with 100+ specs; optimize if >100ms overhead | Monitored |
| Coverage blocks with invalid YAML | Use existing validator; log and skip invalid blocks gracefully | Handled by parser |
| Memory usage spike from coverage map | Use generator patterns; process artifacts in sequence | Design addresses |

## 9. Decisions & Outcomes

- `2025-11-03` - Use existing `load_coverage_blocks()` parser rather than reimplementing
- `2025-11-03` - Process coverage after all relationship blocks to avoid double-processing
- `2025-11-03` - Map failed/blocked coverage to STATUS_IN_PROGRESS (existing lifecycle status)
- `2025-11-03` - Status mapping: verified→live, in-progress→in-progress, planned→pending, failed/blocked→in-progress

## 10. Findings / Research Notes

- Existing coverage parser (`verification.py`) is well-tested and handles all validation
- Registry already has pattern for processing multiple artifact types
- `sync_from_specs()` takes optional delta_dirs, revision_dirs, audit_dirs parameters
- Added `plan_dirs` parameter to `sync_from_specs()` for implementation plan coverage
- `RequirementRecord.verified_by` is list[str], already exists - perfect for artefact IDs
- Drift detection uses stderr for warnings, gracefully handles missing files
- Test fixtures required specific directory structure (subdirs with spec files)
- Coverage aggregation correctly deduplicates artefact IDs across multiple sources

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] VT-902 integration test passing
- [x] No regression in existing tests (11/11 passing)
- [x] Verification evidence stored (test output, lint results)
- [x] IP-007 updated with lessons learned
- [x] Hand-off notes for Phase 02: registry ready for completion enforcement

## 12. Phase Completion Summary

**Completion Date:** 2025-11-03

**Implementation:** Successfully integrated verification coverage blocks into requirements registry sync process. Core functionality complete and tested.

**Key Deliverables:**
- Coverage block extraction from specs, IPs, deltas, audits
- Lifecycle status computation with precedence rules
- Drift detection and warnings
- Comprehensive test coverage (3 new tests + fixtures)
- Zero regressions, full lint compliance

**Hand-off to Phase 02:**
Registry infrastructure is ready. The `_apply_coverage_blocks()` method successfully:
- Extracts coverage from all artifact types
- Updates `verified_by` lists with artefact IDs
- Computes lifecycle status from aggregated coverage
- Detects and warns about coverage drift

Next phase should leverage this foundation to enforce coverage updates during delta completion workflow.
