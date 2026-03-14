---
id: mem.fact.cli.typer-exit-inherits-runtimeerror
name: typer.Exit inherits from RuntimeError
kind: memory
status: active
memory_type: fact
created: "2026-03-08"
updated: "2026-03-08"
tags:
  - typer
  - cli
  - gotcha
summary:
  "typer.Exit (click.exceptions.Exit) inherits from RuntimeError \u2014 except\
  \ RuntimeError handlers will swallow it silently"
scope:
  globs:
    - supekku/cli/**
verified: "2026-03-08"
provenance:
  sources:
    - DE-068
    - supekku/cli/edit.py
---

# typer.Exit inherits from RuntimeError

## Fact

`typer.Exit` is actually `click.exceptions.Exit`, which inherits from `RuntimeError`:

```
click.exceptions.Exit → RuntimeError → Exception → BaseException
```

## Consequence

Any `except RuntimeError` handler in a typer command will catch `typer.Exit` and swallow it — typically re-wrapping as `typer.Exit(EXIT_FAILURE)`, turning success exits into failures.

## Required guard

Always place `except typer.Exit: raise` **before** `except RuntimeError` in typer command try/except blocks:

```python
try:
    ...
except typer.Exit:
    raise
except RuntimeError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
```

## Provenance

Discovered in [[DE-068]] phase 2. All `supekku/cli/edit.py` commands now include the guard.
