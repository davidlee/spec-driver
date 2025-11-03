# Phase 05 Enhancement - File Path Tracking

## Added: 2025-11-03

### What Was Enhanced

Added file path tracking to `phase.tracking@v1` schema for better traceability and context.

### New Schema Fields

#### Phase-Level Files

```yaml
files:
  references:  # Research/reference materials consulted
    - "path/to/spec.md"
    - "path/to/exemplar_code.py"
  context:     # Related phases, similar implementations (supports globs)
    - "path/to/similar/phase.md"
    - "change/deltas/DE-*/phases/phase-*.md"  # Glob patterns work
```

**Use cases**:
- **references**: Document which specs/docs/code were referenced during phase
- **context**: Point to similar phases, related implementations for context
- Audit trail: "What did we read to understand this?"
- Supports glob patterns for finding related work

#### Task-Level Files

```yaml
tasks:
  - id: "5.1"
    description: "..."
    status: completed
    files:
      added:     # New files created
        - "path/to/new_file.py"
      modified:  # Existing files changed
        - "path/to/updated_file.py"
      removed:   # Files deleted
        - "path/to/old_file.py"
      tests:     # Test files (added or run)
        - "path/to/test_file.py"
```

**Use cases**:
- Track which files were touched per task
- Link tasks to specific code changes
- Identify test coverage per task
- Enable git commit correlation
- Simplify code review ("What changed in task 5.1?")
- Change impact analysis ("Which tasks touched this file?")

### Files Modified

1. **supekku/scripts/lib/blocks/plan.py**
   - Added validation for `files.references` and `files.examples` (phase-level)
   - Added validation for `task.files.{added,modified,removed,tests}` (task-level)
   - All file path fields are optional arrays of strings

2. **supekku/scripts/lib/blocks/tracking_test.py**
   - Added 4 new tests for file path validation
   - Tests cover: valid phase files, valid task files, invalid structures
   - Total: 19 tests passing

3. **supekku/templates/phase.md**
   - Updated template with file path examples
   - Clear inline documentation
   - Shows both phase-level and task-level file tracking

4. **change/deltas/DE-004-phase-management-implementation/phases/phase-05.md**
   - Added actual file paths from Phase 05 implementation
   - Demonstrates real-world usage

### Example from Phase 05

```yaml
files:
  references:
    - "supekku/scripts/lib/blocks/plan.py"  # Existing pattern to follow
    - "supekku/scripts/lib/blocks/verification_test.py"  # Test example
    - "specify/product/PROD-006/PROD-006.md"  # Spec
  context:
    - "change/deltas/DE-004-*/phases/phase-01.md"  # Similar phase
    - "change/deltas/DE-004-*/phases/phase-04.md"  # Another similar phase

tasks:
  - id: "5.1"
    description: "Define phase.tracking@v1 schema"
    status: completed
    files:
      modified:
        - "supekku/scripts/lib/blocks/plan.py"

  - id: "5.5"
    description: "Write VT-PHASE-007 tests"
    status: completed
    files:
      added:
        - "supekku/scripts/lib/blocks/tracking_test.py"
      tests:
        - "supekku/scripts/lib/blocks/tracking_test.py"
```

### Benefits

1. **Traceability**: Clear link between tasks and code changes
2. **Context**: Know what was consulted/referenced
3. **Auditability**: Track what files were affected
4. **Handoff**: Better documentation for future developers
5. **Git integration**: Could auto-correlate commits to tasks
6. **Change impact**: Query which tasks touched a file
7. **Test coverage**: Explicit test file tracking per task

### Testing

- ✅ 19 tests passing (4 new file-tracking tests)
- ✅ Ruff: clean
- ✅ Pylint: 9.48/10
- ✅ Backward compat: File fields are optional
- ✅ Phase-05 displays correctly with file data

### Future Possibilities

1. **Git integration**: `spec-driver task-files 5.1` → show actual git diff
2. **Change reports**: "Which files were most frequently modified?"
3. **Test gap analysis**: "Which tasks have no test files?"
4. **Impact analysis**: "Find all tasks that touched auth.py"
5. **Auto-population**: Parse git commits to populate file lists
6. **Dependency mapping**: Build file→task→requirement graph

## Summary

File path tracking makes the phase.tracking@v1 schema **even more delicious** by adding:
- Phase-level context (what we referenced)
- Task-level granularity (what we changed)
- Optional fields (no breaking changes)
- Comprehensive validation (catches errors early)

Phase 05 now serves as a living example with real file paths from its own implementation.
