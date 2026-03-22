# supekku.cli.list.deltas

List deltas command.

## Functions

- @app.command(deltas) `list_deltas(root, ids, status, implements, substring, spec_filter, related_to, relation, referenced_by, not_referenced_by, unaudited, refs, tag, regexp, case_insensitive, format_type, json_output, truncate, details, external, show_all) -> None`: List deltas with optional filtering and status grouping.

By default, completed deltas are hidden. Use --all to show them.

The --filter flag does substring matching (case-insensitive).
The --regexp flag filters on ID, name, and slug fields.
The --implements flag filters by requirement ID (reverse relationship query).
The --spec flag filters by spec reference (applies_to.specs + relations).
The --related-to flag searches all reference slots.
The --relation flag filters by TYPE:TARGET in .relations only.
The --referenced-by/--not-referenced-by flags filter by reverse references.
The --unaudited flag is sugar for --not-referenced-by audit -s completed.

Examples:
  list deltas                         # Shows active deltas (hides completed)
  list deltas --all                   # Shows all deltas
  list deltas -s draft,in-progress    # Multi-value status filter
  list deltas --implements PROD-010.FR-004     # Reverse relationship query
  list deltas --spec PROD-010                  # Deltas touching a spec
  list deltas --related-to IMPR-006            # Deltas referencing IMPR-006
  list deltas --relation relates_to:IMPR-006   # By relation type and target
  list deltas --refs                           # Include refs column
  list deltas --json                           # JSON output
  list deltas --unaudited                      # Completed deltas without an audit
  list deltas --referenced-by audit            # Deltas referenced by any audit
