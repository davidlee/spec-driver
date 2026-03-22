---
id: mem.pattern.typechecking.ty-known-issues
name: 'ty typechecking: known false positives and workarounds'
kind: memory
status: active
memory_type: pattern
created: '2026-03-23'
updated: '2026-03-23'
verified: '2026-03-23'
confidence: high
tags:
- typechecking
- ty
- dx
summary: Known ty false positives and workarounds for typechecking the supekku codebase
scope:
  commands:
  - ty
  - typecheck
  - type
  globs:
  - supekku/**
---

# ty typechecking: known false positives and workarounds

## Running

```bash
ty check                    # from repo root
uv run ruff check supekku spec_driver  # lint (keep clean alongside ty)
```

Config lives in `pyproject.toml` under `[tool.ty.rules]`.
`unused-type-ignore-comment = "ignore"` is set because we use multiple type checkers.

## Known ty false positives (~169 remaining as of DE-126)

### 1. `pytest.fail()` / `pytest.skip()` — ~34 errors

ty misinterprets the `Never` return type in exception-raising contexts.
These are **not real errors**. Do not suppress line-by-line; wait for ty to fix.

Files: `supekku/cli/test_cli.py`, `supekku/cli/edit_test.py`, `supekku/scripts/lib/docs/python/variants_test.py`

### 2. YAML block parsing — dict inference failures — ~40+ errors

ty can't infer types through YAML-parsed nested dicts (e.g. `yaml.safe_load`
output). Functions like `_require_key`, `.get()` on parsed blocks, and
`__getitem__` on `dict[Unknown, Unknown]` trigger `invalid-argument-type`.

Files: `supekku/scripts/lib/blocks/revision.py`, `plan.py`, `verification.py`,
`workflow_metadata.py`

### 3. Pydantic `**kwargs` spreading — suppressed with `type: ignore`

When tests build a dict and spread it into a Pydantic model (`Model(**fm)`),
ty can't see through Pydantic's `@field_validator` coercion (e.g. `str` → `date`).

**Workaround**: `# type: ignore[invalid-argument-type]` on the spread line.
Already applied to: `memory/models_test.py`, `change_formatters_test.py`,
`memory_formatters_test.py`, `list_test.py`, `backlog/models_test.py`,
`drift_formatters_test.py`, `phase_model_test.py`, `table_utils_test.py`.

### 4. `invalid-assignment` on `Item` / `Mapping` subscripts — ~13 errors

ty doesn't track type widening for dicts after construction. Also can't assign
to subscripts on `Item` (from `python-frontmatter`).

### 5. `.lower()` on `bool | str` union — 4 errors

ty correctly flags `.lower()` on `bool`, but the code handles it at runtime.
Files: `supekku/scripts/lib/sync/adapters/base_test.py`

## Systemic fix patterns (applied in DE-126)

| Pattern | Fix | Impact |
|---|---|---|
| `RootOption` (`Path \| None`) passed to `Path` params | Widen signatures + `resolve_root()` helper | ~50 errors |
| `_FakeWorkspace` vs `Workspace` in diagnostics tests | `DiagnosticWorkspace` Protocol | ~50 errors |
| Frontmatter dicts inferred as `dict[str, str]` | Annotate as `dict[str, Any]` | ~45 errors |
| `registry.get()` returns `Spec \| None` without narrowing | `assert x is not None` guards | ~20 errors |
| `.label.plain` on Textual `str \| Text` | `_plain()` helper with `isinstance` check | ~14 errors |
| `RequirementRecord(**{**r.__dict__, ...})` | `dataclasses.replace()` | ~24 errors |
| Stale import `supekku.models.decision` | Fix to `supekku.scripts.lib.decisions.registry` | 1 error |
| Wrong relative imports in `validator.py` | Use absolute imports | 2 errors |
