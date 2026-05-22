"""Migration step v0_10_0_002_spec_blocks — ADR-010 placement for spec kind.

Forward-only sweep that:

- Cuts deprecated FM keys: ``packages``, ``concerns``, ``hypotheses``,
  ``decisions``, ``verification_strategy``, ``scope``.
- Emits ``supekku:spec.{concerns,hypotheses,decisions}@v1`` blocks in
  the body when the corresponding FM field carried non-empty content.
- Moves FM ``scope`` to a prose paragraph in the body (§1).
- Defaults ``category`` to ``unknown`` and ``c4_level`` to ``unknown``
  when missing (taxonomy-strict tolerance per DEC-139-08).

See DR-139 §3.1 + §8 for the canonical mechanics.

Per DEC-138-12 this package may not import anything from ``supekku.*``
or from non-``migrations`` ``spec_driver`` subtrees.
"""

from __future__ import annotations

from .migration import SpecBlocksStep

step = SpecBlocksStep()

__all__ = ["SpecBlocksStep", "step"]
