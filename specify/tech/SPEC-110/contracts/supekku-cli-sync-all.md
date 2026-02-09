# supekku.cli.sync

Unified synchronization command for specs, ADRs, and registries.

## Constants

- `app`

## Functions

- `_sync_adr(root) -> dict`: Execute ADR registry synchronization.
- `_sync_backlog(root) -> dict`: Execute backlog priority registry synchronization.
- `_sync_requirements(root) -> dict`: Execute requirements registry synchronization from specs.
- `_sync_specs(root, tech_dir, registry_path, targets, language, existing, check, dry_run, _allow_missing_source, prune, force) -> dict`: Execute spec synchronization.
- @app.command `sync(targets, language, existing, check, dry_run, allow_missing_source, specs, adr, backlog, prune, force) -> None`: Synchronize specifications and registries with source code.

Unified command for multi-language spec synchronization. Supports:
- Go (via gomarkdoc)
- Python (via AST analysis)
- Zig (via doc comment parsing)
- ADR/decision registry synchronization
- Backlog priority registry synchronization

By default, only syncs specs. Use --adr or --backlog to sync registries.
