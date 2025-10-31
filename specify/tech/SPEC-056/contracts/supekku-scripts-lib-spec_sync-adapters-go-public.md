# supekku.scripts.lib.spec_sync.adapters.go

Go language adapter for specification synchronization.

## Classes

### GoAdapter

Language adapter for Go packages using existing gomarkdoc workflow.

Wraps the existing TechSpecSyncEngine logic to provide consistent interface
with other language adapters while maintaining full backward compatibility.

**Inherits from:** LanguageAdapter

#### Methods

- `describe(self, unit) -> SourceDescriptor`: Describe how a Go package should be processed.

Args:
    unit: Go package source unit

Returns:
    SourceDescriptor with Go-specific metadata
- `discover_targets(self, repo_root, requested) -> list[SourceUnit]`: Discover Go packages using `go list`.

Args:
    repo_root: Root directory of the repository
    requested: Optional list of specific package paths to process

Returns:
    List of SourceUnit objects for Go packages

Raises:
    GoToolchainNotAvailableError: If Go toolchain is not available
- `generate(self, unit) -> list[DocVariant]`: Generate documentation for a Go package using gomarkdoc.

Args:
    unit: Go package source unit
    spec_dir: Specification directory to write documentation to
    check: If True, only check if docs would change

Returns:
    List of DocVariant objects with generation results

Raises:
    GoToolchainNotAvailableError: If Go toolchain is not available
    GomarkdocNotAvailableError: If gomarkdoc is not available
- @staticmethod `is_go_available() -> bool`: Check if Go toolchain is available in PATH.
- @staticmethod `is_gomarkdoc_available() -> bool`: Check if gomarkdoc is available in PATH.
- `supports_identifier(self, identifier) -> bool`: Check if identifier looks like a Go package path.

Args:
    identifier: Identifier to check

Returns:
    True if identifier appears to be a Go package path

### GoToolchainNotAvailableError

Raised when Go toolchain is required but not available.

**Inherits from:** RuntimeError

### GomarkdocNotAvailableError

Raised when gomarkdoc is required but not available.

**Inherits from:** RuntimeError
