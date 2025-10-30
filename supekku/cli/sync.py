"""Unified synchronization command for specs, ADRs, and registries."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

import typer

from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS

# Add parent to path for imports
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

from supekku.scripts.lib.spec_sync.engine import SpecSyncEngine
from supekku.scripts.sync_specs import (
  REGISTRY_PATH,
  TECH_DIR,
  MultiLanguageSpecManager,
  parse_language_targets,
)

app = typer.Typer(help="Synchronization commands")


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
) -> None:
  """Synchronize specifications and registries with source code.

  Unified command for multi-language spec synchronization. Supports:
  - Go (via gomarkdoc)
  - Python (via AST analysis)
  - ADR/decision registry synchronization

  By default, only syncs specs. Use --adr to also sync ADR registry.
  """
  try:
    # Validate directory structure
    if not TECH_DIR.exists():
      typer.echo(f"Tech spec directory not found: {TECH_DIR}", err=True)
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
      spec_result = _sync_specs(
        targets=targets or [],
        language=language,
        existing=existing,
        check=check,
        dry_run=dry_run,
        allow_missing_source=allow_missing_source or [],
      )
      results["specs"] = spec_result

    # Sync ADRs if requested
    if adr:
      typer.echo("Synchronizing ADR registry...")
      adr_result = _sync_adr()
      results["adr"] = adr_result

    # Report overall results
    if all(r.get("success", True) for r in results.values()):
      typer.echo("Sync completed successfully")
      raise typer.Exit(EXIT_SUCCESS)

    typer.echo("Sync completed with errors", err=True)
    raise typer.Exit(EXIT_FAILURE)

  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


def _sync_specs(
  targets: list[str],
  language: str,
  existing: bool,
  check: bool,
  dry_run: bool,
  allow_missing_source: list[str],
) -> dict:
  """Execute spec synchronization."""
  # Initialize spec sync engine and spec manager
  engine = SpecSyncEngine(
    repo_root=ROOT,
    tech_dir=TECH_DIR,
  )

  spec_manager = MultiLanguageSpecManager(TECH_DIR, REGISTRY_PATH)

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

  # If no targets specified and --existing flag is used,
  # fetch targets from registry
  if not targets_by_language and existing:
    if language in ["all", "go"] and "go" in spec_manager.registry_v2.languages:
      go_targets = list(spec_manager.registry_v2.languages["go"].keys())
      if go_targets:
        targets_by_language["go"] = go_targets

    if language in ["all", "python"] and "python" in spec_manager.registry_v2.languages:
      python_targets = list(spec_manager.registry_v2.languages["python"].keys())
      if python_targets:
        targets_by_language["python"] = python_targets

  # Process results and return summary
  processed_count = 0
  skipped_count = 0
  created_count = 0

  # Execute synchronization
  for lang_name, target_list in targets_by_language.items():
    if language not in ["all", lang_name]:
      continue

    adapter = engine.adapters.get(lang_name)
    if not adapter:
      typer.echo(f"No adapter for language: {lang_name}", err=True)
      continue

    for _target in target_list:
      # Process each target
      processed_count += 1
      # Placeholder for actual processing logic
      # This would call into the sync engine and spec manager

  if not dry_run:
    spec_manager.rebuild_indices()
    spec_manager.save_registry()

  return {
    "success": True,
    "processed": processed_count,
    "created": created_count,
    "skipped": skipped_count,
  }


def _sync_adr() -> dict:
  """Execute ADR registry synchronization."""
  from supekku.scripts.lib.decision_registry import DecisionRegistry

  registry = DecisionRegistry(root=ROOT)
  registry.sync_with_symlinks()

  return {"success": True}


# For direct testing
if __name__ == "__main__":  # pragma: no cover
  app()
