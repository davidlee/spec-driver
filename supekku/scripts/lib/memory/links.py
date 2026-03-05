"""Memory link parsing and resolution.

Pure functions for extracting [[...]] wikilinks from memory body content,
resolving them against a known artifact index, and serializing results
for frontmatter storage.

Also provides graph operations: backlink computation and depth expansion.

No I/O — callers provide the body text and artifact index.
"""

from __future__ import annotations

import re
from collections import defaultdict, deque
from dataclasses import dataclass, field

from supekku.scripts.lib.core.artifact_ids import classify_artifact_id
from supekku.scripts.lib.memory.ids import normalize_memory_id

# Regex for [[target]] or [[target|label]]
_LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")

# Fenced code blocks: ``` or ~~~, optionally with language tag
_FENCE_RE = re.compile(r"^(`{3,}|~{3,}).*$", re.MULTILINE)

# Inline code: `...` or ``...``
_INLINE_CODE_RE = re.compile(r"`{1,2}[^`]+`{1,2}")


# ── Data types ───────────────────────────────────────────────


@dataclass(frozen=True)
class ParsedLink:
  """A [[...]] token extracted from body text."""

  raw: str
  target: str
  label: str | None = None


@dataclass(frozen=True)
class ResolvedLink:
  """A link resolved against the artifact index."""

  id: str
  path: str
  label: str | None = None
  kind: str = ""


@dataclass(frozen=True)
class MissingLink:
  """An unresolved link target."""

  raw: str


@dataclass
class LinkResolutionResult:
  """Aggregate result from resolving all links in a body."""

  out: list[ResolvedLink] = field(default_factory=list)
  missing: list[MissingLink] = field(default_factory=list)
  warnings: list[str] = field(default_factory=list)


# ── Parser ───────────────────────────────────────────────────


def _strip_code(body: str) -> str:
  """Remove fenced code blocks and inline code from body text.

  Replaces code regions with whitespace to preserve character offsets
  for error reporting while preventing link extraction from code.
  """
  result = body

  # Strip fenced code blocks (``` ... ``` or ~~~ ... ~~~)
  fence_positions = list(_FENCE_RE.finditer(result))
  ranges_to_blank: list[tuple[int, int]] = []
  i = 0
  while i < len(fence_positions):
    opener = fence_positions[i]
    fence_char = opener.group(1)[0]  # ` or ~
    fence_len = len(opener.group(1))
    # Find matching closer
    for j in range(i + 1, len(fence_positions)):
      closer = fence_positions[j]
      closer_char = closer.group(1)[0]
      closer_len = len(closer.group(1))
      if closer_char == fence_char and closer_len >= fence_len:
        ranges_to_blank.append((opener.start(), closer.end()))
        i = j + 1
        break
    else:
      # No closer found — blank from opener to end
      ranges_to_blank.append((opener.start(), len(result)))
      break
    continue

  # Blank fenced ranges (reverse to preserve indices)
  for start, end in reversed(ranges_to_blank):
    result = result[:start] + " " * (end - start) + result[end:]

  # Strip inline code
  return _INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), result)


def parse_links(body: str) -> list[ParsedLink]:
  """Extract [[...]] link tokens from body text.

  Skips links inside fenced code blocks and inline code.
  Deduplicates by target, keeping the first occurrence's label.

  Args:
    body: Markdown body text.

  Returns:
    List of unique ParsedLink objects.
  """
  if not body:
    return []

  stripped = _strip_code(body)
  seen: dict[str, ParsedLink] = {}

  for match in _LINK_RE.finditer(stripped):
    raw = match.group(1)
    # Split on first | for label
    if "|" in raw:
      target_part, label_part = raw.split("|", 1)
      target = target_part.strip()
      label: str | None = label_part.strip()
    else:
      target = raw.strip()
      label = None

    # Skip empty targets
    if not target:
      continue

    if target not in seen:
      seen[target] = ParsedLink(raw=raw.strip(), target=target, label=label)

  return list(seen.values())


# ── Resolver ─────────────────────────────────────────────────


def resolve_parsed_link(
  link: ParsedLink,
  *,
  known_artifacts: dict[str, tuple[str, str]],
  source_id: str,
) -> ResolvedLink | MissingLink | None:
  """Resolve a single parsed link against the artifact index.

  Resolution strategy:
    0. Strip mem: URI scheme → canonical mem. prefix
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
  """
  target = link.target

  # Strip mem: URI scheme → canonical mem. prefix
  if target.startswith("mem:"):
    target = "mem." + target[4:]

  # Self-link: exact match
  if target == source_id:
    return None

  # Direct lookup
  if target in known_artifacts:
    path, kind = known_artifacts[target]
    return ResolvedLink(id=target, path=path, label=link.label, kind=kind)

  # Recognized artifact ID but not in index → missing
  if classify_artifact_id(target) is not None:
    return MissingLink(raw=target)

  # Try memory normalization (shorthand → mem.prefix)
  try:
    normalized = normalize_memory_id(target)
  except ValueError:
    return MissingLink(raw=target)

  # Self-link via normalized form
  if normalized == source_id:
    return None

  # Lookup normalized
  if normalized in known_artifacts:
    path, kind = known_artifacts[normalized]
    return ResolvedLink(id=normalized, path=path, label=link.label, kind=kind)

  return MissingLink(raw=target)


def resolve_all_links(
  body: str,
  *,
  known_artifacts: dict[str, tuple[str, str]],
  source_id: str,
) -> LinkResolutionResult:
  """Parse and resolve all links in a body.

  Args:
    body: Markdown body text.
    known_artifacts: Map of id → (path, kind).
    source_id: ID of the source memory record.

  Returns:
    LinkResolutionResult with resolved, missing, and warnings.
  """
  result = LinkResolutionResult()
  links = parse_links(body)

  for link in links:
    resolved = resolve_parsed_link(
      link,
      known_artifacts=known_artifacts,
      source_id=source_id,
    )
    if resolved is None:
      result.warnings.append(f"Self-link skipped: [[{link.target}]]")
    elif isinstance(resolved, ResolvedLink):
      result.out.append(resolved)
    elif isinstance(resolved, MissingLink):
      result.missing.append(resolved)

  return result


# ── Serialization ────────────────────────────────────────────


_VALID_LINK_MODES = frozenset({"none", "missing", "compact", "full"})


def links_to_frontmatter(
  result: LinkResolutionResult,
  mode: str = "missing",
) -> dict:
  """Serialize link resolution result for YAML frontmatter.

  Returns empty dict if no links (or if mode suppresses all output).
  Sorted by id for deterministic output.

  Modes:
    none:    Always return empty dict (suppress all link persistence).
    missing: Persist only unresolved links (links.missing). Default.
    compact: Persist id-only entries for resolved links + missing.
    full:    Persist full resolved entries (id, path, kind, label)
             + missing.

  Args:
    result: Resolution result to serialize.
    mode: Link persistence mode (none/missing/compact/full).

  Returns:
    Dict suitable for frontmatter links field. Empty dict if no links.
  """
  if mode not in _VALID_LINK_MODES:
    msg = f"Invalid link mode: {mode!r}"
    raise ValueError(msg)

  if mode == "none":
    return {}

  if not result.out and not result.missing:
    return {}

  data: dict = {}

  if result.out and mode in ("compact", "full"):
    entries = sorted(result.out, key=lambda r: r.id)
    if mode == "compact":
      data["out"] = [{"id": e.id} for e in entries]
    else:
      out_list = []
      for entry in entries:
        item: dict = {
          "id": entry.id,
          "path": entry.path,
          "kind": entry.kind,
        }
        if entry.label:
          item["label"] = entry.label
        out_list.append(item)
      data["out"] = out_list

  if result.missing:
    data["missing"] = [{"raw": m.raw} for m in result.missing]

  return data


# ── Graph operations ──────────────────────────────────────────


@dataclass(frozen=True)
class LinkGraphNode:
  """A node in a link graph expansion."""

  id: str
  name: str
  depth: int
  memory_type: str = ""


_MAX_LINK_DEPTH = 5


def _normalize_link_target(target: str) -> str:
  """Normalize a parsed link target to canonical form.

  Strips mem: URI scheme and applies memory ID normalization.
  Recognized non-memory artifacts (SPEC-*, PROB-*, etc.) are returned as-is.
  Returns the original target if normalization fails.
  """
  t = target
  if t.startswith("mem:"):
    t = "mem." + t[4:]

  # Recognized non-memory artifact — return as-is
  if classify_artifact_id(t) is not None:
    return t

  try:
    return normalize_memory_id(t)
  except ValueError:
    return t


def compute_backlinks(bodies: dict[str, str]) -> dict[str, list[str]]:
  """Compute reverse edges from forward links in memory bodies.

  For each source memory, parses ``[[...]]`` links from its body and
  records the source as a backlink on each target. Self-links are excluded.

  Args:
    bodies: Mapping of memory ID to body text.

  Returns:
    Dict mapping target ID to sorted list of source IDs that link to it.
  """
  backlinks: dict[str, list[str]] = defaultdict(list)

  for source_id, body in bodies.items():
    links = parse_links(body)
    for link in links:
      target = _normalize_link_target(link.target)
      if target != source_id:
        backlinks[target].append(source_id)

  return {k: sorted(v) for k, v in backlinks.items()}


def expand_link_graph(
  root_id: str,
  bodies: dict[str, str],
  names: dict[str, str],
  types: dict[str, str],
  *,
  max_depth: int = 1,
) -> list[LinkGraphNode]:
  """Expand outgoing link graph from a root node via BFS.

  Follows ``[[...]]`` links in memory bodies to the given depth,
  returning a flat list of discovered nodes with depth annotations.
  Cycle-safe via visited set. Only expands nodes present in ``bodies``.

  Args:
    root_id: Starting memory ID.
    bodies: Mapping of memory ID to body text.
    names: Mapping of memory ID to display name.
    types: Mapping of memory ID to memory type.
    max_depth: Maximum expansion depth (capped at 5).

  Returns:
    List of LinkGraphNode in BFS order (root at depth 0).
  """
  max_depth = min(max_depth, _MAX_LINK_DEPTH)

  root_name = names.get(root_id, root_id)
  root_type = types.get(root_id, "")
  result: list[LinkGraphNode] = [
    LinkGraphNode(id=root_id, name=root_name, depth=0, memory_type=root_type),
  ]

  if max_depth == 0:
    return result

  visited: set[str] = {root_id}
  queue: deque[tuple[str, int]] = deque([(root_id, 0)])

  while queue:
    current_id, current_depth = queue.popleft()
    if current_depth >= max_depth:
      continue

    body = bodies.get(current_id, "")
    if not body:
      continue

    links = parse_links(body)
    for link in links:
      target = _normalize_link_target(link.target)
      if target in visited:
        continue
      visited.add(target)

      # Only expand nodes we have bodies for (known memories)
      target_name = names.get(target, target)
      target_type = types.get(target, "")
      node = LinkGraphNode(
        id=target,
        name=target_name,
        depth=current_depth + 1,
        memory_type=target_type,
      )
      result.append(node)

      if target in bodies:
        queue.append((target, current_depth + 1))

  return result
