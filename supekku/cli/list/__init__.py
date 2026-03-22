"""List commands for specs, deltas, and changes.

Thin CLI layer: parse args → load registry → filter → format → output
Display formatting is delegated to supekku.scripts.lib.formatters
"""

from __future__ import annotations

import typer

from supekku.scripts.lib.core.relation_types import RELATION_TYPES

app = typer.Typer(help="List artifacts", no_args_is_help=True)


def _parse_relation_filter(value: str) -> tuple[str, str]:
  """Parse ``TYPE:TARGET`` from ``--relation`` flag.

  Splits on the first colon. Raises :class:`typer.BadParameter` if no colon
  is present. Emits a warning on stderr for unrecognised relation types.
  """
  if ":" not in value:
    msg = f"--relation requires TYPE:TARGET (got '{value}')"
    raise typer.BadParameter(msg)
  rel_type, target = value.split(":", 1)
  rel_type = rel_type.strip()
  target = target.strip()
  if not rel_type or not target:
    msg = f"--relation requires non-empty TYPE and TARGET (got '{value}')"
    raise typer.BadParameter(msg)
  if rel_type not in RELATION_TYPES:
    import sys

    print(f"Warning: unknown relation type '{rel_type}'", file=sys.stderr)
  return rel_type, target


# Import sub-modules to trigger @app.command() registration.
# Each sub-module imports `app` from this package and registers commands on it.
from supekku.cli.list import backlog as _backlog  # noqa: E402, F401
from supekku.cli.list import backlog_items as _backlog_items  # noqa: E402, F401
from supekku.cli.list import changes as _changes  # noqa: E402, F401
from supekku.cli.list import deltas as _deltas  # noqa: E402, F401
from supekku.cli.list import governance as _governance  # noqa: E402, F401
from supekku.cli.list import misc as _misc  # noqa: E402, F401
from supekku.cli.list import requirements as _requirements  # noqa: E402, F401
from supekku.cli.list import reviews as _reviews  # noqa: E402, F401
from supekku.cli.list import specs as _specs  # noqa: E402, F401

# ---------------------------------------------------------------------------
# Singular command aliases (PROD-010 FR-016: forgiving input parsing)
# ---------------------------------------------------------------------------
_PLURAL_TO_SINGULAR = {
  "specs": "spec",
  "deltas": "delta",
  "changes": "change",
  "adrs": "adr",
  "policies": "policy",
  "standards": "standard",
  "requirements": "requirement",
  "revisions": "revision",
  "audits": "audit",
  "issues": "issue",
  "problems": "problem",
  "improvements": "improvement",
  "risks": "risk",
  "cards": "card",
  "memories": "memory",
  "plans": "plan",
}

# Collect registered command functions by name, then register singular aliases
_registered = {cmd.name: cmd for cmd in app.registered_commands}
for _plural, _singular in _PLURAL_TO_SINGULAR.items():
  _cmd_info = _registered.get(_plural)
  if _cmd_info and _cmd_info.callback:
    app.command(_singular, hidden=True)(_cmd_info.callback)

# schemas singular alias
_schema_cmd = _registered.get("schemas")
if _schema_cmd and _schema_cmd.callback:
  app.command("schema", hidden=True)(_schema_cmd.callback)
