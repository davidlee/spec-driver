"""Install spec-driver workspace structure and initial files.

This script sets up the necessary directory structure and registry files
for a new spec-driver workspace.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import yaml

# Import after path setup to avoid circular imports
from supekku.scripts.lib.paths import SPEC_DRIVER_DIR


def get_package_root() -> Path:
    """Find the root directory of the installed spec-driver package."""
    # The script is in supekku/scripts/, so package root is two levels up
    return Path(__file__).parent.parent


def initialize_workspace(target_root: Path) -> None:  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    """Initialize spec-driver workspace structure and files.

    Args:
        target_root: Root directory where workspace should be initialized

    """
    target_root = target_root.resolve()

    if not target_root.exists():
        sys.exit(1)


    # Create directory structure
    directories = [
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

    for dir_path in directories:
        full_path = target_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)

    # Create empty backlog/backlog.md file
    backlog_file = target_root / "backlog" / "backlog.md"
    if not backlog_file.exists():
        backlog_file.write_text(
            "# Backlog\n\n"
            "Track improvements, issues, problems, and risks here.\n\n"
            "## Structure\n\n"
            "- `improvements/` - Enhancement ideas and feature requests\n"
            "- `issues/` - Known issues and bugs\n"
            "- `problems/` - Current problems requiring attention\n"
            "- `risks/` - Identified risks and mitigation strategies\n",
            encoding="utf-8",
        )

    # Initialize empty registry files
    registry_dir = target_root / SPEC_DRIVER_DIR / "registry"
    registries = {
        "deltas.yaml": {"deltas": {}},
        "revisions.yaml": {"revisions": {}},
        "audits.yaml": {"audits": {}},
        "decisions.yaml": {"decisions": {}},
        "requirements.yaml": {"requirements": {}},
    }

    for registry_file, initial_content in registries.items():
        registry_path = registry_dir / registry_file
        if not registry_path.exists():
            registry_path.write_text(
                yaml.safe_dump(initial_content, sort_keys=False),
                encoding="utf-8",
            )
        else:
            pass

    # Copy templates from package to target
    package_root = get_package_root()
    template_src = package_root / "templates"
    template_dest = target_root / SPEC_DRIVER_DIR / "templates"

    if template_src.exists():
        for template_file in template_src.glob("*.md"):
            dest_file = template_dest / template_file.name
            if not dest_file.exists():
                shutil.copy2(template_file, dest_file)
            else:
                pass

    # Copy about files from package to target
    about_src = package_root / "about"
    about_dest = target_root / SPEC_DRIVER_DIR / "about"

    if about_src.exists():
        for about_file in about_src.rglob("*"):
            if about_file.is_file():
                relative_path = about_file.relative_to(about_src)
                dest_file = about_dest / relative_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                if not dest_file.exists():
                    shutil.copy2(about_file, dest_file)
                else:
                    pass

    # Copy agent files to .claude/commands/ if .claude exists
    claude_dir = target_root / ".claude"
    if claude_dir.exists() and claude_dir.is_dir():
        commands_dir = claude_dir / "commands"
        commands_dir.mkdir(parents=True, exist_ok=True)

        agents_src = package_root / "agents"
        if agents_src.exists():
            for agent_file in agents_src.glob("*.md"):
                dest_file = commands_dir / agent_file.name
                if not dest_file.exists():
                    shutil.copy2(agent_file, dest_file)
                else:
                    pass
    else:
        pass



def main() -> None:
    """Main entry point for spec-driver-install command."""
    parser = argparse.ArgumentParser(
        description="Initialize spec-driver workspace structure",
    )
    parser.add_argument(
        "target_dir",
        nargs="?",
        default=".",
        help="Target directory to initialize (default: current directory)",
    )

    args = parser.parse_args()
    target_path = Path(args.target_dir)

    initialize_workspace(target_path)


if __name__ == "__main__":
    main()
