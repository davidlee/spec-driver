---
id: mem.concept.spec-driver.ceremony.pioneer
name: Pioneer Ceremony Mode
kind: memory
status: active
memory_type: concept
updated: "2026-03-06"
verified: "2026-03-06"
confidence: high
tags: [spec-driver, ceremony, pioneer]
summary: "Low ceremony: ship and learn. Cards for most work, optional ADRs, minimal spec-driver overhead. Speed over traceability."
priority:
  severity: medium
  weight: 7
provenance:
  sources:
    - kind: adr
      ref: ADR-004
---

# Pioneer Ceremony Mode

## Intent

Ship and learn. Capture change with minimal overhead. Avoid process ceremony
that doesn't yet pay for itself.

## Activated Primitives

- **Kanban cards** (`T123-*.md`) — primary work tracking
- **ADRs** — when a decision genuinely matters (MVP policy layer)
- **Specs** — optional; usually assembly specs only, when helpful

## What's NOT Active

- Deltas, implementation plans, and phases are intentionally absent by default
- Backlog metadata linkage is optional and often manual
- No formal verification/audit cycle

## Typical Flow

```
card -> implement -> (optional ADR) -> done
```

## How Specs Behave Here

In pioneer mode, specs (if they exist) are **aspirational** — they describe
where you want to go, not necessarily what the system is today. This is fine.
The [[mem.concept.spec-driver.philosophy|idealised form]] where specs are truth
is something the project converges toward, not something it starts with.

## Agent Guidance

- Check `workflow.toml [cards]` for card conventions
- Do not create deltas or IPs unless explicitly asked
- If a significant change needs explicit design or planning, equivalent records
  may still exist outside the delta bundle
- If a decision has lasting impact, suggest an ADR
- Keep documentation lightweight — cards are the primary record
