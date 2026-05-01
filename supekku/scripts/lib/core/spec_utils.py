"""Utilities for working with specification files and frontmatter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
  import yaml
except ImportError as exc:
  msg = "PyYAML is required for spec tooling. Install with `pip install PyYAML`."
  raise SystemExit(
    msg,
  ) from exc

try:
  import frontmatter
except ImportError as exc:
  msg = (
    "python-frontmatter is required for spec tooling. Install with "
    "`pip install python-frontmatter`."
  )
  raise SystemExit(
    msg,
  ) from exc

from .frontmatter_schema import (
  FrontmatterValidationResult,
  validate_frontmatter,
)


class MarkdownLoadError(ValueError):
  """Raised when a markdown file's frontmatter cannot be parsed."""


def load_markdown_file(path: Path | str) -> tuple[dict[str, Any], str]:
  """Load markdown file and extract frontmatter and content.

  Raises:
    MarkdownLoadError: if the file's YAML frontmatter cannot be parsed.
      The original ``yaml.YAMLError`` is chained via ``__cause__``.
  """
  path = Path(path)
  text = path.read_text(encoding="utf-8")
  try:
    post = frontmatter.loads(text)
  except yaml.YAMLError as exc:
    mark = getattr(exc, "problem_mark", None)
    where = (
      f" at line {mark.line + 1}, column {mark.column + 1}" if mark is not None else ""
    )
    detail = f"invalid YAML frontmatter in {path}{where}: {exc.__class__.__name__}"
    raise MarkdownLoadError(detail) from exc
  frontmatter_data: dict[str, Any] = dict(post.metadata or {})
  body = post.content.lstrip("\n")
  if body and text.endswith("\n") and not body.endswith("\n"):
    body = body + "\n"
  return frontmatter_data, body


def dump_markdown_file(
  path: Path | str,
  frontmatter: dict[str, Any],
  body: str,
) -> None:
  """Write frontmatter and content to a markdown file."""
  from .frontmatter_writer import dump_frontmatter_yaml  # noqa: PLC0415

  path = Path(path)
  frontmatter_yaml = dump_frontmatter_yaml(frontmatter)
  body = body.lstrip("\n")
  if body and not body.endswith("\n"):
    body = body + "\n"
  combined = f"---\n{frontmatter_yaml}\n---\n\n{body}"
  path.write_text(combined, encoding="utf-8")


def ensure_list_entry(frontmatter: dict[str, Any], key: str) -> list[Any]:
  """Ensure a frontmatter key contains a list value."""
  value = frontmatter.setdefault(key, [])
  if not isinstance(value, list):
    msg = f"frontmatter[{key!r}] expected list, got {type(value).__name__}"
    raise TypeError(
      msg,
    )
  return value


def append_unique(values: list[Any], item: Any) -> bool:
  """Append item to list if not already present, return True if added."""
  if item in values:
    return False
  values.append(item)
  return True


def extract_h1_title(content: str, prefix: str = "") -> str:
  """Extract the first H1 heading from markdown content.

  Scans lines for the first that starts with ``# {prefix}`` (when a prefix is
  given) or any ``# `` heading (when no prefix is given).  Returns the full
  heading line (stripped) on match, or an empty string if none is found.

  The H1 text includes the ``# `` sigil.  Callers that only need the bare
  title text should strip it themselves.

  Args:
    content: Markdown body to scan.
    prefix: Optional prefix that must follow the ``# `` sigil.

  Returns:
    The first matching H1 line (stripped), or ``""`` if not found.
  """
  search = f"# {prefix}" if prefix else "# "
  for line in content.split("\n"):
    stripped = line.strip()
    if stripped.startswith(search):
      return stripped
  return ""


def load_validated_markdown_file(
  path: Path | str,
  *,
  kind: str | None = None,
) -> tuple[FrontmatterValidationResult, str]:
  """Load a markdown file and validate its frontmatter against the schema.

  Raises FrontmatterValidationError if validation fails.
  """
  frontmatter, body = load_markdown_file(path)
  result = validate_frontmatter(frontmatter, kind=kind)
  return result, body
