---
id: PROD-002
slug: delta-creation-workflow
name: Delta Creation Workflow
created: '2025-11-02'
updated: '2025-11-02'
status: draft
kind: prod
aliases: []
relations:
  - type: informs
    target: ADR-002
    nature: Follows proven workflow pattern from spec creation
guiding_principles:
  - Mirror PROD-001 pattern for consistency
  - Automate scaffolding
  - Guide comprehensively via agent command
  - Validate early to catch errors
  - Hybrid discovery (user input + agent suggestions)
  - Plan by default, flag to skip
assumptions:
  - Users have spec-driver installed
  - Agents can access registries for discovery
  - Projects have delta/plan/phase templates
  - Users understand delta/plan/phase artifact structure
  - Default workflow creates plan + first phase
---

# PROD-002 – Delta Creation Workflow

```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: PROD-002
requirements:
  primary:
    - PROD-002.FR-001
    - PROD-002.FR-002
    - PROD-002.FR-003
    - PROD-002.FR-004
    - PROD-002.FR-005
    - PROD-002.FR-006
    - PROD-002.NF-001
    - PROD-002.NF-002
  collaborators: []
interactions:
  - with: PROD-001
    nature: Mirrors proven spec creation workflow pattern for delta artifacts
```

```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: PROD-002
capabilities:
  - id: frictionless-delta-creation
    name: Frictionless Delta Creation
    responsibilities:
      - Guide users through complete delta creation without confusion
      - Eliminate manual file creation and YAML editing
      - Provide contextual help at every step of the workflow
    requirements:
      - PROD-002.FR-001
      - PROD-002.FR-002
      - PROD-002.NF-001
    summary: >-
      Ensures users can create complete delta artifacts (delta + plan + first phase)
      through a single guided command without needing to understand file structure
      or YAML syntax. The workflow mirrors PROD-001's proven pattern.
    success_criteria:
      - First-time users complete delta creation without external documentation
      - Zero "what do I do now?" moments during the workflow
      - Delta bundle includes all necessary artifacts with proper structure
  - id: intelligent-discovery
    name: Intelligent Relationship Discovery
    responsibilities:
      - Accept user-provided spec and requirement relationships
      - Discover and suggest additional related entities
      - Ask focused confirmation questions
    requirements:
      - PROD-002.FR-003
      - PROD-002.FR-004
    summary: >-
      Provides hybrid relationship discovery combining explicit user input with
      intelligent agent suggestions. Minimizes cognitive burden while ensuring
      comprehensive relationship tracking.
    success_criteria:
      - All user-provided relationships correctly captured
      - Agent suggests relevant additional relationships when appropriate
      - Discovery questions limited to confirmation (not full specification)
  - id: integrated-validation
    name: Integrated Validation
    responsibilities:
      - Validate structure and relationships during creation
      - Catch errors before delta completion
      - Ensure delta bundle (delta + design revision + plan + phases + notes) is well-formed and complete
    requirements:
      - PROD-002.FR-005
      - PROD-002.NF-002
    summary: >-
      Integrates validation throughout creation, catching errors early and ensuring
      the final delta bundle (including the design revision) is complete and consistent before user moves to
      implementation.
    success_criteria:
      - Validation errors caught and explained clearly
      - >95% first-attempt success rate
      - All delta bundles properly structured and valid
```

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: PROD-002
entries:
  - artefact: VT-001
    kind: VT
    requirement: PROD-002.FR-001
    status: planned
    notes: Test agent command workflow from invocation to completion
  - artefact: VT-002
    kind: VT
    requirement: PROD-002.FR-002
    status: planned
    notes: Verify delta bundle structure (delta + design revision + plan + phase artifacts)
  - artefact: VT-003
    kind: VT
    requirement: PROD-002.FR-003
    status: planned
    notes: Test hybrid discovery with user input and agent suggestions
  - artefact: VT-004
    kind: VT
    requirement: PROD-002.FR-004
    status: planned
    notes: Verify relationship capture and validation
  - artefact: VT-005
    kind: VT
    requirement: PROD-002.FR-005
    status: planned
    notes: Test validation error detection and clear messaging
  - artefact: VT-006
    kind: VT
    requirement: PROD-002.FR-006
    status: verified
    notes: Implemented in DE-013. Design revision (DR) file automatically scaffolded with valid design_revision frontmatter schema when creating delta. Template includes sections for current/target behavior, architecture impact, code hotspots. Tests verify DR creation with correct frontmatter and delta ID linkage.
    implemented_by: DE-013
    verified_by: IP-013.PHASE-01
  - artefact: VA-001
    kind: VA
    requirement: PROD-002.NF-001
    status: planned
    notes: User testing with first-time users measuring friction and completion time
  - artefact: VA-002
    kind: VA
    requirement: PROD-002.NF-002
    status: planned
    notes: Track delta creation success rates across 200 attempts
```

## 1. Intent & Summary

- **Problem / Purpose**: Creating deltas to track codebase changes is prohibitively difficult in a framework explicitly designed around spec-driven development with change tracking. Users face steep learning curve understanding delta/plan/phase structure, file organization, YAML schemas, and relationship management. This friction undermines the value proposition of comprehensive change tracking and implementation planning.

- **Value Signals**: Deltas are the primary mechanism for tracking and planning codebase changes in spec-driven development. Reducing delta creation friction directly impacts:
  - Developer workflow efficiency (target: <5 minutes to create complete delta bundle)
  - Change traceability across specs and requirements
  - Implementation planning quality and consistency
  - Agent-assisted change management effectiveness
  - Adoption of spec-driven workflow (target: 80%+ of changes tracked via deltas)

- **Guiding Principles**:
  - **Learn from PROD-001**: Apply proven spec creation workflow pattern
  - **Automate relentlessly**: Tools handle all mechanical tasks (file creation, structure, validation)
  - **Guide comprehensively**: Agent commands provide complete workflow without cluttering templates
  - **Validate early**: Catch errors before user invests time in implementation
  - **Hybrid discovery**: Balance user knowledge with intelligent suggestions
  - **Plan by default**: Implementation plans valuable; make skipping them explicit choice

- **Assumptions**:
  - Users have spec-driver installed and available
  - Claude Code or compatible agent environment available
  - Projects using spec-driver have delta/plan/phase templates
  - Users prefer guided workflows over reading documentation
  - Default behavior creates complete delta bundles (delta + design revision + plan + first phase)

- **Change History**:
  - 2025-11-02: Initial draft mirroring PROD-001 pattern for delta artifacts

## 2. Stakeholders & Journeys

### Personas / Actors

1. **Solo Developer (Sarah)**
   - **Context**: Working on personal project with spec-driver
   - **Goals**: Track changes systematically without process overhead
   - **Pains**: Doesn't remember delta/plan/phase structure between coding sessions; gets stuck on YAML syntax
   - **Expectations**: Type `/supekku.create-delta <change description>`, answer minimal questions, get complete delta bundle

2. **Team Lead (Marcus)**
   - **Context**: Managing team using spec-driven development
   - **Goals**: Ensure all changes properly tracked and planned
   - **Pains**: Team members skip delta creation due to complexity; inconsistent change tracking
   - **Expectations**: Workflow so simple that team consistently uses it; deltas link correctly to specs/requirements

3. **Developer on Team (Aisha)**
   - **Context**: Implementing features on established spec-driven project
   - **Goals**: Create delta before starting work; link to correct specs/requirements
   - **Pains**: Uncertain which specs/requirements her change touches; forgets to create delta until midway through implementation
   - **Expectations**: Workflow helps discover relationships; can create delta at any point (start or mid-implementation)

4. **AI Agent (Claude/Codex)**
   - **Context**: Assisting user with feature implementation
   - **Goals**: Create delta as part of implementation workflow
   - **Pains**: Complex workflows fail; unclear when to create delta vs start coding
   - **Expectations**: Clear command structure; validation prevents errors; can create delta proactively

### Primary Journeys / Flows

**Journey 1: Developer Creates Delta for Known Change**

Given Sarah wants to refactor the authentication module
1. Sarah types `/supekku.create-delta refactor authentication module`
2. Agent asks: "I found SPEC-042 (authentication). Is this change related to it?"
3. Sarah confirms: "Yes"
4. Agent asks: "Which requirements: FR-001 (auth flow), FR-003 (token refresh), NF-002 (performance)?"
5. Sarah selects: "FR-003 and NF-002"
6. Agent creates complete delta bundle (delta file, design revision, implementation plan, first phase)
7. Agent reports: "Created DE-002 at change/deltas/DE-002-refactor-authentication-module/"
8. Sarah opens delta file, reviews plan, starts implementation following phase guidance

Then Sarah has complete change tracking from the start
And she can implement with clear phase-based plan

**Journey 2: Agent Creates Delta Proactively During Implementation**

Given Claude is implementing payment processing feature
1. Claude recognizes change impacts multiple specs (SPEC-018, SPEC-042)
2. Claude invokes delta creation with inferred relationships
3. Claude asks user: "Should this also implement SPEC-018.FR-005 (transaction logging)?"
4. User confirms or adjusts
5. Claude creates delta bundle (delta, design revision, implementation plan, first phase)
6. Claude continues implementation following phase structure

Then change is tracked from inception
And implementation follows structured plan

**Journey 3: Quick Delta Without Full Planning**

Given Sarah needs to fix a typo in documentation
1. Sarah types `/supekku.create-delta fix typo in user guide --skip-plan`
2. Agent creates lightweight delta (delta + design revision only, no plan/phases)
3. Workflow completes in <2 minutes
4. Sarah fixes typo, marks delta complete

Then Sarah has change tracking without planning overhead
And lightweight changes don't require unnecessary structure

### Edge Cases & Non-goals

**Edge Cases**:
- User provides change description with no clear spec relationship → Agent performs discovery, asks for confirmation
- User wants to track change midway through implementation → Workflow supports retroactive delta creation
- Very complex change touches many specs → Agent helps prioritize primary vs secondary relationships
- User doesn't know which requirements affected → Agent suggests based on description keywords

**Non-goals**:
- **Updating existing deltas** (separate workflow, similar to PROD-001 spec refinement)
- **Multi-delta creation from single description** (one command = one delta)
- **Automatic delta creation on commits** (policy/workflow integration, project-specific)
- **Delta approval workflows** (team-specific process, out of initial scope)
- **Phase execution automation** (manual phase progression, separate concern)

## 3. Responsibilities & Requirements

### Capability Overview

**Frictionless Delta Creation** ensures users can invoke a single command and receive a complete delta bundle without needing to understand file structure, YAML syntax, or relationship management. The workflow eliminates all manual tasks and guides users from description to validated delta.

**Intelligent Relationship Discovery** balances user knowledge with agent intelligence - users provide what they know, agents discover and suggest what might be missing. This hybrid approach minimizes cognitive burden while ensuring comprehensive relationship tracking.

**Integrated Validation** prevents frustration by catching errors early - before users invest time in implementation. Clear error messages guide users to corrections when needed.

### Functional Requirements

- **FR-001**: Agent Command Provides Complete Workflow Guidance
  Users can invoke a single agent command (`/supekku.create-delta <description>`) that guides them through complete delta creation without consulting external documentation or understanding delta/plan/phase structure.
  *Verification*: VT-001 - Test complete workflow from command to validated delta bundle

- **FR-002**: Default Behavior Creates Complete Delta Bundle
  By default, delta creation produces four artifacts: delta file (tracks change), design revision (captures architecture intent), implementation plan (organizes work), and first phase (ready to execute), with option to skip plan/phase via flag for lightweight tracking (design revision remains).
  *Verification*: VT-002 - Verify bundle contains all four artifacts with proper cross-references

- **FR-003**: Users Can Provide Known Relationships Explicitly
  Users can specify specs (`--spec SPEC-XXX`) and requirements (`--requirement SPEC-XXX.FR-YYY`) they know the change affects, and workflow accepts and validates these inputs.
  *Verification*: VT-003 - Test user-provided relationships correctly captured

- **FR-004**: Agent Discovers and Suggests Additional Relationships
  When users provide partial relationship information or none at all, agent searches specs and requirements to suggest related entities, asking focused confirmation questions rather than requiring users to specify everything.
  *Verification*: VT-004 - Measure suggestion relevance across diverse change descriptions

- **FR-005**: Clear Error Messages Guide Users to Corrections
  When validation fails (non-existent spec ID, malformed structure, broken relationships), users receive specific error messages explaining the problem and suggesting corrections.
  *Verification*: VT-005 - Test error messages provide actionable guidance

- **FR-006**: Delta Creation Includes Design Revision Artifact
  Every delta creation automatically scaffolds a design revision (DR) document capturing architectural intent, current vs target behavior, and affected code hotspots, using the design_revision frontmatter schema and template structure.
  *Rationale*: Design revisions provide architecture context needed for implementation and review
  *Verification*: VT-006 - Verify DR file created with valid frontmatter and template structure

### Non-Functional Requirements

- **NF-001**: First-Time Users Complete Delta Creation in Under 5 Minutes
  Users with zero delta creation experience can create their first complete delta bundle in <5 minutes with zero "what do I do now?" friction points, matching PROD-001's ease-of-use standard.
  *Measurement*: VA-001 - User testing with 10 first-time users measuring completion time and friction incidents

- **NF-002**: Creation Success Rate Exceeds 95% on First Attempt
  Deltas created through the guided workflow complete successfully (all files created, valid structure, no validation errors) on first attempt in >95% of cases.
  *Measurement*: VA-002 - Track delta creation outcomes across 200 real attempts

### Success Metrics / Signals

- **Adoption**: 80%+ of changes tracked via deltas (vs manual tracking or no tracking)
- **Quality**: <5% of created deltas require manual corrections post-creation
- **Onboarding**: First-time users create valid delta in <5 minutes
- **Confidence**: User survey shows 85%+ agree "I felt guided throughout the process"
- **Agent effectiveness**: Agents complete workflow without intervention in 90%+ of attempts
- **Validation success**: >95% first-attempt creation success rate

## 4. Solution Outline

### User Experience / Outcomes

**Desired Behaviors**:

1. **Single-Command Invocation**: User types `/supekku.create-delta <change description>` and receives complete workflow guidance
2. **Conversational Discovery**: Agent asks 2-3 focused questions about relationships when needed
3. **Transparent Progress**: User sees clear workflow stages ("Creating delta...", "Discovering relationships...", "Validating...")
4. **Immediate Usability**: Delta bundle ready for implementation immediately after creation
5. **Flexible Planning**: Users can skip plan creation for lightweight changes via flag

**User Expectations**:
- Workflow duration: 2-5 minutes depending on complexity
- Zero manual file creation or YAML editing
- Clear error messages if something goes wrong
- Delta bundle includes everything needed to start implementation

### Data & Contracts

**Delta Bundle Contents** (user view):
- **Delta file**: Describes the change, motivation, scope, affected specs/requirements
- **Implementation plan**: Organizes work into phases with clear objectives
- **First phase**: Ready-to-execute phase with tasks, entrance/exit criteria
- **Notes file**: Workspace for implementation notes

**User-Provided Input**:
- Change description (required)
- Spec IDs (optional via `--spec`)
- Requirement IDs (optional via `--requirement`)
- Skip plan flag (optional via `--skip-plan` or `--allow-missing-plan`)

## 5. Behaviour & Scenarios

### Primary Flows

**Flow 1: Guided Creation with Discovery**
1. User invokes command with description
2. Agent extracts key information from description
3. Agent performs relationship discovery
4. Agent asks confirmation questions (2-3 max)
5. Agent creates delta bundle (delta, design revision, implementation plan, first phase)
6. Agent validates structure and relationships
7. User receives completion confirmation with file paths

**Flow 2: Explicit Relationships Provided**
1. User invokes command with --spec and --requirement flags
2. Agent validates provided IDs exist
3. Agent asks if additional relationships needed
4. Agent creates delta bundle (delta, design revision, implementation plan, first phase)
5. Validation confirms structure
6. User begins implementation

**Flow 3: Lightweight Mode**
1. User invokes command with --skip-plan flag
2. Agent creates delta + design revision only (no plan/phases)
3. Workflow completes quickly (<2 min)
4. User proceeds with simple change

### Error Handling / Guards

**User-Friendly Error Handling**:
- Spec doesn't exist → "SPEC-042 not found. Did you mean SPEC-024 (Authentication)?"
- Requirement doesn't exist → "SPEC-042.FR-010 not found. SPEC-042 has: FR-001, FR-003, NF-002"
- Invalid description → "Could you provide more details about this change?"

**Recovery Paths**:
- Agent suggests corrections
- User can adjust input
- Workflow resumes without starting over

## 6. Quality & Verification

### Testing Strategy

**VT-001: End-to-End Workflow** (FR-001)
- Test complete flow from command to validated delta
- Verify user can complete without external help
- Success: 100% workflow completion

**VT-002: Bundle Structure** (FR-002)
- Verify delta bundle contains all expected artifacts (delta, design revision, implementation plan, phase sheets, notes)
- Test cross-references between files work correctly
- Success: 100% structural correctness

**VT-003: User Input Handling** (FR-003)
- Test explicit spec/requirement input
- Verify validation of user-provided IDs
- Success: All valid inputs accepted, invalid inputs caught

**VT-004: Discovery Effectiveness** (FR-004)
- Measure suggestion relevance
- Test with diverse change descriptions
- Success: 80%+ relevant suggestion rate

**VT-005: Error Messaging** (FR-005)
- Test error scenarios
- Verify messages are clear and actionable
- Success: Users can self-correct based on messages

**VA-001: User Experience** (NF-001)
- Test with 10 first-time users
- Measure completion time and friction points
- Success: <5 min, zero critical friction

**VA-002: Success Rate** (NF-002)
- Track 200 real delta creations
- Measure first-attempt success
- Success: >95% success rate

### Research / Validation

**Hypothesis 1**: Guided workflow reduces delta creation time by 80% vs manual
- Test: Time users with/without workflow
- Target: 5 min guided vs 25+ min manual

**Hypothesis 2**: Relationship discovery catches missing links in 60%+ of cases
- Test: Compare discovered relationships to user-provided
- Target: Agent suggests at least one relevant relationship 60%+ of time

### Observability & Analysis

**User Metrics**:
- Weekly delta creation count
- First-attempt success rate (rolling 30-day)
- Average completion time
- Discovery acceptance rate
- Skip-plan usage rate

**Quality Indicators**:
- Error rate by category
- Relationship completeness
- User satisfaction scores

### Security & Compliance

**Data Privacy**:
- Delta content may include sensitive implementation details
- No external telemetry without opt-in
- Local-only operations

### Acceptance Gates

1. **Workflow Completeness**: VT-001 passes with 100% success across 20 test cases
2. **Bundle Quality**: VT-002 shows 100% correct structure
3. **Discovery Effectiveness**: VT-004 demonstrates 80%+ relevant suggestions
4. **User Experience**: VA-001 shows <5 min completion, zero critical friction
5. **Success Rate**: VA-002 demonstrates >95% first-attempt success
6. **Real-World Validation**: 10 users create deltas successfully without help

## 7. Backlog Hooks & Dependencies

### Related Specs / PROD

**Direct Model**:
- **PROD-001** (spec creation workflow): This spec mirrors PROD-001's proven pattern for delta artifacts

**Future Candidates**:
- Delta completion workflow (similar to spec refinement need identified in PROD-001)
- Phase progression workflows
- Delta approval and review processes
- Git integration for automatic delta tracking

### Risks & Mitigations

**RISK-001**: Users bypass workflow and create deltas manually
- **Likelihood**: Medium (power users prefer direct control)
- **Impact**: Low (manual creation still valid, just misses guidance)
- **Mitigation**: Ensure manual workflow remains supported; provide good CLI error messages

**RISK-002**: Relationship discovery suggests irrelevant relationships
- **Likelihood**: Medium (keyword matching can be noisy)
- **Impact**: Medium (annoying but not blocking)
- **Mitigation**: Limit suggestions to top 5; tune discovery algorithms based on feedback

**RISK-003**: No workflow for completing partially-created deltas
- **Likelihood**: Very High (mirrors PROD-001 RISK-007)
- **Impact**: High (users with partial deltas can't use workflow)
- **Mitigation**: Create separate completion workflow
- **Status**: HIGH PRIORITY future work

**RISK-004**: Users don't understand when to create delta vs just implement
- **Likelihood**: High (workflow adoption requires culture change)
- **Impact**: Medium (inconsistent adoption)
- **Mitigation**: Documentation, team training, agent proactive suggestions

### Known Gaps / Debt

**Gaps**:
- **HIGH PRIORITY**: No delta completion workflow for existing/partial deltas
- Discovery uses simple keyword matching (could improve with relationship graph analysis)
- Multi-agent platform testing not conducted
- No guidance on when deltas are required vs optional

### Open Decisions / Questions

**Decision 1**: Should agents proactively suggest delta creation?
- **Context**: Agent notices user starting significant change without delta
- **Options**: (A) Proactively suggest (B) Only create when asked (C) Team configurable
- **Leaning**: C (team configurable policy)

**Decision 2**: How to handle delta creation for already-in-progress work?
- **Context**: User realizes mid-implementation they should have created delta
- **Options**: (A) Create retroactive delta (B) Require delta before starting (C) Allow but warn
- **Leaning**: A (support retroactive creation)

**Decision 3**: Should workflow support template customization?
- **Context**: Teams may want different delta/plan/phase structures
- **Options**: (A) Support full customization (B) Fixed templates (C) Limited extension points
- **Decision**: DEFERRED - start with fixed templates, add customization based on feedback
