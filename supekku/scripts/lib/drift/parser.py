"""Drift ledger body parser — heading split with fenced YAML extraction.

Parses a drift ledger markdown body into structured DriftEntry models.
Follows DEC-065-02 (fenced YAML blocks) and DEC-065-03 (section-based parser).

Parser contract (DR-065):
- Fences processed before headings (fence/heading precedence)
- Malformed YAML → warning, entry with _parse_error in extra
- Missing required nested keys → warning, malformed record skipped
- Duplicate entry IDs → warning, both preserved
- No YAML block → warning, heading-only entry
- Multiple YAML blocks → first parsed, rest is analysis
"""

from __future__ import annotations

import logging
import re
from typing import Any

import yaml

from .models import Claim, DiscoveredBy, DriftEntry, Source

logger = logging.getLogger(__name__)

# Entry heading pattern: ### DL-NNN.MMM: title
_ENTRY_HEADING_RE = re.compile(r"^###\s+(DL-\d+\.\d+):\s*(.+)$", re.MULTILINE)

# Fenced code block pattern (any language tag)
_FENCE_RE = re.compile(r"^```\w*\s*$", re.MULTILINE)


def parse_ledger_body(body: str) -> tuple[str, list[DriftEntry]]:
  """Parse a drift ledger body into freeform body and entries.

  Args:
    body: markdown body after frontmatter removal.

  Returns:
    (freeform_body, entries) — freeform_body is content before the first
    entry heading; entries are parsed DriftEntry models.
  """
  freeform_body, entry_sections = _split_sections(body)

  entries: list[DriftEntry] = []
  seen_ids: set[str] = set()

  for heading, section_body in entry_sections:
    entry = _parse_entry_section(heading, section_body)
    if entry is None:
      continue
    if entry.id in seen_ids:
      logger.warning("Duplicate entry ID %r in ledger", entry.id)
    seen_ids.add(entry.id)
    entries.append(entry)

  return freeform_body.strip(), entries


def _split_sections(
  body: str,
) -> tuple[str, list[tuple[str, str]]]:
  """Split body on ### headings, respecting fenced code blocks.

  Returns (freeform_body, entry_sections) where entry_sections are
  (heading_text, section_body) tuples.

  Fence/heading precedence (DEC-065-03): content inside fenced code
  blocks is opaque — ### lines inside fences are not entry boundaries.
  """
  lines = body.split("\n")
  in_fence = False
  entry_sections: list[tuple[str, str]] = []
  current_lines: list[str] = []
  current_heading: str | None = None
  freeform_lines: list[str] | None = None

  for line in lines:
    # Track fence state
    if _FENCE_RE.match(line):
      in_fence = not in_fence
      current_lines.append(line)
      continue

    # Only split on ### headings outside fences
    if not in_fence and line.startswith("### "):
      # Save the previous section
      if current_heading is None:
        freeform_lines = current_lines
      else:
        entry_sections.append((current_heading, "\n".join(current_lines)))
      current_lines = []
      current_heading = line
      continue

    current_lines.append(line)

  # Save the final section
  if current_heading is None:
    freeform_lines = current_lines
  else:
    entry_sections.append((current_heading, "\n".join(current_lines)))

  freeform = "\n".join(freeform_lines) if freeform_lines else ""
  return freeform, entry_sections


def _parse_entry_section(heading: str, section_body: str) -> DriftEntry | None:
  """Parse a single entry section into a DriftEntry.

  Args:
    heading: the ### heading line
    section_body: content after the heading

  Returns:
    DriftEntry or None if the heading doesn't match the expected pattern.
  """
  match = _ENTRY_HEADING_RE.match(heading)
  if not match:
    logger.warning("Entry heading does not match expected pattern: %r", heading)
    return None

  entry_id = match.group(1)
  title = match.group(2).strip()

  # Extract the first fenced YAML block
  yaml_data, analysis = _extract_yaml_block(section_body)

  if yaml_data is None:
    logger.warning("No YAML block found for entry %s", entry_id)
    return DriftEntry(id=entry_id, title=title)

  return _build_entry(entry_id, title, yaml_data, analysis)


def _extract_yaml_block(section_body: str) -> tuple[dict[str, Any] | None, str]:
  """Extract the first fenced YAML block from a section.

  Returns:
    (yaml_data, analysis) — yaml_data is the parsed dict (or None),
    analysis is the remaining markdown outside the fence.
  """
  lines = section_body.split("\n")
  in_fence = False
  fence_lines: list[str] = []
  before_fence: list[str] = []
  after_fence: list[str] = []
  fence_found = False
  fence_closed = False

  for line in lines:
    if not fence_found and not in_fence and _FENCE_RE.match(line):
      in_fence = True
      fence_found = True
      continue

    if in_fence and not fence_closed and _FENCE_RE.match(line):
      in_fence = False
      fence_closed = True
      continue

    if in_fence and not fence_closed:
      fence_lines.append(line)
    elif not fence_found:
      before_fence.append(line)
    else:
      after_fence.append(line)

  if not fence_found:
    return None, section_body.strip()

  # Parse YAML
  yaml_text = "\n".join(fence_lines)
  try:
    data = yaml.safe_load(yaml_text)
    if not isinstance(data, dict):
      logger.warning("YAML block is not a mapping: %r", type(data).__name__)
      return None, section_body.strip()
  except yaml.YAMLError as exc:
    logger.warning("Malformed YAML in entry: %s", exc)
    return {"_parse_error": str(exc)}, _join_analysis(before_fence, after_fence)

  return data, _join_analysis(before_fence, after_fence)


def _join_analysis(before: list[str], after: list[str]) -> str:
  """Join before/after fence content into analysis text."""
  parts = []
  before_text = "\n".join(before).strip()
  after_text = "\n".join(after).strip()
  if before_text:
    parts.append(before_text)
  if after_text:
    parts.append(after_text)
  return "\n\n".join(parts)


def _build_entry(
  entry_id: str,
  title: str,
  data: dict[str, Any],
  analysis: str,
) -> DriftEntry:
  """Construct a DriftEntry from parsed YAML data.

  Handles _parse_error from malformed YAML. Builds typed substructures
  with warnings for malformed records (DEC-065-06).
  """
  if "_parse_error" in data:
    return DriftEntry(
      id=entry_id,
      title=title,
      extra=data,
    )

  # Extract known fields, collect extras
  known_keys = {
    "status",
    "entry_type",
    "severity",
    "topic",
    "owner",
    "sources",
    "claims",
    "assessment",
    "resolution_path",
    "resolution_ref",
    "affected_artifacts",
    "discovered_by",
    "analysis",
    "evidence",
  }
  extra = {k: v for k, v in data.items() if k not in known_keys}

  return DriftEntry(
    id=entry_id,
    title=title,
    status=data.get("status", "open"),
    entry_type=data.get("entry_type", ""),
    severity=data.get("severity", ""),
    topic=data.get("topic", ""),
    owner=data.get("owner", ""),
    sources=_parse_sources(data.get("sources", []), entry_id),
    claims=_parse_claims(data.get("claims", []), entry_id),
    assessment=data.get("assessment", ""),
    resolution_path=data.get("resolution_path", ""),
    resolution_ref=data.get("resolution_ref", ""),
    affected_artifacts=data.get("affected_artifacts", []) or [],
    discovered_by=_parse_discovered_by(data.get("discovered_by"), entry_id),
    analysis=analysis or data.get("analysis", ""),
    evidence=data.get("evidence", []) or [],
    extra=extra,
  )


def _parse_sources(raw: list[Any], entry_id: str) -> list[Source]:
  """Parse source dicts into typed Source objects."""
  if not isinstance(raw, list):
    logger.warning("Entry %s: sources is not a list, skipping", entry_id)
    return []
  sources = []
  for item in raw:
    if not isinstance(item, dict):
      logger.warning("Entry %s: source item is not a dict, skipping", entry_id)
      continue
    kind = item.get("kind")
    ref = item.get("ref")
    if not kind:
      logger.warning("Entry %s: source missing 'kind', skipping", entry_id)
      continue
    if not ref:
      logger.warning("Entry %s: source missing 'ref', skipping", entry_id)
      continue
    sources.append(Source(kind=kind, ref=str(ref), note=str(item.get("note", ""))))
  return sources


def _parse_claims(raw: list[Any], entry_id: str) -> list[Claim]:
  """Parse claim dicts into typed Claim objects."""
  if not isinstance(raw, list):
    logger.warning("Entry %s: claims is not a list, skipping", entry_id)
    return []
  claims = []
  for item in raw:
    if not isinstance(item, dict):
      logger.warning("Entry %s: claim item is not a dict, skipping", entry_id)
      continue
    kind = item.get("kind")
    text = item.get("text")
    if not kind:
      logger.warning("Entry %s: claim missing 'kind', skipping", entry_id)
      continue
    if not text:
      logger.warning("Entry %s: claim missing 'text', skipping", entry_id)
      continue
    claims.append(Claim(kind=kind, text=str(text), label=str(item.get("label", ""))))
  return claims


def _parse_discovered_by(
  raw: dict[str, Any] | None, entry_id: str
) -> DiscoveredBy | None:
  """Parse discovered_by dict into typed DiscoveredBy object."""
  if raw is None:
    return None
  if not isinstance(raw, dict):
    logger.warning("Entry %s: discovered_by is not a dict, skipping", entry_id)
    return None
  kind = raw.get("kind")
  if not kind:
    logger.warning("Entry %s: discovered_by missing 'kind', skipping", entry_id)
    return None
  return DiscoveredBy(kind=kind, ref=str(raw.get("ref", "")))
