# supekku.scripts.list_changes

List change artefacts (deltas, revisions, audits) with optional filters.

## Constants

- `KIND_CHOICES`
- `ROOT`

## Functions

- `format_artifact(artifact) -> str`
- `iter_artifacts(root, kinds)`
- `main(argv) -> int`
- `matches_filters(artifact) -> bool`
- `parse_args(argv) -> argparse.Namespace`
