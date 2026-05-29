"""Revision change summary for `list revisions` enrichment (DE-142 P03).

Mirrors `audit_check.AuditFindingsSummary`: a domain summary computed from the
``supekku:revision.change`` block, carrying cell-formatting methods for the list
view (presentation on the domain summary is the audit precedent).

``applies_to`` (the deduped spec/requirement union) is derived separately at load
(`artifacts._derive_revision_applies_to`). The source/destination SPLIT the list
columns need lives here (DR-142 §7.1, §13.2) and is never folded back into
``applies_to`` (no competing truth).
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

from supekku.scripts.lib.blocks.revision import extract_revision_blocks
from supekku.scripts.lib.core.spec_utils import load_markdown_file

if TYPE_CHECKING:
  from supekku.scripts.lib.changes.artifacts import ChangeArtifact

_EMPTY_CELL = "–"


@dataclass(frozen=True)
class RevisionChangeSummary:
  """Source/destination/requirement breakdown for a revision (DR-142 §7.1)."""

  sources: list[str]
  destinations: list[str]
  requirements: list[str]

  def source_cell(self) -> str:
    """``N (first-id)`` of origin spec refs, or em-dash."""
    if not self.sources:
      return _EMPTY_CELL
    return f"{len(self.sources)} ({self.sources[0]})"

  def destination_cell(self) -> str:
    """``N (first-id)`` of destination specs, or em-dash."""
    if not self.destinations:
      return _EMPTY_CELL
    return f"{len(self.destinations)} ({self.destinations[0]})"

  def requirements_cell(self) -> str:
    """Count of requirement ids, or em-dash."""
    return str(len(self.requirements)) if self.requirements else _EMPTY_CELL


def revision_change_summary(artifact: ChangeArtifact) -> RevisionChangeSummary:
  """Compute the scope breakdown from the revision's change block(s).

  sources   ← unique ``requirements[].origin[].ref`` where ``kind == "spec"``
  destinations ← unique ``requirements[].destination.spec``
  requirements ← unique ``requirements[].requirement_id``

  Block-derived only; unparseable blocks are skipped (tolerant load, mirroring
  `audit_findings_summary`). All three lists are sorted for determinism.
  """
  body = ""
  with contextlib.suppress(FileNotFoundError, ValueError, OSError):
    _fm, body = load_markdown_file(artifact.path)

  sources: set[str] = set()
  destinations: set[str] = set()
  requirements: set[str] = set()
  for block in extract_revision_blocks(body):
    try:
      data = block.parse()
    except ValueError:
      continue
    for req in data.get("requirements") or []:
      if not isinstance(req, dict):
        continue
      requirement_id = req.get("requirement_id")
      if requirement_id:
        requirements.add(str(requirement_id))
      destination = req.get("destination")
      if isinstance(destination, dict) and destination.get("spec"):
        destinations.add(str(destination["spec"]))
      for origin in req.get("origin") or []:
        if (
          isinstance(origin, dict)
          and origin.get("kind") == "spec"
          and origin.get("ref")
        ):
          sources.add(str(origin["ref"]))

  return RevisionChangeSummary(
    sources=sorted(sources),
    destinations=sorted(destinations),
    requirements=sorted(requirements),
  )


__all__ = ["RevisionChangeSummary", "revision_change_summary"]
