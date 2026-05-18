"""Enum registry for CLI introspection and status validation.

Maps dotted enum paths (e.g. 'delta.status') to sorted lists of valid
values.

DE-137 IP-137-P01 splits the registry into two categories per DR-137 §5.2:

* **Category A** — artefact-kind ``<kind>.status`` enums whose canonical
  source is the per-kind ``FRONTMATTER_METADATA_REGISTRY[kind].fields['status']
  .enum_values``. The ``_kind_status(kind)`` factory below walks the
  registry at call time so additions/changes to per-kind metadata flow
  through without a registry edit.
* **Category B** — block-level discriminators and CLI-only enums whose
  canonical source is not (yet) per-kind frontmatter. These stay
  hardcoded as ``lambda`` providers; per-block-metadata homes for them
  follow in DE-138..142 and successor deltas.
"""

from __future__ import annotations

from collections.abc import Callable

from supekku.scripts.lib.backlog.models import (
  BACKLOG_BASE_STATUSES,
)
from supekku.scripts.lib.blocks.verification import (
  VALID_KINDS as VERIFICATION_KINDS,
)
from supekku.scripts.lib.core.frontmatter_metadata import (
  FRONTMATTER_METADATA_REGISTRY,
)
from supekku.scripts.lib.drift.models import LEDGER_STATUSES

# Category A — sourced from FRONTMATTER_METADATA_REGISTRY at call time.
_CATEGORY_A_KINDS: tuple[str, ...] = (
  "delta",
  "phase",
  "revision",
  "audit",
  "requirement",
  "verification",
  "spec",
  "policy",
  "standard",
  "memory",
  "issue",
  "problem",
  "risk",
  "adr",
)


def _kind_status(kind: str) -> Callable[[], list[str]]:
  """Provider that returns the sorted ``status`` enum_values for *kind*.

  Returns ``[]`` if the kind has no metadata entry or its ``status``
  field carries no ``enum_values`` — the empty list is the explicit
  signal that the registry walk found nothing (rather than an exception).
  """

  def _provider() -> list[str]:
    meta = FRONTMATTER_METADATA_REGISTRY.get(kind)
    if meta is None or "status" not in meta.fields:
      return []
    enum_values = meta.fields["status"].enum_values or []
    return sorted(enum_values)

  return _provider


ENUM_REGISTRY: dict[str, Callable[[], list[str]]] = {
  # Category A — derived from per-kind FRONTMATTER_METADATA_REGISTRY.
  **{f"{kind}.status": _kind_status(kind) for kind in _CATEGORY_A_KINDS},
  # Category B — block-level / CLI enums, hardcoded for now.
  "verification.kind": lambda: sorted(VERIFICATION_KINDS),
  "backlog.status": lambda: sorted(BACKLOG_BASE_STATUSES),
  "improvement.status": lambda: sorted(BACKLOG_BASE_STATUSES),
  "drift.status": lambda: sorted(LEDGER_STATUSES),
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
