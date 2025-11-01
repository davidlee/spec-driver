# supekku.scripts.requirements

Manage requirements registry: sync, list, search, and update status.

## Constants

- `DEFAULT_AUDIT_DIRS`
- `DEFAULT_DELTA_DIRS`
- `DEFAULT_REVISION_DIRS`
- `DEFAULT_SPEC_DIRS`
- `REGISTRY_PATH`
- `ROOT` - type: ignore

## Functions

- `build_parser() -> argparse.ArgumentParser`: Build argument parser for requirements registry management.

Returns:
  Configured ArgumentParser with subcommands.
- `main(argv) -> int`: Manage requirements registry: sync, list, search, and update status.

Args:
  argv: Optional command-line arguments.

Returns:
  Exit code: 0 on success, 1 on error.
