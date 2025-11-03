"""Editor invocation utilities for interactive file editing."""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path


class EditorError(RuntimeError):
  """Base class for editor-related errors."""


class EditorNotFoundError(EditorError):
  """Raised when no suitable editor can be found."""


class EditorInvocationError(EditorError):
  """Raised when editor subprocess fails."""


def find_editor() -> str | None:
  """Find suitable editor from environment variables.

  Checks in order: $EDITOR, $VISUAL, then vi as fallback.

  Returns:
      Path to editor executable, or None if none found

  Example:
      >>> editor = find_editor()
      >>> if editor:
      ...     print(f"Using editor: {editor}")
  """
  # Try environment variables first
  for env_var in ["EDITOR", "VISUAL"]:
    editor = os.environ.get(env_var)
    if editor:
      return editor

  # Fallback to vi (universal on Unix systems)
  return "vi"


def invoke_editor(
  content: str,
  instructions: str = "",
  file_suffix: str = ".md",
) -> str | None:
  """Open content in user's editor, return edited result.

  Creates temporary file with content, opens in $EDITOR (or $VISUAL, or vi),
  waits for user to save and exit, then returns edited content.

  Args:
      content: Initial content to edit
      instructions: Optional instructions prepended as comment
      file_suffix: File extension for temp file (default: .md)

  Returns:
      Edited content string, or None if user cancelled (empty file)

  Raises:
      EditorNotFoundError: If no suitable editor found
      EditorInvocationError: If editor subprocess fails

  Example:
      >>> result = invoke_editor("Initial content", "Edit and save")
      >>> if result:
      ...     print("User edited content")
      ... else:
      ...     print("User cancelled")
  """
  editor = find_editor()
  if not editor:
    msg = "No editor found. Set $EDITOR or $VISUAL environment variable."
    raise EditorNotFoundError(msg)

  # Create temporary file with content
  try:
    with tempfile.NamedTemporaryFile(
      mode="w",
      suffix=file_suffix,
      delete=False,
      encoding="utf-8",
    ) as tmp_file:
      temp_path = Path(tmp_file.name)

      # Write instructions as comment if provided
      if instructions:
        tmp_file.write(f"# {instructions}\n\n")

      tmp_file.write(content)
      tmp_file.flush()

    # Invoke editor
    try:
      subprocess.run(
        [editor, str(temp_path)],
        check=True,
      )
    except subprocess.CalledProcessError as e:
      msg = f"Editor failed: {e}"
      raise EditorInvocationError(msg) from e
    except FileNotFoundError as e:
      msg = f"Editor not found: {editor}"
      raise EditorNotFoundError(msg) from e

    # Read back edited content
    edited_content = temp_path.read_text(encoding="utf-8")

    # Return None if user saved empty file (indicates cancellation)
    if not edited_content.strip():
      return None

    return edited_content

  finally:
    # Cleanup temp file
    if temp_path.exists():
      temp_path.unlink()
