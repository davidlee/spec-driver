# supekku.cli.common

Common utilities, options, and callbacks for CLI commands.

This module provides reusable CLI option types, shared data types for artifact
resolution, and consistent flag behavior across all CLI commands.

## Standardized Flags

Across all list commands, we use consistent flag patterns:
- `--format`: Output format (table|json|tsv)
- `--truncate`: Enable field truncation in table output (default: off, full content)
- `--filter`: Substring filter (case-insensitive)
- `--regexp`: Regular expression pattern for filtering
- `--case-insensitive`: Make regexp matching case-insensitive
- `--status`: Filter by status (entity-specific values)
- `--root`: Repository root directory

## Module Notes

- # Standardized Flags

## Constants

- `ARTIFACT_PREFIXES_PLAN` - Plan ID prefix for normalization
- `CaseInsensitiveOption`
- `ContentTypeOption`
- `EXIT_FAILURE` - Exit codes
- `EXIT_SUCCESS` - Exit codes
- `ExternalOption`
- `FormatOption` - Standardized list command options
- `PagerOption`
- `RegexpOption`
- `RootOption` - Common option definitions for reuse
- `TruncateOption`
- `VersionOption` - Version option for main app

## Functions

- `emit_artifact(ref) -> None`: Dispatch artifact output by mode.

Supports path, raw, body, json, content-type, or formatted output.

Handles mutual-exclusivity check for --json/--path/--raw/--body-only
and calls the appropriate output function. When ``content_type`` is
provided it takes precedence over the boolean flags (with a warning if
both are given).  Always raises typer.Exit.

Args:
  ref: Resolved artifact reference.
  json_output: If True, output JSON via json_fn.
  path_only: If True, echo the artifact path.
  raw_output: If True, echo raw file content.
  body_only: If True, echo body text only (no frontmatter).
  content_type: Unified content-type selector (overrides boolean flags).
  format_fn: Callable(record) -> str for default formatted output.
  json_fn: Callable(record) -> str for JSON output. Required.

Raises:
  typer.Exit: Always — EXIT_SUCCESS on success, EXIT_FAILURE on error.
- `extract_yaml_frontmatter(path) -> str`: Extract raw YAML frontmatter block from a markdown file.

Returns the YAML content between the opening and closing ``---`` fences,
without the fences themselves.  Returns an empty string if no frontmatter
is found.
- `find_artifacts(artifact_type, pattern, root) -> Iterator[ArtifactRef]`: Find all artifacts of a type matching a fnmatch pattern.

Companion to resolve_artifact for the find verb group. Returns an
iterator of ArtifactRef for all matching artifacts.

Args:
  artifact_type: Artifact type key (e.g. 'revision', 'spec').
  pattern: fnmatch pattern to match against artifact IDs.
  root: Repository root path.

Yields:
  ArtifactRef for each matching artifact.

Raises:
  ValueError: If artifact_type is not in the dispatch table.
- `get_editor() -> <BinOp>`: Get editor command from environment or fallback.

Resolution order: $EDITOR -> $VISUAL -> vi

Returns:
  Editor command string, or None if no editor available.
- `get_pager() -> <BinOp>`: Get pager command from environment or fallback.

Resolution order: $PAGER -> less -> more

Returns:
  Pager command string, or None if no pager available.
- `load_all_artifacts(root, artifact_type) -> list[Any]`: Load all artifacts of a given type for cross-registry queries.

Used by ``--referenced-by`` / ``--not-referenced-by`` CLI flags to load
referrer registries.  Uses lazy imports matching existing common.py patterns.

Args:
  root: Repository root path.
  artifact_type: Artifact type key (e.g. 'audit', 'delta', 'spec').

Returns:
  List of artifact records from the resolved registry.

Raises:
  typer.BadParameter: If artifact_type is unknown.
- `matches_regexp(pattern, text_fields, case_insensitive) -> bool`: Check if any of the text fields match the given regexp pattern.

Args:
  pattern: Regular expression pattern (None means no filtering)
  text_fields: List of text fields to search
  case_insensitive: Whether to perform case-insensitive matching

Returns:
  True if pattern is None (no filter) or if any field matches the pattern

Raises:
  re.error: If the pattern is invalid
- `normalize_id(artifact_type, raw_id) -> str`: Normalize artifact ID by prepending prefix if raw_id is numeric-only.

For artifact types with unambiguous prefixes, allows shorthand like '001' or '1'
to be expanded to 'ADR-001' etc. Numeric IDs are zero-padded to 3 digits.

Args:
  artifact_type: The artifact type key (e.g., 'adr', 'delta')
  raw_id: The user-provided ID (e.g., '001', 'ADR-001', 'foo')

Returns:
  Normalized ID with prefix, or original ID if not applicable.

Examples:
  >>> normalize_id("adr", "1")
  'ADR-001'
  >>> normalize_id("adr", "001")
  'ADR-001'
  >>> normalize_id("adr", "ADR-001")
  'ADR-001'
  >>> normalize_id("spec", "001")
  '001'
- `open_in_editor(path) -> None`: Open file in editor.

Args:
  path: Path to file to open

Raises:
  RuntimeError: If no editor is available
- `open_in_pager(path) -> None`: Open file in pager.

Args:
  path: Path to file to open

Raises:
  RuntimeError: If no pager is available
- `render_file(path) -> None`: Render markdown file to stdout without paging.

Cascade: glow → rich → raw stdout.

Args:
  path: Path to markdown file.
- `render_file_paged(path) -> None`: Render markdown file in a pager.

Cascade: $PAGER → glow -p → ov → less → more.

Args:
  path: Path to markdown file.

Raises:
  RuntimeError: If no pager or renderer is available.
- `resolve_artifact(artifact_type, raw_id, root) -> ArtifactRef`: Resolve an artifact by type and ID, returning an ArtifactRef.

Uses a dispatch table to delegate to type-specific resolvers. Each
resolver handles ID normalization, registry lookup, and not-found errors.

Args:
  artifact_type: Artifact type key (e.g. 'revision', 'spec', 'adr').
  raw_id: User-provided ID (may be shorthand like '1' or full like 'RE-001').
  root: Repository root path.

Returns:
  ArtifactRef with resolved id, path, and record.

Raises:
  ArtifactNotFoundError: If the artifact cannot be found.
  ValueError: If artifact_type is not in the dispatch table.
- `resolve_by_id(raw_id, root) -> list[tuple[Tuple[str, ArtifactRef]]]`: Resolve artifact type from a bare ID (prefixed or numeric).

Uses _build_artifact_index() from resolve.py for O(1) lookup across all
registries (DEC-063-04 / POL-001).

Args:
  raw_id: User-provided ID (e.g. 'DE-061', '61', 'SPEC-009').
  root: Repository root path.

Returns:
  List of (artifact_type, ArtifactRef) tuples. Empty if no match.
  Prefixed IDs return 0 or 1 matches; numeric IDs may return multiple.
- `root_option_callback(value) -> Path`: Callback to process root directory option with auto-detection.

Args:
    value: The provided root path, or None to auto-detect

Returns:
    Resolved root path
- `version_callback(value) -> None`: Print version and exit if --version flag is provided.

Args:
    value: Whether --version was specified

## Classes

### AmbiguousArtifactError

Raised when multiple artifacts match a single-target lookup.

**Inherits from:** Exception

### ArtifactNotFoundError

Raised when an artifact cannot be found by ID.

**Inherits from:** Exception

### ArtifactRef

Resolved artifact reference returned by resolve_artifact.

### ContentType

Unified output content-type selector for show commands.

**Inherits from:** enum.Enum, str

### InferringGroup

Typer Group that infers artifact type from bare IDs.

When resolve_command() encounters an unknown subcommand name, it stores
the name as an inferred artifact ID and routes to the hidden "inferred"
command for resolution.

**Inherits from:** typer.core.TyperGroup

#### Methods

- `resolve_command(self, ctx, args) -> tuple[Tuple[<BinOp>, <BinOp>, list[str]]]`: Resolve command, falling back to ID inference for unknown names.
