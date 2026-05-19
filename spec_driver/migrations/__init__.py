"""Migration framework for spec-driver schema-version sweeps.

This package is the canonical home for forward-only artefact-data
migrations. Per DR-137 §5.6 and POL-003 / DEC-137-11, migration step
modules import **only** from ``spec_driver.migrations._protocol``,
``spec_driver.migrations._helpers``, ``spec_driver.migrations._folder``,
the standard library, and pinned ``pyyaml``. The
``Migrations isolation`` import-linter contract enforces.

DE-137 ships zero migrations; the framework lands here and the
sibling DE-138..142 deltas activate per-kind sweeps.
"""

from __future__ import annotations
