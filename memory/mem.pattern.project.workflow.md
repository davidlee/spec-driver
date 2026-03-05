---
id: mem.pattern.project.workflow
name: Project Development Workflow
kind: memory
status: active
memory_type: pattern
updated: '2026-03-04'
verified: '2026-03-04'
confidence: high
tags:
- project
- workflow
summary: Project-owned development workflow stub. Defaults to the spec-driver core
  loop; edit to add local shortcuts, required steps, or ceremony overrides.
priority:
  severity: high
  weight: 10
provenance:
  sources:
  - kind: memory
    note: Default development loop (platform reference)
    ref: mem.pattern.spec-driver.core-loop
---

# Project Development Workflow

This project follows the [[mem.pattern.spec-driver.core-loop]] as its
default development workflow.

Edit this memory to customise. Common overrides:

- Additional CI/CD steps before closure
- Required review gates or sign-off steps
- Shortcuts for low-ceremony work (e.g. skip DR/IP for small fixes)
- Local naming conventions or branch strategies
