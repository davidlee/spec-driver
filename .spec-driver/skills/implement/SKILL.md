---
name: implement
description: "Executes a defined task or implementation plan by reading the governing card and design doc, coding against the plan, running tests, and recording notes. Use when a delta, card, or implementation plan is ready for coding and the design/planning phase is complete."
---

## Workflow

1. **Load context**: find and read the governing card and design doc.
   - `spec-driver find card $ARGUMENTS`
   - Read the card, design doc, and implementation plan (if one exists).
   - If the plan is already in progress, skip `/preflight`.
2. **Retrieve memories**: run `/retrieving-memory` for files and subsystems you expect to touch.
   - `spec-driver list memories -p <path>` to surface glob-scoped memories.
3. **Check governance**: read `/doctrine` — verify the approach aligns with accepted ADRs, policies, and standards.
4. **Implement**: code against the plan, following delta-first execution flow by default.
   - The design doc is canon; the plan is guidance. If they conflict meaningfully, run `/consult`.
   - Treat revision-first as a concession path, not the default.
   - Treat ceremony mode as guidance posture, not runtime enforcement.
5. **Record progress**: run `/notes` after each complete unit of work.
   - If a unit reveals a durable gotcha, workflow, or invariant, run `/capturing-memory` or `/maintaining-memory` before considering that unit done.
6. **Handle obstacles**: if you encounter unforeseen blockers, run `/consult`.
7. **Close-out**: for delta completion, follow `uv run spec-driver complete delta` prerequisites (especially coverage readiness).
8. **Context limits**: if running low on context, stop before exhaustion and run `/continuation`.
