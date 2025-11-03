"""List commands for specs, deltas, and changes.

Thin CLI layer: parse args → load registry → filter → format → output
Display formatting is delegated to supekku.scripts.lib.formatters
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Annotated

import typer

from supekku.cli.common import (
  EXIT_FAILURE,
  EXIT_SUCCESS,
  CaseInsensitiveOption,
  FormatOption,
  RegexpOption,
  RootOption,
  TruncateOption,
  matches_regexp,
)
from supekku.scripts.lib.changes.lifecycle import VALID_STATUSES, normalize_status
from supekku.scripts.lib.changes.registry import ChangeRegistry
from supekku.scripts.lib.core.filters import parse_multi_value_filter
from supekku.scripts.lib.decisions.registry import DecisionRegistry
from supekku.scripts.lib.formatters.backlog_formatters import format_backlog_list_table
from supekku.scripts.lib.formatters.change_formatters import (
  format_change_list_table,
  format_change_with_context,
)
from supekku.scripts.lib.formatters.decision_formatters import (
  format_decision_list_table,
)
from supekku.scripts.lib.formatters.policy_formatters import format_policy_list_table
from supekku.scripts.lib.formatters.requirement_formatters import (
  format_requirement_list_table,
)
from supekku.scripts.lib.formatters.spec_formatters import (
  format_spec_list_item,
  format_spec_list_table,
)
from supekku.scripts.lib.formatters.standard_formatters import (
  format_standard_list_table,
)
from supekku.scripts.lib.policies.registry import PolicyRegistry
from supekku.scripts.lib.specs.registry import SpecRegistry
from supekku.scripts.lib.standards.registry import StandardRegistry

app = typer.Typer(help="List artifacts", no_args_is_help=True)


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
  status: Annotated[
    str | None,
    typer.Option(
      "--status",
      "-s",
      help="Filter by status (draft, active, deprecated, superseded)",
    ),
  ] = None,
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
  regexp: RegexpOption = None,
  case_insensitive: CaseInsensitiveOption = False,
  format_type: FormatOption = "table",
  json_output: Annotated[
    bool,
    typer.Option(
      "--json",
      help="Output result as JSON (shorthand for --format=json)",
    ),
  ] = False,
  truncate: TruncateOption = False,
  paths: Annotated[
    bool,
    typer.Option(
      "--paths",
      help="Include relative file paths in the output (TSV format only)",
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
  """List SPEC/PROD artifacts with optional filtering.

  The --filter flag does substring matching (case-insensitive).
  The --regexp flag does pattern matching on ID, slug, and name fields.
  """
  # --json flag overrides --format
  if json_output:
    format_type = "json"

  # Parse multi-value kind filter
  kind_values = parse_multi_value_filter(kind) if kind != "all" else []
  # Validate kind values
  valid_kinds = {"tech", "product", "prod", "all"}
  for k in kind_values:
    if k not in valid_kinds:
      typer.echo(f"Error: invalid kind: {k}", err=True)
      raise typer.Exit(EXIT_FAILURE)

  # Validate format
  if format_type not in ["table", "json", "tsv"]:
    typer.echo(f"Error: invalid format: {format_type}", err=True)
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

    # Apply status filter (multi-value OR logic)
    if status:
      status_values = parse_multi_value_filter(status)
      status_normalized = [normalize_status(s) for s in status_values]
      specs = [
        spec for spec in specs if normalize_status(spec.status) in status_normalized
      ]

    if filter_substring:
      specs = [
        spec
        for spec in specs
        if filter_substring in spec.id.lower()
        or filter_substring in spec.slug.lower()
        or filter_substring in spec.name.lower()
      ]

    # Apply regexp filter on id, slug, name
    if regexp:
      try:
        specs = [
          spec
          for spec in specs
          if matches_regexp(regexp, [spec.id, spec.slug, spec.name], case_insensitive)
        ]
      except re.error as e:
        typer.echo(f"Error: invalid regexp pattern: {e}", err=True)
        raise typer.Exit(EXIT_FAILURE) from e

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

    # Filter by kind (multi-value OR logic)
    def normalise_kind(requested_kinds: list[str], spec_id: str) -> bool:
      if not requested_kinds:  # "all" or no filter
        return True
      # Check if spec matches any of the requested kinds
      for k in requested_kinds:
        if k in ("tech", "all") and spec_id.startswith("SPEC-"):
          return True
        if k in ("product", "prod", "all") and spec_id.startswith("PROD-"):
          return True
      return False

    specs = [spec for spec in specs if normalise_kind(kind_values, spec.id)]

    if not specs:
      raise typer.Exit(EXIT_SUCCESS)

    # Sort and format
    specs.sort(key=lambda spec: spec.id)

    # For TSV with paths, use old formatter; otherwise use new table formatter
    if format_type == "tsv" and paths:
      for spec in specs:
        line = format_spec_list_item(
          spec,
          include_path=paths,
          include_packages=packages,
          root=registry.root,
        )
        typer.echo(line)
    else:
      output = format_spec_list_table(
        specs,
        format_type=format_type,
        no_truncate=not truncate,
        include_packages=packages,
      )
      typer.echo(output)

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
  regexp: RegexpOption = None,
  case_insensitive: CaseInsensitiveOption = False,
  format_type: FormatOption = "table",
  json_output: Annotated[
    bool,
    typer.Option(
      "--json",
      help="Output result as JSON (shorthand for --format=json)",
    ),
  ] = False,
  truncate: TruncateOption = False,
  details: Annotated[
    bool,
    typer.Option(
      "--details",
      "-d",
      help="Show related specs, requirements, and phases (TSV format only)",
    ),
  ] = False,
) -> None:
  """List deltas with optional filtering and status grouping.

  The --regexp flag filters on ID, name, and slug fields.
  """
  # --json flag overrides --format
  if json_output:
    format_type = "json"

  # Validate format
  if format_type not in ["table", "json", "tsv"]:
    typer.echo(f"Error: invalid format: {format_type}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  try:
    registry = ChangeRegistry(root=root, kind="delta")
    artifacts = registry.collect()

    if not artifacts:
      raise typer.Exit(EXIT_SUCCESS)

    delta_ids = set(ids) if ids else None

    # Parse multi-value status filter
    status_values = parse_multi_value_filter(status)
    status_normalized = (
      [normalize_status(s) for s in status_values] if status_values else []
    )

    # Apply filters
    filtered_artifacts = []
    for artifact in artifacts.values():
      # Check ID filter
      if delta_ids is not None and artifact.id not in delta_ids:
        continue
      # Check status filter (multi-value OR logic)
      if (
        status_normalized and normalize_status(artifact.status) not in status_normalized
      ):
        continue
      # Check regexp filter on id, name, slug
      if regexp:
        try:
          if not matches_regexp(
            regexp,
            [artifact.id, artifact.name, artifact.slug],
            case_insensitive,
          ):
            continue
        except re.error as e:
          typer.echo(f"Error: invalid regexp pattern: {e}", err=True)
          raise typer.Exit(EXIT_FAILURE) from e

      filtered_artifacts.append(artifact)

    if not filtered_artifacts:
      raise typer.Exit(EXIT_SUCCESS)

    # Sort by ID (alphabetical order)
    filtered_artifacts.sort(key=lambda x: x.id)

    # Format and output
    # For TSV with details, use old formatter; otherwise use new table formatter
    if format_type == "tsv" and details:
      for artifact in filtered_artifacts:
        output = format_change_with_context(artifact)
        typer.echo(output)
    else:
      output = format_change_list_table(
        filtered_artifacts,
        format_type=format_type,
        no_truncate=not truncate,
      )
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
  regexp: RegexpOption = None,
  case_insensitive: CaseInsensitiveOption = False,
  format_type: FormatOption = "table",
  json_output: Annotated[
    bool,
    typer.Option(
      "--json",
      help="Output result as JSON (shorthand for --format=json)",
    ),
  ] = False,
  truncate: TruncateOption = False,
  paths: Annotated[
    bool,
    typer.Option(
      "--paths",
      help="Include relative file paths (TSV format only)",
    ),
  ] = False,
  relations: Annotated[
    bool,
    typer.Option(
      "--relations",
      help="Include relation tuples (type:target) (TSV format only)",
    ),
  ] = False,
  applies: Annotated[
    bool,
    typer.Option(
      "--applies",
      help="Include applies_to.requirements list (TSV format only)",
    ),
  ] = False,
  plan: Annotated[
    bool,
    typer.Option(
      "--plan",
      help="Include plan overview for deltas (TSV format only)",
    ),
  ] = False,
) -> None:
  """List change artifacts (deltas, revisions, audits) with optional filters.

  The --filter flag does substring matching (case-insensitive).
  The --regexp flag does pattern matching on ID, slug, and name fields.
  """
  # --json flag overrides --format
  if json_output:
    format_type = "json"

  # Parse multi-value kind filter
  kind_values = parse_multi_value_filter(kind) if kind != "all" else []
  # Validate kind values
  valid_change_kinds = {"delta", "revision", "audit", "all"}
  for k in kind_values:
    if k not in valid_change_kinds:
      typer.echo(f"Error: invalid kind: {k}", err=True)
      raise typer.Exit(EXIT_FAILURE)

  # Validate format
  if format_type not in ["table", "json", "tsv"]:
    typer.echo(f"Error: invalid format: {format_type}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  try:
    # Multi-value kind filter - expand "all" or use parsed values
    kinds = kind_values if kind_values else ["delta", "revision", "audit"]
    all_artifacts = []

    # Parse multi-value status filter
    status_values = parse_multi_value_filter(status)
    status_normalized = [s.lower() for s in status_values] if status_values else []

    for current_kind in kinds:
      registry = ChangeRegistry(root=root, kind=current_kind)
      artifacts = registry.collect()

      for artifact in artifacts.values():
        # Check substring filter
        if substring:
          text = substring.lower()
          if not (
            text in artifact.id.lower()
            or text in artifact.slug.lower()
            or text in artifact.name.lower()
          ):
            continue

        # Check regexp filter
        if regexp:
          try:
            if not matches_regexp(
              regexp,
              [artifact.id, artifact.slug, artifact.name],
              case_insensitive,
            ):
              continue
          except re.error as e:
            typer.echo(f"Error: invalid regexp pattern: {e}", err=True)
            raise typer.Exit(EXIT_FAILURE) from e

        # Check status filter (multi-value OR logic)
        if status_normalized and artifact.status.lower() not in status_normalized:
          continue

        # Check applies_to filter
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

        all_artifacts.append((current_kind, artifact))

    if not all_artifacts:
      raise typer.Exit(EXIT_SUCCESS)

    # Sort by ID (alphabetical order)
    all_artifacts.sort(key=lambda x: x[1].id)

    # Format and output
    # For TSV with extra columns, use old formatter; otherwise use new table formatter
    has_extra_columns = paths or relations or applies or plan
    if format_type == "tsv" and has_extra_columns:
      for current_kind, artifact in all_artifacts:
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
    else:
      # Extract just the artifacts
      artifacts_only = [artifact for _, artifact in all_artifacts]
      output = format_change_list_table(
        artifacts_only,
        format_type=format_type,
        no_truncate=not truncate,
      )
      typer.echo(output)

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("adrs")
def list_adrs(
  root: RootOption = None,
  status: Annotated[
    str | None,
    typer.Option(
      "--status",
      "-s",
      help="Filter by status (accepted, draft, deprecated, etc.)",
    ),
  ] = None,
  tag: Annotated[
    str | None,
    typer.Option(
      "--tag",
      "-t",
      help="Filter by tag",
    ),
  ] = None,
  spec: Annotated[
    str | None,
    typer.Option(
      "--spec",
      help="Filter by spec reference",
    ),
  ] = None,
  delta: Annotated[
    str | None,
    typer.Option(
      "--delta",
      "-d",
      help="Filter by delta reference",
    ),
  ] = None,
  requirement_filter: Annotated[
    str | None,
    typer.Option(
      "--requirement",
      help="Filter by requirement reference",
    ),
  ] = None,
  policy: Annotated[
    str | None,
    typer.Option(
      "--policy",
      "-p",
      help="Filter by policy reference",
    ),
  ] = None,
  standard: Annotated[
    str | None,
    typer.Option(
      "--standard",
      help="Filter by standard reference",
    ),
  ] = None,
  regexp: RegexpOption = None,
  case_insensitive: CaseInsensitiveOption = False,
  format_type: FormatOption = "table",
  json_output: Annotated[
    bool,
    typer.Option(
      "--json",
      help="Output result as JSON (shorthand for --format=json)",
    ),
  ] = False,
  truncate: TruncateOption = False,
) -> None:
  """List Architecture Decision Records (ADRs) with optional filtering.

  The --regexp flag filters on title and summary fields.
  Other flags filter on specific structured fields (status, tags, references).
  """
  # --json flag overrides --format
  if json_output:
    format_type = "json"

  # Validate format
  if format_type not in ["table", "json", "tsv"]:
    typer.echo(f"Error: invalid format: {format_type}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  try:
    registry = DecisionRegistry(root=root)

    # Apply structured filters
    if any([tag, spec, delta, requirement_filter, policy, standard]):
      decisions = registry.filter(
        tag=tag,
        spec=spec,
        delta=delta,
        requirement=requirement_filter,
        policy=policy,
        standard=standard,
      )
    else:
      decisions = list(registry.iter(status=status))

    # Apply regexp filter on title and summary
    if regexp:
      try:
        decisions = [
          d
          for d in decisions
          if matches_regexp(regexp, [d.title, d.summary], case_insensitive)
        ]
      except re.error as e:
        typer.echo(f"Error: invalid regexp pattern: {e}", err=True)
        raise typer.Exit(EXIT_FAILURE) from e

    if not decisions:
      raise typer.Exit(EXIT_SUCCESS)

    # Sort and format
    decisions_sorted = sorted(decisions, key=lambda d: d.id)
    output = format_decision_list_table(decisions_sorted, format_type, truncate)
    typer.echo(output)

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("policies")
def list_policies(
  root: RootOption = None,
  status: Annotated[
    str | None,
    typer.Option(
      "--status",
      "-s",
      help="Filter by status (draft, required, deprecated)",
    ),
  ] = None,
  tag: Annotated[
    str | None,
    typer.Option(
      "--tag",
      "-t",
      help="Filter by tag",
    ),
  ] = None,
  spec: Annotated[
    str | None,
    typer.Option(
      "--spec",
      help="Filter by spec reference",
    ),
  ] = None,
  delta: Annotated[
    str | None,
    typer.Option(
      "--delta",
      "-d",
      help="Filter by delta reference",
    ),
  ] = None,
  requirement_filter: Annotated[
    str | None,
    typer.Option(
      "--requirement",
      help="Filter by requirement reference",
    ),
  ] = None,
  standard: Annotated[
    str | None,
    typer.Option(
      "--standard",
      help="Filter by standard reference",
    ),
  ] = None,
  regexp: RegexpOption = None,
  case_insensitive: CaseInsensitiveOption = False,
  format_type: FormatOption = "table",
  json_output: Annotated[
    bool,
    typer.Option(
      "--json",
      help="Output result as JSON (shorthand for --format=json)",
    ),
  ] = False,
  truncate: TruncateOption = False,
) -> None:
  """List policies with optional filtering.

  The --regexp flag filters on title and summary fields.
  Other flags filter on specific structured fields (status, tags, references).
  """
  # --json flag overrides --format
  if json_output:
    format_type = "json"

  # Validate format
  if format_type not in ["table", "json", "tsv"]:
    typer.echo(f"Error: invalid format: {format_type}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  try:
    registry = PolicyRegistry(root=root)

    # Apply structured filters
    if any([tag, spec, delta, requirement_filter, standard]):
      policies = registry.filter(
        tag=tag,
        spec=spec,
        delta=delta,
        requirement=requirement_filter,
        standard=standard,
      )
    else:
      policies = list(registry.iter(status=status))

    # Apply regexp filter on title
    if regexp:
      try:
        policies = [
          p for p in policies if matches_regexp(regexp, [p.title], case_insensitive)
        ]
      except re.error as e:
        typer.echo(f"Error: invalid regexp pattern: {e}", err=True)
        raise typer.Exit(EXIT_FAILURE) from e

    if not policies:
      raise typer.Exit(EXIT_SUCCESS)

    # Sort and format
    policies_sorted = sorted(policies, key=lambda p: p.id)
    output = format_policy_list_table(policies_sorted, format_type, truncate)
    typer.echo(output)

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("standards")
def list_standards(
  root: RootOption = None,
  status: Annotated[
    str | None,
    typer.Option(
      "--status",
      "-s",
      help="Filter by status (draft, required, default, deprecated)",
    ),
  ] = None,
  tag: Annotated[
    str | None,
    typer.Option(
      "--tag",
      "-t",
      help="Filter by tag",
    ),
  ] = None,
  spec: Annotated[
    str | None,
    typer.Option(
      "--spec",
      help="Filter by spec reference",
    ),
  ] = None,
  delta: Annotated[
    str | None,
    typer.Option(
      "--delta",
      "-d",
      help="Filter by delta reference",
    ),
  ] = None,
  requirement_filter: Annotated[
    str | None,
    typer.Option(
      "--requirement",
      help="Filter by requirement reference",
    ),
  ] = None,
  policy: Annotated[
    str | None,
    typer.Option(
      "--policy",
      "-p",
      help="Filter by policy reference",
    ),
  ] = None,
  regexp: RegexpOption = None,
  case_insensitive: CaseInsensitiveOption = False,
  format_type: FormatOption = "table",
  json_output: Annotated[
    bool,
    typer.Option(
      "--json",
      help="Output result as JSON (shorthand for --format=json)",
    ),
  ] = False,
  truncate: TruncateOption = False,
) -> None:
  """List standards with optional filtering.

  The --regexp flag filters on title and summary fields.
  Other flags filter on specific structured fields (status, tags, references).
  """
  # --json flag overrides --format
  if json_output:
    format_type = "json"

  # Validate format
  if format_type not in ["table", "json", "tsv"]:
    typer.echo(f"Error: invalid format: {format_type}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  try:
    registry = StandardRegistry(root=root)

    # Apply structured filters
    if any([tag, spec, delta, requirement_filter, policy]):
      standards = registry.filter(
        tag=tag,
        spec=spec,
        delta=delta,
        requirement=requirement_filter,
        policy=policy,
      )
    else:
      standards = list(registry.iter(status=status))

    # Apply regexp filter on title
    if regexp:
      try:
        standards = [
          s for s in standards if matches_regexp(regexp, [s.title], case_insensitive)
        ]
      except re.error as e:
        typer.echo(f"Error: invalid regexp pattern: {e}", err=True)
        raise typer.Exit(EXIT_FAILURE) from e

    if not standards:
      raise typer.Exit(EXIT_SUCCESS)

    # Sort and format
    standards_sorted = sorted(standards, key=lambda s: s.id)
    output = format_standard_list_table(standards_sorted, format_type, truncate)
    typer.echo(output)

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("requirements")
def list_requirements(
  root: RootOption = None,
  spec: Annotated[
    str | None,
    typer.Option("--spec", "-s", help="Filter by spec ID"),
  ] = None,
  status: Annotated[
    str | None,
    typer.Option("--status", help="Filter by status"),
  ] = None,
  kind: Annotated[
    str | None,
    typer.Option("--kind", "-k", help="Filter by kind (FR|NF)"),
  ] = None,
  category: Annotated[
    str | None,
    typer.Option("--category", "-c", help="Filter by category (substring match)"),
  ] = None,
  substring: Annotated[
    str | None,
    typer.Option(
      "--filter",
      "-f",
      help="Substring filter on label or title (case-insensitive)",
    ),
  ] = None,
  regexp: RegexpOption = None,
  case_insensitive: CaseInsensitiveOption = False,
  format_type: FormatOption = "table",
  json_output: Annotated[
    bool,
    typer.Option(
      "--json",
      help="Output result as JSON (shorthand for --format=json)",
    ),
  ] = False,
  truncate: TruncateOption = False,
) -> None:
  """List requirements with optional filtering.

  The --filter flag does substring matching (case-insensitive).
  The --regexp flag does pattern matching on UID, label, title, and category fields.
  The --category flag does substring matching on category field.
  Use --case-insensitive (-i) to make regexp and category filters case-insensitive.
  """
  # --json flag overrides --format
  if json_output:
    format_type = "json"

  # Validate format
  if format_type not in ["table", "json", "tsv"]:
    typer.echo(f"Error: invalid format: {format_type}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  try:
    from pathlib import Path

    from supekku.scripts.lib.core.paths import get_registry_dir
    from supekku.scripts.lib.requirements.registry import RequirementsRegistry

    repo_root = Path(root) if root else Path.cwd()
    registry_path = get_registry_dir(repo_root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    requirements = list(registry.records.values())

    # Apply filters
    if spec:
      requirements = [r for r in requirements if spec.upper() in r.specs]

    # Multi-value status filter (OR logic)
    if status:
      status_values = parse_multi_value_filter(status)
      status_normalized = [s.lower() for s in status_values]
      requirements = [r for r in requirements if r.status.lower() in status_normalized]

    # Multi-value kind filter (OR logic)
    if kind:
      kind_values = parse_multi_value_filter(kind)
      kind_prefixes = [k.upper() for k in kind_values]
      requirements = [
        r
        for r in requirements
        if any(r.label.startswith(prefix) for prefix in kind_prefixes)
      ]

    # Category filter (substring match, respects --case-insensitive)
    if category:
      if case_insensitive:
        category_lower = category.lower()
        requirements = [
          r
          for r in requirements
          if r.category and category_lower in r.category.lower()
        ]
      else:
        requirements = [
          r for r in requirements if r.category and category in r.category
        ]

    if substring:
      filter_lower = substring.lower()
      requirements = [
        r
        for r in requirements
        if filter_lower in r.label.lower() or filter_lower in r.title.lower()
      ]

    # Apply regexp filter on uid, label, title, category
    if regexp:
      try:
        requirements = [
          r
          for r in requirements
          if matches_regexp(
            regexp, [r.uid, r.label, r.title, r.category or ""], case_insensitive
          )
        ]
      except re.error as e:
        typer.echo(f"Error: invalid regexp pattern: {e}", err=True)
        raise typer.Exit(EXIT_FAILURE) from e

    if not requirements:
      raise typer.Exit(EXIT_SUCCESS)

    # Sort and format
    requirements.sort(key=lambda r: r.uid)
    output = format_requirement_list_table(requirements, format_type, truncate)
    typer.echo(output)

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("revisions")
def list_revisions(
  root: RootOption = None,
  status: Annotated[
    str | None,
    typer.Option("--status", "-s", help="Filter by status"),
  ] = None,
  spec: Annotated[
    str | None,
    typer.Option("--spec", help="Filter by spec reference"),
  ] = None,
  substring: Annotated[
    str | None,
    typer.Option(
      "--filter",
      "-f",
      help="Substring filter on ID or name (case-insensitive)",
    ),
  ] = None,
  regexp: RegexpOption = None,
  case_insensitive: CaseInsensitiveOption = False,
  format_type: FormatOption = "table",
  json_output: Annotated[
    bool,
    typer.Option(
      "--json",
      help="Output result as JSON (shorthand for --format=json)",
    ),
  ] = False,
  truncate: TruncateOption = False,
) -> None:
  """List revisions with optional filtering.

  The --filter flag does substring matching (case-insensitive).
  The --regexp flag does pattern matching on ID, slug, and name fields.
  """
  # --json flag overrides --format
  if json_output:
    format_type = "json"

  # Validate format
  if format_type not in ["table", "json", "tsv"]:
    typer.echo(f"Error: invalid format: {format_type}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  try:
    registry = ChangeRegistry(root=root, kind="revision")
    revisions = list(registry.collect().values())

    # Apply filters (multi-value status OR logic)
    if status:
      status_values = parse_multi_value_filter(status)
      status_normalized = [s.lower() for s in status_values]
      revisions = [r for r in revisions if r.status.lower() in status_normalized]
    if spec:
      spec_upper = spec.upper()
      revisions = [
        r
        for r in revisions
        if r.relations
        and any(spec_upper in str(rel.get("target", "")).upper() for rel in r.relations)
      ]
    if substring:
      filter_lower = substring.lower()
      revisions = [
        r
        for r in revisions
        if filter_lower in r.id.lower() or filter_lower in r.name.lower()
      ]

    # Apply regexp filter on id, slug, name
    if regexp:
      try:
        revisions = [
          r
          for r in revisions
          if matches_regexp(regexp, [r.id, r.slug, r.name], case_insensitive)
        ]
      except re.error as e:
        typer.echo(f"Error: invalid regexp pattern: {e}", err=True)
        raise typer.Exit(EXIT_FAILURE) from e

    if not revisions:
      raise typer.Exit(EXIT_SUCCESS)

    # Sort and format
    revisions.sort(key=lambda r: r.id)
    output = format_change_list_table(revisions, format_type, not truncate)
    typer.echo(output)

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("backlog")
def list_backlog(
  root: RootOption = None,
  kind: Annotated[
    str,
    typer.Option(
      "--kind",
      "-k",
      help="Filter by kind (issue|problem|improvement|risk|all)",
    ),
  ] = "all",
  status: Annotated[
    str | None,
    typer.Option("--status", "-s", help="Filter by status"),
  ] = None,
  substring: Annotated[
    str | None,
    typer.Option(
      "--filter",
      "-f",
      help="Substring filter on title (case-insensitive)",
    ),
  ] = None,
  regexp: RegexpOption = None,
  case_insensitive: CaseInsensitiveOption = False,
  format_type: FormatOption = "table",
  truncate: TruncateOption = False,
  order_by_id: Annotated[
    bool,
    typer.Option(
      "--order-by-id",
      "-o",
      help="Order by ID (chronological) instead of priority",
    ),
  ] = False,
) -> None:
  """List backlog items with optional filtering.

  By default, items are sorted by priority (registry order → severity → ID).
  Use --order-by-id to sort chronologically by ID instead.

  The --filter flag does substring matching (case-insensitive).
  The --regexp flag does pattern matching on ID and title fields.
  """
  if kind not in ["issue", "problem", "improvement", "risk", "all"]:
    typer.echo(f"Error: invalid kind: {kind}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  # Validate format
  if format_type not in ["table", "json", "tsv"]:
    typer.echo(f"Error: invalid format: {format_type}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  try:
    from pathlib import Path

    from supekku.scripts.lib.backlog.priority import sort_by_priority
    from supekku.scripts.lib.backlog.registry import (
      discover_backlog_items,
      load_backlog_registry,
    )

    repo_root = Path(root) if root else None
    items = discover_backlog_items(root=repo_root, kind=kind)

    # Apply filters
    if status:
      items = [i for i in items if i.status.lower() == status.lower()]
    if substring:
      filter_lower = substring.lower()
      items = [i for i in items if filter_lower in i.title.lower()]

    # Apply regexp filter on id, title
    if regexp:
      try:
        items = [
          i for i in items if matches_regexp(regexp, [i.id, i.title], case_insensitive)
        ]
      except re.error as e:
        typer.echo(f"Error: invalid regexp pattern: {e}", err=True)
        raise typer.Exit(EXIT_FAILURE) from e

    if not items:
      raise typer.Exit(EXIT_SUCCESS)

    # Apply priority ordering (unless --order-by-id specified)
    if not order_by_id:
      ordering = load_backlog_registry(root=repo_root)
      items = sort_by_priority(items, ordering)

    # Format and output
    output = format_backlog_list_table(items, format_type, truncate)
    typer.echo(output)

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("issues")
def list_issues(
  root: RootOption = None,
  status: Annotated[
    str | None,
    typer.Option("--status", "-s", help="Filter by status"),
  ] = None,
  substring: Annotated[
    str | None,
    typer.Option(
      "--filter",
      "-f",
      help="Substring filter on title (case-insensitive)",
    ),
  ] = None,
  regexp: RegexpOption = None,
  case_insensitive: CaseInsensitiveOption = False,
  format_type: FormatOption = "table",
  truncate: TruncateOption = False,
) -> None:
  """List backlog issues with optional filtering.

  Shortcut for: list backlog --kind issue
  """
  list_backlog(
    root=root,
    kind="issue",
    status=status,
    substring=substring,
    regexp=regexp,
    case_insensitive=case_insensitive,
    format_type=format_type,
    truncate=truncate,
  )


@app.command("problems")
def list_problems(
  root: RootOption = None,
  status: Annotated[
    str | None,
    typer.Option("--status", "-s", help="Filter by status"),
  ] = None,
  substring: Annotated[
    str | None,
    typer.Option(
      "--filter",
      "-f",
      help="Substring filter on title (case-insensitive)",
    ),
  ] = None,
  regexp: RegexpOption = None,
  case_insensitive: CaseInsensitiveOption = False,
  format_type: FormatOption = "table",
  truncate: TruncateOption = False,
) -> None:
  """List backlog problems with optional filtering.

  Shortcut for: list backlog --kind problem
  """
  list_backlog(
    root=root,
    kind="problem",
    status=status,
    substring=substring,
    regexp=regexp,
    case_insensitive=case_insensitive,
    format_type=format_type,
    truncate=truncate,
  )


@app.command("improvements")
def list_improvements(
  root: RootOption = None,
  status: Annotated[
    str | None,
    typer.Option("--status", "-s", help="Filter by status"),
  ] = None,
  substring: Annotated[
    str | None,
    typer.Option(
      "--filter",
      "-f",
      help="Substring filter on title (case-insensitive)",
    ),
  ] = None,
  regexp: RegexpOption = None,
  case_insensitive: CaseInsensitiveOption = False,
  format_type: FormatOption = "table",
  truncate: TruncateOption = False,
) -> None:
  """List backlog improvements with optional filtering.

  Shortcut for: list backlog --kind improvement
  """
  list_backlog(
    root=root,
    kind="improvement",
    status=status,
    substring=substring,
    regexp=regexp,
    case_insensitive=case_insensitive,
    format_type=format_type,
    truncate=truncate,
  )


@app.command("risks")
def list_risks(
  root: RootOption = None,
  status: Annotated[
    str | None,
    typer.Option("--status", "-s", help="Filter by status"),
  ] = None,
  substring: Annotated[
    str | None,
    typer.Option(
      "--filter",
      "-f",
      help="Substring filter on title (case-insensitive)",
    ),
  ] = None,
  regexp: RegexpOption = None,
  case_insensitive: CaseInsensitiveOption = False,
  format_type: FormatOption = "table",
  truncate: TruncateOption = False,
) -> None:
  """List backlog risks with optional filtering.

  Shortcut for: list backlog --kind risk
  """
  list_backlog(
    root=root,
    kind="risk",
    status=status,
    substring=substring,
    regexp=regexp,
    case_insensitive=case_insensitive,
    format_type=format_type,
    truncate=truncate,
  )


# For direct testing
if __name__ == "__main__":  # pragma: no cover
  app()
