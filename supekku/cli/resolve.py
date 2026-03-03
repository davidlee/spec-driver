"""Resolve commands for cross-artifact link resolution."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Annotated

import typer

from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS
from supekku.scripts.lib.changes.registry import ChangeRegistry
from supekku.scripts.lib.core.repo import find_repo_root
from supekku.scripts.lib.core.spec_utils import dump_markdown_file, load_markdown_file
from supekku.scripts.lib.decisions.registry import DecisionRegistry
from supekku.scripts.lib.memory.links import links_to_frontmatter, resolve_all_links
from supekku.scripts.lib.memory.registry import MemoryRegistry
from supekku.scripts.lib.specs.registry import SpecRegistry

log = logging.getLogger(__name__)

ArtifactIndex = dict[str, tuple[str, str]]
"""Artifact ID → (relative_path, kind)."""

app = typer.Typer(help="Resolve cross-references", no_args_is_help=True)


@app.command("links")
def resolve_links(
  dry_run: Annotated[
    bool,
    typer.Option(
      "--dry-run",
      help="Show what would change without modifying files",
    ),
  ] = False,
  link_mode: Annotated[
    str,
    typer.Option(
      "--link-mode",
      help=(
        "Link persistence mode: none (suppress all), "
        "missing (unresolved only, default), "
        "compact (id-only resolved + missing), "
        "full (complete resolved + missing)"
      ),
    ),
  ] = "missing",
) -> None:
  """Resolve [[...]] links in memory record bodies.

  Parses wikilink tokens from memory body text, resolves them
  against known artifacts, and writes results to frontmatter.
  """
  root = find_repo_root()

  if dry_run:
    typer.echo("Resolving memory links (dry run)...")
  else:
    typer.echo("Resolving memory links...")

  try:
    stats = _resolve_memory_links(
      root,
      dry_run=dry_run,
      link_mode=link_mode,
    )
  except Exception as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e

  typer.echo(
    f"  Processed: {stats['processed']} records, "
    f"resolved: {stats['resolved']} links, "
    f"missing: {stats['missing']} targets",
  )

  if stats["warnings"]:
    for warning in stats["warnings"]:
      typer.echo(f"  Warning: {warning}", err=True)

  raise typer.Exit(EXIT_SUCCESS)


# ── Artifact index collectors ──────────────────────────────────


def _collect_memory_artifacts(root: Path, index: ArtifactIndex) -> None:
  """Add memory records to the artifact index."""
  registry = MemoryRegistry(root=root)
  for mem_id, record in registry.collect().items():
    rel_path = str(Path(record.path).relative_to(root))
    index[mem_id] = (rel_path, "memory")


def _collect_decisions(root: Path, index: ArtifactIndex) -> None:
  """Add ADR decisions to the artifact index."""
  try:
    registry = DecisionRegistry(root=root)
    for decision in registry.iter():
      if decision.path:
        rel = str(Path(decision.path).relative_to(root))
        index[decision.id] = (rel, "adr")
  except Exception:  # noqa: BLE001  # pylint: disable=broad-exception-caught
    log.debug("Skipping decisions registry", exc_info=True)


def _collect_specs(root: Path, index: ArtifactIndex) -> None:
  """Add specs to the artifact index."""
  try:
    registry = SpecRegistry(root=root)
    for spec in registry.all_specs():
      rel = str(spec.path.relative_to(root))
      index[spec.id] = (rel, "spec")
  except Exception:  # noqa: BLE001  # pylint: disable=broad-exception-caught
    log.debug("Skipping specs registry", exc_info=True)


def _collect_changes(root: Path, index: ArtifactIndex) -> None:
  """Add change artifacts (deltas, revisions, audits) to the artifact index."""
  try:
    for kind in ("delta", "revision", "audit"):
      registry = ChangeRegistry(root=root, kind=kind)
      for artifact_id, artifact in registry.collect().items():
        rel = str(artifact.path.relative_to(root))
        index[artifact_id] = (rel, kind)
  except Exception:  # noqa: BLE001  # pylint: disable=broad-exception-caught
    log.debug("Skipping changes registry", exc_info=True)


def _build_artifact_index(root: Path) -> ArtifactIndex:
  """Build artifact ID → (relative_path, kind) index.

  Collects IDs from all known registries: decisions, specs,
  deltas, revisions, audits, and memory records.

  Args:
    root: Repository root path.

  Returns:
    Dict mapping artifact ID to (relative_path, kind).
  """
  index: ArtifactIndex = {}
  _collect_memory_artifacts(root, index)
  _collect_decisions(root, index)
  _collect_specs(root, index)
  _collect_changes(root, index)
  return index


# ── Link resolution ────────────────────────────────────────────


def _resolve_single_memory(
  mem_file: Path,
  index: ArtifactIndex,
  stats: dict,
  *,
  dry_run: bool,
  link_mode: str = "missing",
) -> None:
  """Resolve links in a single memory file and update stats."""
  try:
    fm, body = load_markdown_file(mem_file)
  except Exception:  # noqa: BLE001  # pylint: disable=broad-exception-caught
    return

  source_id = fm.get("id", "")
  if not source_id:
    return

  result = resolve_all_links(body, known_artifacts=index, source_id=source_id)
  stats["processed"] += 1
  stats["resolved"] += len(result.out)
  stats["missing"] += len(result.missing)
  stats["warnings"].extend(result.warnings)

  links_data = links_to_frontmatter(result, mode=link_mode)
  has_existing = bool(fm.get("links"))
  has_new = bool(links_data)

  if not has_existing and not has_new:
    return

  if not dry_run:
    if has_new:
      fm["links"] = links_data
    elif has_existing:
      del fm["links"]
    dump_markdown_file(mem_file, fm, body)


def _resolve_memory_links(
  root: Path,
  dry_run: bool = False,
  link_mode: str = "missing",
) -> dict:
  """Resolve inline links in all memory records.

  For each mem.*.md file: parse body for [[...]] tokens,
  resolve against artifact index, update frontmatter links field.

  Args:
    root: Repository root path.
    dry_run: If True, skip writing changes.

  Returns:
    Stats dict with processed, resolved, missing, warnings counts.
  """
  index = _build_artifact_index(root)
  mem_dir = root / "memory"
  stats: dict = {"processed": 0, "resolved": 0, "missing": 0, "warnings": []}

  if not mem_dir.exists():
    return stats

  for mem_file in sorted(mem_dir.glob("mem.*.md")):
    _resolve_single_memory(
      mem_file,
      index,
      stats,
      dry_run=dry_run,
      link_mode=link_mode,
    )

  return stats
