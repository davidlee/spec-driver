"""Utilities for parsing verification coverage YAML blocks."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import yaml

if TYPE_CHECKING:
  from pathlib import Path

COVERAGE_MARKER = "supekku:verification.coverage@v1"
COVERAGE_SCHEMA = "supekku.verification.coverage"
COVERAGE_VERSION = 1

# Valid verification artifact kinds
VALID_KINDS = {"VT", "VA", "VH"}

# Valid verification statuses
VALID_STATUSES = {"planned", "in-progress", "verified", "failed", "blocked"}

# ID patterns for validation
_VERIFICATION_ID = re.compile(r"^V[TAH]-\d{3,}$")
_SUBJECT_ID = re.compile(r"^(SPEC|PROD|IP|AUD)-\d{3,}(?:-[A-Z0-9]+)*$")
_REQUIREMENT_ID = re.compile(r"^(SPEC|PROD)-\d{3,}(?:-[A-Z0-9]+)*\.(FR|NFR)-[A-Z0-9-]+$")
_PHASE_ID = re.compile(r"^IP-\d{3,}(?:-[A-Z0-9]+)*\.PHASE-\d{2}$")


@dataclass(frozen=True)
class VerificationCoverageBlock:
  """Parsed YAML block containing verification coverage entries."""

  raw_yaml: str
  data: dict[str, Any]


class VerificationCoverageValidator:
  """Validator for verification coverage blocks."""

  def validate(
    self,
    block: VerificationCoverageBlock,
    *,
    subject_id: str | None = None,
  ) -> list[str]:
    """Validate coverage block against schema.

    Args:
      block: Parsed coverage block to validate.
      subject_id: Optional expected subject ID to match against.

    Returns:
      List of error messages (empty if valid).
    """
    errors: list[str] = []
    data = block.data

    # Validate schema and version
    if data.get("schema") != COVERAGE_SCHEMA:
      errors.append(
        f"coverage block must declare schema {COVERAGE_SCHEMA}",
      )
    if data.get("version") != COVERAGE_VERSION:
      errors.append(f"coverage block must declare version {COVERAGE_VERSION}")

    # Validate subject
    subject_value = str(data.get("subject", ""))
    if not subject_value:
      errors.append("coverage block missing subject id")
    elif not _SUBJECT_ID.match(subject_value):
      errors.append(
        f"subject '{subject_value}' does not match expected pattern "
        "(SPEC|PROD|IP|AUD)-###",
      )
    elif subject_id and subject_value != subject_id:
      errors.append(
        f"coverage block subject {subject_value} does not match "
        f"expected {subject_id}",
      )

    # Validate entries
    entries = data.get("entries")
    if not entries:
      errors.append("coverage block missing entries")
    elif not isinstance(entries, list):
      errors.append("entries must be a list")
    else:
      for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
          errors.append(f"entry[{idx}] must be an object")
          continue

        # Validate artefact ID
        artefact = entry.get("artefact")
        if not artefact:
          errors.append(f"entry[{idx}] missing artefact")
        elif not isinstance(artefact, str):
          errors.append(f"entry[{idx}] artefact must be a string")
        elif not _VERIFICATION_ID.match(artefact):
          errors.append(
            f"entry[{idx}] artefact '{artefact}' does not match "
            "pattern V[TAH]-###",
          )

        # Validate kind
        kind = entry.get("kind")
        if not kind:
          errors.append(f"entry[{idx}] missing kind")
        elif not isinstance(kind, str):
          errors.append(f"entry[{idx}] kind must be a string")
        elif kind not in VALID_KINDS:
          errors.append(
            f"entry[{idx}] kind '{kind}' must be one of: "
            f"{', '.join(sorted(VALID_KINDS))}",
          )

        # Validate requirement ID
        requirement = entry.get("requirement")
        if not requirement:
          errors.append(f"entry[{idx}] missing requirement")
        elif not isinstance(requirement, str):
          errors.append(f"entry[{idx}] requirement must be a string")
        elif not _REQUIREMENT_ID.match(requirement):
          errors.append(
            f"entry[{idx}] requirement '{requirement}' does not match "
            "pattern (SPEC|PROD)-###.(FR|NFR)-...",
          )

        # Validate phase (optional)
        phase = entry.get("phase")
        if phase is not None:
          if not isinstance(phase, str):
            errors.append(f"entry[{idx}] phase must be a string")
          elif not _PHASE_ID.match(phase):
            errors.append(
              f"entry[{idx}] phase '{phase}' does not match "
              "pattern IP-###.PHASE-##",
            )

        # Validate status
        status = entry.get("status")
        if not status:
          errors.append(f"entry[{idx}] missing status")
        elif not isinstance(status, str):
          errors.append(f"entry[{idx}] status must be a string")
        elif status not in VALID_STATUSES:
          errors.append(
            f"entry[{idx}] status '{status}' must be one of: "
            f"{', '.join(sorted(VALID_STATUSES))}",
          )

        # Validate notes (optional)
        notes = entry.get("notes")
        if notes is not None and not isinstance(notes, str):
          errors.append(f"entry[{idx}] notes must be a string")

    return errors


_COVERAGE_PATTERN = re.compile(
  r"```(?:yaml|yml)\s+" + re.escape(COVERAGE_MARKER) + r"\n(.*?)```",
  re.DOTALL,
)


def extract_coverage_blocks(text: str) -> list[VerificationCoverageBlock]:
  """Extract and parse all coverage blocks from markdown content.

  Args:
    text: Markdown content containing coverage blocks.

  Returns:
    List of parsed VerificationCoverageBlock instances.

  Raises:
    ValueError: If YAML is invalid or doesn't parse to a mapping.
  """
  blocks: list[VerificationCoverageBlock] = []
  for match in _COVERAGE_PATTERN.finditer(text):
    raw = match.group(1)
    try:
      data = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:  # pragma: no cover
      msg = f"invalid coverage YAML: {exc}"
      raise ValueError(msg) from exc
    if not isinstance(data, dict):
      msg = "coverage block must parse to mapping"
      raise ValueError(msg)
    blocks.append(VerificationCoverageBlock(raw_yaml=raw, data=data))
  return blocks


def load_coverage_blocks(path: Path) -> list[VerificationCoverageBlock]:
  """Load and extract coverage blocks from file.

  Args:
    path: Path to markdown file.

  Returns:
    List of parsed VerificationCoverageBlock instances.
  """
  text = path.read_text(encoding="utf-8")
  return extract_coverage_blocks(text)


__all__ = [
  "COVERAGE_MARKER",
  "COVERAGE_SCHEMA",
  "COVERAGE_VERSION",
  "VALID_KINDS",
  "VALID_STATUSES",
  "VerificationCoverageBlock",
  "VerificationCoverageValidator",
  "extract_coverage_blocks",
  "load_coverage_blocks",
]
