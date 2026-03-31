---
name: notes
description: "Records structured implementation notes on the active card after completing a task, phase, or unit of work. Captures what was done, surprises, open questions, and verification status. Use when finishing a coding task, completing a phase, or when the user asks to document progress."
---

## Workflow

1. **Find the card**: locate the active card with `spec-driver find card` if not already known.
2. **Write concise notes** on the card covering:
   - What was completed.
   - Surprises, adaptations, or rough edges encountered.
   - Follow-up actions and open questions.
   - Relevant commit hashes (or note uncommitted work).
   - Whether `.spec-driver` changes were committed per doctrine, or still pending with a reason.
   - Verification status: did the verification command pass since last code change, or are there outstanding errors?
3. **Capture durable knowledge**: if notes reveal a reusable fact, pattern, or gotcha that would save a future agent time, run `/capturing-memory` or `/maintaining-memory` before treating the unit as done.

### Example

```markdown
## Notes — Phase 02

- Implemented registry caching for `SpecRegistry.all_specs()`.
- Surprise: existing tests assumed fresh registry per call; adapted 3 tests.
- Commit: `a1b2c3d` (code + .spec-driver changes together).
- `just test` passes. `just lint` clean.
- Open: cache invalidation on file watch not yet wired — follow-up in next phase.
```
