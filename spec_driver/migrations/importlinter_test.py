"""VT-CC-021: Migrations isolation import-linter contract.

Runs ``lint-imports`` against a temporary checkout of the project where
a deliberately-violating migration step is planted under
``spec_driver/migrations/``. The contract MUST report
``Migrations isolation BROKEN`` and exit non-zero. Removing the
violation restores ``KEPT``.

The test is slow (subprocess + dependency graph build) — marked
``slow`` if the repo carries the marker; otherwise runs unconditionally.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _project_files() -> list[Path]:
  """Paths required to invoke ``lint-imports`` from a tempdir copy."""
  candidates = [
    "pyproject.toml",
    "spec_driver",
    "supekku",
  ]
  return [_PROJECT_ROOT / name for name in candidates]


@pytest.mark.skipif(
  shutil.which("uvx") is None and shutil.which("lint-imports") is None,
  reason="Neither uvx nor lint-imports is available on PATH",
)
def test_migrations_isolation_breaks_on_forbidden_import(tmp_path: Path) -> None:
  workdir = tmp_path / "project"
  workdir.mkdir()
  for src in _project_files():
    dst = workdir / src.name
    if src.is_dir():
      shutil.copytree(
        src,
        dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
      )
    else:
      shutil.copy2(src, dst)

  # Plant a deliberately-violating step that imports a forbidden module.
  violator_dir = workdir / "spec_driver" / "migrations" / "v0_10_0_999_violator"
  violator_dir.mkdir(parents=True)
  (violator_dir / "__init__.py").write_text("", encoding="utf-8")
  (violator_dir / "migration.py").write_text(
    "from __future__ import annotations\n"
    "from pathlib import Path\n"
    "import spec_driver.core  # forbidden by Migrations isolation\n"
    "from spec_driver.migrations._protocol import (\n"
    "  BaseMigrationStep, StepPreview, StepResult,\n"
    ")\n"
    "\n"
    "class _Step(BaseMigrationStep):\n"
    "  applies_to_kind = 'delta'\n"
    "  description = 'violator'\n"
    "\n"
    "step = _Step()\n",
    encoding="utf-8",
  )

  res = subprocess.run(
    ["uvx", "import-linter", "lint"],
    cwd=workdir,
    check=False,
    capture_output=True,
    text=True,
    timeout=180,
  )
  combined = (res.stdout or "") + (res.stderr or "")
  assert res.returncode != 0, combined
  assert "Migrations isolation BROKEN" in combined, combined
  assert "spec_driver.core" in combined, combined


@pytest.mark.skipif(
  shutil.which("uvx") is None and shutil.which("lint-imports") is None,
  reason="Neither uvx nor lint-imports is available on PATH",
)
def test_migrations_isolation_kept_on_clean_tree() -> None:
  """Clean tree — both layers + the new isolation contract pass."""
  res = subprocess.run(
    ["uvx", "import-linter", "lint"],
    cwd=_PROJECT_ROOT,
    check=False,
    capture_output=True,
    text=True,
    timeout=180,
  )
  combined = (res.stdout or "") + (res.stderr or "")
  assert res.returncode == 0, combined
  assert "Migrations isolation KEPT" in combined, combined
