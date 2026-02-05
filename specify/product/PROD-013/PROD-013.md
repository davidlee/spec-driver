---
id: PROD-013
slug: cli-artifact-file-access
name: CLI Artifact File Access
created: '2026-02-04'
updated: '2026-02-04'
status: draft
kind: prod
aliases: [artifact-access, file-access]
relations: []
guiding_principles:
  - Composable commands for shell pipelines
  - Consistent flags across artifact types
  - Minimal friction to view/edit artifacts
  - Follow Unix conventions ($PAGER, $EDITOR)
assumptions:
  - Users work primarily in terminal environments
  - Shell composability (piping, subshells) is valuable
  - Consistency reduces cognitive load
---

# PROD-013 – CLI Artifact File Access

```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: PROD-013
requirements:
  primary:
    - PROD-013.FR-001
    - PROD-013.FR-002
    - PROD-013.FR-003
    - PROD-013.FR-004
    - PROD-013.FR-005
    - PROD-013.FR-006
    - PROD-013.FR-007
    - PROD-013.NF-001
    - PROD-013.NF-002
  collaborators: []
interactions: []
```

```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: PROD-013
capabilities:
  - id: path-output
    name: Path Output for Show Commands
    responsibilities:
      - Output file path only via --path flag
      - Support all artifact types consistently
    requirements: [PROD-013.FR-001]
    summary: >-
      All `show` subcommands support --path flag to output only the file path,
      enabling shell composition like `$EDITOR $(spec-driver show adr 001 --path)`.
    success_criteria:
      - --path flag works on all show subcommands
      - Output is a single line with absolute or relative path

  - id: raw-content-output
    name: Raw Content Output
    responsibilities:
      - Output raw file content via --raw flag
      - Pipe-friendly output without formatting
    requirements: [PROD-013.FR-002]
    summary: >-
      All `show` subcommands support --raw flag to output the raw file content,
      useful for piping to grep, less, or other tools.
    success_criteria:
      - --raw outputs file content without modification
      - Works with pipes and redirects

  - id: view-command
    name: View Command with Pager
    responsibilities:
      - Open artifact in $PAGER (or less/more fallback)
      - Support all artifact types
    requirements: [PROD-013.FR-003]
    summary: >-
      A `view` command opens artifact files in the user's preferred pager,
      providing a convenient way to read artifacts without manual path lookup.
    success_criteria:
      - Respects $PAGER environment variable
      - Falls back to less, then more if $PAGER unset
      - Works for all artifact types

  - id: edit-command
    name: Edit Command with Editor
    responsibilities:
      - Open artifact in $EDITOR (or sensible fallback)
      - Support all artifact types
    requirements: [PROD-013.FR-004]
    summary: >-
      An `edit` command opens artifact files in the user's preferred editor,
      providing a convenient way to modify artifacts without manual path lookup.
    success_criteria:
      - Respects $EDITOR environment variable
      - Falls back to $VISUAL, then vi if unset
      - Works for all artifact types

  - id: find-all-artifacts
    name: Find Command for All Artifact Types
    responsibilities:
      - Extend find command to support all artifact types
      - Output file paths for matching artifacts
    requirements: [PROD-013.FR-005]
    summary: >-
      The `find` command supports all artifact types (not just cards),
      enabling repo-wide file lookup by artifact ID.
    success_criteria:
      - find subcommands exist for spec, delta, adr, etc.
      - Outputs one path per line

  - id: flag-consistency
    name: Consistent CLI Flags
    responsibilities:
      - Ensure --json flag on all show subcommands
      - Ensure --path flag on all show subcommands
      - Document flag availability matrix
    requirements: [PROD-013.FR-006, PROD-013.FR-007]
    summary: >-
      CLI flags are consistent across artifact types. All show commands
      support --json, --path, and --raw. List commands support --json
      and common filtering flags.
    success_criteria:
      - No flag gaps between artifact types
      - Flag behavior identical across commands
```

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: PROD-013
entries:
  - artefact: VT-001
    kind: VT
    requirement: PROD-013.FR-001
    status: verified
    notes: show_test.py - ShowPathFlagTest covers --path on all show commands
  - artefact: VT-002
    kind: VT
    requirement: PROD-013.FR-002
    status: verified
    notes: show_test.py - ShowRawFlagTest covers --raw on all show commands (7 tests)
  - artefact: VT-003
    kind: VT
    requirement: PROD-013.FR-003
    status: verified
    notes: view_test.py - 16 tests covering pager resolution and invocation
  - artefact: VT-004
    kind: VT
    requirement: PROD-013.FR-004
    status: verified
    notes: edit_test.py - 11 tests covering editor resolution and invocation
  - artefact: VT-005
    kind: VT
    requirement: PROD-013.FR-005
    status: verified
    notes: find_test.py - 13 tests covering find subcommands for all artifact types
  - artefact: VT-006
    kind: VT
    requirement: PROD-013.FR-006
    status: verified
    notes: show_test.py - ShowCardJsonFlagTest covers --json on show card
  - artefact: VT-007
    kind: VT
    requirement: PROD-013.FR-007
    status: verified
    notes: show_test.py - JSON output tests verify path field present
```

## 1. Intent & Summary

- **Problem / Purpose**: Users cannot easily view or edit artifact files by ID. Current workflow requires manually navigating to `specify/decisions/ADR-001-*.md` or similar paths. The `show` command outputs formatted metadata, not file content or paths.

- **Value Signals**:
  - Reduced friction: `spec-driver edit adr 001` vs manual path lookup
  - Shell composability: `$EDITOR $(spec-driver show adr 001 --path)`
  - Consistency: same flags work across all artifact types

- **Guiding Principles**:
  - Unix philosophy: small tools that compose well
  - Least surprise: flags work the same everywhere
  - Progressive disclosure: simple defaults, power via flags

- **Change History**: Initial specification based on CLI audit.

## 2. Stakeholders & Journeys

### Personas / Actors

**Developer (Human)**
- Goals: Quickly view/edit specs, ADRs, deltas without path lookup
- Pains: Remembering file paths; inconsistent CLI flags
- Expectations: `spec-driver edit adr 001` just works

**AI Agent**
- Goals: Retrieve artifact paths for file operations
- Pains: Must parse formatted output or guess paths
- Expectations: `--path` or `--json` gives structured data

### Primary Journeys / Flows

**Journey 1: Quick Edit**
```
GIVEN developer wants to edit ADR-012
WHEN runs `spec-driver edit adr 012`
THEN $EDITOR opens with the ADR file
AND developer can immediately edit
```

**Journey 2: Shell Composition**
```
GIVEN developer wants to grep an ADR
WHEN runs `spec-driver show adr 012 --raw | grep -i 'decision'`
THEN sees matching lines from the raw file
```

**Journey 3: Agent Path Lookup**
```
GIVEN agent needs file path for SPEC-009
WHEN runs `spec-driver show spec SPEC-009 --path`
THEN receives single line: specify/tech/SPEC-009/SPEC-009.md
AND can use path for file operations
```

### Edge Cases & Non-goals

**Non-goals:**
- GUI/TUI interfaces (terminal-only)
- Multi-file artifacts (return primary file only for --path)
- Creating new artifacts (handled by `create` command)

**Edge Cases:**
- Missing $EDITOR/$PAGER: fall back to sensible defaults
- Artifact not found: clear error message with suggestions
- Multiple files match (delta bundles): return primary file

## 3. Responsibilities & Requirements

### Capability Overview

See `supekku:spec.capabilities@v1` block above.

### Functional Requirements

- **FR-001**: All `show` subcommands MUST support `--path` flag that outputs only the file path
  *Verification*: VT-001 - Test on all show subcommands

- **FR-002**: All `show` subcommands MUST support `--raw` flag that outputs raw file content
  *Verification*: VT-002 - Test raw output matches file content

- **FR-003**: System MUST provide `view` command that opens artifact in `$PAGER` (fallback: less, more)
  *Verification*: VT-003 - Test pager invocation

- **FR-004**: System MUST provide `edit` command that opens artifact in `$EDITOR` (fallback: $VISUAL, vi)
  *Verification*: VT-004 - Test editor invocation

- **FR-005**: `find` command MUST support all artifact types (spec, delta, adr, revision, requirement, policy, standard), not just card
  *Verification*: VT-005 - Test find subcommands exist and work

- **FR-006**: All `show` subcommands MUST support `--json` flag for structured output
  *Verification*: VT-006 - Test --json on show card (currently missing)

- **FR-007**: `--json` output MUST include `path` field for all artifacts
  *Verification*: VT-006 - Verify path in JSON output

### Non-Functional Requirements

- **NF-001**: Path resolution MUST complete in <100ms for any artifact
  *Measurement*: Timing tests on cold cache

- **NF-002**: CLI flag names MUST be consistent across all artifact types
  *Measurement*: Automated flag audit

### Success Metrics / Signals

- **Adoption**: Users can view/edit artifacts without manual path lookup
- **Consistency**: Zero flag gaps between artifact types (audit passes)

## 4. Solution Outline

### User Experience / Outcomes

**New Commands:**
```bash
# View artifact in pager
spec-driver view adr ADR-012
spec-driver view spec SPEC-009
spec-driver view delta DE-005

# Edit artifact in editor
spec-driver edit adr ADR-012
spec-driver edit spec SPEC-009
spec-driver edit delta DE-005
```

**New Flags on `show`:**
```bash
# Output path only (composable)
spec-driver show adr ADR-012 --path
# Output: specify/decisions/ADR-012-some-title.md

# Output raw content
spec-driver show adr ADR-012 --raw
# Output: (full file content)

# JSON includes path
spec-driver show adr ADR-012 --json
# Output: {"id": "ADR-012", ..., "path": "specify/decisions/ADR-012-some-title.md"}
```

**Extended `find`:**
```bash
# Find files for any artifact type
spec-driver find spec SPEC-009
spec-driver find adr ADR-012
spec-driver find delta DE-005
```

### Data & Contracts

Path resolution uses existing registry infrastructure. Each artifact type's registry knows file locations.

## 5. Behaviour & Scenarios

### Primary Flows

**Flow 1: show --path**
1. User runs `spec-driver show adr ADR-012 --path`
2. System loads decision registry
3. Finds ADR-012 entry
4. Outputs path from registry metadata
5. Exit 0

**Flow 2: view command**
1. User runs `spec-driver view adr ADR-012`
2. System resolves path (as above)
3. Reads $PAGER (fallback: less, more)
4. Executes: `$PAGER <path>`
5. Pager displays file

**Flow 3: edit command**
1. User runs `spec-driver edit adr ADR-012`
2. System resolves path
3. Reads $EDITOR (fallback: $VISUAL, vi)
4. Executes: `$EDITOR <path>`
5. Editor opens file

### Error Handling / Guards

- **Artifact not found**: `Error: ADR-012 not found. Did you mean ADR-001?`
- **No pager available**: `Error: No pager found. Set $PAGER or install less.`
- **No editor available**: `Error: No editor found. Set $EDITOR or install vi.`

## 6. Quality & Verification

### Testing Strategy

- Unit tests for path resolution
- Integration tests for view/edit (mock $EDITOR/$PAGER)
- CLI flag consistency audit (automated)

### Acceptance Gates

- [ ] All FR verified via VT suite
- [ ] Flag audit shows no gaps
- [ ] Documentation updated

## 7. Backlog Hooks & Dependencies

### CLI Flag Audit (Current State)

**show subcommands:**
| Command | --json | --path | --raw | --root | Other |
|---------|--------|--------|-------|--------|-------|
| spec | ✓ | ✗ | ✗ | ✓ | |
| delta | ✓ | ✗ | ✗ | ✓ | |
| revision | ✓ | ✗ | ✗ | ✓ | |
| requirement | ✓ | ✗ | ✗ | ✓ | |
| adr | ✓ | ✗ | ✗ | ✓ | |
| policy | ✓ | ✗ | ✗ | ✓ | |
| standard | ✓ | ✗ | ✗ | ✓ | |
| card | ✗ | ✓ (-q) | ✗ | ✓ | -a/--anywhere |

**Gaps identified:**
- `show card` missing `--json`
- All show commands missing `--path` (except card has `-q`)
- All show commands missing `--raw`

**list subcommands:**
| Command | --json | --format | --truncate | --regexp | --paths |
|---------|--------|----------|------------|----------|---------|
| specs | ✓ | ✓ | ✓ | ✓ | ✓ |
| deltas | ✓ | ✓ | ✓ | ✓ | ✗ |
| changes | ✓ | ✓ | ✓ | ✓ | ✓ |
| adrs | ✓ | ✓ | ✓ | ✓ | ✗ |
| requirements | ✓ | ✓ | ✓ | ✓ | ✗ |
| cards | ✓ | ✓ | ✗ | ✗ | ✗ |
| policies | ✓ | ✓ | ✓ | ✓ | ✗ |
| standards | ✓ | ✓ | ✓ | ✓ | ✗ |

**Gaps identified:**
- `list cards` missing `--truncate`, `--regexp`
- Several list commands missing `--paths`

### Implementation Order

1. **Phase 1**: Add `--path` flag to all `show` subcommands
2. **Phase 2**: Add `view` and `edit` commands
3. **Phase 3**: Extend `find` to all artifact types
4. **Phase 4**: Flag consistency cleanup (`--json` on card, `--paths` on list commands)

### Open Decisions

**Q1: Relative vs Absolute Paths**
- Current: Most paths are relative to repo root
- Proposal: Keep relative, add `--absolute` flag if needed
- Status: Use relative paths (consistent with existing behavior)

**Q2: Multi-file Artifacts**
- Delta bundles contain multiple files (DE-xxx.md, DR-xxx.md, IP-xxx.md, phases/)
- Proposal: `--path` returns primary file (DE-xxx.md); `find` returns all files
- Status: Needs confirmation
