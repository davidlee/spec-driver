"""Enum registry for CLI introspection.

Maps dotted enum paths (e.g. 'delta.status') to sorted lists of valid
values. Sources are lifecycle constants where they exist; hardcoded
values where no constant is defined.
"""

from __future__ import annotations

from collections.abc import Callable

from supekku.scripts.lib.blocks.verification import (
  VALID_KINDS as VERIFICATION_KINDS,
)
from supekku.scripts.lib.blocks.verification import (
  VALID_STATUSES as VERIFICATION_STATUSES,
)
from supekku.scripts.lib.changes.lifecycle import (
  VALID_STATUSES as CHANGE_STATUSES,
)
from supekku.scripts.lib.requirements.lifecycle import (
  VALID_STATUSES as REQUIREMENT_STATUSES,
)

ENUM_REGISTRY: dict[str, Callable[[], list[str]]] = {
  # From lifecycle constants
  "delta.status": lambda: sorted(s for s in CHANGE_STATUSES if s != "complete"),
  "requirement.status": lambda: sorted(REQUIREMENT_STATUSES),
  "verification.kind": lambda: sorted(VERIFICATION_KINDS),
  "verification.status": lambda: sorted(VERIFICATION_STATUSES),
  # No lifecycle constants — stable conventions
  "command.format": lambda: ["json", "table", "tsv"],
  "requirement.kind": lambda: ["FR", "NF"],
  "spec.kind": lambda: ["prod", "tech"],
}


def get_enum_values(path: str) -> list[str] | None:
  """Return sorted enum values for a dotted path, or None if unknown."""
  provider = ENUM_REGISTRY.get(path)
  return provider() if provider else None


def list_enum_paths() -> list[str]:
  """Return all registered enum paths, sorted."""
  return sorted(ENUM_REGISTRY)


__all__ = [
  "ENUM_REGISTRY",
  "get_enum_values",
  "list_enum_paths",
]
