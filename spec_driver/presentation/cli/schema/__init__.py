"""``spec-driver schema`` Typer group (IP-137-P03 / DR-137 §5.3).

New top-level group carrying read-only schema-introspection
subcommands. Coexists with the existing ``show schema`` and ``list
schema`` surfaces (which live inside other groups).
"""

from __future__ import annotations

import typer

app = typer.Typer(
  name="schema",
  help="Inspect frontmatter metadata schemas (enums, aliases, fields).",
  no_args_is_help=True,
)

from spec_driver.presentation.cli.schema import (  # noqa: E402  pylint: disable=wrong-import-position
  enums,
)

__all__ = ["app", "enums"]
