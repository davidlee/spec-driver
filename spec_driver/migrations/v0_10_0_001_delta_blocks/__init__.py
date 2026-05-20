"""Migration step v0_10_0_001_delta_blocks — ADR-010 placement for delta kind.

Forward-only sweep that:

- Cuts the DR-136 §4 universal frontmatter keys
  (``lifecycle``, ``aliases``, ``auditers``, ``source``).
- Cuts the delta-specific frontmatter keys ``applies_to``,
  ``context_inputs``, ``risk_register``, ``outcome_summary``.
- Synthesises the ``supekku:delta.context_inputs@v1`` and
  ``supekku:delta.risk_register@v1`` blocks from frontmatter when those
  blocks are missing.
- Synthesises the ``supekku:delta.relationships@v1`` block from
  frontmatter ``applies_to`` when that block is missing and frontmatter
  carries linkage data (DR-138 §7.3 step 3 — F-138-27).
- Moves frontmatter ``outcome_summary`` to a body ``## Outcome``
  section.
- Deletes the body ``## 7. Risks & Mitigations`` section and renumbers
  top-level ``## N.`` headings ``§§8-9 → §§7-8``.

See DR-138 §7 for the canonical mechanics.

Per DR-138 §7.6 + DEC-138-12 this package may not import anything from
``supekku.*`` or from the non-``migrations`` ``spec_driver`` subtrees
(``core``, ``models``, ``domain``, ``orchestration``, ``presentation``);
the ``Migrations isolation`` import-linter contract enforces this.
"""

from __future__ import annotations

from .migration import DeltaBlocksStep

step = DeltaBlocksStep()

__all__ = ["DeltaBlocksStep", "step"]
