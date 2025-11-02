---
id: PROD-007
slug: agent-tech-spec-backfill
name: Agent tech spec backfill
created: '2025-11-02'
updated: '2025-11-02'
status: draft
kind: prod
aliases: []
relations: []
guiding_principles: []
assumptions: []
---

# PROD-007 – agent tech spec backfill

```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: PROD-007
requirements:
  primary:
    - PROD-007.FR-001
    - PROD-007.FR-002
    - PROD-007.FR-003
    - PROD-007.FR-004
    - PROD-007.NF-001
    - PROD-007.NF-002
  collaborators:
    - PROD-001.FR-001
    - PROD-001.FR-002
interactions:
  - with: PROD-001
    nature: Extends spec creation workflow to handle completion of existing/incomplete specs (addresses RISK-007)
```

```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: PROD-007
capabilities:
  - id: effortless-completion
    name: Effortless Spec Completion
    responsibilities:
      - Enable users to complete placeholder specs without manual YAML editing
      - Guide through completion workflow with minimal questions
      - Preserve any manually-created content
    requirements:
      - PROD-007.FR-001
      - PROD-007.FR-002
      - PROD-007.NF-002
    summary: >-
      Users can transform auto-generated placeholder specs into complete,
      detailed specifications through a guided agent workflow that asks minimal
      questions and leverages existing code documentation for context.
    success_criteria:
      - Users complete placeholder specs without external documentation
      - Zero manual YAML block editing required
      - Manually-created content never overwritten
  - id: bulk-elevation
    name: Bulk Spec Elevation
    responsibilities:
      - Support completing multiple specs in one workflow
      - Provide progress visibility during batch operations
      - Handle errors gracefully without halting entire batch
    requirements:
      - PROD-007.FR-003
      - PROD-007.FR-004
      - PROD-007.NF-001
    summary: >-
      Teams can elevate all auto-generated placeholder specs (10s or 100s) in
      a single workflow, with clear progress reporting and configurable speed
      vs. control tradeoffs.
    success_criteria:
      - Batch operations show clear progress indicators
      - Errors in one spec don't halt batch
      - Users can choose interactive vs. automated modes
```

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: PROD-007
entries:
  - artefact: VT-001
    kind: VT
    requirement: PROD-007.FR-001
    status: planned
    notes: Test agent workflow completes existing spec without manual YAML editing
  - artefact: VT-002
    kind: VT
    requirement: PROD-007.FR-002
    status: planned
    notes: Test manual content preservation during completion workflow
  - artefact: VT-003
    kind: VT
    requirement: PROD-007.FR-003
    status: planned
    notes: Test batch workflow completes multiple specs with progress reporting
  - artefact: VA-001
    kind: VA
    requirement: PROD-007.NF-001
    status: planned
    notes: User testing with 10 users completing batch of 5-10 placeholder specs
  - artefact: VA-002
    kind: VA
    requirement: PROD-007.NF-002
    status: planned
    notes: Track question count across 50 spec completion sessions
```

## 1. Intent & Summary

- **Problem / Purpose**: After running `spec-driver sync`, users have dozens or hundreds of auto-generated placeholder specs that need to be elevated into detailed, useful documentation. Manually completing these specs is tedious, error-prone, and requires deep knowledge of YAML schemas, spec-driver conventions, and documentation structure. This creates a barrier preventing teams from achieving comprehensive spec coverage across their codebase, undermining the value of spec-driven development.

- **Value Signals**:
  - **Coverage**: Enable teams to achieve 80%+ spec coverage across codebase (currently <20% due to manual effort)
  - **Efficiency**: Reduce time to complete a spec from 2+ hours (manual) to <10 minutes (agent-assisted)
  - **Quality**: Maintain high spec quality through guided workflows and validation
  - **Adoption**: Lower barrier for teams to adopt spec-driven development practices

- **Guiding Principles**:
  - **Preserve human work**: Never overwrite manually-created content
  - **Leverage existing docs**: Use auto-generated code documentation (contracts) as primary context source
  - **Minimize questions**: Ask only critical questions; make informed assumptions for the rest
  - **Batch-friendly**: Support both single-spec (interactive) and bulk (automated) workflows
  - **Progress transparency**: Always show what's happening during long operations
  - **Fail gracefully**: One bad spec shouldn't block completing the other 99

- **Change History**:
  - 2025-11-02: Initial draft addressing PROD-001/RISK-007 (no completion workflow)

## 2. Stakeholders & Journeys

### Personas / Actors

**Team Lead (Marcus)** - Managing codebase with 50+ packages
- **Goals**: Complete all auto-generated specs to establish baseline documentation
- **Pains**: Manual completion too time-consuming; inconsistent quality across team
- **Expectations**: Bulk operation that handles 50 specs in reasonable time (<30 min); can review/adjust after

**Solo Developer (Sarah)** - Working on OSS project
- **Goals**: Document the 5 new packages she just added
- **Pains**: Forgets YAML syntax between sessions; wants guidance not manual work
- **Expectations**: Interactive workflow that asks her key questions, fills in technical details automatically

### Primary Journeys / Flows

**Journey 1: Solo developer elevates single spec**

Given Sarah ran `spec-driver sync` and has placeholder spec SPEC-042 for her new `auth` package
1. Sarah types `/supekku.elevate SPEC-042`
2. Agent reads existing placeholder spec
3. Agent reads auto-generated contracts (API documentation) for `auth` package
4. Agent asks 2 questions: "Should this document internal helpers or only public API?" and "Any security considerations beyond standard auth?"
5. Sarah answers: "Only public API" and "Yes, supports MFA"
6. Agent fills all 7 sections using contracts + Sarah's answers
7. Agent validates, runs sync
8. Sarah reviews completed spec: "SPEC-042 complete; 3 classes, 12 functions documented"

Then Sarah has complete spec ready to reference during development
And she didn't manually edit any YAML

**Journey 2: Team lead batch-elevates 50 specs**

Given Marcus has 50 placeholder specs from recent sync operation
1. Marcus types `/supekku.elevate --batch "specify/tech/SPEC-*.md"`
2. Agent discovers 50 incomplete specs
3. Agent asks: "Interactive or automated mode?"
4. Marcus chooses: "Automated - use contracts and make reasonable assumptions"
5. Agent shows: "Processing 50 specs... 10/50 complete... 25/50 complete..."
6. After 15 minutes: "47/50 completed; 3 failed (contracts missing)"
7. Marcus reviews summary, addresses 3 failures individually

Then Marcus has 47 specs elevated automatically
And can focus manual effort on the 3 edge cases

### Edge Cases & Non-goals

**Edge Cases**:
- Spec has partial manual content → preserve it, complete only placeholders
- Contracts missing for package → complete with limited context, mark for review
- User wants to restart failed batch → support resuming from failures

**Non-goals**:
- Creating new specs from scratch (PROD-001 handles this)
- Editing arbitrary spec content (use text editor)
- Real-time collaboration (out of scope)

## 3. Responsibilities & Requirements

### Capability Overview

**Effortless Spec Completion** enables users to elevate placeholder specs through a guided workflow that asks minimal questions, uses existing code documentation (contracts) for context, and preserves any manually-created content.

**Bulk Spec Elevation** supports batch operations across multiple specs with progress reporting, error isolation, and configurable automation levels (interactive vs. automated).

### Functional Requirements

- **FR-001**: Users MUST be able to complete placeholder specs through guided agent workflow
  Agent command reads existing spec, identifies incomplete sections, uses contracts for context, asks clarifying questions (≤3), fills sections, validates, and reports completion status.
  *Verification*: VT-001 - End-to-end workflow test with real placeholder spec

- **FR-002**: System MUST preserve manually-created spec content during completion
  Detection logic identifies human-written vs. placeholder text; only placeholder sections are modified.
  *Verification*: VT-002 - Test with partially-completed spec; verify manual content unchanged

- **FR-003**: Users MUST be able to complete multiple specs in batch mode
  Support glob pattern matching for multi-spec selection; show progress indicators; continue on errors.
  *Verification*: VT-003 - Batch workflow with 10 specs, 2 intentional failures

- **FR-004**: Users MUST be able to choose automation level for batch operations
  Interactive mode (ask questions per spec) vs. automated mode (infer from contracts, make assumptions).
  *Verification*: VT-003 - Test both modes with same batch

### Non-Functional Requirements

- **NF-001**: Batch operations MUST show clear progress and complete in reasonable time
  10 specs in <15 minutes (automated mode); 50 specs in <30 minutes acceptable.
  *Measurement*: VA-001 - User testing with real batches of 5-50 specs

- **NF-002**: Interactive mode MUST minimize user questions
  ≤3 questions per spec for typical cases; more allowed for complex edge cases if user opts in.
  *Measurement*: VA-002 - Track question count across 50 completion sessions

### Success Metrics / Signals

- **Adoption**: 70%+ of placeholder specs elevated within 2 weeks of feature launch
- **Efficiency**: Average completion time <10 minutes per spec (vs. 2+ hours manual)
- **Quality**: 90%+ of elevated specs pass validation on first attempt
- **User satisfaction**: 80%+ report "would recommend" in post-use survey

## 4. Solution Outline

### User Experience / Outcomes

**Desired Behaviors**:
- User types single command (`/supekku.elevate SPEC-123`) and receives completed spec
- Agent shows what it's doing: "Reading contracts... Analyzing 3 classes... Filling Section 3..."
- Questions are focused and easy to answer: "Public API only or include internals?"
- Batch mode shows progress: "Completed 15/50 specs (3 failed - contracts missing)"
- Errors are clear and actionable: "SPEC-042 failed: contracts directory not found. Run sync first."

**Acceptance Notes**:
- Zero manual YAML editing required
- User doesn't need to remember spec-driver conventions
- Batch failures don't lose progress on successful specs
- Can pause and resume batch operations

### Data & Contracts

**Key Entities**:
- Placeholder spec: Auto-generated spec with template boilerplate, no real content
- Contracts: AST-generated API documentation (functions, classes, types) in `contracts/` directory
- Completion status: pending, in_progress, completed, failed

**User-Facing Interactions**:
- Command: `/supekku.elevate <spec-id>` or `/supekku.elevate --batch <pattern>`
- Progress indicators: "3/10 complete..."
- Completion report: Summary of successes/failures with actionable next steps

## 5. Behaviour & Scenarios

### Primary Flows

See Section 2 (Stakeholders & Journeys) for detailed user flows.

### Error Handling / Guards

- **Contracts missing**: Complete with limited context, mark spec for manual review
- **Partial manual content**: Preserve it, only fill placeholder sections
- **Validation failure**: Report specific errors, allow retry or manual fix
- **Batch interrupted**: Save progress, allow resume from failures

## 6. Quality & Verification

### Testing Strategy

- VT-001 → FR-001: End-to-end workflow test
- VT-002 → FR-002: Manual content preservation test
- VT-003 → FR-003, FR-004: Batch mode with different automation levels
- VA-001 → NF-001: Performance/timing with real batches
- VA-002 → NF-002: Question count tracking

### Research / Validation

**Hypothesis 1**: Users prefer automated batch mode over interactive for 10+ specs
- **Test**: A/B test with 20 users completing 15-spec batch
- **Metric**: Mode preference, completion time, satisfaction score

**Hypothesis 2**: Contract-based completion produces acceptable quality
- **Test**: Compare agent-completed vs. manually-completed specs
- **Metric**: Completeness score, validation success rate, reviewer feedback

### Observability & Analysis

- Completion success rate (overall and per-batch)
- Average questions asked per spec
- Time per spec (interactive vs. automated)
- Failure categories (contracts missing, validation errors, etc.)

### Acceptance Gates

1. VT-001, VT-002, VT-003 passing (all functional requirements verified)
2. VA-001: Batch performance within targets (10 specs <15min, 50 specs <30min)
3. VA-002: Question count ≤3 per spec in 80%+ of cases
4. Real-world validation: 5 users successfully elevate batches of 10+ specs

## 7. Backlog Hooks & Dependencies

### Related Specs / PROD

- **PROD-001** (streamline spec creation): Extends with completion workflow; addresses RISK-007
- Future tech spec will define implementation details (CLI commands, detection logic, etc.)

### Risks & Mitigations

**RISK-001**: Contract quality varies; completion quality suffers
- **Likelihood**: Medium (contracts are auto-generated, quality depends on code)
- **Impact**: Medium (specs incomplete or inaccurate)
- **Mitigation**: Mark low-confidence sections for review; allow manual override

**RISK-002**: Users expect perfect AI completion; disappointed by limitations
- **Likelihood**: High (AI hype sets unrealistic expectations)
- **Impact**: Low (feature still useful despite limitations)
- **Mitigation**: Clear documentation of capabilities/limits; mark assumptions in specs

**RISK-003**: Batch mode overwrites manual work due to detection bugs
- **Likelihood**: Low (conservative detection logic)
- **Impact**: Critical (data loss)
- **Mitigation**: Dry-run mode; comprehensive tests; err on side of preservation

### Known Gaps / Debt

- No agent command `/supekku.elevate` exists yet (needs creation)
- Detection logic for manual vs. placeholder content undefined
- CLI batch mode not yet implemented
- Performance characteristics unknown (need benchmarking)

### Open Decisions / Questions

**Decision 1**: Default to interactive or automated for batch mode?
- **Options**: (A) Interactive (safer), (B) Automated (faster)
- **Leaning**: A (interactive) with clear option to switch

**Decision 2**: How to handle incomplete contracts (some functions missing docs)?
- **Options**: (A) Mark spec incomplete, (B) Complete with available info + note gaps
- **Leaning**: B (partial completion better than none)

## Appendices

### Glossary

- **Placeholder spec**: Auto-generated spec with template boilerplate, minimal useful content
- **Contracts**: Deterministic API documentation generated from code AST
- **Elevation**: Process of transforming placeholder spec into complete, detailed specification
