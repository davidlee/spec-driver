"""Integration tests for sync defaults: contracts-first, opt-in spec creation.

VT-SYNC-DEFAULTS-001 through 005, verifying DE-028 preference resolution,
backward compat heuristic, and flag passthrough.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from supekku.cli.sync import app
from supekku.scripts.lib.core.sync_preferences import MARKER_FILENAME

_SPEC_DRIVER_DIR = ".spec-driver"
_MARKER_PATH = f"{_SPEC_DRIVER_DIR}/{MARKER_FILENAME}"

_SYNC_SPECS_SUCCESS = {
  "success": True,
  "processed": 0,
  "created": 0,
  "skipped": 0,
  "orphaned": 0,
}
_SYNC_REQS_SUCCESS = {"success": True, "created": 0, "updated": 0}


class SyncDefaultsTest(unittest.TestCase):
  """VT-SYNC-DEFAULTS: preference resolution and backward compat."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    self.tech_dir = self.root / "specify" / "tech"
    self.tech_dir.mkdir(parents=True)
    self.registry_path = self.tech_dir / "registry_v2.json"
    self._write_registry({})

  def tearDown(self) -> None:
    self.tmpdir.cleanup()

  # -- helpers --

  def _write_registry(self, languages: dict) -> None:
    self.registry_path.write_text(
      json.dumps({"version": 2, "languages": languages}),
      encoding="utf-8",
    )

  def _marker_path(self) -> Path:
    return self.root / _MARKER_PATH

  def _invoke(self, args: list[str] | None = None):
    return self.runner.invoke(app, ["sync", *(args or [])])

  # -- VT-001: fresh dir, no flags → contracts-only, no spec creation --

  @patch("supekku.cli.sync._sync_requirements")
  @patch("supekku.cli.sync._sync_specs")
  @patch("supekku.cli.sync.find_repo_root")
  def test_vt001_fresh_dir_defaults_to_contracts_only(
    self,
    mock_root: MagicMock,
    mock_sync_specs: MagicMock,
    mock_sync_reqs: MagicMock,
  ) -> None:
    """VT-SYNC-DEFAULTS-001: fresh repo, bare `sync` → no spec creation."""
    mock_root.return_value = self.root
    mock_sync_specs.return_value = _SYNC_SPECS_SUCCESS
    mock_sync_reqs.return_value = _SYNC_REQS_SUCCESS

    result = self._invoke()

    assert result.exit_code == 0, result.output
    mock_sync_specs.assert_called_once()
    call_kwargs = mock_sync_specs.call_args
    assert call_kwargs.kwargs["create_specs"] is False
    assert call_kwargs.kwargs["generate_contracts"] is True
    assert not self._marker_path().exists()

  # -- VT-002: --specs → persist + subsequent bare sync inherits --

  @patch("supekku.cli.sync._sync_requirements")
  @patch("supekku.cli.sync._sync_specs")
  @patch("supekku.cli.sync.find_repo_root")
  def test_vt002_specs_flag_persists_and_inherited(
    self,
    mock_root: MagicMock,
    mock_sync_specs: MagicMock,
    mock_sync_reqs: MagicMock,
  ) -> None:
    """VT-SYNC-DEFAULTS-002: --specs persists; subsequent sync inherits."""
    mock_root.return_value = self.root
    mock_sync_specs.return_value = _SYNC_SPECS_SUCCESS
    mock_sync_reqs.return_value = _SYNC_REQS_SUCCESS

    # First run: --specs
    result = self._invoke(["--specs"])
    assert result.exit_code == 0, result.output
    assert mock_sync_specs.call_args.kwargs["create_specs"] is True
    assert self._marker_path().exists(), "marker should be written"

    # Second run: no flag — should still create specs from marker
    mock_sync_specs.reset_mock()
    result = self._invoke()
    assert result.exit_code == 0, result.output
    assert mock_sync_specs.call_args.kwargs["create_specs"] is True

  # -- VT-003: --no-contracts → spec processing, no contract generation --

  @patch("supekku.cli.sync._sync_requirements")
  @patch("supekku.cli.sync._sync_specs")
  @patch("supekku.cli.sync.find_repo_root")
  def test_vt003_no_contracts_flag_skips_contract_generation(
    self,
    mock_root: MagicMock,
    mock_sync_specs: MagicMock,
    mock_sync_reqs: MagicMock,
  ) -> None:
    """VT-SYNC-DEFAULTS-003: --specs --no-contracts → specs yes, contracts no."""
    mock_root.return_value = self.root
    mock_sync_specs.return_value = _SYNC_SPECS_SUCCESS
    mock_sync_reqs.return_value = _SYNC_REQS_SUCCESS

    result = self._invoke(["--specs", "--no-contracts"])

    assert result.exit_code == 0, result.output
    mock_sync_specs.assert_called_once()
    call_kwargs = mock_sync_specs.call_args
    assert call_kwargs.kwargs["create_specs"] is True
    assert call_kwargs.kwargs["generate_contracts"] is False

  # -- VT-004: existing registry entries → backward compat opt-in --

  @patch("supekku.cli.sync._sync_requirements")
  @patch("supekku.cli.sync._sync_specs")
  @patch("supekku.cli.sync.find_repo_root")
  def test_vt004_existing_registry_triggers_backward_compat(
    self,
    mock_root: MagicMock,
    mock_sync_specs: MagicMock,
    mock_sync_reqs: MagicMock,
  ) -> None:
    """VT-SYNC-DEFAULTS-004: populated registry → implicit opt-in + marker."""
    mock_root.return_value = self.root
    mock_sync_specs.return_value = _SYNC_SPECS_SUCCESS
    mock_sync_reqs.return_value = _SYNC_REQS_SUCCESS

    # Populate registry with existing spec entries
    self._write_registry(
      {
        "go": {"internal/foo": {"spec_id": "SPEC-001"}},
      }
    )

    result = self._invoke()

    assert result.exit_code == 0, result.output
    assert self._marker_path().exists(), "marker should be written by heuristic"
    mock_sync_specs.assert_called_once()
    assert mock_sync_specs.call_args.kwargs["create_specs"] is True
    assert "Existing specs detected" in result.output

  # -- VT-005: fresh dir → hint message on stderr --

  @patch("supekku.cli.sync._sync_requirements")
  @patch("supekku.cli.sync._sync_specs")
  @patch("supekku.cli.sync.find_repo_root")
  def test_vt005_hint_message_when_specs_off(
    self,
    mock_root: MagicMock,
    mock_sync_specs: MagicMock,
    mock_sync_reqs: MagicMock,
  ) -> None:
    """VT-SYNC-DEFAULTS-005: fresh dir sync emits hint about --specs."""
    mock_root.return_value = self.root
    mock_sync_specs.return_value = _SYNC_SPECS_SUCCESS
    mock_sync_reqs.return_value = _SYNC_REQS_SUCCESS

    result = self._invoke()

    assert result.exit_code == 0, result.output
    assert "Spec auto-creation is off" in result.output
    assert "--specs" in result.output


if __name__ == "__main__":
  unittest.main()
