# CLI UX Research Report

**Date**: 2025-11-03
**Researcher**: Claude (Sonnet 4.5)
**Scope**: Non-destructive CLI commands (list, show, schema, validate, sync)
**Methodology**: Systematic exploration with focus on consistency, discoverability, error handling, and human vs agent workflows

---

## Executive Summary

The CLI demonstrates solid foundational UX with good error handling and consistent patterns. Key strengths include excellent typo suggestions, clean table formatting, and comprehensive filtering. Critical gaps exist in JSON output consistency, status filtering patterns, and documentation of output modes.

**Priority recommendations:**
1. Standardize `--json` availability across all list commands
2. Unify status filtering patterns (some commands use `-s`, some don't support it)
3. Add `--help` examples for common workflows
4. Document which fields appear in table vs TSV vs JSON modes

---

## 1. Discovery & Help System

### Strengths
- Main help clearly groups commands by function
- Subcommand help is comprehensive with option descriptions
- Rich formatting makes help text scannable

### Issues
**[MEDIUM]** Missing usage examples in help text
- No examples of common filter combinations
- No guidance on format differences (table/json/tsv)
- Agent users won't know when `--json` is available

**[LOW]** Inconsistent command naming conventions
- `list specs` (plural) vs `show spec` (singular) - this is actually correct
- `list changes` (generic) vs `list deltas` (specific) - slight cognitive overhead

### Recommendations
```markdown
# For each list command, add:
Examples:
  # List all draft deltas
  spec-driver list deltas -s draft

  # Find specs by package
  spec-driver list specs --package supekku/cli

  # Export to JSON for scripting
  spec-driver list requirements --format json
```

---

## 2. Command Structure & Consistency

### List Commands Analysis

| Command | Status Filter | Regex Filter | JSON Output | TSV Options |
|---------|---------------|--------------|-------------|-------------|
| `list specs` | ❌ | ✅ `-r` | ✅ `--json` | ✅ `--paths`, `--packages` |
| `list deltas` | ✅ `-s` | ✅ `-r` | ✅ `--format json` | ✅ `--details` |
| `list adrs` | ✅ `-s` | ✅ `-r` | ✅ `--format json` | ❌ |
| `list requirements` | ✅ `--status` | ✅ `-r` | ✅ `--format json` | ❌ |
| `list revisions` | ✅ `-s` | ✅ `-r` | ✅ `--format json` | ❌ |
| `list changes` | ✅ `-s` | ✅ `-r` | ✅ `--format json` | ✅ `--paths`, `--relations`, `--applies`, `--plan` |

### Critical Inconsistencies

**[HIGH] JSON flag inconsistency**
- `list specs` uses `--json` shorthand
- All others use `--format json`
- **Recommendation**: Standardize on `--format json` with `--json` as universal shorthand

**[HIGH] Status filter inconsistency**
- Most commands: `-s` / `--status`
- Requirements: `--status` (no short flag)
- Specs: **No status filter at all**
- **Recommendation**: Add `-s`/`--status` to ALL list commands

**[MEDIUM] TSV detail flags vary by artifact**
- Deltas: `--details` (phases, specs, requirements)
- Changes: `--paths`, `--relations`, `--applies`, `--plan`
- Specs: `--paths`, `--packages`
- Requirements/ADRs: **No TSV details**
- **Recommendation**: Audit what details are useful per artifact, then standardize naming

---

## 3. Output Formats & Token Efficiency

### Table Format (Default)
**Strengths:**
- Rich formatting with borders and alignment
- Truncates gracefully with `--truncate`
- Human-readable at a glance

**Issues:**
- No indication of what's truncated (visual only)
- Column widths fixed - may not adapt well to narrow terminals

### JSON Format
**Strengths:**
- Well-structured, parseable
- Includes full paths and metadata
- Consistent `{"items": [...]}` wrapper

**Issues:**
**[HIGH]** Inconsistent availability (see table above)
**[MEDIUM]** No streaming for large result sets
**[LOW]** No `--compact` option for agents needing minimal tokens

### TSV Format
**Strengths:**
- Machine-readable, grep-friendly
- Optional detail flags for token control

**Issues:**
**[MEDIUM]** Not all commands support detail flags
**[LOW]** No header row option (`--no-header` for scripts)

### Recommendations
1. **Add to all list commands:**
   ```
   --json          Shorthand for --format=json
   --compact       Minimal JSON (no whitespace)
   --no-header     Suppress header row in TSV
   ```

2. **Document output modes clearly:**
   - Table: Human viewing, rich formatting
   - JSON: Agent parsing, full metadata
   - TSV: Scripting, grep, token-efficient drilling

---

## 4. Show Commands Analysis

### Tested Commands
- `show delta DE-004` - ✅ Clear, hierarchical
- `show spec SPEC-110` - ✅ Minimal but useful
- `show adr ADR-001` - ✅ Metadata-focused
- `show requirement PROD-006.FR-001` - ✅ Lifecycle tracking

### Strengths
- Hierarchical display (delta → plan → phases)
- Progress indicators for phases (9/19 tasks - 47%)
- Clear file path references

### Issues
**[MEDIUM]** `show spec` very minimal
- Only shows: ID, name, slug, kind, status, packages, file path
- Humans might want: summary, requirements count, coverage status
- Agents need: `--json` option (currently missing)

**[MEDIUM]** `show delta` doesn't offer JSON
- Complex nested structure would benefit from JSON
- **Test**: `spec-driver show delta DE-004 --json` → ✅ Actually works!
- **Issue**: Not documented in `--help`

**[LOW]** No `--format` consistency with list commands
- `show delta --json` works
- Should `show spec --json` also work? (Currently missing)

### Recommendations
1. Add `--json` to ALL show commands
2. Enhance `show spec` human output:
   ```
   ID: SPEC-110
   Name: supekku/cli Specification
   Status: draft
   Requirements: 12 total (3 verified, 9 pending)
   Coverage: 25%
   Related Deltas: DE-004, DE-006
   File: specify/tech/SPEC-110/SPEC-110.md
   ```

---

## 5. Schema Commands (Agent-Focused)

### Excellent Design
- Clear separation: block schemas vs frontmatter schemas
- Comprehensive list view with descriptions
- Full JSON Schema output for validation

### Minor Issues
**[LOW]** Error message could be more helpful
```bash
$ spec-driver schema show supekku.phase.overview
Error: Unknown block type: supekku.phase.overview
```

Should suggest: `Did you mean 'phase.overview'? (Prefix 'supekku.' is implied)`

**[LOW]** No `--compact` for agents
- Full JSON Schema is verbose (100+ lines)
- Agents might only need required fields or structure outline

### Recommendations
1. Improve error message with suggestion
2. Add `--outline` flag for abbreviated view:
   ```
   phase.overview (supekku.phase.overview v1)
   Required: schema, version, phase, plan, delta
   Optional: objective, entrance_criteria, exit_criteria, verification, tasks, risks
   ```

---

## 6. Error Handling & Guidance

### Excellent Examples
```bash
$ spec-driver list delta
Error: No such command 'delta'. Did you mean 'deltas'?  ✅ Clear suggestion

$ spec-driver list specs --status draft
Error: No such option: --status Did you mean --paths?  ⚠️  Suggestion not ideal

$ spec-driver show delta DE-999
Error: Delta not found: DE-999  ✅ Clear, concise

$ spec-driver list deltas --format xml
Error: invalid format: xml  ⚠️  Should list valid formats
```

### Recommendations
1. **When option doesn't exist, suggest valid options:**
   ```
   Error: No such option: --status
   Available filters: --kind, --filter, --package, --regexp
   See 'spec-driver list specs --help' for details
   ```

2. **For invalid enum values, show valid choices:**
   ```
   Error: invalid format: xml
   Valid formats: table, json, tsv
   ```

---

## 7. Human vs Agent Workflows

### Current State

**Human-optimized commands:**
- `list` (table output) ✅
- `show` (formatted text) ✅
- Error messages with suggestions ✅

**Agent-optimized commands:**
- `schema list` / `schema show` ✅
- `--json` on most commands ⚠️ (inconsistent)
- `--format json` ✅ (but not everywhere)

### Gaps

**[HIGH] No `--machine-readable` mode**
- Agents want: compact JSON, no ANSI colors, predictable structure
- Currently must specify `--format json` and hope it's supported

**[MEDIUM] Schema introspection partial**
- Agents can see frontmatter schemas ✅
- Agents can't discover: valid status values per artifact, valid filter values, relationship types
- **Example need**: "What are valid delta statuses?" → Not exposed via CLI

**[LOW] No streaming/pagination**
- `list requirements` returns 77 items at once
- For large projects, this will be slow and token-heavy

### Recommendations

1. **Add universal `--machine-readable` flag:**
   ```bash
   spec-driver list deltas --machine-readable
   # Implies: --format=json --compact --no-color
   ```

2. **Add metadata introspection:**
   ```bash
   spec-driver schema show enums.delta.status
   # Output: ["draft", "in-progress", "completed", "deferred"]

   spec-driver schema show enums.requirement.kind
   # Output: ["FR", "NF"]
   ```

3. **Add pagination for large result sets:**
   ```bash
   spec-driver list requirements --limit 20 --offset 0
   spec-driver list requirements --page 2 --per-page 20
   ```

---

## 8. Filter Patterns & Predictability

### Current Filter Types

| Filter Type | Flags | Commands | Notes |
|-------------|-------|----------|-------|
| **Substring** | `-f`, `--filter` | specs, requirements, changes, revisions | Case-insensitive, matches ID/name/slug |
| **Regex** | `-r`, `--regexp` | All list commands | Optional `-i` for case-insensitive |
| **Status** | `-s`, `--status` | deltas, adrs, requirements, revisions, changes | Exact match |
| **Kind** | `-k`, `--kind` | specs, changes | Enum values |
| **Relationship** | `--spec`, `--delta`, etc | adrs, requirements, revisions | References |
| **Package** | `-p`, `--package` | specs | Substring match |

### Strengths
- Regex available everywhere (good for agents)
- Substring filters are case-insensitive (good for humans)
- Relationship filters enable discovery

### Issues
**[HIGH]** Specs lack status filtering
- Every other artifact can filter by status
- Specs are stuck with post-filtering via grep/jq

**[MEDIUM]** Relationship filters inconsistent
- ADRs: `--spec`, `--delta`, `--requirement`, `--policy`
- Requirements: `--spec`, `--implemented-by`, `--verified-by`
- Revisions: `--spec` only
- **Gap**: Can't easily find "all deltas implementing SPEC-110"

**[MEDIUM]** No multi-value filters
```bash
# Want: multiple statuses
spec-driver list deltas -s draft -s in-progress  # Doesn't work

# Workaround:
spec-driver list deltas --regexp '(draft|in-progress)'  # Works but obscure
```

### Recommendations

1. **Add status filter to specs:**
   ```bash
   spec-driver list specs -s draft
   spec-driver list specs -s active,verified  # Multi-value
   ```

2. **Add reverse relationship queries:**
   ```bash
   spec-driver list deltas --implements SPEC-110
   spec-driver list requirements --verified-by VT-*
   ```

3. **Support multi-value filters:**
   ```bash
   spec-driver list deltas -s draft,in-progress
   # Equivalent to: status IN (draft, in-progress)
   ```

---

## 9. Consistency with Workflows

### Key Workflows (from supekku/about/*)

**Workflow 1: Find work to do**
```bash
# Human: Browse draft deltas
spec-driver list deltas -s draft  ✅ Works

# Agent: Get structured delta info
spec-driver list deltas -s draft --format json  ✅ Works

# Agent: Get delta details for planning
spec-driver show delta DE-004 --json  ✅ Works (undocumented)
```

**Workflow 2: Check requirement coverage**
```bash
# Find pending requirements in a spec
spec-driver list requirements --spec SPEC-110 --status pending  ✅ Works

# See verification status
spec-driver show requirement SPEC-110.FR-001  ✅ Works

# Find what deltas implement it
spec-driver list deltas --json | jq '.items[] | select(.applies_to.requirements[] | contains("SPEC-110.FR-001"))'  ⚠️ Tedious
```
**Missing**: `spec-driver list deltas --implements SPEC-110.FR-001`

**Workflow 3: Audit decisions**
```bash
# List accepted ADRs
spec-driver list adrs -s accepted  ✅ Works

# Find specs related to an ADR
spec-driver list specs --json | jq '.items[] | select(.relations[]? | select(.type == "informs" and .target == "ADR-001"))'  ⚠️ Very tedious
```
**Missing**: `spec-driver list specs --informed-by ADR-001`

### Recommendations
1. Add reverse relationship queries (see section 8)
2. Document common workflow patterns in `--help` examples
3. Consider workflow-specific commands:
   ```bash
   spec-driver audit coverage SPEC-110
   spec-driver audit requirements --status pending
   ```

---

## 10. Principle of Least Surprise

### Surprises Found

**[POSITIVE]** Typo suggestions are excellent
```bash
$ spec-driver list delta
Error: No such command 'delta'. Did you mean 'deltas'?
```

**[NEGATIVE]** Status filter missing from specs
- Every other artifact has it
- Users will try `--status` and fail

**[NEGATIVE]** JSON availability unclear
- Some commands: `--json`
- Others: `--format json`
- Some show commands: works but undocumented

**[NEGATIVE]** "Changes" vs "Deltas" distinction
- `list changes` shows deltas, revisions, audits
- `list deltas` shows only deltas
- Not obvious from command names alone

### Recommendations
1. Add note to `list changes --help`:
   ```
   Note: Use 'list deltas' for delta-specific filters.
   'list changes' provides a unified view across all change artifact types.
   ```

2. Make `--json` universal and documented

3. Add status filter to specs

---

## 11. Token Efficiency vs Information

### List Views - Good Balance
- **Default (table)**: ID, status, name → Quick scan
- **TSV**: Optionally add paths, packages, details
- **JSON**: Full metadata

**Observation**: Users can drill down progressively without over-fetching.

### Show Views - Could Improve

**Current**: `show spec SPEC-110`
```
ID: SPEC-110
Name: supekku/cli Specification
Status: draft
Packages: supekku/cli
File: specify/tech/SPEC-110/SPEC-110.md
```
**5 lines, ~120 chars** → Very minimal, forces file read for any details

**Proposed**: Add `--summary` mode (default)
```
ID: SPEC-110
Name: supekku/cli Specification
Status: draft
Packages: supekku/cli
Requirements: 12 (3 verified, 9 pending)
Coverage: 25%
Related: 2 deltas, 1 ADR
File: specify/tech/SPEC-110/SPEC-110.md
```
**8 lines, ~200 chars** → More useful, still token-efficient

**Proposed**: Add `--full` mode
```
[Summary above]
[Requirements list]
[Coverage breakdown]
[Related artifacts]
```

### Recommendations
- Keep current minimal show as default
- Add `--verbose` for expanded human view
- Add `--json` for full machine-readable dump
- Document expected use: `list` for discovery, `show` for details, file read for full content

---

## 12. Quick Wins (High Value, Low Effort)

### Priority 1: Consistency Fixes
1. ✅ Add `--json` as universal shorthand across all commands
2. ✅ Add `-s`/`--status` filter to `list specs`
3. ✅ Document `--json` availability in show command help

### Priority 2: Error Messages
4. ✅ Improve "invalid format" errors to list valid options
5. ✅ Improve "no such option" errors to suggest relevant alternatives

### Priority 3: Documentation
6. ✅ Add examples section to each list command help
7. ✅ Add workflow guide: docs/cli-workflows.md

### Priority 4: Discoverability
8. ✅ Add `spec-driver list changes --help` note about deltas distinction
9. ✅ Add metadata introspection: `schema show enums.{artifact}.{field}`

---

## 13. Larger Improvements (Requires Design)

### Medium-Term (Next Quarter)
1. **Reverse relationship queries**
   - Design query syntax
   - Index requirements for performance
   - Estimated effort: 2-3 days

2. **Multi-value filters**
   - Parse comma-separated values
   - Update all filter implementations
   - Estimated effort: 1-2 days

3. **Enhanced show spec output**
   - Compute coverage percentages
   - Fetch related artifacts
   - Format hierarchically
   - Estimated effort: 2-3 days

### Long-Term (Future Releases)
4. **Pagination for large result sets**
   - Add --limit/--offset or --page/--per-page
   - Stream JSON for very large lists
   - Estimated effort: 3-5 days

5. **Workflow-specific commands**
   - `audit coverage`
   - `audit drift`
   - `find implements <REQ-ID>`
   - Estimated effort: 5-7 days

6. **Interactive mode**
   - `spec-driver explore` → Interactive TUI
   - Navigate artifacts, drill down, filter dynamically
   - Estimated effort: 1-2 weeks

---

## 14. Summary & Action Items

### What's Working Well
- ✅ Consistent command structure (list/show/schema)
- ✅ Excellent error messages with typo suggestions
- ✅ Comprehensive filtering via regex
- ✅ Clean, readable table output
- ✅ Schema introspection for agents

### Critical Gaps
- ❌ JSON output inconsistency (--json vs --format json)
- ❌ Status filter missing from specs
- ❌ Reverse relationship queries unavailable
- ❌ Workflow examples missing from help

### Immediate Actions (This Week)
1. Audit all list commands, add `--json` everywhere
2. Add status filter to `list specs`
3. Update help text with examples for top 3 commands
4. Document output mode differences in docs/

### Next Sprint
5. Implement reverse relationship queries
6. Add multi-value filter support
7. Enhance `show spec` output
8. Write CLI workflow guide

### Backlog
9. Pagination for large lists
10. Metadata/enum introspection
11. Interactive explore mode

---

## Appendix: Testing Coverage

### Commands Tested
- ✅ `spec-driver --help`
- ✅ `list specs` (default, --json, --format tsv, -k tech)
- ✅ `list deltas` (default, -s draft, --format json, --format tsv)
- ✅ `list adrs` (default, -s accepted, --format json)
- ✅ `list requirements` (default, --format json)
- ✅ `list revisions --help`
- ✅ `list changes --help`
- ✅ `show delta DE-004` (default, --json)
- ✅ `show spec SPEC-110`
- ✅ `show adr ADR-001`
- ✅ `show requirement PROD-006.FR-001`
- ✅ `schema list`
- ✅ `schema show frontmatter.delta`
- ✅ `schema show phase.overview`
- ✅ `validate --help`
- ✅ `sync --help`

### Error Cases Tested
- ✅ Typo: `list delta` → Suggested `deltas`
- ✅ Invalid ID: `show delta DE-999` → Clear error
- ✅ Invalid option: `list specs --status draft` → Suggested `--paths`
- ✅ Invalid format: `--format xml` → Error (could be clearer)
- ✅ Invalid schema: `schema show nonexistent` → Lists available types

### Edge Cases Tested
- ✅ JSON parsability (confirmed valid JSON structure)
- ✅ TSV format (confirmed tab-separated, no header issues)
- ✅ Large result sets (77 requirements returned cleanly)
- ✅ Filter combinations (regex + kind worked correctly)

---

**End of Report**

*This report should inform UX improvement tasks for the CLI. Prioritize consistency fixes first, then expand capabilities based on actual user workflows.*
