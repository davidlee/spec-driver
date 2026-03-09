# supekku.cli.list

List commands for specs, deltas, and changes.

Thin CLI layer: parse args → load registry → filter → format → output
Display formatting is delegated to supekku.scripts.lib.formatters

## Constants

- `_PLURAL_TO_SINGULAR` - Singular command aliases - dynamically register
- `app`

## Functions

- `_format_stale_memories(records, root) -> str`: Compute staleness and format as tiered table.
- `_parse_relation_filter(value) -> tuple[Tuple[str, str]]`: Parse ``TYPE:TARGET`` from ``--relation`` flag.

Splits on the first colon. Raises :class:`typer.BadParameter` if no colon
is present. Emits a warning on stderr for unrecognised relation types.
- @app.command(adrs) `list_adrs(root, status, tag, spec, delta, requirement_filter, policy, standard, substring, regexp, case_insensitive, format_type, json_output, truncate) -> None`: List Architecture Decision Records (ADRs) with optional filtering.

The --filter flag does substring matching (case-insensitive).
The --regexp flag filters on title and summary fields.
Other flags filter on specific structured fields (status, tags, references).

Examples:
  list adrs -s accepted             # Filter by status
  list adrs --spec SPEC-110 --json  # ADRs referencing a spec
  list adrs -t cli                  # Filter by tag
- @app.command(audits) `list_audits(root, status, spec, substring, regexp, case_insensitive, format_type, json_output, truncate, external) -> None`: List audits with optional filtering.

The --filter flag does substring matching (case-insensitive).
The --regexp flag does pattern matching on ID, slug, and name fields.
- @app.command(backlog) `list_backlog(root, kind, status, substring, severity, json_output, regexp, case_insensitive, format_type, truncate, order, prioritize, show_all, limit, pager, external) -> None`: List backlog items with optional filtering.

By default, items are sorted by priority (registry order → severity → ID) and
resolved/implemented items are excluded. Use --all to include all statuses.
Use --order to sort by: id, severity, status, or kind.
Use --severity to filter by priority level (e.g. p1, p2, p3).

Use --prioritize to open the filtered items in your editor for interactive reordering.
After saving, the registry will be updated with your new ordering.

The --filter flag does substring matching (case-insensitive).
The --regexp flag does pattern matching on ID and title fields.
- @app.command(cards) `list_cards(root, lane, all_lanes, substring, regexp, case_insensitive, format_type, json_output, truncate) -> None`: List kanban cards with optional filtering.

By default, hides cards in done/ and archived/ lanes. Use --all to show everything.
The --filter flag does substring matching (case-insensitive).
The --regexp flag does pattern matching on ID and title fields.
- @app.command(changes) `list_changes(root, kind, substring, status, applies_to, regexp, case_insensitive, format_type, json_output, truncate, paths, relations, applies, plan, external) -> None`: List change artifacts (deltas, revisions, audits) with optional filters.

The --filter flag does substring matching (case-insensitive).
The --regexp flag does pattern matching on ID, slug, and name fields.
- @app.command(deltas) `list_deltas(root, ids, status, implements, substring, related_to, relation, refs, regexp, case_insensitive, format_type, json_output, truncate, details, external) -> None`: List deltas with optional filtering and status grouping.

The --filter flag does substring matching (case-insensitive).
The --regexp flag filters on ID, name, and slug fields.
The --implements flag filters by requirement ID (reverse relationship query).
The --related-to flag searches all reference slots.
The --relation flag filters by TYPE:TARGET in .relations only.

Examples:
  list deltas -s draft,in-progress            # Multi-value status filter
  list deltas --implements PROD-010.FR-004     # Reverse relationship query
  list deltas --related-to IMPR-006            # Deltas referencing IMPR-006
  list deltas --relation relates_to:IMPR-006   # By relation type and target
  list deltas --refs                           # Include refs column
  list deltas --json                           # JSON output
- @app.command(drift) `list_drift(root, status, substring, regexp, case_insensitive, format_type, truncate) -> None`: List drift ledgers.
- @app.command(improvements) `list_improvements(root, status, severity, substring, json_output, regexp, case_insensitive, format_type, truncate, order, prioritize, show_all, limit, pager, external) -> None`: List backlog improvements with optional filtering.

Shortcut for: list backlog --kind improvement

By default, resolved/implemented items are excluded. Use --all to show all.
- @app.command(issues) `list_issues(root, status, severity, substring, json_output, regexp, case_insensitive, format_type, truncate, order, prioritize, show_all, limit, pager, external) -> None`: List backlog issues with optional filtering.

Shortcut for: list backlog --kind issue

By default, resolved/implemented items are excluded. Use --all to show all.
- @app.command(memories) `list_memories(root, status, memory_type, tag, path, command, match_tag, include_draft, limit, substring, regexp, case_insensitive, format_type, json_output, links_to, truncate, stale) -> None`: List memory records with optional filtering and scope matching.

The --filter flag does substring matching (case-insensitive).
Metadata pre-filters (--type, --status, --tag) apply first (AND logic).
Scope matching (--path, --command, --match-tag) filters by context (OR).
Results ordered deterministically by severity/weight/specificity/recency/id. - noqa: PLR0913
- @app.command(plans) `list_plans(root, status, substring, regexp, case_insensitive, format_type, json_output, truncate) -> None`: List implementation plans with optional filtering.

The --filter flag does substring matching (case-insensitive).
The --regexp flag does pattern matching on ID, slug, and name fields.
- @app.command(policies) `list_policies(root, status, tag, spec, delta, requirement_filter, standard, substring, regexp, case_insensitive, format_type, json_output, truncate, external) -> None`: List policies with optional filtering.

The --filter flag does substring matching (case-insensitive).
The --regexp flag filters on title and summary fields.
Other flags filter on specific structured fields (status, tags, references).
- @app.command(problems) `list_problems(root, status, severity, substring, json_output, regexp, case_insensitive, format_type, truncate, order, prioritize, show_all, limit, pager, external) -> None`: List backlog problems with optional filtering.

Shortcut for: list backlog --kind problem

By default, resolved/implemented items are excluded. Use --all to show all.
- @app.command(requirements) `list_requirements(root, spec, status, kind, category, verified_by, vstatus, vkind, substring, regexp, case_insensitive, format_type, json_output, source_kind, truncate, external) -> None`: List requirements with optional filtering.

The --filter flag does substring matching (case-insensitive).
The --regexp flag does pattern matching on UID, label, title, and category fields.
The --category flag does substring matching on category field.
The --verified-by flag filters by verification artifact (supports glob patterns).
Use --case-insensitive (-i) to make regexp and category filters case-insensitive.

Examples:
  list requirements -k FR,NF                   # Multi-value kind filter
  list requirements --verified-by "VT-CLI-*"   # Glob pattern match
  list requirements --vstatus verified --json   # Verification status filter
  list requirements --spec SPEC-110 --vkind VT  # Combined filters
  list requirements --source-kind issue          # Filter by source
- @app.command(revisions) `list_revisions(root, status, spec, substring, regexp, case_insensitive, format_type, json_output, truncate, external) -> None`: List revisions with optional filtering.

The --filter flag does substring matching (case-insensitive).
The --regexp flag does pattern matching on ID, slug, and name fields.
- @app.command(risks) `list_risks(root, status, severity, substring, json_output, regexp, case_insensitive, format_type, truncate, order, prioritize, show_all, limit, pager, external) -> None`: List backlog risks with optional filtering.

Shortcut for: list backlog --kind risk

By default, resolved/implemented items are excluded. Use --all to show all.
- @app.command(schemas) `list_schemas_cmd(schema_type) -> None`: List available block and/or frontmatter schemas.
- @app.command(specs) `list_specs(root, kind, status, substring, package_filter, package_path, for_path, category, c4_level, informed_by, related_to, relation, refs, regexp, case_insensitive, format_type, json_output, truncate, paths, packages, external) -> None`: List SPEC/PROD artifacts with optional filtering.

The --filter flag does substring matching (case-insensitive).
The --regexp flag does pattern matching on ID, slug, and name fields.
The --informed-by flag filters by ADR ID (reverse relationship query).
The --related-to flag searches all reference slots (relations, informed_by).
The --relation flag filters by TYPE:TARGET in .relations only.

Examples:
  list specs -k prod,tech            # Multi-value kind filter
  list specs -s active --json        # JSON output with status filter
  list specs --informed-by ADR-001   # Specs informed by an ADR
  list specs --related-to ADR-001    # Specs referencing ADR-001 in any slot
  list specs --relation implements:PROD-010  # By relation type and target
  list specs --refs                  # Include refs column
- @app.command(standards) `list_standards(root, status, tag, spec, delta, requirement_filter, policy, substring, regexp, case_insensitive, format_type, json_output, truncate, external) -> None`: List standards with optional filtering.

The --filter flag does substring matching (case-insensitive).
The --regexp flag filters on title and summary fields.
Other flags filter on specific structured fields (status, tags, references).
