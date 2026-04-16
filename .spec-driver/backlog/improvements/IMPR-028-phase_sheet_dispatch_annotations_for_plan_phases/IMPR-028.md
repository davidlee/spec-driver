---
id: IMPR-028
name: Phase sheet dispatch annotations for plan-phases
created: "2026-04-16"
updated: "2026-04-16"
status: idea
kind: improvement
---

# Phase sheet dispatch annotations for plan-phases

## Summary

Add optional fields to phase sheet task schema that `/plan-phases` can populate
to give `/dispatch` better signals for batching, model routing, and review
granularity.

## Proposed Fields

- `parallelizable: true|false` — whether task can run concurrently with others
- `complexity: low|medium|high` — influences model routing (high → opus)
- `touches: [list of file globs]` — file scope for overlap detection
- `review: tight|normal` — review granularity hint

## Motivation

DE-132 (`/dispatch` skill) initially infers these from existing phase sheet
structure. Explicit annotations from `/plan-phases` would improve dispatch
quality and reduce orchestrator guesswork.

## Relations

- Motivated by: DE-132 (DEC-132-01, resolved question on phase sheet fields)
- Applies to: `/plan-phases` skill, phase sheet schema

