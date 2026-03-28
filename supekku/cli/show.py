"""Show commands for displaying detailed information about artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any

import typer

from supekku.cli.common import (
  ARTIFACT_PREFIXES,
  EXIT_FAILURE,
  EXIT_SUCCESS,
  ArtifactNotFoundError,
  ArtifactRef,
  ContentTypeOption,
  InferringGroup,
  RootOption,
  emit_artifact,
  load_all_artifacts,
  resolve_artifact,
  resolve_by_id,
  resolve_root,
)
from supekku.scripts.lib.cards import CardRegistry
from supekku.scripts.lib.core.repo import find_repo_root
from supekku.scripts.lib.core.templates import TemplateNotFoundError, render_template
from supekku.scripts.lib.formatters.card_formatters import format_card_details
from supekku.scripts.lib.formatters.change_formatters import (
  format_audit_details,
  format_delta_details,
  format_delta_details_json,
  format_plan_details,
  format_revision_details,
)
from supekku.scripts.lib.formatters.decision_formatters import format_decision_details
from supekku.scripts.lib.formatters.memory_formatters import format_memory_details
from supekku.scripts.lib.formatters.policy_formatters import format_policy_details
from supekku.scripts.lib.formatters.relation_formatters import format_related_section
from supekku.scripts.lib.formatters.requirement_formatters import (
  format_requirement_details,
)
from supekku.scripts.lib.formatters.spec_formatters import format_spec_details
from supekku.scripts.lib.formatters.standard_formatters import format_standard_details
from supekku.scripts.lib.memory.registry import MemoryRegistry

# Reverse mapping: ID prefix → artifact kind for forward reference grouping.
_PREFIX_TO_KIND: dict[str, str] = {v: k for k, v in ARTIFACT_PREFIXES.items()}
# Spec prefixes are not in ARTIFACT_PREFIXES — add common ones.
_PREFIX_TO_KIND.update(
  {
    "SPEC-": "spec",
    "PROD-": "spec",
  }
)

# Per-kind reverse lookup registries (DEC-090-15).
_RELATED_REGISTRIES: dict[str, tuple[str, ...]] = {
  "spec": ("delta", "revision", "audit", "adr", "requirement", "policy", "standard"),
  "delta": ("audit", "revision", "backlog"),
  "requirement": ("delta", "adr", "policy", "standard"),
  "issue": ("delta",),
}


def _infer_kind_from_id(target_id: str) -> str:
  """Infer artifact kind from a target ID prefix.

  Falls back to ``"unknown"`` if no prefix matches.
  """
  upper = target_id.upper()
  for prefix, kind in _PREFIX_TO_KIND.items():
    if upper.startswith(prefix):
      return kind
  return "unknown"


def _gather_reverse_refs(
  repo_root: Path,
  entity_id: str,
  entity_kind: str,
) -> dict[str, list[tuple[str, str]]]:
  """Gather reverse references grouped by kind for ``--related``.

  Loads only registries relevant to *entity_kind* per DEC-090-15.

  Returns:
    Dict mapping kind → [(id, name), ...] for each referencing artifact.
  """
  from supekku.scripts.lib.relations.query import find_related_to  # noqa: PLC0415

  registry_kinds = _RELATED_REGISTRIES.get(entity_kind, ())
  result: dict[str, list[tuple[str, str]]] = {}
  for kind in registry_kinds:
    try:
      artifacts = load_all_artifacts(repo_root, kind)
      related = find_related_to(artifacts, entity_id)
      if related:
        result[kind] = [
          (
            getattr(a, "id", getattr(a, "uid", "?")),
            getattr(a, "name", getattr(a, "title", "")),
          )
          for a in related
        ]
    except (FileNotFoundError, ValueError):
      continue  # Registry not available — skip silently
  return result


def _gather_forward_refs(
  artifact: Any,
) -> list[dict[str, str]]:
  """Gather forward references from *artifact* for ``--related`` JSON."""
  from supekku.scripts.lib.relations.query import collect_references  # noqa: PLC0415

  return [
    {"type": hit.detail or "", "target": hit.target, "source": hit.source}
    for hit in collect_references(artifact)
  ]


app = typer.Typer(
  help="Show detailed artifact information",
  no_args_is_help=True,
  cls=InferringGroup,
)


@app.command("spec")
def show_spec(  # noqa: PLR0913
  spec_id: Annotated[str, typer.Argument(help="Spec ID (e.g., SPEC-009, PROD-042)")],
  json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
  path_only: Annotated[bool, typer.Option("--path", help="Output path only")] = False,
  raw_output: Annotated[
    bool, typer.Option("--raw", help="Output raw file content")
  ] = False,
  requirements: Annotated[
    bool, typer.Option("--requirements", help="Show full requirements list")
  ] = False,
  related: Annotated[
    bool, typer.Option("--related", help="Show forward and reverse references")
  ] = False,
  content_type: ContentTypeOption = None,
  root: RootOption = None,
) -> None:
  """Show detailed information about a specification."""
  try:
    ref = resolve_artifact("spec", spec_id, root)
    repo_root = find_repo_root(root)

    # Count requirements for this spec
    fr_count = nf_count = other_req_count = 0
    requirements_list: list[tuple[str, str, str]] | None = None
    try:
      from supekku.scripts.lib.requirements.registry import (
        RequirementsRegistry,  # noqa: PLC0415
      )

      req_registry = RequirementsRegistry(root=repo_root)
      if requirements:
        requirements_list = []
      for rec in req_registry.iter():
        if ref.id in rec.specs:
          if rec.kind == "functional":
            fr_count += 1
            label = "FR"
          elif rec.kind in ("non_functional", "non-functional"):
            nf_count += 1
            label = "NF"
          else:
            other_req_count += 1
            label = rec.kind
          if requirements_list is not None:
            requirements_list.append((rec.uid, label, rec.title))
    except (FileNotFoundError, ValueError):
      pass  # No requirements registry — counts stay at zero

    # Reverse lookup: counts for default view, full neighbourhood for --related
    delta_count = revision_count = audit_count = 0
    reverse_refs: dict[str, list[tuple[str, str]]] = {}
    if related:
      reverse_refs = _gather_reverse_refs(repo_root, ref.id, "spec")
      delta_count = len(reverse_refs.get("delta", []))
      revision_count = len(reverse_refs.get("revision", []))
      audit_count = len(reverse_refs.get("audit", []))
    else:
      try:
        from supekku.scripts.lib.changes.registry import ChangeRegistry  # noqa: PLC0415
        from supekku.scripts.lib.relations.query import find_related_to  # noqa: PLC0415

        for kind in ("delta", "revision", "audit"):
          change_reg = ChangeRegistry(root=repo_root, kind=kind)
          related_arts = find_related_to(change_reg.iter(), ref.id)
          if kind == "delta":
            delta_count = len(related_arts)
          elif kind == "revision":
            revision_count = len(related_arts)
          else:
            audit_count = len(related_arts)
      except (FileNotFoundError, ValueError):
        pass  # No change registry — counts stay at zero

    total_req_count = fr_count + nf_count + other_req_count

    def _format(r):  # type: ignore[no-untyped-def]
      base = format_spec_details(
        r,
        root=root,
        fr_count=fr_count,
        nf_count=nf_count,
        other_req_count=other_req_count,
        delta_count=0 if related else delta_count,
        revision_count=0 if related else revision_count,
        audit_count=0 if related else audit_count,
        requirements_list=requirements_list,
        registry_empty_hint=total_req_count == 0,
      )
      if related:
        related_lines = format_related_section(reverse_refs)
        return base + "\n".join(related_lines)
      return base

    def _json(r):  # type: ignore[no-untyped-def]
      data = r.to_dict(repo_root)
      if not related and (delta_count or revision_count or audit_count):
        data["reverse_lookup_counts"] = {
          "deltas": delta_count,
          "revisions": revision_count,
          "audits": audit_count,
        }
      if requirements_list is not None:
        data["requirements"] = [
          {"id": rid, "kind": kind, "title": title}
          for rid, kind, title in requirements_list
        ]
      if related:
        data["related"] = {
          "forward": _gather_forward_refs(ref.record),
          "referenced_by": {
            kind: [{"id": aid, "name": aname} for aid, aname in refs]
            for kind, refs in reverse_refs.items()
          },
        }
      return json.dumps(data, indent=2)

    emit_artifact(
      ref,
      json_output=json_output,
      path_only=path_only,
      raw_output=raw_output,
      content_type=content_type,
      format_fn=_format,
      json_fn=_json,
    )
  except ArtifactNotFoundError as e:
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
  related: Annotated[
    bool, typer.Option("--related", help="Show forward and reverse references")
  ] = False,
  content_type: ContentTypeOption = None,
  root: RootOption = None,
) -> None:
  """Show detailed information about a delta."""
  try:
    ref = resolve_artifact("delta", delta_id, root)
    repo_root = find_repo_root(root)

    # Reverse lookups: audits and revisions referencing this delta
    linked_audits: list[tuple[str, str]] = []
    linked_revisions: list[tuple[str, str]] = []
    reverse_refs: dict[str, list[tuple[str, str]]] = {}
    if related:
      reverse_refs = _gather_reverse_refs(repo_root, ref.id, "delta")
      linked_audits = reverse_refs.get("audit", [])
      linked_revisions = reverse_refs.get("revision", [])
    else:
      try:
        from supekku.scripts.lib.changes.registry import ChangeRegistry  # noqa: PLC0415
        from supekku.scripts.lib.relations.query import find_related_to  # noqa: PLC0415

        for kind, dest in (("audit", linked_audits), ("revision", linked_revisions)):
          change_reg = ChangeRegistry(root=repo_root, kind=kind)
          for artifact in find_related_to(change_reg.iter(), ref.id):
            dest.append((artifact.id, artifact.name))
      except (FileNotFoundError, ValueError):
        pass

    def _format(r):  # type: ignore[no-untyped-def]
      base = format_delta_details(
        r,
        root=root,
        linked_audits=linked_audits,
        linked_revisions=linked_revisions,
      )
      if related:
        # Append full neighbourhood (excluding audit/revision already shown)
        skip = ("audit", "revision")
        extra_refs = {k: v for k, v in reverse_refs.items() if k not in skip}
        if extra_refs:
          related_lines = format_related_section(extra_refs)
          return base + "\n".join(related_lines)
      return base

    def _json(r):  # type: ignore[no-untyped-def]
      data = format_delta_details_json(r, root=root)
      # format_delta_details_json returns a JSON string; parse, enrich, re-encode
      import json as _json_mod  # noqa: PLC0415

      parsed = _json_mod.loads(data)
      if linked_audits:
        parsed["linked_audits"] = [
          {"id": aid, "name": aname} for aid, aname in linked_audits
        ]
      if linked_revisions:
        parsed["linked_revisions"] = [
          {"id": rid, "name": rname} for rid, rname in linked_revisions
        ]
      if related:
        parsed["related"] = {
          "forward": _gather_forward_refs(ref.record),
          "referenced_by": {
            kind: [{"id": aid, "name": aname} for aid, aname in refs]
            for kind, refs in reverse_refs.items()
          },
        }
      return _json_mod.dumps(parsed, indent=2)

    emit_artifact(
      ref,
      json_output=json_output,
      path_only=path_only,
      raw_output=raw_output,
      content_type=content_type,
      format_fn=_format,
      json_fn=_json,
    )
  except ArtifactNotFoundError as e:
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
  content_type: ContentTypeOption = None,
  root: RootOption = None,
) -> None:
  """Show detailed information about a revision."""
  try:
    ref = resolve_artifact("revision", revision_id, root)
    emit_artifact(
      ref,
      json_output=json_output,
      path_only=path_only,
      raw_output=raw_output,
      content_type=content_type,
      format_fn=lambda r: format_revision_details(r, root=root),
      json_fn=lambda r: json.dumps(r.to_dict(root), indent=2),
    )
  except ArtifactNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("requirement")
def show_requirement(  # noqa: PLR0913
  req_id: Annotated[str, typer.Argument(help="Requirement ID (e.g., SPEC-009.FR-001)")],
  json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
  path_only: Annotated[bool, typer.Option("--path", help="Output path only")] = False,
  raw_output: Annotated[
    bool, typer.Option("--raw", help="Output raw file content")
  ] = False,
  related: Annotated[
    bool, typer.Option("--related", help="Show forward and reverse references")
  ] = False,
  content_type: ContentTypeOption = None,
  root: RootOption = None,
) -> None:
  """Show detailed information about a requirement."""
  try:
    ref = resolve_artifact("requirement", req_id, root)
    repo_root = find_repo_root(root)

    reverse_refs: dict[str, list[tuple[str, str]]] = {}
    if related:
      reverse_refs = _gather_reverse_refs(repo_root, ref.id, "requirement")

    def _format(r):  # type: ignore[no-untyped-def]
      base = format_requirement_details(r)
      if related:
        related_lines = format_related_section(reverse_refs)
        return base + "\n".join(related_lines)
      return base

    def _json(r):  # type: ignore[no-untyped-def]
      data = r.to_dict()
      if related:
        data["related"] = {
          "forward": _gather_forward_refs(ref.record),
          "referenced_by": {
            kind: [{"id": aid, "name": aname} for aid, aname in refs]
            for kind, refs in reverse_refs.items()
          },
        }
      return json.dumps(data, indent=2)

    emit_artifact(
      ref,
      json_output=json_output,
      path_only=path_only,
      raw_output=raw_output,
      content_type=content_type,
      format_fn=_format,
      json_fn=_json,
    )
  except ArtifactNotFoundError as e:
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
  content_type: ContentTypeOption = None,
  root: RootOption = None,
) -> None:
  """Show detailed information about a specific decision/ADR."""
  try:
    ref = resolve_artifact("adr", decision_id, root)
    repo_root = find_repo_root(root)
    emit_artifact(
      ref,
      json_output=json_output,
      path_only=path_only,
      raw_output=raw_output,
      content_type=content_type,
      format_fn=format_decision_details,
      json_fn=lambda r: json.dumps(r.to_dict(repo_root), indent=2),
    )
  except ArtifactNotFoundError as e:
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
  content_type: ContentTypeOption = None,
  root: RootOption = None,
) -> None:
  """Show detailed information about a specific policy."""
  try:
    ref = resolve_artifact("policy", policy_id, root)
    repo_root = find_repo_root(root)
    emit_artifact(
      ref,
      json_output=json_output,
      path_only=path_only,
      raw_output=raw_output,
      content_type=content_type,
      format_fn=format_policy_details,
      json_fn=lambda r: json.dumps(r.to_dict(repo_root), indent=2),
    )
  except ArtifactNotFoundError as e:
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
  content_type: ContentTypeOption = None,
  root: RootOption = None,
) -> None:
  """Show detailed information about a specific standard."""
  try:
    ref = resolve_artifact("standard", standard_id, root)
    repo_root = find_repo_root(root)
    emit_artifact(
      ref,
      json_output=json_output,
      path_only=path_only,
      raw_output=raw_output,
      content_type=content_type,
      format_fn=format_standard_details,
      json_fn=lambda r: json.dumps(r.to_dict(repo_root), indent=2),
    )
  except ArtifactNotFoundError as e:
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
  content_type: ContentTypeOption = None,
  root: RootOption = None,
) -> None:
  """Show detailed information about a specific card."""
  try:
    registry = CardRegistry(root=resolve_root(root))
    card = registry.resolve_card(card_id, anywhere=anywhere)
    ref = ArtifactRef(id=card_id, path=card.path, record=card)
    emit_artifact(
      ref,
      json_output=json_output,
      path_only=path_only,
      raw_output=raw_output,
      content_type=content_type,
      format_fn=format_card_details,
      json_fn=lambda r: json.dumps(r.to_dict(), indent=2),
    )
  except ArtifactNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except (FileNotFoundError, ValueError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("memory")
def show_memory(  # noqa: PLR0913
  memory_id: Annotated[
    str,
    typer.Argument(
      help="Memory ID (e.g., mem.pattern.cli.skinny or pattern.cli.skinny)",
    ),
  ],
  json_output: Annotated[
    bool,
    typer.Option("--json", help="Output as JSON"),
  ] = False,
  path_only: Annotated[
    bool,
    typer.Option("--path", help="Output path only"),
  ] = False,
  raw_output: Annotated[
    bool,
    typer.Option("--raw", help="Output raw file content"),
  ] = False,
  body_only: Annotated[
    bool,
    typer.Option(
      "--body-only",
      "-b",
      help="Output body text only (no frontmatter)",
    ),
  ] = False,
  links_depth: Annotated[
    int | None,
    typer.Option(
      "--links-depth",
      help="Expand outgoing link graph to N levels",
    ),
  ] = None,
  tree: Annotated[
    bool,
    typer.Option("--tree", help="Show link graph as indented tree"),
  ] = False,
  content_type: ContentTypeOption = None,
  root: RootOption = None,
) -> None:
  """Show detailed information about a specific memory record."""
  try:
    from supekku.scripts.lib.memory.ids import normalize_memory_id  # noqa: PLC0415

    normalized_id = normalize_memory_id(memory_id)
    registry = MemoryRegistry(root=root)
    record = registry.find(normalized_id)

    if not record:
      typer.echo(
        f"Error: Memory not found: {normalized_id}",
        err=True,
      )
      raise typer.Exit(EXIT_FAILURE)

    # Graph expansion mode
    if links_depth is not None:
      from supekku.scripts.lib.formatters.memory_formatters import (  # noqa: PLC0415
        format_link_graph_json,
        format_link_graph_table,
        format_link_graph_tree,
      )
      from supekku.scripts.lib.memory.links import expand_link_graph  # noqa: PLC0415

      all_records = registry.collect()
      bodies = registry.collect_bodies()
      names = {mid: r.name for mid, r in all_records.items()}
      types = {mid: r.memory_type for mid, r in all_records.items()}
      nodes = expand_link_graph(
        normalized_id,
        bodies,
        names,
        types,
        max_depth=links_depth,
      )
      if json_output:
        typer.echo(format_link_graph_json(nodes))
      elif tree:
        typer.echo(format_link_graph_tree(nodes))
      else:
        typer.echo(format_link_graph_table(nodes))
      raise typer.Exit(EXIT_SUCCESS)

    repo_root = find_repo_root(root)
    ref = ArtifactRef(
      id=record.id,
      path=Path(record.path),
      record=record,
    )
    emit_artifact(
      ref,
      json_output=json_output,
      path_only=path_only,
      raw_output=raw_output,
      body_only=body_only,
      content_type=content_type,
      format_fn=format_memory_details,
      json_fn=lambda r: json.dumps(r.to_dict(repo_root), indent=2),
    )
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("plan")
def show_plan(
  plan_id: Annotated[str, typer.Argument(help="Plan ID (e.g., IP-041, 041)")],
  json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
  path_only: Annotated[bool, typer.Option("--path", help="Output path only")] = False,
  raw_output: Annotated[
    bool, typer.Option("--raw", help="Output raw file content")
  ] = False,
  content_type: ContentTypeOption = None,
  root: RootOption = None,
) -> None:
  """Show detailed information about an implementation plan."""
  try:
    ref = resolve_artifact("plan", plan_id, root)
    emit_artifact(
      ref,
      json_output=json_output,
      path_only=path_only,
      raw_output=raw_output,
      content_type=content_type,
      format_fn=lambda r: format_plan_details(r, root=root, path=ref.path),
      json_fn=lambda r: json.dumps(r, indent=2),
    )
  except ArtifactNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("audit")
def show_audit(
  audit_id: Annotated[str, typer.Argument(help="Audit ID (e.g., AUD-001, 001)")],
  json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
  path_only: Annotated[bool, typer.Option("--path", help="Output path only")] = False,
  raw_output: Annotated[
    bool, typer.Option("--raw", help="Output raw file content")
  ] = False,
  content_type: ContentTypeOption = None,
  root: RootOption = None,
) -> None:
  """Show detailed information about an audit."""
  try:
    ref = resolve_artifact("audit", audit_id, root)
    emit_artifact(
      ref,
      json_output=json_output,
      path_only=path_only,
      raw_output=raw_output,
      content_type=content_type,
      format_fn=lambda r: format_audit_details(r, root=root),
      json_fn=lambda r: json.dumps(r.to_dict(root), indent=2),
    )
  except ArtifactNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("drift")
def show_drift(
  ledger_id: Annotated[str, typer.Argument(help="Drift ledger ID (e.g., DL-047)")],
  json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
  path_only: Annotated[bool, typer.Option("--path", help="Output path only")] = False,
  raw_output: Annotated[
    bool, typer.Option("--raw", help="Output raw file content")
  ] = False,
  content_type: ContentTypeOption = None,
  root: RootOption = None,
) -> None:
  """Show detailed information about a drift ledger."""
  try:
    ref = resolve_artifact("drift_ledger", ledger_id, root)
    from supekku.scripts.lib.formatters.drift_formatters import (  # noqa: PLC0415
      format_drift_details,
      format_drift_details_json,
    )

    emit_artifact(
      ref,
      json_output=json_output,
      path_only=path_only,
      raw_output=raw_output,
      content_type=content_type,
      format_fn=format_drift_details,
      json_fn=format_drift_details_json,
    )
  except ArtifactNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("issue")
def show_issue(  # noqa: PLR0913
  issue_id: Annotated[str, typer.Argument(help="Issue ID (e.g., ISSUE-001)")],
  json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
  path_only: Annotated[bool, typer.Option("--path", help="Output path only")] = False,
  raw_output: Annotated[
    bool, typer.Option("--raw", help="Output raw file content")
  ] = False,
  related: Annotated[
    bool, typer.Option("--related", help="Show forward and reverse references")
  ] = False,
  content_type: ContentTypeOption = None,
  root: RootOption = None,
) -> None:
  """Show detailed information about an issue."""
  try:
    ref = resolve_artifact("issue", issue_id, root)
    repo_root = find_repo_root(root)

    reverse_refs: dict[str, list[tuple[str, str]]] = {}
    if related:
      reverse_refs = _gather_reverse_refs(repo_root, ref.id, "issue")

    def _format(r):  # type: ignore[no-untyped-def]
      base = f"Issue: {r.id}\nName: {r.title}\nStatus: {r.status}\nKind: {r.kind}"
      if related:
        related_lines = format_related_section(reverse_refs)
        return base + "\n".join(related_lines)
      return base

    def _json(r):  # type: ignore[no-untyped-def]
      data = r.to_dict()
      if related:
        data["related"] = {
          "forward": _gather_forward_refs(ref.record),
          "referenced_by": {
            kind: [{"id": aid, "name": aname} for aid, aname in refs]
            for kind, refs in reverse_refs.items()
          },
        }
      return json.dumps(data, indent=2, default=str)

    emit_artifact(
      ref,
      json_output=json_output,
      path_only=path_only,
      raw_output=raw_output,
      content_type=content_type,
      format_fn=_format,
      json_fn=_json,
    )
  except ArtifactNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("problem")
def show_problem(
  problem_id: Annotated[str, typer.Argument(help="Problem ID (e.g., PROB-001)")],
  json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
  path_only: Annotated[bool, typer.Option("--path", help="Output path only")] = False,
  raw_output: Annotated[
    bool, typer.Option("--raw", help="Output raw file content")
  ] = False,
  content_type: ContentTypeOption = None,
  root: RootOption = None,
) -> None:
  """Show detailed information about a problem."""
  try:
    ref = resolve_artifact("problem", problem_id, root)
    emit_artifact(
      ref,
      json_output=json_output,
      path_only=path_only,
      raw_output=raw_output,
      content_type=content_type,
      format_fn=lambda r: (
        f"Problem: {r.id}\nName: {r.title}\nStatus: {r.status}\nKind: {r.kind}"
      ),
      json_fn=lambda r: json.dumps(r.to_dict(), indent=2, default=str),
    )
  except ArtifactNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("improvement")
def show_improvement(
  improvement_id: Annotated[
    str, typer.Argument(help="Improvement ID (e.g., IMPR-001)")
  ],
  json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
  path_only: Annotated[bool, typer.Option("--path", help="Output path only")] = False,
  raw_output: Annotated[
    bool, typer.Option("--raw", help="Output raw file content")
  ] = False,
  content_type: ContentTypeOption = None,
  root: RootOption = None,
) -> None:
  """Show detailed information about an improvement."""
  try:
    ref = resolve_artifact("improvement", improvement_id, root)
    emit_artifact(
      ref,
      json_output=json_output,
      path_only=path_only,
      raw_output=raw_output,
      content_type=content_type,
      format_fn=lambda r: (
        f"Improvement: {r.id}\nName: {r.title}\nStatus: {r.status}\nKind: {r.kind}"
      ),
      json_fn=lambda r: json.dumps(r.to_dict(), indent=2, default=str),
    )
  except ArtifactNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("risk")
def show_risk(
  risk_id: Annotated[str, typer.Argument(help="Risk ID (e.g., RISK-001)")],
  json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
  path_only: Annotated[bool, typer.Option("--path", help="Output path only")] = False,
  raw_output: Annotated[
    bool, typer.Option("--raw", help="Output raw file content")
  ] = False,
  content_type: ContentTypeOption = None,
  root: RootOption = None,
) -> None:
  """Show detailed information about a risk."""
  try:
    ref = resolve_artifact("risk", risk_id, root)
    emit_artifact(
      ref,
      json_output=json_output,
      path_only=path_only,
      raw_output=raw_output,
      content_type=content_type,
      format_fn=lambda r: (
        f"Risk: {r.id}\nName: {r.title}\nStatus: {r.status}\nKind: {r.kind}"
      ),
      json_fn=lambda r: json.dumps(r.to_dict(), indent=2, default=str),
    )
  except ArtifactNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("backlog")
def show_backlog(
  item_id: Annotated[str, typer.Argument(help="Backlog item ID (e.g., ISSUE-009)")],
  json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
  path_only: Annotated[bool, typer.Option("--path", help="Output path only")] = False,
  raw_output: Annotated[
    bool, typer.Option("--raw", help="Output raw file content")
  ] = False,
  content_type: ContentTypeOption = None,
  root: RootOption = None,
) -> None:
  """Show a backlog item (issue, problem, improvement, or risk)."""
  try:
    ref = resolve_artifact("backlog", item_id, root)
    emit_artifact(
      ref,
      json_output=json_output,
      path_only=path_only,
      raw_output=raw_output,
      content_type=content_type,
      format_fn=lambda r: (
        f"{r.kind.title()}: {r.id}\nName: {r.title}\nStatus: {r.status}\nKind: {r.kind}"
      ),
      json_fn=lambda r: json.dumps(r.to_dict(), indent=2, default=str),
    )
  except ArtifactNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


# --- ID inference fallback ---


@app.command("schema")
def show_schema_cmd(
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
  """Show schema details for a block type or frontmatter kind."""
  from supekku.cli.schema import show_schema  # noqa: PLC0415

  show_schema(block_type=block_type, format_type=format_type)


@app.command("relations")
def show_relations(
  artifact_id: Annotated[
    str,
    typer.Argument(help="Artifact ID to show relations for (e.g., DE-097, SPEC-001)"),
  ],
  direction: Annotated[
    str,
    typer.Option(
      "--direction",
      "-d",
      help="Query direction: forward, inverse, or both",
    ),
  ] = "both",
  json_output: Annotated[
    bool,
    typer.Option("--json", help="Output as JSON"),
  ] = False,
  root: RootOption = None,
) -> None:
  """Show cross-artifact reference neighbourhood for an artifact.

  Displays all artifacts that this ID references (forward) and/or
  all artifacts that reference this ID (inverse), grouped by type.

  If the ID is not found as a node, still shows any inverse edges
  (other artifacts may reference a non-existent ID). Emits a warning
  if the ID itself is not a known artifact.
  """
  from supekku.scripts.lib.core.artifact_ids import (  # noqa: PLC0415
    normalize_artifact_id,
  )
  from supekku.scripts.lib.relations.graph import (  # noqa: PLC0415
    build_reference_graph,
    query_neighbourhood,
  )
  from supekku.scripts.lib.workspace import Workspace  # noqa: PLC0415

  valid_directions = ("forward", "inverse", "both")
  if direction not in valid_directions:
    typer.echo(
      f"Error: --direction must be one of {valid_directions}",
      err=True,
    )
    raise typer.Exit(EXIT_FAILURE)

  try:
    repo_root = find_repo_root(root)
    workspace = Workspace(root=repo_root)
    graph = build_reference_graph(workspace)

    # Try normalization if ID not in graph
    resolved_id = artifact_id
    if artifact_id not in graph.nodes:
      norm = normalize_artifact_id(artifact_id, frozenset(graph.nodes))
      if norm.canonical:
        resolved_id = norm.canonical
        typer.echo(
          f"Note: '{artifact_id}' resolved to '{resolved_id}'",
          err=True,
        )
      elif direction != "inverse":
        typer.echo(
          f"Warning: '{artifact_id}' is not a known artifact",
          err=True,
        )

    neighbourhood = query_neighbourhood(graph, resolved_id, direction=direction)

    if json_output:
      _show_relations_json(resolved_id, graph, neighbourhood)
    else:
      _show_relations_text(resolved_id, graph, neighbourhood)

  except Exception as exc:  # noqa: BLE001
    typer.echo(f"Error: {exc}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  raise typer.Exit(EXIT_SUCCESS)


def _show_relations_text(
  artifact_id: str,
  graph: Any,
  neighbourhood: dict[str, list[Any]],
) -> None:
  """Format and print relations as text."""
  kind = graph.nodes.get(artifact_id, "unknown")
  typer.echo(f"Relations for {artifact_id} ({kind})")

  forward = neighbourhood.get("forward", [])
  inverse = neighbourhood.get("inverse", [])

  if not forward and not inverse:
    typer.echo("  (no relations found)")
    return

  if forward:
    typer.echo(f"\n  Forward references ({artifact_id} →):")
    for edge in sorted(forward, key=lambda e: (e.detail, e.target)):
      target_kind = graph.nodes.get(edge.target, "?")
      label = edge.detail or edge.source_slot
      typer.echo(f"    {label:<20s} → {edge.target} ({target_kind})")

  if inverse:
    typer.echo(f"\n  Inverse references (→ {artifact_id}):")
    for edge in sorted(inverse, key=lambda e: (e.detail, e.source)):
      source_kind = graph.nodes.get(edge.source, "?")
      label = edge.detail or edge.source_slot
      typer.echo(f"    {edge.source:<20s} ← {label} ({source_kind})")

  if graph.diagnostics:
    typer.echo("\n  Diagnostics:")
    for diag in graph.diagnostics:
      typer.echo(f"    ⚠ {diag}")


def _show_relations_json(
  artifact_id: str,
  graph: Any,
  neighbourhood: dict[str, list[Any]],
) -> None:
  """Format and print relations as JSON."""
  data: dict[str, Any] = {
    "artifact_id": artifact_id,
    "kind": graph.nodes.get(artifact_id, "unknown"),
  }
  for direction_key in ("forward", "inverse"):
    edges = neighbourhood.get(direction_key, [])
    data[direction_key] = [
      {
        "source": e.source,
        "target": e.target,
        "source_slot": e.source_slot,
        "detail": e.detail,
        "target_kind": graph.nodes.get(e.target, "unknown"),
      }
      for e in edges
    ]
  if graph.diagnostics:
    data["diagnostics"] = graph.diagnostics
  typer.echo(json.dumps(data, indent=2))


@app.command("inferred", hidden=True)
def show_inferred(
  ctx: typer.Context,
  json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
  path_only: Annotated[bool, typer.Option("--path", help="Output path only")] = False,
  raw_output: Annotated[
    bool, typer.Option("--raw", help="Output raw file content")
  ] = False,
  root: RootOption = None,
) -> None:
  """Show an artifact by inferring its type from the ID."""
  raw_id = ctx.obj["inferred_id"]
  repo_root = find_repo_root(root)
  matches = resolve_by_id(raw_id, repo_root)

  if not matches:
    typer.echo(f"Error: no artifact found matching '{raw_id}'", err=True)
    raise typer.Exit(EXIT_FAILURE)

  if len(matches) > 1:
    typer.echo(f"Ambiguous ID '{raw_id}' matches:", err=True)
    for kind, ref in matches:
      typer.echo(f"  {ref.id} ({kind})", err=True)
    typer.echo("Specify the type: e.g. 'show delta ...'", err=True)
    raise typer.Exit(EXIT_FAILURE)

  kind, ref = matches[0]

  # For --path and --raw, handle directly (type-agnostic)
  if path_only:
    typer.echo(ref.path)
    raise typer.Exit(EXIT_SUCCESS)
  if raw_output:
    typer.echo(ref.path.read_text())
    raise typer.Exit(EXIT_SUCCESS)

  # For default and --json, dispatch to the type-specific show handler.
  # This reuses the existing per-type formatters without duplication.
  show_handlers: dict[str, Any] = {
    "adr": lambda: show_adr(ref.id, json_output=json_output, root=root),
    "delta": lambda: show_delta(ref.id, json_output=json_output, root=root),
    "revision": lambda: show_revision(ref.id, json_output=json_output, root=root),
    "spec": lambda: show_spec(ref.id, json_output=json_output, root=root),
    "plan": lambda: show_plan(ref.id, json_output=json_output, root=root),
    "audit": lambda: show_audit(ref.id, json_output=json_output, root=root),
    "policy": lambda: show_policy(ref.id, json_output=json_output, root=root),
    "standard": lambda: show_standard(ref.id, json_output=json_output, root=root),
    "memory": lambda: show_memory(ref.id, json_output=json_output, root=root),
    "card": lambda: show_card(ref.id, json_output=json_output, root=root),
    "drift_ledger": lambda: show_drift(ref.id, json_output=json_output, root=root),
    "issue": lambda: show_issue(ref.id, json_output=json_output, root=root),
    "problem": lambda: show_problem(ref.id, json_output=json_output, root=root),
    "improvement": lambda: show_improvement(ref.id, json_output=json_output, root=root),
    "risk": lambda: show_risk(ref.id, json_output=json_output, root=root),
    "requirement": lambda: show_requirement(ref.id, json_output=json_output, root=root),
  }

  handler = show_handlers.get(kind)
  if handler:
    handler()
  else:
    typer.echo(f"Error: unsupported artifact type for show: {kind}", err=True)
    raise typer.Exit(EXIT_FAILURE)


# For direct testing
if __name__ == "__main__":  # pragma: no cover
  app()
