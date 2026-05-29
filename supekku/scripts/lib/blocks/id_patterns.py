"""Shared artefact ID regex patterns for block metadata validation.

Domain-specific constants reused across block-type modules
(`revision_metadata.py`, `verification_metadata.py`). Placed at the
`blocks/` package level per STD-003: the narrowest shared lib/ subpackage
covering all callers, alongside the `yaml_utils.py` precedent. Not in the
generic `blocks/metadata/` engine package — these encode spec-driver ID
shapes, not metadata-engine machinery.

The universe spans `SPEC`/`PROD`/`ISSUE` containers and the `FR`/`NF`/`NFR`
requirement tokens (DEC-142-08): a deliberate broadening over the former
SPEC-only/`(FR|NFR)` regexes, which rejected 97 legitimate corpus refs.
ADR is excluded — ADRs are decisions, not specs.
"""

from __future__ import annotations

# Requirement reference, e.g. ``SPEC-122.FR-003``, ``PROD-007.NF-001``,
# ``ISSUE-016.FR-016.001`` (dotted suffix allowed).
REQUIREMENT_ID_PATTERN = (
  r"^(SPEC|PROD|ISSUE)-\d{3,}(?:-[A-Z0-9]+)*\.(FR|NF|NFR)-[A-Z0-9.-]+$"
)

# Spec/container reference, e.g. ``SPEC-100``, ``PROD-014``, ``ISSUE-016``.
SPEC_ID_PATTERN = r"^(SPEC|PROD|ISSUE)-\d{3,}(?:-[A-Z0-9]+)*$"

__all__ = [
  "REQUIREMENT_ID_PATTERN",
  "SPEC_ID_PATTERN",
]
