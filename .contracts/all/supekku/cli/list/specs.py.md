# supekku.cli.list.specs

List specs command.

## Functions

- @app.command(specs) `list_specs(root, kind, status, substring, package_filter, package_path, for_path, category, c4_level, informed_by, related_to, relation, tag, refs, regexp, case_insensitive, format_type, json_output, truncate, paths, packages, external) -> None`: List SPEC/PROD artifacts with optional filtering.

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
