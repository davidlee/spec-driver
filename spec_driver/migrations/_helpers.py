"""Bytes-level helpers shared across migration steps (frozen-forever, F-20).

This module is the **sole exception** to the per-step vendoring rule:
migration step modules import these three primitives rather than
re-copying them. The narrow surface enables reuse while guaranteeing
schema-version isolation — nothing here may depend on or expose any
schema concept.

Frozen-forever discipline (F-35): behaviour and signature are pinned.
Bug fixes are allowed (and required when found); behaviour/signature
changes are framework v2 work, gated by ``/scope-delta``.
"""

from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

_FRONTMATTER_DELIMITER = "---"


def split_frontmatter(text: str) -> tuple[str, str]:
  """Split markdown text into (yaml_block, body).

  Returns ``('', text)`` when no leading ``---`` delimiter pair exists.
  The leading and trailing delimiter lines are stripped from the yaml
  block. Bytes-only — does NOT parse YAML.
  """
  if not text.startswith(_FRONTMATTER_DELIMITER):
    return "", text

  remainder = text[len(_FRONTMATTER_DELIMITER) :]
  if not remainder.startswith("\n"):
    return "", text

  # Find the closing delimiter on its own line. yaml_block keeps the
  # trailing newline before the closing ``---`` so round-trip emit
  # reconstructs the original byte layout.
  body_start = remainder.find(f"\n{_FRONTMATTER_DELIMITER}\n", 1)
  if body_start == -1:
    # Maybe file ends with --- and no trailing newline.
    body_start = remainder.find(f"\n{_FRONTMATTER_DELIMITER}", 1)
    if body_start == -1:
      return "", text
    yaml_block = remainder[1 : body_start + 1]
    body = remainder[body_start + 1 + len(_FRONTMATTER_DELIMITER) :]
    return yaml_block, body

  yaml_block = remainder[1 : body_start + 1]
  body = remainder[body_start + 1 + len(_FRONTMATTER_DELIMITER) + 1 :]
  return yaml_block, body


def atomic_write(path: Path, content: str) -> None:
  """Write *content* to *path* via sibling tempfile + ``os.replace``.

  Preserves the file mode of an existing file when overwriting.
  """
  path = Path(path)
  directory = path.parent
  directory.mkdir(parents=True, exist_ok=True)

  existing_mode: int | None = None
  if path.exists():
    existing_mode = path.stat().st_mode & 0o777

  fd, tmp_name = tempfile.mkstemp(
    prefix=f".{path.name}.",
    suffix=".tmp",
    dir=str(directory),
  )
  tmp_path = Path(tmp_name)
  try:
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
      fh.write(content)
    if existing_mode is not None:
      tmp_path.chmod(existing_mode)
    tmp_path.replace(path)
  except Exception:
    if tmp_path.exists():
      tmp_path.unlink()
    raise


def replace_in_frontmatter_block(fm_text: str, key: str, new_value: str) -> str:
  """Rewrite a top-level scalar key's value while preserving surrounding text.

  Matches ``<key>: <old_value>`` at the start of a line (top-level
  only — indented child keys are ignored). The replacement preserves
  any trailing comment (``# ...``) after the value, the line's
  newline, and all other lines untouched.

  Raises ``KeyError`` when *key* is not present at the top level.
  """
  pattern = re.compile(
    rf"(?m)^(?P<prefix>{re.escape(key)}:[ \t]*)"
    r"(?P<value>(?:'[^']*'|\"[^\"]*\"|[^#\n]*?))"
    r"(?P<suffix>[ \t]*(?:#.*)?)$"
  )
  matches = list(pattern.finditer(fm_text))
  if not matches:
    raise KeyError(key)

  match = matches[0]
  start, end = match.span()
  return (
    fm_text[:start]
    + match.group("prefix")
    + new_value
    + match.group("suffix")
    + fm_text[end:]
  )
