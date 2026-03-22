---
id: STD-001
title: "STD-001: CLI implementation standard (Typer/Rich)"
status: required
created: "2025-11-04"
updated: "2026-03-22"
reviewed: "2026-03-22"
owners: []
supersedes: []
superseded_by: []
policies: []
specs: [SPEC-110]
requirements: []
deltas: []
related_policies: [POL-001]
related_standards: [STD-002]
tags: [cli, ui, typer, rich]
summary: "Canonical patterns for CLI command implementation: Workspace acquisition, Typer/Rich usage, module size limits, error handling."
---

# STD-001: CLI implementation standard (Typer/Rich)

## Statement

All CLI command implementations must follow these canonical patterns:

1. **Workspace acquisition**: Acquire registries exclusively through
   `Workspace` (or its properties), constructed once per CLI invocation and
   passed via Typer context. Do not directly import or instantiate individual
   registry classes in CLI modules. (See ADR-011.)

2. **Framework usage**: Use Typer for argument/option declaration. Use Rich
   for all formatted terminal output. No bare `print()` in CLI modules.

3. **Module size**: CLI command modules must not exceed 500 lines. If a
   command group grows beyond that, extract domain logic to `scripts/lib/`
   and formatting to `formatters/`. CLI modules should contain only argument
   parsing, delegation, and output wiring.

4. **Error handling**: Use `typer.Exit(code=EXIT_FAILURE)` with a Rich error
   panel. Bare `sys.exit()` is prohibited. Shared error-handling patterns
   (e.g. artifact-not-found, validation failure) must use the canonical
   decorator or helper, not per-command try/except boilerplate.

5. **Shared helpers**: Common CLI patterns (format validation, JSON flag
   resolution, status filtering, artifact resolution) must use shared helpers
   from `cli/common.py` or equivalent. Duplicating these patterns inline in
   command functions is a POL-001 violation.

6. **Domain logic boundary**: CLI commands must not contain domain logic
   (parsing, state derivation, filesystem traversal beyond simple path
   resolution). Domain logic belongs in `scripts/lib/`. CLI commands
   delegate to library functions and format their results.

## Rationale

The CLI layer has accumulated significant boilerplate through organic growth:
format validation repeated 13×, JSON flag override 17×, error handling
try/except 16×, and direct registry instantiation bypassing the Workspace
facade. This standard codifies the patterns that prevent recurrence.

## Scope

- Applies to all Python files in `supekku/cli/`.
- Applies to new code immediately. Existing violations are tracked by
  DE-114 (god-file splits), DE-117 (boilerplate reduction), and DE-120
  (Workspace enforcement).
- Does not apply to `scripts/lib/` (library layer) or `tui/` (TUI layer).

## Verification

- Code review must reject new CLI commands that instantiate registries
  directly, duplicate shared helpers, or exceed the module size limit.
- `just check` includes lint gates; STD-002 file-size limits apply.
- Audits of `supekku/cli/` should flag inline domain logic and boilerplate
  repetition.

## References

- ADR-009: standard registry API convention
- POL-001: maximise code reuse, minimise sprawl
- STD-002: govern lint signal
- SPEC-110: supekku/cli Specification
