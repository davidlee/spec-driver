# supekku.cli.schema

CLI command for displaying YAML block schemas.

Thin CLI layer: parse args → load registry → format → output

## Constants

- `__all__`
- `app`
- `console`

## Functions

- `_generate_placeholder_value(param_name, param_type_str, schema_name) -> Any`: Generate a placeholder value for a parameter.

Args:
  param_name: Name of the parameter
  param_type_str: String representation of the parameter type
  schema_name: Name of the schema (e.g., "delta.relationships")

Returns:
  Placeholder value appropriate for the parameter type - pylint: disable=too-many-return-statements,too-complex
- `_render_json(schema) -> None`: Render schema as JSON.

Args:
  schema: BlockSchema instance to render
- `_render_json_schema(block_type, schema) -> None`: Render JSON Schema (Draft 2020-12) for metadata-driven blocks.

Args:
  block_type: Block type identifier (e.g., 'verification.coverage')
  schema: BlockSchema instance to render
- `_render_markdown(schema) -> None`: Render schema as markdown documentation.

Args:
  schema: BlockSchema instance to render
- `_render_yaml_example(schema) -> None`: Render example YAML block by calling renderer with minimal args.

Args:
  schema: BlockSchema instance to render
- @app.command(list) `list_schemas() -> None`: List all available block schemas.
- @app.command(show) `show_schema(block_type, format_type) -> None`: Show schema details for a specific block type.

Args:
  block_type: Block type identifier (e.g., 'delta.relationships')
  format_type: Output format (markdown, json, yaml-example)
