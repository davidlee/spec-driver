# Notes for DE-083

## 2026-03-09

### What was done
- Created `DE-083` as the follow-up delta for work intentionally left unresolved when closing `DE-055`.
- Scoped the delta around two linked concerns:
  - keeping the audit loop strongly biased toward authoritative spec reconciliation
  - tuning revision/spec authorship skills so audit findings flow into existing specs, revisions, or new specs with less ambiguity

### Boundaries
- `DE-055` remains the design/implementation record for routing, DR-loop, and close-out guidance already landed.
- `DE-079` remains the implementation home for runtime audit schema, validation, and completion gates.
- `DE-083` is the skill-authoring and workflow follow-through layer that should sit on top of those two deltas rather than duplicate them.

### Immediate next step
- Shape `DR-083` before creating phases.

### Verification
- `uv run spec-driver show delta DE-083` succeeded after the delta/DR/IP rewrites.
- The plan currently has three planned phases and no phase sheet yet, by design; phase creation is deferred until `DR-083` is current.

### DR shaping update
- Resolved the main design boundary in `DR-083`: DE-083 should strengthen existing skills rather than introduce a dedicated spec-authoring skill.
- Settled the branch order as `existing spec patch -> revision -> revision-led new spec`, keeping the new-spec case inside the existing `revision` audit disposition rather than reopening the `DE-079` contract.
- Identified direct governance/spec revision targets as `PROD-011` and `SPEC-151`, with `PROD-002` and `PROD-001` treated as collaborator surfaces to confirm during implementation.
