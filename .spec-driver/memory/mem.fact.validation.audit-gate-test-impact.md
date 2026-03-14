---
id: mem.fact.validation.audit-gate-test-impact
name: validator audit gate fires on requirement-bearing deltas
kind: memory
status: active
memory_type: fact
created: '2026-03-09'
updated: '2026-03-09'
tags: [validation, audit, testing]
summary: WorkspaceValidator._validate_audit_gate_coverage warns when a delta has applies_to.requirements but no completed
  conformance audit. Tests creating deltas with requirements must filter by level or message content, not assert exact issue
  counts.
scope:
  globs: [supekku/scripts/lib/validation/**]
  paths:
  - supekku/scripts/lib/validation/validator.py
  - supekku/scripts/lib/validation/validator_test.py
provenance:
  sources: [DE-079, 1d6f835]
verified: '2026-03-09'
---

# validator audit gate fires on requirement-bearing deltas

- `_validate_audit_gate_coverage` resolves `audit_gate` for every delta. Deltas with non-empty `applies_to.requirements` resolve `auto` → `required`.
- If no completed conformance audit with matching `delta_ref` exists → warning.
- **Test impact**: any test that creates a delta with requirements will see this warning unless a matching conformance audit is also created.
- Fix: filter assertions by `i.level == "error"` or exclude `"Audit gate" in i.message` rather than asserting exact issue counts.
