"""Lockstep: frozen migration regex must match runtime parser pattern.

Cross-cutting test ensuring DEC-138-12 frozen-local patterns in the
migration module stay in sync with the runtime parser. Lives outside
``spec_driver.migrations`` to satisfy the import-linter isolation
contract.
"""

from __future__ import annotations

from spec_driver.migrations.spec_requirements.migration import (
  _REQUIREMENT_LINE as _FROZEN,
)
from supekku.scripts.lib.requirements.parser import (
  _REQUIREMENT_LINE as _RUNTIME,
)


class TestMigrationLockstep:
  def test_frozen_regex_matches_runtime_pattern(self):
    assert _FROZEN.pattern == _RUNTIME.pattern

  def test_frozen_regex_matches_runtime_flags(self):
    assert _FROZEN.flags == _RUNTIME.flags
