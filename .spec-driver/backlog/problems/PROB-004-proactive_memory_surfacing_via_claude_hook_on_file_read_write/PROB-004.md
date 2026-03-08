---
id: PROB-004
name: Proactive memory surfacing via Claude hook on file read/write
created: '2026-03-08'
updated: '2026-03-08'
status: captured
kind: problem
---

# Proactive memory surfacing via Claude hook on file read/write

## Problem

Agents routinely fail to consult spec-driver memories before modifying
unfamiliar subsystems. The `/retrieving-memory` skill exists but requires
agent discipline — agents must remember to invoke it, and often don't.

The result is preventable mistakes: agents repeat known gotchas, violate
established patterns, or miss constraints that a relevant memory would
have surfaced. The `mem.gotcha.textual.tab-key-handling` memory from
DE-061 Phase 2 is a concrete example — without it, a future agent would
hit the same Textual Tab key trap.

## Proposed Direction

A Claude pre-hook on Read/Write tool calls that:

1. Extracts the file path from the hook input
2. Checks spec-driver's memory system for memories whose `scope.globs`
   match the file path
3. If high-value matches exist, injects a terse suggestion into context
   (memory ID + one-line summary, not the full content)

The memory selection infrastructure already exists: `scope.globs` is a
first-class field on memory records, and `selection.py` implements glob
matching with specificity scoring (paths=3 > globs=2 > commands=1 >
tags=0). The hook would call into this existing system.

## Prior Art

- `artifact_event.py` (DE-060): Claude hook that processes tool calls,
  extracts file paths and artifact IDs, emits structured events. Proves
  the hook→file-path→domain-logic pipeline works.
- `selection.py`: Full glob matching with `_glob_match`,
  `_matches_globs`, specificity scoring, priority/criticality ranking.
- Existing memories with `scope.globs` (e.g. `["src/auth/**"]` in tests).

## Open Design Questions

1. **Latency**: `uv run spec-driver` startup cost on every Read/Write
   may be unacceptable. Options:
   - Lightweight standalone script that reads memory files directly and
     uses the matching logic (no CLI startup)
   - Precomputed index file (glob → memory IDs), regenerated when
     memories change
   - Accept the latency (measure first — it may be fine)

2. **Write-only vs read+write**: Reads are very frequent and
   exploratory. Writes are lower-volume and higher-stakes. Write-only
   hooks would have better signal-to-noise. But reads are when agents
   form their understanding — surfacing a gotcha before they even start
   coding has value.

3. **Noise and deduplication**: If 5 memories match `supekku/tui/**`,
   the agent gets the same suggestions on every file touch. Needs
   per-conversation or per-session dedup. Claude hooks lack session
   state, so this requires a sidecar file
   (`.spec-driver/run/memory-hints-seen.json` or similar), or
   accepting some repetition.

4. **Injection format**: The suggestion should be terse — memory ID +
   one-line summary. The agent decides whether to read it. But how
   terse? Just the ID? ID + summary? ID + summary + "consult before
   modifying"?

5. **Filtering threshold**: Not all matching memories are worth
   surfacing on every file touch. Should the hook filter by:
   - Priority/criticality (only `critical` or `high`)?
   - Memory type (only `gotcha` and `pattern`, not `concept`)?
   - Specificity score (only direct glob matches, not `**` catch-alls)?
   - Some combination?

6. **Interaction with existing skills**: If the hook surfaces a memory
   suggestion and the agent reads it, does that satisfy the
   `/retrieving-memory` trigger? Or should the skill still fire
   independently? Risk of double-surfacing vs risk of gaps.

## Constraints

- Must not noticeably degrade tool call latency in the common case
  (no matches)
- Must not flood context with low-value suggestions
- Must work with the existing memory schema — no schema changes
  required (scope.globs already exists)
- Should degrade gracefully if memories have no globs (just no
  suggestions, not errors)
