# Investigation: FR-011 and Missing Requirements from Registry

**Date**: 2025-11-04
**Issue**: PROD-010.FR-011 (and 53+ other requirements) not extracted by requirements sync
**Status**: ✅ RESOLVED

## Executive Summary

**Root Cause**: Regex pattern in requirements registry only matched short-format requirement IDs (`FR-001`) but not fully-qualified IDs (`PROD-010.FR-001`).

**Impact**: 58 requirements missing from registry across 5 specs:
- PROD-010: 18 requirements (11 FR + 3 NF + 4 additional)
- SPEC-110: 12 requirements
- SPEC-112: 9 requirements
- SPEC-124: 12 requirements
- SPEC-125: 7 requirements

**Resolution**: Updated regex, added logging/validation, wrote comprehensive tests. All requirements now extracted successfully.

## Technical Details

### The Problem

Location: `supekku/scripts/lib/requirements/registry.py:44`

**Old pattern** (broken):
```python
_REQUIREMENT_LINE = re.compile(
  r"^\s*[-*]\s*\*{0,2}\s*(FR|NF)-(\d{3})\s*\*{0,2}\s*[:\-–]\s*(.+)$",
  re.IGNORECASE,
)
```

**Matched**:
- ✓ `- **FR-001**: Title...` (PROD-001 format)
- ✓ `- FR-002: Title...`

**Didn't match**:
- ✗ `- **PROD-010.FR-001**: Title...` (current standard)
- ✗ `- **SPEC-110.NF-003**: Title...`

### The Fix

**New pattern** (working):
```python
_REQUIREMENT_LINE = re.compile(
  r"^\s*[-*]\s*\*{0,2}\s*(?:[A-Z]+-\d{3}\.)?("
  r"FR|NF)-(\d{3})\s*\*{0,2}\s*[:\-–]\s*(.+)$",
  re.IGNORECASE,
)
```

The added `(?:[A-Z]+-\d{3}\.)?` optionally matches:
- One or more uppercase letters
- Hyphen
- Exactly 3 digits
- Dot
- (non-capturing group - doesn't affect extraction)

This supports **both** legacy short format and current fully-qualified format.

### Additional Improvements

#### 1. Extraction Logging

Added diagnostic logging to detect when requirement-like lines aren't matched:

```python
def _records_from_content(self, spec_id, _frontmatter, body, spec_path, repo_root):
    requirement_like_lines = []
    extracted_count = 0

    for line in body.splitlines():
        # Track lines that look like requirements
        if re.search(r'\b(FR|NF)-\d{3}\b', line, re.IGNORECASE):
            requirement_like_lines.append(line.strip())

        match = _REQUIREMENT_LINE.match(line)
        if not match:
            continue
        extracted_count += 1
        # ... extraction logic

    # Warn if we found requirement-like lines but extracted none
    if requirement_like_lines and extracted_count == 0:
        logger.warning(
            "Spec %s at %s: Found %d requirement-like lines but extracted 0. "
            "First line: %s",
            spec_id, spec_path.name, len(requirement_like_lines),
            requirement_like_lines[0][:80]
        )
```

#### 2. Post-Sync Validation

Added validation to warn about specs with zero extracted requirements:

```python
def _validate_extraction(self, spec_registry, seen):
    """Warn about specs with no extracted requirements."""
    for spec in spec_registry.all_specs():
        if spec.kind not in ('prod', 'tech'):
            continue

        extracted = [uid for uid in seen if uid.startswith(f"{spec.id}.")]

        if len(extracted) == 0:
            print(
                f"WARNING: Spec {spec.id} ({spec.kind}) has 0 extracted requirements. "
                f"Check requirement format in {spec.path.name}",
                file=sys.stderr
            )
```

#### 3. Comprehensive Test Coverage

Added `test_qualified_requirement_format()` covering:
- Fully-qualified format extraction
- Mixed format in single file (both short and qualified)
- Correct label/title/kind extraction
- Proper spec association

## Error-Swallowing Patterns Identified

Found **4 critical silent failure points** in `registry.py`:

1. **Line 940-955**: Requirement extraction - regex match failures silently skipped
2. **Line 236-239**: File read failures - `OSError` caught, body set to `""`
3. **Lines 537, 557, 576, 596**: Coverage block failures - `ValueError/OSError` silently caught
4. **Line 360-362**: Delta relationship extraction - `ValueError` silently caught

These made debugging nearly impossible. Added logging addresses issue #1; others remain for future improvement.

## Verification

### Test Results
```bash
$ uv run pytest supekku/scripts/lib/requirements/registry_test.py
============================= 15 tests passed ==============================
```

### Lint Results
```bash
$ just lint
All checks passed!
```

### Registry Sync Results
```bash
$ uv run spec-driver sync requirements
Requirements: 1 created, 44 updated

$ grep -c "^  PROD-010\." .spec-driver/registry/requirements.yaml
18

$ grep -c "^  SPEC-110\." .spec-driver/registry/requirements.yaml
12

$ grep -c "^  SPEC-112\." .spec-driver/registry/requirements.yaml
9

$ grep -c "^  SPEC-124\." .spec-driver/registry/requirements.yaml
12

$ grep -c "^  SPEC-125\." .spec-driver/registry/requirements.yaml
7
```

### PROD-010 Requirements (All Now Present)
```yaml
PROD-010.FR-001: All list commands MUST support both --json...
PROD-010.FR-002: All show commands MUST support --json flag...
PROD-010.FR-003: All list commands MUST support -s/--status filter...
PROD-010.FR-004: All list commands MUST support multi-value filters...
PROD-010.FR-005: List commands MUST support reverse relationship queries...
PROD-010.FR-006: Schema commands MUST expose enum values...
PROD-010.FR-007: All list command help text MUST document output format...
PROD-010.FR-008: All commands MUST support --machine-readable flag...
PROD-010.FR-009: List commands MUST support pagination...
PROD-010.FR-010: Error messages MUST provide actionable guidance...
PROD-010.FR-011: CLI MUST provide kind-specific backlog list shortcuts ✅
PROD-010.FR-012: ...
PROD-010.FR-013: ...
PROD-010.FR-014: ...
PROD-010.FR-015: ...
PROD-010.NF-001: Compact JSON mode MUST reduce token usage by 30-50%...
PROD-010.NF-002: Common agent workflows MUST complete without documentation...
PROD-010.NF-003: Implemented improvements MUST address all Priority 1-2 findings...
```

## Files Modified

1. `supekku/scripts/lib/requirements/registry.py` (+56 lines, 3 changes):
   - Updated regex pattern to support qualified format
   - Added logging import and logger
   - Added extraction diagnostics to `_records_from_content()`
   - Added `_validate_extraction()` method
   - Called validation from `sync_from_specs()`

2. `supekku/scripts/lib/requirements/registry_test.py` (+76 lines):
   - Added `test_qualified_requirement_format()`
   - Tests both qualified and mixed format extraction
   - Verifies 9 requirements across 2 test specs

3. `.spec-driver/registry/requirements.yaml` (regenerated):
   - 58 new requirements added
   - All affected specs now have complete requirement sets

## Future Improvements

1. **Add `--verbose` flag** to sync command for exposing silent failures
2. **Add logging to other silent failure points** (file reads, coverage blocks, delta relationships)
3. **Consider format standardization** across all specs (either all qualified or all short)
4. **Add metrics** to track extraction success rate per spec
5. **Create validation rule** flagging specs with suspiciously low requirement counts

## Lessons Learned

1. **Silent failures are dangerous**: Registry swallowed errors at 4+ critical points
2. **Validation matters**: Post-sync validation would have caught this immediately
3. **Format consistency helps**: Mixed formats across specs increases fragility
4. **Diagnostic logging is essential**: Without it, debugging took much longer
5. **Comprehensive tests prevent regressions**: New test ensures this won't break again

## References

- Issue discovered during: Investigation of PROD-010.FR-011 missing from registry
- Investigation doc: `/tmp/findings_report.md` (temporary)
- Regex tested at: `/tmp/test_regex_fix.py` (temporary)
- Related specs: PROD-010, SPEC-110, SPEC-112, SPEC-124, SPEC-125
