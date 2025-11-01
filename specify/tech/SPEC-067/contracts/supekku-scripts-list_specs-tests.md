# supekku.scripts.list_specs

List SPEC/PROD artefacts with optional substring filtering.

Thin script layer: parse args → load registry → filter → format → output
Display formatting is delegated to supekku.scripts.lib.formatters

## Constants

- `ROOT`

## Functions

- `main(argv) -> int`: List SPEC/PROD artifacts with filtering and formatting options.

Args:
  argv: Optional command-line arguments.

Returns:
  Exit code: 0 on success.
- `normalise_kind(requested, spec_id) -> bool`: Check if spec ID matches the requested kind filter.

Args:
  requested: Kind filter ("all", "tech", or "product").
  spec_id: Spec identifier to check.

Returns:
  True if spec matches the filter, False otherwise.
- `parse_args(argv) -> argparse.Namespace`: Parse command-line arguments for spec listing.

Args:
  argv: Optional list of command-line arguments.

Returns:
  Parsed argument namespace.
