---
name: notes
description: Whenever you complete a task or phase - record implementation notes.
---

Update the card with implementation notes.

If you don't know where it is, find it with `spec-driver find`.

be concise, but record:
- what's done
- any
  - surprises encountered or adaptations required
  - potential rough edges, omissions, or refactorings for later
  - follow-up actions advisable
  - open questions relating to completed or upcoming work
  - durable facts, patterns, or gotchas that should become a memory
  - relevant commit hash(es), or: uncommitted work
- if the verification command has run successfully since code was last modified, or:
  outstanding errors

If the note identifies a reusable fact/pattern/gotcha that would save a future
agent meaningful time, run `/capturing-memory` or `/maintaining-memory` before
you treat the task, phase, or delta as wrapped.
