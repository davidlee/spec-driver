---
id: ISSUE-044
name: "VCS abstraction scope \u2014 design depth and interface shape undefined"
created: "2026-03-06"
updated: "2026-03-06"
status: open
kind: issue
categories: []
severity: p3
impact: user
---

# VCS abstraction scope — design depth and interface shape undefined

## Context

PROD-011 FR-008 specifies a VCS abstraction layer (git, jj, etc.) but no design
doc, ADR, or spec addresses how deep the abstraction goes, what operations need
it, or what the interface looks like.

## Current State

Git is the only practical VCS today. No alternative VCS support has been needed.

## When to Act

Revisit if/when a non-git VCS (e.g. jj/Jujutsu) becomes a real requirement.
No design work or ADR needed until the need is felt.

## References

- PROD-011 FR-008
- DL-047.020
