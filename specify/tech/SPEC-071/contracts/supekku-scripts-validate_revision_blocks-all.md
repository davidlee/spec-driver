# supekku.scripts.validate_revision_blocks

Validate structured revision change blocks and optionally format them.

## Constants

- `ROOT`

## Functions

- `_emit_messages(path, messages) -> None`
- `_print_schema() -> None`
- `discover_revision_files(root, explicit, scan_all) -> list[Path]`
- `format_file(content, updates) -> str`
- `main(argv) -> int`
- `parse_args(argv) -> argparse.Namespace`
