# supekku.scripts.validate_workspace

Validate workspace metadata and relationships.

## Functions

- `get_repo_root(start) -> Path`: Get repository root from starting path.

Args:
  start: Starting path to search from.

Returns:
  Repository root path.
- `main(argv) -> int`: Validate workspace metadata and relationships.

Args:
  argv: Optional command-line arguments.

Returns:
  Exit code: 0 if validation passes, 1 if issues found.
- `parse_args(argv) -> argparse.Namespace`: Parse command-line arguments for workspace validation.

Args:
  argv: Optional list of command-line arguments.

Returns:
  Parsed argument namespace.
