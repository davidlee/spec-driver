# supekku.cli.list.misc

List cards, memories, and schemas commands.

## Functions

- @app.command(cards) `list_cards(root, lane, all_lanes, substring, regexp, case_insensitive, format_type, json_output, truncate) -> None`: List kanban cards with optional filtering.

By default, hides cards in done/ and archived/ lanes. Use --all to show everything.
The --filter flag does substring matching (case-insensitive).
The --regexp flag does pattern matching on ID and title fields.
- @app.command(memories) `list_memories(root, status, memory_type, tag, path, command, match_tag, include_draft, limit, substring, regexp, case_insensitive, format_type, json_output, links_to, truncate, stale) -> None`: List memory records with optional filtering and scope matching.

The --filter flag does substring matching (case-insensitive).
Metadata pre-filters (--type, --status, --tag) apply first (AND logic).
Scope matching (--path, --command, --match-tag) filters by context (OR).
Results ordered deterministically by severity/weight/specificity/recency/id. - noqa: PLR0913
- @app.command(schemas) `list_schemas_cmd(schema_type) -> None`: List available block and/or frontmatter schemas.
