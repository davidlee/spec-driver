---
id: PROD-006
slug: phase-management
name: Phase Management
created: '2025-11-02'
updated: '2025-11-02'
status: draft
kind: prod
aliases: []
relations: []
guiding_principles:
  - Phases organize implementation work into manageable, verifiable chunks
  - Sequential execution with clear gates reduces risk and enables progress tracking
  - Automation should reduce toil while preserving human oversight of critical transitions
assumptions:
  - Implementation plans are created before phases
  - Phases are primarily created sequentially as work progresses
  - Phase templates provide consistent structure across different delta types
  - Developers work on one phase at a time per implementation plan
---

# PROD-006 – Phase Management

```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: PROD-006
requirements:
  primary:
    - PROD-006.FR-001
    - PROD-006.FR-002
    - PROD-006.FR-003
    - PROD-006.FR-004
    - PROD-006.FR-005
    - PROD-006.NF-001
    - PROD-006.NF-002
  collaborators: []
interactions:
  - with: PROD-005
    nature: Verification artifacts link to phases for execution tracking
```

```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: PROD-006
capabilities:
  - id: phase-creation
    name: Phase Creation and Templating
    responsibilities:
      - Generate phase documents from templates with correct frontmatter
      - Auto-populate phase metadata (ID, plan, delta relationships)
      - Support sequential phase numbering within plans
      - Provide consistent structure across phase documents
    requirements:
      - PROD-006.FR-001
      - PROD-006.FR-002
      - PROD-006.NF-001
    summary: >-
      Enables developers to create phase documents with correct metadata structure,
      automated ID sequencing, and template-driven consistency. Reduces manual
      toil and ensures phases are properly linked to their implementation plans
      and parent deltas.
    success_criteria:
      - Phase created with single command and minimal input
      - Phase IDs follow convention (IP-XXX.PHASE-NN)
      - Frontmatter schema validates successfully
      - Template provides complete structure with examples

  - id: phase-visibility
    name: Phase Visibility and Navigation
    responsibilities:
      - Display phase details within delta context
      - Show phase progression and status
      - Link phases to verification artifacts
      - Provide clear phase objectives and criteria
    requirements:
      - PROD-006.FR-003
      - PROD-006.FR-004
      - PROD-006.NF-002
    summary: >-
      Surfaces phase information through enhanced delta display commands,
      enabling developers to understand execution status, navigate between
      phases, and track verification progress without manually reading
      multiple markdown files.
    success_criteria:
      - Delta display shows all phases with objectives
      - Phase entrance/exit criteria visible
      - Verification artifacts linked to specific phases
      - Clear indication of current/active phase

  - id: phase-metadata-validation
    name: Phase Metadata Validation
    responsibilities:
      - Validate phase.overview schema structure
      - Ensure phase-plan-delta relationships are consistent
      - Verify phase numbering is sequential
      - Detect orphaned or malformed phases
    requirements:
      - PROD-006.FR-005
      - PROD-006.NF-001
    summary: >-
      Maintains metadata integrity through schema validation and relationship
      checks. Prevents inconsistent phase structures that could break tooling
      or create confusion about execution state.
    success_criteria:
      - Invalid phase.overview blocks rejected at sync time
      - Broken phase-plan-delta links detected and reported
      - Duplicate phase IDs flagged
      - Non-sequential phase numbering warned
```

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: PROD-006
entries:
  - artefact: VT-PHASE-001
    kind: VT
    requirement: PROD-006.FR-001
    status: planned
    notes: Unit tests for phase creation with various plan/delta contexts

  - artefact: VT-PHASE-002
    kind: VT
    requirement: PROD-006.FR-002
    status: planned
    notes: Integration test for phase metadata population and sequencing

  - artefact: VT-PHASE-003
    kind: VT
    requirement: PROD-006.FR-003
    status: planned
    notes: Formatter tests for enhanced delta display with phases

  - artefact: VT-PHASE-004
    kind: VT
    requirement: PROD-006.FR-004
    status: planned
    notes: E2E test for phase navigation workflow

  - artefact: VT-PHASE-005
    kind: VT
    requirement: PROD-006.FR-005
    status: planned
    notes: Schema validation tests for phase.overview frontmatter

  - artefact: VA-PHASE-001
    kind: VA
    requirement: PROD-006.NF-001
    status: planned
    notes: Design review of phase metadata schema extensibility

  - artefact: VA-PHASE-002
    kind: VA
    requirement: PROD-006.NF-002
    status: planned
    notes: UX review of delta display with phase information
```

## 1. Intent & Summary

**Problem / Purpose**:
Implementation plans decompose deltas into execution phases, but currently phases must be created manually by copying templates, filling metadata, and ensuring consistency. There's no tooling to create phases, no command to view phase details, and enhanced delta display doesn't show phase information effectively.

**Value Signals**:
- Reduce phase creation time from ~5 minutes to <30 seconds
- Eliminate metadata errors in phase frontmatter
- Enable quick assessment of implementation progress via `show delta`
- Provide foundation for future phase status tracking and gate automation

**Guiding Principles**:
- **Sequential simplicity**: Phases created one at a time as work progresses, not batch-created upfront
- **Automation where valuable**: Auto-populate boilerplate (IDs, relationships), but preserve human control over objectives and criteria
- **Progressive disclosure**: Basic `create phase` now, advanced status management later
- **Consistency through templates**: Single source of truth for phase structure

**Change History**:
- Initial spec created 2025-11-02 based on DE-002 implementation experience
- Identified need during manual creation of IP-002.PHASE-01

## 2. Stakeholders & Journeys

**Personas / Actors**:

1. **Solo Developer** (primary)
   - Goals: Create phases quickly, track progress, minimize context switching
   - Pains: Manual metadata entry, forgetting template structure, checking phase numbering
   - Expectations: One command to create phase, clear display of what's done/next

2. **AI Agent / Assistant** (secondary)
   - Goals: Follow structured workflow, update phase documents, report progress
   - Pains: Parsing phase structure from markdown, determining next phase number
   - Expectations: Machine-readable phase info, clear validation feedback

**Primary Journeys / Flows**:

### Journey 1: Creating First Phase
```
GIVEN implementation plan IP-002 exists with phases listed in frontmatter
WHEN developer runs `create phase "Phase 01 - Foundation" --plan IP-002`
THEN
  - System creates `change/deltas/DE-002-.../phases/phase-01.md`
  - Frontmatter populated with:
    - phase: IP-002.PHASE-01
    - plan: IP-002
    - delta: DE-002 (from plan)
    - name: "Phase 01 - Foundation"
  - Template sections rendered with examples
  - Confirmation shows file path and phase ID
```

### Journey 2: Creating Sequential Phase
```
GIVEN phase-01.md already exists for IP-002
WHEN developer runs `create phase "Phase 02 - Migration" --plan IP-002`
THEN
  - System detects existing phases, determines next number is 02
  - Creates phase-02.md with auto-incremented ID
  - Links to same plan and delta as previous phases
```

### Journey 3: Viewing Delta with Phases
```
GIVEN IP-002 has 3 phases defined
WHEN developer runs `show delta DE-002`
THEN display shows:
  - Delta basics (id, name, status)
  - Plan: IP-002 (3 phases)
  - For each phase:
    - Phase ID and name
    - Objective (truncated to ~80 chars)
    - Status if tracked
  - File path to delta document
```

**Edge Cases & Non-goals**:

**Edge Cases**:
- Creating phase for plan with no existing phases → starts at PHASE-01
- Plan frontmatter lists phases but files don't exist → warning, proceed
- Phase numbering gaps (01, 03 missing 02) → allow but warn
- Multiple deltas with same plan → error, ambiguous context

**Non-goals** (for MVP):
- Phase status state machine (planned → in-progress → complete)
- Automatic phase creation from plan frontmatter
- Phase templates by type (foundation, migration, verification)
- Gate validation (entrance criteria checking)
- Phase reordering or renumbering
- Deleting or archiving phases
- List/filter phases across all plans

## 3. Responsibilities & Requirements

### Capability Overview

**Phase Creation and Templating** ensures developers can quickly scaffold phase documents with correct metadata. The system handles ID sequencing, relationship linking, and template rendering, reducing manual work and preventing metadata inconsistencies.

**Phase Visibility and Navigation** makes phase information accessible through enhanced delta display. Developers see execution structure at a glance without navigating directory trees or reading multiple files.

**Phase Metadata Validation** maintains schema compliance and relationship integrity. The sync process catches malformed frontmatter or broken links before they cause tooling failures.

### Functional Requirements

- **FR-001**: System MUST create phase markdown files from template with valid `phase.overview` frontmatter block
  *Verification*: VT-PHASE-001 - Create phase with various plan contexts, validate schema

- **FR-002**: System MUST automatically determine next phase number by examining existing phases for the given plan
  *Verification*: VT-PHASE-002 - Create phases 01-03 sequentially, verify numbering

- **FR-003**: System MUST enhance delta display to show plan ID, phase count, and phase summaries with objectives
  *Verification*: VT-PHASE-003 - Test formatter output matches expected structure

- **FR-004**: System MUST auto-populate phase metadata including phase ID, plan ID, and delta ID from plan context
  *Verification*: VT-PHASE-004 - Verify frontmatter contains correct relationship IDs

- **FR-005**: System MUST validate phase.overview schema during sync and report validation errors
  *Verification*: VT-PHASE-005 - Test sync with malformed phase frontmatter

### Non-Functional Requirements

- **NF-001**: Phase creation command MUST complete in <2 seconds for plans with up to 20 existing phases
  *Measurement*: VA-PHASE-001 - Benchmark phase creation performance

- **NF-002**: Delta display MUST remain readable with up to 10 phases without truncation loss of critical information
  *Measurement*: VA-PHASE-002 - UX review of delta display with varying phase counts

### Success Metrics / Signals

- **Adoption**: 100% of new phases created via command (not manual copying)
- **Quality**: Zero phase metadata validation errors in production deltas
- **Developer Experience**: Phase creation time reduced from 5 min → 30 sec
- **Visibility**: Developers use `show delta` to check phase status instead of reading files

## 4. Solution Outline

### User Experience / Outcomes

**Creating a Phase**:
```bash
$ spec-driver create phase "Phase 01 - Foundation" --plan IP-002

Phase created: IP-002.PHASE-01
change/deltas/DE-002-python-package-level-spec-granularity/phases/phase-01.md
```

**Viewing Delta with Phases** (enhanced output):
```
Delta: DE-002
Name: Delta - Python package-level spec granularity
Status: draft
Kind: delta

Applies To:
  Specs: PROD-005
  Requirements:
    - PROD-005.FR-001
    - PROD-005.FR-002

Plan: IP-002 (3 phases)
  Phase 01 - Foundation: Implement package detection logic, validate deterministic...
  Phase 02 - Migration: Delete file-level specs, generate package-level specs...
  Phase 03 - Verification: Complete verification testing (VT-003, VT-004)...

Relations:
  - : PROD-005

File: change/deltas/DE-002-.../DE-002.md
```

**Desired Behaviors**:
1. Developer discovers plan needs phases
2. Runs `create phase` with name and plan ID
3. System creates file, populates metadata, confirms success
4. Developer edits phase document to add criteria/tasks
5. Later uses `show delta` to review all phases at a glance

### Data & Contracts

**Phase Document Structure** (`phases/phase-NN.md`):
```yaml
schema: supekku.phase.overview
version: 1
phase: IP-XXX.PHASE-NN         # Auto-generated
plan: IP-XXX                    # From --plan flag
delta: DE-XXX                   # Looked up from plan
name: "Phase NN - <Name>"       # From positional arg
objective: >-
  <Filled by developer>         # Template placeholder
entrance_criteria: []           # Template placeholder
exit_criteria: []               # Template placeholder
```

**Plan Frontmatter** (`IP-XXX.md`):
```yaml
schema: supekku.plan.overview
version: 1
plan: IP-XXX
delta: DE-XXX
phases:
  - id: IP-XXX.PHASE-01
    name: Phase 01 - Foundation
    objective: >-
      Brief objective statement
    entrance_criteria: [...]
    exit_criteria: [...]
```

**Enhanced Delta Display** (formatter output):
- Plan section expands to show phase summaries
- Objective truncated to ~80 chars for readability
- Phase IDs clickable/copyable for navigation

## 5. Behaviour & Scenarios

### Primary Flows

**Flow 1: Create First Phase**
1. Developer identifies plan ID from delta (e.g., `IP-002` in `DE-002.md`)
2. Runs: `spec-driver create phase "Phase 01 - Tooling" --plan IP-002`
3. System:
   - Finds plan document at `change/deltas/DE-002-.../IP-002.md`
   - Reads `delta: DE-002` from plan frontmatter
   - Checks `phases/` directory → empty, start numbering at 01
   - Renders template with:
     - `phase: IP-002.PHASE-01`
     - `plan: IP-002`
     - `delta: DE-002`
     - `name: Phase 01 - Tooling`
   - Writes `phases/phase-01.md`
4. Outputs: "Phase created: IP-002.PHASE-01" + file path
5. Developer edits phase file to add objectives, criteria, tasks

**Flow 2: Create Sequential Phase**
1. Developer completes Phase 01, ready for Phase 02
2. Runs: `spec-driver create phase "Phase 02 - Migration" --plan IP-002`
3. System:
   - Scans `phases/` directory
   - Finds `phase-01.md` with `phase: IP-002.PHASE-01`
   - Increments to PHASE-02
   - Creates `phase-02.md` with updated metadata
4. Developer continues workflow

**Flow 3: View Delta to Check Progress**
1. Developer runs: `spec-driver show delta DE-002`
2. System:
   - Loads delta from registry
   - Finds plan `IP-002` referenced in frontmatter
   - Reads plan frontmatter for `phases[]` array
   - Formats each phase: ID + truncated objective
3. Displays enhanced output with all phases
4. Developer sees what's been planned, what's next

### Error Handling / Guards

**Error: Plan Not Found**
```bash
$ spec-driver create phase "Phase 01" --plan IP-999
Error: Implementation plan not found: IP-999
```

**Error: Invalid Phase Name**
```bash
$ spec-driver create phase "" --plan IP-002
Error: Phase name is required
```

**Warning: Numbering Gap**
```bash
$ spec-driver create phase "Phase 03" --plan IP-002
Warning: Gaps detected in phase numbering (found: 01, creating: 03)
Phase created: IP-002.PHASE-03
```

**Error: Missing Delta in Plan**
```bash
# If IP-002.md has malformed frontmatter without delta field
Error: Plan IP-002 does not specify delta ID in frontmatter
```

**Graceful: No Phases in Plan**
```bash
$ spec-driver show delta DE-002
# If plan exists but has no phases
Plan: IP-002 (0 phases)
```

## 6. Quality & Verification

### Testing Strategy

**Unit Tests** (VT-PHASE-001, VT-PHASE-002):
- `test_create_phase_first_in_sequence()` → phase-01.md created
- `test_create_phase_auto_increment()` → phase-02, phase-03 numbered correctly
- `test_phase_metadata_population()` → frontmatter has plan, delta, phase IDs
- `test_invalid_plan_id()` → error raised
- `test_empty_phase_name()` → error raised

**Integration Tests** (VT-PHASE-003):
- `test_phase_template_rendering()` → all sections present with placeholders
- `test_schema_validation_on_sync()` → malformed phase rejected
- `test_formatter_delta_with_phases()` → output includes phase summaries

**E2E Tests** (VT-PHASE-004):
- Create plan → create 3 phases → show delta → verify all phases displayed
- Create phase with gaps → warning shown but creation succeeds

### Research / Validation

**UX Validation** (VA-PHASE-002):
- Present delta display with 1, 3, 5, 10 phases to developer
- Verify readability and information scannability
- Confirm truncation strategy preserves key objective info

### Observability & Analysis

**Metrics**:
- Phase creation command usage (count per week)
- Validation errors per phase created (target: <1%)
- `show delta` invocations (indicator of adoption)

**Telemetry** (future):
- Phase count distribution across deltas
- Average time between phase creations (workflow velocity)

### Security & Compliance

- No sensitive data in phase documents (public repo)
- File system paths validated to prevent directory traversal
- Template rendering escapes user input to prevent injection

### Verification Coverage

See `supekku:verification.coverage@v1` block above. All FR/NF requirements mapped to verification artifacts.

### Acceptance Gates

**MVP Launch Criteria**:
- [ ] `create phase` command implemented and tested (VT-PHASE-001, VT-PHASE-002)
- [ ] Phase metadata auto-population working (VT-PHASE-004)
- [ ] Enhanced delta display shows phases (VT-PHASE-003)
- [ ] Schema validation enforces phase.overview correctness (VT-PHASE-005)
- [ ] All tests passing (`just test`)
- [ ] Linters passing (`just lint`, `just pylint`)
- [ ] Documentation updated with phase creation examples

## 7. Backlog Hooks & Dependencies

### Related Specs / PROD

**PROD-005: Python Package-Level Spec Granularity**
- IP-002 is implementing PROD-005
- Phase verification artifacts (VT-001, VT-002) link to phases
- Demonstrates phase management capabilities in real use

### Risks & Mitigations

| Risk | Description | Likelihood | Impact | Mitigation |
|------|-------------|-----------|--------|------------|
| RISK-001 | Plan frontmatter doesn't include delta ID | Low | High | Validate during plan creation; error clearly if missing |
| RISK-002 | Phase numbering conflicts if files created manually | Medium | Low | Scan filesystem for actual phases, not just frontmatter |
| RISK-003 | Large phase counts make delta display unreadable | Low | Medium | Truncate objectives, paginate if >10 phases |
| RISK-004 | Template changes break existing phases | Low | High | Version phase.overview schema; support v1 indefinitely |

### Known Gaps / Debt

**Future Enhancements** (not blocking MVP):
- Phase status tracking (planned → in-progress → complete → verified)
- `list phases --plan IP-XXX` command for phase discovery
- Gate validation (check entrance criteria before marking in-progress)
- Phase templates by type (foundation, migration, verification, cleanup)
- Automatic plan frontmatter update when creating phases
- `show phase IP-002.PHASE-01` dedicated detail view
- Phase completion automation (update status, check exit criteria)

**Implementation Notes**:
- Phase creation should follow existing patterns in `supekku/cli/create.py`
- Formatters go in `supekku/scripts/lib/formatters/change_formatters.py`
- Phase metadata parsing in `supekku/scripts/lib/changes/blocks/`
- Template at `supekku/templates/phase.md` already exists

### Open Decisions / Questions

**Q1: Should creating a phase update plan frontmatter automatically?**
- Option A: Yes, append to `phases[]` array (requires parsing/writing YAML safely)
- Option B: No, manual sync via `spec-driver sync` (simpler, consistent with current model)
- **Recommendation**: Start with B (manual sync), evaluate A if friction too high

**Q2: Phase numbering format - zero-padded or not?**
- Current: `PHASE-01`, `PHASE-02` (two digits)
- Alternative: `PHASE-1`, `PHASE-2` (minimal digits)
- **Decision**: Keep two-digit padding for consistent sorting and readability

**Q3: Error vs warning for phase numbering gaps?**
- Could be legitimate (phase removed or merged)
- Could be accident (typo in phase name)
- **Decision**: Warn but allow, gives developer flexibility

## Appendices

### A. Phase.overview Schema Reference

See `spec-driver schema show phase.overview` for complete schema.

**Required Fields**:
- `schema`: "supekku.phase.overview"
- `version`: 1
- `phase`: Phase ID (e.g., "IP-002.PHASE-01")
- `plan`: Plan ID (e.g., "IP-002")
- `delta`: Delta ID (e.g., "DE-002")

**Optional Fields**:
- `name`: Human-readable phase name
- `objective`: What this phase achieves
- `entrance_criteria`: Array of criteria for starting
- `exit_criteria`: Array of criteria for completion
- `verification`: Object with tests[] and evidence[] arrays
- `tasks`: Array of task descriptions
- `risks`: Array of risk descriptions

### B. Existing Phase Example

See `change/deltas/DE-002-.../phases/phase-01.md` for reference implementation created manually. This spec aims to automate creation of similar documents.

### C. Related ADRs

None yet. Future ADR may be needed if phase state machine becomes complex.
