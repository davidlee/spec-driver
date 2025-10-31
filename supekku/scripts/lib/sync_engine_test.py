"""Tests for sync_engine module."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from subprocess import CompletedProcess

import pytest

from supekku.scripts.lib.spec_utils import load_markdown_file
from supekku.scripts.lib.sync_engine import (
  GomarkdocNotAvailableError,
  SyncOptions,
  TechSpecSyncEngine,
)


class TechSpecSyncEngineTest(unittest.TestCase):
  """Test cases for TechSpecSyncEngine functionality."""

  def _build_engine(
    self,
    root: Path,
    *,
    gomarkdoc_available: bool = True,
    run_packages: list[str] | None = None,
    log_messages: list[str] | None = None,
    registry_path: Path,
    generate_calls: list[tuple[Path, str, bool, bool]] | None = None,
  ) -> TechSpecSyncEngine:
    if run_packages is None:
      run_packages = []
    if log_messages is None:
      log_messages = []
    if generate_calls is None:
      generate_calls = []

    def log(msg: str) -> None:
      log_messages.append(msg)

    def run(cmd: list[str]) -> CompletedProcess[str]:
      if cmd == ["go", "list", "-m"]:
        return CompletedProcess(cmd, 0, stdout="example.com/app\n", stderr="")
      if cmd == ["go", "list", "./..."]:
        stdout = "\n".join(run_packages) + ("\n" if run_packages else "")
        return CompletedProcess(cmd, 0, stdout=stdout, stderr="")
      msg = f"Unexpected command: {cmd}"
      raise AssertionError(msg)

    def gomarkdoc() -> bool:
      return gomarkdoc_available

    def generate_docs(
      spec_dir: Path,
      module_pkg: str,
      include_unexported: bool,
      check: bool,
    ) -> None:
      generate_calls.append((spec_dir, module_pkg, include_unexported, check))

    tech_dir = root / "specify" / "tech"
    tech_dir.mkdir(parents=True, exist_ok=True)

    return TechSpecSyncEngine(
      root=root,
      tech_dir=tech_dir,
      registry_path=registry_path,
      log=log,
      run_cmd=run,
      gomarkdoc_available=gomarkdoc,
      generate_docs=generate_docs,
    )

  def test_synchronize_creates_spec_and_generates_docs(self) -> None:
    """Test that synchronizing creates spec and generates documentation."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = Path(tmpdir)
      pkg_path = root / "internal" / "foo"
      pkg_path.mkdir(parents=True)
      (pkg_path / "file.go").write_text("package foo\n")

      registry_path = root / "specify" / "tech" / "registry.json"
      generate_calls: list[tuple[Path, str, bool, bool]] = []

      engine = self._build_engine(
        root,
        run_packages=["example.com/app/internal/foo"],
        registry_path=registry_path,
        generate_calls=generate_calls,
      )

      result = engine.synchronize(SyncOptions())

      assert result.created_specs == {"internal/foo": "SPEC-001"}
      assert len(generate_calls) == 2
      assert (True, False) in {(call[2], call[3]) for call in generate_calls}

      spec_dir = root / "specify" / "tech" / "SPEC-001"
      spec_file = spec_dir / "SPEC-001.md"
      assert spec_file.exists()
      frontmatter, _ = load_markdown_file(spec_file)
      assert "internal/foo" in frontmatter.get("packages", [])

  def test_synchronize_check_mode_requires_existing_spec(self) -> None:
    """Test that check mode skips packages without existing spec stubs."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = Path(tmpdir)
      pkg_path = root / "internal" / "foo"
      pkg_path.mkdir(parents=True)
      (pkg_path / "file.go").write_text("package foo\n")

      tech_dir = root / "specify" / "tech"
      tech_dir.mkdir(parents=True, exist_ok=True)
      registry_path = tech_dir / "registry.json"
      registry_v2 = {
        "version": 2,
        "languages": {"go": {"internal/foo": "SPEC-010"}},
        "metadata": {},
      }
      registry_path.write_text(json.dumps(registry_v2))

      generate_calls: list[tuple[Path, str, bool, bool]] = []

      engine = self._build_engine(
        root,
        run_packages=["example.com/app/internal/foo"],
        registry_path=registry_path,
        generate_calls=generate_calls,
      )

      result = engine.synchronize(SyncOptions(existing=True, check=True))

      assert not result.created_specs
      assert len(generate_calls) == 0
      assert len(result.skipped_packages) == 1
      skipped = result.skipped_packages[0]
      assert skipped.package == "internal/foo"
      assert skipped.reason == "missing spec stub"

  def test_synchronize_warns_when_gomarkdoc_missing(self) -> None:
    """Test that synchronization warns when gomarkdoc tool is not available."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = Path(tmpdir)
      pkg_path = root / "pkg"
      pkg_path.mkdir(parents=True)
      (pkg_path / "file.go").write_text("package pkg\n")

      registry_path = root / "specify" / "tech" / "registry.json"
      generate_calls: list[tuple[Path, str, bool, bool]] = []

      engine = self._build_engine(
        root,
        gomarkdoc_available=False,
        run_packages=["example.com/app/pkg"],
        registry_path=registry_path,
        generate_calls=generate_calls,
      )

      result = engine.synchronize(SyncOptions())

      assert result.warnings == [
        "gomarkdoc not found; documentation generation skipped",
      ]
      assert not generate_calls

  def test_check_mode_raises_when_gomarkdoc_missing(self) -> None:
    """Test that check mode raises an error when gomarkdoc is unavailable."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = Path(tmpdir)
      pkg_path = root / "pkg"
      pkg_path.mkdir(parents=True)
      (pkg_path / "file.go").write_text("package pkg\n")

      registry_path = root / "specify" / "tech" / "registry.json"

      engine = self._build_engine(
        root,
        gomarkdoc_available=False,
        run_packages=["example.com/app/pkg"],
        registry_path=registry_path,
      )

      with pytest.raises(GomarkdocNotAvailableError):
        engine.synchronize(SyncOptions(check=True))

  def test_allow_missing_go_creates_spec(self) -> None:
    """Test that allowing missing go files still creates spec for package."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = Path(tmpdir)
      pkg_path = root / "concept" / "group"
      pkg_path.mkdir(parents=True)

      registry_path = root / "specify" / "tech" / "registry.json"
      generate_calls: list[tuple[Path, str, bool, bool]] = []

      engine = self._build_engine(
        root,
        run_packages=["example.com/app/concept/group"],
        registry_path=registry_path,
        generate_calls=generate_calls,
      )

      result = engine.synchronize(
        SyncOptions(
          packages=["example.com/app/concept/group"],
          allow_missing_go=True,
        ),
      )

      assert "concept/group" in result.processed_packages
      spec_dir = root / "specify" / "tech"
      assert any(path.name.startswith("SPEC-") for path in spec_dir.iterdir())


if __name__ == "__main__":
  unittest.main()
