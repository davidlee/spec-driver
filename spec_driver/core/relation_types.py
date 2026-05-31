"""Named constants for relation types and reference sources (POL-002).

RELATION_TYPES enumerates the valid values for the ``type`` field in
frontmatter ``relations`` entries.

REFERENCE_SOURCES enumerates the slots that :func:`collect_references`
searches when building a complete forward-reference list for an artifact.
"""

from __future__ import annotations

RELATION_TYPES: frozenset[str] = frozenset(
  {
    "implements",
    "verifies",
    "depends_on",
    "collaborates_with",
    "provides_for",
    "supersedes",
    "superseded_by",
    "relates_to",
    "blocks",
    "blocked_by",
    "decomposes",
    "tracked_by",
  }
)

REFERENCE_SOURCES: frozenset[str] = frozenset(
  {
    "relation",
    "applies_to",
    "context_input",
    "informed_by",
    "domain_field",
    "backlog_field",
  }
)

__all__ = ["REFERENCE_SOURCES", "RELATION_TYPES"]
