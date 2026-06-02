"""Re-export shim → spec_driver.domain.records.standard / spec_driver.domain.registries.standard.

DO NOT add new code here. Canonical homes:
  - StandardRecord: spec_driver.domain.records.standard
  - StandardRegistry: spec_driver.domain.registries.standard
"""

from __future__ import annotations

from spec_driver.domain.records.standard import StandardRecord  # noqa: F401
from spec_driver.domain.registries.standard import StandardRegistry  # noqa: F401

__all__ = ["StandardRecord", "StandardRegistry"]
