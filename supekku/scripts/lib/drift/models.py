"""Drift ledger models and lifecycle vocabulary.

A drift ledger tracks divergence between normative truth (specs/ADRs/policies)
and observed truth (code/contracts/runtime). See IMPR-007, ADR-008, DR-065.

Lifecycle constants use permissive validation with warnings (DEC-057-08 pattern).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# -- Ledger lifecycle statuses --

LEDGER_STATUSES: frozenset[str] = frozenset({"open", "closed"})

# -- Entry lifecycle statuses --

ENTRY_STATUSES: frozenset[str] = frozenset(
  {
    "open",
    "triaged",
    "adjudicated",
    "resolved",
    "deferred",
    "dismissed",
    "superseded",
  }
)

# -- Entry types --

ENTRY_TYPES: frozenset[str] = frozenset(
  {
    "contradiction",
    "implementation_drift",
    "stale_claim",
    "missing_decision",
    "ambiguous_intent",
  }
)

# -- Severity levels --

SEVERITIES: frozenset[str] = frozenset({"blocking", "significant", "cosmetic"})

# -- Assessment values --

ASSESSMENTS: frozenset[str] = frozenset(
  {"confirmed", "disputed", "not_drift", "deferred"}
)

# -- Resolution paths --

RESOLUTION_PATHS: frozenset[str] = frozenset(
  {"ADR", "RE", "DE", "editorial", "no_change", "backlog"}
)


def is_valid_entry_status(status: str) -> bool:
  """Check whether a status is in the accepted entry lifecycle set.

  Returns True for known statuses, False for unknown. Logs a warning
  for unknown values (permissive validation per DEC-057-08).
  """
  if status in ENTRY_STATUSES:
    return True
  logger.warning(
    "Entry status %r is not in accepted values: %s",
    status,
    sorted(ENTRY_STATUSES),
  )
  return False


def is_valid_ledger_status(status: str) -> bool:
  """Check whether a status is in the accepted ledger lifecycle set."""
  if status in LEDGER_STATUSES:
    return True
  logger.warning(
    "Ledger status %r is not in accepted values: %s",
    status,
    sorted(LEDGER_STATUSES),
  )
  return False


# -- Typed substructures (DEC-065-06) --


@dataclass(frozen=True)
class Source:
  """Where drift appears — an artifact reference with optional context."""

  kind: str  # spec, prod, adr, policy, doc, impl, contract, ...
  ref: str  # artifact ID or path
  note: str = ""


@dataclass(frozen=True)
class Claim:
  """What is conflicting or unclear — an assertion, observation, gap, or question."""

  kind: str  # assertion, observation, gap, question
  text: str
  label: str = ""  # optional: expected, observed, A, B, freeform


@dataclass(frozen=True)
class DiscoveredBy:
  """Discovery origin for a drift entry."""

  kind: str  # audit, survey, agent, human
  ref: str = ""  # optional: VA-047-001, etc.


# -- Entry and Ledger models --


@dataclass
class DriftEntry:
  """A single drift entry within a ledger.

  Fields follow IMPR-007 D1–D14 with typed substructures (DEC-065-06).
  Progressive strictness: only id, title, status, and entry_type are
  expected at minimum. All other fields default to empty.
  """

  id: str  # "DL-047.001"
  title: str  # from heading after ID
  status: str = "open"
  entry_type: str = ""  # contradiction, implementation_drift, ...
  severity: str = ""  # blocking, significant, cosmetic
  topic: str = ""  # lifecycle, taxonomy, contracts, ...
  owner: str = ""
  sources: list[Source] = field(default_factory=list)
  claims: list[Claim] = field(default_factory=list)
  assessment: str = ""  # confirmed, disputed, not_drift, deferred
  resolution_path: str = ""  # ADR, RE, DE, editorial, no_change, backlog
  resolution_ref: str = ""  # ADR-008, DE-050, etc.
  affected_artifacts: list[str] = field(default_factory=list)
  discovered_by: DiscoveredBy | None = None
  analysis: str = ""  # freeform markdown outside YAML fence
  evidence: list[str] = field(default_factory=list)
  extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class DriftLedger:
  """A drift ledger — one file per scope of work.

  Contains frontmatter metadata plus parsed entries.
  See IMPR-007 D1 (ledger-as-file) and DEC-065-08 (body preserved).
  """

  id: str  # "DL-047"
  name: str
  status: str = "open"
  path: Path = field(default_factory=Path)
  created: str = ""
  updated: str = ""
  delta_ref: str = ""  # owning delta, if any
  body: str = ""  # freeform content before entries
  frontmatter: dict[str, Any] = field(default_factory=dict)
  entries: list[DriftEntry] = field(default_factory=list)
