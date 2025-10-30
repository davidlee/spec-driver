"""Go language adapter for specification synchronization."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from supekku.scripts.lib.spec_sync.models import (
    DocVariant,
    SourceDescriptor,
    SourceUnit,
)

from .base import LanguageAdapter

if TYPE_CHECKING:
    from collections.abc import Sequence


class GoAdapter(LanguageAdapter):
    """Language adapter for Go packages using existing gomarkdoc workflow.

    Wraps the existing TechSpecSyncEngine logic to provide consistent interface
    with other language adapters while maintaining full backward compatibility.
    """

    language: ClassVar[str] = "go"

    def discover_targets(
        self,
        repo_root: Path,
        requested: Sequence[str] | None = None,
    ) -> list[SourceUnit]:
        """Discover Go packages using `go list`.

        Args:
            repo_root: Root directory of the repository
            requested: Optional list of specific package paths to process

        Returns:
            List of SourceUnit objects for Go packages

        """
        # Import at runtime to avoid circular imports
        from supekku.scripts.lib.sync_engine import TechSpecSyncEngine

        # Create temporary engine to use existing discovery logic
        temp_engine = TechSpecSyncEngine(
            root=repo_root,
            tech_dir=repo_root / "specify" / "tech",
            registry_path=repo_root / "specify" / "tech" / "registry_v2.json",
        )

        module = temp_engine.go_module_name()

        # Use existing target resolution logic
        if requested:
            targets = []
            for item in requested:
                if item.startswith(module):
                    targets.append(item)
                else:
                    rel = item.strip("./")
                    targets.append(f"{module}/{rel}")
        else:
            result = temp_engine.run_cmd(["go", "list", "./..."])
            targets = result.stdout.splitlines()

        # Filter and normalize packages
        source_units = []
        for module_pkg in targets:
            if temp_engine.should_skip(module_pkg):
                continue

            rel_pkg = temp_engine.normalize_package(module_pkg, module)
            pkg_path = repo_root / rel_pkg

            # Only include if package directory exists
            if pkg_path.exists():
                source_units.append(
                    SourceUnit(
                        language=self.language, identifier=rel_pkg, root=repo_root,
                    ),
                )

        return source_units

    def describe(self, unit: SourceUnit) -> SourceDescriptor:
        """Describe how a Go package should be processed.

        Args:
            unit: Go package source unit

        Returns:
            SourceDescriptor with Go-specific metadata

        """
        self._validate_unit_language(unit)

        # Generate slug parts from package path
        slug_parts = unit.identifier.split("/")

        # Default frontmatter for Go packages
        default_frontmatter = {
            "packages": [unit.identifier],
            "sources": [
                {
                    "language": "go",
                    "identifier": unit.identifier,
                    "variants": [
                        {
                            "name": "public",
                            "path": "contracts/interfaces.md",
                        },
                        {
                            "name": "internal",
                            "path": "contracts/internals.md",
                        },
                    ],
                },
            ],
        }

        # Document variants that will be generated
        variants = [
            DocVariant(
                name="public",
                path=Path("contracts/interfaces.md"),
                hash="",
                status="unchanged",
            ),
            DocVariant(
                name="internal",
                path=Path("contracts/internals.md"),
                hash="",
                status="unchanged",
            ),
        ]

        return SourceDescriptor(
            slug_parts=slug_parts,
            default_frontmatter=default_frontmatter,
            variants=variants,
        )

    def generate(
        self, unit: SourceUnit, *, spec_dir: Path, check: bool = False,
    ) -> list[DocVariant]:
        """Generate documentation for a Go package using gomarkdoc.

        Args:
            unit: Go package source unit
            spec_dir: Specification directory to write documentation to
            check: If True, only check if docs would change

        Returns:
            List of DocVariant objects with generation results

        """
        self._validate_unit_language(unit)

        # Import at runtime to avoid circular imports
        from supekku.scripts.lib.sync_engine import TechSpecSyncEngine

        # Get module name for full package path
        temp_engine = TechSpecSyncEngine(
            root=self.repo_root,
            tech_dir=self.repo_root / "specify" / "tech",
            registry_path=self.repo_root / "specify" / "tech" / "registry_v2.json",
        )
        module = temp_engine.go_module_name()
        module_pkg = f"{module}/{unit.identifier}"

        # Determine output paths within spec directory
        contracts_dir = spec_dir / "contracts"
        public_output = contracts_dir / "interfaces.md"
        internal_output = contracts_dir / "internals.md"

        variants = []

        # Generate public docs (interfaces)
        try:
            if check and not public_output.exists():
                # In check mode, if file doesn't exist, it's missing
                variants.append(
                    DocVariant(
                        name="public",
                        path=public_output.relative_to(spec_dir),
                        hash="",
                        status="created",  # Would be created
                    ),
                )
            else:
                # Generate or check public docs
                contracts_dir.mkdir(parents=True, exist_ok=True)

                content_hash = ""
                if check:
                    # Check mode - run gomarkdoc --check
                    cmd = [
                        "gomarkdoc",
                        "--format",
                        "github",
                        "--check",
                        "--output",
                        str(public_output),
                        module_pkg,
                    ]
                    try:
                        subprocess.run(cmd, check=True, capture_output=True, text=True)
                        status = "unchanged"
                    except subprocess.CalledProcessError:
                        status = "changed"  # Would be changed
                else:
                    # Check if file exists before generation
                    existed_before = public_output.exists()
                    old_hash = None
                    if existed_before:
                        with open(public_output, encoding="utf-8") as f:
                            old_content = f.read()
                        old_hash = hashlib.sha256(
                            old_content.encode("utf-8"),
                        ).hexdigest()

                    # Generate mode
                    cmd = [
                        "gomarkdoc",
                        "--format",
                        "github",
                        "--output",
                        str(public_output),
                        module_pkg,
                    ]
                    subprocess.run(cmd, check=True, capture_output=True, text=True)

                    # Determine status by checking if file changed
                    content_hash = ""
                    if public_output.exists():
                        with open(public_output, encoding="utf-8") as f:
                            content = f.read()
                        content_hash = hashlib.sha256(
                            content.encode("utf-8"),
                        ).hexdigest()

                        if not existed_before:
                            status = "created"
                        elif content_hash != old_hash:
                            status = "changed"
                        else:
                            status = "unchanged"
                    else:
                        status = "created"

                variants.append(
                    DocVariant(
                        name="public",
                        path=public_output.relative_to(spec_dir),
                        hash=content_hash if not check else "",
                        status=status,
                    ),
                )

        except subprocess.CalledProcessError:
            # Handle gomarkdoc errors gracefully
            variants.append(
                DocVariant(
                    name="public",
                    path=public_output.relative_to(spec_dir)
                    if public_output
                    else Path(),
                    hash="",
                    status="unchanged",  # Error status would be handled at higher level
                ),
            )

        # Generate internal docs (with unexported symbols)
        try:
            if check and not internal_output.exists():
                variants.append(
                    DocVariant(
                        name="internal",
                        path=internal_output.relative_to(spec_dir),
                        hash="",
                        status="created",
                    ),
                )
            else:
                content_hash = ""
                if check:
                    cmd = [
                        "gomarkdoc",
                        "--format",
                        "github",
                        "--check",
                        "--include-unexported",
                        "--output",
                        str(internal_output),
                        module_pkg,
                    ]
                    try:
                        subprocess.run(cmd, check=True, capture_output=True, text=True)
                        status = "unchanged"
                    except subprocess.CalledProcessError:
                        status = "changed"
                else:
                    # Check if file exists before generation
                    existed_before = internal_output.exists()
                    old_hash = None
                    if existed_before:
                        with open(internal_output, encoding="utf-8") as f:
                            old_content = f.read()
                        old_hash = hashlib.sha256(
                            old_content.encode("utf-8"),
                        ).hexdigest()

                    cmd = [
                        "gomarkdoc",
                        "--format",
                        "github",
                        "--include-unexported",
                        "--output",
                        str(internal_output),
                        module_pkg,
                    ]
                    subprocess.run(cmd, check=True, capture_output=True, text=True)

                    if internal_output.exists():
                        with open(internal_output, encoding="utf-8") as f:
                            content = f.read()
                        content_hash = hashlib.sha256(
                            content.encode("utf-8"),
                        ).hexdigest()

                        if not existed_before:
                            status = "created"
                        elif content_hash != old_hash:
                            status = "changed"
                        else:
                            status = "unchanged"
                    else:
                        status = "created"

                variants.append(
                    DocVariant(
                        name="internal",
                        path=internal_output.relative_to(spec_dir),
                        hash=content_hash if not check else "",
                        status=status,
                    ),
                )

        except subprocess.CalledProcessError:
            variants.append(
                DocVariant(
                    name="internal",
                    path=internal_output.relative_to(spec_dir)
                    if internal_output
                    else Path(),
                    hash="",
                    status="unchanged",
                ),
            )

        return variants

    def supports_identifier(self, identifier: str) -> bool:
        """Check if identifier looks like a Go package path.

        Args:
            identifier: Identifier to check

        Returns:
            True if identifier appears to be a Go package path

        """
        # Go package paths typically:
        # - Use forward slashes as separators
        # - Don't end with file extensions
        # - May start with domain names or "internal/"
        # - Don't contain spaces or special characters (except /, -, _)

        if not identifier:
            return False

        # Basic sanity checks
        if " " in identifier or "\n" in identifier or "\t" in identifier:
            return False

        # Check for file extensions (Go packages are directories)
        if identifier.endswith((".go", ".py", ".ts", ".js")):
            return False

        # Go packages commonly start with these patterns
        go_patterns = [
            "cmd/",
            "internal/",
            "pkg/",
            "test/",
            "tools/",
        ]

        # Allow common Go patterns or domain-like paths
        if any(identifier.startswith(pattern) for pattern in go_patterns):
            return True

        # Allow simple paths with reasonable characters
        return bool(all(c.isalnum() or c in "/-_." for c in identifier))
