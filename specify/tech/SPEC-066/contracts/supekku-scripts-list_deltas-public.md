# supekku.scripts.list_deltas

List deltas with optional filtering and status grouping.

Thin script layer: parse args → load registry → filter → format → output
Display formatting is delegated to supekku.scripts.lib.formatters

## Constants

- `ROOT`

## Functions

- `main(argv) -> int`: Main entry point for listing deltas.
- `matches_filters(artifact) -> bool`: Check if artifact matches the given filters.
- `parse_args(argv) -> argparse.Namespace`: Parse command-line arguments.
