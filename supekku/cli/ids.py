"""Artifact ID normalization and prefix handling."""

from __future__ import annotations

# Artifact types with unambiguous prefixes (can use numeric shorthand)
ARTIFACT_PREFIXES: dict[str, str] = {
  "adr": "ADR-",
  "delta": "DE-",
  "revision": "RE-",
  "policy": "POL-",
  "standard": "STD-",
  "issue": "ISSUE-",
  "problem": "PROB-",
  "improvement": "IMPR-",
  "risk": "RISK-",
  "plan": "IP-",
  "audit": "AUD-",
  "drift_ledger": "DL-",
}

# Plan ID prefix for normalization
ARTIFACT_PREFIXES_PLAN = "IP-"

# Reverse mapping: prefix string → artifact type key.
# Used by resolve_by_id() to infer artifact type from a bare ID like "DE-061".
PREFIX_TO_TYPE: dict[str, str] = {
  "ADR": "adr",
  "DE": "delta",
  "RE": "revision",
  "POL": "policy",
  "STD": "standard",
  "SPEC": "spec",
  "PROD": "spec",
  "IP": "plan",
  "AUD": "audit",
  "ISSUE": "issue",
  "PROB": "problem",
  "IMPR": "improvement",
  "RISK": "risk",
  "T": "card",
  "DL": "drift_ledger",
}


def normalize_id(artifact_type: str, raw_id: str) -> str:
  """Normalize artifact ID by prepending prefix if raw_id is numeric-only.

  For artifact types with unambiguous prefixes, allows shorthand like '001' or '1'
  to be expanded to 'ADR-001' etc. Numeric IDs are zero-padded to 3 digits.

  Args:
    artifact_type: The artifact type key (e.g., 'adr', 'delta')
    raw_id: The user-provided ID (e.g., '001', 'ADR-001', 'foo')

  Returns:
    Normalized ID with prefix, or original ID if not applicable.

  Examples:
    >>> normalize_id("adr", "1")
    'ADR-001'
    >>> normalize_id("adr", "001")
    'ADR-001'
    >>> normalize_id("adr", "ADR-001")
    'ADR-001'
    >>> normalize_id("spec", "001")
    '001'

  """
  if artifact_type not in ARTIFACT_PREFIXES:
    return raw_id  # No normalization for ambiguous types

  prefix = ARTIFACT_PREFIXES[artifact_type]

  # Already has correct prefix
  if raw_id.upper().startswith(prefix):
    return raw_id.upper()

  # Numeric-only: prepend prefix with zero-padding
  if raw_id.isdigit():
    return f"{prefix}{int(raw_id):03d}"

  # Not numeric, return as-is (might be a slug or other format)
  return raw_id


def _normalize_plan_id(raw_id: str) -> str:
  """Normalize plan ID: '41' -> 'IP-041', 'IP-041' -> 'IP-041'."""
  if raw_id.upper().startswith(ARTIFACT_PREFIXES_PLAN):
    return raw_id.upper()
  if raw_id.isdigit():
    return f"{ARTIFACT_PREFIXES_PLAN}{int(raw_id):03d}"
  return raw_id


def _parse_prefix(raw_id: str) -> str | None:
  """Extract alphabetic prefix from an ID like 'DE-061' or 'ISSUE-045'.

  Returns the prefix string (e.g. 'DE', 'ISSUE') if the ID matches the
  PREFIX-NNN pattern, or None otherwise.
  """
  parts = raw_id.split("-", 1)
  if len(parts) == 2 and parts[0].isalpha():
    return parts[0].upper()
  return None
