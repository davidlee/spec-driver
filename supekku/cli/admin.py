"""Admin command group for niche workspace maintenance operations."""

from __future__ import annotations

import typer

from supekku.cli import backfill, compact, resolve

app = typer.Typer(help="Workspace maintenance commands", no_args_is_help=True)

app.add_typer(compact.app, name="compact", help="Compact artifact frontmatter")
app.add_typer(resolve.app, name="resolve", help="Resolve cross-artifact references")
app.add_typer(backfill.app, name="backfill", help="Backfill incomplete artifacts")
