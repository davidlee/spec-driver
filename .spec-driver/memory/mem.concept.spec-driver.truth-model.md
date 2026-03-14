---
id: mem.concept.spec-driver.truth-model
name: Truth Model
kind: memory
status: active
memory_type: concept
updated: "2026-03-06"
verified: "2026-03-06"
confidence: high
tags: [spec-driver, truth-model, contracts, specs]
summary: Contracts record observed truth (what code exposes). Specs express intent and constraints. Never let them become competing sources of truth.
priority:
  severity: high
  weight: 9
provenance:
  sources:
    - kind: adr
      ref: ADR-004
    - kind: adr
      ref: ADR-003
    - kind: doc
      note: "Contracts, Sync, and Truth section"
      ref: CLAUDE.md
---

# Truth Model

## The Critical Distinction

Spec-driver maintains two complementary views of the system:

|               | Specs                            | Contracts                    |
| ------------- | -------------------------------- | ---------------------------- |
| **Nature**    | Intent and constraints           | Observed truth               |
| **Source**    | Human-authored                   | Generated from code          |
| **Answers**   | What the system SHOULD be        | What the system IS           |
| **Stability** | Evergreen, evolves via revisions | Derived, regenerated on sync |

## The Rule

**Do not create competing sources of truth.**

- Specs should not duplicate full API signatures that contracts already capture
- Assembly specs should frame requirements as constraints that can be validated
  against contracts/code — not as authoritative copies of what the code exposes
- When specs and contracts disagree, that is a finding — not something to
  paper over

## In Practice

- Use [[mem.concept.spec-driver.contract|contracts]] for "what does the code expose?"
- Use [[mem.concept.spec-driver.spec|specs]] for "what requirements must the code satisfy?"
- Use [[mem.concept.spec-driver.audit|audits]] to detect and resolve disagreements
