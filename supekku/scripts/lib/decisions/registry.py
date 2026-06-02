"""Re-export shim → spec_driver.domain.records.decision / .registries.decision.

DO NOT add new code here. Canonical homes:
  - DecisionRecord: spec_driver.domain.records.decision
  - DecisionRegistry: spec_driver.domain.registries.decision
"""

from __future__ import annotations

from spec_driver.domain.records.decision import DecisionRecord  # noqa: F401
from spec_driver.domain.registries.decision import DecisionRegistry  # noqa: F401

__all__ = ["DecisionRecord", "DecisionRegistry"]
