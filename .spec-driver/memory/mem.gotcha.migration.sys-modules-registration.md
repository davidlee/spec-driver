---
id: mem.gotcha.migration.sys-modules-registration
name: Migration step sys.modules registration requirement
kind: memory
status: active
memory_type: fact
created: '2026-05-21'
updated: '2026-05-21'
verified: '2026-05-21'
confidence: high
tags:
- migration
- gotcha
- dataclass
summary: Migration steps using @dataclass + from __future__ import annotations crash
  under spec_from_file_location loading unless sys.modules registration happens before
  exec_module
---

# Migration step sys.modules registration requirement

The migration orchestrator loads step modules via `importlib.util.spec_from_file_location` + `exec_module`. Python 3.13 dataclass introspection (`dataclasses._is_type`) resolves `cls.__module__` against `sys.modules`. If the module is not registered before `exec_module`, any `@dataclass` decorator crashes with `AttributeError: 'NoneType' object has no attribute '__dict__'`.

## Fix

In `spec_driver/presentation/cli/admin/migrate.py::_import_step_module`, `sys.modules[spec.name] = module` must be called before `loader.exec_module(module)`. Fixed in commit `b3cf1906` (DE-138 P02).

## When this bites

- Creating any new migration step that uses `@dataclass(frozen=True)` under `from __future__ import annotations`
- DE-137 fake-step fixtures used plain classes, so this never surfaced until DE-138 shipped the first real step

## Provenance

- [[DE-138]] P02 notes; commit `b3cf1906`
- `spec_driver/presentation/cli/admin/migrate.py`
