"""Memory ID validation, normalization, and utilities.

Canonical form: mem.<type>.<domain>.<subject>[.<purpose>]
  - Charset per segment: [a-z0-9]+(-[a-z0-9]+)*
  - Separator: .
  - 2–7 total segments (mem + 1–6 user segments)
  - Lowercase enforced on write

Shorthand: omit mem. prefix -> prepend automatically.
"""

from __future__ import annotations

import re

# Segments: lowercase alphanumeric, hyphens allowed (not leading/trailing).
_SEGMENT_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Max total segments (mem + up to 6 user segments).
_MAX_SEGMENTS = 7


def validate_memory_id(raw: str) -> str:
  """Validate and return canonical memory ID.

  Args:
    raw: Raw ID string (must already have mem. prefix).

  Returns:
    Canonical (lowercased) memory ID.

  Raises:
    ValueError: If the ID is malformed.
  """
  if not raw or not raw.strip():
    msg = "Memory ID cannot be empty"
    raise ValueError(msg)

  canonical = raw.strip().lower()

  if not canonical.startswith("mem."):
    msg = f"Memory ID must start with 'mem.': {raw!r}"
    raise ValueError(msg)

  segments = canonical.split(".")
  if len(segments) < 2:
    msg = f"Memory ID must start with 'mem.': {raw!r}"
    raise ValueError(msg)

  if len(segments) > _MAX_SEGMENTS:
    msg = f"Memory ID has too many segments (max {_MAX_SEGMENTS}): {raw!r}"
    raise ValueError(msg)

  for i, seg in enumerate(segments):
    if not seg:
      msg = f"Memory ID has empty segment: {raw!r}"
      raise ValueError(msg)
    if i == 0:
      continue  # 'mem' prefix already validated
    if not _SEGMENT_RE.match(seg):
      msg = f"Memory ID has invalid segment {seg!r}: {raw!r}"
      raise ValueError(msg)

  return canonical


def normalize_memory_id(raw: str) -> str:
  """Normalize shorthand to canonical form.

  Prepends 'mem.' if missing, lowercases, then validates.

  Args:
    raw: Raw ID or shorthand (e.g., 'pattern.cli.skinny').

  Returns:
    Canonical memory ID.

  Raises:
    ValueError: If the resulting ID is malformed.
  """
  if not raw or not raw.strip():
    msg = "Memory ID cannot be empty"
    raise ValueError(msg)

  cleaned = raw.strip().lower()

  if not cleaned.startswith("mem."):
    cleaned = f"mem.{cleaned}"

  return validate_memory_id(cleaned)


def extract_type_from_id(memory_id: str) -> str | None:
  """Extract the type segment (second segment) from a canonical memory ID.

  Args:
    memory_id: A memory ID string.

  Returns:
    The type segment, or None if not a valid semantic memory ID.
  """
  if not memory_id.startswith("mem."):
    return None

  segments = memory_id.split(".")
  if len(segments) < 2:
    return None

  return segments[1]


def filename_from_id(memory_id: str) -> str:
  """Derive filename from canonical memory ID.

  Args:
    memory_id: Canonical memory ID (e.g., 'mem.pattern.cli.skinny').

  Returns:
    Filename string (e.g., 'mem.pattern.cli.skinny.md').
  """
  return f"{memory_id}.md"
