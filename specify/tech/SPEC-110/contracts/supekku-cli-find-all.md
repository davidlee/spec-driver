# supekku.cli.find

Find commands for locating artifacts by ID across the repository.

## Constants

- `app`

## Functions

- `_matches_pattern(artifact_id, pattern) -> bool`: Check if artifact ID matches pattern (case-insensitive).
- @app.command(adr) `find_adr(pattern, root) -> None`: Find ADRs matching ID pattern.

Supports fnmatch patterns: * matches everything, ? matches single char.
Examples: ADR-*, ADR-00?, ADR-01*
- @app.command(card) `find_card(card_id, root) -> None`: Find all files matching card ID (repo-wide filename search).

Searches for files matching the pattern T###-*.md anywhere in the repository.
Prints one path per line.
- @app.command(delta) `find_delta(pattern, root) -> None`: Find deltas matching ID pattern.

Supports fnmatch patterns: * matches everything, ? matches single char.
Examples: DE-*, DE-00?, DE-02*
- @app.command(policy) `find_policy(pattern, root) -> None`: Find policies matching ID pattern.

Supports fnmatch patterns: * matches everything, ? matches single char.
Examples: POL-*, POL-00?, POL-01*
- @app.command(revision) `find_revision(pattern, root) -> None`: Find revisions matching ID pattern.

Supports fnmatch patterns: * matches everything, ? matches single char.
Examples: RE-*, RE-00?, RE-01*
- @app.command(spec) `find_spec(pattern, root) -> None`: Find specs matching ID pattern.

Supports fnmatch patterns: * matches everything, ? matches single char.
Examples: SPEC-*, PROD-01?, *-009
- @app.command(standard) `find_standard(pattern, root) -> None`: Find standards matching ID pattern.

Supports fnmatch patterns: * matches everything, ? matches single char.
Examples: STD-*, STD-00?, STD-01*
