# supekku.cli.sync

Unified synchronization command for specs, ADRs, and registries.

## Constants

- `app`

## Functions

- @app.command `sync(targets, language, existing, check, dry_run, allow_missing_source, specs, adr, backlog, prune, force) -> None`: Synchronize specifications and registries with source code.

Unified command for multi-language spec synchronization. Supports:
- Go (via gomarkdoc)
- Python (via AST analysis)
- Zig (via doc comment parsing)
- ADR/decision registry synchronization
- Backlog priority registry synchronization

By default, only syncs specs. Use --adr or --backlog to sync registries.
