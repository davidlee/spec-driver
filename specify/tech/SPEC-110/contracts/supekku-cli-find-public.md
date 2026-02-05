# supekku.cli.find

Find commands for locating artifacts by ID across the repository.

## Constants

- `app`

## Functions

- @app.command(card) `find_card(card_id, root) -> None`: Find all files matching card ID (repo-wide filename search).

Searches for files matching the pattern T###-*.md anywhere in the repository.
Prints one path per line.
