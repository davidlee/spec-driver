#!/usr/bin/env python3
"""Migrate existing draft specs to stub status.

One-time migration script to update specs with status='draft' and ≤30 lines
to status='stub'. This aligns existing auto-generated specs with the new
convention where sync creates specs with status='stub'.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

from supekku.scripts.lib.specs.detection import is_stub_spec
from supekku.scripts.lib.specs.registry import SpecRegistry


def migrate_stub_status(root: Path | None = None, dry_run: bool = True) -> dict:
  """Migrate draft specs that are actually stubs to status='stub'.

  Args:
    root: Repository root path (auto-detected if None)
    dry_run: If True, report what would change without modifying files

  Returns:
    Dictionary with migration results:
      - migrated: List of spec IDs that were migrated
      - skipped: List of (spec_id, reason) tuples for skipped specs
      - errors: List of (spec_id, error) tuples for failed migrations

  """
  if root is None:
    # Auto-detect repository root
    current = Path.cwd()
    while current != current.parent:
      if (current / ".git").exists():
        root = current
        break
      current = current.parent
    else:
      root = Path.cwd()

  # Load spec registry
  registry = SpecRegistry(root=root)

  migrated = []
  skipped = []
  errors = []

  # Process all specs
  for spec in registry.all_specs():
    try:
      # Only migrate specs with status='draft' that are detected as stubs
      if spec.status != "draft":
        skipped.append((spec.id, f"status={spec.status} (not draft)"))
        continue

      if not is_stub_spec(spec.path):
        skipped.append((spec.id, "not detected as stub (>30 lines or modified)"))
        continue

      # This is a draft spec that should be a stub - migrate it
      if dry_run:
        migrated.append(spec.id)
      else:
        # Read the file
        content = spec.path.read_text(encoding="utf-8")

        # Parse frontmatter
        if not content.startswith("---\n"):
          errors.append((spec.id, "invalid frontmatter format"))
          continue

        # Find frontmatter boundaries
        end_idx = content.find("\n---\n", 4)
        if end_idx == -1:
          errors.append((spec.id, "could not find frontmatter end"))
          continue

        # Parse and update frontmatter
        frontmatter_text = content[4:end_idx]
        frontmatter_dict = yaml.safe_load(frontmatter_text)

        frontmatter_dict["status"] = "stub"

        # Serialize updated frontmatter
        updated_frontmatter = yaml.dump(
          frontmatter_dict,
          default_flow_style=False,
          allow_unicode=True,
          sort_keys=False,
        )

        # Reconstruct file content
        body = content[end_idx + 5 :]  # Skip "\n---\n"
        updated_content = f"---\n{updated_frontmatter}---\n{body}"

        # Write back
        spec.path.write_text(updated_content, encoding="utf-8")
        migrated.append(spec.id)

    except Exception as e:  # noqa: BLE001
      errors.append((spec.id, str(e)))

  return {
    "migrated": migrated,
    "skipped": skipped,
    "errors": errors,
  }


def main() -> None:
  """Execute migration with command-line interface."""
  # Parse simple arguments
  dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
  verbose = "--verbose" in sys.argv or "-v" in sys.argv

  mode = "DRY RUN" if dry_run else "LIVE RUN"
  print(f"=== Stub Status Migration ({mode}) ===\n")

  # Run migration
  results = migrate_stub_status(dry_run=dry_run)

  # Report results
  print(f"Migrated: {len(results['migrated'])} specs")
  if verbose or not dry_run:
    for spec_id in results["migrated"]:
      symbol = "→" if dry_run else "✓"
      print(f"  {symbol} {spec_id}")

  if results["skipped"] and verbose:
    print(f"\nSkipped: {len(results['skipped'])} specs")
    for spec_id, reason in results["skipped"]:
      print(f"  - {spec_id}: {reason}")

  if results["errors"]:
    print(f"\nErrors: {len(results['errors'])} specs", file=sys.stderr)
    for spec_id, error in results["errors"]:
      print(f"  ✗ {spec_id}: {error}", file=sys.stderr)

  print(f"\n{'Would migrate' if dry_run else 'Migrated'} {len(results['migrated'])} "
        f"draft specs to stub status")

  if dry_run:
    print("\nRun without --dry-run to apply changes")

  sys.exit(0 if not results["errors"] else 1)


if __name__ == "__main__":
  main()
