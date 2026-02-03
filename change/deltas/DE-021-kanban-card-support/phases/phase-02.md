---
id: IP-021.PHASE-02
slug: 021-kanban-card-support-phase-02
name: IP-021 Phase 02
created: '2026-02-03'
updated: '2026-02-03'
completed: '2026-02-03'
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-021.PHASE-02
plan: IP-021
delta: DE-021
objective: >-
  Implement card artifact support with domain package, formatters, CLI commands, and comprehensive tests
entrance_criteria:
  - Phase 1 complete with design locked
  - Open questions resolved
  - Test strategy confirmed
exit_criteria:
  - All VT verification artifacts passing
  - Domain + formatters + CLI implemented
  - just passes (format/lint/test/pylint)
  - Code follows SRP and thin CLI patterns
verification:
  tests:
    - VT-021-001 - ID parsing + lane detection + ambiguity rules
    - VT-021-002 - next-ID allocation scans all lanes
    - VT-021-003 - create card copies template and rewrites only H1/Created
    - VT-021-004 - show card -q path-only behaviour and errors
    - VT-021-005 - find card repo-wide filename matching
    - VT-021-006 - list cards output formats (table/json/tsv)
  evidence:
    - All tests passing
    - Linters passing
    - Manual smoke test of create/list/show/find
tasks:
  - 2.1 Create domain package structure
  - 2.2 Implement Card model (TDD)
  - 2.3 Implement CardRegistry discovery + ID parsing (TDD)
  - 2.4 Implement next-ID allocation (TDD)
  - 2.5 Implement card creation (TDD)
  - 2.6 Implement card resolution (show) (TDD)
  - 2.7 Create card formatters (TDD)
  - 2.8 Add CLI create card command
  - 2.9 Add CLI list cards command
  - 2.10 Add CLI show card command
  - 2.11 Add CLI find card command
  - 2.12 Create kanban/template.md
  - 2.13 Run tests and fix issues
  - 2.14 Run linters and fix issues
risks:
  - Template rewriting might affect user content
  - Ambiguity handling needs careful error messages
  - Lane validation needs clear errors
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-021.PHASE-02
```

# Phase 2 - Implementation

## 1. Objective
Implement complete card artifact support following TDD principles. Build domain package (cards/), formatters, and CLI commands while maintaining thin CLI pattern and SRP.

## 2. Links & References
- **Delta**: DE-021 - Card support (kanban board)
- **Design Revision**: DR-021 - Section 4 (Code Impact Summary)
- **Phase 1**: phases/phase-01.md - Design decisions locked
- **Verification Plan**: IP-021 Section 6 (VT-021-001 through VT-021-006)
- **Similar Implementations**:
  - supekku/scripts/lib/decisions/ - DecisionRegistry pattern
  - supekku/scripts/lib/backlog/ - BacklogRegistry pattern
  - supekku/scripts/lib/formatters/decision_formatters.py - Formatter pattern

## 3. Entrance Criteria
- [x] Phase 1 complete with design locked
- [x] Open questions resolved (defer dependencies, add --lane flag, auto-create template)
- [x] Test strategy confirmed (VT-021-001..006)
- [x] Existing patterns reviewed (decisions, backlog, formatters)

## 4. Exit Criteria / Done When
- [x] All VT-021-001..006 tests passing (32 card tests + all others)
- [x] Domain package implemented (cards/models.py, cards/registry.py)
- [x] Formatters implemented (formatters/card_formatters.py)
- [x] CLI commands implemented (create/list/show/find card)
- [x] kanban/template.md created
- [x] `just` passes (format + lint + test + pylint) - 1524 tests, ruff clean, pylint clean
- [ ] Manual smoke test successful (deferred to Phase 3 VH-021-001)

## 5. Verification
**Tests to run**:
- `uv run pytest supekku/scripts/lib/cards/` - Domain tests
- `uv run pytest supekku/scripts/lib/formatters/card_formatters_test.py` - Formatter tests
- `uv run pytest supekku/cli/` - CLI tests
- `just test` - All tests
- `just lint` - Ruff linter
- `just pylint` - Pylint
- `just` - All quality checks

**Evidence to capture**:
- Test output showing all VT artifacts passing
- Linter output showing zero warnings
- Manual test: create card, list cards, show card, find card

## 6. Assumptions & STOP Conditions
**Assumptions**:
- kanban/ directory exists with backlog/, doing/, done/ subdirectories
- Existing registry patterns are stable and proven
- Typer CLI framework is well-understood
- Pure function formatter pattern is established

**STOP when**:
- Tests reveal ambiguity in ID parsing logic - clarify with user
- Template rewriting affects unexpected content - review with user
- Linter failures require architecture changes - consult user
- Uncertain about formatter output format - verify with user

## 7. Tasks & Progress
*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 2.1 | Create domain package structure | [ ] | cards/ package created with models.py, registry.py |
| [x] | 2.2 | Implement Card model | [ ] | Dataclass with id, title, lane, path, created, status |
| [x] | 2.3 | Implement CardRegistry discovery + ID parsing | [ ] | Glob-based discovery, ID parsing from filename |
| [x] | 2.4 | Implement next-ID allocation | [ ] | Scans all lanes for max ID |
| [x] | 2.5 | Implement card creation | [ ] | Template-based with H1/Created rewrite |
| [x] | 2.6 | Implement card resolution (show) | [ ] | Ambiguity detection, --anywhere support |
| [x] | 2.7 | Create card formatters | [ ] | Table/tsv/json formats, detail view |
| [x] | 2.8 | Add CLI create card command | [ ] | create.py - thin orchestration |
| [x] | 2.9 | Add CLI list cards command | [ ] | list.py - filtering + formatting + --all flag |
| [x] | 2.10 | Add CLI show card command | [ ] | show.py - resolution + display |
| [x] | 2.11 | Add CLI find card command | [ ] | find.py - repo-wide search |
| [x] | 2.12 | Create kanban/template.md | [ ] | Minimal template with sections |
| [x] | 2.13 | Run tests and fix issues | [ ] | All 1524 tests pass, fixed rebase issues |
| [x] | 2.14 | Run linters and fix issues | [ ] | ruff + pylint passing |

### Task Details

- **2.1 Create domain package structure**
  - **Design / Approach**: Follow decisions/backlog pattern
  - **Files / Components**:
    - supekku/scripts/lib/cards/__init__.py (new)
    - supekku/scripts/lib/cards/models.py (new)
    - supekku/scripts/lib/cards/registry.py (new)
    - supekku/scripts/lib/cards/registry_test.py (new)
  - **Testing**: N/A (structure only)
  - **Observations & AI Notes**:
  - **Commits / References**:

- **2.2 Implement Card model (TDD)**
  - **Design / Approach**: Dataclass with id, title, lane, path, created fields
  - **Files / Components**: cards/models.py
  - **Testing**: VT-021-001 - ID parsing, lane detection
  - **Test Cases**:
    - Parse ID from filename T123-description.md → T123
    - Detect lane from path kanban/doing/T123.md → "doing"
    - Handle missing lane (no kanban/ in path) → None or "unknown"
    - Parse title from first H1
    - Parse Created date
  - **Observations & AI Notes**:
  - **Commits / References**:

- **2.3 Implement CardRegistry discovery + ID parsing (TDD)**
  - **Design / Approach**: Scan kanban/** for T###-*.md, parse metadata
  - **Files / Components**: cards/registry.py
  - **Testing**: VT-021-001 - Discovery across lanes, ambiguity detection
  - **Test Cases**:
    - Discover cards across all lanes (backlog/doing/done)
    - Handle multiple cards with same ID (ambiguity error)
    - Handle cards outside kanban/ with --anywhere
    - Return empty list when no cards found
  - **Observations & AI Notes**:
  - **Commits / References**:

- **2.4 Implement next-ID allocation (TDD)**
  - **Design / Approach**: Scan all T###-*.md, find max ID, return max+1
  - **Files / Components**: cards/registry.py - next_id() method
  - **Testing**: VT-021-002 - ID allocation across lanes
  - **Test Cases**:
    - Empty kanban → T001
    - Existing T001, T002 → T003
    - Gaps in sequence (T001, T005) → T006
    - Scan all lanes, not just backlog
  - **Observations & AI Notes**:
  - **Commits / References**:

- **2.5 Implement card creation (TDD)**
  - **Design / Approach**: Copy template, rewrite H1 + Created, allocate ID, support --lane
  - **Files / Components**: cards/registry.py - create_card() method
  - **Testing**: VT-021-003 - Template preservation, H1/Created rewrite
  - **Test Cases**:
    - Create with description → rewrites first H1 to `# T###: description`
    - Inserts/updates `Created: YYYY-MM-DD` line
    - Preserves all other template content verbatim
    - Auto-creates kanban/template.md if missing
    - Respects --lane flag (backlog/doing/done, default backlog)
    - Validates lane exists or errors clearly
  - **Observations & AI Notes**:
  - **Commits / References**:

- **2.6 Implement card resolution (show) (TDD)**
  - **Design / Approach**: Resolve T### to path, handle ambiguity, support --anywhere
  - **Files / Components**: cards/registry.py - resolve_card() method
  - **Testing**: VT-021-004 - Path resolution, ambiguity errors, -q flag
  - **Test Cases**:
    - Unambiguous match → return single Card
    - No match → error with clear message
    - Multiple matches → error listing candidates
    - --anywhere flag expands search beyond kanban/
    - -q flag returns only path string
  - **Observations & AI Notes**:
  - **Commits / References**:

- **2.7 Create card formatters (TDD)**
  - **Design / Approach**: Pure functions for table/tsv/json output
  - **Files / Components**:
    - formatters/card_formatters.py (new)
    - formatters/card_formatters_test.py (new)
  - **Testing**: VT-021-006 - Output format consistency
  - **Test Cases**:
    - format_card_list_table(cards, "table") → aligned columns
    - format_card_list_table(cards, "tsv") → tab-separated
    - format_card_list_json(cards) → valid JSON array
    - format_card_details(card) → human-readable detail view
    - Handle empty card list gracefully
  - **Observations & AI Notes**:
  - **Commits / References**:

- **2.8 Add CLI create card command**
  - **Design / Approach**: Thin orchestration: parse args → registry.create_card → output
  - **Files / Components**: supekku/cli/create.py - create_card() function
  - **Testing**: CLI integration test
  - **Implementation**:
    - @app.command("card")
    - Args: description (positional), --lane (optional, default backlog)
    - Call CardRegistry(root).create_card(description, lane)
    - Print success message with path
  - **Observations & AI Notes**:
  - **Commits / References**:

- **2.9 Add CLI list cards command**
  - **Design / Approach**: Thin orchestration: registry → filter → format → output
  - **Files / Components**: supekku/cli/list.py - list_cards() function
  - **Testing**: CLI integration test
  - **Implementation**:
    - @app.command("cards")
    - Args: --lane filter, --format {table|tsv|json}
    - Call CardRegistry(root).all_cards()
    - Filter by lane if specified
    - Format with card_formatters
    - Print output
  - **Observations & AI Notes**:
  - **Commits / References**:

- **2.10 Add CLI show card command**
  - **Design / Approach**: Thin orchestration: resolve → format → output
  - **Files / Components**: supekku/cli/show.py - show_card() function
  - **Testing**: VT-021-004 - Path-only output, error handling
  - **Implementation**:
    - @app.command("card")
    - Args: card_id (T###), -q/--quiet, --anywhere
    - Call CardRegistry(root).resolve_card(id, anywhere)
    - If -q: print path only
    - Else: format with format_card_details and print
    - Handle ambiguity/not-found errors with clear messages
  - **Observations & AI Notes**:
  - **Commits / References**:

- **2.11 Add CLI find card command**
  - **Design / Approach**: New find.py module + command group, repo-wide filename search
  - **Files / Components**:
    - supekku/cli/find.py (new)
    - supekku/cli/main.py (register find group)
  - **Testing**: VT-021-005 - Repo-wide filename matching
  - **Implementation**:
    - Create find.py with Typer app
    - @app.command("card")
    - Args: card_id (T###)
    - Search repo for ^T###-.*\.md$ filename pattern
    - Print all matches (one per line)
    - Register find app in main.py
  - **Observations & AI Notes**:
  - **Commits / References**:

- **2.12 Create kanban/template.md**
  - **Design / Approach**: Minimal template with H1 placeholder, Created field
  - **Files / Components**: kanban/template.md (new)
  - **Testing**: Manual verification
  - **Template Content**:
    ```markdown
    # T000: Placeholder

    Created:

    ## Description

    ## Notes
    ```
  - **Observations & AI Notes**:
  - **Commits / References**:

- **2.13 Run tests and fix issues**
  - **Design / Approach**: Execute `just test`, address failures
  - **Files / Components**: All test files
  - **Testing**: All VT-021-001..006 must pass
  - **Observations & AI Notes**:
  - **Commits / References**:

- **2.14 Run linters and fix issues**
  - **Design / Approach**: Execute `just lint` and `just pylint`, fix all warnings
  - **Files / Components**: All source files
  - **Testing**: Zero warnings required
  - **Observations & AI Notes**:
  - **Commits / References**:

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| Template rewriting breaks user content | Test with varied templates; only rewrite H1 + Created | mitigated |
| Ambiguous ID resolution confuses users | Clear error messages listing candidates | mitigated |
| Lane validation inconsistent | Validate against known lanes (backlog/doing/done) | mitigated |
| Performance with large kanban/ directory | Use glob patterns, not recursive walks; defer optimization | accepted |
| Missing template.md blocks creation | Auto-create on first use with clear message | mitigated |

## 9. Decisions & Outcomes
- `2026-02-03` - TDD approach: write tests before implementation for each VT artifact
- `2026-02-03` - Follow established patterns from decisions/ and backlog/ domains
- `2026-02-03` - **UX Enhancement**: list cards now hides done/archived lanes by default, added --all flag (user feedback)
- `2026-02-03` - Phase 2 complete: All automated tests passing, ready for manual verification

## 10. Findings / Research Notes
- Decision formatters use helper functions (_format_*) for reusable components
- Backlog registry has next_identifier() pattern for ID allocation
- CLI commands are thin (~20-50 lines) with all logic in registry
- **Rebase issues fixed**: 5 backlog list_test.py failures (ISSUE-002/003 filtering) resolved post-rebase
- **Unrelated test fix**: typescript_test.py required package.json in test setup for package root detection
- **Test coverage**: 32 card-specific tests across models, registry, formatters, CLI
- **Pattern adherence**: Successfully followed SRP + thin CLI patterns; formatters are pure functions
- **Performance**: Glob-based discovery efficient; no performance concerns observed
- **UX refinement**: User feedback led to --all flag for list cards; default now hides done/archived lanes
- **Future enhancement**: Regex lane filtering deferred to future work (keep scope contained)

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied (except manual smoke test → Phase 3)
- [x] All VT-021-001..006 tests passing (32 card tests)
- [x] `just` passes (format/lint/test/pylint) - 1524 tests, ruff clean, pylint clean
- [x] Verification evidence: All tests pass, linters clean
- [x] Phase 2 notes updated with observations
- [x] Hand-off notes to Phase 3 (manual verification VH-021-001)
