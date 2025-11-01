# supekku.scripts.validate_revision_blocks

Validate structured revision change blocks and optionally format them.

## Constants

- `ROOT`

## Functions

- `_emit_messages(_path, messages) -> None`
- `_print_schema() -> None`
- `discover_revision_files(root, explicit, scan_all) -> list[Path]`: Discover revision markdown files to validate.

Args:
  root: Repository root path.
  explicit: List of explicitly specified file or directory paths.
  scan_all: Whether to scan all revision files automatically.

Returns:
  Sorted list of revision file paths to validate.
- `format_file(content, updates) -> str`: Apply formatting updates to file content.

Args:
  content: Original file content.
  updates: List of (block, replacement) tuples to apply.

Returns:
  Updated file content with replacements applied.
- `main(argv) -> int`: Validate and optionally format revision block YAML in markdown files.

Args:
  argv: Optional command-line arguments.

Returns:
  Exit code: 0 on success, 1 on validation errors.
- `parse_args(argv) -> argparse.Namespace`: Parse command-line arguments for revision block validation.

Args:
  argv: Optional list of command-line arguments. Defaults to sys.argv.

Returns:
  Parsed argument namespace.
