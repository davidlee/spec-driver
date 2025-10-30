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
        print(
            f"Error: Target directory {target_root} does not exist",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Installing spec-driver workspace in {target_root}")

    # Create directory structure
    directories = [
        "change/audits",
        "change/deltas",
        "change/revisions",
        "specify/decisions",
        "specify/policies",
        "specify/product",
        "specify/tech",
        "supekku/registry",
        "supekku/templates",
        "supekku/about",
    ]

    for dir_path in directories:
        full_path = target_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"  Created {dir_path}/")

    # Initialize empty registry files
    registry_dir = target_root / "supekku" / "registry"
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
            print(f"  Initialized {registry_file}")
        else:
            print(f"  Skipped {registry_file} (already exists)")

    # Copy templates from package to target
    package_root = get_package_root()
    template_src = package_root / "templates"
    template_dest = target_root / "supekku" / "templates"

    if template_src.exists():
        print("  Copying templates...")
        for template_file in template_src.glob("*.md"):
            dest_file = template_dest / template_file.name
            if not dest_file.exists():
                shutil.copy2(template_file, dest_file)
                print(f"    Copied {template_file.name}")
            else:
                print(f"    Skipped {template_file.name} (already exists)")

    # Copy about files from package to target
    about_src = package_root / "about"
    about_dest = target_root / "supekku" / "about"

    if about_src.exists():
        print("  Copying about documentation...")
        for about_file in about_src.rglob("*"):
            if about_file.is_file():
                relative_path = about_file.relative_to(about_src)
                dest_file = about_dest / relative_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                if not dest_file.exists():
                    shutil.copy2(about_file, dest_file)
                    print(f"    Copied {relative_path}")
                else:
                    print(f"    Skipped {relative_path} (already exists)")

    # Copy agent files to .claude/commands/ if .claude exists
    claude_dir = target_root / ".claude"
    if claude_dir.exists() and claude_dir.is_dir():
        print("  Found .claude directory, copying agent commands...")
        commands_dir = claude_dir / "commands"
        commands_dir.mkdir(parents=True, exist_ok=True)

        agents_src = package_root / "agents"
        if agents_src.exists():
            for agent_file in agents_src.glob("*.md"):
                dest_file = commands_dir / agent_file.name
                if not dest_file.exists():
                    shutil.copy2(agent_file, dest_file)
                    print(f"    Copied {agent_file.name}")
                else:
                    print(f"    Skipped {agent_file.name} (already exists)")
    else:
        print("  No .claude directory found, skipping agent installation")

    print("\nWorkspace initialized successfully!")
    print("\nNext steps:")
    print("  - Create your first spec with: spec-driver-spec")
    print("  - Create an ADR with: spec-driver-adr")
    print("  - See all commands with: spec-driver-* (tab completion)")


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
