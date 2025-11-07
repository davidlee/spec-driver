# Delta Scope: Implementation Execution Workflow

**Requirements**: PROD-011 (FR-001 through FR-007)
**Related Docs**: `docs/implementation-workflow.md`

---

## Objectives

1. Remove phase-01 auto-creation from delta creation
2. Enable `create phase` to work when no phases exist
3. Implement 5 slash commands for guided implementation workflow
4. Maintain backward compatibility with existing deltas

---

## Scope of Changes

### 1. Delta Creation Changes (FR-001)

**Files to Modify**:
- `supekku/scripts/lib/changes/creation.py` - `create_delta()` function
- `supekku/cli/create.py` - `create_delta` command
- `supekku/scripts/lib/changes/creation_test.py` - Update tests

**Changes**:
- Remove phase-01 creation logic from `create_delta()`
- Update delta creation to produce only 4 artifacts:
  1. Delta file (DE-XXX.md)
  2. Design Revision (DR-XXX.md)
  3. Implementation Plan (IP-XXX.md)
  4. Notes file (notes.md)
- Add `--create-phase` flag for backward compatibility (optional)
- Update tests to verify no phase directory created

**Migration Consideration**:
- Existing deltas with phase-01 unaffected
- New deltas start clean, phase created via command

---

### 2. Phase Creation Enhancement (FR-002)

**Files to Modify**:
- `supekku/scripts/lib/changes/creation.py` - `create_phase()` function
- `supekku/scripts/lib/changes/creation_test.py` - Add test cases

**Changes**:
- Modify `create_phase()` to handle empty phases directory:
  ```python
  def determine_next_phase_number(plan_dir: Path) -> int:
      """Determine next phase number, returns 1 if no phases exist."""
      phases_dir = plan_dir / "phases"
      if not phases_dir.exists():
          return 1

      existing = list(phases_dir.glob("phase-*.md"))
      if not existing:
          return 1

      numbers = [extract_phase_num(p) for p in existing]
      return max(numbers) + 1
  ```

- Ensure entry/exit criteria copied from IP even for phase-01
- Test with plans that have zero phases

**Verification**:
- Unit test: create phase on plan with no phases → phase-01
- Unit test: phase-01 has entry/exit from IP
- Integration test: full flow (create delta → plan → phase)

---

### 3. Slash Command Implementation (FR-003 through FR-007)

**Files to Create**:
```
.claude/commands/
├── supekku-plan.md
├── supekku-phase.md
├── supekku-task.md
├── supekku-phase-complete.md
└── supekku-delta-complete.md
```

**Command Structure**:
Each command is a markdown file that expands to a detailed prompt. Structure:

```markdown
# /supekku.<command>

[Agent instructions for this workflow stage]

## Context to Gather
- Current delta state
- Files to read
- State to check

## Workflow Steps
1. Step 1
2. Step 2
...

## Success Criteria
- What to verify
- What to update

## Commit Message Template
commit-type: description
```

---

#### 3a. `/supekku.plan` Command (FR-003)

**File**: `.claude/commands/supekku-plan.md`

**Purpose**: Guide through IP/DR completion, set delta in-progress

**Agent Prompt Outline**:
```markdown
You are helping the user flesh out their implementation plan and design revision.

## Read Current State
1. Read delta file (DE-XXX.md) for scope
2. Read design revision (DR-XXX.md) - likely template
3. Read implementation plan (IP-XXX.md) - likely template

## Guide User Through

### Design Revision Completion
1. Current Behavior Analysis
   - What code currently does
   - Pain points or issues
   - Code hotspots affected

2. Target Behavior Specification
   - What should change
   - New capabilities
   - Expected outcomes

3. Architecture Impact
   - Packages/modules affected
   - New dependencies
   - Migration considerations

### Implementation Plan Completion
1. Phase Breakdown
   - How many phases? (default 1-3)
   - What's the objective of each?
   - What are the entry/exit criteria?

2. Testing Strategy
   - What verification artifacts needed?
   - Unit/integration/manual tests?
   - Coverage expectations?

3. Dependencies
   - Blocking work?
   - Concurrent deltas?
   - External dependencies?

## Research as Needed
- Explore codebase to understand current behavior
- Review related specs/requirements
- Check existing deltas for patterns

## Update Files
1. DR-XXX.md - Fill all sections
2. IP-XXX.md - Complete phase overview table and criteria
3. DE-XXX.md - Set status: in-progress

## Prepare Commit
Message: "plan: complete IP and DR for DE-XXX"
Files: DR-XXX.md, IP-XXX.md, DE-XXX.md
```

---

#### 3b. `/supekku.phase` Command (FR-004)

**File**: `.claude/commands/supekku-phase.md`

**Purpose**: Create phase with entry/exit from IP, break down into tasks

**Agent Prompt Outline**:
```markdown
You are helping the user create and plan a phase.

## Read Current State
1. Read IP-XXX.md to find plan metadata
2. Check existing phases in phases/ directory
3. Read phase overview table from IP

## Create Phase
Run: `spec-driver create phase --plan IP-XXX`

This will:
- Create phases/phase-0N.md (numbered automatically)
- Copy entry/exit criteria from IP
- Set up frontmatter

## Validate Entry Criteria
For each entry criterion copied from IP:
1. Check if satisfied
2. If not, identify what's needed
3. Either:
   - Help satisfy it now
   - Update criterion if inappropriate
   - Confirm user wants to proceed anyway

## Break Down Objective
Read phase objective from IP.
Suggest 5-10 concrete tasks:
1. Task 1
2. Task 2
...

Order by dependency.
Refine with user input.

## Update Phase File
Fill task list in phases/phase-0N.md

## Prepare Commit
Message: "phase: create phase-0N for IP-XXX"
Files: phases/phase-0N.md
```

---

#### 3c. `/supekku.task` Command (FR-005)

**File**: `.claude/commands/supekku-task.md`

**Purpose**: Update phase progress, maintain documentation

**Agent Prompt Outline**:
```markdown
You are helping the user track task completion during implementation.

## Read Current Phase
1. Find current phase (highest numbered, not yet complete)
2. Read phases/phase-0N.md
3. Show task list with completion status

## Capture Progress
1. Ask which task was completed
2. Prompt for notes:
   - What was implemented?
   - Any discoveries?
   - Any concerns?

## Update Phase File
1. Increment task count in metadata
2. Add notes to phase notes section
3. Update completion percentage

## Remind About Commits
Guide proper git workflow:
1. Commit code changes separately (feat/fix/refactor)
2. Then commit phase progress

## Success
- Phase card updated
- Progress documented
- User reminded of commit hygiene
```

---

#### 3d. `/supekku.phase-complete` Command (FR-006)

**File**: `.claude/commands/supekku-phase-complete.md`

**Purpose**: Validate phase completion, summarize in delta

**Agent Prompt Outline**:
```markdown
You are helping the user complete a phase.

## Validate Completion
1. Read phases/phase-0N.md
2. Check all tasks complete
3. Verify exit criteria:
   - Tests passing? Run `just test`
   - Linters clean? Run `just lint`
   - Each criterion satisfied?

## Summarize Phase
Extract key information:
- What was accomplished
- Important decisions made
- Follow-up items identified

Add summary to DE-XXX.md:
```
## Phase N Summary (completed YYYY-MM-DD)
- Accomplishment 1
- Accomplishment 2
- Decision: X because Y
- Follow-up: ISSUE-XXX created for Z
```

## Prepare Commit
Message: "complete: phase-0N of IP-XXX"
Files: phases/phase-0N.md, DE-XXX.md
```

---

#### 3e. `/supekku.delta-complete` Command (FR-007)

**File**: `.claude/commands/supekku-delta-complete.md`

**Purpose**: Final validation, sync, complete delta

**Agent Prompt Outline**:
```markdown
You are helping the user complete a delta.

## Validate Completeness
1. All phases complete?
2. All requirements implemented?
3. All verification artifacts executed?

## Run Sync
$ spec-driver sync

Verify:
- Registries updated
- Requirements show implemented_by
- Coverage evidence linked

## Validate Coverage
For each requirement:
- Has implemented_by: DE-XXX?
- Has verified_by: VT/VA/VH-XXX?
- Has status: verified?

## Run Workspace Validation
$ spec-driver validate

Check for:
- Broken relationships
- Missing artifacts
- Schema violations

## Guide Completion
Prompt user to run:
$ spec-driver complete delta DE-XXX

If it fails:
- Explain what's missing
- Help resolve issues
- Retry

## Verify Final State
Check delta status = completed

## Prepare Final Commit
Message: "complete: DE-XXX implementation"

Summary of:
- What was delivered
- Requirements satisfied
- Tests passing
- Coverage updated
```

---

## Implementation Checklist

### Phase 1: Core Changes
- [ ] Remove phase-01 creation from `create_delta()`
- [ ] Add `--create-phase` flag (backward compat)
- [ ] Update `create_phase()` to handle empty phases dir
- [ ] Write unit tests for both changes
- [ ] Update integration tests
- [ ] Verify existing deltas unaffected

### Phase 2: Command Implementation
- [ ] Create `.claude/commands/supekku-plan.md`
- [ ] Create `.claude/commands/supekku-phase.md`
- [ ] Create `.claude/commands/supekku-task.md`
- [ ] Create `.claude/commands/supekku-phase-complete.md`
- [ ] Create `.claude/commands/supekku-delta-complete.md`
- [ ] Test each command in isolation
- [ ] Test full workflow end-to-end

### Phase 3: Documentation & Verification
- [ ] Update `docs/implementation-workflow.md` (already done)
- [ ] Update `supekku/INIT.md` with new workflow
- [ ] Update ADR if needed (command naming, state management)
- [ ] Pilot test with 2-3 developers
- [ ] Gather feedback and iterate
- [ ] Update based on feedback

### Phase 4: Migration & Rollout
- [ ] Document migration path in release notes
- [ ] Create example delta using new workflow
- [ ] Record walkthrough video/screencast
- [ ] Announce to team
- [ ] Monitor adoption metrics

---

## Testing Strategy

### Unit Tests

**Delta Creation** (`creation_test.py`):
```python
def test_create_delta_without_phase():
    """Delta creation produces 4 files, no phases directory."""
    result = create_delta(...)
    assert (delta_dir / "DE-XXX.md").exists()
    assert (delta_dir / "DR-XXX.md").exists()
    assert (delta_dir / "IP-XXX.md").exists()
    assert (delta_dir / "notes.md").exists()
    assert not (delta_dir / "phases").exists()

def test_create_delta_with_phase_flag():
    """--create-phase flag creates phase-01."""
    result = create_delta(..., create_phase=True)
    assert (delta_dir / "phases" / "phase-01.md").exists()
```

**Phase Creation** (`creation_test.py`):
```python
def test_create_phase_empty_plan():
    """create_phase works on plan with no existing phases."""
    result = create_phase(plan_id="IP-099")
    assert result.phase_id == "IP-099.PHASE-01"
    assert "entrance_criteria" in result.content  # Copied from IP

def test_create_phase_with_existing():
    """create_phase increments from existing phases."""
    # Setup: create phase-01, phase-02
    result = create_phase(plan_id="IP-099")
    assert result.phase_id == "IP-099.PHASE-03"
```

### Integration Tests

**Full Workflow** (manual or automated):
1. `create delta "Test workflow"`
2. Verify 4 files, no phases
3. `/supekku.plan` → verify IP/DR filled
4. `/supekku.phase` → verify phase-01 created with IP criteria
5. Complete tasks manually
6. `/supekku.task` → verify progress tracked
7. `/supekku.phase-complete` → verify summary in delta
8. `/supekku.delta-complete` → verify validation and completion

### User Acceptance Testing

- 3 developers use new workflow for real deltas
- Observe friction points
- Gather feedback on command clarity
- Measure completion rates and quality

---

## Risks & Mitigations

### Risk: Breaking Existing Workflows
**Likelihood**: Low
**Impact**: High
**Mitigation**:
- Backward compatibility via `--create-phase` flag
- Existing deltas with phase-01 unaffected
- Manual workflow still works without commands
- Thorough testing before release

### Risk: Command Adoption Too Low
**Likelihood**: Medium
**Impact**: Medium
**Mitigation**:
- Make commands genuinely helpful, not just reminders
- Provide clear documentation and examples
- Gather feedback early and iterate
- Don't force adoption - let value drive usage

### Risk: Commands Too Verbose/Slow
**Likelihood**: Medium
**Impact**: Low
**Mitigation**:
- Keep prompts focused on essentials
- Allow skipping steps user already completed
- Support manual workflow as faster alternative
- Iterate based on user feedback

### Risk: State Management Complexity
**Likelihood**: Low
**Impact**: Medium
**Mitigation**:
- Infer all state from artifacts (no hidden state)
- Commands are idempotent where possible
- Clear error messages if prerequisites missing
- Document state expectations in prompts

---

## Success Criteria

### Functional
- [ ] `create delta` produces 4 files (no phase)
- [ ] `create phase` works on empty plans
- [ ] All 5 commands functional
- [ ] Commands validate prerequisites
- [ ] Backward compatibility maintained
- [ ] Tests passing

### Quality
- [ ] Commands used in 3+ pilot deltas successfully
- [ ] No regressions in existing deltas
- [ ] Documentation complete and clear
- [ ] User feedback 80%+ positive

### Adoption (3 months post-release)
- [ ] 70%+ of new deltas use at least one command
- [ ] 95%+ verification artifact completeness
- [ ] 20% reduction in delta lifecycle time
- [ ] 50% reduction in incomplete deltas

---

## Follow-up Work

### Enhancements (Future Deltas)
- Add `/supekku.research` for pre-planning investigation
- Integrate with IDE for inline progress updates
- Add workflow visualization (current stage diagram)
- Add command usage telemetry (privacy-preserving)

### Documentation Updates
- Create video walkthrough of new workflow
- Update onboarding guide for new developers
- Add workflow to `supekku/INIT.md`
- Create cheat sheet of command purposes

### Team Adoption
- Announce via team channel
- Office hours for questions
- Monitor early adoption and support
- Gather feedback for iteration

---

## Related Artifacts

- **Spec**: `specify/product/PROD-011/PROD-011.md`
- **Workflow Doc**: `docs/implementation-workflow.md`
- **Current Code**:
  - `supekku/scripts/lib/changes/creation.py`
  - `supekku/cli/create.py`
- **Tests**: `supekku/scripts/lib/changes/creation_test.py`
- **Commands**: `.claude/commands/supekku-*.md`
