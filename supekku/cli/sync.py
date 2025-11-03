"""Unified synchronization command for specs, ADRs, and registries."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS
from supekku.scripts.lib.core.repo import find_repo_root
from supekku.scripts.lib.sync.engine import SpecSyncEngine
from supekku.scripts.lib.sync.models import SourceUnit
from supekku.scripts.sync_specs import (
  MultiLanguageSpecManager,
  parse_language_targets,
)

app = typer.Typer(help="Synchronization commands", no_args_is_help=True)


@app.command()
def sync(
  targets: Annotated[
    list[str] | None,
    typer.Argument(
      help="Specific targets to sync. Format: [language:]identifier "
      "(e.g., go:internal/foo, python:module.py)",
    ),
  ] = None,
  language: Annotated[
    str,
    typer.Option(
      "--language",
      "-l",
      help="Language to synchronize (go, python, or all)",
    ),
  ] = "all",
  existing: Annotated[
    bool,
    typer.Option(
      "--existing",
      help="Only operate on targets already registered in the registry",
    ),
  ] = False,
  check: Annotated[
    bool,
    typer.Option(
      "--check",
      help="Check mode: verify documentation is up-to-date without modifying files",
    ),
  ] = False,
  dry_run: Annotated[
    bool,
    typer.Option(
      "--dry-run",
      help="Show what would be created/modified without making actual changes",
    ),
  ] = False,
  allow_missing_source: Annotated[
    list[str] | None,
    typer.Option(
      "--allow-missing-source",
      help="Allow spec creation even when source files are missing "
      "(format: go:path, python:path)",
    ),
  ] = None,
  specs: Annotated[
    bool,
    typer.Option(
      "--specs",
      help="Synchronize tech specs with source code",
    ),
  ] = True,
  adr: Annotated[
    bool,
    typer.Option(
      "--adr",
      help="Synchronize ADR/decision registry",
    ),
  ] = False,
  prune: Annotated[
    bool,
    typer.Option(
      "--prune",
      help="Remove stub specs for deleted source (use --force for non-stubs)",
    ),
  ] = False,
  force: Annotated[
    bool,
    typer.Option(
      "--force",
      help="Allow pruning of non-stub specs (requires --prune)",
    ),
  ] = False,
) -> None:
  """Synchronize specifications and registries with source code.

  Unified command for multi-language spec synchronization. Supports:
  - Go (via gomarkdoc)
  - Python (via AST analysis)
  - ADR/decision registry synchronization

  By default, only syncs specs. Use --adr to also sync ADR registry.
  """
  # Auto-discover repository root
  root = find_repo_root()
  tech_dir = root / "specify" / "tech"
  registry_path = tech_dir / "registry_v2.json"

  # Validate directory structure
  if not tech_dir.exists():
    typer.echo(f"Tech spec directory not found: {tech_dir}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  if language not in ["go", "python", "all"]:
    typer.echo(
      f"Invalid language: {language}. Must be go, python, or all",
      err=True,
    )
    raise typer.Exit(EXIT_FAILURE)

  results = {}

  # Sync specs if requested
  if specs:
    typer.echo("Synchronizing tech specs...")
    try:
      spec_result = _sync_specs(
        root=root,
        tech_dir=tech_dir,
        registry_path=registry_path,
        targets=targets or [],
        language=language,
        existing=existing,
        check=check,
        dry_run=dry_run,
        _allow_missing_source=allow_missing_source or [],
        prune=prune,
        force=force,
      )
      results["specs"] = spec_result
    except (FileNotFoundError, ValueError, KeyError) as e:
      typer.echo(f"Error: {e}", err=True)
      raise typer.Exit(EXIT_FAILURE) from e

  # Sync ADRs if requested
  if adr:
    typer.echo("Synchronizing ADR registry...")
    try:
      adr_result = _sync_adr(root=root)
      results["adr"] = adr_result
    except Exception as e:
      typer.echo(f"Error syncing ADRs: {e}", err=True)
      raise typer.Exit(EXIT_FAILURE) from e

  # Always sync requirements from specs
  typer.echo("Synchronizing requirements registry...")
  try:
    req_result = _sync_requirements(root=root)
    results["requirements"] = req_result
  except Exception as e:
    typer.echo(f"Error syncing requirements: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e

  # Report overall results
  if all(r.get("success", True) for r in results.values()):
    typer.echo("Sync completed successfully")
    raise typer.Exit(EXIT_SUCCESS)

  typer.echo("Sync completed with errors", err=True)
  raise typer.Exit(EXIT_FAILURE)


def _sync_specs(
  root: Path,
  tech_dir: Path,
  registry_path: Path,
  targets: list[str],
  language: str,
  existing: bool,
  check: bool,
  dry_run: bool,
  _allow_missing_source: list[str],
  prune: bool,
  force: bool,
) -> dict:
  """Execute spec synchronization."""
  # Initialize spec sync engine and spec manager
  engine = SpecSyncEngine(
    repo_root=root,
    tech_dir=tech_dir,
  )

  spec_manager = MultiLanguageSpecManager(tech_dir, registry_path)

  # Process target specifications
  targets_by_language = {}

  # Handle targets argument
  if targets:
    parsed_targets = parse_language_targets(targets)

    # Merge targets
    for lang, target_list in parsed_targets.items():
      if lang in targets_by_language:
        targets_by_language[lang].extend(target_list)
      else:
        targets_by_language[lang] = target_list

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

  # Handle default mode when no targets specified
  if not targets_by_language:
    if existing:
      # --existing mode: fetch targets from registry
      if language in ["all", "go"] and "go" in spec_manager.registry_v2.languages:
        go_targets = list(spec_manager.registry_v2.languages["go"].keys())
        if go_targets:
          targets_by_language["go"] = go_targets

      if (
        language in ["all", "python"] and "python" in spec_manager.registry_v2.languages
      ):
        python_targets = list(spec_manager.registry_v2.languages["python"].keys())
        if python_targets:
          targets_by_language["python"] = python_targets
    # Auto-discovery mode: discover from source code
    elif language == "all":
      # Enable all available adapters for auto-discovery
      for lang_name in engine.adapters:
        targets_by_language[lang_name] = []
    # Enable specific language for auto-discovery
    elif language in engine.adapters:
      targets_by_language[language] = []

  # Process results and return summary
  processed_count = 0
  skipped_count = 0
  created_count = 0
  orphaned_count = 0

  # Execute synchronization
  for lang_name, target_list in targets_by_language.items():
    if language not in ["all", lang_name]:
      continue

    adapter = engine.adapters.get(lang_name)
    if not adapter:
      typer.echo(f"No adapter for language: {lang_name}", err=True)
      continue

    typer.echo(f"\n=== Synchronizing {lang_name.upper()} targets ===")

    # Discover source units
    orphaned_units = []
    try:
      if existing:
        typer.echo("Discovery mode: existing registry entries only")
        source_units = []
        if lang_name in spec_manager.registry_v2.languages:
          for identifier in spec_manager.registry_v2.languages[lang_name]:
            unit = SourceUnit(language=lang_name, identifier=identifier, root=root)

            # Validate source exists
            validation = adapter.validate_source_exists(unit)
            if validation["status"] == "missing":
              orphaned_units.append(unit)
              typer.echo(f"  ⚠ Orphaned: {identifier} (source deleted)", err=True)
            else:
              source_units.append(unit)
      else:
        typer.echo("Discovery mode: requested targets + auto-discovery")
        requested = target_list if target_list else None
        source_units = adapter.discover_targets(root, requested)

        # Always detect orphaned specs in discovery mode
        if lang_name in spec_manager.registry_v2.languages:
          registered_ids = set(spec_manager.registry_v2.languages[lang_name].keys())
          discovered_ids = {unit.identifier for unit in source_units}
          orphaned_ids = registered_ids - discovered_ids

          for orphaned_id in orphaned_ids:
            unit = SourceUnit(language=lang_name, identifier=orphaned_id, root=root)
            orphaned_units.append(unit)
            typer.echo(f"  ⚠ Orphaned: {orphaned_id} (source deleted)", err=True)
    except Exception as e:
      # Check if this language has existing specs in the registry
      has_existing_specs = lang_name in spec_manager.registry_v2.languages and bool(
        spec_manager.registry_v2.languages[lang_name]
      )

      if has_existing_specs:
        # Language has specs but toolchain failed - this is an error
        typer.echo(f"Error discovering {lang_name} targets: {e}", err=True)
        spec_count = len(spec_manager.registry_v2.languages[lang_name])
        typer.echo(
          f"Cannot sync {lang_name}: toolchain unavailable but "
          f"{spec_count} specs exist in registry",
          err=True,
        )
        # Return early with failure
        return {
          "success": False,
          "error": f"{lang_name} toolchain unavailable with existing specs",
          "processed": processed_count,
          "created": created_count,
          "skipped": skipped_count,
          "orphaned": orphaned_count,
        }
      # No existing specs - toolchain unavailability is just a warning
      typer.echo(f"Warning: {lang_name} toolchain unavailable: {e}")
      typer.echo(f"Skipping {lang_name} synchronization (no existing specs)")
      continue

    typer.echo(f"Found {len(source_units)} {lang_name} source units")
    if orphaned_units:
      typer.echo(f"Found {len(orphaned_units)} orphaned specs", err=True)

    if not source_units and not orphaned_units:
      typer.echo(f"No {lang_name} source units to process")
      continue

    # Process each source unit
    created_specs = {}
    skipped_units = []

    for unit in source_units:
      typer.echo(f"Processing {unit.identifier}...")

      result = spec_manager.process_source_unit(
        unit,
        adapter,
        check_mode=check,
        dry_run=dry_run,
      )

      if result["processed"]:
        processed_count += 1
        if dry_run:
          typer.echo(f"  → Would process {unit.identifier} -> {result['spec_id']}")
        else:
          typer.echo(f"  ✓ Processed {unit.identifier} -> {result['spec_id']}")

        # Report documentation variants
        for variant in result["doc_variants"]:
          if dry_run:
            typer.echo(f"    - {variant.name}: would generate")
          else:
            typer.echo(f"    - {variant.name}: {variant.status}")

        # Show paths that would be created in dry-run mode
        if dry_run and result["would_create_paths"]:
          typer.echo("  Paths that would be created:")
          for path in result["would_create_paths"]:
            typer.echo(f"    • {path}")

        if result["created"]:
          created_count += 1
          created_specs[unit.identifier] = result["spec_id"]
          if dry_run:
            typer.echo(f"  → Would create new spec: {result['spec_id']}")
          else:
            typer.echo(f"  ✓ Created new spec: {result['spec_id']}")

      elif result["skipped"]:
        skipped_count += 1
        skipped_units.append(f"{unit.identifier}: {result['reason']}")
        typer.echo(f"  ✗ Skipped {unit.identifier}: {result['reason']}")

    # Handle orphaned specs
    if orphaned_units:
      orphaned_count += len(orphaned_units)

      if prune:
        from supekku.scripts.lib.deletion.executor import DeletionExecutor

        typer.echo(f"\n  Pruning {len(orphaned_units)} orphaned specs...")
        executor = DeletionExecutor(root)

        # Build set of orphaned spec IDs for cross-reference validation
        orphaned_spec_ids: set[str] = set()
        for orphaned_unit in orphaned_units:
          spec_id = spec_manager.registry_v2.get_spec_id(
            orphaned_unit.language,
            orphaned_unit.identifier,
          )
          if spec_id:
            orphaned_spec_ids.add(spec_id)

        # Delete each orphaned spec with validation
        for orphaned_unit in orphaned_units:
          # Get spec_id from registry
          spec_id = spec_manager.registry_v2.get_spec_id(
            orphaned_unit.language,
            orphaned_unit.identifier,
          )

          if spec_id:
            # Check if spec is a stub (stubs can be pruned without --force)
            from supekku.scripts.lib.specs.detection import is_stub_spec
            from supekku.scripts.lib.specs.registry import SpecRegistry

            spec_registry = SpecRegistry(root=root)
            spec = spec_registry.get(spec_id)

            if spec and not is_stub_spec(spec.path) and not force:
              typer.echo(
                f"    ⚠ Skipping {spec_id} ({orphaned_unit.identifier}): "
                f"non-stub spec (use --force to prune)",
                err=True,
              )
              continue

            # Validate deletion with orphan context
            plan = executor.validator.validate_spec_deletion(
              spec_id,
              orphaned_specs=orphaned_spec_ids,
            )

            # Display warnings if deletion blocked
            if not plan.is_safe:
              msg = f"    ⚠ Cannot prune {spec_id}"
              msg += f" ({orphaned_unit.identifier}):"
              typer.echo(msg, err=True)
              for warning in plan.warnings:
                typer.echo(f"      → {warning}", err=True)
              continue

            # Proceed with deletion
            if dry_run:
              typer.echo(f"    → Would delete {spec_id} ({orphaned_unit.identifier})")
            else:
              try:
                executor.delete_spec(spec_id, dry_run=False)
                typer.echo(f"    ✓ Deleted {spec_id} ({orphaned_unit.identifier})")
              except Exception as e:
                typer.echo(f"    ✗ Failed to delete {spec_id}: {e}", err=True)

    # Report language results
    typer.echo(f"\n{lang_name.upper()} Results:")
    typer.echo(f"  Processed: {processed_count} units")
    typer.echo(f"  Created: {len(created_specs)} specs")
    typer.echo(f"  Skipped: {len(skipped_units)} units")
    if orphaned_count > 0:
      typer.echo(f"  Orphaned: {orphaned_count} units", err=True)
      if not prune:
        typer.echo("    (use --prune to remove)", err=True)

    if created_specs:
      typer.echo("  New specs created:")
      for identifier, spec_id in created_specs.items():
        typer.echo(f"    {spec_id}: {identifier}")

    if skipped_units:
      typer.echo("  Skipped reasons:")
      for reason in skipped_units:
        typer.echo(f"    - {reason}")

  # Rebuild symlink indices if any changes were made
  if processed_count > 0 and not dry_run:
    typer.echo("\nRebuilding symlink indices...")
    spec_manager.rebuild_indices()
    spec_manager.save_registry()
    typer.echo("✓ Symlink indices updated")

  return {
    "success": True,
    "processed": processed_count,
    "created": created_count,
    "skipped": skipped_count,
    "orphaned": orphaned_count,
  }


def _sync_adr(root: Path) -> dict:
  """Execute ADR registry synchronization."""
  from supekku.scripts.lib.decisions.registry import DecisionRegistry

  registry = DecisionRegistry(root=root)
  registry.sync_with_symlinks()

  return {"success": True}


def _sync_requirements(root: Path) -> dict:
  """Execute requirements registry synchronization from specs."""
  from supekku.scripts.lib.core.paths import get_registry_dir
  from supekku.scripts.lib.requirements.registry import RequirementsRegistry
  from supekku.scripts.lib.specs.registry import SpecRegistry

  spec_registry = SpecRegistry(root)
  requirements_path = get_registry_dir(root) / "requirements.yaml"
  req_registry = RequirementsRegistry(requirements_path)

  # Gather change artifact directories
  delta_dir = root / "change" / "deltas"
  revision_dir = root / "change" / "revisions"
  audit_dir = root / "change" / "audits"

  delta_dirs = [delta_dir] if delta_dir.exists() else None
  revision_dirs = [revision_dir] if revision_dir.exists() else None
  audit_dirs = [audit_dir] if audit_dir.exists() else None

  stats = req_registry.sync_from_specs(
    spec_registry=spec_registry,
    delta_dirs=delta_dirs,
    revision_dirs=revision_dirs,
    audit_dirs=audit_dirs,
  )
  req_registry.save()

  typer.echo(
    f"  Requirements: {stats.created} created, {stats.updated} updated",
  )

  return {"success": True, "created": stats.created, "updated": stats.updated}


# For direct testing
if __name__ == "__main__":  # pragma: no cover
  app()
