"""Re-export shim → spec_driver.domain.records.policy / .registries.policy.

DO NOT add new code here. Canonical homes:
  - PolicyRecord: spec_driver.domain.records.policy
  - PolicyRegistry: spec_driver.domain.registries.policy
"""

from __future__ import annotations

from spec_driver.domain.records.policy import PolicyRecord  # noqa: F401
from spec_driver.domain.registries.policy import PolicyRegistry  # noqa: F401

__all__ = ["PolicyRecord", "PolicyRegistry"]
