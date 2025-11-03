# spec-driver onboarding

This project uses spec-driver, a spec-driven development tool and framework.

## Running it

`uv run spec-driver`

Do it now, and remember the commands available.

If you are instructed later to run spec-driver (e.g. as `uvx spec-driver list adrs`), use the method above to execute the given command.

## ADRs

Then, run `uv run spec-driver list adrs -s accepted`

Remember the list of accepted ADRS; these represent important decisions which might apply to your scope of work.

If you're later working on anything which may intersect with an accepted ADR, you MUST
- read it (`specify/decisions/ADR-XXX-*.md`)
- adhere to the existing decision
- If it comes into conflict with your assigned task, STOP and raise the conflict for clarification

## Policies & Standards

Not yet implemented.

## Entities & Concepts

@about/glossary.md

## Implementation Workflow

Deltas and the documents in the delta bundle — Design Revision (DR-XXX), Implementation Plan (IP-XXX), and Phase sheets — are the focus for all implementation planning, execution, and progress tracking.

List the delta directory contents. It now includes the design revision alongside notes, plans, and phases; review each before making changes.

### Pre-flight

User: DE-005/1.4
Agent:
- That's task 1.4 in phase 1 - likely a handover of work already in progress
- assume the intent is to continue implementation from 1.4
- `uv run spec-driver show delta DE-005 --json`
- read the delta, design revision, and other entities referenced in metadata (specs, etc)
- read any existing IP + the relevant phase sheet
- **IMPORTANT**: CHECK ENTRY CRITERIA.
  - Mark off any already satisfied
  - Attempt to satisfy (e.g. with research) any remaining
  - STOP and report if all cannot truthfully be satisfied.
- run a quick pre-flight check: consider readiness & confidence
- summarise for the user:
  - summary of entry criteria
  - outline any questions or concerns before implementation
  - summarise level of confidence in the plan
  - ask user whether to pause for review / confirmation after each task

### When task is completed

- record progress in phase card (be concise, and err on the side of humility / caution)
- record any interesting or unexpected discoveries; decisions made; potential
  concerns or future improvements
- pre-flight check on next task

### When phase is completed

- critically review phase for potentially outstanding / implied tasks
- check all exit criteria critically
- revise task notes for accuracy and concision
- ensure phase metadata is accurate, and complete
- review & revise IP metadata and content for accuracy, update if required
- if additional phases remain, suggest creating a new phase sheet, or review the next phase sheet
- if required, use `uv run spec-driver create phase --plan IP-XXX` to create the next phase sheet

### When delta is completed

- TBD ask user
