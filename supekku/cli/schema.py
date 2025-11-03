"""CLI command for displaying YAML block schemas.

Thin CLI layer: parse args → load registry → format → output
"""

from __future__ import annotations

import json
from typing import Annotated, Any

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

# Import to ensure schemas are registered
import supekku.scripts.lib.blocks.delta  # noqa: F401  # pylint: disable=unused-import
import supekku.scripts.lib.blocks.plan  # noqa: F401  # pylint: disable=unused-import
import supekku.scripts.lib.blocks.relationships  # noqa: F401  # pylint: disable=unused-import
import supekku.scripts.lib.blocks.revision  # noqa: F401  # pylint: disable=unused-import
import supekku.scripts.lib.blocks.verification  # noqa: F401  # pylint: disable=unused-import
from supekku.scripts.lib.blocks.metadata import metadata_to_json_schema
from supekku.scripts.lib.blocks.schema_registry import (
  get_block_schema,
  list_block_types,
)
from supekku.scripts.lib.core.frontmatter_metadata import (
  FRONTMATTER_METADATA_REGISTRY,
  get_frontmatter_metadata,
)

app = typer.Typer(help="Show YAML block schemas", no_args_is_help=True)
console = Console()


@app.command("list")
def list_schemas(
  schema_type: Annotated[
    str | None,
    typer.Argument(help="Schema type: 'blocks', 'frontmatter', or omit for both"),
  ] = None,
) -> None:
  """List all available block schemas and/or frontmatter schemas.

  Examples:
    schema list              # List all schemas (blocks and frontmatter)
    schema list blocks       # List only block schemas
    schema list frontmatter  # List only frontmatter schemas
  """
  show_blocks = schema_type in (None, "blocks")
  show_frontmatter = schema_type in (None, "frontmatter")

  if schema_type and not (show_blocks or show_frontmatter):
    console.print(f"[red]Unknown schema type: {schema_type}[/red]")
    console.print("Available types: blocks, frontmatter")
    raise typer.Exit(code=1)

  # List block schemas
  if show_blocks:
    block_types = list_block_types()

    if not block_types:
      console.print("[yellow]No block schemas registered[/yellow]")
    else:
      table = Table(title="Available Block Schemas")
      table.add_column("Block Type", style="cyan", no_wrap=True)
      table.add_column("Marker", style="green")
      table.add_column("Version", style="yellow", justify="center")
      table.add_column("Description", style="white")

      for block_type in block_types:
        schema = get_block_schema(block_type)
        if schema:
          table.add_row(
            block_type,
            schema.marker,
            str(schema.version),
            schema.description,
          )

      console.print(table)

  # List frontmatter schemas
  if show_frontmatter:
    if show_blocks:
      console.print()  # Add spacing between tables

    frontmatter_kinds = sorted(FRONTMATTER_METADATA_REGISTRY.keys())

    if not frontmatter_kinds:
      console.print("[yellow]No frontmatter schemas registered[/yellow]")
    else:
      table = Table(title="Available Frontmatter Schemas")
      table.add_column("Kind", style="cyan", no_wrap=True)
      table.add_column("Schema ID", style="green")
      table.add_column("Description", style="white")

      for kind in frontmatter_kinds:
        metadata = get_frontmatter_metadata(kind)
        table.add_row(
          f"frontmatter.{kind}",
          metadata.schema_id,
          metadata.description,
        )

      console.print(table)


@app.command("show")
def show_schema(
  block_type: Annotated[
    str | None,
    typer.Argument(help="Block type (e.g., 'delta.relationships', 'frontmatter.prod')"),
  ] = None,
  format_type: Annotated[
    str,
    typer.Option(
      "--format",
      "-f",
      help="Output format (markdown, json, json-schema, yaml-example)",
    ),
  ] = "json-schema",
) -> None:
  """Show schema details for a specific block type or frontmatter kind.

  Examples:
    schema show delta.relationships --format=json-schema
    schema show frontmatter.prod --format=json-schema
    schema show frontmatter.delta --format=yaml-example

  Args:
    block_type: Block type identifier (e.g., 'delta.relationships', 'frontmatter.prod')
    format_type: Output format (default: json-schema)
  """
  # If no block_type provided, show the list
  if not block_type:
    list_schemas()
    return

  # Check if this is a frontmatter schema request
  if block_type.startswith("frontmatter."):
    _show_frontmatter_schema(block_type, format_type)
    return

  # Otherwise, handle as a block schema
  schema = get_block_schema(block_type)
  if not schema:
    console.print(f"[red]Unknown block type: {block_type}[/red]")
    available = ", ".join(list_block_types())
    console.print(f"Available types: {available}")
    console.print("\nFor frontmatter schemas, use: frontmatter.<kind>")
    fm_kinds = ", ".join(sorted(FRONTMATTER_METADATA_REGISTRY.keys()))
    console.print(f"Available frontmatter kinds: {fm_kinds}")
    raise typer.Exit(code=1)

  if format_type == "markdown":
    _render_markdown(schema)
  elif format_type == "json":
    _render_json(schema)
  elif format_type == "json-schema":
    _render_json_schema(block_type, schema)
  elif format_type == "yaml-example":
    _render_yaml_example(schema)
  else:
    console.print(f"[red]Unknown format: {format_type}[/red]")
    console.print("Available formats: markdown, json, json-schema, yaml-example")
    raise typer.Exit(code=1)


def _show_frontmatter_schema(block_type: str, format_type: str) -> None:
  """Show frontmatter schema for a specific kind.

  Args:
    block_type: Frontmatter block type (e.g., 'frontmatter.prod')
    format_type: Output format ('json-schema' or 'yaml-example')
  """
  # Extract kind from block_type (e.g., 'frontmatter.prod' -> 'prod')
  kind = block_type.replace("frontmatter.", "")

  # Validate kind
  if kind not in FRONTMATTER_METADATA_REGISTRY:
    console.print(f"[red]Unknown frontmatter kind: {kind}[/red]")
    available = ", ".join(sorted(FRONTMATTER_METADATA_REGISTRY.keys()))
    console.print(f"Available kinds: {available}")
    raise typer.Exit(code=1)

  # Get metadata
  metadata = get_frontmatter_metadata(kind)

  # Render based on format
  if format_type == "json-schema":
    _render_frontmatter_json_schema(kind, metadata)
  elif format_type == "yaml-example":
    _render_frontmatter_yaml_example(kind, metadata)
  else:
    console.print(f"[red]Unsupported format for frontmatter: {format_type}[/red]")
    console.print("Available formats for frontmatter: json-schema, yaml-example")
    raise typer.Exit(code=1)


def _render_frontmatter_json_schema(kind: str, metadata) -> None:
  """Render frontmatter JSON Schema (Draft 2020-12).

  Args:
    kind: Frontmatter kind (e.g., 'prod')
    metadata: FrontmatterMetadata instance
  """
  json_schema = metadata_to_json_schema(metadata)
  json_output = json.dumps(json_schema, indent=2)
  syntax = Syntax(json_output, "json", theme="monokai")
  console.print(
    Panel(syntax, title=f"JSON Schema: frontmatter.{kind}", expand=False),
  )


def _render_frontmatter_yaml_example(kind: str, metadata) -> None:
  """Render frontmatter YAML example.

  Args:
    kind: Frontmatter kind (e.g., 'prod')
    metadata: FrontmatterMetadata instance
  """
  import yaml as yaml_lib

  if not metadata.examples or len(metadata.examples) == 0:
    console.print(f"[yellow]No examples available for frontmatter.{kind}[/yellow]")
    raise typer.Exit(code=1)

  # Use first example (minimal by convention)
  example_data = metadata.examples[0]
  example_yaml = yaml_lib.dump(example_data, default_flow_style=False, sort_keys=False)
  syntax = Syntax(example_yaml, "yaml", theme="monokai")
  console.print(
    Panel(syntax, title=f"Example: frontmatter.{kind}", expand=False),
  )


def _render_markdown(schema) -> None:
  """Render schema as markdown documentation.

  Args:
    schema: BlockSchema instance to render
  """
  params = schema.get_parameters()

  lines = [
    f"# {schema.name}",
    "",
    f"**Marker**: `{schema.marker}`",
    f"**Version**: {schema.version}",
    "",
    schema.description,
    "",
    "## Parameters",
    "",
  ]

  if not params:
    lines.append("_No parameters_")
  else:
    for param_name, param_info in params.items():
      required = "**required**" if param_info["required"] else "optional"
      param_type = str(param_info["type"])
      # Simplify type display
      if "typing." in param_type:
        param_type = param_type.replace("typing.", "")
      lines.append(f"- `{param_name}`: {param_type} ({required})")
      if param_info["default"] is not None:
        lines.append(f"  - Default: `{param_info['default']}`")

  markdown_text = "\n".join(lines)
  markdown = Markdown(markdown_text)
  console.print(Panel(markdown, title=f"Schema: {schema.name}", expand=False))


def _render_json(schema) -> None:
  """Render schema as JSON.

  Args:
    schema: BlockSchema instance to render
  """
  params = schema.get_parameters()

  # Convert type annotations to strings for JSON serialization
  serializable_params = {}
  for name, info in params.items():
    serializable_params[name] = {
      "required": info["required"],
      "type": str(info["type"]),
      "default": str(info["default"]) if info["default"] is not None else None,
    }

  schema_dict = {
    "name": schema.name,
    "marker": schema.marker,
    "version": schema.version,
    "description": schema.description,
    "parameters": serializable_params,
  }

  json_output = json.dumps(schema_dict, indent=2)
  syntax = Syntax(json_output, "json", theme="monokai")
  console.print(syntax)


def _render_json_schema(block_type: str, schema) -> None:
  """Render JSON Schema (Draft 2020-12) for metadata-driven blocks.

  Args:
    block_type: Block type identifier (e.g., 'verification.coverage')
    schema: BlockSchema instance to render
  """
  # Map block types to their metadata definitions
  metadata_registry = {
    "verification.coverage": "supekku.scripts.lib.blocks.verification_metadata",
    "delta.relationships": "supekku.scripts.lib.blocks.delta_metadata",
    "plan.overview": "supekku.scripts.lib.blocks.plan_metadata",
    "phase.overview": "supekku.scripts.lib.blocks.plan_metadata",
    "phase.tracking": "supekku.scripts.lib.blocks.tracking_metadata",
    "revision.change": "supekku.scripts.lib.blocks.revision_metadata",
  }

  if block_type not in metadata_registry:
    console.print(f"[yellow]JSON Schema not yet available for {block_type}[/yellow]")
    console.print("This block has not been migrated to metadata-driven validation yet.")
    console.print("Use --format=json for parameter info instead.")
    return

  # Import and get metadata
  try:
    module_path = metadata_registry[block_type]

    # Import the module
    import importlib

    module = importlib.import_module(module_path)
    metadata = getattr(module, f"{block_type.upper().replace('.', '_')}_METADATA")

    # Generate JSON Schema
    from supekku.scripts.lib.blocks.metadata import metadata_to_json_schema

    json_schema = metadata_to_json_schema(metadata)

    # Pretty print
    json_output = json.dumps(json_schema, indent=2)
    syntax = Syntax(json_output, "json", theme="monokai")
    console.print(
      Panel(syntax, title=f"JSON Schema: {block_type}", expand=False),
    )

    # Print helpful hint about yaml-example
    console.print()
    console.print(
      "[dim]💡 Tip: See a complete YAML example with:[/dim]",
    )
    console.print(
      f"[cyan]  schema show {block_type} --format=yaml-example[/cyan]",
    )
  except (ImportError, AttributeError) as e:
    console.print(f"[red]Error loading metadata for {block_type}: {e}[/red]")
    console.print("This may be a bug - please report it.")


def _generate_placeholder_value(  # pylint: disable=too-many-return-statements,too-complex
  param_name: str,
  param_type_str: str,
  schema_name: str,
) -> Any:
  """Generate a placeholder value for a parameter.

  Args:
    param_name: Name of the parameter
    param_type_str: String representation of the parameter type
    schema_name: Name of the schema (e.g., "delta.relationships")

  Returns:
    Placeholder value appropriate for the parameter type
  """
  if "str" in param_type_str:
    if param_name.endswith("_id") or param_name == "delta_id":
      # Generate appropriate ID based on schema type
      if "delta" in schema_name:
        return "DE-001"
      if "plan" in schema_name:
        return "IP-001"
      if "phase" in schema_name:
        return "IP-001-P01"
      if "spec" in schema_name:
        return "SPEC-001"
      if "revision" in schema_name:
        return "RE-001"
      return "EXAMPLE-001"
    return f"example-{param_name}"
  if "int" in param_type_str:
    return 1
  if "list" in param_type_str:
    return []
  if "dict" in param_type_str:
    return {}
  return None


def _render_yaml_example(schema) -> None:
  """Render example YAML block using metadata examples or renderer.

  Args:
    schema: BlockSchema instance to render
  """
  # Map block types to their metadata definitions
  metadata_registry = {
    "verification.coverage": "supekku.scripts.lib.blocks.verification_metadata",
    "delta.relationships": "supekku.scripts.lib.blocks.delta_metadata",
    "plan.overview": "supekku.scripts.lib.blocks.plan_metadata",
    "phase.overview": "supekku.scripts.lib.blocks.plan_metadata",
    "phase.tracking": "supekku.scripts.lib.blocks.tracking_metadata",
    "revision.change": "supekku.scripts.lib.blocks.revision_metadata",
  }

  # Try to use metadata example first for migrated validators
  if schema.name in metadata_registry:
    try:
      import importlib

      import yaml as yaml_lib

      module_path = metadata_registry[schema.name]
      module = importlib.import_module(module_path)
      metadata = getattr(module, f"{schema.name.upper().replace('.', '_')}_METADATA")

      if metadata.examples and len(metadata.examples) > 0:
        example_data = metadata.examples[0]
        example_yaml = (
          f"```yaml {schema.marker}\n"
          f"{yaml_lib.dump(example_data, default_flow_style=False, sort_keys=False)}"
          f"```"
        )
        syntax = Syntax(example_yaml, "yaml", theme="monokai")
        console.print(
          Panel(syntax, title=f"Example: {schema.name}", expand=False),
        )
        return
    except (ImportError, AttributeError, IndexError):
      pass  # Fall through to renderer-based approach

  # Fall back to renderer-based approach for non-migrated validators
  params = schema.get_parameters()

  # Build minimal args to call renderer
  args = []
  kwargs = {}

  for param_name, param_info in params.items():
    if param_info["required"]:
      # Provide placeholder values for required params
      param_type_str = str(param_info["type"])
      value = _generate_placeholder_value(param_name, param_type_str, schema.name)
      args.append(value)

  try:
    # Call renderer with minimal required args
    if args:
      example_yaml = schema.renderer(*args, **kwargs)
    else:
      example_yaml = schema.renderer(**kwargs)

    syntax = Syntax(example_yaml, "yaml", theme="monokai")
    console.print(
      Panel(syntax, title=f"Example: {schema.name}", expand=False),
    )
  except (TypeError, ValueError) as e:
    console.print(f"[yellow]Could not generate example: {e}[/yellow]")
    console.print("Use --format=markdown or --format=json for schema details.")


__all__ = ["app"]
