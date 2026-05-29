"""Spec requirements migration: prose bullets → structured block.

Per DEC-138-12 this module imports only stdlib +
``spec_driver.migrations._helpers`` + pyyaml.
All constants are frozen-local copies of runtime values.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import yaml

from spec_driver.migrations._helpers import atomic_write, split_frontmatter

# ---------------------------------------------------------------------------
# Frozen-local constants (must match runtime parser/block values)
# ---------------------------------------------------------------------------

_REQUIREMENTS_MARKER = "supekku:spec.requirements@v1"
_REQUIREMENTS_SCHEMA = "supekku.spec.requirements"
_REQUIREMENTS_VERSION = 1

_LIFECYCLE_VALUES = frozenset({
  "pending", "in-progress", "active",
  "retired", "deprecated", "superseded",
})

_KIND_CANONICAL = {"functional", "non-functional"}
_KIND_ALIAS_MAP = {"FR": "functional", "NF": "non-functional", "NFR": "non-functional"}

# Frozen copy of parser._REQUIREMENT_LINE (spec bullet format only).
# Heading-form backlog requirements excluded per DEC-140-08.
_REQUIREMENT_LINE = re.compile(
  r"^\s*[-*]\s*\*{0,2}\s*(?:[A-Z]+-\d{3}\.)?("
  r"FR|NF)-(\d{3})\s*\*{0,2}\s*(?:\(([^)]+)\))?"
  r"(?:\[([^\]]*)\])?\s*[:\-–]\s*(.+)$",
  re.IGNORECASE,
)

_BLOCK_DETECT = re.compile(
  r"```(?:yaml|yml)\s+" + re.escape(_REQUIREMENTS_MARKER) + r"\n(.*?)```",
  re.DOTALL,
)

# Drift kinds (stable strings for ledger entries).
DRIFT_REQUIREMENT_UNPARSEABLE = "requirement_unparseable"
DRIFT_DESCRIPTION_PLACEHOLDER = "description_placeholder"
DRIFT_ACCEPTANCE_PLACEHOLDER = "acceptance_placeholder"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DriftEntry:
  """Single drift observation from migration."""

  spec_id: str
  kind: str
  detail: str


@dataclass(frozen=True)
class MigrationResult:
  """Result of migrating one spec file."""

  spec_id: str
  text: str
  changed: bool
  requirements_count: int
  drift: list[DriftEntry] = field(default_factory=list)


@dataclass(frozen=True)
class ParsedRequirement:
  """Requirement extracted from prose bullet."""

  id: str
  title: str
  kind: str
  category: str | None = None
  tags: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def _parse_requirements(body: str) -> list[ParsedRequirement]:
  """Extract requirement entries from prose body using frozen regex."""
  results: list[ParsedRequirement] = []
  for line in body.splitlines():
    match = _REQUIREMENT_LINE.match(line)
    if not match:
      continue
    prefix, number, category, tags_raw, title = match.groups()
    kind_prefix = prefix.upper()
    kind = _KIND_ALIAS_MAP.get(kind_prefix, "functional")
    tags = (
      sorted(t.strip() for t in tags_raw.split(",") if t.strip())
      if tags_raw else []
    )
    results.append(ParsedRequirement(
      id=f"{kind_prefix}-{number}",
      title=title.strip(),
      kind=kind,
      category=category.strip() if category else None,
      tags=tags,
    ))
  return results


def _is_requirement_like_line(line: str) -> bool:
  """Return True if line plausibly attempts to define a requirement."""
  bare_id = re.compile(r"\b(?:[A-Z]+-\d{3}\.)?(FR|NF)-\d{3}\b", re.IGNORECASE)
  crossref = re.compile(r"\bper\s+(?:[A-Z]+-\d{3}\.)?(FR|NF)-\d{3}\b", re.IGNORECASE)
  in_parens = re.compile(
    r"\([^)]*\b(?:[A-Z]+-\d{3}\.)?(FR|NF)-\d{3}\b[^)]*\)", re.IGNORECASE
  )
  if not bare_id.search(line):
    return False
  if crossref.search(line):
    return False
  stripped = in_parens.sub("", line)
  return bool(bare_id.search(stripped))


# ---------------------------------------------------------------------------
# Rendering (frozen-local copy of render_spec_requirements_block)
# ---------------------------------------------------------------------------


def _yaml_scalar(value: str) -> str:
  """Quote a YAML scalar if it contains characters that need quoting."""
  if any(c in value for c in ":{}[]#&*!|>'\",@`"):
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'
  return value


def _render_block(spec_id: str, requirements: list[ParsedRequirement]) -> str:
  """Render a supekku:spec.requirements@v1 block from parsed requirements."""
  lines = [
    f"```yaml {_REQUIREMENTS_MARKER}",
    f"schema: {_REQUIREMENTS_SCHEMA}",
    f"version: {_REQUIREMENTS_VERSION}",
    f"spec: {spec_id}",
    "requirements:",
  ]

  if not requirements:
    lines[-1] = "requirements: []"
  else:
    for req in requirements:
      lines.append(f"  - id: {req.id}")
      lines.append(f"    title: {_yaml_scalar(req.title)}")
      lines.append("    lifecycle: pending")
      lines.append(f"    kind: {req.kind}")
      if req.category:
        lines.append(f"    category: {_yaml_scalar(req.category)}")
      lines.append('    description: ""')
      lines.append("    acceptance_criteria: []")
      if req.tags:
        tag_str = ", ".join(req.tags)
        lines.append(f"    tags: [{tag_str}]")

  lines.append("```")
  return "\n".join(lines)


# ---------------------------------------------------------------------------
# Block insertion
# ---------------------------------------------------------------------------

_FIRST_HEADING = re.compile(r"^#{1,6}\s", re.MULTILINE)


def _insert_block(text: str, block: str) -> str:
  """Insert block after frontmatter, before first heading."""
  yaml_text, body = split_frontmatter(text)
  if not yaml_text:
    return f"{block}\n\n{text}"

  heading_match = _FIRST_HEADING.search(body)
  if heading_match:
    before = body[:heading_match.start()].rstrip()
    after = body[heading_match.start():]
    joiner = "\n\n" if before else "\n"
    new_body = f"{before}{joiner}{block}\n\n{after}"
  else:
    trimmed = body.rstrip()
    joiner = "\n\n" if trimmed else "\n"
    new_body = f"{trimmed}{joiner}{block}\n"

  return f"---\n{yaml_text}---\n{new_body}"


# ---------------------------------------------------------------------------
# Guard
# ---------------------------------------------------------------------------


def has_requirements_block(text: str) -> bool:
  """Return True if text already contains a spec.requirements block."""
  return bool(_BLOCK_DETECT.search(text))


# ---------------------------------------------------------------------------
# Post-write validation
# ---------------------------------------------------------------------------


def _validate_written_block(text: str, spec_id: str) -> list[str]:
  """Validate that written file contains a parseable requirements block."""
  errors: list[str] = []
  matches = list(_BLOCK_DETECT.finditer(text))
  if not matches:
    errors.append("no spec.requirements block found after write")
    return errors
  if len(matches) > 1:
    errors.append("multiple spec.requirements blocks found after write")
  raw = matches[0].group(1)
  try:
    data = yaml.safe_load(raw)
  except yaml.YAMLError as exc:
    errors.append(f"block YAML unparseable after write: {exc}")
    return errors
  if not isinstance(data, dict):
    errors.append("block does not parse to mapping")
    return errors
  if data.get("spec") != spec_id:
    errors.append(f"spec field mismatch: expected {spec_id}, got {data.get('spec')}")
  if "requirements" not in data:
    errors.append("missing requirements array in block")
  return errors


# ---------------------------------------------------------------------------
# Drift detection
# ---------------------------------------------------------------------------


def _detect_drift(
  spec_id: str,
  body: str,
  parsed: list[ParsedRequirement],
) -> list[DriftEntry]:
  """Detect unparseable requirement-like lines and placeholder fields."""
  drift: list[DriftEntry] = []

  for line in body.splitlines():
    if _is_requirement_like_line(line) and not _REQUIREMENT_LINE.match(line):
      drift.append(DriftEntry(
        spec_id=spec_id,
        kind=DRIFT_REQUIREMENT_UNPARSEABLE,
        detail=f"unparseable requirement-like line: {line.strip()[:120]}",
      ))

  for req in parsed:
    drift.append(DriftEntry(
      spec_id=spec_id,
      kind=DRIFT_DESCRIPTION_PLACEHOLDER,
      detail=f"{req.id}: description is empty placeholder",
    ))
    drift.append(DriftEntry(
      spec_id=spec_id,
      kind=DRIFT_ACCEPTANCE_PLACEHOLDER,
      detail=f"{req.id}: acceptance_criteria is empty placeholder",
    ))

  return drift


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def migrate_spec(
  spec_id: str,
  text: str,
) -> MigrationResult:
  """Transform a spec file: parse prose requirements → insert block.

  Pure function. Does not read/write files.
  """
  if has_requirements_block(text):
    return MigrationResult(
      spec_id=spec_id, text=text, changed=False,
      requirements_count=0,
    )

  _, body = split_frontmatter(text)
  parsed = _parse_requirements(body)

  block = _render_block(spec_id, parsed)
  new_text = _insert_block(text, block)
  drift = _detect_drift(spec_id, body, parsed)

  return MigrationResult(
    spec_id=spec_id,
    text=new_text,
    changed=True,
    requirements_count=len(parsed),
    drift=drift,
  )


def apply_migration(
  spec_path: Path,
  spec_id: str,
  *,
  dry_run: bool = False,
) -> MigrationResult:
  """Read spec file, migrate, optionally write.

  On write failure or post-write validation failure, reverts to original.
  """
  original = spec_path.read_text(encoding="utf-8")
  result = migrate_spec(spec_id, original)

  if not result.changed or dry_run:
    return result

  atomic_write(spec_path, result.text)

  written = spec_path.read_text(encoding="utf-8")
  errors = _validate_written_block(written, spec_id)
  if errors:
    atomic_write(spec_path, original)
    raise ValueError(
      f"post-write validation failed for {spec_id}, reverted: "
      + "; ".join(errors)
    )

  return result


def write_drift_ledger(
  drift_dir: Path,
  spec_id: str,
  entries: list[DriftEntry],
  delta_ref: str = "DE-140",
) -> Path | None:
  """Write drift ledger entries to a DL-NNN file."""
  if not entries:
    return None

  drift_dir.mkdir(parents=True, exist_ok=True)
  next_id = _next_drift_id(drift_dir)
  slug = f"de_140_migrate_{spec_id.lower().replace('-', '_')}"
  filename = f"DL-{next_id:03d}-{slug}.md"
  path = drift_dir / filename

  timestamp = datetime.now(tz=UTC).strftime("%Y-%m-%d")
  lines = [
    "---",
    f"id: DL-{next_id:03d}",
    f"name: DE-140 requirements migration {spec_id}",
    f"created: '{timestamp}'",
    f"updated: '{timestamp}'",
    "status: open",
    "kind: drift_ledger",
    f"delta_ref: {delta_ref}",
    "---",
    "",
    f"# DL-{next_id:03d} — DE-140 requirements migration {spec_id}",
    "",
    f"Drift entries from requirements migration of {spec_id}.",
    "",
    "## Entries",
    "",
  ]

  for i, entry in enumerate(entries, 1):
    body = yaml.safe_dump(
      {
        "target": entry.spec_id,
        "drift_kind": entry.kind,
        "detail": entry.detail,
        "disposition": "open",
        "owner": "unassigned",
        "status": "open",
      },
      sort_keys=False,
      allow_unicode=True,
    ).rstrip("\n")
    lines.extend([
      f"### DL-{next_id:03d}.{i:03d}: {entry.kind} — {entry.spec_id}",
      "",
      "```yaml",
      body,
      "```",
      "",
    ])

  atomic_write(path, "\n".join(lines))
  return path


def _next_drift_id(drift_dir: Path) -> int:
  """Allocate next sequential DL-NNN ID."""
  max_id = 0
  pattern = re.compile(r"^DL-(\d{3})")
  for child in drift_dir.iterdir():
    match = pattern.match(child.name)
    if match:
      max_id = max(max_id, int(match.group(1)))
  return max_id + 1
