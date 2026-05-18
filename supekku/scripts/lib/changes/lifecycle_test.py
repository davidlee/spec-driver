"""Tests for change artifact lifecycle constants (post DE-137).

The legacy ``normalize_status`` and ``CANONICAL_STATUS_MAP`` were retired
in DE-137 IP-137-P01 (DEC-137-14 / DEC-137-23). Their successor —
``blocks.metadata.aliases.normalize_field`` — is exercised by
``blocks/metadata/aliases_test.py`` (VT-CC-013 parity).
"""

from __future__ import annotations

from .lifecycle import (
  CHANGE_STATUSES,
  STATUS_COMPLETED,
  STATUS_DRAFT,
  STATUS_IN_PROGRESS,
  STATUS_PENDING,
)


def test_canonical_change_statuses() -> None:
  """``CHANGE_STATUSES`` enumerates the canonical change-artefact statuses."""
  assert (
    frozenset(
      {
        STATUS_DRAFT,
        STATUS_PENDING,
        STATUS_IN_PROGRESS,
        STATUS_COMPLETED,
        "deferred",
      }
    )
    == CHANGE_STATUSES
  )


def test_canonical_constants_exposed() -> None:
  """Status constants remain exported for callers (compat re-export)."""
  assert STATUS_DRAFT == "draft"
  assert STATUS_PENDING == "pending"
  assert STATUS_IN_PROGRESS == "in-progress"
  assert STATUS_COMPLETED == "completed"
