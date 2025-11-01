# supekku.scripts.change_registry

Generate registries for change artefacts (deltas, revisions, audits).

## Constants

- `KINDS`

## Functions

- `main(argv) -> int`: Generate registries for change artefacts.

Args:
  argv: Optional command-line arguments.

Returns:
  Exit code: 0 on success.
- `parse_args(argv) -> argparse.Namespace`: Parse command-line arguments for change registry generation.

Args:
  argv: Optional list of command-line arguments.

Returns:
  Parsed argument namespace.
