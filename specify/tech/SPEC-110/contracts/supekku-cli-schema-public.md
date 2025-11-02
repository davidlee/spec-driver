# supekku.cli.schema

CLI command for displaying YAML block schemas.

Thin CLI layer: parse args → load registry → format → output

## Constants

- `app`
- `console`

## Functions

- @app.command(list) `list_schemas(schema_type) -> None`: List all available block schemas and/or frontmatter schemas.

Examples:
  schema list              # List all schemas (blocks and frontmatter)
  schema list blocks       # List only block schemas
  schema list frontmatter  # List only frontmatter schemas
- @app.command(show) `show_schema(block_type, format_type) -> None`: Show schema details for a specific block type or frontmatter kind.

Examples:
  schema show delta.relationships --format=json-schema
  schema show frontmatter.prod --format=json-schema
  schema show frontmatter.delta --format=yaml-example

Args:
  block_type: Block type identifier (e.g., 'delta.relationships', 'frontmatter.prod')
  format_type: Output format (default: json-schema)
