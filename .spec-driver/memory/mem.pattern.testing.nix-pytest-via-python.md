---
id: mem.pattern.testing.nix-pytest-via-python
name: Use uv run python -m pytest, not uv run pytest
kind: memory
status: active
memory_type: pattern
created: '2026-06-01'
updated: '2026-06-01'
verified: '2026-06-01'
confidence: high
tags:
- testing
- nix
- footgun
scope:
  commands:
  - uv run pytest
  - uv run python -m pytest
summary: In this nix shell, uv run pytest fails to resolve packages; always use uv
  run python -m pytest instead
---

# Use uv run python -m pytest, not uv run pytest

## Summary

In this nix development shell, `uv run pytest` fails to resolve installed
Python packages (e.g. `tomlkit`), causing `ModuleNotFoundError` during test
collection. `uv run python -m pytest` works correctly.

## Context

During DE-128 P04 (2026-05-31), `sync_preferences_test.py` failed to collect:

```
uv run pytest spec_driver/core/sync_preferences_test.py
# ModuleNotFoundError: No module named 'tomlkit'
```

Yet `tomlkit` was importable:

```
uv run python -c "import tomlkit; print(tomlkit.__version__)"
# 0.13.3
```

The fix:

```
uv run python -m pytest spec_driver/core/sync_preferences_test.py -x -q
# 12 passed
```

This is consistent across the project — always use `python -m pytest` in
this nix environment.
