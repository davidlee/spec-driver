# supekku.scripts.lib.memory.links

Memory link parsing and resolution.

Pure functions for extracting [[...]] wikilinks from memory body content,
resolving them against a known artifact index, and serializing results
for frontmatter storage.

Also provides graph operations: backlink computation and depth expansion.

No I/O — callers provide the body text and artifact index.

## Constants

- `_FENCE_RE` - Fenced code blocks: ``` or ~~~, optionally with language tag
- `_INLINE_CODE_RE` - Inline code: `...` or `...`
- `_LINK_RE` - Regex for [[target]] or [[target|label]]
- `_MAX_LINK_DEPTH`
- `_VALID_LINK_MODES`

## Functions

- `_normalize_link_target(target) -> str`: Normalize a parsed link target to canonical form.

Strips mem: URI scheme and applies memory ID normalization.
Recognized non-memory artifacts (SPEC-_, PROB-_, etc.) are returned as-is.
Returns the original target if normalization fails.

- `_strip_code(body) -> str`: Remove fenced code blocks and inline code from body text.

Replaces code regions with whitespace to preserve character offsets
for error reporting while preventing link extraction from code.

- `compute_backlinks(bodies) -> dict[Tuple[str, list[str]]]`: Compute reverse edges from forward links in memory bodies.

For each source memory, parses `[[...]]` links from its body and
records the source as a backlink on each target. Self-links are excluded.

Args:
bodies: Mapping of memory ID to body text.

Returns:
Dict mapping target ID to sorted list of source IDs that link to it.

- `expand_link_graph(root_id, bodies, names, types) -> list[LinkGraphNode]`: Expand outgoing link graph from a root node via BFS.

Follows `[[...]]` links in memory bodies to the given depth,
returning a flat list of discovered nodes with depth annotations.
Cycle-safe via visited set. Only expands nodes present in `bodies`.

Args:
root_id: Starting memory ID.
bodies: Mapping of memory ID to body text.
names: Mapping of memory ID to display name.
types: Mapping of memory ID to memory type.
max_depth: Maximum expansion depth (capped at 5).

Returns:
List of LinkGraphNode in BFS order (root at depth 0).

- `links_to_frontmatter(result, mode) -> dict`: Serialize link resolution result for YAML frontmatter.

Returns empty dict if no links (or if mode suppresses all output).
Sorted by id for deterministic output.

Modes:
none: Always return empty dict (suppress all link persistence).
missing: Persist only unresolved links (links.missing). Default.
compact: Persist id-only entries for resolved links + missing.
full: Persist full resolved entries (id, path, kind, label) + missing.

Args:
result: Resolution result to serialize.
mode: Link persistence mode (none/missing/compact/full).

Returns:
Dict suitable for frontmatter links field. Empty dict if no links.

- `parse_links(body) -> list[ParsedLink]`: Extract [[...]] link tokens from body text.

Skips links inside fenced code blocks and inline code.
Deduplicates by target, keeping the first occurrence's label.

Args:
body: Markdown body text.

Returns:
List of unique ParsedLink objects.

- `resolve_all_links(body) -> LinkResolutionResult`: Parse and resolve all links in a body.

Args:
body: Markdown body text.
known_artifacts: Map of id → (path, kind).
source_id: ID of the source memory record.

Returns:
LinkResolutionResult with resolved, missing, and warnings.

- `resolve_parsed_link(link) -> <BinOp>`: Resolve a single parsed link against the artifact index.

Resolution strategy: 0. Strip mem: URI scheme → canonical mem. prefix

1. Self-link check (target == source_id) → None
2. Direct lookup in known_artifacts
3. classify_artifact_id for recognized but missing artifacts
4. Memory normalization (prepend mem.) → lookup
5. Not found → MissingLink

Args:
link: Parsed link to resolve.
known_artifacts: Map of id → (path, kind).
source_id: ID of the source memory record (for self-link detection).

Returns:
ResolvedLink if found, MissingLink if not, None if self-link.

## Classes

### LinkGraphNode

A node in a link graph expansion.

### LinkResolutionResult

Aggregate result from resolving all links in a body.

### MissingLink

An unresolved link target.

### ParsedLink

A [[...]] token extracted from body text.

### ResolvedLink

A link resolved against the artifact index.
