# Implementation Workflow Guide

**Status**: Proposed
**Target Spec**: PROD-011 (Implementation Execution Workflow)
**Related Specs**: PROD-002 (Delta Creation), PROD-006 (Phase Management)

---

## Problem Statement

### Current State

When `create delta` runs, it generates:
1. Delta file (DE-XXX.md)
2. Design Revision (DR-XXX.md)
3. Implementation Plan (IP-XXX.md)
4. **Phase 01 (phases/phase-01.md)** ← Created too early
5. Notes file (notes.md)

**The Issue**: Phase-01 is created before the IP is fleshed out.

Since then, we've added intelligence to `create phase` that copies entry/exit criteria from the IP into the new phase. This works perfectly for phases 2+ because the IP has been filled in. But phase-01 is created alongside the IP (both empty), so it can't benefit from this intelligence.

### Impact

- Phase-01 lacks entry/exit criteria copied from IP
- Manual duplication required to sync IP gates to phase-01
- Workflow friction for every delta
- Intelligence feature underutilized for the most common case (first phase)

---

## Target State

### New Delta Creation

`create delta` generates:
1. Delta file (DE-XXX.md) - template only
2. Design Revision (DR-XXX.md) - template only
3. Implementation Plan (IP-XXX.md) - template only
4. Notes file (notes.md) - empty
5. **No initial phase** - created later via slash command

### Guided Implementation Lifecycle

Five slash commands guide users through the full implementation lifecycle:

```
create delta → /supekku.plan → /supekku.phase → /supekku.task → /supekku.phase-complete → /supekku.delta-complete
```

---

## Workflow Commands

### 1. `/supekku.plan` - Implementation Planning

**When**: After `create delta`, before starting implementation

**Purpose**: Flesh out the implementation plan and prepare for execution

**Agent Actions**:
1. Read delta, DR, IP templates
2. Guide user through:
   - Fleshing out Design Revision:
     - Current behavior analysis
     - Target behavior specification
     - Architecture impact assessment
     - Code hotspots identification
   - Implementation Plan completion:
     - Phase breakdown
     - Entry/exit criteria for each phase
     - Dependencies and constraints
     - Testing strategy
3. Conduct any necessary research:
   - Code exploration for affected areas
   - Spec/requirement analysis
   - Related delta/audit review
4. Update delta status to `in-progress`
5. Commit changes with message: "plan: complete IP and DR for DE-XXX"

**Success Criteria**:
- DR sections filled with concrete details
- IP phase overview table complete with clear objectives
- Entry/exit criteria defined for all phases
- Delta status = in-progress
- Clean commit

**Example Invocation**:
```
User: /supekku.plan
Agent: I'll help you flesh out the implementation plan for DE-015.

Let me start by reading the delta scope...
[reads DE-015, DR-015, IP-015]

For the Design Revision, I need to understand:
1. What's the current behavior? [walks through codebase]
2. What's the target behavior? [analyzes requirements]
3. What code areas are affected? [identifies hotspots]

[Interactive Q&A to complete DR]

Now for the Implementation Plan...
[Guides through phase breakdown, criteria]

I've updated:
- DR-015.md (current/target behavior, hotspots)
- IP-015.md (3 phases with entry/exit criteria)
- DE-015.md (status: in-progress)

Ready to commit? [yes/no]
```

---

### 2. `/supekku.phase` - Phase Planning

**When**: Before starting work on a phase (including phase-01)

**Purpose**: Create phase sheet with entry criteria and task breakdown

**Agent Actions**:
1. Run `create phase --plan IP-XXX` to generate phase sheet
   - Automatically copies entry/exit criteria from IP
   - Creates phases/phase-0N.md with correct numbering
2. Review phase entry criteria with user
   - Check if all criteria are satisfied
   - If not satisfied, identify what needs to be done first
3. Break down phase objective into concrete tasks
   - Review phase objective from IP
   - Suggest 5-10 actionable tasks
   - Order tasks by dependency
4. Update phase sheet with task list
5. Commit: "phase: create phase-0N for IP-XXX"

**Success Criteria**:
- Phase file created with correct ID (IP-XXX.PHASE-0N)
- Entry/exit criteria copied from IP
- All entry criteria checked and satisfied
- Task list complete and ordered
- Clean commit

**Example Invocation**:
```
User: /supekku.phase
Agent: I'll create the next phase for IP-015.

Running: create phase --plan IP-015
✓ Created phases/phase-02.md (IP-015.PHASE-02)
✓ Copied entry/exit criteria from IP-015

Let me check the entry criteria:
1. [x] Phase 1 complete - verified
2. [x] Core registry implemented - verified
3. [ ] Database schema reviewed - NOT satisfied

Entry criterion 3 is not satisfied. Should we:
a) Review database schema now
b) Proceed anyway (risky)
c) Update entry criteria

[Interactive resolution]

Now let me break down the phase objective into tasks:
Phase Objective: "Implement CLI commands for registry access"

Suggested tasks:
1. Add list command for registry items
2. Add show command for registry detail
3. Implement filtering options
4. Add JSON output support
5. Write unit tests for CLI commands
6. Update CLI documentation

[Refine with user]

Ready to commit? [yes/no]
```

---

### 3. `/supekku.task` - Task Execution

**When**: During phase execution, as you complete tasks

**Purpose**: Remind user to update phase card and prepare commits

**Agent Actions**:
1. Read current phase sheet
2. Show task list with current completion status
3. Ask which task was just completed
4. Prompt user to update phase notes with:
   - What was done
   - Any discoveries or decisions
   - Any concerns or blockers
5. Remind about commit best practices
6. Optionally help prepare commit message

**Success Criteria**:
- Phase card metadata updated (tasks completed count)
- Phase notes updated with progress
- User reminded of commit hygiene
- Context maintained for next task

**Example Invocation**:
```
User: /supekku.task
Agent: Let me check your progress on phase-02...

Current status: 3/6 tasks completed (50%)
✓ 1. Add list command for registry items
✓ 2. Add show command for registry detail
✓ 3. Implement filtering options
[ ] 4. Add JSON output support
[ ] 5. Write unit tests for CLI commands
[ ] 6. Update CLI documentation

Which task did you just complete? [4]

Great! Let me update the phase card.

What should I note about this task?
- What did you implement?
- Any interesting discoveries?
- Any concerns or questions?

[Capture notes]

Updated phases/phase-02.md:
- Progress: 4/6 (67%)
- Notes: Added JSON output support via --json flag...

Remember to commit your code changes separately:
  git add supekku/cli/list.py supekku/cli/show.py
  git commit -m "feat(cli): add JSON output support"

Then commit phase progress:
  git add phases/phase-02.md
  git commit -m "progress: complete task 4 - JSON output support"
```

---

### 4. `/supekku.phase-complete` - Phase Completion

**When**: When all phase tasks are complete

**Purpose**: Validate phase completion and document results

**Agent Actions**:
1. Review phase for completion:
   - All tasks marked complete
   - Exit criteria satisfied
   - Phase notes complete and accurate
2. Update phase metadata:
   - Set completion status
   - Verify all entry/exit criteria checked
3. Summarize phase in delta (DE-XXX.md):
   - What was accomplished
   - Key decisions or discoveries
   - Any follow-up items
4. Run linters and tests (remind user)
5. Prepare commit: "complete: phase-0N of IP-XXX"

**Success Criteria**:
- All phase tasks completed
- All exit criteria satisfied
- Phase summary added to delta
- Linters and tests passing
- Clean commit

**Example Invocation**:
```
User: /supekku.phase-complete
Agent: Let me verify phase-02 is ready for completion...

Checking tasks: 6/6 ✓
Checking exit criteria:
1. [x] CLI commands implemented - verified
2. [x] Tests written and passing - checking...
3. [x] Documentation updated - verified

Running verification:
$ just test
✓ 156/156 tests passing

$ just lint
✓ No issues

Phase-02 is complete! Let me summarize for the delta...

[Generates summary based on phase notes]

Updated DE-015.md:
## Phase 2 Summary (completed 2025-11-04)
- Implemented CLI list/show commands with filtering
- Added JSON output support for automation
- Discovered: filtering by status requires enum validation
- All tests passing, documentation updated

Ready to commit? [yes/no]
```

---

### 5. `/supekku.delta-complete` - Delta Completion

**When**: After all phases complete, ready to mark delta done

**Purpose**: Final validation and delta completion

**Agent Actions**:
1. Validate delta completeness:
   - All phases complete
   - All requirements implemented
   - All verification artifacts executed
2. Run workspace sync:
   - `spec-driver sync`
   - Update registries
3. Validate coverage:
   - Check coverage metadata up to date
   - All implemented requirements have `verified_by`
   - All verification artifacts have status
4. Run workspace validation:
   - `spec-driver validate`
   - Check for broken relationships
5. Guide user through `complete delta` command
6. Verify final status = completed
7. Prepare final commit: "complete: DE-XXX implementation"

**Success Criteria**:
- All phases completed
- All verification artifacts executed and documented
- Coverage metadata accurate and complete
- Registries synced
- Workspace validation passing
- Delta status = completed
- Clean final commit

**Example Invocation**:
```
User: /supekku.delta-complete
Agent: Let me verify DE-015 is ready for completion...

Phase Status:
✓ Phase-01: complete
✓ Phase-02: complete
✓ Phase-03: complete

Verification Artifacts:
✓ VT-015-001: verified (unit tests passing)
✓ VT-015-002: verified (integration tests passing)
✓ VA-015-001: verified (agent validation complete)

Running sync...
$ spec-driver sync
✓ Registries updated
✓ Requirements registry: 2 updated
✓ Coverage evidence linked

Checking coverage metadata...
PROD-010.FR-012: ✓ implemented_by: DE-015, verified_by: VT-015-001
PROD-010.FR-013: ✓ implemented_by: DE-015, verified_by: VT-015-002

Running validation...
$ spec-driver validate
✓ No issues found

Everything looks good! Ready to complete the delta.

Run: spec-driver complete delta DE-015

[Waits for user]

Delta status verified: completed ✓

Let me prepare the final commit...

Commit message:
complete: DE-015 implementation

- Implemented help system with core/project docs
- Added help command with 3 subcommands
- All tests passing (168/168)
- All requirements verified
- Coverage metadata updated

Ready to commit? [yes/no]
```

---

## Flow Diagram

```
┌─────────────────┐
│  create delta   │ Creates: DE-XXX, DR-XXX, IP-XXX, notes.md
└────────┬────────┘         (templates only, no phase-01)
         │
         v
┌─────────────────┐
│ /supekku.plan   │ Fleshes out DR + IP, sets delta in-progress
└────────┬────────┘ Commit: "plan: complete IP and DR for DE-XXX"
         │
         v
┌─────────────────┐
│ /supekku.phase  │ Creates phase-01 with entry/exit from IP
└────────┬────────┘ Commit: "phase: create phase-01 for IP-XXX"
         │
         v
   ┌─────────────────────┐
   │  Implementation     │
   │  (code + tests)     │
   └──────────┬──────────┘
              │
         ┌────v────┐
         │ /supekku│  Periodically during implementation
         │ .task   │  Updates phase progress, reminds about commits
         └────┬────┘
              │
              v
   ┌──────────────────────┐
   │  More implementation │
   └──────────┬───────────┘
              │
         ┌────v────┐
         │ /supekku│ (repeat as needed)
         │ .task   │
         └────┬────┘
              │
              v
┌────────────────────────┐
│ /supekku.phase-complete│ Validates phase, summarizes in delta
└────────┬───────────────┘ Commit: "complete: phase-01 of IP-XXX"
         │
         v
    ┌─────────────┐
    │ More phases?│
    └─────┬───────┘
          │
      ┌───v───┐
      │  yes  │─────> Back to /supekku.phase
      └───────┘       (creates phase-02, etc)
          │
      ┌───v───┐
      │   no  │
      └───┬───┘
          │
          v
┌─────────────────────────┐
│ /supekku.delta-complete │ Final validation, sync, complete delta
└─────────────────────────┘ Commit: "complete: DE-XXX implementation"
```

---

## Benefits

### 1. **Phase-01 Gets Full Intelligence**
- Entry/exit criteria copied from filled-in IP
- Same intelligent workflow as phases 2+
- No manual duplication needed

### 2. **Guided Workflow Reduces Friction**
- Clear commands for each stage
- Agent provides context-aware guidance
- Reduces "what do I do now?" moments

### 3. **Better Documentation**
- Phase notes remind users to document progress
- Delta summaries built incrementally
- Commit messages follow conventions

### 4. **Quality Gates**
- Entry criteria checked before phase start
- Exit criteria validated before phase complete
- Coverage validated before delta complete

### 5. **Flexibility**
- Users can still work manually if preferred
- Commands are optional helpers, not requirements
- Workflow adapts to delta complexity

---

## Migration Path

### For Existing Deltas with Phase-01

No changes required. Existing phase-01 files continue to work.

### For New Deltas

After upgrading spec-driver:

1. `create delta <description>` - no phase-01 created
2. `/supekku.plan` - flesh out IP/DR
3. `/supekku.phase` - create phase-01 (gets entry/exit from IP)
4. Continue with implementation

### Backward Compatibility

- Old deltas with phase-01 created at delta creation continue to work
- `create phase` works whether phase-01 exists or not
- Workflow commands are purely additive (don't break existing processes)

---

## Implementation Notes

### create phase Enhancement

Must handle case where no phases exist yet:
- Check for existing phases in plan directory
- If none exist, create phase-01
- If phases exist, create next numbered phase
- Always copy entry/exit criteria from IP if available

### Slash Command Structure

Commands live in `.claude/commands/`:
- `supekku-plan.md`
- `supekku-phase.md`
- `supekku-task.md`
- `supekku-phase-complete.md`
- `supekku-delta-complete.md`

Each command expands to a detailed prompt guiding the agent through the workflow stage.

### State Tracking

Commands check current state:
- Delta status (planned → in-progress → completed)
- IP completion (empty vs fleshed out)
- Phase existence and status
- Verification artifact status

No additional state files needed - everything inferred from existing artifact state.

---

## Open Questions

1. Should `/supekku.plan` be mandatory or optional?
   - **Proposal**: Optional but highly recommended
   - Users can proceed directly to implementation if IP is simple

2. Should we prevent `create phase` if IP is empty?
   - **Proposal**: No, allow but warn
   - Sometimes users know what they're doing

3. Should delta completion require all verification artifacts?
   - **Proposal**: Yes, but allow `--force` override
   - Same pattern as current `complete delta` command

4. Should we support phase-01 auto-creation via flag?
   - **Proposal**: Yes, add `--create-phase` flag to `create delta`
   - For users who prefer old workflow

---

## Success Metrics

- **Adoption**: 70%+ of new deltas use workflow commands
- **Quality**: Delta completion time reduced by 20%
- **Coverage**: 95%+ of deltas have complete verification artifacts
- **Satisfaction**: User survey shows 80%+ find workflow helpful
- **Error Reduction**: 50% fewer incomplete deltas

---

**Next Steps**:
1. Create PROD-011 spec for Implementation Execution Workflow
2. Create requirements (FR-001 through FR-006)
3. Create delta to implement changes
4. Write slash command prompts
5. Test workflow with pilot users
