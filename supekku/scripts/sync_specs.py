#!/usr/bin/env python3
"""Multi-language specification synchronization.

Synchronizes technical specifications with source code across multiple languages,
generating interface documentation and maintaining registry mappings.

Supports Go (via gomarkdoc) and Python (via AST analysis) with extensible
adapter architecture for additional languages.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TECH_DIR = ROOT / "specify" / "tech"
REGISTRY_PATH = TECH_DIR / "registry_v2.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# pylint: disable=wrong-import-position
from supekku.scripts.lib.registry_migration import RegistryV2  # type: ignore
from supekku.scripts.lib.spec_index import SpecIndexBuilder  # type: ignore
from supekku.scripts.lib.spec_sync.engine import SpecSyncEngine  # type: ignore
from supekku.scripts.lib.spec_sync.models import SourceUnit  # type: ignore
from supekku.scripts.lib.spec_utils import (  # type: ignore
    append_unique,
    dump_markdown_file,
    ensure_list_entry,
    load_markdown_file,
)


class MultiLanguageSpecManager:
    """Manages spec creation and registry updates for multiple languages."""

    def __init__(self, tech_dir: Path, registry_path: Path) -> None:
        self.tech_dir = tech_dir
        self.registry_path = registry_path
        self.registry_v2 = RegistryV2.from_file(registry_path)
        self._current_adapter = (
            None  # Initialize to avoid attribute-defined-outside-init
        )
        self._dry_run_next_id = None  # Track next ID for dry-run mode

    def _get_next_spec_id(self, dry_run: bool = False) -> str:
        """Generate the next available SPEC-### ID."""
        # In dry-run mode, use and increment our counter
        if dry_run:
            if self._dry_run_next_id is None:
                # Initialize counter on first call
                self._dry_run_next_id = self._calculate_next_id_number()

            spec_id = f"SPEC-{self._dry_run_next_id:03d}"
            self._dry_run_next_id += 1
            return spec_id

        # Normal mode: calculate from registry and filesystem
        return f"SPEC-{self._calculate_next_id_number():03d}"

    def _calculate_next_id_number(self) -> int:
        """Calculate the next available SPEC ID number."""
        existing_ids = []

        # Get IDs from registry
        for lang_mappings in self.registry_v2.languages.values():
            existing_ids.extend(lang_mappings.values())

        # Get IDs from filesystem
        if self.tech_dir.exists():
            for entry in self.tech_dir.iterdir():
                if entry.is_dir() and entry.name.startswith("SPEC-"):
                    parts = entry.name.split("-")
                    if len(parts) >= 2:
                        existing_ids.append("-".join(parts[:2]))

        # Find highest number
        highest = 0
        for spec_id in existing_ids:
            if isinstance(spec_id, str) and spec_id.startswith("SPEC-"):
                try:
                    highest = max(highest, int(spec_id.split("-")[1]))
                except (ValueError, IndexError):
                    continue

        return highest + 1

    def _create_spec_directory_and_file(
        self, spec_id: str, source_unit, descriptor,
    ) -> Path:
        """Create spec directory and markdown file."""
        spec_dir = self.tech_dir / spec_id
        spec_dir.mkdir(parents=True, exist_ok=True)

        spec_file = spec_dir / f"{spec_id}.md"
        if spec_file.exists():
            return spec_file

        # Create frontmatter based on language
        today = date.today().isoformat()
        frontmatter = {
            "id": spec_id,
            "slug": "-".join(descriptor.slug_parts),
            "name": f"{source_unit.identifier} Specification",
            "created": today,
            "updated": today,
            "status": "draft",
            "kind": "spec",
            "responsibilities": [],
            "aliases": [],
        }

        # Add multi-language frontmatter from descriptor
        frontmatter.update(descriptor.default_frontmatter)

        # Create body
        body = (
            f"# {spec_id} – {source_unit.identifier}\n\n"
            "> TODO: Populate responsibilities, behaviour, quality requirements, "
            "and testing strategy.\n"
        )

        dump_markdown_file(spec_file, frontmatter, body)
        return spec_file

    def _update_registry(self, source_unit, spec_id: str) -> None:
        """Update the registry with new mapping."""
        self.registry_v2.add_source_unit(
            source_unit.language, source_unit.identifier, spec_id,
        )
        self.registry_v2.save_to_file(self.registry_path)

    def _ensure_source_in_spec(self, spec_file: Path, source_unit) -> None:
        """Ensure the source unit is listed in spec frontmatter."""
        frontmatter, body = load_markdown_file(spec_file)

        # Handle legacy packages field for Go
        if source_unit.language == "go":
            packages = ensure_list_entry(frontmatter, "packages")
            if append_unique(packages, source_unit.identifier):
                dump_markdown_file(spec_file, frontmatter, body)

        # Handle new sources field
        sources = ensure_list_entry(frontmatter, "sources")

        # Check if this source is already listed
        source_exists = False
        for source in sources:
            if (
                source.get("language") == source_unit.language
                and source.get("identifier") == source_unit.identifier
            ):
                source_exists = True
                break

        if not source_exists:
            # Add new source entry
            adapter = None
            if hasattr(self, "_current_adapter"):
                adapter = self._current_adapter

            if adapter:
                descriptor = adapter.describe(source_unit)
                sources.append(descriptor.default_frontmatter["sources"][0])
                dump_markdown_file(spec_file, frontmatter, body)

    def process_source_unit(
        self, source_unit, adapter, check_mode: bool = False, dry_run: bool = False,
    ) -> dict:
        """Process a single source unit - create spec, update registry, generate docs."""
        result = {
            "processed": False,
            "created": False,
            "skipped": False,
            "spec_id": None,
            "reason": None,
            "doc_variants": [],
            "would_create_paths": [],  # For dry-run mode
        }

        self._current_adapter = adapter  # Store for _ensure_source_in_spec

        try:
            # Get source descriptor
            descriptor = adapter.describe(source_unit)

            # Check if already in registry
            spec_id = self.registry_v2.get_spec_id(
                source_unit.language, source_unit.identifier,
            )

            # Create new spec if needed
            if not spec_id:
                if check_mode:
                    result["skipped"] = True
                    result["reason"] = "no registered spec for check mode"
                    return result

                spec_id = self._get_next_spec_id(dry_run=dry_run)
                result["created"] = True
                result["spec_id"] = spec_id

                if dry_run:
                    # Show what would be created
                    spec_dir = self.tech_dir / spec_id
                    spec_file = spec_dir / f"{spec_id}.md"
                    result["would_create_paths"].append(str(spec_file))
                else:
                    # Create spec directory and file
                    spec_file = self._create_spec_directory_and_file(
                        spec_id, source_unit, descriptor,
                    )

                    # Update registry
                    self._update_registry(source_unit, spec_id)
            else:
                result["spec_id"] = spec_id

            # Determine spec directory
            spec_dir = self.tech_dir / spec_id
            spec_file = spec_dir / f"{spec_id}.md"

            if not dry_run and not spec_file.exists():
                result["skipped"] = True
                result["reason"] = "spec file missing"
                return result

            if not dry_run:
                # Ensure source is listed in spec frontmatter
                self._ensure_source_in_spec(spec_file, source_unit)

                # Generate documentation
                doc_variants = adapter.generate(
                    source_unit, spec_dir=spec_dir, check=check_mode,
                )
                result["doc_variants"] = doc_variants
            else:
                # Dry-run: show what doc paths would be created
                for variant in descriptor.variants:
                    variant_path = spec_dir / variant.path
                    result["would_create_paths"].append(str(variant_path))
                # Use descriptor variants for display
                result["doc_variants"] = descriptor.variants

            result["processed"] = True

            return result

        except (OSError, ValueError, RuntimeError) as e:
            result["skipped"] = True
            result["reason"] = str(e)
            return result

    def rebuild_indices(self) -> None:
        """Rebuild symlink indices."""
        index_builder = SpecIndexBuilder(self.tech_dir)
        index_builder.rebuild()

    def save_registry(self) -> None:
        """Save the registry to disk."""
        self.registry_v2.save_to_file(self.registry_path)


def parse_language_targets(targets: list[str]) -> dict[str, list[str]]:
    """Parse language-prefixed targets into language-specific lists.

    Args:
        targets: List of targets, optionally prefixed with language
                 (e.g., "go:internal/foo", "python:module.py")

    Returns:
        Dictionary mapping language to list of identifiers

    """
    language_targets = {}

    for target in targets:
        if ":" in target:
            # Language-prefixed target
            language, identifier = target.split(":", 1)
            if language not in language_targets:
                language_targets[language] = []
            language_targets[language].append(identifier)
        else:
            # Unspecified language - let adapters determine support
            # Add to 'auto' key for later resolution
            if "auto" not in language_targets:
                language_targets["auto"] = []
            language_targets["auto"].append(target)

    return language_targets


def main() -> None:
    """Main entry point for multi-language spec synchronization."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Language selection
    parser.add_argument(
        "--language",
        choices=["go", "python", "all"],
        default="all",
        help="Language to synchronize (default: all)",
    )

    # Target specification
    parser.add_argument(
        "--targets",
        nargs="*",
        help="Specific targets to sync. Format: [language:]identifier "
        "(e.g., go:internal/foo, python:module.py)",
    )

    # Legacy package support for backwards compatibility
    parser.add_argument(
        "packages",
        nargs="*",
        help="Legacy: Go package paths to sync (for backwards compatibility)",
    )

    # Mode selection
    parser.add_argument(
        "--existing",
        action="store_true",
        help="Only operate on targets already registered in the registry",
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Check mode: verify documentation is up-to-date without modifying files",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created/modified without making actual changes",
    )

    # Language-specific options
    parser.add_argument(
        "--allow-missing-source",
        nargs="*",
        metavar="LANG:PATH",
        help="Allow spec creation even when source files are missing "
        "(format: go:path, python:path)",
    )

    args = parser.parse_args()

    # Validate directory structure
    if not TECH_DIR.exists():
        sys.exit(f"Tech spec directory not found: {TECH_DIR}")


    # Initialize spec sync engine and spec manager
    engine = SpecSyncEngine(
        repo_root=ROOT,
        tech_dir=TECH_DIR,
    )

    spec_manager = MultiLanguageSpecManager(TECH_DIR, REGISTRY_PATH)

    # Process target specifications
    targets_by_language = {}

    # Handle legacy packages argument (maps to Go targets)
    if args.packages:
        targets_by_language["go"] = args.packages

    # Handle new targets argument
    if args.targets:
        parsed_targets = parse_language_targets(args.targets)

        # Merge with existing targets
        for lang, targets in parsed_targets.items():
            if lang in targets_by_language:
                targets_by_language[lang].extend(targets)
            else:
                targets_by_language[lang] = targets

    # Handle auto-detected targets (no language prefix)
    if "auto" in targets_by_language:
        auto_targets = targets_by_language.pop("auto")

        # Try to resolve with each adapter
        for lang_name, adapter in engine.adapters.items():
            resolved_targets = []
            for target in auto_targets:
                if adapter.supports_identifier(target):
                    resolved_targets.append(target)

            if resolved_targets:
                if lang_name in targets_by_language:
                    targets_by_language[lang_name].extend(resolved_targets)
                else:
                    targets_by_language[lang_name] = resolved_targets

    # Handle --existing mode - populate targets from registry
    # Default to existing mode if no targets specified
    if (args.existing or not targets_by_language) and not targets_by_language:
        # If no specific targets provided but --existing requested, get all from registry
        if args.language == "all":
            # Process all languages from registry
            # Auto-discover Go (bounded by go.mod) and Python (now with test filtering)
            if "go" in engine.adapters:
                targets_by_language["go"] = []
            if "python" in engine.adapters:
                targets_by_language["python"] = []
            # Also process any other languages already in registry
            for language in spec_manager.registry_v2.languages:
                if language not in targets_by_language:
                    targets_by_language[language] = []
        else:
            # Process specific language from registry (or auto-discover if adapter exists)
            targets_by_language[args.language] = []

    # Filter by requested language
    if args.language != "all":
        # Keep only requested language
        targets_by_language = {
            lang: targets
            for lang, targets in targets_by_language.items()
            if lang == args.language
        }

    # Process each language
    total_processed = 0
    total_created = 0
    total_skipped = 0
    all_warnings = []

    for language, targets in targets_by_language.items():
        if language not in engine.adapters:
            continue


        adapter = engine.adapters[language]

        # Discover source units
        if args.existing:
            # Get existing entries from registry and convert to source units
            source_units = []
            if language in spec_manager.registry_v2.languages:
                for identifier in spec_manager.registry_v2.languages[language]:
                    source_units.append(
                        SourceUnit(language=language, identifier=identifier, root=ROOT),
                    )
        else:
            requested = targets if targets else None
            source_units = adapter.discover_targets(ROOT, requested)


        if not source_units:
            continue

        # Process each source unit
        created_specs = {}
        skipped_units = []

        for unit in source_units:

            result = spec_manager.process_source_unit(
                unit, adapter, check_mode=args.check, dry_run=args.dry_run,
            )

            if result["processed"]:
                total_processed += 1
                if args.dry_run:
                    pass
                else:
                    pass

                # Report documentation variants
                for _variant in result["doc_variants"]:
                    if args.dry_run:
                        pass
                    else:
                        pass

                # Show paths that would be created in dry-run mode
                if args.dry_run and result["would_create_paths"]:
                    for _path in result["would_create_paths"]:
                        pass

                if result["created"]:
                    total_created += 1
                    created_specs[unit.identifier] = result["spec_id"]
                    if args.dry_run:
                        pass
                    else:
                        pass

            elif result["skipped"]:
                total_skipped += 1
                skipped_units.append(f"{unit.identifier}: {result['reason']}")

        # Report language results

        if created_specs:
            for identifier in created_specs:
                pass

        if skipped_units:
            for _reason in skipped_units:
                pass

    # Rebuild symlink indices if any changes were made
    if total_processed > 0 and not args.dry_run:
        spec_manager.rebuild_indices()

    # Overall summary
    if args.dry_run:
        pass

    if all_warnings:
        for _warning in all_warnings:
            pass

    if total_processed == 0 and not args.existing:
        pass


if __name__ == "__main__":
    main()
