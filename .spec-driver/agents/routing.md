# Skill Routing

Choose AND INVOKE the governing skill before doing substantive work. Do not respond,
explore, inspect files, or start implementation until you have decided.

If you skip routing because the task feels familiar, simple, or urgent — stop.
That is a routing failure.

## Routing Table (priority order)

1. **spec-driver entities or CLI** → `/spec-driver`
2. **mandatory spec-driver process guidance** → /using-spec-driver
3. **"what is the right way here?"**, unfamiliar subsystem, assumption risk → `/retrieving-memory`; add `/doctrine` when governance matters
4. **substantive new work, path unclear** → `/preflight`
5. **code-changing intent, no governing artefact** → `/scope-delta` (or `/shape-revision` first when revision-first governance applies)
6. **delta exists, DR/IP/phase incomplete** → `/draft-design-revision` then `/plan-phases` after DR approved
7. **delta phase active, planning artefacts exist** → `/execute-phase`
8. **implementation complete, reconciliation needed** → `/audit-change` then `/close-change`

## Default Stance

- If unsure, route to the stricter skill, not the looser one. (probably /using-spec-driver)
- Do not implement without a governing artefact (card, delta, or revision).
- `/using-spec-driver` has extended guardrails and failure-mode guidance.
