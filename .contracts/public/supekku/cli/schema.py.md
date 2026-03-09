# supekku.cli.schema

Schema display functions for YAML block and frontmatter schemas.

Library module — no Typer app. Called by show.py and list.py.

## Constants

- `console`

## Functions

- `list_schemas(schema_type) -> None`: List all available block schemas and/or frontmatter schemas.

Examples:
  schema list              # List all schemas (blocks and frontmatter)
  schema list blocks       # List only block schemas
  schema list frontmatter  # List only frontmatter schemas
- `show_schema(block_type, format_type) -> None`: Show schema details for a specific block type or frontmatter kind.

Examples:
  schema show delta.relationships --format=json-schema
  schema show frontmatter.prod --format=json-schema
  schema show frontmatter.delta --format=yaml-example

Args:
  block_type: Block type identifier (e.g., 'delta.relationships', 'frontmatter.prod')
  format_type: Output format (default: json-schema)
