"""Utilities for working with specification files and frontmatter.

`dump_markdown_file_create(..., kind=)` and `dump_markdown_file_update(...)`
are the canonical write helpers (DEC-137-15 / F-1):

- `_create` builds frontmatter via `render_frontmatter_for_kind(kind, data=fm)`
  so enum-comment hints appear inline. Errors if the path already exists.
- `_update` rewrites an existing artefact, preserving trailing `# ...`
  comments per top-level scalar key.

The legacy `dump_markdown_file(path, fm, body)` survives temporarily as a
thin alias of `_update` so the ~33 production + ~95 test ripple sites can
migrate in batches; the alias is removed once `rg dump_markdown_file\\b`
reports zero remaining callers (IP-137-P02 task 2.9).
"""

from __future__ import annotations

import re
from collections.abc import Mapping
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


def _normalise_body(body: str) -> str:
  body = body.lstrip("\n")
  if body and not body.endswith("\n"):
    body = body + "\n"
  return body


def _atomic_write(path: Path, text: str) -> None:
  tmp = path.with_suffix(path.suffix + ".tmp")
  tmp.write_text(text, encoding="utf-8")
  tmp.replace(path)


_TRAILING_COMMENT_RE = re.compile(
  r"^(?P<key>[A-Za-z_][\w-]*):\s+\S.*?\s+#\s*(?P<comment>.*?)\s*$",
)


def _extract_inline_comments(fm_text: str) -> dict[str, str]:
  """Return `{top_level_key: comment_text}` for `key: value  # comment` lines.

  Only top-level scalar lines participate. Container-opening lines (`key:`
  followed by nothing on the same line, or `key: [item, ...]`) and comment-
  only lines do not contribute to the map.
  """
  comments: dict[str, str] = {}
  for line in fm_text.splitlines():
    if not line or line.lstrip().startswith("#"):
      continue
    match = _TRAILING_COMMENT_RE.match(line)
    if match:
      comments[match.group("key")] = match.group("comment")
  return comments


def _read_existing_frontmatter_text(path: Path) -> str:
  text = path.read_text(encoding="utf-8")
  if not text.startswith("---"):
    return ""
  end_idx = text.find("\n---", 3)
  if end_idx == -1:
    return ""
  return text[3:end_idx].lstrip("\n").rstrip()


def dump_markdown_file_create(
  path: Path | str,
  frontmatter: Mapping[str, Any],
  body: str,
  *,
  kind: str,
) -> None:
  """Write a NEW artefact at *path*, rendering frontmatter with enum hints.

  Routes through `render_frontmatter_for_kind(kind, data=frontmatter)` so
  enum-comment hints appear inline (POL-001). For kinds without a registered
  metadata entry (e.g. spec testing companions, improvement backlog items)
  falls through to plain `emit_yaml_block` — no hints, but still atomic and
  consistent with the rest of the create path. Errors if *path* already
  exists.
  """
  from spec_driver.core.yaml_emit import emit_yaml_block  # noqa: PLC0415
  from spec_driver.orchestration.templates import (  # noqa: PLC0415
    UnknownKindError,
    render_frontmatter_for_kind,
  )

  path = Path(path)
  if path.exists():
    msg = f"refusing to overwrite existing artefact: {path} (use _update)"
    raise FileExistsError(msg)
  try:
    fm_yaml = render_frontmatter_for_kind(kind, data=dict(frontmatter))
  except UnknownKindError:
    fm_yaml = emit_yaml_block(dict(frontmatter))
  combined = f"---\n{fm_yaml}\n---\n\n{_normalise_body(body)}"
  _atomic_write(path, combined)


def dump_markdown_file_update(
  path: Path | str,
  frontmatter: Mapping[str, Any],
  body: str,
) -> None:
  """Rewrite an EXISTING artefact at *path*, preserving inline frontmatter comments.

  Reads the existing frontmatter region, lexes trailing `# ...` annotations per
  top-level scalar key, and re-emits via `emit_yaml_block` with that preserved
  map. Atomic (temp + rename). No kind awareness — comment hints come from the
  existing file, not metadata.
  """
  from spec_driver.core.yaml_emit import emit_yaml_block  # noqa: PLC0415

  path = Path(path)
  existing_fm_text = _read_existing_frontmatter_text(path) if path.exists() else ""
  comments = _extract_inline_comments(existing_fm_text) if existing_fm_text else {}
  fm_yaml = emit_yaml_block(dict(frontmatter), comments=comments)
  combined = f"---\n{fm_yaml}\n---\n\n{_normalise_body(body)}"
  _atomic_write(path, combined)


def dump_markdown_file(
  path: Path | str,
  frontmatter: dict[str, Any],
  body: str,
) -> None:
  """DEPRECATED legacy alias of `dump_markdown_file_update`.

  Retained temporarily during IP-137-P02 ripple migration. Removed at task 2.9
  once `rg dump_markdown_file\\b` reports zero remaining callers
  (DEC-137-15 / F-1; no permanent shim).
  """
  dump_markdown_file_update(path, frontmatter, body)


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
