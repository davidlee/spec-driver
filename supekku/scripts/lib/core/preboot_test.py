"""Tests for preboot context generation."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

import pytest

from supekku.scripts.lib.core.preboot import (
  BOOT_SEQUENCE,
  GENERATED_HEADER,
  GOVERNANCE_LISTINGS,
  PI_OUTPUT_DIR,
  PI_OUTPUT_FILE,
  PREBOOT_OUTPUT_DIR,
  PREBOOT_OUTPUT_FILE,
  generate_preboot_content,
  write_preboot_file,
)

_SUBPROCESS_TARGET = "supekku.scripts.lib.core.preboot.subprocess.run"


@contextmanager
def _patch_subprocess(side_effect=None):
  """Patch subprocess.run in the preboot module."""
  with patch(_SUBPROCESS_TARGET, side_effect=side_effect):
    yield


@pytest.fixture()
def workspace(tmp_path: Path) -> Path:
  """Create a minimal workspace with boot-sequence files."""
  sd = tmp_path / ".spec-driver"

  # Create boot-sequence files
  files = {
    "about/dogma.md": "# Dogma\n\n- No implementation without spec",
    "agents/exec.md": "# Execution\n\nRun via: `uv run spec-driver`",
    "agents/glossary.md": "# Glossary\n\n## Card\n\nA card is a task.",
    "agents/workflow.md": "# Workflow\n\nCeremony: town_planner",
    "agents/policy.md": "# Policy\n\nADRs are enabled.",
    "agents/memory.md": "# Memory\n\nUse /retrieving-memory.",
    "hooks/doctrine.md": "# Doctrine\n\n- Kanban IDs: T123-*",
  }
  for rel_path, content in files.items():
    path = sd / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

  # workflow.toml with exec command
  (sd / "workflow.toml").write_text(
    '[tool]\nexec = "uv run spec-driver"\n',
    encoding="utf-8",
  )

  return tmp_path


def _mock_run(listing_outputs: dict[str, str] | None = None):
  """Create a mock for subprocess.run that returns TSV for governance listings."""
  defaults = {
    "list adrs": "ADR-001\taccepted\tuse spec-driver\t2025-11-01",
    "list policies": "POL-001\trequired\tmaximise reuse\t2026-03-05",
    "list standards": "STD-002\trequired\tgovern lint\t2026-03-07",
  }
  outputs = listing_outputs or defaults

  def side_effect(cmd, **_kwargs):
    cmd_str = " ".join(cmd)
    for key, output in outputs.items():
      if key in cmd_str:
        return type("Result", (), {"returncode": 0, "stdout": output, "stderr": ""})()
    return type("Result", (), {"returncode": 1, "stdout": "", "stderr": "unknown"})()

  return side_effect


class TestGeneratePrebootContent:
  """Tests for generate_preboot_content."""

  def test_contains_all_boot_files(self, workspace: Path) -> None:
    """Generated content includes all 7 boot-sequence files."""
    with _patch_subprocess(_mock_run()):
      content = generate_preboot_content(workspace)

    for heading, rel_path in BOOT_SEQUENCE:
      assert f"## {heading}" in content
      file_content = (workspace / rel_path).read_text(encoding="utf-8").strip()
      assert file_content in content

  def test_contains_governance_listings(self, workspace: Path) -> None:
    """Generated content includes all 3 governance listings."""
    with _patch_subprocess(_mock_run()):
      content = generate_preboot_content(workspace)

    for heading, _args in GOVERNANCE_LISTINGS:
      assert f"## {heading}" in content

    assert "ADR-001" in content
    assert "POL-001" in content
    assert "STD-002" in content

  def test_governance_listings_are_tsv(self, workspace: Path) -> None:
    """Governance listings contain tab-separated values."""
    with _patch_subprocess(_mock_run()):
      content = generate_preboot_content(workspace)

    assert "ADR-001\taccepted\tuse spec-driver\t2025-11-01" in content

  def test_listings_after_policy_section(self, workspace: Path) -> None:
    """Governance listings appear after Policy section, before Memory."""
    with _patch_subprocess(_mock_run()):
      content = generate_preboot_content(workspace)

    policy_pos = content.index("## Policy & Governance")
    adrs_pos = content.index("## Accepted ADRs")
    memory_pos = content.index("## Memory")
    assert policy_pos < adrs_pos < memory_pos

  def test_generated_header(self, workspace: Path) -> None:
    """Content starts with the generated-file comment."""
    with _patch_subprocess(_mock_run()):
      content = generate_preboot_content(workspace)

    assert content.startswith(GENERATED_HEADER)

  def test_idempotent(self, workspace: Path) -> None:
    """Two runs produce identical output."""
    mock = _mock_run()
    with _patch_subprocess(mock):
      content1 = generate_preboot_content(workspace)
    with _patch_subprocess(mock):
      content2 = generate_preboot_content(workspace)

    assert content1 == content2

  def test_missing_boot_file(self, workspace: Path) -> None:
    """Missing boot file produces a comment, not an error."""
    (workspace / ".spec-driver" / "about" / "dogma.md").unlink()

    with _patch_subprocess(_mock_run()):
      content = generate_preboot_content(workspace)

    assert "<!-- missing:" in content
    assert "## Dogma" in content

  def test_failed_listing(self, workspace: Path) -> None:
    """Failed governance listing produces a comment, not an error."""

    def fail_all(cmd, **_kwargs):
      return type("Result", (), {"returncode": 1, "stdout": "", "stderr": "err"})()

    with _patch_subprocess(fail_all):
      content = generate_preboot_content(workspace)

    assert "<!-- listing failed:" in content

  def test_respects_exec_from_workflow_toml(self, workspace: Path) -> None:
    """Exec command is read from workflow.toml [tool] section."""
    (workspace / ".spec-driver" / "workflow.toml").write_text(
      '[tool]\nexec = "python -m supekku"\n',
      encoding="utf-8",
    )

    captured_cmds: list[list[str]] = []

    def capture_run(cmd, **_kwargs):
      captured_cmds.append(list(cmd))
      return type("Result", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    with _patch_subprocess(capture_run):
      generate_preboot_content(workspace)

    assert captured_cmds
    for cmd in captured_cmds:
      assert cmd[0] == "python"
      assert cmd[1] == "-m"
      assert cmd[2] == "supekku"

  def test_trailing_newline(self, workspace: Path) -> None:
    """Output ends with exactly one trailing newline."""
    with _patch_subprocess(_mock_run()):
      content = generate_preboot_content(workspace)

    assert content.endswith("\n")
    assert not content.endswith("\n\n")


class TestWritePrebootFile:
  """Tests for write_preboot_file."""

  def test_writes_to_correct_path(self, workspace: Path) -> None:
    """Output lands at .agents/spec-driver-boot.md."""
    with _patch_subprocess(_mock_run()):
      result = write_preboot_file(workspace)

    expected = workspace / PREBOOT_OUTPUT_DIR / PREBOOT_OUTPUT_FILE
    assert result == expected
    assert expected.is_file()

  def test_creates_output_directory(self, workspace: Path) -> None:
    """Creates .agents/ if it doesn't exist."""
    agents_dir = workspace / PREBOOT_OUTPUT_DIR
    assert not agents_dir.exists()

    with _patch_subprocess(_mock_run()):
      write_preboot_file(workspace)

    assert agents_dir.is_dir()

  def test_skips_write_when_unchanged(self, workspace: Path) -> None:
    """Does not rewrite file if content is identical."""
    mock = _mock_run()
    with _patch_subprocess(mock):
      path = write_preboot_file(workspace)
      mtime1 = path.stat().st_mtime_ns

    # Small delay not needed — we check content equality
    with _patch_subprocess(mock):
      write_preboot_file(workspace)
      mtime2 = path.stat().st_mtime_ns

    assert mtime1 == mtime2

  def test_overwrites_when_changed(self, workspace: Path) -> None:
    """Rewrites file when content has changed."""
    mock = _mock_run()
    with _patch_subprocess(mock):
      path = write_preboot_file(workspace)

    original = path.read_text(encoding="utf-8")

    # Change a source file
    dogma = workspace / ".spec-driver" / "about" / "dogma.md"
    dogma.write_text("# Updated Dogma\n\n- New rule", encoding="utf-8")

    with _patch_subprocess(mock):
      write_preboot_file(workspace)

    updated = path.read_text(encoding="utf-8")
    assert updated != original
    assert "Updated Dogma" in updated

  def test_writes_pi_append_system(self, workspace: Path) -> None:
    """Also writes .pi/APPEND_SYSTEM.md for pi auto-discovery."""
    with _patch_subprocess(_mock_run()):
      write_preboot_file(workspace)

    pi_path = workspace / PI_OUTPUT_DIR / PI_OUTPUT_FILE
    assert pi_path.is_file()

  def test_pi_output_matches_primary(self, workspace: Path) -> None:
    """pi output is identical to primary output."""
    with _patch_subprocess(_mock_run()):
      primary = write_preboot_file(workspace)

    pi_path = workspace / PI_OUTPUT_DIR / PI_OUTPUT_FILE
    assert primary.read_text(encoding="utf-8") == pi_path.read_text(encoding="utf-8")

  def test_pi_output_skips_write_when_unchanged(self, workspace: Path) -> None:
    """pi output not rewritten if content is identical."""
    mock = _mock_run()
    with _patch_subprocess(mock):
      write_preboot_file(workspace)
      pi_path = workspace / PI_OUTPUT_DIR / PI_OUTPUT_FILE
      mtime1 = pi_path.stat().st_mtime_ns

    with _patch_subprocess(mock):
      write_preboot_file(workspace)
      mtime2 = pi_path.stat().st_mtime_ns

    assert mtime1 == mtime2
