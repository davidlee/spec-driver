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
from supekku.scripts.lib.blocks.schema_registry import (
  get_block_schema,
  list_block_types,
)

app = typer.Typer(help="Show YAML block schemas", no_args_is_help=True)
console = Console()


@app.command("list")
def list_schemas() -> None:
  """List all available block schemas."""
  block_types = list_block_types()

  if not block_types:
    console.print("[yellow]No block schemas registered[/yellow]")
    return

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


@app.command("show")
def show_schema(
  block_type: Annotated[str, typer.Argument(help="Block type to show")],
  format_type: Annotated[
    str,
    typer.Option(
      "--format",
      "-f",
      help="Output format",
    ),
  ] = "markdown",
) -> None:
  """Show schema details for a specific block type.

  Args:
    block_type: Block type identifier (e.g., 'delta.relationships')
    format_type: Output format (markdown, json, yaml-example)
  """
  schema = get_block_schema(block_type)
  if not schema:
    console.print(f"[red]Unknown block type: {block_type}[/red]")
    available = ", ".join(list_block_types())
    console.print(f"Available types: {available}")
    raise typer.Exit(code=1)

  if format_type == "markdown":
    _render_markdown(schema)
  elif format_type == "json":
    _render_json(schema)
  elif format_type == "yaml-example":
    _render_yaml_example(schema)
  else:
    console.print(f"[red]Unknown format: {format_type}[/red]")
    console.print("Available formats: markdown, json, yaml-example")
    raise typer.Exit(code=1)


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
  """Render example YAML block by calling renderer with minimal args.

  Args:
    schema: BlockSchema instance to render
  """
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
