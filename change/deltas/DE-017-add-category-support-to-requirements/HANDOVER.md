# DE-017 Handover Notes

**Date**: 2025-11-04
**Phase Completed**: Phase 1 - Data Model & Parser
**Next Phase**: Phase 2 - CLI & Formatters
**Status**: Ready for continuation

## What Was Accomplished

### Phase 1 Complete ✓

**Data Model & Parser** - All 9 tasks completed successfully.

**Key Deliverables**:
- ✅ Category field added to RequirementRecord (`category: str | None`)
- ✅ Regex extended to parse `**FR-001**(category): description` syntax
- ✅ Frontmatter category parsing with body precedence
- ✅ Serialization/merge logic with category support
- ✅ Comprehensive test coverage (VT-017-001, VT-017-002)
- ✅ All linters passing (ruff + pylint)

**Test Results**:
- 1352 tests passing (4 new category tests added)
- Zero lint warnings
- Backward compatible - all existing tests pass

**Commits**:
1. `d217830` - feat: category field + parsing (tasks 1.1-1.6)
2. `aa533e7` - test: VT-017-001 and VT-017-002 (tasks 1.7-1.9)
3. `9a03f92` - docs: phase-01 completion tracking
4. `b563f4d` - docs: phase-02 sheet creation

## Implementation Details

### Category Syntax Supported

**Inline (body precedence)**:
```markdown
- **FR-001**(auth): Authentication requirement
- **FR-002**(security/auth): Hierarchical category
- **NF-001**(perf.db): Dot-delimited category
```

**Frontmatter (fallback)**:
```yaml
---
category: security
---
```

**Precedence**: Inline category > Frontmatter category

### Files Modified

**Core Implementation**:
- `supekku/scripts/lib/requirements/registry.py` - RequirementRecord model, regex, parser
- `supekku/scripts/lib/core/frontmatter_metadata/spec.py` - Schema metadata
- `supekku/scripts/lib/core/frontmatter_metadata/prod.py` - Schema metadata

**Tests**:
- `supekku/scripts/lib/requirements/registry_test.py` - 4 new test methods

**Documentation**:
- `change/deltas/DE-017-add-category-support-to-requirements/phases/phase-01.md` - Complete
- `change/deltas/DE-017-add-category-support-to-requirements/phases/phase-02.md` - Ready

## What's Next: Phase 2

### Objective
Add category filtering and display to the `list requirements` CLI command.

### Key Tasks (8 total)

1. **Create requirement_formatters.py** - Pure formatting functions
2. **Implement format_requirement_list_item** - Tab-separated output with category column
3. **Add --category filter** - Substring match on category field
4. **Extend regexp/case-insensitive filters** - Include category in search
5. **Update CLI to use formatter** - Skinny CLI pattern
6. **Write VT-017-003** - CLI filtering integration tests
7. **Write VT-017-004** - Category display integration tests
8. **Linters** - Ensure zero warnings

### Starting Points

**Find list requirements CLI**:
```bash
# Locate the command
grep -r "def.*list.*requirement" supekku/
uv run spec-driver list requirements --help

# Likely locations:
# - supekku/scripts/requirements.py
# - supekku/cli/list.py
```

**Review formatter patterns**:
```bash
# Existing formatters as templates
cat supekku/scripts/lib/formatters/decision_formatters.py
cat supekku/scripts/lib/formatters/change_formatters.py

# Architecture guide
cat AGENTS.md  # Section: Adding a Formatter
```

**Expected output format**:
```
label    status    category    title
FR-001   pending   auth        Authentication requirement
FR-002   active    security    Data encryption
FR-003   pending   -           No category requirement
```

### Exit Criteria for Phase 2

- [ ] `requirement_formatters.py` module created
- [ ] Category column displays in list output
- [ ] `--category` filter works (substring match)
- [ ] Regexp/case-insensitive filters include category
- [ ] VT-017-003 and VT-017-004 passing
- [ ] Linters clean
- [ ] Formatter has comprehensive unit tests

### Risks to Watch

1. **CLI output format change** - Keep backward compatible, add category as new column
2. **Filter logic complexity** - Follow existing filter patterns
3. **Cannot find CLI command** - Use grep to locate, check existing list commands
4. **Test infrastructure gaps** - Use tempdir-based integration tests like Phase 1

## Quick Commands

```bash
# Run full test suite
just test

# Run quick validation
just quickcheck

# Lint specific file
just pylint supekku/scripts/lib/formatters/requirement_formatters.py

# Check current CLI behavior
uv run spec-driver list requirements --help
uv run spec-driver list requirements
```

## Phase Sheet Location

**Current Phase (complete)**:
`change/deltas/DE-017-add-category-support-to-requirements/phases/phase-01.md`

**Next Phase (ready)**:
`change/deltas/DE-017-add-category-support-to-requirements/phases/phase-02.md`

## Implementation Philosophy

**Follow AGENTS.md principles**:
- SRP - Formatters have NO business logic
- Pure functions - `(input) -> output` with no side effects
- Skinny CLI - Orchestrate, never implement
- Avoid premature abstraction - Start specific, generalize later

**TDD Approach**:
1. Write tests first (VT-017-003, VT-017-004)
2. Implement formatters (pure functions)
3. Update CLI (thin orchestration)
4. Lint as you go
5. Commit on task completion

## Token Budget Note

Starting Phase 2 continuation: ~97k of ~150k practical tokens remaining (adequate runway for Phase 2 completion).

## Questions?

Refer to:
- `DE-017.md` - Delta motivation and scope
- `DR-017.md` - Design decisions
- `IP-017.md` - Implementation plan overview
- `phase-01.md` - Completed phase details
- `phase-02.md` - Next phase details
- `AGENTS.md` - Architecture patterns

---

**Status**: Ready for Phase 2 implementation. All entrance criteria satisfied. ✓
