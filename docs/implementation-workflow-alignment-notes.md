# Implementation Workflow Alignment Notes

This document outlines what needs to change in `implementation-workflow.md` to align with the revised PROD-011 spec.

## Current State vs. Target State

### 1. **Hook Customization** (Major Addition)

**Current**: Commands described as if they're fixed, built-in functionality.

**Target**: Commands are customizable hooks installed locally.

**Changes Needed**:
- Add section on hook installation: `spec-driver install workflow-hooks`
- Explain hooks are markdown files in `.claude/commands/`
- Show example of customizing a hook
- Document preservation of modifications on update
- Reference help system for workflow documentation (PROD-010.FR-012-014)

### 2. **Automation Configuration** (Major Addition)

**Current**: Fixed automation behavior (agent commits, stages, etc.)

**Target**: IP metadata controls automation level, project defaults exist.

**Changes Needed**:
- Add IP frontmatter automation schema documentation
- Show examples of different automation strategies:
  - `commit_strategy: per_task` (frequent commits)
  - `commit_strategy: per_phase` (milestone commits)
  - `commit_strategy: manual` (user controls)
  - `commit_strategy: on_demand` (agent asks each time)
- Document project defaults in `.spec-driver/config.yaml`
- Show how commands respect automation config

### 3. **VCS Abstraction** (Major Addition)

**Current**: Hardcoded git commands throughout.

**Target**: VCS-agnostic with configuration for git, jj, others.

**Changes Needed**:
- Replace all `git commit`, `git add`, etc. with abstract descriptions
- Add examples for both git and jj workflows
- Document `vcs_commands` configuration in IP metadata
- Show how to adapt workflow for different VCS tools

### 4. **Constitution Integration** (Major Addition)

**Current**: No mention of ADRs, policies, or standards.

**Target**: Constitution embedded in commands and validated by tooling.

**Changes Needed**:
- Add section on constitution discovery
- Document onboarding command: `spec-driver onboard`
- Show how commands reference relevant ADRs
- Add pre-flight validation examples
- Document constitution validation: `spec-driver validate constitution`
- Show workflow stages checking against standards

### 5. **Flexibility Emphasis** (Tone/Philosophy Change)

**Current**: Presents workflow as "the way" with manual as alternative.

**Target**: Emphasizes flexibility, customization, adaptation.

**Changes Needed**:
- Add guiding principle: "Commands are customizable hooks"
- Emphasize workflow stages are starting points, not requirements
- Add examples of different team adaptations
- Show how same primitives support varied workflows
- Remove prescriptive language ("must", "should"), use "can", "may"

## Recommended Structure for Revised implementation-workflow.md

```markdown
# Implementation Workflow Guide

## Overview

This guide describes the default implementation workflow provided by spec-driver's
workflow hooks. These hooks are **locally installed and customizable** - teams can
adapt them to their needs.

## Quick Start

1. Install workflow hooks: `spec-driver install workflow-hooks`
2. (Optional) Customize hooks in `.claude/commands/`
3. (Optional) Configure automation in `.spec-driver/config.yaml`
4. Use hooks as guides during implementation

## Philosophy

- **Customizable hooks, not prescriptive process**: Adapt to your team's needs
- **Configuration over convention**: Control automation level via metadata
- **Constitution enforcement**: ADRs/policies/standards embedded in workflow
- **Manual always valid**: Use hooks or work manually - your choice

## Constitution & Onboarding

Before starting, run:
```bash
spec-driver onboard
```

This shows:
- Core concepts (specs, deltas, phases, requirements)
- Workflow stages overview
- Active ADRs, policies, standards
- Project-specific conventions

## Workflow Hooks

### 1. Implementation Planning: `/supekku.plan`

**When**: After creating delta, before starting implementation

**Purpose**: Complete IP and DR, set up for execution

**What It Does**:
- Guides through DR completion (current/target behavior, hotspots)
- Helps break down work into phases
- Defines entry/exit criteria
- Checks relevant ADRs for guidance
- Sets delta to in-progress
- Handles commits per automation config

**Customization Examples**:
- Add team-specific research steps
- Integrate with project planning tools
- Adjust ADR checking strategy
- Modify commit behavior

**Automation Config**:
```yaml
automation:
  commit_strategy: per_phase  # Don't commit during planning
  agent_prepares_commits: false  # User writes commit messages
```

### 2. Phase Planning: `/supekku.phase`

[Similar structure for each command...]

### 3. Task Execution: `/supekku.task`

### 4. Phase Completion: `/supekku.phase-complete`

### 5. Delta Completion: `/supekku.delta-complete`

## Configuration

### IP Automation Metadata

Each IP can configure automation:

```yaml
schema: supekku.plan.overview
version: 1
plan: IP-XXX
delta: DE-XXX
automation:
  commit_strategy: per_task | per_phase | manual | on_demand
  agent_prepares_commits: boolean
  agent_stages_files: boolean
  agent_suggests_messages: boolean
  vcs: git | jj | other
  vcs_commands:
    commit: "git commit -m"
    stage: "git add"
    status: "git status"
    diff: "git diff"
  run_tests_before_commit: boolean
  run_lint_before_commit: boolean
phases: [...]
```

### Project Defaults

Set project-wide defaults in `.spec-driver/config.yaml`:

```yaml
automation:
  default_commit_strategy: per_phase
  default_vcs: git
  constitution_enforcement: strict

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

## VCS Support

### Git Workflow

[Example with git commands]

### Jj Workflow

[Example with jj commands, showing configuration]

### Custom VCS

[How to configure for other tools]

## Constitution Integration

### Discovery

Run `spec-driver onboard` to see active constitution.

### During Workflow

Commands automatically:
- Reference relevant ADRs
- Remind about policies
- Validate against standards

### Validation

Before delta completion:
```bash
spec-driver validate constitution --delta DE-XXX
```

Checks:
- ADR compliance
- Policy adherence
- Standard requirements (tests, lint, coverage)

## Customization Examples

### Example 1: Minimal Automation (Manual Workflow)

Team prefers full control:

```yaml
automation:
  commit_strategy: manual
  agent_prepares_commits: false
  agent_stages_files: false
  agent_suggests_messages: true  # Still helpful
```

Commands provide guidance but don't touch git.

### Example 2: Maximum Automation (Fast Iteration)

Solo developer wants speed:

```yaml
automation:
  commit_strategy: per_task
  agent_prepares_commits: true
  agent_stages_files: true
  run_tests_before_commit: false  # Run manually later
```

Commands handle all bookkeeping automatically.

### Example 3: Team with Jira Integration

Modify `.claude/commands/supekku-task.md`:

```markdown
## Task Completion

1. Ask which task completed
2. Update phase progress
3. Capture notes
4. **Prompt**: "Update Jira ticket [PROJECT-XXX]? [yes]"
5. If yes, guide Jira update
6. Handle commit per automation config
```

### Example 4: Custom Constitution Check

Add to `.claude/commands/supekku-plan.md`:

```markdown
## Team-Specific Constitution

Check our team ADRs:
- ADR-042: Always use descriptive task names
- ADR-051: Phase plans reviewed by tech lead

Prompt: "Have you reviewed with tech lead? [yes/no]"
```

## Migration from Auto-Created Phase-01

If you have existing deltas with phase-01 created at delta creation time,
no changes needed - they continue to work.

For new deltas:
1. `create delta` produces no phase
2. Complete IP first
3. Run `/supekku.phase` to create phase-01 with IP criteria

## Troubleshooting

### Hook Not Found

Install hooks: `spec-driver install workflow-hooks`

### Modified Hook Overwritten

Hooks preserve modifications by default. If overwritten:
1. Check for backup: `.claude/commands/supekku-plan.md.backup`
2. Re-customize from backup

### Automation Not Respected

Check IP frontmatter has `automation:` section. If missing, uses project defaults.

### Constitution Validation Fails

Common issues:
- Missing tests: Add VT artifacts
- Low coverage: Write more tests
- Lint errors: Run `just lint`
- ADR violations: Read relevant ADR, fix or request exception

## FAQ

**Q: Are workflow hooks required?**
A: No, completely optional. Manual workflow always supported.

**Q: Can I modify hooks?**
A: Yes! They're installed locally like templates for customization.

**Q: Will updates break my customizations?**
A: No, modifications preserved. You can review diffs and merge if desired.

**Q: Can I use workflow without agents?**
A: Hooks are designed for agents, but workflow stages apply to manual work too.

**Q: What if my team uses Mercurial/SVN/other VCS?**
A: Configure `vcs_commands` in automation metadata with your VCS commands.

## See Also

- PROD-011: Implementation Execution Workflow (spec)
- PROD-006: Phase Management (spec)
- PROD-010: CLI Improvements (help system)
- `spec-driver help workflows` (after installation)
```

## Migration Checklist

When updating implementation-workflow.md:

- [ ] Add hook installation section
- [ ] Document automation configuration schema
- [ ] Replace hardcoded git commands with VCS-agnostic descriptions
- [ ] Add constitution integration (onboarding, validation)
- [ ] Show customization examples (at least 4 varied scenarios)
- [ ] Add jj workflow example alongside git
- [ ] Emphasize flexibility and customization throughout
- [ ] Update philosophy/principles section
- [ ] Add configuration reference section
- [ ] Add troubleshooting and FAQ sections
- [ ] Remove prescriptive "must" language
- [ ] Add "manual always valid" reminders

## Files to Create/Update

1. **Update**: `docs/implementation-workflow.md` (major revision per above)
2. **Create**: `.spec-driver/templates/implementation-plan-template.md` (add automation schema)
3. **Create**: `.spec-driver/templates/config.yaml` (project defaults)
4. **Create**: `.spec-driver/hooks/` (default hooks before installation)
   - `supekku-plan.md`
   - `supekku-phase.md`
   - `supekku-task.md`
   - `supekku-phase-complete.md`
   - `supekku-delta-complete.md`
5. **Update**: `specify/product/PROD-011/PROD-011.md` (replace with revised version)
