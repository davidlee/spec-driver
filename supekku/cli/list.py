"""List commands for specs, deltas, and changes.

Thin CLI layer: parse args → load registry → filter → format → output
Display formatting is delegated to supekku.scripts.lib.formatters
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS, RootOption
from supekku.scripts.lib.change_lifecycle import VALID_STATUSES, normalize_status
from supekku.scripts.lib.change_registry import ChangeRegistry
from supekku.scripts.lib.formatters.change_formatters import format_change_with_context
from supekku.scripts.lib.formatters.spec_formatters import format_spec_list_item
from supekku.scripts.lib.specs.registry import SpecRegistry

app = typer.Typer(help="List artifacts")


@app.command("specs")
def list_specs(
  root: RootOption = None,
  kind: Annotated[
    str,
    typer.Option(
      "--kind",
      "-k",
      help="Restrict to tech specs, product specs, or both",
    ),
  ] = "all",
  substring: Annotated[
    str | None,
    typer.Option(
      "--filter",
      "-f",
      help="Substring to match against spec ID, slug, or name (case-insensitive)",
    ),
  ] = None,
  package_filter: Annotated[
    str | None,
    typer.Option(
      "--package",
      "-p",
      help="Substring to match against declared package paths",
    ),
  ] = None,
  package_path: Annotated[
    str | None,
    typer.Option(
      "--package-path",
      help="Exact package path to resolve via by-package index",
    ),
  ] = None,
  for_path: Annotated[
    str | None,
    typer.Option(
      "--for-path",
      help="Filter specs whose packages include PATH",
    ),
  ] = None,
  paths: Annotated[
    bool,
    typer.Option(
      "--paths",
      help="Include relative file paths in the output",
    ),
  ] = False,
  packages: Annotated[
    bool,
    typer.Option(
      "--packages",
      help="Include package list in the output",
    ),
  ] = False,
) -> None:
  """List SPEC/PROD artifacts with optional filtering."""
  if kind not in ["tech", "product", "all"]:
    typer.echo(f"Error: invalid kind: {kind}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  try:
    registry = SpecRegistry(root)
    filter_substring = (substring or "").strip().lower()

    spec_root = registry.root / "specify" / "tech"
    package_index_root = spec_root / "by-package"

    package_filters: list[str] = []
    package_exact: set[str] = set()

    if package_filter:
      package_filters.append(package_filter.strip().lower())

    def resolve_package_path(pkg_path: str) -> None:
      node = package_index_root / Path(pkg_path) / "spec"
      if node.exists():
        try:
          target = node.resolve()
          package_exact.add(target.name)
        except OSError:
          pass

    if package_path:
      resolve_package_path(package_path.strip())

    if for_path is not None:
      raw_path = for_path
      base = Path.cwd() if raw_path == "." else Path(raw_path)
      if not base.is_absolute():
        base = (Path.cwd() / base).resolve()
      try:
        relative = base.relative_to(package_index_root)
        resolve_package_path(str(relative))
      except ValueError:
        try:
          relative = base.relative_to(registry.root)
          package_filters.append(relative.as_posix().lower())
        except ValueError:
          package_filters.append(base.as_posix().lower())

    specs = registry.all_specs()
    if filter_substring:
      specs = [
        spec
        for spec in specs
        if filter_substring in spec.id.lower()
        or filter_substring in spec.slug.lower()
        or filter_substring in spec.name.lower()
      ]

    if package_exact:
      specs = [spec for spec in specs if spec.id in package_exact]

    if package_filters:
      specs = [
        spec
        for spec in specs
        if spec.packages
        and any(
          any(filter_value in pkg.lower() for pkg in spec.packages)
          for filter_value in package_filters
        )
      ]

    specs.sort(key=lambda spec: spec.id)

    def normalise_kind(requested: str, spec_id: str) -> bool:
      if requested == "all":
        return True
      if requested == "tech":
        return spec_id.startswith("SPEC-")
      if requested == "product":
        return spec_id.startswith("PROD-")
      return True

    for spec in specs:
      if not normalise_kind(kind, spec.id):
        continue
      line = format_spec_list_item(
        spec,
        include_path=paths,
        include_packages=packages,
        root=registry.root,
      )
      typer.echo(line)

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("deltas")
def list_deltas(
  root: RootOption = None,
  ids: Annotated[
    list[str] | None,
    typer.Argument(
      help="Specific delta IDs to display (e.g., DE-002 DE-005)",
    ),
  ] = None,
  status: Annotated[
    str | None,
    typer.Option(
      "--status",
      "-s",
      help=f"Filter by status. Valid: {', '.join(sorted(VALID_STATUSES))}",
    ),
  ] = None,
  details: Annotated[
    bool,
    typer.Option(
      "--details",
      "-d",
      help="Show related specs, requirements, and phases",
    ),
  ] = False,
) -> None:
  """List deltas with optional filtering and status grouping."""
  try:
    registry = ChangeRegistry(root=root, kind="delta")
    artifacts = registry.collect()

    if not artifacts:
      raise typer.Exit(EXIT_SUCCESS)

    delta_ids = set(ids) if ids else None

    for artifact in artifacts.values():
      # Check filters
      if delta_ids is not None and artifact.id not in delta_ids:
        continue
      if status and normalize_status(artifact.status) != normalize_status(status):
        continue

      # Format and output
      if details:
        output = format_change_with_context(artifact)
      else:
        output = f"{artifact.id}\t{artifact.status}\t{artifact.name}"
      typer.echo(output)

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("changes")
def list_changes(
  root: RootOption = None,
  kind: Annotated[
    str,
    typer.Option(
      "--kind",
      "-k",
      help="Change artifact kind to list (delta, revision, audit, all)",
    ),
  ] = "all",
  substring: Annotated[
    str | None,
    typer.Option(
      "--filter",
      "-f",
      help="Substring to match against ID, slug, or name (case-insensitive)",
    ),
  ] = None,
  status: Annotated[
    str | None,
    typer.Option(
      "--status",
      "-s",
      help="Filter by status (exact match)",
    ),
  ] = None,
  applies_to: Annotated[
    str | None,
    typer.Option(
      "--applies-to",
      "-a",
      help="Filter artifacts that reference a requirement",
    ),
  ] = None,
  paths: Annotated[
    bool,
    typer.Option(
      "--paths",
      help="Include relative file paths",
    ),
  ] = False,
  relations: Annotated[
    bool,
    typer.Option(
      "--relations",
      help="Include relation tuples (type:target)",
    ),
  ] = False,
  applies: Annotated[
    bool,
    typer.Option(
      "--applies",
      help="Include applies_to.requirements list",
    ),
  ] = False,
  plan: Annotated[
    bool,
    typer.Option(
      "--plan",
      help="Include plan overview for deltas",
    ),
  ] = False,
) -> None:
  """List change artifacts (deltas, revisions, audits) with optional filters."""
  if kind not in ["delta", "revision", "audit", "all"]:
    typer.echo(f"Error: invalid kind: {kind}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  try:
    kinds = ["delta", "revision", "audit"] if kind == "all" else [kind]

    for current_kind in kinds:
      registry = ChangeRegistry(root=root, kind=current_kind)
      artifacts = registry.collect()

      for artifact in artifacts.values():
        # Check filters
        if substring:
          text = substring.lower()
          if not (
            text in artifact.id.lower()
            or text in artifact.slug.lower()
            or text in artifact.name.lower()
          ):
            continue
        if status and artifact.status.lower() != status.lower():
          continue
        if applies_to:
          match = applies_to.lower()
          applies_list = []
          reqs = artifact.applies_to.get("requirements") if artifact.applies_to else []
          if isinstance(reqs, list):
            applies_list.extend(str(item).lower() for item in reqs)
          for relation in artifact.relations:
            target = str(relation.get("target", "")).lower()
            applies_list.append(target)
          if match not in applies_list:
            continue

        # Format output
        line = f"{artifact.id}\t{artifact.name}"

        if paths and hasattr(artifact, "path"):
          try:
            rel = artifact.path.relative_to(root)
          except (ValueError, AttributeError):
            rel = artifact.path if hasattr(artifact, "path") else ""
          line += f"\t{rel.as_posix() if rel else ''}"

        if relations and artifact.relations:
          rel_str = ", ".join(
            f"{r.get('type', '?')}:{r.get('target', '?')}" for r in artifact.relations
          )
          line += f"\t{rel_str}"

        if applies and artifact.applies_to:
          reqs = artifact.applies_to.get("requirements", [])
          if reqs:
            line += f"\t{', '.join(str(r) for r in reqs)}"

        if plan and current_kind == "delta" and artifact.plan:
          plan_id = artifact.plan.get("plan_id", "")
          phases = artifact.plan.get("phases", [])
          phase_count = len(phases) if phases else 0
          line += f"\t{plan_id}\t{phase_count} phases"

        typer.echo(line)

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


# For direct testing
if __name__ == "__main__":  # pragma: no cover
  app()
