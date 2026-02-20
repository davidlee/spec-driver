# supekku.cli.find

Find commands for locating artifacts by ID across the repository.

## Constants

- `app`

## Functions

- `_matches_pattern(artifact_id, pattern) -> bool`: Check if artifact ID matches pattern (case-insensitive).
- @app.command(adr) `find_adr(pattern, root) -> None`: Find ADRs matching ID pattern.

Supports fnmatch patterns: * matches everything, ? matches single char.
Also accepts numeric-only IDs (e.g., 001 -> ADR-001).
Examples: ADR-*, ADR-00?, 001
- @app.command(card) `find_card(card_id, root) -> None`: Find all files matching card ID (repo-wide filename search).

Searches for files matching the pattern T###-*.md anywhere in the repository.
Prints one path per line.
- @app.command(delta) `find_delta(pattern, root) -> None`: Find deltas matching ID pattern.

Supports fnmatch patterns: * matches everything, ? matches single char.
Also accepts numeric-only IDs (e.g., 001 -> DE-001).
Examples: DE-*, DE-00?, 001
- @app.command(policy) `find_policy(pattern, root) -> None`: Find policies matching ID pattern.

Supports fnmatch patterns: * matches everything, ? matches single char.
Also accepts numeric-only IDs (e.g., 001 -> POL-001).
Examples: POL-*, POL-00?, 001
- @app.command(revision) `find_revision(pattern, root) -> None`: Find revisions matching ID pattern.

Supports fnmatch patterns: * matches everything, ? matches single char.
Also accepts numeric-only IDs (e.g., 001 -> RE-001).
Examples: RE-*, RE-00?, 001
- @app.command(spec) `find_spec(pattern, root) -> None`: Find specs matching ID pattern.

Supports fnmatch patterns: * matches everything, ? matches single char.
Examples: SPEC-*, PROD-01?, *-009
- @app.command(standard) `find_standard(pattern, root) -> None`: Find standards matching ID pattern.

Supports fnmatch patterns: * matches everything, ? matches single char.
Also accepts numeric-only IDs (e.g., 001 -> STD-001).
Examples: STD-*, STD-00?, 001
