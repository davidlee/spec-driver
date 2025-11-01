"""Go toolchain utilities for module discovery and command execution."""

from __future__ import annotations

import subprocess
from pathlib import Path
from shutil import which


class GoToolchainError(RuntimeError):
  """Raised when Go toolchain operations fail."""


def is_go_available() -> bool:
  """Check if Go toolchain is available in PATH.

  Returns:
      True if 'go' command is found in PATH, False otherwise

  Example:
      >>> if is_go_available():
      ...     print("Go is installed")
  """
  return which("go") is not None


def get_go_module_name(repo_root: Path) -> str:
  """Get the Go module name from go.mod.

  Args:
      repo_root: Repository root containing go.mod

  Returns:
      Module name (e.g., "github.com/user/repo")

  Raises:
      GoToolchainError: If go command fails or go.mod not found

  Example:
      >>> module = get_go_module_name(Path("/path/to/repo"))
      >>> print(module)
      "github.com/user/repo"
  """
  try:
    result = subprocess.run(
      ["go", "list", "-m"],
      cwd=repo_root,
      check=True,
      capture_output=True,
      text=True,
    )
    return result.stdout.strip()
  except subprocess.CalledProcessError as e:
    msg = f"Failed to read Go module name: {e.stderr}"
    raise GoToolchainError(msg) from e


def run_go_list(
  repo_root: Path,
  pattern: str = "./...",
) -> list[str]:
  """Run 'go list' and return package paths.

  Args:
      repo_root: Repository root
      pattern: Package pattern (default: "./..." for all packages)

  Returns:
      List of package paths

  Raises:
      GoToolchainError: If go list command fails

  Example:
      >>> packages = run_go_list(Path("/repo"))
      >>> print(packages)
      ["github.com/user/repo", "github.com/user/repo/internal/foo"]
  """
  try:
    result = subprocess.run(
      ["go", "list", pattern],
      cwd=repo_root,
      check=True,
      capture_output=True,
      text=True,
    )
    return result.stdout.splitlines()
  except subprocess.CalledProcessError as e:
    msg = f"Failed to list Go packages: {e.stderr}"
    raise GoToolchainError(msg) from e


def normalize_go_package(pkg: str, module: str) -> str:
  """Convert absolute package path to relative package path.

  Args:
      pkg: Package path (may be absolute or relative)
      module: Go module name

  Returns:
      Relative package path

  Example:
      >>> normalize_go_package(
      ...     "github.com/user/repo/internal/foo",
      ...     "github.com/user/repo"
      ... )
      "internal/foo"
  """
  if pkg.startswith(module + "/"):
    return pkg[len(module) + 1 :]
  return pkg
