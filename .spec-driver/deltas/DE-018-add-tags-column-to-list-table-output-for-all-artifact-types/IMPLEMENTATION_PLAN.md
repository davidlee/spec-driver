# DE-018 Implementation Plan

## Executive Summary

Add Tags column to table output for all artifact list commands, following the pattern established in DE-010 for policies and standards.

**Status**: Ready for implementation
**Delta**: DE-018
**Specs**: SPEC-110 (CLI), SPEC-120 (Formatters)
**Pattern Source**: policy_formatters.py, standard_formatters.py (DE-010)

## Pattern Analysis from DE-010

From `policy_formatters.py`, the pattern involves:

1. **Column definition** in `_format_as_table()`:
   ```python
   columns=["ID", "Title", "Tags", "Status", "Updated"]
   ```

2. **Row preparation** in `_prepare_policy_row()`:
   ```python
   tags = ", ".join(policy.tags) if policy.tags else ""
   tags_styled = f"[#d79921]{tags}[/#d79921]" if tags else ""
   return [policy_id, title, tags_styled, status_styled, updated_date]
   ```

3. **Column width calculation** in `_calculate_column_widths()`:
   ```python
   tags_width = 20
   # Adjust other column calculations to account for tags
   ```

## Current State Analysis

### decision_formatters.py
- **Current columns**: `["ID", "Title", "Status", "Updated"]`
- **Current row**: `[decision_id, title, status_styled, updated_date]`
- **Needs**: Add Tags column after Status, before Updated

### spec_formatters.py
- **Note**: Uses different implementation (no `_format_as_table` function)
- **Current**: `format_spec_list_table()` uses simple list formatting
- **Needs**: Add Tags column to table rendering

### change_formatters.py
- **Note**: Uses different implementation (no `_format_as_table` function)
- **Current**: `format_change_list_table()` handles deltas, revisions, audits
- **Needs**: Add Tags column

### requirement_formatters.py
- **Needs investigation**: Check current implementation pattern

### backlog_formatters.py
- **Needs investigation**: Check current implementation pattern

## Implementation Tasks

### Phase 1: Research & Pattern Verification
1. ✅ Read policy_formatters.py to understand DE-010 pattern
2. ✅ Identify all formatters needing updates
3. ⬜ Read each formatter file to understand current structure
4. ⬜ Identify any formatters with non-standard patterns
5. ⬜ Document approach for each formatter

### Phase 2: Update Formatters (Following Pattern)

For each formatter, apply the pattern:

#### 2.1 decision_formatters.py
- Update `_format_as_table()`: Add "Tags" to columns list
- Update `_prepare_decision_row()`: Add tags formatting and return tags_styled
- Update `_calculate_column_widths()`: Add tags_width calculation
- Update docstrings to reflect new column

#### 2.2 spec_formatters.py
- Investigate current implementation
- Add Tags column following established pattern
- Maintain consistency with other formatters

#### 2.3 change_formatters.py
- Investigate current implementation
- Add Tags column following established pattern
- Handle deltas, revisions, audits uniformly

#### 2.4 requirement_formatters.py
- Investigate current implementation
- Add Tags column following established pattern

#### 2.5 backlog_formatters.py
- Investigate current implementation
- Add Tags column following established pattern

### Phase 3: Comprehensive Testing

For each formatter (*_formatters_test.py):

#### 3.1 Test cases needed:
- Empty tags (no tags on artifact)
- Single tag
- Multiple tags (2-3 tags)
- Long tag list (>5 tags, may need truncation)
- Tags with special characters
- Integration with table rendering

#### 3.2 Test files to update:
- decision_formatters_test.py
- spec_formatters_test.py
- change_formatters_test.py
- requirement_formatters_test.py
- backlog_formatters_test.py

### Phase 4: Quality Assurance

1. Run linters:
   - `just lint` (ruff - must pass with 0 warnings)
   - `just pylint` (must meet ratchet threshold)

2. Run tests:
   - `just test` (all tests must pass)

3. Visual consistency check:
   - `uv run spec-driver list adrs`
   - `uv run spec-driver list specs`
   - `uv run spec-driver list deltas`
   - `uv run spec-driver list requirements`
   - Verify consistent column ordering and formatting

### Phase 5: Documentation & Completion

1. Update IP-018.md with actual implementation details
2. Create phase-01.md with task execution notes
3. Update notes.md with any discoveries or decisions
4. Verify all acceptance criteria from DE-018.md

## Design Decisions

### Tags Column Placement
- **Decision**: Placement varies by formatter based on artifact priorities
- **Rationale**: Different artifacts have different column priorities
- **Examples**:
  - Decisions: ID, Title, Tags, Status, Updated
  - Changes: ID, Kind, Status, Tags, Name, Updated
  - Requirements: ID, Type, Status, Tags, Name

### Tags Column Width
- **Decision**: 20 characters (following DE-010)
- **Rationale**: Balances discoverability with space for other columns
- **Truncation**: If needed, handled by table rendering utilities

### Tags Styling
- **Decision**: Use `[#d79921]` color for tags (following DE-010)
- **Rationale**: Consistent visual treatment across artifact types
- **Empty tags**: Show empty string, not "—" or "N/A"

## Risks & Mitigations

1. **Non-standard formatter implementations**
   - Risk: Some formatters may not follow the standard pattern
   - Mitigation: Research each formatter, adapt pattern as needed
   - Status: Will be discovered in Phase 1

2. **Column width conflicts**
   - Risk: Adding Tags may crowd other columns on narrow terminals
   - Mitigation: Follow DE-010 width calculations, test on standard terminal sizes
   - Status: Low risk - DE-010 proved the pattern works

3. **Missing tags attribute**
   - Risk: Some artifact models may not have tags attribute
   - Mitigation: Check model definitions, default to empty list if missing
   - Status: Will be discovered during implementation

## Success Criteria

- [ ] All 5 formatters display Tags column
- [ ] Tags shown as comma-separated list or empty string
- [ ] Column widths adjust properly
- [ ] All tests pass (`just test`)
- [ ] Both linters pass (`just lint` + `just pylint`)
- [ ] Visual consistency verified across artifact types
- [ ] No regressions in existing functionality

## Next Steps

1. Mark first todo as complete
2. Begin Phase 1: Research remaining formatters
3. Document findings in notes.md
4. Proceed to Phase 2 implementation
