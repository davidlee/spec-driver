"""Shared artifact ID classification and normalization.

Consolidated patterns for recognizing spec-driver artifact IDs.
Memory IDs (mem.*) use a different scheme — see memory/ids.py.
"""

from __future__ import annotations

import re
from collections.abc import Set
from dataclasses import dataclass

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


# ── ID normalization ───────────────────────────────────────────

# Matches PREFIX-DIGITS with optional trailing segments.
_PREFIX_NUM_RE = re.compile(r"^([A-Z]+-?)(\d+)((?:\.[A-Z].*|(?:-[A-Z0-9]+)*)?)$")

_MAX_PAD_WIDTH = 6


@dataclass(frozen=True)
class NormalizationResult:
  """Result of attempting to normalize an artifact ID.

  Attributes:
    canonical: Resolved canonical form, or None if no match found.
    original: The input string as provided.
    diagnostic: Warning message when a non-canonical form resolves.
  """

  canonical: str | None
  original: str
  diagnostic: str | None = None


def normalize_artifact_id(
  raw: str,
  known_ids: Set[str],
) -> NormalizationResult:
  """Attempt to normalize a potentially non-canonical artifact ID.

  Strategy:
    1. Direct lookup — if raw is in known_ids, it is already canonical.
    2. Parse prefix + numeric suffix (+ optional trailing segments).
    3. Try zero-padded variants of the numeric portion against known_ids,
       from current width+1 up to ``_MAX_PAD_WIDTH``.
    4. Return first match with a diagnostic, or None if no match.

  Does not assume a fixed digit width — tries increasing padding until
  either a match is found or a reasonable limit is reached.  This
  supports current 3-digit IDs and future 4-digit+ IDs.

  Args:
    raw: Raw ID string (e.g. ``"ADR-11"``).
    known_ids: Set of canonical IDs to match against.

  Returns:
    NormalizationResult with canonical form (if found) and diagnostic.
  """
  if not raw:
    return NormalizationResult(canonical=None, original=raw)

  # Direct lookup — already canonical
  if raw in known_ids:
    return NormalizationResult(canonical=raw, original=raw)

  # Parse prefix + digits + optional suffix
  match = _PREFIX_NUM_RE.match(raw)
  if not match:
    return NormalizationResult(canonical=None, original=raw)

  prefix, digits, suffix = match.group(1), match.group(2), match.group(3)
  num = int(digits)

  # Try increasing zero-padding widths
  for width in range(len(digits) + 1, _MAX_PAD_WIDTH + 1):
    candidate = f"{prefix}{num:0{width}d}{suffix}"
    if candidate in known_ids:
      return NormalizationResult(
        canonical=candidate,
        original=raw,
        diagnostic=f"Non-canonical ID '{raw}' resolved to '{candidate}'",
      )

  return NormalizationResult(canonical=None, original=raw)
