---
id: mem.fact.autobahn-independence
name: spec-driver must not depend on autobahn
kind: memory
status: active
memory_type: fact
created: '2026-03-22'
updated: '2026-03-22'
verified: '2026-03-22'
confidence: high
tags:
- architecture
- autobahn
- boundary
summary: spec-driver must never depend on autobahn for basic functionality; the dependency
  is strictly one-directional
---

# spec-driver must not depend on autobahn

The dependency between spec-driver and autobahn is strictly one-directional:

- **autobahn depends on spec-driver** — consumes workflow schemas, CLI contracts, artifact files
- **spec-driver must never depend on autobahn** — all spec-driver functionality must work without autobahn installed, running, or present

This means:
- No imports from autobahn in spec-driver code
- No runtime checks for autobahn presence
- Extension points for autobahn (e.g., `session` metadata on review round records) must be optional and opaque — spec-driver carries them but doesn't interpret them
- CLI commands, state machines, guards, and validation must function identically with or without autobahn
- Test suites must not require autobahn

If a feature seems to require autobahn awareness, the design is wrong — restructure so spec-driver provides the contract and autobahn consumes it.

Promote to [[POL-003]] if the boundary gets more complex or if violations are observed.
