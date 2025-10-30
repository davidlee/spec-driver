"""Tests for the install script."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from supekku.scripts.install import get_package_root, initialize_workspace
from supekku.scripts.lib.paths import SPEC_DRIVER_DIR


def test_get_package_root() -> None:
    """Test that get_package_root returns the supekku directory."""
    root = get_package_root()
    assert root.name == "supekku"
    assert (root / "templates").exists()
    assert (root / "about").exists()


def test_initialize_workspace_creates_directories(tmp_path: Path) -> None:
    """Test that initialize_workspace creates the expected directory structure."""
    initialize_workspace(tmp_path)

    # Verify directories were created
    expected_dirs = [
        "change/audits",
        "change/deltas",
        "change/revisions",
        "specify/decisions",
        "specify/policies",
        "specify/product",
        "specify/tech",
        "backlog/improvements",
        "backlog/issues",
        "backlog/problems",
        "backlog/risks",
        f"{SPEC_DRIVER_DIR}/registry",
        f"{SPEC_DRIVER_DIR}/templates",
        f"{SPEC_DRIVER_DIR}/about",
    ]

    for dir_path in expected_dirs:
        assert (tmp_path / dir_path).is_dir(), f"Directory {dir_path} not created"

    # Verify backlog.md was created
    backlog_file = tmp_path / "backlog" / "backlog.md"
    assert backlog_file.exists(), "backlog/backlog.md not created"

    # Verify content
    content = backlog_file.read_text()
    assert "# Backlog" in content
    assert "improvements/" in content


def test_initialize_workspace_creates_registry_files(tmp_path: Path) -> None:
    """Test that initialize_workspace creates registry files with correct content."""
    initialize_workspace(tmp_path)

    registry_dir = tmp_path / SPEC_DRIVER_DIR / "registry"

    # Check each registry file
    expected_registries = {
        "deltas.yaml": {"deltas": {}},
        "revisions.yaml": {"revisions": {}},
        "audits.yaml": {"audits": {}},
        "decisions.yaml": {"decisions": {}},
        "requirements.yaml": {"requirements": {}},
    }

    for filename, expected_content in expected_registries.items():
        registry_file = registry_dir / filename
        assert registry_file.exists(), f"Registry file {filename} not created"

        content = yaml.safe_load(registry_file.read_text())
        assert content == expected_content, f"Registry {filename} has wrong content"


def test_initialize_workspace_copies_templates(tmp_path: Path) -> None:
    """Test that initialize_workspace copies template files."""
    initialize_workspace(tmp_path)

    template_dir = tmp_path / SPEC_DRIVER_DIR / "templates"
    assert template_dir.exists()

    # Check that at least some template files were copied
    template_files = list(template_dir.glob("*.md"))
    assert len(template_files) > 0, "No template files were copied"

    # Verify a specific template exists
    assert (template_dir / "ADR.md").exists()


def test_initialize_workspace_copies_about_files(tmp_path: Path) -> None:
    """Test that initialize_workspace copies about documentation."""
    initialize_workspace(tmp_path)

    about_dir = tmp_path / SPEC_DRIVER_DIR / "about"
    assert about_dir.exists()

    # Check that about files were copied
    about_files = list(about_dir.rglob("*.md"))
    assert len(about_files) > 0, "No about files were copied"


def test_initialize_workspace_copies_agents_when_claude_exists(tmp_path: Path) -> None:
    """Test that initialize_workspace copies agents if .claude exists."""
    # Create .claude directory before installing
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()

    initialize_workspace(tmp_path)

    commands_dir = claude_dir / "commands"
    assert commands_dir.exists()

    # Check that agent files were copied
    agent_files = list(commands_dir.glob("*.md"))
    assert len(agent_files) > 0, "No agent files were copied"


def test_initialize_workspace_skips_agents_when_no_claude(tmp_path: Path) -> None:
    """Test that initialize_workspace skips agents if .claude doesn't exist."""
    initialize_workspace(tmp_path)

    # .claude directory should not be created
    claude_dir = tmp_path / ".claude"
    assert not claude_dir.exists()


def test_initialize_workspace_skips_existing_files(tmp_path: Path) -> None:
    """Test that initialize_workspace doesn't overwrite existing files."""
    registry_dir = tmp_path / SPEC_DRIVER_DIR / "registry"
    registry_dir.mkdir(parents=True)

    # Create a registry file with custom content
    deltas_file = registry_dir / "deltas.yaml"
    custom_content = {"deltas": {"DE-001": {"title": "Test"}}}
    deltas_file.write_text(yaml.safe_dump(custom_content))

    initialize_workspace(tmp_path)

    # Verify the file wasn't overwritten
    content = yaml.safe_load(deltas_file.read_text())
    assert content == custom_content


def test_initialize_workspace_fails_on_nonexistent_directory() -> None:
    """Test that initialize_workspace exits if target directory doesn't exist."""
    nonexistent = Path("/tmp/definitely-does-not-exist-12345")

    with pytest.raises(SystemExit):
        initialize_workspace(nonexistent)
