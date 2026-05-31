"""Shared file I/O utilities."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


def atomic_write(path: Path, content: str) -> Path:
  """Write content atomically via temp-file + rename.

  Creates the parent directory if it does not exist.  Writes to a temporary
  file in the same directory (same filesystem), then renames it into place so
  readers always see either the old or the new file — never a partially-written
  one.

  Args:
    path: Destination file path.
    content: Text content to write (UTF-8 encoded).

  Returns:
    The destination path.

  Raises:
    OSError: If the write or rename fails.
  """
  path.parent.mkdir(parents=True, exist_ok=True)
  fd, tmp = tempfile.mkstemp(
    dir=path.parent,
    suffix=".tmp",
    prefix=path.stem + "_",
  )
  closed = False
  try:
    os.write(fd, content.encode("utf-8"))
    os.close(fd)
    closed = True
    Path(tmp).replace(path)
  except BaseException:
    if not closed:
      os.close(fd)
    tmp_path = Path(tmp)
    if tmp_path.exists():
      tmp_path.unlink()
    raise
  return path


__all__ = ["atomic_write"]
