# supekku.scripts.list_deltas

List deltas with optional filtering and status grouping.

## Constants

- `ROOT`

## Functions

- `format_delta_basic(artifact) -> str`: Format delta as: id status name.
- `format_delta_with_details(artifact) -> str`: Format delta with related specs, requirements, and phases.
- `main(argv) -> int`: Main entry point for listing deltas.
- `matches_filters(artifact) -> bool`: Check if artifact matches the given filters.
- `parse_args(argv) -> argparse.Namespace`: Parse command-line arguments.
