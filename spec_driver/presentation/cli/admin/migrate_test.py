"""Tests for ``spec-driver admin migrate`` orchestrator.

Covers VT-CC-018, 019, 020, 023, 029, 031. Fixture migration steps are
generated on the fly under ``tmp_path/migrations/`` so they remain
out of the production discovery walk.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
import tomlkit
from typer.testing import CliRunner

from spec_driver.presentation.cli.admin import migrate as orchestrator
from spec_driver.presentation.cli.admin.migrate import (
  _acquire_lock,
  _advance_watermark,
  _discover_steps,
  _LockHeldError,
  _pending_steps,
  _read_last_applied,
  _release_lock,
  _run_step,
  _validate_step_kinds,
)
from supekku.cli.admin import app as admin_app

_FAKE_STEP_BODY = """\
from __future__ import annotations
from pathlib import Path
from spec_driver.migrations._helpers import atomic_write, split_frontmatter
from spec_driver.migrations._protocol import (
  BaseMigrationStep, StepPreview, StepResult,
)

_MARKER = "# de-137 fake-migration marker"


class _Step(BaseMigrationStep):
  applies_to_kind = "delta"
  description = "fake — append marker comment to body"

  def applies_to(self, file_path: Path) -> bool:
    text = file_path.read_text(encoding="utf-8")
    return _MARKER not in text

  def preview(self, file_path: Path) -> StepPreview:
    if not self.applies_to(file_path):
      return StepPreview(touched=[], skipped=[file_path], drift=[])
    return StepPreview(touched=[file_path], skipped=[], drift=[])

  def apply(self, file_path: Path) -> StepResult:
    if not self.applies_to(file_path):
      return StepResult(touched=[], skipped=[file_path])
    text = file_path.read_text(encoding="utf-8")
    atomic_write(file_path, text + _MARKER + "\\n")
    return StepResult(touched=[file_path], skipped=[])


step = _Step()
"""

_RAISING_STEP_BODY = """\
from __future__ import annotations
from pathlib import Path
from spec_driver.migrations._helpers import atomic_write
from spec_driver.migrations._protocol import (
  BaseMigrationStep, StepPreview, StepResult,
)

_MARKER = "# de-137 raising-migration marker"


class _Step(BaseMigrationStep):
  applies_to_kind = "delta"
  description = "raises on the configured filename"

  raise_on: str = ""

  def applies_to(self, file_path: Path) -> bool:
    return _MARKER not in file_path.read_text(encoding="utf-8")

  def preview(self, file_path: Path) -> StepPreview:
    return StepPreview(touched=[file_path], skipped=[], drift=[])

  def apply(self, file_path: Path) -> StepResult:
    if file_path.name == self.raise_on:
      raise RuntimeError("simulated mid-walk failure")
    text = file_path.read_text(encoding="utf-8")
    atomic_write(file_path, text + _MARKER + "\\n")
    return StepResult(touched=[file_path], skipped=[])


step = _Step()
"""

_BAD_KIND_STEP_BODY = """\
from __future__ import annotations
from pathlib import Path
from spec_driver.migrations._protocol import (
  BaseMigrationStep, StepPreview, StepResult,
)


class _Step(BaseMigrationStep):
  applies_to_kind = "speec"
  description = "intentionally wrong kind"


step = _Step()
"""


def _write_fake_step(
  migrations_dir: Path, folder: str, body: str = _FAKE_STEP_BODY
) -> Path:
  step_dir = migrations_dir / folder
  step_dir.mkdir(parents=True, exist_ok=True)
  (step_dir / "__init__.py").write_text("", encoding="utf-8")
  (step_dir / "migration.py").write_text(body, encoding="utf-8")
  return step_dir


def _write_delta_artefact(repo_root: Path, name: str = "DE-001.md") -> Path:
  delta_dir = repo_root / ".spec-driver" / "deltas" / "DE-001"
  delta_dir.mkdir(parents=True, exist_ok=True)
  path = delta_dir / name
  path.write_text(
    "---\nid: DE-001\nkind: delta\nstatus: draft\n---\nbody\n",
    encoding="utf-8",
  )
  return path


class TestDiscovery:
  def test_skips_non_matching_folders(self, tmp_path: Path) -> None:
    migrations = tmp_path / "migrations"
    migrations.mkdir()
    (migrations / "__pycache__").mkdir()
    (migrations / "not_a_migration").mkdir()
    assert _discover_steps(migrations) == []

  def test_parses_and_imports_step(self, tmp_path: Path) -> None:
    migrations = tmp_path / "migrations"
    _write_fake_step(migrations, "v0_10_0_001_fake")
    loaded = _discover_steps(migrations)
    assert len(loaded) == 1
    assert loaded[0].folder.name == "v0_10_0_001_fake"
    assert loaded[0].step.applies_to_kind == "delta"

  def test_missing_migration_py_raises(self, tmp_path: Path) -> None:
    migrations = tmp_path / "migrations"
    (migrations / "v0_10_0_001_empty").mkdir(parents=True)
    with pytest.raises(RuntimeError, match="missing migration.py"):
      _discover_steps(migrations)

  def test_loads_step_using_local_dataclass(self, tmp_path: Path) -> None:
    """Regression: ``_import_step_module`` must register the imported module
    in ``sys.modules`` so step bodies that use ``@dataclass`` under
    ``from __future__ import annotations`` resolve their own ``__module__``.

    Without the registration, Python 3.13 dataclass introspection raises
    ``AttributeError: 'NoneType' object has no attribute '__dict__'`` on
    every step that owns a ``@dataclass`` type — i.e. any non-trivial step
    such as the v0_10_0_001_delta_blocks DE-138 implementation.
    """
    body = (
      "from __future__ import annotations\n"
      "from dataclasses import dataclass\n"
      "from pathlib import Path\n"
      "from spec_driver.migrations._protocol import "
      "BaseMigrationStep, StepPreview, StepResult\n\n"
      "@dataclass(frozen=True)\n"
      "class _Local:\n"
      "  value: int\n\n"
      "class _Step(BaseMigrationStep):\n"
      "  applies_to_kind = 'delta'\n"
      "  description = 'dataclass regression'\n"
      "  def applies_to(self, file_path: Path) -> bool:\n"
      "    return False\n"
      "  def preview(self, file_path: Path) -> StepPreview:\n"
      "    return StepPreview(touched=[], skipped=[file_path], drift=[])\n"
      "  def apply(self, file_path: Path) -> StepResult:\n"
      "    return StepResult(touched=[], skipped=[file_path], drift_entries=[])\n\n"
      "step = _Step()\n"
    )
    migrations = tmp_path / "migrations"
    _write_fake_step(migrations, "v0_10_0_001_dataclass", body=body)
    loaded = _discover_steps(migrations)
    assert len(loaded) == 1
    assert loaded[0].step.applies_to_kind == "delta"


class TestKindValidation:
  """VT-CC-031: fail-fast on unregistered applies_to_kind."""

  def test_bad_kind_exits(self, tmp_path: Path) -> None:
    migrations = tmp_path / "migrations"
    _write_fake_step(migrations, "v0_10_0_002_bad", body=_BAD_KIND_STEP_BODY)
    loaded = _discover_steps(migrations)
    import click  # noqa: PLC0415

    with pytest.raises(click.exceptions.Exit) as exc:
      _validate_step_kinds(loaded)
    assert exc.value.exit_code == 1


class TestPendingSelection:
  def test_no_watermark_yields_all(self, tmp_path: Path) -> None:
    migrations = tmp_path / "migrations"
    _write_fake_step(migrations, "v0_10_0_001_a")
    _write_fake_step(migrations, "v0_10_0_002_b")
    loaded = _discover_steps(migrations)
    assert [p.folder.name for p in _pending_steps(loaded, None)] == [
      "v0_10_0_001_a",
      "v0_10_0_002_b",
    ]

  def test_watermark_filters(self, tmp_path: Path) -> None:
    migrations = tmp_path / "migrations"
    _write_fake_step(migrations, "v0_10_0_001_a")
    _write_fake_step(migrations, "v0_10_0_002_b")
    loaded = _discover_steps(migrations)
    pending = _pending_steps(loaded, "v0_10_0_001_a")
    assert [p.folder.name for p in pending] == ["v0_10_0_002_b"]


class TestRunStep:
  """VT-CC-018/019/020/023: dispatch + idempotency + atomicity + recovery."""

  def test_applies_to_candidate(self, tmp_path: Path) -> None:
    migrations = tmp_path / "migrations"
    _write_fake_step(migrations, "v0_10_0_001_fake")
    [loaded] = _discover_steps(migrations)
    _write_delta_artefact(tmp_path, "DE-001.md")
    results, _ = _run_step(tmp_path, loaded, dry_run=False)
    assert len(results) == 1
    delta_file = tmp_path / ".spec-driver" / "deltas" / "DE-001" / "DE-001.md"
    assert "de-137 fake-migration marker" in delta_file.read_text(encoding="utf-8")

  def test_idempotent_no_op_on_second_run(self, tmp_path: Path) -> None:
    """VT-CC-019: second apply on a post-state file is a no-op."""
    migrations = tmp_path / "migrations"
    _write_fake_step(migrations, "v0_10_0_001_fake")
    [loaded] = _discover_steps(migrations)
    _write_delta_artefact(tmp_path)
    _run_step(tmp_path, loaded, dry_run=False)
    pre = (tmp_path / ".spec-driver" / "deltas" / "DE-001" / "DE-001.md").read_text(
      encoding="utf-8"
    )
    results, _ = _run_step(tmp_path, loaded, dry_run=False)
    post = (tmp_path / ".spec-driver" / "deltas" / "DE-001" / "DE-001.md").read_text(
      encoding="utf-8"
    )
    assert results == []
    assert pre == post

  def test_idempotent_mixed_corpus(self, tmp_path: Path) -> None:
    """VT-CC-019: mixed pre/post corpus reaches uniformly applied final state."""
    migrations = tmp_path / "migrations"
    _write_fake_step(migrations, "v0_10_0_001_fake")
    [loaded] = _discover_steps(migrations)
    sd = tmp_path / ".spec-driver" / "deltas"
    sd.mkdir(parents=True)
    pre_file = sd / "DE-001" / "DE-001.md"
    pre_file.parent.mkdir()
    pre_file.write_text(
      "---\nid: DE-001\nkind: delta\nstatus: draft\n---\nbody\n",
      encoding="utf-8",
    )
    post_file = sd / "DE-002" / "DE-002.md"
    post_file.parent.mkdir()
    post_file.write_text(
      "---\nid: DE-002\nkind: delta\nstatus: draft\n---\n"
      "body\n# de-137 fake-migration marker\n",
      encoding="utf-8",
    )
    results, _ = _run_step(tmp_path, loaded, dry_run=False)
    assert {p.name for r in results for p in r.touched} == {"DE-001.md"}
    assert "de-137 fake-migration marker" in pre_file.read_text(encoding="utf-8")
    # Second run: both files are now post-state.
    results2, _ = _run_step(tmp_path, loaded, dry_run=False)
    assert results2 == []

  def test_mid_walk_recovery(self, tmp_path: Path) -> None:
    """VT-CC-020/023: raise mid-walk; rerun reaches all; watermark not advanced."""
    migrations = tmp_path / "migrations"
    _write_fake_step(migrations, "v0_10_0_001_raising", body=_RAISING_STEP_BODY)
    [loaded] = _discover_steps(migrations)
    loaded.step.raise_on = "DE-002.md"
    sd = tmp_path / ".spec-driver" / "deltas"
    files: list[Path] = []
    for did in ("DE-001", "DE-002", "DE-003"):
      d = sd / did
      d.mkdir(parents=True)
      f = d / f"{did}.md"
      f.write_text(
        f"---\nid: {did}\nkind: delta\nstatus: draft\n---\nbody\n",
        encoding="utf-8",
      )
      files.append(f)

    with pytest.raises(RuntimeError, match="simulated"):
      _run_step(tmp_path, loaded, dry_run=False)

    # File 1 in post-state; file 2 unchanged (atomic_write never landed);
    # file 3 untouched (loop aborted).
    assert "de-137 raising-migration marker" in files[0].read_text(encoding="utf-8")
    assert "de-137 raising-migration marker" not in files[1].read_text(encoding="utf-8")
    assert "de-137 raising-migration marker" not in files[2].read_text(encoding="utf-8")

    # Watermark must NOT have advanced — caller never reached _advance_watermark.
    assert _read_last_applied(tmp_path) is None

    # Recovery: clear the raise condition and rerun.
    loaded.step.raise_on = "<never>"
    _run_step(tmp_path, loaded, dry_run=False)
    for f in files:
      assert "de-137 raising-migration marker" in f.read_text(encoding="utf-8")


class TestWatermark:
  def test_round_trip(self, tmp_path: Path) -> None:
    (tmp_path / ".spec-driver").mkdir()
    workflow_toml = tmp_path / ".spec-driver" / "workflow.toml"
    workflow_toml.write_text(
      'ceremony = "town_planner"\n[tool]\nexec = "uv run spec-driver"\n',
      encoding="utf-8",
    )
    assert _read_last_applied(tmp_path) is None
    _advance_watermark(tmp_path, "v0_10_0_001_a")
    assert _read_last_applied(tmp_path) == "v0_10_0_001_a"
    doc = tomlkit.parse(workflow_toml.read_text(encoding="utf-8"))
    assert doc["migrations"]["last_applied"] == "v0_10_0_001_a"


class TestLockfile:
  """VT-CC-029: PID-liveness lockfile semantics."""

  @pytest.mark.skipif(sys.platform == "win32", reason="POSIX liveness probe")
  def test_live_pid_aborts(self, tmp_path: Path) -> None:
    lock_path = tmp_path / ".spec-driver" / "run" / "migrations" / ".lock"
    lock_path.parent.mkdir(parents=True)
    lock_path.write_text(
      f"{os.getpid()}\n2026-05-19T12:00:00+00:00\nuuid-stub\n",
      encoding="utf-8",
    )
    with pytest.raises(_LockHeldError, match="concurrent invocation"):
      _acquire_lock(tmp_path)
    # Lockfile must NOT be deleted by the aborting process.
    assert lock_path.exists()

  @pytest.mark.skipif(sys.platform == "win32", reason="POSIX liveness probe")
  def test_stale_pid_overwrites(self, tmp_path: Path) -> None:
    lock_path = tmp_path / ".spec-driver" / "run" / "migrations" / ".lock"
    lock_path.parent.mkdir(parents=True)
    # PID 2^31-1 will not exist on any sane runner.
    dead_pid = 2147483646
    lock_path.write_text(
      f"{dead_pid}\n2026-05-19T12:00:00+00:00\nuuid-stub\n",
      encoding="utf-8",
    )
    acquired = _acquire_lock(tmp_path)
    assert acquired == lock_path
    content = lock_path.read_text(encoding="utf-8").strip().splitlines()
    assert int(content[0]) == os.getpid()
    _release_lock(lock_path)

  def test_acquire_then_release(self, tmp_path: Path) -> None:
    acquired = _acquire_lock(tmp_path)
    assert acquired.exists()
    _release_lock(acquired)
    assert not acquired.exists()


class TestCheckList:
  """VT-CC-018: --check / --list against fixture inventory."""

  def test_check_lists_pending(
    self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    migrations = tmp_path / "migrations"
    _write_fake_step(migrations, "v0_10_0_001_fake")
    monkeypatch.setattr(orchestrator, "_migrations_dir", lambda: migrations)
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    res = runner.invoke(admin_app, ["migrate", "--check", "--root", str(tmp_path)])
    assert res.exit_code == 0
    assert "v0_10_0_001_fake" in res.output
    assert "kind=delta" in res.output

  def test_check_clean_on_empty_inventory(
    self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    empty = tmp_path / "migrations"
    empty.mkdir()
    monkeypatch.setattr(orchestrator, "_migrations_dir", lambda: empty)
    runner = CliRunner()
    res = runner.invoke(admin_app, ["migrate", "--check", "--root", str(tmp_path)])
    assert res.exit_code == 0
    assert "no pending migrations" in res.output

  def test_kind_required_for_sweep(
    self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    empty = tmp_path / "migrations"
    empty.mkdir()
    monkeypatch.setattr(orchestrator, "_migrations_dir", lambda: empty)
    runner = CliRunner()
    res = runner.invoke(admin_app, ["migrate", "--root", str(tmp_path)])
    assert res.exit_code != 0
    assert "positional <kind> required" in res.output
