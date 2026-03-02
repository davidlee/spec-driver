"""Shared artifact ID classification.

Consolidated patterns for recognizing spec-driver artifact IDs.
Memory IDs (mem.*) use a different scheme — see memory/ids.py.
"""

from __future__ import annotations

import re

# Order matters: requirement must be checked before spec/prod (more specific).
ID_PATTERNS: dict[str, re.Pattern[str]] = {
  "requirement": re.compile(
    r"^(?:SPEC|PROD)-\d{3,}(?:-[A-Z0-9]+)*\.(?:FR|NFR)-[A-Z0-9-]+$"
  ),
  "spec": re.compile(r"^SPEC-\d{3,}(?:-[A-Z0-9]+)*$"),
  "prod": re.compile(r"^PROD-\d{3,}(?:-[A-Z0-9]+)*$"),
  "adr": re.compile(r"^ADR-\d{3,}$"),
  "delta": re.compile(r"^DE-\d{3,}$"),
  "revision": re.compile(r"^RE-\d{3,}$"),
  "audit": re.compile(r"^AUD-\d{3,}$"),
  "phase": re.compile(r"^IP-\d{3,}(?:-[A-Z0-9]+)*\.PHASE-\d{2}$"),
  "plan": re.compile(r"^IP-\d{3,}$"),
  "verification": re.compile(r"^V[TAH]-\d{3,}$"),
  "policy": re.compile(r"^POL-\d{3,}$"),
  "standard": re.compile(r"^STD-\d{3,}$"),
  "backlog": re.compile(r"^(?:ISSUE|IMPR|PROB|RISK)-\d{3,}$"),
}


def classify_artifact_id(raw: str) -> str | None:
  """Return artifact kind string, or None if unrecognized.

  Args:
    raw: Raw ID string to classify.

  Returns:
    Kind string (e.g. 'spec', 'adr', 'requirement') or None.
  """
  for kind, pattern in ID_PATTERNS.items():
    if pattern.match(raw):
      return kind
  return None


def is_artifact_id(raw: str) -> bool:
  """True if raw matches any known artifact ID pattern."""
  return classify_artifact_id(raw) is not None


def is_kind(raw: str, kind: str) -> bool:
  """True if raw matches the pattern for a specific artifact kind.

  More efficient than classify_artifact_id when checking a single kind.

  Args:
    raw: Raw ID string to check.
    kind: Expected kind (e.g. 'spec', 'adr', 'requirement').

  Raises:
    KeyError: If kind is not in ID_PATTERNS.
  """
  return bool(ID_PATTERNS[kind].match(raw))
