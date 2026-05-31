"""Legacy re-export shim — see spec_driver.core.npm_utils."""

from spec_driver.core.npm_utils import (
  PackageManager,
  PackageManagerInfo,
  detect_package_manager,
  get_install_instructions,
  get_package_manager_info,
  is_bun_available,
  is_npm_available,
  is_npm_package_available,
  is_pnpm_available,
)

__all__ = [
  "PackageManager",
  "PackageManagerInfo",
  "detect_package_manager",
  "get_install_instructions",
  "get_package_manager_info",
  "is_bun_available",
  "is_npm_available",
  "is_npm_package_available",
  "is_pnpm_available",
]
