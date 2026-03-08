"""Tests for drift ledger registry (VT-065-registry)."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from supekku.scripts.lib.drift.registry import DriftLedgerRegistry


@pytest.fixture
def drift_dir(tmp_path: Path) -> Path:
  """Create a .spec-driver/drift/ directory with test ledgers."""
  sd = tmp_path / ".spec-driver" / "drift"
  sd.mkdir(parents=True)
  return sd


def _write_ledger(drift_dir: Path, filename: str, content: str) -> Path:
  """Write a ledger file and return its path."""
  path = drift_dir / filename
  path.write_text(textwrap.dedent(content), encoding="utf-8")
  return path


class TestDiscovery:
  """Registry discovers ledger files in .spec-driver/drift/."""

  def test_empty_directory(self, drift_dir: Path, tmp_path: Path):
    reg = DriftLedgerRegistry(root=tmp_path)
    assert reg.collect() == {}

  def test_nonexistent_directory(self, tmp_path: Path):
    reg = DriftLedgerRegistry(root=tmp_path)
    assert reg.collect() == {}

  def test_discovers_ledger_files(self, drift_dir: Path, tmp_path: Path):
    _write_ledger(
      drift_dir,
      "DL-047-test.md",
      """\
      ---
      id: DL-047
      name: Test ledger
      status: open
      kind: drift_ledger
      ---

      # DL-047 — Test ledger
    """,
    )
    reg = DriftLedgerRegistry(root=tmp_path)
    ledgers = reg.collect()
    assert "DL-047" in ledgers
    assert ledgers["DL-047"].name == "Test ledger"

  def test_ignores_non_ledger_files(self, drift_dir: Path, tmp_path: Path):
    _write_ledger(
      drift_dir,
      "DL-047-test.md",
      """\
      ---
      id: DL-047
      name: Test ledger
      status: open
      ---
    """,
    )
    (drift_dir / "README.md").write_text("Not a ledger")
    (drift_dir / "notes.txt").write_text("Also not a ledger")
    reg = DriftLedgerRegistry(root=tmp_path)
    assert len(reg.collect()) == 1

  def test_discovers_multiple_ledgers(self, drift_dir: Path, tmp_path: Path):
    _write_ledger(
      drift_dir,
      "DL-047-first.md",
      """\
      ---
      id: DL-047
      name: First
      status: open
      ---
    """,
    )
    _write_ledger(
      drift_dir,
      "DL-048-second.md",
      """\
      ---
      id: DL-048
      name: Second
      status: closed
      ---
    """,
    )
    reg = DriftLedgerRegistry(root=tmp_path)
    assert len(reg.collect()) == 2


class TestFind:
  """Registry find by ID."""

  def test_find_existing(self, drift_dir: Path, tmp_path: Path):
    _write_ledger(
      drift_dir,
      "DL-047-test.md",
      """\
      ---
      id: DL-047
      name: Test
      status: open
      ---
    """,
    )
    reg = DriftLedgerRegistry(root=tmp_path)
    ledger = reg.find("DL-047")
    assert ledger is not None
    assert ledger.id == "DL-047"

  def test_find_nonexistent(self, drift_dir: Path, tmp_path: Path):
    reg = DriftLedgerRegistry(root=tmp_path)
    assert reg.find("DL-999") is None


class TestIter:
  """Registry iteration with optional status filter."""

  def test_iter_all(self, drift_dir: Path, tmp_path: Path):
    _write_ledger(
      drift_dir,
      "DL-047-a.md",
      """\
      ---
      id: DL-047
      name: A
      status: open
      ---
    """,
    )
    _write_ledger(
      drift_dir,
      "DL-048-b.md",
      """\
      ---
      id: DL-048
      name: B
      status: closed
      ---
    """,
    )
    reg = DriftLedgerRegistry(root=tmp_path)
    all_ledgers = list(reg.iter())
    assert len(all_ledgers) == 2

  def test_iter_by_status(self, drift_dir: Path, tmp_path: Path):
    _write_ledger(
      drift_dir,
      "DL-047-a.md",
      """\
      ---
      id: DL-047
      name: Open one
      status: open
      ---
    """,
    )
    _write_ledger(
      drift_dir,
      "DL-048-b.md",
      """\
      ---
      id: DL-048
      name: Closed one
      status: closed
      ---
    """,
    )
    reg = DriftLedgerRegistry(root=tmp_path)
    open_ledgers = list(reg.iter(status="open"))
    assert len(open_ledgers) == 1
    assert open_ledgers[0].id == "DL-047"


class TestParsedContent:
  """Registry correctly parses ledger content including entries."""

  def test_entries_parsed(self, drift_dir: Path, tmp_path: Path):
    _write_ledger(
      drift_dir,
      "DL-047-test.md",
      """\
      ---
      id: DL-047
      name: Test
      status: open
      ---

      # DL-047 — Test

      ## Entries

      ### DL-047.001: First entry

      ```yaml
      status: open
      entry_type: contradiction
      ```

      ### DL-047.002: Second entry

      ```yaml
      status: resolved
      entry_type: stale_claim
      ```
    """,
    )
    reg = DriftLedgerRegistry(root=tmp_path)
    ledger = reg.find("DL-047")
    assert ledger is not None
    assert len(ledger.entries) == 2
    assert ledger.entries[0].id == "DL-047.001"
    assert ledger.entries[1].status == "resolved"

  def test_body_preserved(self, drift_dir: Path, tmp_path: Path):
    _write_ledger(
      drift_dir,
      "DL-047-test.md",
      """\
      ---
      id: DL-047
      name: Test
      status: open
      ---

      ## Corpus coverage

      | Doc | Surveyed |
      | --- | --- |
      | PROD-001 | yes |

      ### DL-047.001: Entry

      ```yaml
      status: open
      entry_type: contradiction
      ```
    """,
    )
    reg = DriftLedgerRegistry(root=tmp_path)
    ledger = reg.find("DL-047")
    assert ledger is not None
    assert "Corpus coverage" in ledger.body
    assert "PROD-001" in ledger.body

  def test_delta_ref_extracted(self, drift_dir: Path, tmp_path: Path):
    _write_ledger(
      drift_dir,
      "DL-047-test.md",
      """\
      ---
      id: DL-047
      name: Test
      status: open
      delta_ref: DE-047
      ---
    """,
    )
    reg = DriftLedgerRegistry(root=tmp_path)
    ledger = reg.find("DL-047")
    assert ledger is not None
    assert ledger.delta_ref == "DE-047"

  def test_lazy_loading(self, drift_dir: Path, tmp_path: Path):
    """Registry doesn't load until first access."""
    _write_ledger(
      drift_dir,
      "DL-047-test.md",
      """\
      ---
      id: DL-047
      name: Test
      status: open
      ---
    """,
    )
    reg = DriftLedgerRegistry(root=tmp_path)
    assert reg._ledgers is None  # noqa: SLF001
    reg.collect()
    assert reg._ledgers is not None  # noqa: SLF001


class TestMalformedLedgers:
  """Registry handles malformed ledger files gracefully."""

  def test_missing_id_skipped(self, drift_dir: Path, tmp_path: Path):
    _write_ledger(
      drift_dir,
      "DL-047-test.md",
      """\
      ---
      name: No ID
      status: open
      ---
    """,
    )
    reg = DriftLedgerRegistry(root=tmp_path)
    assert reg.collect() == {}

  def test_malformed_frontmatter_skipped(self, drift_dir: Path, tmp_path: Path):
    (drift_dir / "DL-047-bad.md").write_text(
      "not valid frontmatter\n---\nstill broken",
      encoding="utf-8",
    )
    reg = DriftLedgerRegistry(root=tmp_path)
    # Should not raise, just skip
    assert len(reg.collect()) == 0
