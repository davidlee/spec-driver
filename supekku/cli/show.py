"""Show commands for displaying detailed information about artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS, RootOption, normalize_id
from supekku.scripts.lib.cards import CardRegistry
from supekku.scripts.lib.changes.registry import ChangeRegistry
from supekku.scripts.lib.core.repo import find_repo_root
from supekku.scripts.lib.core.templates import TemplateNotFoundError, render_template
from supekku.scripts.lib.decisions.registry import DecisionRegistry
from supekku.scripts.lib.formatters.card_formatters import format_card_details
from supekku.scripts.lib.formatters.change_formatters import (
  format_delta_details,
  format_delta_details_json,
  format_revision_details,
)
from supekku.scripts.lib.formatters.decision_formatters import format_decision_details
from supekku.scripts.lib.formatters.policy_formatters import format_policy_details
from supekku.scripts.lib.formatters.requirement_formatters import (
  format_requirement_details,
)
from supekku.scripts.lib.formatters.spec_formatters import format_spec_details
from supekku.scripts.lib.formatters.standard_formatters import format_standard_details
from supekku.scripts.lib.policies.registry import PolicyRegistry
from supekku.scripts.lib.requirements.registry import RequirementsRegistry
from supekku.scripts.lib.specs.registry import SpecRegistry
from supekku.scripts.lib.standards.registry import StandardRegistry

app = typer.Typer(help="Show detailed artifact information", no_args_is_help=True)


@app.command("spec")
def show_spec(
  spec_id: Annotated[str, typer.Argument(help="Spec ID (e.g., SPEC-009, PROD-042)")],
  json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
  path_only: Annotated[bool, typer.Option("--path", help="Output path only")] = False,
  raw_output: Annotated[
    bool, typer.Option("--raw", help="Output raw file content")
  ] = False,
  root: RootOption = None,
) -> None:
  """Show detailed information about a specification."""
  try:
    if sum([json_output, path_only, raw_output]) > 1:
      typer.echo("Error: --json, --path, and --raw are mutually exclusive", err=True)
      raise typer.Exit(EXIT_FAILURE)

    registry = SpecRegistry(root=root)
    spec = registry.get(spec_id)

    if not spec:
      typer.echo(f"Error: Specification not found: {spec_id}", err=True)
      raise typer.Exit(EXIT_FAILURE)

    if path_only:
      typer.echo(spec.path)
    elif raw_output:
      typer.echo(spec.path.read_text())
    elif json_output:
      from supekku.scripts.lib.core.repo import find_repo_root

      repo_root = find_repo_root(root)
      output = spec.to_dict(repo_root)
      typer.echo(json.dumps(output, indent=2))
    else:
      typer.echo(format_spec_details(spec, root=root))

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("delta")
def show_delta(
  delta_id: Annotated[str, typer.Argument(help="Delta ID (e.g., DE-003, 003)")],
  json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
  path_only: Annotated[bool, typer.Option("--path", help="Output path only")] = False,
  raw_output: Annotated[
    bool, typer.Option("--raw", help="Output raw file content")
  ] = False,
  root: RootOption = None,
) -> None:
  """Show detailed information about a delta."""
  try:
    if sum([json_output, path_only, raw_output]) > 1:
      typer.echo("Error: --json, --path, and --raw are mutually exclusive", err=True)
      raise typer.Exit(EXIT_FAILURE)

    normalized_id = normalize_id("delta", delta_id)
    registry = ChangeRegistry(root=root, kind="delta")
    artifacts = registry.collect()
    artifact = artifacts.get(normalized_id)

    if not artifact:
      typer.echo(f"Error: Delta not found: {normalized_id}", err=True)
      raise typer.Exit(EXIT_FAILURE)

    if path_only:
      typer.echo(artifact.path)
    elif raw_output:
      typer.echo(artifact.path.read_text())
    elif json_output:
      typer.echo(format_delta_details_json(artifact, root=root))
    else:
      typer.echo(format_delta_details(artifact, root=root))

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("revision")
def show_revision(
  revision_id: Annotated[str, typer.Argument(help="Revision ID (e.g., RE-001, 001)")],
  json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
  path_only: Annotated[bool, typer.Option("--path", help="Output path only")] = False,
  raw_output: Annotated[
    bool, typer.Option("--raw", help="Output raw file content")
  ] = False,
  root: RootOption = None,
) -> None:
  """Show detailed information about a revision."""
  try:
    if sum([json_output, path_only, raw_output]) > 1:
      typer.echo("Error: --json, --path, and --raw are mutually exclusive", err=True)
      raise typer.Exit(EXIT_FAILURE)

    normalized_id = normalize_id("revision", revision_id)
    registry = ChangeRegistry(root=root, kind="revision")
    artifacts = registry.collect()
    artifact = artifacts.get(normalized_id)

    if not artifact:
      typer.echo(f"Error: Revision not found: {normalized_id}", err=True)
      raise typer.Exit(EXIT_FAILURE)

    if path_only:
      typer.echo(artifact.path)
    elif raw_output:
      typer.echo(artifact.path.read_text())
    elif json_output:
      output = (
        artifact.to_dict() if hasattr(artifact, "to_dict") else {"id": artifact.id}
      )
      typer.echo(json.dumps(output, indent=2))
    else:
      typer.echo(format_revision_details(artifact, root=root))

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("requirement")
def show_requirement(
  req_id: Annotated[str, typer.Argument(help="Requirement ID (e.g., SPEC-009.FR-001)")],
  json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
  path_only: Annotated[bool, typer.Option("--path", help="Output path only")] = False,
  raw_output: Annotated[
    bool, typer.Option("--raw", help="Output raw file content")
  ] = False,
  root: RootOption = None,
) -> None:
  """Show detailed information about a requirement."""
  try:
    if sum([json_output, path_only, raw_output]) > 1:
      typer.echo("Error: --json, --path, and --raw are mutually exclusive", err=True)
      raise typer.Exit(EXIT_FAILURE)

    repo_root = find_repo_root(root)
    registry_path = repo_root / ".spec-driver" / "registry" / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    requirement = registry.records.get(req_id)

    if not requirement:
      typer.echo(f"Error: Requirement not found: {req_id}", err=True)
      raise typer.Exit(EXIT_FAILURE)

    if path_only or raw_output:
      req_dict = requirement.to_dict() if hasattr(requirement, "to_dict") else {}
      path_str = req_dict.get("path", "")
      if not path_str:
        typer.echo(f"Error: No path found for requirement: {req_id}", err=True)
        raise typer.Exit(EXIT_FAILURE)
      full_path = repo_root / path_str
      if path_only:
        typer.echo(full_path)
      else:
        typer.echo(full_path.read_text())
    elif json_output:
      output = (
        requirement.to_dict() if hasattr(requirement, "to_dict") else {"uid": req_id}
      )
      typer.echo(json.dumps(output, indent=2))
    else:
      typer.echo(format_requirement_details(requirement))

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("adr")
def show_adr(
  decision_id: Annotated[str, typer.Argument(help="Decision ID (e.g., ADR-001, 001)")],
  json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
  path_only: Annotated[bool, typer.Option("--path", help="Output path only")] = False,
  raw_output: Annotated[
    bool, typer.Option("--raw", help="Output raw file content")
  ] = False,
  root: RootOption = None,
) -> None:
  """Show detailed information about a specific decision/ADR."""
  try:
    if sum([json_output, path_only, raw_output]) > 1:
      typer.echo("Error: --json, --path, and --raw are mutually exclusive", err=True)
      raise typer.Exit(EXIT_FAILURE)

    normalized_id = normalize_id("adr", decision_id)
    registry = DecisionRegistry(root=root)
    decision = registry.find(normalized_id)

    if not decision:
      typer.echo(f"Error: Decision not found: {normalized_id}", err=True)
      raise typer.Exit(EXIT_FAILURE)

    if path_only:
      typer.echo(decision.path)
    elif raw_output:
      typer.echo(Path(decision.path).read_text())
    elif json_output:
      from supekku.scripts.lib.core.repo import find_repo_root

      repo_root = find_repo_root(root)
      output = decision.to_dict(repo_root)
      typer.echo(json.dumps(output, indent=2))
    else:
      typer.echo(format_decision_details(decision))

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("policy")
def show_policy(
  policy_id: Annotated[str, typer.Argument(help="Policy ID (e.g., POL-001, 001)")],
  json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
  path_only: Annotated[bool, typer.Option("--path", help="Output path only")] = False,
  raw_output: Annotated[
    bool, typer.Option("--raw", help="Output raw file content")
  ] = False,
  root: RootOption = None,
) -> None:
  """Show detailed information about a specific policy."""
  try:
    if sum([json_output, path_only, raw_output]) > 1:
      typer.echo("Error: --json, --path, and --raw are mutually exclusive", err=True)
      raise typer.Exit(EXIT_FAILURE)

    normalized_id = normalize_id("policy", policy_id)
    registry = PolicyRegistry(root=root)
    policy = registry.find(normalized_id)

    if not policy:
      typer.echo(f"Error: Policy not found: {normalized_id}", err=True)
      raise typer.Exit(EXIT_FAILURE)

    if path_only:
      typer.echo(policy.path)
    elif raw_output:
      typer.echo(Path(policy.path).read_text())
    elif json_output:
      from supekku.scripts.lib.core.repo import find_repo_root

      repo_root = find_repo_root(root)
      output = policy.to_dict(repo_root)
      typer.echo(json.dumps(output, indent=2))
    else:
      typer.echo(format_policy_details(policy))

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("standard")
def show_standard(
  standard_id: Annotated[str, typer.Argument(help="Standard ID (e.g., STD-001, 001)")],
  json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
  path_only: Annotated[bool, typer.Option("--path", help="Output path only")] = False,
  raw_output: Annotated[
    bool, typer.Option("--raw", help="Output raw file content")
  ] = False,
  root: RootOption = None,
) -> None:
  """Show detailed information about a specific standard."""
  try:
    if sum([json_output, path_only, raw_output]) > 1:
      typer.echo("Error: --json, --path, and --raw are mutually exclusive", err=True)
      raise typer.Exit(EXIT_FAILURE)

    normalized_id = normalize_id("standard", standard_id)
    registry = StandardRegistry(root=root)
    standard = registry.find(normalized_id)

    if not standard:
      typer.echo(f"Error: Standard not found: {normalized_id}", err=True)
      raise typer.Exit(EXIT_FAILURE)

    if path_only:
      typer.echo(standard.path)
    elif raw_output:
      typer.echo(Path(standard.path).read_text())
    elif json_output:
      from supekku.scripts.lib.core.repo import find_repo_root

      repo_root = find_repo_root(root)
      output = standard.to_dict(repo_root)
      typer.echo(json.dumps(output, indent=2))
    else:
      typer.echo(format_standard_details(standard))

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("template")
def show_template(
  kind: Annotated[str, typer.Argument(help="Spec kind: 'tech' or 'product'")],
  json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
  root: RootOption = None,
) -> None:
  """Show the specification template for a given kind."""
  try:
    # Validate kind
    if kind not in ("tech", "product"):
      typer.echo(
        f"Error: Invalid kind '{kind}'. Must be 'tech' or 'product'.",
        err=True,
      )
      raise typer.Exit(EXIT_FAILURE)

    # Map kind to template variable value
    template_kind = "prod" if kind == "product" else "spec"

    # Render template with placeholder variables
    variables = {
      "spec_id": "SPEC-XXX" if kind == "tech" else "PROD-XXX",
      "name": "specification name",
      "kind": template_kind,
      "spec_relationships_block": "",
      "spec_capabilities_block": "",
      "spec_verification_block": "",
    }

    template_content = render_template("spec.md", variables, root)

    if json_output:
      output = {
        "kind": kind,
        "template": template_content,
      }
      typer.echo(json.dumps(output, indent=2))
    else:
      typer.echo(template_content)

    raise typer.Exit(EXIT_SUCCESS)
  except TemplateNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except (FileNotFoundError, ValueError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("card")
def show_card(
  card_id: Annotated[str, typer.Argument(help="Card ID (e.g., T123)")],
  json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
  path_only: Annotated[
    bool,
    typer.Option(
      "--path",
      "-q",
      help="Print only the path (for scripting)",
    ),
  ] = False,
  raw_output: Annotated[
    bool, typer.Option("--raw", help="Output raw file content")
  ] = False,
  anywhere: Annotated[
    bool,
    typer.Option(
      "--anywhere",
      "-a",
      help="Search entire repo instead of just kanban/",
    ),
  ] = False,
  root: RootOption = None,
) -> None:
  """Show detailed information about a specific card."""
  try:
    if sum([json_output, path_only, raw_output]) > 1:
      typer.echo("Error: --json, --path, and --raw are mutually exclusive", err=True)
      raise typer.Exit(EXIT_FAILURE)

    registry = CardRegistry(root=root)

    if path_only:
      # Path-only output for --path/-q flag
      path = registry.resolve_path(card_id, anywhere=anywhere)
      typer.echo(path)
    elif raw_output:
      path = registry.resolve_path(card_id, anywhere=anywhere)
      typer.echo(Path(path).read_text())
    elif json_output:
      card = registry.resolve_card(card_id, anywhere=anywhere)
      typer.echo(json.dumps(card.to_dict(), indent=2))
    else:
      # Full card details
      card = registry.resolve_card(card_id, anywhere=anywhere)
      typer.echo(format_card_details(card))

    raise typer.Exit(EXIT_SUCCESS)

  except FileNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except ValueError as e:
    # Ambiguity error
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


# For direct testing
if __name__ == "__main__":  # pragma: no cover
  app()
