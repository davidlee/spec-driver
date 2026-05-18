"""`spec-driver validate` Typer group (DR-137 §5.4 DEC-137-17).

Bare `spec-driver validate` prints help and exits 2 via Typer's
`no_args_is_help=True`. Named-peer subcommands:

- ``validate workspace`` (workspace-wide validation; renamed from the
  prior bare-form top-level command)
- ``validate file <path>`` (single-file authoring-time validation)
- ``validate templates`` (CI gate, moved from the P02 hyphenated
  ``spec-driver validate-templates`` stopgap)

Uniform exit-code contract (F-46) across all subcommands:

- ``0`` — no error-severity diagnostics surfaced
- ``1`` — at least one error-severity diagnostic surfaced
- ``2`` — usage error (bare invocation, invalid flag, non-existent path)
"""

from __future__ import annotations

import typer

app = typer.Typer(
  name="validate",
  help="Validate workspace artefacts, individual files, or templates.",
  no_args_is_help=True,
)

# Subcommand modules register against the shared ``app`` import. Side-effect
# imports keep the module-level layout discoverable and Typer-idiomatic.
from spec_driver.presentation.cli.validate import (  # noqa: E402  pylint: disable=wrong-import-position
  file,
  templates,
  workspace,
)

__all__ = ["app", "file", "templates", "workspace"]
