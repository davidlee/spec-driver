# Notes for DE-018

## Investigation Summary

Completed investigation of all formatters to understand their current implementation patterns.

### Formatter Implementation Patterns

#### Pattern A: Dedicated Helper Functions (policy, standard, decision)
- Uses `_format_as_table()`, `_prepare_*_row()`, `_calculate_column_widths()`
- Example: `policy_formatters.py` (DE-010 reference implementation)
- **decision_formatters.py** follows this pattern

#### Pattern B: Inline Implementation (spec, change, requirement, backlog)
- Table creation and row preparation done inline in `format_*_list_table()`
- No separate helper functions
- Examples: spec_formatters.py, change_formatters.py, requirement_formatters.py, backlog_formatters.py

### Current Column Structures

1. **decision_formatters.py** (Pattern A):
   - Current: `["ID", "Title", "Status", "Updated"]`
   - Row: `[decision_id, title, status_styled, updated_date]`
   - **Needs**: Add Tags after Status

2. **spec_formatters.py** (Pattern B):
   - Current: `["ID", "Name", "Status"]` (+ optional "Packages")
   - Row: `[styled_id, spec.name, styled_status]` (+ optional packages)
   - **Needs**: Add Tags after Status

3. **change_formatters.py** (Pattern B):
   - Current: `["ID", "Status", "Name"]`
   - Row: `[styled_id, styled_status, change.name]`
   - **Needs**: Add Tags after Status (or after ID?)

4. **requirement_formatters.py** (Pattern B):
   - Current: `["Spec", "Label", "Category", "Title", "Status"]`
   - Row: `[spec_styled, label_styled, category_styled, req.title, status_styled]`
   - **Needs**: Add Tags (placement TBD - after Category?)

5. **backlog_formatters.py** (Pattern B):
   - Current: `["ID", "Kind", "Status", "Title", "Severity"]`
   - Row: `[item_id, item.kind, status_styled, item.title, severity]`
   - **Needs**: Add Tags after Status

### Tags Column Placement Strategy

Conventional order: Title/Name, Tags, Status (following decision_formatters pattern)

1. **decision_formatters**: `ID, Title, Tags, Status, Updated` (reference pattern)
2. **spec_formatters**: `ID, Name, Tags, Status` (+ optional Packages)
3. **change_formatters**: `ID, Name, Tags, Status` (changed from ID, Status, Name)
4. **requirement_formatters**: `Spec, Label, Category, Title, Tags, Status`
5. **backlog_formatters**: `ID, Kind, Title, Tags, Status, Severity`

### Implementation Approach

For each formatter:
1. Add Tags to columns list
2. Format tags: `", ".join(artifact.tags) if artifact.tags else ""`
3. Style tags (if applicable): `f"[#d79921]{tags}[/#d79921]" if tags else ""`
4. Add tags to row data
5. Adjust column width calculations to include tags_width=20

### Data Model Verification Needed

Must verify that all artifact models have `tags` attribute:
- Decision (ADR) - likely has tags
- Spec (SPEC/PROD) - likely has tags
- ChangeArtifact (Delta/Revision/Audit) - likely has tags
- RequirementRecord - need to verify
- BacklogItem - need to verify

### Testing Strategy

For each formatter:
- Test empty tags (no tags)
- Test single tag
- Test multiple tags
- Test long tag lists
- Verify column width calculations
- Verify styling consistency

## Decisions Made

1. **Tags column width**: 20 characters (following DE-010 pattern)
2. **Tags styling**: Use `[#d79921]` color for consistency
3. **Empty tags**: Show empty string, not "—" or "N/A"
4. **Column placement**: Varies by formatter to respect artifact-specific priorities

## Implementation Complete

All formatters have been successfully updated with Tags column:

### Files Modified

1. **decision_formatters.py** - Added Tags column (ID, Title, Tags, Status, Updated)
2. **spec_formatters.py** - Added Tags column (ID, Name, Tags, Status)
3. **change_formatters.py** - Added Tags column (ID, Name, Tags, Status)
4. **requirement_formatters.py** - Added Tags column (Spec, Label, Category, Title, Tags, Status)
5. **backlog_formatters.py** - Added Tags column (ID, Kind, Title, Tags, Status, Severity)

### Key Implementation Details

- Used `getattr(obj, "tags", [])` pattern for all formatters to handle models that may not have tags attribute
- Tags column width: 20 characters (consistent with DE-010)
- Tags styling: `[#d79921]` color for visual consistency
- Empty tags: display empty string (not "—" or "N/A")
- All column widths adjusted to accommodate Tags column

### Test Results

- All 1459 tests pass
- All formatter-specific tests pass (143 tests in formatters/)
- Ruff linter: All checks passed for formatters/
- Pylint: 9.80/10 rating (excellent)

### Lessons Learned

1. Not all artifact models have `tags` attribute - using `getattr()` with default is safer
2. Models without tags: BacklogItem, RequirementRecord, Spec, ChangeArtifact
3. Models with tags: Decision (ADR), Policy, Standard
4. Defensive programming with getattr prevents AttributeError exceptions

## Architectural Improvement

Per user suggestion, added `tags` property/field to all models instead of using defensive `getattr()`:

### Models Updated with Tags Support

1. **Spec** (`specs/models.py`) - Added `@property tags()` following existing pattern
2. **ChangeArtifact** (`changes/artifacts.py`) - Added `tags: list[str]` field + extraction from frontmatter
3. **RequirementRecord** (`requirements/registry.py`) - Added `tags: list[str]` field + serialization support
4. **BacklogItem** (`backlog/models.py` + `backlog/registry.py`) - Added `tags: list[str]` field + extraction from frontmatter

### Benefits of This Approach

- **Type safety**: Models now explicitly declare tags support
- **Consistency**: All artifacts have tags in frontmatter, models now reflect this
- **Simpler code**: Removed all defensive `getattr()` calls from formatters
- **Discoverability**: Tags are now a first-class feature, easier to find in IDEs
- **Better architecture**: Models match the actual data structure

### Final Test Results

- **All 1459 tests passing** ✓
- **Ruff linter**: All checks passed ✓

## Implementation Complete

DE-018 is fully implemented with improved architecture.
