---
id: mem.pattern.pylint.summary-workflow
name: Pylint Summary Workflow
kind: memory
status: active
memory_type: pattern
updated: "2026-03-07"
verified: "2026-03-07"
tags:
  - pylint
  - lint
  - workflow
summary:
  Use just pylint-files during implementation and just pylint-report before
  final full-repo verification; both persist full json and print compact summaries.
scope:
  paths:
    - Justfile
    - supekku/scripts/pylint_report.py
    - supekku/scripts/lib/core/pylint_report.py
  commands:
    - just pylint-files
    - just pylint-report
    - just pylint
provenance:
  sources:
    - kind: code
      ref: Justfile
    - kind: code
      ref: supekku/scripts/pylint_report.py
    - kind: code
      ref: supekku/scripts/lib/core/pylint_report.py
    - kind: delta
      ref: DE-058
---

# Pylint Summary Workflow

## Summary

- During implementation, run `just pylint-files <paths...>` on touched files.
- Before final verification, run `just pylint-report` for the full repo.
- Keep `just pylint` as the authoritative gate when you need the raw upstream
  behavior; use the summary commands to reduce rework and output scanning.

## Context

- `just pylint-report` writes full json to
  `.spec-driver/run/pylint/full.json` and prints:
  - score
  - total message count
  - top message symbols
  - files with most messages
  - first messages by severity
- `just pylint-files <paths...>` writes to
  `.spec-driver/run/pylint/files.json` with the same summary shape for touched
  files.
- This pattern supports the repo rule that touched files must not gain new
  warnings and should have their pre-existing warnings addressed.
