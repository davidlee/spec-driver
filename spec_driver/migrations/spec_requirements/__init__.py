"""Interactive per-spec requirement migration (DE-140, DR-140 §6).

Converts prose-format requirements (``- **FR-001**: Title``) to
structured ``supekku:spec.requirements@v1`` YAML blocks.

NOT a batch-orchestrated step — standalone interactive command via
``spec-driver admin migrate-requirements``. Folder name intentionally
does not match the ``v<M>_<m>_<p>_<N>_<slug>`` pattern so the batch
orchestrator skips it.

Per DEC-138-12: this module imports only stdlib + pyyaml +
``spec_driver.migrations._helpers``.
"""

from __future__ import annotations

__all__: list[str] = []
