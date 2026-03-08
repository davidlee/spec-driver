"""Enum registry for CLI introspection and status validation.

Maps dotted enum paths (e.g. 'delta.status') to sorted lists of valid
values. Sources are lifecycle constants where they exist; hardcoded
values where no constant is defined.
"""

from __future__ import annotations

from collections.abc import Callable

from supekku.scripts.lib.backlog.models import (
  BACKLOG_BASE_STATUSES,
  RISK_STATUSES,
)
from supekku.scripts.lib.blocks.verification import (
  VALID_KINDS as VERIFICATION_KINDS,
)
from supekku.scripts.lib.blocks.verification import (
  VALID_STATUSES as VERIFICATION_STATUSES,
)
from supekku.scripts.lib.changes.lifecycle import (
  VALID_STATUSES as CHANGE_STATUSES,
)
from supekku.scripts.lib.decisions.lifecycle import ADR_STATUSES
from supekku.scripts.lib.drift.models import LEDGER_STATUSES
from supekku.scripts.lib.memory.lifecycle import MEMORY_STATUSES
from supekku.scripts.lib.policies.lifecycle import POLICY_STATUSES
from supekku.scripts.lib.requirements.lifecycle import (
  VALID_STATUSES as REQUIREMENT_STATUSES,
)
from supekku.scripts.lib.specs.lifecycle import SPEC_STATUSES
from supekku.scripts.lib.standards.lifecycle import STANDARD_STATUSES


def _change_statuses() -> list[str]:
  return sorted(s for s in CHANGE_STATUSES if s != "complete")


ENUM_REGISTRY: dict[str, Callable[[], list[str]]] = {
  # From lifecycle constants
  "delta.status": _change_statuses,
  "revision.status": _change_statuses,
  "audit.status": _change_statuses,
  "requirement.status": lambda: sorted(REQUIREMENT_STATUSES),
  "verification.kind": lambda: sorted(VERIFICATION_KINDS),
  "verification.status": lambda: sorted(VERIFICATION_STATUSES),
  # Backlog statuses — unified base with risk extensions (DEC-075-05)
  "backlog.status": lambda: sorted(BACKLOG_BASE_STATUSES),
  "issue.status": lambda: sorted(BACKLOG_BASE_STATUSES),
  "problem.status": lambda: sorted(BACKLOG_BASE_STATUSES),
  "improvement.status": lambda: sorted(BACKLOG_BASE_STATUSES),
  "risk.status": lambda: sorted(RISK_STATUSES),
  # Drift ledger statuses
  "drift.status": lambda: sorted(LEDGER_STATUSES),
  # Governance artifact statuses (DE-075)
  "spec.status": lambda: sorted(SPEC_STATUSES),
  "adr.status": lambda: sorted(ADR_STATUSES),
  "policy.status": lambda: sorted(POLICY_STATUSES),
  "standard.status": lambda: sorted(STANDARD_STATUSES),
  "memory.status": lambda: sorted(MEMORY_STATUSES),
  # No lifecycle constants — stable conventions
  "command.format": lambda: ["json", "table", "tsv"],
  "requirement.kind": lambda: ["FR", "NF"],
  "spec.kind": lambda: ["prod", "tech"],
}


def get_enum_values(path: str) -> list[str] | None:
  """Return sorted enum values for a dotted path, or None if unknown."""
  provider = ENUM_REGISTRY.get(path)
  return provider() if provider else None


def validate_status_for_entity(entity_type: str, status: str) -> None:
  """Validate a status value against the enum for an entity type.

  Raises ``ValueError`` if *status* is empty/whitespace-only or if
  an enum exists for *entity_type* and *status* is not in it.
  Accepts silently when no enum is registered.
  """
  if not status or not status.strip():
    msg = "Status must not be empty"
    raise ValueError(msg)

  valid_values = get_enum_values(f"{entity_type}.status")
  if valid_values is None:
    return

  if status in valid_values:
    return

  msg = (
    f"Invalid status '{status}' for {entity_type}. "
    f"Valid values: {', '.join(valid_values)}"
  )
  raise ValueError(msg)


def list_enum_paths() -> list[str]:
  """Return all registered enum paths, sorted."""
  return sorted(ENUM_REGISTRY)


__all__ = [
  "ENUM_REGISTRY",
  "get_enum_values",
  "list_enum_paths",
  "validate_status_for_entity",
]
