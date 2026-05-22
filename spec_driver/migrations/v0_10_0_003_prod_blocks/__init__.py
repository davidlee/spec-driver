"""Migration step v0_10_0_003_prod_blocks — DR-139 §3.2 placement for prod kind.

Forward-only sweep that:

- Cuts deprecated FM keys: ``hypotheses``, ``decisions``,
  ``verification_strategy``, ``scope``.
- Emits ``supekku:spec.{hypotheses,decisions}@v1`` blocks when FM
  carried non-empty content (shared schema per DEC-139-01).
- Moves FM ``scope`` to a prose paragraph in the body.

See DR-139 §3.2 for the canonical mechanics.

Per DEC-138-12 this package may not import anything from ``supekku.*``
or from non-``migrations`` ``spec_driver`` subtrees.
"""

from __future__ import annotations

from .migration import ProdBlocksStep

step = ProdBlocksStep()

__all__ = ["ProdBlocksStep", "step"]
