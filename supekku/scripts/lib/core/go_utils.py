"""Legacy re-export shim — see spec_driver.core.go_utils."""

from spec_driver.core.go_utils import (
  GoToolchainError,
  get_go_module_name,
  is_go_available,
  normalize_go_package,
  run_go_list,
)

__all__ = [
  "GoToolchainError",
  "get_go_module_name",
  "is_go_available",
  "normalize_go_package",
  "run_go_list",
]
