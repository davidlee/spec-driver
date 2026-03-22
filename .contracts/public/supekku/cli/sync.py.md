# supekku.cli.sync

Unified synchronization command for specs, ADRs, and registries.

## Constants

- `app`

## Functions

- @app.command `sync(targets, language, existing, check, dry_run, allow_missing_source, specs, contracts, memory_links, link_mode, prune, force) -> None`: Synchronize specifications and registries with source code.

Unified command for multi-language spec synchronization. Supports:

- Go (via gomarkdoc)
- Python (via AST analysis)
- Zig (via doc comment parsing)
- ADR/decision registry synchronization
- Backlog priority registry synchronization

By default, generates contracts for existing specs and syncs all registries
(ADR, backlog, requirements). Spec auto-creation is off unless opted in
with --specs (persisted for future runs).
