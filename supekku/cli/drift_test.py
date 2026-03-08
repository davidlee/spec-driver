"""Tests for drift ledger CLI commands (create, list, show)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from typer.testing import CliRunner

from supekku.cli.create import app as create_app
from supekku.cli.list import app as list_app
from supekku.cli.show import app as show_app


class _DriftTestBase(unittest.TestCase):
  """Shared setup for drift CLI tests."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    self.drift_dir = self.root / ".spec-driver" / "drift"

  def tearDown(self) -> None:
    self.tmpdir.cleanup()

  def _create_ledger(
    self,
    name: str = "Test ledger",
    delta: str | None = None,
  ) -> Path:
    """Create a ledger file directly for test setup."""
    self.drift_dir.mkdir(parents=True, exist_ok=True)
    existing = list(self.drift_dir.glob("DL-*.md"))
    next_num = len(existing) + 1
    ledger_id = f"DL-{next_num:03d}"
    slug = name.lower().replace(" ", "-")
    path = self.drift_dir / f"{ledger_id}-{slug}.md"
    delta_line = f"delta_ref: {delta}" if delta else "delta_ref: ''"
    path.write_text(f"""---
id: {ledger_id}
name: {name}
created: '2026-03-08'
updated: '2026-03-08'
status: open
kind: drift_ledger
{delta_line}
---

# {ledger_id} — {name}

## Entries

### {ledger_id}.001: Sample entry

```yaml
status: open
entry_type: contradiction
severity: blocking
topic: lifecycle
```

This is an example drift entry.
""")
    return path


class CreateDriftTest(_DriftTestBase):
  """Tests for `create drift` CLI command."""

  def test_create_drift_ledger(self) -> None:
    result = self.runner.invoke(
      create_app,
      ["drift", "Spec corpus review", "--root", str(self.root)],
    )
    assert result.exit_code == 0, result.stdout
    assert "Drift ledger created: DL-001" in result.stdout
    assert self.drift_dir.exists()
    files = list(self.drift_dir.glob("DL-001-*.md"))
    assert len(files) == 1

  def test_create_drift_with_delta(self) -> None:
    result = self.runner.invoke(
      create_app,
      ["drift", "Delta review", "--delta", "DE-065", "--root", str(self.root)],
    )
    assert result.exit_code == 0, result.stdout
    files = list(self.drift_dir.glob("DL-001-*.md"))
    content = files[0].read_text()
    assert "delta_ref: DE-065" in content

  def test_create_drift_sequential_ids(self) -> None:
    self._create_ledger("First")
    result = self.runner.invoke(
      create_app,
      ["drift", "Second", "--root", str(self.root)],
    )
    assert result.exit_code == 0, result.stdout
    assert "DL-002" in result.stdout


class ListDriftTest(_DriftTestBase):
  """Tests for `list drift` CLI command."""

  def test_list_empty(self) -> None:
    self.drift_dir.mkdir(parents=True)
    result = self.runner.invoke(
      list_app,
      ["drift", "--root", str(self.root)],
    )
    assert result.exit_code == 0, result.stdout
    assert "Drift Ledgers" in result.stdout

  def test_list_with_ledgers(self) -> None:
    self._create_ledger("First ledger")
    self._create_ledger("Second ledger")
    result = self.runner.invoke(
      list_app,
      ["drift", "--root", str(self.root)],
    )
    assert result.exit_code == 0, result.stdout
    assert "DL-001" in result.stdout
    assert "DL-002" in result.stdout

  def test_list_json(self) -> None:
    self._create_ledger("Test ledger")
    result = self.runner.invoke(
      list_app,
      ["drift", "--format", "json", "--root", str(self.root)],
    )
    assert result.exit_code == 0, result.stdout
    data = json.loads(result.stdout)
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == "DL-001"

  def test_list_filter(self) -> None:
    self._create_ledger("Spec corpus")
    self._create_ledger("Lifecycle review")
    result = self.runner.invoke(
      list_app,
      ["drift", "--filter", "lifecycle", "--format", "json", "--root", str(self.root)],
    )
    assert result.exit_code == 0, result.stdout
    data = json.loads(result.stdout)
    assert len(data["items"]) == 1
    assert "Lifecycle" in data["items"][0]["name"]

  def test_list_status_filter(self) -> None:
    self._create_ledger("Open ledger")
    # Create a closed one
    self.drift_dir.mkdir(parents=True, exist_ok=True)
    closed_path = self.drift_dir / "DL-002-closed.md"
    closed_path.write_text("""---
id: DL-002
name: Closed ledger
created: '2026-03-08'
updated: '2026-03-08'
status: closed
kind: drift_ledger
delta_ref: ''
---

# DL-002 — Closed ledger

## Entries
""")
    result = self.runner.invoke(
      list_app,
      ["drift", "--status", "closed", "--format", "json", "--root", str(self.root)],
    )
    assert result.exit_code == 0, result.stdout
    data = json.loads(result.stdout)
    assert len(data["items"]) == 1
    assert data["items"][0]["status"] == "closed"


class ShowDriftTest(_DriftTestBase):
  """Tests for `show drift` CLI command."""

  def test_show_drift_ledger(self) -> None:
    self._create_ledger("Test ledger")
    result = self.runner.invoke(
      show_app,
      ["drift", "DL-001", "--root", str(self.root)],
    )
    assert result.exit_code == 0, result.stdout
    assert "ID: DL-001" in result.stdout
    assert "Name: Test ledger" in result.stdout

  def test_show_drift_json(self) -> None:
    self._create_ledger("JSON test", delta="DE-047")
    result = self.runner.invoke(
      show_app,
      ["drift", "DL-001", "--json", "--root", str(self.root)],
    )
    assert result.exit_code == 0, result.stdout
    data = json.loads(result.stdout)
    assert data["id"] == "DL-001"
    assert data["delta_ref"] == "DE-047"
    assert len(data["entries"]) == 1

  def test_show_drift_path(self) -> None:
    path = self._create_ledger("Path test")
    result = self.runner.invoke(
      show_app,
      ["drift", "DL-001", "--path", "--root", str(self.root)],
    )
    assert result.exit_code == 0, result.stdout
    assert str(path) in result.stdout

  def test_show_drift_raw(self) -> None:
    self._create_ledger("Raw test")
    result = self.runner.invoke(
      show_app,
      ["drift", "DL-001", "--raw", "--root", str(self.root)],
    )
    assert result.exit_code == 0, result.stdout
    assert "---" in result.stdout
    assert "id: DL-001" in result.stdout

  def test_show_drift_not_found(self) -> None:
    self.drift_dir.mkdir(parents=True)
    result = self.runner.invoke(
      show_app,
      ["drift", "DL-999", "--root", str(self.root)],
    )
    assert result.exit_code != 0


class InferredShowDriftTest(_DriftTestBase):
  """Tests for ID inference dispatch to drift ledgers."""

  def test_show_inferred_dl_prefix(self) -> None:
    """show DL-001 should resolve via prefix inference."""
    self._create_ledger("Inferred test")
    result = self.runner.invoke(
      show_app,
      ["DL-001", "--root", str(self.root)],
    )
    assert result.exit_code == 0, result.stdout
    assert "DL-001" in result.stdout


if __name__ == "__main__":
  unittest.main()
