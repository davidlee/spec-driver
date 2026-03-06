---
name: audit-change
description: Perform verification/audit pass after implementation (or as discovery/backfill), reconcile against specs/contracts, and route findings into closure or follow-up change.
---
You are reconciling realised behavior with intended behavior.

Inputs:
- Delta/phase outputs, relevant specs, contracts, and verification artifacts.
- Ceremony/policy posture from generated agent docs.

Process:
1. Determine audit mode:
   - Conformance (post-implementation)
   - Discovery/backfill (existing code)
2. Gather evidence:
   - Tests and checks required by spec/delta/plan
   - Contract observations where relevant
3. Update verification coverage blocks to valid statuses:
   - `planned`, `in-progress`, `verified`, `failed`, `blocked`
4. Patch owning specs to match contracts and audit findings:
   - Update requirement/coverage statements that are now wrong
   - Record any unresolved drift explicitly
5. If your workflow uses standalone audit docs, record findings there as well.
6. Run:
   - `uv run spec-driver sync`
   - `uv run spec-driver validate`
7. Route outcomes:
   - If aligned: hand off to `/close-change`
   - If drift/gaps: create follow-up backlog/revision/delta and `/consult` if tradeoffs are material

Outcomes:
- Evidence is recorded in owning artifacts.
- Specs are reconciled to observed behavior before closure.
- Alignment status is explicit, with follow-up actions when not aligned.
