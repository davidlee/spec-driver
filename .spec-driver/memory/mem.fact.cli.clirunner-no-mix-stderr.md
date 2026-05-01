---
id: mem.fact.cli.clirunner-no-mix-stderr
name: CliRunner no longer accepts mix_stderr kwarg
kind: memory
status: active
memory_type: fact
created: '2026-05-01'
updated: '2026-05-01'
verified: '2026-05-01'
confidence: high
tags:
- cli
- typer
- testing
- gotcha
summary: "typer.testing.CliRunner() in this repo's pinned Click rejects mix_stderr=False as TypeError; stderr is split by default \u2014 pass nothing."
scope:
  globs:
    - supekku/cli/**
    - supekku/**/*_test.py
  commands:
    - uv run python -m pytest
provenance:
  sources:
    - DE-135
    - supekku/cli/list_test.py
---

# CliRunner no longer accepts mix_stderr kwarg

## Fact

`typer.testing.CliRunner` (which delegates to `click.testing.CliRunner`) in the
Click version pinned by this repo does **not** accept `mix_stderr` as a keyword
argument. Passing `CliRunner(mix_stderr=False)` raises:

```
TypeError: CliRunner.__init__() got an unexpected keyword argument 'mix_stderr'
```

## Required usage

Plain `CliRunner()` already separates stdout from stderr \u2014 the `result` object
has independent `result.stdout` and `result.stderr` attributes:

```python
self.runner = CliRunner()
result = self.runner.invoke(app, [...])
assert result.exit_code == 0
assert "warning text" in result.stderr
assert "expected output" in result.stdout
```

## Why this surprised me

Older Click documentation and recipes show `CliRunner(mix_stderr=False)` as the
incantation to split streams. That kwarg was removed; in current Click the
default is split, and there is no migration shim.

## Provenance

Discovered in [[DE-135]] phase 1 while writing VT-DR135-002. Existing tests in
`supekku/cli/list_test.py` (line ~1677, ~2038) read `result.stderr` directly
under plain `CliRunner()` and confirm the split-by-default behaviour.
