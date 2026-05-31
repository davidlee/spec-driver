"""Utilities for npm package manager detection and dependency handling.

This module provides centralized functionality for:
- Detecting package managers (npm, pnpm, bun) from lockfiles
- Checking availability of package managers and npm packages
- Building correct command syntax for each package manager
- Generating installation instructions

Designed for reuse across TypeScriptAdapter, installer, and doctor command.
"""

import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from shutil import which
from typing import Literal

# Type alias for supported package managers
PackageManager = Literal["npm", "pnpm", "bun"]


@dataclass
class PackageManagerInfo:
  """Information about detected package manager and its commands.

  Attributes:
      name: Package manager name (npm, pnpm, or bun)
      build_npx_command: Function to build npx-equivalent command for a package
      install_global_command: Command to install package globally
      install_local_command: Command to install package locally (dev dependency)

  """

  name: PackageManager
  build_npx_command: Callable[[str], list[str]]
  install_global_command: list[str]
  install_local_command: list[str]


def is_npm_available() -> bool:
  """Check if npm is available in PATH.

  Returns:
      True if 'npm' command is found in PATH, False otherwise

  """
  return which("npm") is not None


def is_pnpm_available() -> bool:
  """Check if pnpm is available in PATH.

  Returns:
      True if 'pnpm' command is found in PATH, False otherwise

  """
  return which("pnpm") is not None


def is_bun_available() -> bool:
  """Check if bun is available in PATH.

  Returns:
      True if 'bun' command is found in PATH, False otherwise

  """
  return which("bun") is not None


def detect_package_manager(path: Path) -> PackageManager:
  """Detect package manager from lockfile.

  Walks up directory tree to find lockfile.
  Priority: pnpm > bun > npm

  Args:
      path: Starting path (file or directory)

  Returns:
      Package manager name: 'pnpm', 'bun', or 'npm'

  """
  current = path if path.is_dir() else path.parent

  while current != current.parent:
    if (current / "pnpm-lock.yaml").exists():
      return "pnpm"
    if (current / "bun.lockb").exists():
      return "bun"
    if (current / "package-lock.json").exists() or (current / "yarn.lock").exists():
      return "npm"
    current = current.parent

  # Default to npm
  return "npm"


def get_package_manager_info(path: Path) -> PackageManagerInfo:
  """Get package manager info for given path.

  Detects package manager from lockfile and returns appropriate commands.
  Falls back to npm if detected package manager is not available in PATH.

  Args:
      path: Path to detect package manager from (file or directory)

  Returns:
      PackageManagerInfo with commands for detected/available package manager

  """
  pm = detect_package_manager(path)

  if pm == "pnpm" and is_pnpm_available():
    return PackageManagerInfo(
      name="pnpm",
      build_npx_command=lambda pkg: ["pnpm", "dlx", f"--package={pkg}", pkg],
      install_global_command=["pnpm", "add", "-g"],
      install_local_command=["pnpm", "add", "--save-dev"],
    )

  if pm == "bun" and is_bun_available():
    return PackageManagerInfo(
      name="bun",
      build_npx_command=lambda pkg: ["bunx", "--yes", pkg],
      install_global_command=["bun", "add", "-g"],
      install_local_command=["bun", "add", "--save-dev"],
    )

  # Default to npm (also fallback if pnpm/bun detected but not available)
  return PackageManagerInfo(
    name="npm",
    build_npx_command=lambda pkg: ["npx", "--yes", pkg],
    install_global_command=["npm", "install", "-g"],
    install_local_command=["npm", "install", "--save-dev"],
  )


def is_npm_package_available(
  package_name: str, package_root: Path | None = None
) -> bool:
  """Check if npm package is available locally or globally.

  Checks local node_modules/.bin/ first (if package_root provided),
  then falls back to global PATH check.

  Args:
      package_name: Name of the npm package to check
      package_root: Optional project root directory to check for local installation

  Returns:
      True if package is available locally (and executable) or globally

  """
  # Check local installation first if package_root provided
  if package_root is not None:
    local_bin = package_root / "node_modules" / ".bin" / package_name
    # Check if exists, is file, and is executable
    if local_bin.exists() and local_bin.is_file() and os.access(local_bin, os.X_OK):
      return True

  # Fall back to global PATH check
  return which(package_name) is not None


def get_install_instructions(
  package_name: str, pm_info: PackageManagerInfo, prefer_local: bool = False
) -> str:
  """Generate installation instructions for the user's package manager.

  Args:
      package_name: Name of the npm package
      pm_info: Package manager information with install commands
      prefer_local: If True, show local installation first, else global first

  Returns:
      Formatted multi-line installation instructions

  """
  # Build command strings
  global_cmd = " ".join(pm_info.install_global_command + [package_name])
  local_cmd = " ".join(pm_info.install_local_command + [package_name])

  # Format instructions based on preference
  if prefer_local:
    return f"Install locally: {local_cmd}\nOr globally: {global_cmd}"
  return f"Install globally: {global_cmd}\nOr locally: {local_cmd}"
