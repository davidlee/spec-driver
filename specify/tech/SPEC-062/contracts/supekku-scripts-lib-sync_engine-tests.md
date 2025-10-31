# supekku.scripts.lib.sync_engine

Synchronization engine for managing spec and change relationships.

## Constants

- `CONTRACTS_DIRNAME`
- `DocGeneratorFn`
- `LogFn`
- `PRIVATE_DOC`
- `PUBLIC_DOC`
- `RunFn`
- `SKIP_KEYWORDS`
- `__all__`

## Functions

- `default_generate_docs(spec_dir, module_pkg, include_unexported, check) -> None`: Generate documentation using gomarkdoc.
- `default_gomarkdoc_available() -> bool`: Check if gomarkdoc command is available in PATH.
- `default_log(message) -> None`: Default logging function that prints to stdout.
- `default_run(cmd) -> CompletedProcess[str]`: Default command runner using subprocess.

## Classes

### GomarkdocNotAvailableError

Raised when gomarkdoc is required but not available.

**Inherits from:** RuntimeError

### SkippedPackage

Information about a package that was skipped during sync.

### SyncOptions

Configuration options for specification synchronization.

### SyncResult

Results from a specification synchronization operation.

### TechSpecSyncEngine

Engine for synchronizing technical specifications with source code.

#### Methods

- @staticmethod `determine_slug(package) -> str`: Generate a filesystem-safe slug from package path.
- `ensure_package_list(self, spec_path, package) -> None`: Ensure package is listed in spec frontmatter.
- `ensure_spec_stub(self, spec_dir, spec_id, slug, package) -> <BinOp>`: Ensure a spec stub file exists, creating if allowed.
- `go_module_name(self) -> str`: Get the Go module name from go.mod. - Internal helpers ----------------------------------------------
- `load_registry(self) -> dict[Tuple[str, str]]`: Load the package-to-spec registry from disk (v2 format only).
- `next_spec_id(self, existing) -> str`: Generate the next available SPEC-### ID.
- @staticmethod `normalize_package(pkg, module) -> str`: Convert absolute package path to relative package path.
- `package_has_go_files(self, rel_pkg) -> bool`: Check if package contains non-test Go files.
- `resolve_spec_dir(self, spec_id) -> Path`: Resolve the directory path for a given spec ID.
- `save_registry(self, registry) -> None`: Save the package-to-spec registry to disk (v2 format only).
- @staticmethod `should_skip(pkg) -> bool`: Check if package should be skipped based on patterns.
- `spec_ids_from_disk(self) -> list[str]`: Get all existing spec IDs from filesystem.
- `synchronize(self, options) -> SyncResult`: Synchronize specifications with source code packages. - Public API -----------------------------------------------------
- `__init__(self) -> None`: Initialize the TechSpecSyncEngine with required dependencies.
- `_resolve_package_targets(self, options, module, registry) -> list[str]`: Resolve which packages to process based on options. - Private helper -------------------------------------------------
