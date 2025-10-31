# supekku.scripts.lib.spec_sync.models

Core data models for multi-language specification synchronization.

## Classes

### DocVariant

Named documentation artifact produced per source unit.

Examples:
    - Go: DocVariant("public",
        Path("contracts/go/foo-public.md"), "abc123", "created")
    - Python: DocVariant("api",
        Path("contracts/python/workspace-api.md"), "def456", "changed")

### SourceDescriptor

Metadata describing how a source unit should be processed.

### SourceUnit

Canonical identifier for a language-specific source unit.

Examples:
    - Go package: SourceUnit("go", "internal/foo", Path("/repo"))
    - Python module: SourceUnit("python",
        "supekku/scripts/lib/workspace.py", Path("/repo"))

### SyncOutcome

Results from a specification synchronization operation.
