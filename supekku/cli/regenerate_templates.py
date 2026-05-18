"""`spec-driver admin regenerate-templates` — rewrite template frontmatter.

Walks `supekku/templates/*.md`, calling
`spec_driver.orchestration.templates.regenerate_template` per kind. Bodies
preserved verbatim; only the frontmatter region is rewritten.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from spec_driver.orchestration.templates import (
  TEMPLATE_PLACEHOLDERS,
  regenerate_template,
  validate_templates,
)
from supekku.scripts.lib.core.repo import find_repo_root

app = typer.Typer(help="Regenerate template frontmatter from metadata")


_TEMPLATE_FILES: dict[str, str] = {
  "adr": "ADR.md",
  "audit": "audit.md",
  "delta": "delta.md",
  "design_revision": "design_revision.md",
  "phase": "phase.md",
  "plan": "plan.md",
  "policy": "policy-template.md",
  "revision": "revision.md",
  "spec": "spec.md",
  "standard": "standard-template.md",
}


@app.callback(invoke_without_command=True)
def regenerate(
  kind: Annotated[
    str | None,
    typer.Argument(
      help="Optional kind filter (delta, spec, phase, ...); default: all kinds",
    ),
  ] = None,
  dry_run: Annotated[
    bool,
    typer.Option("--dry-run/--apply", help="Report drift without writing"),
  ] = False,
) -> None:
  """Regenerate template frontmatter for every (or one) kind."""
  repo = Path(find_repo_root())
  templates_dir = repo / "supekku" / "templates"
  if not templates_dir.is_dir():
    typer.echo(f"templates directory not found: {templates_dir}", err=True)
    raise typer.Exit(code=1)

  if kind is not None and kind not in TEMPLATE_PLACEHOLDERS:
    typer.echo(f"unknown kind: {kind!r}", err=True)
    raise typer.Exit(code=2)

  targets = (kind,) if kind is not None else tuple(_TEMPLATE_FILES.keys())

  if dry_run:
    drifts = validate_templates(repo, kinds=targets)
    if not drifts:
      typer.echo("templates clean")
      return
    for drift in drifts:
      typer.echo(f"would regenerate {drift.path} (kind={drift.kind})")
    raise typer.Exit(code=1)

  changed: list[Path] = []
  for k in targets:
    fname = _TEMPLATE_FILES.get(k)
    if fname is None:
      continue
    path = templates_dir / fname
    if not path.exists():
      continue
    if regenerate_template(k, path):
      changed.append(path)
  if changed:
    for path in changed:
      typer.echo(f"regenerated {path}")
  else:
    typer.echo("templates already canonical")
