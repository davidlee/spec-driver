"""Backfill commands for replacing stub specs with fresh templates."""

from __future__ import annotations

from typing import Annotated

import typer
import yaml

from supekku.cli.common import EXIT_FAILURE, RootOption
from supekku.scripts.lib.core.templates import TemplateNotFoundError, load_template
from supekku.scripts.lib.specs.detection import is_stub_spec
from supekku.scripts.lib.specs.registry import SpecRegistry

app = typer.Typer(help="Backfill incomplete specifications", no_args_is_help=True)


@app.command("spec")
def backfill_spec(
  spec_id: Annotated[str, typer.Argument(help="Spec ID to backfill")],
  force: Annotated[
    bool, typer.Option("--force", help="Force backfill even if modified")
  ] = False,
  root: RootOption = None,
) -> None:
  """Replace stub spec body with template (preserving frontmatter).

  This command resets a stub spec to a clean template state, filling in
  basic variables (spec_id, name, kind) from frontmatter. The agent or
  user can then complete the sections intelligently.

  By default, only specs detected as stubs (status='stub' or ≤30 lines)
  will be backfilled. Use --force to override this safety check.
  """
  try:
    # Load spec from registry
    registry = SpecRegistry(root=root)
    spec = registry.get(spec_id)

    if not spec:
      typer.echo(f"Error: Specification not found: {spec_id}", err=True)
      raise typer.Exit(EXIT_FAILURE)

    # Check if stub (unless --force)
    if not force and not is_stub_spec(spec.path):
      typer.echo(
        f"Error: {spec_id} has been modified. Use --force to backfill anyway.",
        err=True,
      )
      raise typer.Exit(EXIT_FAILURE)

    # Load template
    try:
      template = load_template("spec.md", repo_root=root)
    except TemplateNotFoundError as e:
      typer.echo(f"Error: {e}", err=True)
      raise typer.Exit(EXIT_FAILURE) from e

    # Render template with basic vars from frontmatter
    # Leave YAML blocks as template boilerplate for agent/user to fill
    rendered_body = template.render(
      spec_id=spec.frontmatter.data.get("id"),
      name=spec.frontmatter.data.get("name"),
      kind=spec.frontmatter.data.get("kind"),
      # YAML blocks left as template boilerplate
      spec_relationships_block="{{ spec_relationships_block }}",
      spec_capabilities_block="{{ spec_capabilities_block }}",
      spec_verification_block="{{ spec_verification_block }}",
    )

    # Write spec: preserve frontmatter, replace body
    _write_spec_with_frontmatter(spec.path, spec.frontmatter.data, rendered_body)

    typer.echo(f"✓ Backfilled {spec_id}: {spec.path}")

  except FileNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except Exception as e:  # noqa: BLE001
    typer.echo(f"Error: Failed to backfill spec: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


def _write_spec_with_frontmatter(
  spec_path,
  frontmatter: dict,
  body: str,
) -> None:
  """Write spec file with frontmatter and body.

  Args:
    spec_path: Path to spec file
    frontmatter: Frontmatter dict to serialize as YAML
    body: Body content (markdown)
  """
  # Convert Mapping to dict if needed (handles immutable mappingproxy)
  frontmatter_dict = dict(frontmatter)

  # Serialize frontmatter as YAML
  frontmatter_yaml = yaml.dump(
    frontmatter_dict,
    default_flow_style=False,
    allow_unicode=True,
    sort_keys=False,
  )

  # Combine frontmatter and body
  content = f"---\n{frontmatter_yaml}---\n\n{body}"

  # Write to file
  spec_path.write_text(content, encoding="utf-8")
