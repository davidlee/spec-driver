"""Pager and editor utilities for CLI commands."""

from __future__ import annotations

from pathlib import Path

import typer


def get_pager() -> str | None:
  """Get pager command from environment or fallback.

  Resolution order: $PAGER -> less -> more

  Returns:
    Pager command string, or None if no pager available.

  """
  import os
  import shutil

  if pager := os.environ.get("PAGER"):
    return pager
  for cmd in ("less", "more"):
    if shutil.which(cmd):
      return cmd
  return None


def get_editor() -> str | None:
  """Get editor command from environment or fallback.

  Resolution order: $EDITOR -> $VISUAL -> vi

  Returns:
    Editor command string, or None if no editor available.

  """
  import os
  import shutil

  for var in ("EDITOR", "VISUAL"):
    if editor := os.environ.get(var):
      return editor
  if shutil.which("vi"):
    return "vi"
  return None


def open_in_pager(path: Path | str) -> None:
  """Open file in pager.

  Args:
    path: Path to file to open

  Raises:
    RuntimeError: If no pager is available

  """
  import subprocess

  pager = get_pager()
  if not pager:
    msg = "No pager found. Set $PAGER or install less."
    raise RuntimeError(msg)
  subprocess.run([pager, str(path)], check=True)


def render_file(path: Path | str) -> None:
  """Render markdown file to stdout without paging.

  Cascade: glow → rich → raw stdout.

  Args:
    path: Path to markdown file.

  """
  import shutil
  import subprocess

  path = Path(path)
  if shutil.which("glow"):
    subprocess.run(["glow", str(path)], check=False)
  elif shutil.which("rich"):
    subprocess.run(["rich", str(path)], check=False)
  else:
    typer.echo(path.read_text())


def render_file_paged(path: Path | str) -> None:
  """Render markdown file in a pager.

  Cascade: $PAGER → glow -p → ov → less → more.

  Args:
    path: Path to markdown file.

  Raises:
    RuntimeError: If no pager or renderer is available.

  """
  import os
  import shutil
  import subprocess

  path = Path(path)

  if pager := os.environ.get("PAGER"):
    subprocess.run([pager, str(path)], check=True)
    return
  if shutil.which("glow"):
    subprocess.run(["glow", "-p", str(path)], check=True)
    return
  for cmd in ("ov", "less", "more"):
    if shutil.which(cmd):
      subprocess.run([cmd, str(path)], check=True)
      return
  msg = "No pager found. Set $PAGER or install glow/less."
  raise RuntimeError(msg)


def open_in_editor(path: Path | str) -> None:
  """Open file in editor.

  Args:
    path: Path to file to open

  Raises:
    RuntimeError: If no editor is available

  """
  import subprocess

  editor = get_editor()
  if not editor:
    msg = "No editor found. Set $EDITOR or install vi."
    raise RuntimeError(msg)
  subprocess.run([editor, str(path)], check=True)
