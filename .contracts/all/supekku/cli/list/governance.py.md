# supekku.cli.list.governance

List ADRs, policies, and standards commands.

## Functions

- @app.command(adrs) `list_adrs(root, status, tag, spec, delta, requirement_filter, policy, standard, substring, regexp, case_insensitive, format_type, json_output, truncate) -> None`: List Architecture Decision Records (ADRs) with optional filtering.

The --filter flag does substring matching (case-insensitive).
The --regexp flag filters on title and summary fields.
Other flags filter on specific structured fields (status, tags, references).

Examples:
  list adrs -s accepted             # Filter by status
  list adrs --spec SPEC-110 --json  # ADRs referencing a spec
  list adrs -t cli                  # Filter by tag
- @app.command(policies) `list_policies(root, status, tag, spec, delta, requirement_filter, standard, substring, regexp, case_insensitive, format_type, json_output, truncate, external) -> None`: List policies with optional filtering.

The --filter flag does substring matching (case-insensitive).
The --regexp flag filters on title and summary fields.
Other flags filter on specific structured fields (status, tags, references).
- @app.command(standards) `list_standards(root, status, tag, spec, delta, requirement_filter, policy, substring, regexp, case_insensitive, format_type, json_output, truncate, external) -> None`: List standards with optional filtering.

The --filter flag does substring matching (case-insensitive).
The --regexp flag filters on title and summary fields.
Other flags filter on specific structured fields (status, tags, references).
