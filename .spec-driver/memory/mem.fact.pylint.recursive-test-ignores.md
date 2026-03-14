---
id: mem.fact.pylint.recursive-test-ignores
name: Pylint Recursive Test Ignores
kind: memory
status: active
memory_type: fact
updated: "2026-03-07"
verified: "2026-03-07"
tags: [pylint, lint, tests]
summary: pylint-per-file-ignores needs recursive glob patterns here; plain *_test.py only matches repo-root files and leaves nested test warnings unsuppressed.
scope:
  paths:
    - pyproject.toml
    - .venv/lib/python3.12/site-packages/pylint_per_file_ignores/_plugin.py
  commands: [just pylint, uv run pylint]
provenance:
  sources:
    - kind: code
      ref: pyproject.toml
      note: Current pylint per-file ignore configuration
    - kind: code
      ref: .venv/lib/python3.12/site-packages/pylint_per_file_ignores/_plugin.py
      note: "Plugin loads file matches via glob.glob(pattern, recursive=True)"
    - kind: delta
      ref: DE-058
---

# Pylint Recursive Test Ignores

## Summary

- `pylint-per-file-ignores` in this repo resolves patterns with recursive glob
  expansion.
- Use recursive test globs such as `**/*_test.py` and `**/test_*.py` in
  `pyproject.toml`.
- Do not use plain `*_test.py` if you expect nested test files to be matched.

## Context

- We confirmed this while fixing lint noise in [[DE-058]].
- Symptom: nested tests still reported `missing-function-docstring` and
  `protected-access` even though per-file ignores appeared to exist.
- Verification: after switching to recursive globs, `just pylint` dropped
  `missing-function-docstring` to 6 non-test occurrences.
