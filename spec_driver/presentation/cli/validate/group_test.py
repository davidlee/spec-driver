"""VT-CC-032 — uniform exit-code contract across ``validate`` subcommands (F-46).

Matrix:
- Bare ``validate`` ⇒ 2 (Typer ``no_args_is_help=True``).
- ``validate workspace`` clean ⇒ 0.
- ``validate workspace --strict`` with baseline warnings ⇒ 1.
- ``validate file <missing>`` ⇒ 2.
- ``validate file <binary>`` ⇒ 2.
- ``validate file <no-frontmatter>`` ⇒ 0.
- ``validate file <clean>`` ⇒ 0.
- ``validate file <error>`` ⇒ 1.
- ``validate templates`` clean ⇒ 0.
"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from spec_driver.presentation.cli.validate import app

runner = CliRunner()


def _clean_delta(tmp_path: Path) -> Path:
  artefact = tmp_path / "DE-100.md"
  artefact.write_text(
    """---
id: DE-100
slug: x
name: x
created: "2026-05-18"
updated: "2026-05-18"
status: draft
kind: delta
---

body
""",
    encoding="utf-8",
  )
  return artefact


def _error_artefact(tmp_path: Path) -> Path:
  artefact = tmp_path / "DE-200.md"
  artefact.write_text(
    """---
id: DE-200
slug: x
name: x
created: "2026-05-18"
updated: "2026-05-18"
status: pending-approval
kind: delta
---

body
""",
    encoding="utf-8",
  )
  return artefact


class TestExitCodeContract:
  def test_bare_validate_exits_2_help(self) -> None:
    result = runner.invoke(app, [])
    assert result.exit_code == 2

  def test_workspace_default_exits_0_on_warnings_only(self) -> None:
    # Live repo has 8 audit-gate warnings — all warning severity ⇒ exit 0
    result = runner.invoke(app, ["workspace"])
    assert result.exit_code == 0

  def test_workspace_strict_exits_1_on_baseline_warnings(self) -> None:
    # --strict promotes baseline warnings to errors ⇒ exit 1
    result = runner.invoke(app, ["workspace", "--strict"])
    assert result.exit_code == 1

  def test_file_missing_exits_2(self, tmp_path: Path) -> None:
    result = runner.invoke(app, ["file", str(tmp_path / "missing.md")])
    assert result.exit_code == 2

  def test_file_binary_exits_2(self, tmp_path: Path) -> None:
    binary = tmp_path / "image.bin"
    binary.write_bytes(b"\x00\x01\x02")
    result = runner.invoke(app, ["file", str(binary)])
    assert result.exit_code == 2

  def test_file_no_frontmatter_exits_0(self, tmp_path: Path) -> None:
    plain = tmp_path / "notes.md"
    plain.write_text("Just prose, no frontmatter.\n", encoding="utf-8")
    result = runner.invoke(app, ["file", str(plain)])
    assert result.exit_code == 0

  def test_file_clean_exits_0(self, tmp_path: Path) -> None:
    artefact = _clean_delta(tmp_path)
    result = runner.invoke(app, ["file", str(artefact)])
    assert result.exit_code == 0

  def test_file_with_strict_error_exits_1(self, tmp_path: Path) -> None:
    artefact = _error_artefact(tmp_path)
    result = runner.invoke(app, ["file", str(artefact), "--strict"])
    assert result.exit_code == 1

  def test_templates_clean_exits_0(self) -> None:
    # Live repo's templates are committed clean post-IP-137-P02.
    result = runner.invoke(app, ["templates"])
    assert result.exit_code == 0

  def test_workspace_help_exits_0(self) -> None:
    result = runner.invoke(app, ["workspace", "--help"])
    assert result.exit_code == 0

  def test_file_help_exits_0(self) -> None:
    result = runner.invoke(app, ["file", "--help"])
    assert result.exit_code == 0

  def test_templates_help_exits_0(self) -> None:
    result = runner.invoke(app, ["templates", "--help"])
    assert result.exit_code == 0
