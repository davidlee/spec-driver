"""Dual-validate snapshot harness for DE-118 block-validator unification.

For each block instance in a `.spec-driver/` corpus, this harness invokes
both the hand-rolled validator (where one still exists) and the
``MetadataValidator(metadata, strict_unknown_keys=True)`` driven by the
block's metadata declaration. Disagreement at the verdict level
(accept/reject) signals drift between the two paths.

CLI:

    python -m supekku.scripts.lib.blocks.metadata.snapshot_compare --root .

Exit code:

    0 — every block agreed (or had no hand-rolled counterpart left).
    1 — at least one disagreement (or malformed-YAML failure).

Lifecycle (DE-118 P02 P04 OQ-HARNESS-LIFECYCLE): manual run only as of
P02; ownership / re-run trigger settled before delta closure.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from supekku.scripts.lib.blocks.relationships import (
  RelationshipsBlock,
  RelationshipsBlockValidator,
)
from supekku.scripts.lib.blocks.revision import RevisionBlockValidator
from supekku.scripts.lib.blocks.schema_registry import BLOCK_SCHEMAS, BlockSchema
from supekku.scripts.lib.blocks.yaml_utils import make_block_pattern
from supekku.scripts.lib.core.spec_utils import load_markdown_file

from .validator import MetadataValidator

# Adapter signature: (data: dict, frontmatter_id: str | None) -> list[str of errors]
HandRolledAdapter = Callable[[dict[str, Any], str | None], list[str]]


def _adapt_revision(data: dict[str, Any], _fid: str | None) -> list[str]:
  return [str(e) for e in RevisionBlockValidator().validate(data)]


def _adapt_spec_relationships(data: dict[str, Any], fid: str | None) -> list[str]:
  block = RelationshipsBlock(raw_yaml="", data=data)
  return RelationshipsBlockValidator().validate(block, spec_id=fid)


# Block types that still have a hand-rolled validator (DE-118 P02 baseline).
# P03 swap commits delete the corresponding entry as each validator retires.
HAND_ROLLED_ADAPTERS: dict[str, HandRolledAdapter] = {
  "revision.change": _adapt_revision,
  "spec.relationships": _adapt_spec_relationships,
}


@dataclass
class Disagreement:
  """A block where hand-rolled and metadata-driven validators disagreed."""

  file: Path
  block_type: str
  hand_rolled_errors: list[str]
  metadata_errors: list[str]

  @property
  def hand_rolled_passed(self) -> bool:
    """True when the hand-rolled validator accepted the block."""
    return not self.hand_rolled_errors

  @property
  def metadata_passed(self) -> bool:
    """True when the metadata-driven validator accepted the block."""
    return not self.metadata_errors

  def render(self) -> str:
    """Render the disagreement as a human-readable multi-line string."""
    lines = [
      f"DISAGREEMENT: {self.file} [{self.block_type}]",
      f"  hand-rolled: {'PASS' if self.hand_rolled_passed else 'FAIL'}",
    ]
    for err in self.hand_rolled_errors:
      lines.append(f"    - {err}")
    lines.append(f"  metadata:    {'PASS' if self.metadata_passed else 'FAIL'}")
    for err in self.metadata_errors:
      lines.append(f"    - {err}")
    return "\n".join(lines)


@dataclass
class MalformedBlock:
  """A YAML block that failed to parse — surfaced separately from disagreements."""

  file: Path
  block_type: str
  reason: str

  def render(self) -> str:
    """Render the malformed-YAML record as a single-line diagnostic string."""
    return f"MALFORMED: {self.file} [{self.block_type}]: {self.reason}"


@dataclass
class Report:
  """Result of a corpus run."""

  files_scanned: int = 0
  blocks_dual_validated: int = 0
  blocks_metadata_only: int = 0
  disagreements: list[Disagreement] = field(default_factory=list)
  malformed: list[MalformedBlock] = field(default_factory=list)

  @property
  def ok(self) -> bool:
    """Run is OK iff zero verdict disagreements.

    Malformed YAML is a pre-existing data-quality concern surfaced for
    visibility but orthogonal to validator drift; it does not gate.
    """
    return not self.disagreements


def _scan_file(
  file: Path,
) -> Iterable[tuple[str, dict[str, Any] | None, BlockSchema, str]]:
  """Yield (block_type, parsed_data_or_None, schema, raw_yaml) for each block.

  ``parsed_data is None`` indicates malformed YAML; ``raw_yaml`` carries the
  unparsed text for diagnostics.
  """
  try:
    text = file.read_text(encoding="utf-8")
  except OSError:
    return
  for block_type, schema in BLOCK_SCHEMAS.items():
    pattern = make_block_pattern(schema.marker)
    for match in pattern.finditer(text):
      raw = match.group(1)
      try:
        parsed = yaml.safe_load(raw) or {}
      except yaml.YAMLError as exc:
        yield (block_type, None, schema, f"YAML parse error: {exc}")
        continue
      if not isinstance(parsed, dict):
        yield (block_type, None, schema, "block YAML did not parse to a mapping")
        continue
      yield (block_type, parsed, schema, raw)


def _frontmatter_id(file: Path) -> str | None:
  """Read frontmatter and return ``id`` field, if any."""
  try:
    frontmatter, _ = load_markdown_file(file)
  except (OSError, ValueError):
    return None
  fid = frontmatter.get("id")
  return str(fid).strip() if fid is not None else None


def compare_block(
  file: Path,
  block_type: str,
  data: dict[str, Any],
  schema: BlockSchema,
  frontmatter_id: str | None,
) -> Disagreement | None:
  """Dual-validate a single block; return ``Disagreement`` on verdict mismatch."""
  adapter = HAND_ROLLED_ADAPTERS.get(block_type)
  if adapter is None or schema.metadata is None:
    return None
  hand_rolled_errors = adapter(data, frontmatter_id)
  metadata_errors = [
    str(e)
    for e in MetadataValidator(schema.metadata, strict_unknown_keys=True).validate(data)
  ]
  hand_rolled_passed = not hand_rolled_errors
  metadata_passed = not metadata_errors
  if hand_rolled_passed != metadata_passed:
    return Disagreement(
      file=file,
      block_type=block_type,
      hand_rolled_errors=hand_rolled_errors,
      metadata_errors=metadata_errors,
    )
  return None


def run(root: Path) -> Report:
  """Run the harness against ``<root>/.spec-driver/`` and return a report."""
  report = Report()
  corpus = root / ".spec-driver"
  if not corpus.is_dir():
    return report
  for md in sorted(corpus.rglob("*.md")):
    report.files_scanned += 1
    fid = _frontmatter_id(md)
    for block_type, parsed, schema, raw_or_reason in _scan_file(md):
      if parsed is None:
        report.malformed.append(
          MalformedBlock(file=md, block_type=block_type, reason=raw_or_reason)
        )
        continue
      if block_type in HAND_ROLLED_ADAPTERS:
        report.blocks_dual_validated += 1
        d = compare_block(md, block_type, parsed, schema, fid)
        if d is not None:
          report.disagreements.append(d)
      else:
        report.blocks_metadata_only += 1
  return report


def _print_report(report: Report) -> None:
  """Print a corpus run summary to stdout."""
  print(
    f"snapshot-compare: scanned {report.files_scanned} files, "
    f"{report.blocks_dual_validated} dual-validated, "
    f"{report.blocks_metadata_only} metadata-only."
  )
  for m in report.malformed:
    print(m.render())
  for d in report.disagreements:
    print(d.render())
  if report.ok:
    print("snapshot-compare: OK (zero disagreements).")
  else:
    print(
      f"snapshot-compare: {len(report.disagreements)} disagreements, "
      f"{len(report.malformed)} malformed."
    )


def main(argv: list[str] | None = None) -> int:
  """CLI entrypoint: parse ``--root``, run the harness, print the report."""
  parser = argparse.ArgumentParser(
    prog="snapshot_compare",
    description="DE-118 dual-validate harness for block validators.",
  )
  parser.add_argument(
    "--root",
    type=Path,
    default=Path(),
    help="Repository root containing .spec-driver/ (default: current directory).",
  )
  args = parser.parse_args(argv)
  report = run(args.root)
  _print_report(report)
  return 0 if report.ok else 1


if __name__ == "__main__":
  sys.exit(main())
