# supekku.scripts.list_changes

List change artefacts (deltas, revisions, audits) with optional filters.

## Constants

- `KIND_CHOICES`

## Functions

- `format_artifact(artifact) -> str`: Format artefact as tab-separated output.

Args:
  artifact: Change artefact to format.
  root: Repository root for relative path calculation.
  include_paths: Whether to include file paths.
  include_relations: Whether to include relations.
  include_applies: Whether to include applies_to requirements.
  include_plan: Whether to include plan overview.

Returns:
  Tab-separated string representation.
- `iter_artifacts(root, kinds)`: Iterate through change artefacts of specified kinds.

Args:
  root: Repository root path.
  kinds: Iterable of artefact kinds to include.

Yields:
  Change artefacts from registries.
- `main(argv) -> int`: List change artefacts with optional filters.

Args:
  argv: Optional command-line arguments.

Returns:
  Exit code: 0 on success.
- `matches_filters(artifact) -> bool`: Check if artefact matches all specified filters.

Args:
  artifact: Change artefact to filter.
  substring: Optional substring to match in ID, slug, or name.
  status: Optional status to match.
  applies_to: Optional requirement reference to match.

Returns:
  True if artefact matches all filters.
- `parse_args(argv) -> argparse.Namespace`: Parse command-line arguments for listing change artefacts.

Args:
  argv: Optional list of command-line arguments.

Returns:
  Parsed argument namespace.
