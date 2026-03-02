"""Memory selection — scope matching, specificity scoring, and path normalization.

Pure functions for deterministic filtering and ordering of memory records.
Implements MEM-FR-003 per JAMMS §5 and design-phase-04-selection.md.
"""

from __future__ import annotations

import contextlib
import fnmatch
import shlex
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from supekku.scripts.lib.memory.models import MemoryRecord


@dataclass
class MatchContext:
  """Caller's current context for scope matching.

  Attributes:
    paths: Changed/target files (repo-relative, POSIX-normalized).
    command: Command being run (e.g. "test auth --verbose").
    tags: Explicit tags for scope matching.
  """

  paths: list[str] = field(default_factory=list)
  command: str | None = None
  tags: list[str] = field(default_factory=list)


def normalize_path(
  path: str, *, repo_root: PurePosixPath | None = None,
) -> str:
  """Normalize a path to repo-relative POSIX form.

  Rules:
    - Strip leading './'
    - Resolve '..' segments
    - Preserve trailing '/' (directory marker)
    - Make absolute paths relative to repo_root if provided
    - Collapse double slashes

  Args:
    path: Raw path string.
    repo_root: If provided, absolute paths are relative to this root.

  Returns:
    Normalized repo-relative POSIX path string.
  """
  if not path:
    return "."

  trailing_slash = path.endswith("/") and path != "/"

  # Make absolute paths relative to repo_root
  if repo_root and PurePosixPath(path).is_absolute():
    with contextlib.suppress(ValueError):
      path = str(PurePosixPath(path).relative_to(repo_root))

  # Resolve .. and . via segment processing
  parts = PurePosixPath(path).parts
  if parts and parts[0] == ".":
    parts = parts[1:]

  resolved: list[str] = []
  for part in parts:
    if part == "..":
      if resolved:
        resolved.pop()
    else:
      resolved.append(part)

  result = "/".join(resolved) if resolved else "."

  if trailing_slash and result != ".":
    result += "/"

  return result


def _matches_paths(
  scope_paths: list[str], context_paths: list[str],
) -> bool:
  """Check if any context path matches any scope path (exact or prefix)."""
  for scope_path in scope_paths:
    if scope_path.endswith("/"):
      for ctx_path in context_paths:
        if (
          ctx_path.startswith(scope_path)
          or ctx_path == scope_path.rstrip("/")
        ):
          return True
    elif scope_path in context_paths:
      return True
  return False


def _glob_match(path: str, pattern: str) -> bool:
  """Match a path against a glob pattern with proper ** support.

  Splits both path and pattern by '/' and matches segment-by-segment:
    - '*' matches any single segment (via fnmatch)
    - '**' matches zero or more segments
    - Other segments matched via fnmatch (supporting *, ?, [seq])
  """
  return _match_segments(path.split("/"), 0, pattern.split("/"), 0)


def _match_segments(
  path_parts: list[str], pi: int,
  pat_parts: list[str], gi: int,
) -> bool:
  """Recursive segment matcher for glob patterns."""
  while pi < len(path_parts) and gi < len(pat_parts):
    if pat_parts[gi] == "**":
      # ** matches zero or more segments
      for skip in range(pi, len(path_parts) + 1):
        if _match_segments(path_parts, skip, pat_parts, gi + 1):
          return True
      return False
    if not fnmatch.fnmatchcase(path_parts[pi], pat_parts[gi]):
      return False
    pi += 1
    gi += 1

  # Consume trailing ** patterns
  while gi < len(pat_parts) and pat_parts[gi] == "**":
    gi += 1

  return pi == len(path_parts) and gi == len(pat_parts)


def _matches_globs(
  scope_globs: list[str], context_paths: list[str],
) -> bool:
  """Check if any context path matches any scope glob pattern."""
  return any(
    _glob_match(ctx_path, glob_pattern)
    for glob_pattern in scope_globs
    for ctx_path in context_paths
  )


def _tokenize_command(command: str) -> list[str]:
  """Split a command into tokens, falling back to whitespace split."""
  try:
    return shlex.split(command)
  except ValueError:
    return command.split()


def _matches_commands(
  scope_commands: list[str], context_command: str,
) -> bool:
  """Check if scope command tokens are a prefix of context command tokens."""
  ctx_tokens = _tokenize_command(context_command)
  for scope_cmd in scope_commands:
    scope_tokens = _tokenize_command(scope_cmd)
    if (
      scope_tokens
      and len(scope_tokens) <= len(ctx_tokens)
      and ctx_tokens[:len(scope_tokens)] == scope_tokens
    ):
      return True
  return False


def matches_scope(record: MemoryRecord, context: MatchContext) -> bool:
  """Check if a record's scope matches the given context.

  OR logic across dimensions. A dimension only participates if the
  context provides input for it.

  Args:
    record: Memory record to check.
    context: Caller's current context.

  Returns:
    True if any active dimension matches.
  """
  scope = record.scope

  scope_paths = scope.get("paths", [])
  if (
    scope_paths and context.paths
    and _matches_paths(scope_paths, context.paths)
  ):
    return True

  scope_globs = scope.get("globs", [])
  if (
    scope_globs and context.paths
    and _matches_globs(scope_globs, context.paths)
  ):
    return True

  scope_commands = scope.get("commands", [])
  if (
    scope_commands and context.command
    and _matches_commands(scope_commands, context.command)
  ):
    return True

  return bool(
    context.tags and record.tags
    and set(context.tags) & set(record.tags)
  )


def scope_specificity(
  record: MemoryRecord, context: MatchContext,
) -> int:
  """Score how specific the scope match is.

  Returns the MAX specificity across matched dimensions:
    3 = matched via scope.paths (exact or prefix)
    2 = matched via scope.globs
    1 = matched via scope.commands
    0 = matched via tags only / no match / no context

  Args:
    record: Memory record to score.
    context: Caller's current context.

  Returns:
    Integer specificity score (0-3).
  """
  score = 0
  scope = record.scope

  scope_paths = scope.get("paths", [])
  if (
    scope_paths and context.paths
    and _matches_paths(scope_paths, context.paths)
  ):
    score = max(score, 3)

  scope_globs = scope.get("globs", [])
  if (
    scope_globs and context.paths
    and _matches_globs(scope_globs, context.paths)
  ):
    score = max(score, 2)

  scope_commands = scope.get("commands", [])
  if (
    scope_commands and context.command
    and _matches_commands(scope_commands, context.command)
  ):
    score = max(score, 1)

  return score


_SEVERITY_RANK: dict[str, int] = {
  "critical": 0,
  "high": 1,
  "medium": 2,
  "low": 3,
  "none": 4,
}
_SEVERITY_DEFAULT = 4
_VERIFIED_NULL_RANK = 999999

_EXCLUDED_STATUSES = frozenset({"deprecated", "superseded", "obsolete"})


def sort_key(
  record: MemoryRecord,
  context: MatchContext | None = None,
  *,
  today: date | None = None,
) -> tuple[int, int, int, int, str]:
  """Build a deterministic sort key for a memory record.

  5-level key per JAMMS §5.4:
    1. severity rank (critical=0 → none=4)
    2. -weight (higher weight sorts first)
    3. -specificity (more specific scope sorts first)
    4. verified recency (fewer days since = better; null = last)
    5. id (lexicographic)

  Args:
    record: Memory record to build key for.
    context: Optional match context for specificity scoring.
    today: Reference date for recency; defaults to date.today().

  Returns:
    5-tuple usable as a sort key.
  """
  priority = record.priority
  severity = priority.get("severity", "none") if priority else "none"
  severity_rank = _SEVERITY_RANK.get(severity, _SEVERITY_DEFAULT)

  weight = priority.get("weight", 0) if priority else 0

  specificity = (
    scope_specificity(record, context) if context else 0
  )

  if record.verified:
    ref = today or date.today()
    verified_days = (ref - record.verified).days
  else:
    verified_days = _VERIFIED_NULL_RANK

  return (severity_rank, -weight, -specificity, verified_days, record.id)


def is_surfaceable(
  record: MemoryRecord,
  context: MatchContext | None = None,
  *,
  include_draft: bool = False,
  skip_status_filter: bool = False,
  thread_recency_days: int = 14,
  today: date | None = None,
) -> bool:
  """Check whether a record should be surfaced.

  Excludes (unless skip_status_filter):
    - status in {deprecated, superseded, obsolete}
    - draft unless include_draft
  Always checks:
    - thread: requires scope-matched to context AND recently verified

  Args:
    record: Memory record to check.
    context: Optional match context for thread evaluation.
    include_draft: Whether to include draft records.
    skip_status_filter: Skip status-based exclusions (when caller
      has already pre-filtered by explicit --status).
    thread_recency_days: Max days since verified for thread inclusion.
    today: Reference date; defaults to date.today().

  Returns:
    True if the record should be surfaced.
  """
  if not skip_status_filter:
    if record.status in _EXCLUDED_STATUSES:
      return False
    if record.status == "draft" and not include_draft:
      return False

  if record.memory_type == "thread":
    return _is_thread_surfaceable(
      record, context,
      recency_days=thread_recency_days, today=today,
    )

  return True


def _is_thread_surfaceable(
  record: MemoryRecord,
  context: MatchContext | None,
  *,
  recency_days: int,
  today: date | None,
) -> bool:
  """Check if a thread record should be surfaced.

  Threads require: context provided, scope matches, and recently verified.
  """
  if not context:
    return False
  if not matches_scope(record, context):
    return False
  if not record.verified:
    return False

  ref = today or date.today()
  return (ref - record.verified).days <= recency_days


def select(
  records: Iterable[MemoryRecord],
  context: MatchContext | None = None,
  *,
  include_draft: bool = False,
  skip_status_filter: bool = False,
  thread_recency_days: int = 14,
  limit: int | None = None,
  today: date | None = None,
) -> list[MemoryRecord]:
  """Filter, match, and order memory records deterministically.

  Pipeline:
    1. Filter by is_surfaceable (status, draft, thread rules)
    2. If context provided, filter non-threads by matches_scope
    3. Sort by sort_key
    4. Apply limit

  Args:
    records: Input memory records.
    context: Optional match context for scope filtering.
    include_draft: Whether to include draft records.
    skip_status_filter: Skip status-based exclusions (when caller
      has already pre-filtered by explicit --status).
    thread_recency_days: Max days since verified for thread inclusion.
    limit: Maximum number of results (None = unlimited).
    today: Reference date; defaults to date.today().

  Returns:
    Sorted list of matching memory records.
  """
  ref_today = today or date.today()

  # Step 1: surfaceability filter
  surfaceable = [
    r for r in records
    if is_surfaceable(
      r, context,
      include_draft=include_draft,
      skip_status_filter=skip_status_filter,
      thread_recency_days=thread_recency_days,
      today=ref_today,
    )
  ]

  # Step 2: scope filter (if context provided)
  if context:
    matched = [
      r for r in surfaceable
      if r.memory_type == "thread" or matches_scope(r, context)
    ]
  else:
    matched = surfaceable

  # Step 3: deterministic sort
  matched.sort(key=lambda r: sort_key(r, context, today=ref_today))

  # Step 4: limit
  if limit is not None:
    matched = matched[:limit]

  return matched
