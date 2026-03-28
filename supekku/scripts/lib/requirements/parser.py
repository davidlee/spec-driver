"""Requirement extraction and parsing from spec content."""

from __future__ import annotations

import logging
import re
import sys
from collections.abc import Iterator, Mapping
from typing import TYPE_CHECKING, Any

from supekku.scripts.lib.core.spec_utils import load_markdown_file

from .lifecycle import STATUS_PENDING
from .models import RequirementRecord

if TYPE_CHECKING:
  from pathlib import Path

  from supekku.scripts.lib.specs.registry import SpecRegistry

logger = logging.getLogger(__name__)

# Updated pattern to support both formats:
# - **FR-001**: Short format (legacy)
# - **PROD-010.FR-001**: Fully-qualified format (current standard)
# Optional tags in square brackets after category: **FR-001**(cat)[tag1, tag2]: Title
_REQUIREMENT_LINE = re.compile(
  r"^\s*[-*]\s*\*{0,2}\s*(?:[A-Z]+-\d{3}\.)?("
  r"FR|NF)-(\d{3})\s*\*{0,2}\s*(?:\(([^)]+)\))?"
  r"(?:\[([^\]]*)\])?\s*[:\-–]\s*(.+)$",
  re.IGNORECASE,
)

# Heading format for backlog items: ### FR-016.001: Title
# Matches dotted format only (NNN.MMM) — no overlap with spec bullet format.
_REQUIREMENT_HEADING = re.compile(
  r"^\s*#{1,4}\s+(FR|NF)-(\d{3})\.(\d{3})\s*[:\-–]\s*(.+)$",
  re.IGNORECASE,
)

# Cross-reference patterns: "per FR-007", "per PROD-004.FR-007".
# These mention a requirement without defining it.
_REQUIREMENT_CROSSREF = re.compile(
  r"\bper\s+(?:[A-Z]+-\d{3}\.)?(FR|NF)-\d{3}\b",
  re.IGNORECASE,
)

# Parenthetical mention: "(…FR-007…)" or "(…PROD-004.FR-007…)".
# When all FR/NF references on a line are inside parentheses, the line
# is citing requirements, not defining them.
_REQUIREMENT_IN_PARENS = re.compile(
  r"\([^)]*\b(?:[A-Z]+-\d{3}\.)?(FR|NF)-\d{3}\b[^)]*\)",
  re.IGNORECASE,
)

_BARE_REQUIREMENT_ID = re.compile(
  r"\b(?:[A-Z]+-\d{3}\.)?(FR|NF)-\d{3}\b",
  re.IGNORECASE,
)


def _has_frontmatter_requirement_definitions(fm: Mapping[str, Any]) -> list[dict]:
  """Return frontmatter entries that look like requirement definitions.

  Detects a ``requirements:`` key whose value is a list of dicts containing
  ``id`` or ``description`` keys — the pattern agents use when they
  incorrectly define requirements in YAML frontmatter instead of body
  bullets.  The ``spec.relationships`` block uses a structurally distinct
  dict with ``primary``/``collaborators`` keys and is not matched.
  """
  raw = fm.get("requirements")
  if not isinstance(raw, list):
    return []
  return [
    entry
    for entry in raw
    if isinstance(entry, dict) and ("id" in entry or "description" in entry)
  ]


def count_requirement_like_lines(body: str) -> int:
  """Count lines in *body* that plausibly define a requirement.

  Public API for callers that need a quick sanity count without running
  full extraction.  Uses the same heuristic as the parser's internal
  diagnostics.
  """
  return sum(1 for line in body.splitlines() if _is_requirement_like_line(line))


def _is_requirement_like_line(line: str) -> bool:
  """Return True if *line* plausibly attempts to define a requirement.

  A line is "requirement-like" if it contains an FR/NF-xxx ID and the
  ID is not purely a cross-reference.  Cross-reference patterns:
  - "per FR-007" / "per PROD-004.FR-007"
  - All IDs on the line are inside parentheses

  Lines with no FR/NF ID at all return False.
  """
  if not _BARE_REQUIREMENT_ID.search(line):
    return False

  # "per <ID>" is a citation, not a definition
  if _REQUIREMENT_CROSSREF.search(line):
    return False

  # If every FR/NF ID on the line is inside parentheses, it's a citation
  stripped = _REQUIREMENT_IN_PARENS.sub("", line)
  return bool(_BARE_REQUIREMENT_ID.search(stripped))


def _load_breakout_metadata(
  spec_path: Path,
) -> dict[str, dict[str, Any]]:
  """Load metadata from breakout requirement files under a spec.

  Scans ``spec_path.parent / "requirements"`` for ``*.md`` files and
  extracts ``tags``, ``ext_id``, and ``ext_url`` from their frontmatter.

  Returns:
    Mapping from qualified requirement ID (e.g. ``SPEC-100.FR-010``)
    to a dict of metadata fields.
  """
  requirements_dir = spec_path.parent / "requirements"
  if not requirements_dir.is_dir():
    return {}
  result: dict[str, dict[str, Any]] = {}
  for file in requirements_dir.glob("*.md"):
    try:
      fm, _ = load_markdown_file(file)
    except (OSError, ValueError):
      continue
    req_id = str(fm.get("id", "")).strip()
    if not req_id:
      continue
    meta: dict[str, Any] = {}
    fm_tags = fm.get("tags")
    if isinstance(fm_tags, list):
      meta["tags"] = [str(t) for t in fm_tags if str(t).strip()]
    fm_ext_id = fm.get("ext_id")
    if fm_ext_id:
      meta["ext_id"] = str(fm_ext_id)
    fm_ext_url = fm.get("ext_url")
    if fm_ext_url:
      meta["ext_url"] = str(fm_ext_url)
    if meta:
      result[req_id] = meta
  return result


def _records_from_frontmatter(
  spec_id: str,
  frontmatter: Any,
  body: str,
  spec_path: Path,
  repo_root: Path,
) -> Iterator[RequirementRecord]:
  """Extract requirement records from spec frontmatter and body."""
  data = getattr(frontmatter, "data", frontmatter)
  mapping = dict(data) if isinstance(data, Mapping) else {}
  mapping.setdefault("id", spec_id)

  # Warn if frontmatter contains requirement-definition-shaped entries
  fm_defs = _has_frontmatter_requirement_definitions(mapping)
  if fm_defs:
    logger.info(
      "Spec %s at %s: frontmatter contains a 'requirements:' array with %d "
      "entries that will not be indexed. Requirements must be defined as body "
      "bullets: '- **FR-001**: Title'.",
      spec_id,
      spec_path.name,
      len(fm_defs),
    )
  breakout_meta = _load_breakout_metadata(spec_path)
  for record in _records_from_content(
    spec_id,
    mapping,
    body,
    spec_path,
    repo_root,
  ):
    meta = breakout_meta.get(record.uid, {})
    if meta:
      if "tags" in meta:
        record.tags = sorted(set(record.tags) | set(meta["tags"]))
      if "ext_id" in meta:
        record.ext_id = meta["ext_id"]
      if "ext_url" in meta:
        record.ext_url = meta["ext_url"]
    yield record


def _records_from_content(
  spec_id: str,
  _frontmatter: Mapping[str, Any],
  body: str,
  spec_path: Path,
  repo_root: Path,
) -> Iterator[RequirementRecord]:
  """Extract requirement records from spec body content.

  Logs warnings if requirement-like lines are found but not extracted.
  """
  try:
    path = spec_path.relative_to(repo_root).as_posix()
  except ValueError:
    path = spec_path.as_posix()

  requirement_like_lines: list[str] = []
  extracted_count = 0
  # Track UIDs to detect collisions (e.g., compound IDs FR-012-01 and
  # FR-012-02 both parsing as FR-012).
  seen_uids: dict[str, str] = {}  # uid → first source line

  for line in body.splitlines():
    # Track lines that plausibly *define* a requirement for diagnostics.
    if _is_requirement_like_line(line):
      requirement_like_lines.append(line.strip())

    # Try bullet format first (spec requirements)
    match = _REQUIREMENT_LINE.match(line)
    if match:
      extracted_count += 1
      prefix, number, category, tags_raw, title = match.groups()
      label = f"{prefix.upper()}-{number}"
      uid = f"{spec_id}.{label}"

      # Collision detection — same UID extracted from multiple lines
      if uid in seen_uids:
        logger.info(
          "Spec %s: duplicate requirement ID %s extracted from lines:\n"
          "  First:  '%s'\n"
          "  Second: '%s'\n"
          "Compound IDs (FR-NNN-NNN) are not supported. "
          "Use sequential IDs: FR-001, FR-002, ...",
          spec_id,
          label,
          seen_uids[uid],
          line.strip(),
        )
      else:
        seen_uids[uid] = line.strip()
      kind = "functional" if label.startswith("FR-") else "non-functional"
      inline_category = category.strip() if category else None
      frontmatter_category = _frontmatter.get("category")
      final_category = inline_category or frontmatter_category
      tags = (
        sorted(t.strip() for t in tags_raw.split(",") if t.strip()) if tags_raw else []
      )

      yield RequirementRecord(
        uid=uid,
        label=label,
        title=title.strip(),
        specs=[spec_id],
        primary_spec=spec_id,
        kind=kind,
        category=final_category,
        status=STATUS_PENDING,
        tags=tags,
        path=path,
      )
      continue

    # Try heading format (backlog dotted requirements)
    heading_match = _REQUIREMENT_HEADING.match(line)
    if heading_match:
      extracted_count += 1
      prefix, artifact_num, seq_num, title = heading_match.groups()
      label = f"{prefix.upper()}-{artifact_num}.{seq_num}"
      uid = f"{spec_id}.{label}"
      kind = "functional" if label.startswith("FR-") else "non-functional"

      if uid in seen_uids:
        logger.info(
          "Spec %s: duplicate requirement ID %s extracted from lines:\n"
          "  First:  '%s'\n"
          "  Second: '%s'",
          spec_id,
          label,
          seen_uids[uid],
          line.strip(),
        )
      else:
        seen_uids[uid] = line.strip()

      yield RequirementRecord(
        uid=uid,
        label=label,
        title=title.strip(),
        specs=[spec_id],
        primary_spec=spec_id,
        kind=kind,
        status=STATUS_PENDING,
        path=path,
      )

  # Warn if requirement-like lines exceed extracted count (was: == 0 only)
  if requirement_like_lines and extracted_count < len(requirement_like_lines):
    logger.warning(
      "Spec %s at %s: Found %d requirement-like lines but extracted %d. "
      "Expected format: '- **FR-001**: Title' or '- **SPEC-100.FR-001**: Title'. "
      "The label inside **bold** must be bare (no description). "
      "First unmatched line: %s",
      spec_id,
      spec_path.name,
      len(requirement_like_lines),
      extracted_count,
      requirement_like_lines[0][:80],
    )


def _requirements_from_spec(
  spec_path: Path,
  spec_id: str,
  repo_root: Path,
) -> Iterator[RequirementRecord]:
  """Extract requirements from a spec file on disk."""
  frontmatter, body = load_markdown_file(spec_path)
  yield from _records_from_content(
    spec_id,
    frontmatter,
    body,
    spec_path,
    repo_root,
  )


def _validate_extraction(
  spec_registry: SpecRegistry,
  seen: set[str],
) -> None:
  """Validate extraction results and warn about potential issues.

  Checks for specs with zero extracted requirements, which may indicate
  format issues or extraction failures.
  """
  for spec in spec_registry.all_specs():
    # Skip non-product/tech specs (like policies, standards)
    if spec.kind not in ("prod", "tech"):
      continue

    # Count requirements extracted from this spec
    extracted = [uid for uid in seen if uid.startswith(f"{spec.id}.")]

    if len(extracted) == 0:
      print(
        f"WARNING: Spec {spec.id} ({spec.kind}) has 0 extracted requirements. "
        f"Expected format: '- **FR-001**: Title' or '- **SPEC-100.FR-001**: Title' "
        f"(label inside **bold** must be bare — no description). "
        f"Check {spec.path.name}",
        file=sys.stderr,
      )
      logger.warning(
        "Spec %s has no extracted requirements - possible format mismatch",
        spec.id,
      )
