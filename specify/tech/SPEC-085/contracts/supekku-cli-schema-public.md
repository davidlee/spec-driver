# supekku.cli.schema

CLI command for displaying YAML block schemas.

Thin CLI layer: parse args → load registry → format → output

## Constants

- `app`
- `console`

## Functions

- @app.command(list) `list_schemas() -> None`: List all available block schemas.
- @app.command(show) `show_schema(block_type, format_type) -> None`: Show schema details for a specific block type.

Args:
  block_type: Block type identifier (e.g., 'delta.relationships')
  format_type: Output format (markdown, json, yaml-example)
