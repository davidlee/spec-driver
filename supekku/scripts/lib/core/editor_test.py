"""Tests for editor invocation utilities."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from .editor import (
  EditorInvocationError,
  EditorNotFoundError,
  find_editor,
  invoke_editor,
)


class TestFindEditor:
  """Test find_editor function."""

  def test_uses_editor_env_var(self) -> None:
    """Test that $EDITOR is checked first."""
    with patch.dict("os.environ", {"EDITOR": "/usr/bin/nano", "VISUAL": "/usr/bin/emacs"}):  # noqa: E501
      assert find_editor() == "/usr/bin/nano"

  def test_falls_back_to_visual(self) -> None:
    """Test fallback to $VISUAL when $EDITOR not set."""
    with patch.dict("os.environ", {"VISUAL": "/usr/bin/emacs"}, clear=True):
      assert find_editor() == "/usr/bin/emacs"

  def test_falls_back_to_vi(self) -> None:
    """Test fallback to vi when no env vars set."""
    with patch.dict("os.environ", {}, clear=True):
      assert find_editor() == "vi"


class TestInvokeEditor:
  """Test invoke_editor function."""

  def test_successful_edit(self, tmp_path: Path) -> None:
    """Test successful editor invocation and content return."""
    # Mock subprocess to simulate editor saving content
    with (
      patch("supekku.scripts.lib.core.editor.find_editor") as mock_find,
      patch("supekku.scripts.lib.core.editor.subprocess.run") as mock_run,
      patch("supekku.scripts.lib.core.editor.tempfile.NamedTemporaryFile") as mock_temp,
    ):
      mock_find.return_value = "/usr/bin/vim"

      # Create actual temp file for testing
      temp_file = tmp_path / "test.md"
      temp_file.write_text("edited content\n", encoding="utf-8")

      # Mock tempfile to use our test file
      mock_file = MagicMock()
      mock_file.name = str(temp_file)
      mock_file.__enter__ = MagicMock(return_value=mock_file)
      mock_file.__exit__ = MagicMock(return_value=False)
      mock_temp.return_value = mock_file

      # Run test
      result = invoke_editor("original content")

      assert result == "edited content\n"
      mock_run.assert_called_once_with(["/usr/bin/vim", str(temp_file)], check=True)

  def test_with_instructions(self, tmp_path: Path) -> None:
    """Test that instructions are prepended to content."""
    with (
      patch("supekku.scripts.lib.core.editor.find_editor") as mock_find,
      patch("supekku.scripts.lib.core.editor.subprocess.run"),
      patch("supekku.scripts.lib.core.editor.tempfile.NamedTemporaryFile") as mock_temp,
    ):
      mock_find.return_value = "vi"

      # Capture what was written to temp file
      written_parts: list[str] = []

      def capture_write(content: str) -> None:
        written_parts.append(content)

      mock_file = MagicMock()
      mock_file.write = capture_write
      mock_file.flush = MagicMock()
      mock_file.name = str(tmp_path / "test.md")
      mock_file.__enter__ = MagicMock(return_value=mock_file)
      mock_file.__exit__ = MagicMock(return_value=False)
      mock_temp.return_value = mock_file

      # Create result file
      result_file = tmp_path / "test.md"
      result_file.write_text("result", encoding="utf-8")

      invoke_editor("content", instructions="Edit this")

      # Verify instructions were added (written in two parts)
      assert len(written_parts) == 2
      assert written_parts[0] == "# Edit this\n\n"
      assert written_parts[1] == "content"

  def test_empty_content_returns_none(self, tmp_path: Path) -> None:
    """Test that empty edited content returns None (cancellation)."""
    with (
      patch("supekku.scripts.lib.core.editor.find_editor") as mock_find,
      patch("supekku.scripts.lib.core.editor.subprocess.run"),
      patch("supekku.scripts.lib.core.editor.tempfile.NamedTemporaryFile") as mock_temp,
    ):
      mock_find.return_value = "vi"

      # Create empty temp file
      temp_file = tmp_path / "test.md"
      temp_file.write_text("", encoding="utf-8")

      mock_file = MagicMock()
      mock_file.name = str(temp_file)
      mock_file.__enter__ = MagicMock(return_value=mock_file)
      mock_file.__exit__ = MagicMock(return_value=False)
      mock_temp.return_value = mock_file

      result = invoke_editor("content")

      assert result is None

  def test_whitespace_only_returns_none(self, tmp_path: Path) -> None:
    """Test that whitespace-only content returns None."""
    with (
      patch("supekku.scripts.lib.core.editor.find_editor") as mock_find,
      patch("supekku.scripts.lib.core.editor.subprocess.run"),
      patch("supekku.scripts.lib.core.editor.tempfile.NamedTemporaryFile") as mock_temp,
    ):
      mock_find.return_value = "vi"

      temp_file = tmp_path / "test.md"
      temp_file.write_text("   \n\n  \t  \n", encoding="utf-8")

      mock_file = MagicMock()
      mock_file.name = str(temp_file)
      mock_file.__enter__ = MagicMock(return_value=mock_file)
      mock_file.__exit__ = MagicMock(return_value=False)
      mock_temp.return_value = mock_file

      result = invoke_editor("content")

      assert result is None

  def test_editor_not_found_raises(self) -> None:
    """Test that missing editor raises EditorNotFoundError."""
    with patch("supekku.scripts.lib.core.editor.find_editor") as mock_find:
      mock_find.return_value = None

      with pytest.raises(EditorNotFoundError, match="No editor found"):
        invoke_editor("content")

  def test_subprocess_failure_raises(self, tmp_path: Path) -> None:
    """Test that subprocess failure raises EditorInvocationError."""
    with (
      patch("supekku.scripts.lib.core.editor.find_editor") as mock_find,
      patch("supekku.scripts.lib.core.editor.subprocess.run") as mock_run,
      patch("supekku.scripts.lib.core.editor.tempfile.NamedTemporaryFile") as mock_temp,
    ):
      mock_find.return_value = "vim"
      mock_run.side_effect = subprocess.CalledProcessError(1, ["vim"])

      temp_file = tmp_path / "test.md"
      mock_file = MagicMock()
      mock_file.name = str(temp_file)
      mock_file.__enter__ = MagicMock(return_value=mock_file)
      mock_file.__exit__ = MagicMock(return_value=False)
      mock_temp.return_value = mock_file

      with pytest.raises(EditorInvocationError, match="Editor failed"):
        invoke_editor("content")

  def test_editor_executable_not_found_raises(self, tmp_path: Path) -> None:
    """Test that missing editor executable raises EditorNotFoundError."""
    with (
      patch("supekku.scripts.lib.core.editor.find_editor") as mock_find,
      patch("supekku.scripts.lib.core.editor.subprocess.run") as mock_run,
      patch("supekku.scripts.lib.core.editor.tempfile.NamedTemporaryFile") as mock_temp,
    ):
      mock_find.return_value = "/nonexistent/editor"
      mock_run.side_effect = FileNotFoundError("editor not found")

      temp_file = tmp_path / "test.md"
      mock_file = MagicMock()
      mock_file.name = str(temp_file)
      mock_file.__enter__ = MagicMock(return_value=mock_file)
      mock_file.__exit__ = MagicMock(return_value=False)
      mock_temp.return_value = mock_file

      with pytest.raises(EditorNotFoundError, match="Editor not found"):
        invoke_editor("content")

  def test_custom_suffix(self, tmp_path: Path) -> None:
    """Test that custom file suffix is used."""
    with (
      patch("supekku.scripts.lib.core.editor.find_editor") as mock_find,
      patch("supekku.scripts.lib.core.editor.subprocess.run"),
      patch("supekku.scripts.lib.core.editor.tempfile.NamedTemporaryFile") as mock_temp,
    ):
      mock_find.return_value = "vi"

      temp_file = tmp_path / "test.txt"
      temp_file.write_text("content", encoding="utf-8")

      mock_file = MagicMock()
      mock_file.name = str(temp_file)
      mock_file.__enter__ = MagicMock(return_value=mock_file)
      mock_file.__exit__ = MagicMock(return_value=False)
      mock_temp.return_value = mock_file

      invoke_editor("content", file_suffix=".txt")

      # Verify suffix was passed to tempfile
      mock_temp.assert_called_once()
      call_kwargs = mock_temp.call_args[1]
      assert call_kwargs["suffix"] == ".txt"
