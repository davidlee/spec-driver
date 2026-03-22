# supekku.cli.find

Find commands for locating artifacts by ID across the repository.

## Constants

- `app`

## Functions

- @app.command(adr) `find_adr(pattern, root) -> None`: Find ADRs matching ID pattern.

Supports fnmatch patterns: _ matches everything, ? matches single char.
Also accepts numeric-only IDs (e.g., 001 -> ADR-001).
Examples: ADR-_, ADR-00?, 001

- @app.command(audit) `find_audit(pattern, root) -> None`: Find audits matching ID pattern.

Supports fnmatch patterns: \* matches everything, ? matches single char.

- @app.command(card) `find_card(card_id, root) -> None`: Find all files matching card ID (repo-wide filename search).

Searches for files matching the pattern T###-\*.md anywhere in the repository.
Prints one path per line.

- @app.command(delta) `find_delta(pattern, root) -> None`: Find deltas matching ID pattern.

Supports fnmatch patterns: _ matches everything, ? matches single char.
Also accepts numeric-only IDs (e.g., 001 -> DE-001).
Examples: DE-_, DE-00?, 001

- @app.command(improvement) `find_improvement(pattern, root) -> None`: Find improvements matching ID pattern.
- @app.command(issue) `find_issue(pattern, root) -> None`: Find issues matching ID pattern.
- @app.command(memory) `find_memory(pattern, root) -> None`: Find memory records matching ID pattern.

Supports fnmatch patterns: \* matches everything, ? matches single char.
The 'mem.' prefix is prepended automatically if the pattern doesn't
already start with it.

Examples: mem.pattern._, pattern.cli._, mem._.auth._

- @app.command(plan) `find_plan(pattern, root) -> None`: Find implementation plans matching ID pattern.

Supports fnmatch patterns: \* matches everything, ? matches single char.
Also accepts numeric-only IDs (e.g., 041 -> IP-041).

- @app.command(policy) `find_policy(pattern, root) -> None`: Find policies matching ID pattern.

Supports fnmatch patterns: _ matches everything, ? matches single char.
Also accepts numeric-only IDs (e.g., 001 -> POL-001).
Examples: POL-_, POL-00?, 001

- @app.command(problem) `find_problem(pattern, root) -> None`: Find problems matching ID pattern.
- @app.command(requirement) `find_requirement(pattern, root) -> None`: Find requirements matching ID pattern.

Supports fnmatch patterns. Accepts colon-separated IDs (normalized to dot).
Examples: SPEC-009.FR-\*, SPEC-009:FR-001

- @app.command(revision) `find_revision(pattern, root) -> None`: Find revisions matching ID pattern.

Supports fnmatch patterns: _ matches everything, ? matches single char.
Also accepts numeric-only IDs (e.g., 001 -> RE-001).
Examples: RE-_, RE-00?, 001

- @app.command(risk) `find_risk(pattern, root) -> None`: Find risks matching ID pattern.
- @app.command(spec) `find_spec(pattern, root) -> None`: Find specs matching ID pattern.

Supports fnmatch patterns: _ matches everything, ? matches single char.
Examples: SPEC-_, PROD-01?, \*-009

- @app.command(standard) `find_standard(pattern, root) -> None`: Find standards matching ID pattern.

Supports fnmatch patterns: _ matches everything, ? matches single char.
Also accepts numeric-only IDs (e.g., 001 -> STD-001).
Examples: STD-_, STD-00?, 001
