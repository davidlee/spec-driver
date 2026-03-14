---
id: mem.concept.spec-driver.contract
name: Contracts
kind: memory
status: active
memory_type: concept
updated: "2026-03-06"
verified: "2026-03-06"
confidence: high
tags: [spec-driver, contracts]
summary: "Contracts are auto-generated API documentation — the canonical record of what the code actually exposes. Observed truth, not authored intent."
priority:
  severity: medium
  weight: 6
provenance:
  sources:
    - kind: adr
      ref: ADR-003
    - kind: adr
      ref: ADR-004
    - kind: doc
      ref: CLAUDE.md
---

# Contracts

## Role in the Loop

Contracts are generated as part of the **verify** step of the
[[mem.pattern.spec-driver.core-loop]]. They capture the observed API surface
of the code — what functions, classes, and interfaces actually exist.

## Key Distinction

Contracts are **observed truth** — generated deterministically from code.
[[mem.concept.spec-driver.spec|Specs]] are **intent/constraints**.
See [[mem.concept.spec-driver.truth-model]] for why this distinction matters.

## Properties

- **Derived and deterministic**: always safe to delete and regenerate
- **Canonical location**: `.contracts/` (with optional compatibility views)
- **Multi-language**: Go, Python, Zig, TypeScript (stub)

## When to Use Contracts vs Code

**Contracts excel at**: API comparison, understanding public surface quickly,
spotting patterns/inconsistencies, initial discovery.

**Code required for**: implementation details, rationale/comments, type
precision, relationships/usage patterns.

## Commands

```bash
uv run spec-driver sync                    # sync all languages
uv run spec-driver sync --check            # validate without writing
uv run spec-driver sync --language python  # specific language
```
