# supekku.scripts.create_new_spec

Create a new SPEC or PROD document bundle from templates.

## Constants

- `ROOT`

## Functions

- `main(argv) -> int`: Create a new SPEC or PROD document bundle.

Args:
  argv: Optional command-line arguments. Defaults to sys.argv[1:].

Returns:
  Exit code: 0 on success, 1 on error.
- `parse_args(argv) -> argparse.Namespace`: Parse command-line arguments for spec creation.

Args:
  argv: List of command-line arguments.

Returns:
  Parsed argument namespace with spec_name joined as a single string.

Raises:
  SystemExit: If spec_name is not provided.
