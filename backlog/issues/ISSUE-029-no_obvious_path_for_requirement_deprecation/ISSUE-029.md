---
id: ISSUE-029
name: no obvious path for requirement deprecation
created: '2026-02-20'
updated: '2026-02-20'
status: open
kind: issue
categories: []
severity: p3
impact: user
---

# no obvious path for requirement deprecation

The actual lifecycle
  semantics you’re worried about live in the supekku:verification.coverage@v1 blocks, and that schema
  explicitly supports status: planned|in-progress|verified|failed|blocked (so you have an honest way to say
  “this used to be verified, but is no longer upheld / needs re-verification”). That lines up with PROD-
  008/009’s “evidence overlay never silently discards history”.
Used blocked because supekku.verification.coverage@v1 doesn’t have an invalid status; the notes carry the
  “invalidated” intent explicitly.)

What we should probably have:
- clear doctrine (docs, agent workflows, etc)
- possibly explicit deprecation / superceded linkage

