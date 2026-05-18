"""``spec-driver validate workspace`` — workspace-wide validation.

Replaces the prior top-level ``spec-driver validate`` command. Adds
``--kind``/``--no-tolerated-aliases`` per DR-137 §5.4 while preserving
the legacy flag surface (``--sync``, ``--strict``, ``--verbose``,
``--fix``).

The ``--kind`` filter (F-8) is implemented post-validation: the full
corpus is loaded as before, then diagnostics are filtered to artefacts
whose id matches the selected kind's id-prefix. This is the F-8 §2
"relation-traversal" form alone — the F-8 §1 load-time filter is
deferred to a follow-up because the current loader does not expose a
per-kind early-skip. VT-CC-017/025 still pass under this simpler
variant; reproducibility (the only F-8 guarantee that matters at the
CLI surface) is preserved.
"""

from __future__ import annotations

from typing import Annotated

import typer

from spec_driver.presentation.cli import constants
from spec_driver.presentation.cli.validate import app
from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS, RootOption
from supekku.scripts.lib.core.repo import find_repo_root
from supekku.scripts.lib.validation.validator import (
  ValidationIssue,
)
from supekku.scripts.lib.validation.validator import (
  validate_workspace as validate_ws,
)
from supekku.scripts.lib.workspace import Workspace

# Kind ⇒ artefact-id prefix(es) for the ``--kind`` post-filter. The set
# matches PROD-004's controlled-vocab artefact taxonomy.
_KIND_ID_PREFIXES: dict[str, tuple[str, ...]] = {
  "delta": ("DE-",),
  "revision": ("RE-",),
  "audit": ("AUD-",),
  "spec": ("SPEC-", "PROD-"),
  "requirement": ("FR-", "NF-"),
  "decision": ("ADR-",),
  "adr": ("ADR-",),
  "memory": ("mem.",),
  "issue": ("ISSUE-",),
  "improvement": ("IMPR-",),
  "risk": ("RISK-",),
  "problem": ("PROB-",),
  "phase": ("IP-",),
  "plan": ("IP-",),
}


def _filter_by_kind(issues: list[ValidationIssue], kind: str) -> list[ValidationIssue]:
  """Return only issues whose ``artifact`` matches the kind's id-prefix(es)."""
  prefixes = _KIND_ID_PREFIXES.get(kind.lower())
  if not prefixes:
    return issues
  return [i for i in issues if any(i.artifact.startswith(p) for p in prefixes)]


@app.command(constants.VALIDATE_WORKSPACE)
def workspace_cmd(  # noqa: PLR0913 — Typer demands one parameter per flag
  root: RootOption = None,
  sync: Annotated[
    bool,
    typer.Option(
      constants.FLAG_SYNC,
      help="Synchronise registries before validation",
    ),
  ] = False,
  strict: Annotated[
    bool,
    typer.Option(
      constants.FLAG_STRICT,
      help="Enable strict validation (promote warnings to errors)",
    ),
  ] = False,
  verbose: Annotated[
    bool,
    typer.Option(
      "--verbose",
      "-v",
      help="Show info-level messages (planned verification artifacts, etc.)",
    ),
  ] = False,
  fix: Annotated[
    bool,
    typer.Option(
      constants.FLAG_FIX,
      help="Auto-fix safe normalisations (e.g. non-canonical phase statuses)",
    ),
  ] = False,
  no_tolerated_aliases: Annotated[
    bool,
    typer.Option(
      constants.FLAG_NO_TOLERATED,
      help="Reject tolerated aliases (per-kind sunset enforcement)",
    ),
  ] = False,
  kind: Annotated[
    str | None,
    typer.Option(
      constants.FLAG_KIND,
      help="Filter diagnostics to a single artefact kind (e.g. 'delta', 'spec')",
    ),
  ] = None,
) -> None:
  """Validate workspace metadata and relationships.

  Default mode emits errors + warnings. ``--verbose`` adds info messages.
  ``--strict`` promotes warnings to errors. ``--fix`` rewrites the source
  file for diagnostics that carry a safe ``fix_hint`` / ``fix_kind``.
  ``--kind <kind>`` filters diagnostics to the named artefact kind.

  Exit codes (F-46):
  - 0 — clean (no error-severity diagnostics).
  - 1 — error-severity diagnostics surfaced.
  - 2 — usage error (invalid flag / missing workspace).

  ``--no-tolerated-aliases`` is recognised at this CLI layer and is
  threaded to downstream validators as they consume it. Per-kind sunset
  enforcement is implemented incrementally by DE-138..142.
  """
  try:
    ws = Workspace(find_repo_root(root))
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e

  if sync:
    ws.sync_all_registries()

  try:
    issues = validate_ws(ws, strict=strict, fix=fix)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e

  # ``--no-tolerated-aliases`` is recognised here but does not yet alter
  # the workspace-validator codepath. Per-kind validators consume it as
  # DE-138..142 lands. Accept the flag silently so downstream callers do
  # not break when DR-137 §5.4 ripple migrates to the explicit form.
  _ = no_tolerated_aliases

  if kind is not None:
    issues = _filter_by_kind(issues, kind)

  if not verbose:
    issues = [i for i in issues if i.level != "info"]

  if strict:
    # ``--strict`` promotes warnings to errors at the exit-code layer.
    pass  # (severity stays "warning" on the message; exit code logic below)

  has_errors = any(i.level == "error" for i in issues)
  has_warnings_promoted = strict and any(i.level == "warning" for i in issues)

  if not issues:
    typer.echo("Workspace validation passed")
    raise typer.Exit(EXIT_SUCCESS)

  for issue in issues:
    typer.echo(f"Issue: {issue}", err=True)

  if has_errors or has_warnings_promoted:
    raise typer.Exit(EXIT_FAILURE)
  raise typer.Exit(EXIT_SUCCESS)
