# supekku.scripts.lib.core.go_utils

Go toolchain utilities for module discovery and command execution.

## Functions

- `get_go_module_name(repo_root) -> str`: Get the Go module name from go.mod.

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
- `is_go_available() -> bool`: Check if Go toolchain is available in PATH.

Returns:
    True if 'go' command is found in PATH, False otherwise

Example:
    >>> if is_go_available():
    ...     print("Go is installed")
- `normalize_go_package(pkg, module) -> str`: Convert absolute package path to relative package path.

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
- `run_go_list(repo_root, pattern) -> list[str]`: Run 'go list' and return package paths.

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

## Classes

### GoToolchainError

Raised when Go toolchain operations fail.

**Inherits from:** RuntimeError
