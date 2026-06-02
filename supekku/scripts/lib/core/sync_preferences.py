"""Re-export shim — see spec_driver.core.sync_preferences."""

from spec_driver.core.sync_preferences import (
  persist_spec_autocreate,
  spec_autocreate_enabled,
)

__all__ = [
  "persist_spec_autocreate",
  "spec_autocreate_enabled",
]
