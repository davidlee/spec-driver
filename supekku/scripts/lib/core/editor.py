"""Legacy re-export shim — see spec_driver.core.editor."""

from spec_driver.core.editor import (
  EditorError,
  EditorInvocationError,
  EditorNotFoundError,
  find_editor,
  invoke_editor,
)

__all__ = [
  "EditorError",
  "EditorInvocationError",
  "EditorNotFoundError",
  "find_editor",
  "invoke_editor",
]
