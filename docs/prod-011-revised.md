---
id: PROD-011
slug: implementation-execution-workflow
name: Implementation Execution Workflow
created: '2025-11-04'
updated: '2025-11-04'
status: draft
kind: prod
aliases: []
relations:
  - type: informs
    target: PROD-002
    description: Extends delta creation with implementation lifecycle guidance
  - type: informs
    target: PROD-006
    description: Enhances phase management with guided workflow commands
  - type: depends_on
    target: PROD-010
    description: Uses help system (FR-012 to FR-014) for workflow documentation
guiding_principles:
  - Workflow commands are customizable hooks, not prescriptive fixed processes
  - Configuration over convention - IP metadata drives automation preferences
  - Constitution (ADRs, policies, standards) embedded in commands and validated by tooling
  - Support varied workflows (delta-first, spec-first, backlog-first) through flexible primitives
  - Manual workflow always remains valid - commands are optional helpers
  - State inferred from artifacts, no hidden state files
assumptions:
  - Users have Claude Code or compatible agent environment
  - Projects may use different VCS tools (git, jj, etc)
  - Teams have varied preferences for commit workflow and automation
  - Implementation plans created before phases (PROD-006)
  - Phase-01 benefits from IP intelligence like later phases (original motivation)
---

# PROD-011 – Implementation Execution Workflow

```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: PROD-011
requirements:
  primary:
    - PROD-011.FR-001  # Remove phase-01 auto-creation
    - PROD-011.FR-002  # Enable phase creation with no phases
    - PROD-011.FR-003  # Hook installation system
    - PROD-011.FR-004  # Default workflow hooks (5 commands)
    - PROD-011.FR-005  # IP metadata for automation preferences
    - PROD-011.FR-006  # Constitution integration in commands
    - PROD-011.FR-007  # Constitution validation tooling
    - PROD-011.FR-008  # VCS abstraction
    - PROD-011.NF-001  # Workflow adoption
    - PROD-011.NF-002  # Delta quality improvement
  collaborators: []
interactions:
  - with: PROD-002
    nature: Extends delta creation workflow with implementation execution guidance
  - with: PROD-006
    nature: Enhances phase management with guided workflow at each stage
  - with: PROD-010
    nature: Uses help system (FR-012 to FR-014) for workflow documentation and installation
```

```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: PROD-011
capabilities:
  - id: core-workflow-fix
    name: Core Workflow Improvements
    responsibilities:
      - Remove phase-01 auto-creation from delta creation
      - Enable create phase to work when no phases exist
      - Allow phase-01 to benefit from IP entry/exit criteria intelligence
    requirements:
      - PROD-011.FR-001
      - PROD-011.FR-002
    summary: >-
      Fixes the fundamental issue where phase-01 is created too early (before IP
      is fleshed out), preventing it from using entry/exit criteria intelligence
      that was added to create phase. This was the original problem statement.
    success_criteria:
      - create delta produces 4 files (delta, DR, IP, notes) without phase directory
      - create phase works on plan with zero existing phases
      - Phase-01 created after IP completion gets entry/exit criteria from IP

  - id: workflow-hook-system
    name: Customizable Workflow Hook System
    responsibilities:
      - Install workflow command hooks to project (like templates)
      - Support local customization of workflow commands
      - Provide default hooks for common workflow stages
      - Enable project-specific workflow adaptations
    requirements:
      - PROD-011.FR-003
      - PROD-011.FR-004
    summary: >-
      Workflow commands are installed locally as customizable markdown files
      (similar to templates), enabling teams to adapt workflows to their needs.
      Default hooks cover the canonical execution workflow (plan → phase → task →
      phase-complete → delta-complete) but can be modified for project preferences.
    success_criteria:
      - Workflow hooks installed to .claude/commands/ as markdown
      - Users can modify command prompts like templates
      - Default hooks cover 5 workflow stages
      - Modified hooks preserved across updates

  - id: metadata-driven-automation
    name: Metadata-Driven Automation Preferences
    responsibilities:
      - Define automation preferences in IP frontmatter
      - Support project-level defaults for automation behavior
      - Enable per-phase or per-delta automation configuration
      - Abstract VCS operations to support git, jj, and other tools
    requirements:
      - PROD-011.FR-005
      - PROD-011.FR-008
    summary: >-
      Implementation Plans include metadata controlling how agents automate workflow
      tasks. Settings like commit strategy (per-task, per-phase, manual), message
      preparation, staging behavior adapt to team preferences. VCS abstraction
      allows projects using jj or other tools to define their own workflows.
    success_criteria:
      - IP frontmatter includes automation schema
      - Project defaults configurable
      - VCS operations abstracted (not hardcoded to git)
      - Commands respect automation preferences

  - id: constitution-integration
    name: Constitution Integration and Enforcement
    responsibilities:
      - Embed constitution (ADRs, policies, standards) in default command behavior
      - Provide tooling to discover and validate constitutional elements
      - Offer onboarding command showing active constitution
      - Enable pre-flight checks before critical operations
    requirements:
      - PROD-011.FR-006
      - PROD-011.FR-007
    summary: >-
      Workflow commands enforce project constitution through embedded checks and
      guidance. Default commands reference relevant ADRs, policies, and standards.
      Tooling (onboarding command, pre-flight validators) makes constitution
      visible and validates work against it. Constitution becomes executable, not
      just documentation.
    success_criteria:
      - Default commands reference relevant ADRs/policies/standards
      - Onboarding command lists active constitutional elements
      - Pre-flight checks validate against constitution
      - Constitution violations surfaced before commits
```

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: PROD-011
entries:
  - artefact: VT-011-001
    kind: VT
    requirement: PROD-011.FR-001
    status: planned
    notes: Test create delta no longer creates phase-01 directory

  - artefact: VT-011-002
    kind: VT
    requirement: PROD-011.FR-002
    status: planned
    notes: Test create phase works when plan has no existing phases

  - artefact: VT-011-003
    kind: VT
    requirement: PROD-011.FR-003
    status: planned
    notes: Test workflow hook installation to .claude/commands/

  - artefact: VT-011-004
    kind: VT
    requirement: PROD-011.FR-004
    status: planned
    notes: Test default workflow hooks (plan, phase, task, phase-complete, delta-complete)

  - artefact: VT-011-005
    kind: VT
    requirement: PROD-011.FR-005
    status: planned
    notes: Test IP automation metadata schema and behavior

  - artefact: VT-011-006
    kind: VT
    requirement: PROD-011.FR-006
    status: planned
    notes: Test default commands include constitution references

  - artefact: VT-011-007
    kind: VT
    requirement: PROD-011.FR-007
    status: planned
    notes: Test constitution validation tooling (onboarding, pre-flight)

  - artefact: VT-011-008
    kind: VT
    requirement: PROD-011.FR-008
    status: planned
    notes: Test VCS abstraction supports git and jj

  - artefact: VH-011-001
    kind: VH
    requirement: PROD-011.NF-001
    status: planned
    notes: User testing measures workflow adoption with 5 developers

  - artefact: VA-011-001
    kind: VA
    requirement: PROD-011.NF-002
    status: planned
    notes: Track delta completion quality before/after workflow
```

## 1. Intent & Summary

### Problem Statement

**Original Problem** (from user request):
Phase-01 is created by `create delta` before the Implementation Plan is fleshed out. Since we added intelligence to `create phase` to copy entry/exit criteria from the IP, phase-01 can't benefit from this intelligence (it's created alongside the empty IP template). This creates manual duplication work.

**Expanded Problem** (discovered through clarification):
Beyond the phase-01 timing issue, developers lack:
- **Customizable workflow support**: Commands are fixed, can't adapt to team/project needs
- **Configuration**: No way to control automation level (commits, messages, agent activity)
- **Constitution enforcement**: ADRs/policies/standards exist but aren't enforced in workflow
- **Flexible primitives**: Workflow assumes one path, doesn't support varied adoption patterns

### Value Signals

Guided implementation workflows directly impact:
- **Developer productivity**: 20% time reduction in delta lifecycle (less workflow friction)
- **Documentation completeness**: 95% complete verification artifacts (vs 70% baseline)
- **Quality consistency**: 50% reduction in incomplete deltas
- **Onboarding efficiency**: New developers complete first delta independently
- **Team autonomy**: Projects adapt workflow to their needs without forking

### Guiding Principles

1. **Customizable hooks, not prescriptive process**: Like templates, workflow commands are locally installed and modifiable
2. **Configuration over convention**: IP metadata and project defaults control automation behavior
3. **Executable constitution**: ADRs/policies/standards embedded in commands and validated by tooling
4. **Support varied workflows**: Delta-first, spec-first, backlog-first all supported through flexible primitives
5. **Manual always valid**: Commands are optional helpers, never required
6. **State from artifacts**: No hidden state - infer everything from existing files

### Assumptions

- Users have Claude Code or compatible agent environment
- Projects may use different VCS tools (git, jj, etc)
- Teams have varied preferences for commit workflow and automation
- Implementation plans created before phases (PROD-006 dependency)
- Phase-01 should benefit from IP intelligence like phases 2+

## 2. Stakeholders & Journeys

### Personas

**1. Solo Developer (Sam)**
- Context: Personal project using spec-driver
- Goals: Maintain discipline without team pressure, customize workflow to their style
- Pains: Default workflow too heavy for small changes; wants commit-per-phase not commit-per-task
- Expectations: Can modify commands to match their process

**2. Team Lead (Taylor)**
- Context: Team of 5 using spec-driver with jj (not git)
- Goals: Establish team workflow, enforce coding standards, adapt to jj commands
- Pains: Hardcoded git assumptions; can't enforce team's ADRs automatically
- Expectations: Configure automation level, customize commands for team, validate against constitution

**3. New Developer (Nathan)**
- Context: First week using spec-driver
- Goals: Understand implementation workflow, follow team conventions
- Pains: Doesn't know what ADRs exist, unclear what automation is happening
- Expectations: Onboarding shows constitution, default workflow teaches process

**4. OSS Contributor (Charlie)**
- Context: Contributing to project using spec-driver, different workflow than their own projects
- Goals: Follow project conventions without modifying their local defaults
- Pains: Can't easily see what's different about this project's workflow
- Expectations: Project-specific customizations visible and documented

### User Journeys

**Journey 1: First Delta with Default Workflow (Nathan)**

```
1. Creates delta: `create delta "Add export feature"`
   → DE-020.md, DR-020.md, IP-020.md, notes.md (no phase-01)

2. Types: `/supekku.plan`
   → Agent reads default plan command from .claude/commands/supekku-plan.md
   → Guides through DR/IP completion, checks relevant ADRs
   → Sets delta in-progress
   → Prompts for commit per IP metadata (default: yes)

3. Types: `/supekku.phase`
   → Agent reads default phase command
   → Creates phase-01 with entry/exit criteria from IP (original fix!)
   → Validates entry criteria
   → Breaks objective into tasks

4. Implements feature, types `/supekku.task` after each task
   → Agent updates phase progress per automation config

5. Types: `/supekku.phase-complete`
   → Validates exit criteria, summarizes

6. Types: `/supekku.delta-complete`
   → Validates coverage, runs constitution checks, completes delta

Result: Complete delta, learned workflow, saw constitution in action
```

**Journey 2: Customized Workflow (Taylor - Team Lead)**

```
1. Installs workflow hooks: `spec-driver install workflow-hooks`
   → Copies default commands to .claude/commands/

2. Modifies .claude/commands/supekku-task.md:
   → Removes per-task commit prompts (team does commit-per-phase)
   → Adds team-specific ADR reminder

3. Creates IP template with automation metadata:
   automation:
     commit_strategy: per_phase
     vcs: jj
     agent_prepares_commits: false

4. Team members use modified workflow:
   → /supekku.task doesn't prompt for commits
   → Phase completion prompts for jj commit
   → ADR reminders specific to team

Result: Workflow adapted to team needs, maintained across updates
```

**Journey 3: Constitution Discovery (Nathan - Day 1)**

```
1. Runs: `spec-driver onboard`
   → Shows core concepts
   → Lists active ADRs (5 accepted)
   → Lists policies (2 active)
   → Lists standards (lint config, test requirements)
   → Explains workflow stages

2. During /supekku.plan:
   → Agent mentions: "Note: ADR-015 (Module Structure) applies to this work"
   → Shows link to ADR

3. Before phase completion:
   → Pre-flight check: "ADR-015 requires tests for new modules - have you added them?"

Result: Constitution visible, enforced, helps Nathan follow standards
```

## 3. Responsibilities & Requirements

### Functional Requirements

#### Capability 1: Core Workflow Fix

**FR-001: Remove Phase-01 Auto-Creation**
System MUST NOT create phase-01.md when running `create delta`. Delta creation produces only: delta file, design revision, implementation plan, and notes file.

*Rationale*: This is the original problem - phase-01 created too early can't benefit from IP intelligence

*Verification*: VT-011-001 - Test create delta output, verify no phases/ directory

**FR-002: Enable Phase Creation When No Phases Exist**
System MUST support `create phase --plan IP-XXX` when plan has zero existing phases, creating phase-01 with entry/exit criteria copied from implementation plan.

*Rationale*: Phase-01 needs same intelligence as phases 2+ (the whole point!)

*Verification*: VT-011-002 - Test create phase on empty plan, verify phase-01 created with IP criteria

---

#### Capability 2: Workflow Hook System

**FR-003: Hook Installation System**
System MUST provide command to install workflow hooks to `.claude/commands/` directory as customizable markdown files, preserving modifications across updates.

*Rationale*: Like templates, workflow commands should be locally customizable

*Implementation*:
- `spec-driver install workflow-hooks` copies default commands to `.claude/commands/`
- Checks for existing modified commands, preserves them
- Updates only if user confirms overwrite

*Verification*: VT-011-003 - Test installation, modification preservation, update behavior

**FR-004: Default Workflow Hooks**
System MUST provide default workflow hooks for five stages: implementation planning, phase planning, task execution, phase completion, delta completion.

*Rationale*: Provide canonical workflow as starting point for customization

*Commands*:
1. `/supekku.plan` - Flesh out IP/DR, research, set delta in-progress
2. `/supekku.phase` - Create phase with IP criteria, validate entry gates, plan tasks
3. `/supekku.task` - Update progress, record notes, commit reminders
4. `/supekku.phase-complete` - Validate exit criteria, summarize, test/lint
5. `/supekku.delta-complete` - Sync, validate coverage, complete delta

NOTE/TODO: - probably also a "wrap up phase sheet for handover" command

*Verification*: VT-011-004 - Test each command in default configuration

---

#### Capability 3: Metadata-Driven Automation

**FR-005: IP Automation Metadata Schema**
System MUST support automation preferences in IP frontmatter, with CLI flag support in create delta / phase, controlling agent behavior during workflow execution.

*Rationale*: Teams have varied preferences for automation level and commit workflow

flags: `--stage-commits [true|phase]`, `--perform-commits [true|phase]` 

*Schema*:
```yaml
schema: supekku.plan.overview
version: 1
plan: IP-XXX
delta: DE-XXX
automation:
  stage_for_commit: false (default) | true | phase # end of phase only
  perfom_commit: false (default) | true | phase # end of phase only 
phases: [...]
```


Future consideration: *Project Defaults*: `.spec-driver/config.yaml` includes `automation` section with project-wide defaults

*Verification*: VT-011-005 - Test schema validation, behavior changes per config

**FR-008: VCS Abstraction**
System MUST abstract VCS operations to support git, jj, and other version control tools through configuration, not hardcoded commands.

*Rationale*: Different projects use different VCS tools

*Implementation*:
- VCS commands specified in IP metadata or project config
- Workflow hooks use abstracted operations (commit, status, diff)
- Default to git if not specified

*Verification*: VT-011-008 - Test workflow with git and jj configurations

---

#### Capability 4: Constitution Integration

**FR-006: Constitution Integration in Commands**
Default workflow hooks MUST embed constitution (ADRs, policies, standards) by referencing relevant documents and reminding users of applicable constraints.

*Rationale*: Constitution should be enforced through workflow, not just documentation

*Implementation*:
- Default commands include constitution discovery and reference
- `/supekku.plan` checks for ADRs related to delta scope
- Phase/delta completion validate against standards

*Verification*: VT-011-006 - Test default commands include constitution checks

**FR-007: Constitution Validation Tooling**
System MUST provide tooling to discover and validate against constitution: onboarding command listing active elements, pre-flight checks before critical operations.

*Rationale*: Constitution must be visible and enforceable, not hidden

*Commands*:
- `spec-driver onboard` - Show constitution + workflow overview (uses PROD-010.FR-012-014 help system)
- `spec-driver governance` - Check work against ADRs/policies/standards
- Pre-flight hooks in workflow commands

*Verification*: VT-011-007 - Test onboarding shows constitution, validate catches violations

---

### Non-Functional Requirements

**NF-001: High Workflow Adoption**
Developers (the primary author) finds them valuable and has no major friction points identified. Community users positive sentiment overall (github issues, etc).

*Measurement*: VH-011-001 - Vibe check.

**NF-002: Improved Delta Quality**
Deltas completed using workflow commands MUST have 95%+ complete verification artifacts, compared to 70% baseline without commands.

*Measurement*: VA-011-001 - Audit delta completion quality before/after workflow introduction

### Success Metrics

- **Adoption**: 70%+ of new deltas use at least one workflow command
- **Customization**: 40%+ of projects modify default workflow hooks
- **Completion**: 95%+ verification artifact completeness (vs 70% baseline)
- **Time**: 20% reduction in delta lifecycle duration
- **Errors**: 50% reduction in incomplete/abandoned deltas
- **Constitution**: 80%+ of workflow executions reference constitution
- **Onboarding**: New developers complete first delta independently
- **Satisfaction**: 80%+ user survey positive on workflow helpfulness

## 4. Solution Outline

### Architecture Overview

```
Workflow Hook System
├── Installation (.spec-driver/hooks/ → .claude/commands/)
├── Default Hooks (5 canonical commands)
├── Customization (local modifications preserved)
└── Constitution Integration (ADR/policy/standard references)

Configuration System
├── IP Automation Metadata (per-plan settings)
├── Project Defaults (.spec-driver/config.yaml)
└── VCS Abstraction (tool-agnostic operations)

Constitution Tooling
├── Discovery (onboarding command)
├── Validation (pre-flight checks)
└── Enforcement (embedded in commands)

Help System Integration (PROD-010.FR-012-014)
├── Core Workflow Docs (immutable)
├── Project Workflow Docs (customizable)
└── Installation Support (bootstrap project docs)
```

### Workflow Hook Structure

Hooks live in `.claude/commands/` as markdown files:

```markdown
# .claude/commands/supekku-plan.md

You are helping the user complete implementation planning for a delta.

## Context Discovery
1. Identify current delta (from working directory or user specification)
2. Read delta, DR, IP files
3. Load automation preferences from IP frontmatter or project defaults
4. Check relevant ADRs using `spec-driver list adrs --status accepted`

## Constitution Check
Review ADRs for guidance on:
- Architecture decisions relevant to delta scope
- Standards for testing, documentation, naming
- Policies for review, verification, commits

## Implementation Plan Completion
Guide user through:
1. Design Revision (current/target behavior, hotspots, impacts)
2. Phase breakdown (objectives, sequencing)
3. Entry/exit criteria (per phase)
4. Testing strategy
5. Dependencies and risks

## Automation Behavior
Per IP automation config:
- If agent_prepares_commits: prepare commit with message "plan: complete IP and DR for DE-XXX"
- If commit_strategy == on_demand: ask user if they want to commit now
- Use vcs_commands.commit from config

## Deliverables
- DR fleshed out with concrete details
- IP phase overview complete
- Delta status updated to in-progress
- Clean commit (if automation configured)
```

Users can modify this file to:
- Change constitution references
- Adjust automation prompts
- Add team-specific checks
- Integrate with project tools

### Configuration Schema

**IP Frontmatter** (`.spec-driver/templates/implementation-plan-template.md`):

```yaml
schema: supekku.plan.overview
version: 1
plan: IP-XXX
delta: DE-XXX
automation:
  # Commit strategy: when to prepare commits
  commit_strategy: per_task  # per_task | per_phase | manual | on_demand

  # Agent responsibilities
  agent_prepares_commits: true
  agent_stages_files: true
  agent_suggests_messages: true

  # VCS configuration
  vcs: git
  vcs_commands:
    commit: "git commit -m"
    stage: "git add"
    status: "git status"
    diff: "git diff"

  # Validation preferences
  run_tests_before_commit: true
  run_lint_before_commit: true

phases: [...]
```

**Project Defaults** (`.spec-driver/config.yaml`):

```yaml
automation:
  default_commit_strategy: per_phase
  default_vcs: git
  constitution_enforcement: strict  # strict | warn | off

help:
  workflow_docs_dir: docs/workflow/

hooks:
  pre_phase_complete:
    - validate_tests
    - validate_lint
  pre_delta_complete:
    - validate_coverage
    - validate_constitution
```

### Constitution Integration Points

1. **Onboarding Command** (leverages PROD-010.FR-012-014):
   ```bash
   $ spec-driver onboard

   === Spec-Driver Onboarding ===

   ## Core Concepts
   [from help system: specs, deltas, phases, requirements]

   ## Workflow Stages
   [from help system: plan → phase → task → complete]

   ## Active Constitution

   Accepted ADRs (5):
   - ADR-015: Module Structure and Naming
   - ADR-023: Test Coverage Requirements
   - ADR-031: Commit Message Format
   [...]

   Active Policies (2):
   - POLICY-001: All code requires tests before merge
   - POLICY-002: Breaking changes require migration guide

   Standards:
   - Lint: ruff (config in pyproject.toml)
   - Test: pytest (threshold: 80% coverage)
   - Format: 2-space indentation

   Run `help workflows` for detailed workflow documentation.
   ```

2. **Pre-Flight Checks in Commands**:
   - `/supekku.plan` checks ADRs relevant to delta scope
   - `/supekku.phase-complete` validates against standards (tests, lint)
   - `/supekku.delta-complete` runs constitution validation

3. **Constitution Validator**:
   ```bash
   $ spec-driver validate constitution [--delta DE-XXX]

   Checking against constitution...

   ✓ ADR-015: Module structure follows convention
   ✓ ADR-023: Test coverage 87% (threshold 80%)
   ✗ ADR-031: 2 commits don't follow message format

   ⚠ POLICY-001: Verification artifacts incomplete (VT-020-002 missing)

   2 issues found (1 error, 1 warning)
   ```

## 5. Behaviour & Scenarios

### Scenario 1: Default Workflow (Nathan - New Developer)

```
1. Nathan creates first delta:
   $ spec-driver create delta "Add CSV export"
   → DE-025.md, DR-025.md, IP-025.md, notes.md
   → No phase-01 (FR-001 fix!)

2. Nathan runs onboarding:
   $ spec-driver onboard
   → Learns concepts, sees 5 ADRs, 2 policies
   → Understands workflow stages

3. Nathan starts implementation planning:
   $ /supekku.plan (in Claude Code)
   → Agent reads DE-025, DR-025, IP-025
   → Agent checks ADRs: "ADR-015 (Module Structure) applies"
   → Agent guides through DR completion (current behavior analysis)
   → Agent guides through IP completion (2 phases planned)
   → Agent sets delta to in-progress
   → Agent (per default automation): "Ready to commit? [yes]"
   → Commits: "plan: complete IP and DR for DE-025"

4. Nathan creates first phase:
   $ /supekku.phase
   → Agent runs: create phase --plan IP-025
   → Phase-01 created with entry/exit from IP (FR-002 fix!)
   → Agent validates entry criteria: all satisfied
   → Agent suggests 6 tasks
   → Agent commits: "phase: create phase-01 for IP-025"

5. Nathan implements 3 tasks:
   $ /supekku.task
   → Agent: "Which task completed? [task 3]"
   → Agent updates phase: 3/6 (50%)
   → Agent captures notes
   → Agent (per automation): "Ready to commit code? [yes]"
   → Commits: "feat(csv): add export formatter"

6. Nathan completes phase:
   $ /supekku.phase-complete
   → Agent checks exit criteria
   → Agent runs tests: just test
   → Agent runs lint: just lint
   → Agent summarizes in DE-025
   → Agent commits: "complete: phase-01 of IP-025"

7. Nathan completes delta:
   $ /supekku.delta-complete
   → Agent validates all phases complete
   → Agent checks verification artifacts
   → Agent runs: spec-driver sync
   → Agent validates coverage metadata
   → Agent runs: spec-driver validate constitution
   → Constitution check: ✗ Missing VT artifact
   → Agent: "Add VT-025-001 for test coverage, then continue"

Result: Nathan learns workflow, sees constitution, completes delta properly
```

### Scenario 2: Customized Workflow (Taylor - Team Lead)

```
1. Taylor sets up team workflow:
   $ spec-driver install workflow-hooks
   → Copies 5 default commands to .claude/commands/

2. Taylor modifies .claude/commands/supekku-task.md:
   - Removes per-task commit prompts
   - Adds team-specific reminder: "Update Jira ticket"
   - References team's ADR-042: "Use descriptive task names"

3. Taylor creates project defaults (.spec-driver/config.yaml):
   automation:
     default_commit_strategy: per_phase
     default_vcs: jj
     constitution_enforcement: strict
   vcs_commands:
     commit: "jj describe -m"
     status: "jj status"

4. Taylor creates IP template with team automation:
   automation:
     commit_strategy: per_phase
     vcs: jj
     agent_prepares_commits: false  # Team prefers manual
     run_tests_before_commit: true

5. Team member uses customized workflow:
   $ /supekku.task
   → Agent: "Update progress (no commit prompt)"
   → Agent: "Remember to update Jira ticket"
   → Uses team's modified command

6. At phase completion:
   $ /supekku.phase-complete
   → Tests run automatically (per config)
   → Agent: "Phase complete. Run: jj describe -m 'complete: phase-01'"
   → Suggests jj command (doesn't auto-commit per config)

Result: Workflow adapted to team needs (jj, manual commits, Jira integration)
```

### Scenario 3: Constitution Violation Caught (Sam)

```
1. Sam creates delta, rushes through implementation:
   $ /supekku.delta-complete

2. Agent runs constitution validation:
   $ spec-driver validate constitution --delta DE-026

   ✗ ADR-023: Test coverage 45% (threshold 80%)
   ✗ POLICY-001: VT artifacts incomplete (2/4 executed)
   ⚠ ADR-031: 3 commits missing conventional format

3. Agent blocks completion:
   "Cannot complete delta - constitution violations found:
    - Add tests to reach 80% coverage
    - Execute VT-026-003 and VT-026-004
    - Consider rebasing commits for message format (optional)"

4. Sam fixes issues, reruns validation:
   $ spec-driver validate constitution --delta DE-026
   ✓ All checks pass

5. Agent proceeds with completion

Result: Constitution enforced, quality maintained, Sam learns standards
```

### Scenario 4: Simple Quick Fix (Elena - Experienced)

```
1. Elena creates delta for bug fix:
   $ spec-driver create delta "Fix date parsing bug"
   → DE-027.md, DR-027.md, IP-027.md, notes.md

2. Elena manually fills simple IP (1 phase, 3 tasks):
   (Skips /supekku.plan - knows what to do)

3. Elena creates phase:
   $ /supekku.phase
   → Phase-01 created with IP criteria (works even for simple cases)

4. Elena implements fix quickly, skips /supekku.task:
   (Manually updates phase as she goes)

5. Elena completes delta directly:
   $ /supekku.delta-complete
   → Agent validates: phase incomplete
   → Agent: "Phase 01 has 2/3 tasks. Complete remaining task or update?"
   → Elena completes final task
   → Agent validates constitution: all good
   → Agent completes delta

Result: Flexibility for experienced users, validation prevents mistakes
```

## 6. Quality & Verification

### Testing Strategy

**Unit Tests**:
- VT-011-001: Delta creation (no phase-01)
- VT-011-002: Phase creation with empty plan
- VT-011-005: Automation metadata parsing and behavior

**Integration Tests**:
- VT-011-003: Hook installation and modification preservation
- VT-011-004: Default workflow hooks end-to-end
- VT-011-008: VCS abstraction with git and jj

**System Tests**:
- VT-011-006: Constitution integration in commands
- VT-011-007: Constitution validation tooling

**User Testing**:
- VH-011-001: 5 developers (2 new, 2 experienced, 1 team lead)
  - Measure: adoption rate, customization usage, satisfaction
  - Observe: friction points, confusion, successful adaptations

**Metrics Validation**:
- VA-011-001: Delta quality audit
  - Before: 70% verification artifact completeness
  - After: Target 95%
  - Track: abandoned deltas, incomplete coverage, constitution violations

### Acceptance Criteria

- [x] Core fix implemented (FR-001, FR-002)
- [ ] Hook installation system working (FR-003)
- [ ] Default workflow hooks complete (FR-004)
- [ ] Automation metadata schema defined and tested (FR-005)
- [ ] VCS abstraction supports git and jj (FR-008)
- [ ] Constitution integration in default commands (FR-006)
- [ ] Constitution validation tooling operational (FR-007)
- [ ] All unit/integration tests passing
- [ ] User testing shows 70%+ adoption intent
- [ ] Documentation complete (help system integration)
- [ ] Backward compatible (existing deltas unaffected)

### Observability

**Telemetry** (privacy-preserving):
- Command usage frequency (which hooks used)
- Customization rate (% projects with modified hooks)
- Automation config distribution (commit strategies)
- Constitution validation runs and violations

**Success Indicators**:
- Workflow adoption trending toward 70%+
- Delta quality improving toward 95%
- Time-to-completion decreasing
- Constitution violations caught pre-commit

## 7. Backlog Hooks & Dependencies

### Dependencies

**Blocking**:
- PROD-006 (Phase Management): create phase intelligence
- PROD-010.FR-012 to FR-014 (Help System): documentation infrastructure

**Related**:
- PROD-002 (Delta Creation): extends with workflow
- All specs: constitution validation applies to all work

### Enabling Delta

**DE-TBD: Implement Workflow Hook System**
- Priority: High
- Complexity: Medium-High
- Phases:
  1. Core fix (remove phase-01, enable create phase)
  2. Hook installation system
  3. Default workflow hooks
  4. Automation metadata and VCS abstraction
  5. Constitution integration and tooling
- Risk: Medium (significant scope, but well-defined)

### Future Enhancements

**Out of Scope for Initial Cut**:
- Workflow state machine (planned → in-progress → blocked → complete)
- Workflow visualization (progress diagrams, phase trees)
- Advanced constitution analysis (ADR conflict detection)
- Multi-repository workflow coordination
- Workflow templates by project type
- Integration with external tools (Jira, Linear, etc)
- Rollback/undo for workflow stages

### Related ADRs

**Needed**:
- ADR-TBD: Workflow hook architecture and customization strategy
- ADR-TBD: VCS abstraction design
- ADR-TBD: Constitution enforcement levels (strict vs warn)

### Known Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Hook customization causes breakage on update | Medium | Medium | Version hooks, migration guide, preserve modifications |
| VCS abstraction incomplete for some tools | Medium | Low | Start with git/jj, document extension points |
| Constitution enforcement too rigid | Low | High | Support enforcement levels (strict/warn/off), user feedback |
| Automation metadata too complex | Medium | Medium | Provide sensible defaults, progressive disclosure |
| Adoption lower than expected | Low | Medium | Strong defaults, clear value prop, user feedback loop |

## 8. Open Questions

**Q1: Should workflow hooks be versioned?**
- Proposal: Yes, version in filename (supekku-plan-v1.md) or frontmatter
- Benefit: Can migrate hooks when schema changes
- Cost: More complexity for users

**Q2: How to handle hook updates when user modified?**
- Proposal: Three-way merge (base, user, new) with conflict markers
- Alternative: Side-by-side install (supekku-plan.md vs supekku-plan-new.md)

**Q3: Should constitution enforcement levels be per-ADR or global?**
- Proposal: Global with per-ADR override
- Example: strict by default, but ADR-031 (commit format) is warn-only

**Q4: How to discover project-specific constitution?**
- Proposal: Scan specify/decisions/ for accepted ADRs, .spec-driver/ for policies
- Need: Standard location for policies and standards files

**Q5: Should help system integration be phase 1 or later phase?**
- Proposal: Phase 2 - core fix and hooks first, help integration after PROD-010 complete
- Rationale: Don't block on PROD-010 implementation timeline

---

## Changes from Original PROD-011

**Added**:
- Customizable workflow hook system (FR-003)
- Metadata-driven automation preferences (FR-005)
- Constitution integration and tooling (FR-006, FR-007)
- VCS abstraction (FR-008)
- Help system dependency (PROD-010.FR-012-014)
- Configuration system architecture
- Team/project customization scenarios

**Preserved**:
- Core fix (remove phase-01 auto-creation)
- Enable create phase when no phases exist
- Five default workflow commands
- Guided workflow benefits
- Manual workflow always valid

**Removed/Deferred**:
- Prescriptive single workflow assumption
- Hardcoded git commands
- Fixed automation behavior
- Missing constitution integration