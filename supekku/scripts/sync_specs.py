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

import typer

ROOT = Path(__file__).resolve().parents[2]
TECH_DIR = ROOT / "specify" / "tech"
REGISTRY_PATH = TECH_DIR / "registry_v2.json"

if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

# pylint: disable=wrong-import-position
from supekku.scripts.lib.contracts.mirror import (  # type: ignore
  python_staging_dir,
  resolve_go_variant_outputs,
  resolve_ts_variant_outputs,
  resolve_zig_variant_outputs,
)
from supekku.scripts.lib.core.spec_utils import (  # type: ignore
  append_unique,
  dump_markdown_file,
  ensure_list_entry,
  load_markdown_file,
)
from supekku.scripts.lib.registry_migration import RegistryV2  # type: ignore
from supekku.scripts.lib.specs.index import SpecIndexBuilder  # type: ignore
from supekku.scripts.lib.sync.engine import SpecSyncEngine  # type: ignore
from supekku.scripts.lib.sync.models import SourceUnit  # type: ignore


class MultiLanguageSpecManager:
  """Manages spec creation and registry updates for multiple languages."""

  def __init__(self, tech_dir: Path, registry_path: Path) -> None:
    self.tech_dir = tech_dir
    self.registry_path = registry_path
    self.registry_v2 = RegistryV2.from_file(registry_path)
    self._current_adapter = None  # Initialize to avoid attribute-defined-outside-init
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
    self,
    spec_id: str,
    source_unit,
    descriptor,
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
      "status": "stub",
      "kind": "spec",
      "category": "unit",
      "c4_level": "code",
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
      source_unit.language,
      source_unit.identifier,
      spec_id,
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
    self,
    source_unit,
    adapter,
    check_mode: bool = False,
    dry_run: bool = False,
    generate_contracts: bool = True,
    create_specs: bool = True,
  ) -> dict:
    """Process a single source unit.

    Create spec, update registry, generate docs.
    """
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
        source_unit.language,
        source_unit.identifier,
      )

      # Create new spec if needed
      has_spec = bool(spec_id)
      if not has_spec:
        if check_mode:
          result["skipped"] = True
          result["reason"] = "no registered spec for check mode"
          return result

        if not create_specs and not generate_contracts:
          result["skipped"] = True
          result["reason"] = "spec auto-creation is off"
          return result

        if create_specs:
          spec_id = self._get_next_spec_id(dry_run=dry_run)
          result["created"] = True
          result["spec_id"] = spec_id

          if dry_run:
            spec_dir = self.tech_dir / spec_id
            spec_file = spec_dir / f"{spec_id}.md"
            result["would_create_paths"].append(str(spec_file))
          else:
            spec_file = self._create_spec_directory_and_file(
              spec_id,
              source_unit,
              descriptor,
            )
            self._update_registry(source_unit, spec_id)
      else:
        result["spec_id"] = spec_id

      # Spec-related work: frontmatter update, file checks
      if has_spec or create_specs:
        spec_dir = self.tech_dir / spec_id
        spec_file = spec_dir / f"{spec_id}.md"

        if not dry_run and not spec_file.exists():
          result["skipped"] = True
          result["reason"] = "spec file missing"
          return result

        if not dry_run:
          self._ensure_source_in_spec(spec_file, source_unit)

      # Contract generation — independent of spec existence
      if not dry_run:
        if generate_contracts:
          contracts_root = source_unit.root / ".contracts"
          variant_outputs = self._resolve_variant_outputs(
            source_unit,
            contracts_root,
          )
          doc_variants = adapter.generate(
            source_unit,
            variant_outputs=variant_outputs,
            check=check_mode,
          )

          if source_unit.language == "python":
            staging = variant_outputs["_staging_dir"]
            doc_variants = self._distribute_python_contracts(
              staging,
              contracts_root,
              doc_variants,
            )

          result["doc_variants"] = doc_variants
      elif generate_contracts and spec_id:
        # Dry-run with spec: show what doc paths would be created
        spec_dir = self.tech_dir / spec_id
        for variant in descriptor.variants:
          variant_path = spec_dir / variant.path
          result["would_create_paths"].append(str(variant_path))
        result["doc_variants"] = descriptor.variants

      result["processed"] = True

      return result

    except (OSError, ValueError, RuntimeError) as e:
      result["skipped"] = True
      result["reason"] = str(e)
      return result

  @staticmethod
  def _resolve_variant_outputs(
    source_unit,
    contracts_root: Path,
  ) -> dict[str, Path]:
    """Compute per-variant canonical output paths for a source unit."""
    lang = source_unit.language
    identifier = source_unit.identifier

    if lang == "go":
      return resolve_go_variant_outputs(identifier, contracts_root)
    if lang == "zig":
      return resolve_zig_variant_outputs(identifier, contracts_root)
    if lang in ("typescript", "javascript"):
      return resolve_ts_variant_outputs(identifier, contracts_root)
    if lang == "python":
      staging = python_staging_dir(identifier, contracts_root)
      return {"_staging_dir": staging}

    msg = f"No variant output resolver for language: {lang}"
    raise ValueError(msg)

  @staticmethod
  def _distribute_python_contracts(
    staging_dir: Path,
    contracts_root: Path,
    doc_variants: list,
  ) -> list:
    """Distribute staged Python contracts to canonical locations.

    Scans staging_dir for generated contract files, parses the header
    to determine the module identity, extracts the variant from the
    filename suffix, and moves each file to its canonical path under
    contracts_root/<view>/<module-path>.py.md.

    Returns updated DocVariant list with canonical paths.
    """
    from supekku.scripts.lib.contracts.mirror import (  # noqa: PLC0415
      extract_python_variant,
      python_module_to_path,
      read_python_module_name,
    )
    from supekku.scripts.lib.sync.models import DocVariant  # noqa: PLC0415

    # Python variant name → canonical view name
    variant_view_map = {
      "public": "public",
      "all": "all",
      "tests": "tests",
    }

    updated_variants: list[DocVariant] = []

    try:
      if not staging_dir.is_dir():
        return list(doc_variants)

      for staged_file in sorted(staging_dir.rglob("*.md")):
        variant = extract_python_variant(staged_file.name)
        if variant is None:
          continue

        module_name = read_python_module_name(staged_file)
        if module_name is None:
          continue

        view = variant_view_map.get(variant, variant)
        mirror_path = f"{python_module_to_path(module_name)}.md"
        canonical_path = contracts_root / view / mirror_path

        canonical_path.parent.mkdir(parents=True, exist_ok=True)
        # Move staged file to canonical location
        import shutil  # noqa: PLC0415

        shutil.move(str(staged_file), str(canonical_path))

        # Find matching doc variant to update its path
        # Map adapter variant names to our output variant names
        adapter_to_output = {
          "public": "api",
          "all": "implementation",
          "tests": "tests",
        }
        output_name = adapter_to_output.get(variant, variant)

        # Find the original variant and create updated version
        original = next(
          (v for v in doc_variants if v.name == output_name),
          None,
        )
        if original:
          updated_variants.append(
            DocVariant(
              name=original.name,
              path=canonical_path,
              hash=original.hash,
              status=original.status,
            ),
          )

    finally:
      # Clean up staging directory
      import shutil  # noqa: PLC0415

      if staging_dir.exists():
        shutil.rmtree(staging_dir)
        # Also remove parent staging dirs if empty
        parent = staging_dir.parent
        while parent != contracts_root and parent.exists():
          try:
            parent.rmdir()  # only succeeds if empty
            parent = parent.parent
          except OSError:
            break

    return updated_variants if updated_variants else list(doc_variants)

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
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
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
    # If no specific targets provided but --existing requested,
    # get all from registry
    if args.language == "all":
      # Process all languages from registry
      # Auto-discover Go (bounded by go.mod) and Python
      # (now with test filtering)
      if "go" in engine.adapters:
        targets_by_language["go"] = []
      if "python" in engine.adapters:
        targets_by_language["python"] = []
      # Process any other languages already in registry
      for language in spec_manager.registry_v2.languages:
        if language not in targets_by_language:
          targets_by_language[language] = []
    else:
      # Process specific language from registry
      # (or auto-discover if adapter exists)
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
      typer.echo(f"Warning: No adapter available for language '{language}' - skipping")
      continue

    typer.echo(f"\n=== Synchronizing {language.upper()} targets ===")

    adapter = engine.adapters[language]

    # Discover source units
    if args.existing:
      typer.echo("Discovery mode: existing registry entries only")
      # Get existing entries from registry and convert to source units
      source_units = []
      if language in spec_manager.registry_v2.languages:
        for identifier in spec_manager.registry_v2.languages[language]:
          source_units.append(
            SourceUnit(language=language, identifier=identifier, root=ROOT),
          )
    else:
      typer.echo("Discovery mode: requested targets + auto-discovery")
      requested = targets if targets else None
      source_units = adapter.discover_targets(ROOT, requested)

    typer.echo(f"Found {len(source_units)} {language} source units")

    if not source_units:
      typer.echo(f"No {language} source units to process")
      continue

    # Process each source unit
    created_specs = {}
    skipped_units = []

    for unit in source_units:
      typer.echo(f"Processing {unit.identifier}...")

      result = spec_manager.process_source_unit(
        unit,
        adapter,
        check_mode=args.check,
        dry_run=args.dry_run,
      )

      if result["processed"]:
        total_processed += 1
        if args.dry_run:
          typer.echo(f"  → Would process {unit.identifier} -> {result['spec_id']}")
        else:
          typer.echo(f"  ✓ Processed {unit.identifier} -> {result['spec_id']}")

        # Report documentation variants
        for variant in result["doc_variants"]:
          if args.dry_run:
            typer.echo(f"    - {variant.name}: would generate")
          else:
            typer.echo(f"    - {variant.name}: {variant.status}")

        # Show paths that would be created in dry-run mode
        if args.dry_run and result["would_create_paths"]:
          typer.echo("  Paths that would be created:")
          for path in result["would_create_paths"]:
            typer.echo(f"    • {path}")

        if result["created"]:
          total_created += 1
          created_specs[unit.identifier] = result["spec_id"]
          if args.dry_run:
            typer.echo(f"  → Would create new spec: {result['spec_id']}")
          else:
            typer.echo(f"  ✓ Created new spec: {result['spec_id']}")

      elif result["skipped"]:
        total_skipped += 1
        skipped_units.append(f"{unit.identifier}: {result['reason']}")
        typer.echo(f"  ✗ Skipped {unit.identifier}: {result['reason']}")

    # Report language results
    typer.echo(f"\n{language.upper()} Results:")
    typer.echo(f"  Processed: {total_processed} units")
    typer.echo(f"  Created: {len(created_specs)} specs")
    typer.echo(f"  Skipped: {len(skipped_units)} units")

    if created_specs:
      typer.echo("  New specs created:")
      for identifier, spec_id in created_specs.items():
        typer.echo(f"    {spec_id}: {identifier}")

    if skipped_units:
      typer.echo("  Skipped reasons:")
      for reason in skipped_units:
        typer.echo(f"    - {reason}")

  # Rebuild symlink indices if any changes were made
  if total_processed > 0 and not args.dry_run:
    typer.echo("\nRebuilding symlink indices...")
    spec_manager.rebuild_indices()
    typer.echo("✓ Symlink indices updated")

  # Overall summary
  typer.echo("\n=== Overall Summary ===")
  if args.dry_run:
    typer.echo("DRY RUN MODE - No files were modified")

  typer.echo(f"Total processed: {total_processed} units")
  typer.echo(f"Total created: {total_created} specs")
  typer.echo(f"Total skipped: {total_skipped} units")

  if all_warnings:
    typer.echo("Warnings:")
    for warning in all_warnings:
      typer.echo(f"  - {warning}")

  if total_processed == 0 and not args.existing:
    typer.echo("\nNo source units found. Try:")
    typer.echo("  - Specify targets: --targets go:internal/foo python:module.py")
    typer.echo("  - Use --existing to process registered packages")
    typer.echo("  - Check language adapters are working")


if __name__ == "__main__":
  main()
