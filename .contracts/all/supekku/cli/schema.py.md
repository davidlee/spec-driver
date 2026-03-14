# supekku.cli.schema

Schema display functions for YAML block and frontmatter schemas.

Library module — no Typer app. Called by show.py and list.py.

## Constants

- `__all__`
- `console`

## Functions

- `_generate_placeholder_value(param_name, param_type_str, schema_name) -> Any`: Generate a placeholder value for a parameter.

Args:
param_name: Name of the parameter
param_type_str: String representation of the parameter type
schema_name: Name of the schema (e.g., "delta.relationships")

Returns:
Placeholder value appropriate for the parameter type - pylint: disable=too-many-return-statements,too-complex

- `_render_frontmatter_json_schema(kind, metadata) -> None`: Render frontmatter JSON Schema (Draft 2020-12).

Args:
kind: Frontmatter kind (e.g., 'prod')
metadata: FrontmatterMetadata instance

- `_render_frontmatter_yaml_example(kind, metadata) -> None`: Render frontmatter YAML example.

Args:
kind: Frontmatter kind (e.g., 'prod')
metadata: FrontmatterMetadata instance

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

- `_render_yaml_example(schema) -> None`: Render example YAML block using metadata examples or renderer.

Args:
schema: BlockSchema instance to render

- `_show_enums(block_type) -> None`: Show enum values for a dotted path, or list all enum paths.

Args:
block_type: 'enums' (list all) or 'enums.<artifact>.<field>'

- `_show_frontmatter_schema(block_type, format_type) -> None`: Show frontmatter schema for a specific kind.

Args:
block_type: Frontmatter block type (e.g., 'frontmatter.prod')
format_type: Output format ('json-schema' or 'yaml-example')

- `list_schemas(schema_type) -> None`: List all available block schemas and/or frontmatter schemas.

Examples:
schema list # List all schemas (blocks and frontmatter)
schema list blocks # List only block schemas
schema list frontmatter # List only frontmatter schemas

- `show_schema(block_type, format_type) -> None`: Show schema details for a specific block type or frontmatter kind.

Examples:
schema show delta.relationships --format=json-schema
schema show frontmatter.prod --format=json-schema
schema show frontmatter.delta --format=yaml-example

Args:
block_type: Block type identifier (e.g., 'delta.relationships', 'frontmatter.prod')
format_type: Output format (default: json-schema)
