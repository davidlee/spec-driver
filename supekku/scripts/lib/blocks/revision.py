"""Utilities for extracting and validating structured revision blocks."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

import yaml

from supekku.scripts.lib.requirements.lifecycle import (
  VALID_STATUSES as REQUIREMENT_VALID_STATUSES,
)

if TYPE_CHECKING:
  from collections.abc import Sequence
  from pathlib import Path

REVISION_BLOCK_MARKER = "supekku:revision.change@v1"
REVISION_BLOCK_SCHEMA_ID = "supekku.revision.change"
REVISION_BLOCK_VERSION = 1

# Public JSON schema definition for agent/tool consumption. The runtime validator
# below mirrors this contract; we avoid making jsonschema a hard dependency but
# keep the formal schema available for external tooling.
REVISION_BLOCK_JSON_SCHEMA: dict[str, Any] = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://vice.supekku.dev/schemas/revision-change@v1.json",
  "title": "Supekku Revision Change Block",
  "type": "object",
  "required": ["schema", "version", "metadata", "specs", "requirements"],
  "additionalProperties": False,
  "properties": {
    "schema": {"const": REVISION_BLOCK_SCHEMA_ID},
    "version": {"const": REVISION_BLOCK_VERSION},
    "metadata": {
      "type": "object",
      "required": ["revision"],
      "additionalProperties": True,
      "properties": {
        "revision": {"type": "string", "pattern": r"^RE-\\d{3,}$"},
        "prepared_by": {"type": "string"},
        "generated_at": {"type": "string"},
      },
    },
    "specs": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["spec_id", "action"],
        "additionalProperties": False,
        "properties": {
          "spec_id": {
            "type": "string",
            "pattern": r"^SPEC-\d{3}(?:-[A-Z0-9]+)*$",
          },
          "action": {
            "type": "string",
            "enum": ["created", "updated", "retired"],
          },
          "summary": {"type": "string"},
          "requirement_flow": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
              "added": {
                "type": "array",
                "items": {
                  "type": "string",
                  "pattern": (
                    r"^SPEC-\d{3}(?:-[A-Z0-9]+)*\."
                    r"(FR|NFR)-[A-Z0-9-]+$"
                  ),
                },
              },
              "removed": {
                "type": "array",
                "items": {
                  "type": "string",
                  "pattern": (
                    r"^SPEC-\d{3}(?:-[A-Z0-9]+)*\."
                    r"(FR|NFR)-[A-Z0-9-]+$"
                  ),
                },
              },
              "moved_in": {
                "type": "array",
                "items": {
                  "type": "string",
                  "pattern": (
                    r"^SPEC-\d{3}(?:-[A-Z0-9]+)*\."
                    r"(FR|NFR)-[A-Z0-9-]+$"
                  ),
                },
              },
              "moved_out": {
                "type": "array",
                "items": {
                  "type": "string",
                  "pattern": (
                    r"^SPEC-\d{3}(?:-[A-Z0-9]+)*\."
                    r"(FR|NFR)-[A-Z0-9-]+$"
                  ),
                },
              },
            },
          },
          "section_changes": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["section", "change"],
              "additionalProperties": False,
              "properties": {
                "section": {"type": "string"},
                "change": {
                  "type": "string",
                  "enum": [
                    "added",
                    "removed",
                    "modified",
                    "renamed",
                  ],
                },
                "before_path": {"type": "string"},
                "after_path": {"type": "string"},
                "notes": {"type": "string"},
              },
            },
          },
        },
      },
    },
    "requirements": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["requirement_id", "kind", "action"],
        "additionalProperties": False,
        "properties": {
          "requirement_id": {
            "type": "string",
            "pattern": r"^SPEC-\d{3}(?:-[A-Z0-9]+)*\.(FR|NFR)-[A-Z0-9-]+$",
          },
          "kind": {
            "type": "string",
            "enum": ["functional", "non-functional"],
          },
          "action": {
            "type": "string",
            "enum": ["introduce", "modify", "move", "retire"],
          },
          "summary": {"type": "string"},
          "origin": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["kind", "ref"],
              "additionalProperties": False,
              "properties": {
                "kind": {
                  "type": "string",
                  "enum": [
                    "spec",
                    "requirement",
                    "backlog",
                    "external",
                  ],
                },
                "ref": {"type": "string"},
                "notes": {"type": "string"},
              },
            },
          },
          "destination": {
            "type": "object",
            "required": ["spec"],
            "additionalProperties": False,
            "properties": {
              "spec": {
                "type": "string",
                "pattern": r"^SPEC-\d{3}(?:-[A-Z0-9]+)*$",
              },
              "requirement_id": {
                "type": "string",
                "pattern": (
                  r"^SPEC-\d{3}(?:-[A-Z0-9]+)*\."
                  r"(FR|NFR)-[A-Z0-9-]+$"
                ),
              },
              "path": {"type": "string"},
              "additional_specs": {
                "type": "array",
                "items": {
                  "type": "string",
                  "pattern": r"^SPEC-\d{3}(?:-[A-Z0-9]+)*$",
                },
              },
            },
          },
          "lifecycle": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
              "status": {
                "type": "string",
                "enum": sorted(REQUIREMENT_VALID_STATUSES),
              },
              "introduced_by": {
                "type": "string",
                "pattern": r"^RE-\\d{3,}$",
              },
              "implemented_by": {
                "type": "array",
                "items": {"type": "string", "pattern": r"^DE-\\d{3,}$"},
              },
              "verified_by": {
                "type": "array",
                "items": {
                  "type": "string",
                  "pattern": r"^AUD-\\d{3,}$",
                },
              },
            },
          },
          "text_changes": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
              "before_excerpt": {"type": "string"},
              "after_excerpt": {"type": "string"},
              "diff_ref": {"type": "string"},
            },
          },
        },
        "allOf": [
          {
            "if": {"properties": {"action": {"const": "move"}}},
            "then": {"required": ["origin", "destination"]},
          },
          {
            "if": {"properties": {"action": {"const": "introduce"}}},
            "then": {"required": ["destination"]},
          },
          {
            "if": {"properties": {"action": {"const": "modify"}}},
            "then": {"required": ["destination"]},
          },
        ],
      },
    },
  },
}


@dataclass(frozen=True)
class ValidationMessage:
  """A validation message with path context for error reporting."""

  path: tuple[Any, ...]
  message: str

  def render_path(self) -> str:
    """Render validation path as human-readable string.

    Returns:
      Formatted path string (e.g., "specs.primary[0]").
    """
    if not self.path:
      return "<root>"
    formatted: list[str] = []
    for element in self.path:
      if isinstance(element, int):
        formatted.append(f"[{element}]")
      elif formatted:
        formatted.append(f".{element}")
      else:
        formatted.append(str(element))
    return "".join(formatted)


@dataclass
class RevisionChangeBlock:
  """Represents a parsed revision change block from markdown."""

  marker: str
  language: str
  info: str
  yaml_content: str
  content_start: int
  content_end: int
  source_path: Path | None = None

  def parse(self) -> dict[str, Any]:
    """Parse YAML content from revision block.

    Returns:
      Parsed YAML data as dictionary.

    Raises:
      ValueError: If YAML is invalid or doesn't parse to a mapping.
    """
    try:
      loaded = yaml.safe_load(self.yaml_content)
    except yaml.YAMLError as exc:  # pragma: no cover - repr includes location
      msg = f"invalid YAML: {exc}"
      raise ValueError(msg) from exc
    if loaded is None:
      return {}
    if not isinstance(loaded, dict):
      msg = "revision block must parse to a mapping"
      raise ValueError(msg)
    return loaded

  def formatted_yaml(self, data: dict[str, Any] | None = None) -> str:
    """Format data as canonical YAML.

    Args:
      data: Optional data to format. If None, parses from yaml_content.

    Returns:
      Formatted YAML string with trailing newline.
    """
    payload = data if data is not None else self.parse()
    dumped = yaml.safe_dump(
      payload,
      sort_keys=False,
      indent=2,
      default_flow_style=False,
    )
    if not dumped.endswith("\n"):
      dumped += "\n"
    return dumped

  def replace_content(self, original: str, new_yaml: str) -> str:
    """Replace block content in original string.

    Args:
      original: Original file content.
      new_yaml: New YAML content to insert.

    Returns:
      Updated content with replacement applied.
    """
    return original[: self.content_start] + new_yaml + original[self.content_end :]


_REQUIREMENT_ID = re.compile(r"^SPEC-\d{3}(?:-[A-Z0-9]+)*\.(FR|NFR)-[A-Z0-9-]+$")
_SPEC_ID = re.compile(r"^SPEC-\d{3}(?:-[A-Z0-9]+)*$")
_REVISION_ID = re.compile(r"^RE-\d{3,}$")
_DELTA_ID = re.compile(r"^DE-\d{3,}$")
_AUDIT_ID = re.compile(r"^AUD-\d{3,}$")
_BACKLOG_ID = re.compile(r"^[A-Z]+-\d{3,}$")


def _is_requirement_id(value: str) -> bool:
  return bool(_REQUIREMENT_ID.match(value))


def _is_spec_id(value: str) -> bool:
  return bool(_SPEC_ID.match(value))


def _is_revision_id(value: str) -> bool:
  return bool(_REVISION_ID.match(value))


def _is_delta_id(value: str) -> bool:
  return bool(_DELTA_ID.match(value))


def _is_audit_id(value: str) -> bool:
  return bool(_AUDIT_ID.match(value))


def _is_backlog_id(value: str) -> bool:
  return bool(_BACKLOG_ID.match(value))


def _disallow_extra_keys(
  mapping: dict[str, Any],
  allowed_keys: Sequence[str],
  path: tuple[Any, ...],
  messages: list[ValidationMessage],
) -> None:
  allowed_set = set(allowed_keys)
  for key in mapping:
    if key not in allowed_set:
      messages.append(ValidationMessage((*path, key), "is not allowed"))


class RevisionBlockValidator:
  """Runtime validator mirroring REVISION_BLOCK_JSON_SCHEMA."""

  def validate(self, data: dict[str, Any]) -> list[ValidationMessage]:
    """Validate revision block data against schema.

    Args:
      data: Parsed revision block data.

    Returns:
      List of validation messages (empty if valid).
    """
    messages: list[ValidationMessage] = []
    self._check_root(data, messages)
    return messages

  def _check_root(
    self,
    data: dict[str, Any],
    messages: list[ValidationMessage],
  ) -> None:
    if not isinstance(data, dict):
      messages.append(ValidationMessage((), "block must be a mapping"))
      return

    self._require_key(data, "schema", messages)
    if data.get("schema") != REVISION_BLOCK_SCHEMA_ID:
      messages.append(
        ValidationMessage(("schema",), "must equal 'supekku.revision.change'"),
      )

    self._require_key(data, "version", messages)
    if data.get("version") != REVISION_BLOCK_VERSION:
      messages.append(ValidationMessage(("version",), "must equal 1"))

    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
      messages.append(ValidationMessage(("metadata",), "must be an object"))
    else:
      self._validate_metadata(metadata, messages)

    specs = data.get("specs")
    if specs is None:
      messages.append(ValidationMessage(("specs",), "is required"))
    elif not isinstance(specs, list):
      messages.append(ValidationMessage(("specs",), "must be an array"))
    else:
      for index, spec in enumerate(specs):
        self._validate_spec(spec, messages, path=("specs", index))

    requirements = data.get("requirements")
    if requirements is None:
      messages.append(ValidationMessage(("requirements",), "is required"))
    elif not isinstance(requirements, list):
      messages.append(ValidationMessage(("requirements",), "must be an array"))
    else:
      for index, requirement in enumerate(requirements):
        self._validate_requirement(
          requirement,
          messages,
          path=("requirements", index),
        )

  def _require_key(
    self,
    data: dict[str, Any],
    key: str,
    messages: list[ValidationMessage],
    *,
    path: Sequence[Any] = (),
  ) -> None:
    if key not in data:
      messages.append(ValidationMessage((*tuple(path), key), "is required"))

  def _validate_metadata(
    self,
    metadata: dict[str, Any],
    messages: list[ValidationMessage],
  ) -> None:
    if "revision" not in metadata:
      messages.append(ValidationMessage(("metadata", "revision"), "is required"))
    else:
      revision = metadata.get("revision")
      if not isinstance(revision, str) or not _is_revision_id(revision):
        messages.append(
          ValidationMessage(
            ("metadata", "revision"),
            "must match pattern RE-###",
          ),
        )
    for optional_key in ("prepared_by", "generated_at"):
      value = metadata.get(optional_key)
      if value is None:
        continue
      if not isinstance(value, str):
        messages.append(
          ValidationMessage(("metadata", optional_key), "must be a string"),
        )

  def _validate_spec(
    self,
    spec: Any,
    messages: list[ValidationMessage],
    *,
    path: tuple[Any, ...],
  ) -> None:
    if not isinstance(spec, dict):
      messages.append(ValidationMessage(path, "must be an object"))
      return

    _disallow_extra_keys(
      spec,
      ("spec_id", "action", "summary", "requirement_flow", "section_changes"),
      path,
      messages,
    )
    self._require_key(spec, "spec_id", messages, path=path)
    self._require_key(spec, "action", messages, path=path)

    spec_id = spec.get("spec_id")
    if spec_id is not None and (
      not isinstance(spec_id, str) or not _is_spec_id(spec_id)
    ):
      messages.append(
        ValidationMessage((*path, "spec_id"), "must be a SPEC identifier"),
      )

    action = spec.get("action")
    if action is not None and action not in {"created", "updated", "retired"}:
      messages.append(
        ValidationMessage(
          (*path, "action"),
          "must be one of created/updated/retired",
        ),
      )

    if "summary" in spec and not isinstance(spec["summary"], str):
      messages.append(ValidationMessage((*path, "summary"), "must be a string"))

    flow = spec.get("requirement_flow")
    if flow is not None:
      if not isinstance(flow, dict):
        messages.append(
          ValidationMessage((*path, "requirement_flow"), "must be an object"),
        )
      else:
        _disallow_extra_keys(
          flow,
          ("added", "removed", "moved_in", "moved_out"),
          (*path, "requirement_flow"),
          messages,
        )
        for key in ("added", "removed", "moved_in", "moved_out"):
          value = flow.get(key)
          if value is None:
            continue
          if not isinstance(value, list):
            messages.append(
              ValidationMessage(
                (*path, "requirement_flow", key),
                "must be an array",
              ),
            )
            continue
          for idx, item in enumerate(value):
            if not isinstance(item, str) or not _is_requirement_id(item):
              messages.append(
                ValidationMessage(
                  (*path, "requirement_flow", key, idx),
                  "must be a requirement identifier",
                ),
              )

    section_changes = spec.get("section_changes")
    if section_changes is not None:
      if not isinstance(section_changes, list):
        messages.append(
          ValidationMessage((*path, "section_changes"), "must be an array"),
        )
      else:
        for idx, change in enumerate(section_changes):
          change_path = (*path, "section_changes", idx)
          if not isinstance(change, dict):
            messages.append(
              ValidationMessage(change_path, "must be an object"),
            )
            continue
          _disallow_extra_keys(
            change,
            ("section", "change", "before_path", "after_path", "notes"),
            change_path,
            messages,
          )
          self._require_key(change, "section", messages, path=change_path)
          self._require_key(change, "change", messages, path=change_path)

          if not isinstance(change.get("section"), str):
            messages.append(
              ValidationMessage(
                (*change_path, "section"),
                "must be a string",
              ),
            )

          allowed = {"added", "removed", "modified", "renamed"}
          if change.get("change") not in allowed:
            messages.append(
              ValidationMessage(
                (*change_path, "change"),
                "must be one of added/removed/modified/renamed",
              ),
            )

          for field in ("before_path", "after_path", "notes"):
            if field in change and not isinstance(change[field], str):
              messages.append(
                ValidationMessage(
                  (*change_path, field),
                  "must be a string",
                ),
              )

  def _validate_requirement(
    self,
    requirement: Any,
    messages: list[ValidationMessage],
    *,
    path: tuple[Any, ...],
  ) -> None:
    if not isinstance(requirement, dict):
      messages.append(ValidationMessage(path, "must be an object"))
      return

    _disallow_extra_keys(
      requirement,
      (
        "requirement_id",
        "kind",
        "action",
        "summary",
        "origin",
        "destination",
        "lifecycle",
        "text_changes",
      ),
      path,
      messages,
    )

    self._require_key(requirement, "requirement_id", messages, path=path)
    self._require_key(requirement, "kind", messages, path=path)
    self._require_key(requirement, "action", messages, path=path)

    requirement_id = requirement.get("requirement_id")
    if requirement_id is not None and (
      not isinstance(requirement_id, str) or not _is_requirement_id(requirement_id)
    ):
      messages.append(
        ValidationMessage(
          (*path, "requirement_id"),
          "must be a requirement identifier",
        ),
      )

    kind = requirement.get("kind")
    if kind not in {"functional", "non-functional"}:
      messages.append(
        ValidationMessage(
          (*path, "kind"),
          "must be functional or non-functional",
        ),
      )

    action = requirement.get("action")
    if action not in {"introduce", "modify", "move", "retire"}:
      messages.append(
        ValidationMessage(
          (*path, "action"),
          "must be one of introduce/modify/move/retire",
        ),
      )

    if "summary" in requirement and not isinstance(requirement["summary"], str):
      messages.append(ValidationMessage((*path, "summary"), "must be a string"))

    origin_required = action == "move"
    destination_required = action in {"introduce", "modify", "move"}

    origin = requirement.get("origin")
    if origin is None:
      if origin_required:
        messages.append(
          ValidationMessage(
            (*path, "origin"),
            "is required when action is move",
          ),
        )
    elif not isinstance(origin, list):
      messages.append(
        ValidationMessage((*path, "origin"), "must be an array"),
      )
    else:
      for idx, item in enumerate(origin):
        origin_path = (*path, "origin", idx)
        if not isinstance(item, dict):
          messages.append(
            ValidationMessage(origin_path, "must be an object"),
          )
          continue
        _disallow_extra_keys(
          item,
          ("kind", "ref", "notes"),
          origin_path,
          messages,
        )
        self._require_key(item, "kind", messages, path=origin_path)
        self._require_key(item, "ref", messages, path=origin_path)

        kind_value = item.get("kind")
        if kind_value not in {"spec", "requirement", "backlog", "external"}:
          messages.append(
            ValidationMessage(
              (*origin_path, "kind"),
              "must be one of spec/requirement/backlog/external",
            ),
          )
        ref_value = item.get("ref")
        if not isinstance(ref_value, str):
          messages.append(
            ValidationMessage(
              (*origin_path, "ref"),
              "must be a string",
            ),
          )
        else:
          if kind_value == "requirement" and not _is_requirement_id(
            ref_value,
          ):
            messages.append(
              ValidationMessage(
                (*origin_path, "ref"),
                "must be a requirement identifier",
              ),
            )
          if kind_value == "spec" and not _is_spec_id(ref_value):
            messages.append(
              ValidationMessage(
                (*origin_path, "ref"),
                "must be a SPEC identifier",
              ),
            )
          if kind_value == "backlog" and not _is_backlog_id(ref_value):
            messages.append(
              ValidationMessage(
                (*origin_path, "ref"),
                "should look like BACKLOG-ID",
              ),
            )
        if "notes" in item and not isinstance(item["notes"], str):
          messages.append(
            ValidationMessage(
              (*origin_path, "notes"),
              "must be a string",
            ),
          )

    destination = requirement.get("destination")
    if destination is None:
      if destination_required:
        messages.append(
          ValidationMessage(
            (*path, "destination"),
            "is required when action is introduce/modify/move",
          ),
        )
    elif not isinstance(destination, dict):
      messages.append(
        ValidationMessage((*path, "destination"), "must be an object"),
      )
    else:
      _disallow_extra_keys(
        destination,
        ("spec", "requirement_id", "path", "additional_specs"),
        (*path, "destination"),
        messages,
      )
      self._require_key(
        destination,
        "spec",
        messages,
        path=(*path, "destination"),
      )
      spec_value = destination.get("spec")
      if spec_value is not None and (
        not isinstance(spec_value, str) or not _is_spec_id(spec_value)
      ):
        messages.append(
          ValidationMessage(
            (*path, "destination", "spec"),
            "must be a SPEC identifier",
          ),
        )
      req_value = destination.get("requirement_id")
      if req_value is not None and (
        not isinstance(req_value, str) or not _is_requirement_id(req_value)
      ):
        messages.append(
          ValidationMessage(
            (*path, "destination", "requirement_id"),
            "must be a requirement identifier",
          ),
        )
      if "path" in destination and not isinstance(destination["path"], str):
        messages.append(
          ValidationMessage(
            (*path, "destination", "path"),
            "must be a string",
          ),
        )
      additional = destination.get("additional_specs")
      if additional is not None:
        if not isinstance(additional, list):
          messages.append(
            ValidationMessage(
              (*path, "destination", "additional_specs"),
              "must be an array",
            ),
          )
        else:
          for idx, spec in enumerate(additional):
            if not isinstance(spec, str) or not _is_spec_id(spec):
              messages.append(
                ValidationMessage(
                  (*path, "destination", "additional_specs", idx),
                  "must be a SPEC identifier",
                ),
              )

    lifecycle = requirement.get("lifecycle")
    if lifecycle is not None:
      if not isinstance(lifecycle, dict):
        messages.append(
          ValidationMessage((*path, "lifecycle"), "must be an object"),
        )
      else:
        _disallow_extra_keys(
          lifecycle,
          ("status", "introduced_by", "implemented_by", "verified_by"),
          (*path, "lifecycle"),
          messages,
        )
        status = lifecycle.get("status")
        if status is not None and status not in REQUIREMENT_VALID_STATUSES:
          messages.append(
            ValidationMessage(
              (*path, "lifecycle", "status"),
              f"must be one of {sorted(REQUIREMENT_VALID_STATUSES)}",
            ),
          )
        introduced_by = lifecycle.get("introduced_by")
        if introduced_by is not None and (
          not isinstance(introduced_by, str) or not _is_revision_id(introduced_by)
        ):
          messages.append(
            ValidationMessage(
              (*path, "lifecycle", "introduced_by"),
              "must match RE identifier pattern",
            ),
          )
        implemented_by = lifecycle.get("implemented_by")
        if implemented_by is not None:
          if not isinstance(implemented_by, list):
            messages.append(
              ValidationMessage(
                (*path, "lifecycle", "implemented_by"),
                "must be an array",
              ),
            )
          else:
            for idx, delta in enumerate(implemented_by):
              if not isinstance(delta, str) or not _is_delta_id(delta):
                messages.append(
                  ValidationMessage(
                    (*path, "lifecycle", "implemented_by", idx),
                    "must be a delta identifier",
                  ),
                )
        verified_by = lifecycle.get("verified_by")
        if verified_by is not None:
          if not isinstance(verified_by, list):
            messages.append(
              ValidationMessage(
                (*path, "lifecycle", "verified_by"),
                "must be an array",
              ),
            )
          else:
            for idx, audit in enumerate(verified_by):
              if not isinstance(audit, str) or not _is_audit_id(audit):
                messages.append(
                  ValidationMessage(
                    (*path, "lifecycle", "verified_by", idx),
                    "must be an audit identifier",
                  ),
                )

    text_changes = requirement.get("text_changes")
    if text_changes is not None:
      if not isinstance(text_changes, dict):
        messages.append(
          ValidationMessage((*path, "text_changes"), "must be an object"),
        )
      else:
        _disallow_extra_keys(
          text_changes,
          ("before_excerpt", "after_excerpt", "diff_ref"),
          (*path, "text_changes"),
          messages,
        )
        for field in ("before_excerpt", "after_excerpt", "diff_ref"):
          if field in text_changes and not isinstance(
            text_changes[field],
            str,
          ):
            messages.append(
              ValidationMessage(
                (*path, "text_changes", field),
                "must be a string",
              ),
            )


def extract_revision_blocks(
  markdown: str,
  *,
  source: Path | None = None,
) -> list[RevisionChangeBlock]:
  """Extract revision change blocks from markdown content.

  Args:
    markdown: Markdown content to parse.
    source: Optional source file path for error reporting.

  Returns:
    List of parsed RevisionChangeBlock objects.
  """
  lines = markdown.splitlines(keepends=True)
  blocks: list[RevisionChangeBlock] = []
  offset = 0
  idx = 0
  while idx < len(lines):
    line = lines[idx]
    line_start = offset
    offset += len(line)
    match = re.match(r"^(`{3,})(.*)$", line.rstrip("\r\n"))
    if not match:
      idx += 1
      continue
    fence = match.group(1)
    info = match.group(2).strip()
    if not info:
      idx += 1
      continue
    info_parts = info.split()
    language = info_parts[0]
    marker = next(
      (part for part in info_parts[1:] if part.startswith("supekku:")),
      "",
    )
    if language not in {"yaml", "yml"} or marker != REVISION_BLOCK_MARKER:
      idx += 1
      continue
    closing_idx = idx + 1
    while closing_idx < len(lines):
      candidate = lines[closing_idx]
      candidate_stripped = candidate.rstrip("\r\n")
      if (
        candidate_stripped.startswith(fence)
        and candidate_stripped[len(fence) :].strip() == ""
      ):
        break
      closing_idx += 1
    if closing_idx >= len(lines):
      idx += 1
      continue
    content_start = line_start + len(line)
    yaml_content = "".join(lines[idx + 1 : closing_idx])
    content_end = content_start + len(yaml_content)
    block = RevisionChangeBlock(
      marker=marker,
      language=language,
      info=info,
      yaml_content=yaml_content,
      content_start=content_start,
      content_end=content_end,
      source_path=source,
    )
    blocks.append(block)
    # move idx to closing fence line
    while idx < closing_idx:
      idx += 1
      offset += len(lines[idx])
    idx += 1
  return blocks


def load_revision_blocks(path: Path) -> list[RevisionChangeBlock]:
  """Load and extract revision change blocks from a file.

  Args:
    path: Path to markdown file.

  Returns:
    List of parsed RevisionChangeBlock objects.
  """
  content = path.read_text(encoding="utf-8")
  return extract_revision_blocks(content, source=path)


def render_revision_change_block(
  revision_id: str,
  *,
  specs: list[dict[str, Any]] | None = None,
  requirements: list[dict[str, Any]] | None = None,
  prepared_by: str | None = None,
  generated_at: str | None = None,
) -> str:
  """Render a revision change YAML block with given values.

  This is the canonical source for the block structure. Templates and
  creation code should use this instead of hardcoding the structure.

  Note: This generates a minimal but valid revision block. For complex revisions,
  consider building the dict structure and using yaml.safe_dump directly.

  Args:
    revision_id: The revision ID (e.g., "RE-001").
    specs: List of spec change dicts with:
      - spec_id: str
      - action: str ("created", "updated", "retired")
      - summary: str (optional)
      - requirement_flow: dict (optional)
      - section_changes: list (optional)
    requirements: List of requirement change dicts with:
      - requirement_id: str
      - kind: str ("functional", "non-functional")
      - action: str ("introduce", "modify", "move", "retire")
      - summary: str (optional)
      - destination: dict (optional)
      - origin: list (optional)
      - lifecycle: dict (optional)
    prepared_by: Optional preparer identifier.
    generated_at: Optional generation timestamp.

  Returns:
    Formatted YAML code block as string.
  """
  # Build metadata
  metadata: dict[str, Any] = {"revision": revision_id}
  if prepared_by:
    metadata["prepared_by"] = prepared_by
  if generated_at:
    metadata["generated_at"] = generated_at
  elif not prepared_by:  # Only add default timestamp if neither field provided
    metadata["generated_at"] = datetime.now().isoformat() + "Z"

  # Build the block data structure
  data: dict[str, Any] = {
    "schema": REVISION_BLOCK_SCHEMA_ID,
    "version": REVISION_BLOCK_VERSION,
    "metadata": metadata,
    "specs": specs or [],
    "requirements": requirements or [],
  }

  # Render as YAML
  yaml_content = yaml.safe_dump(
    data,
    sort_keys=False,
    indent=2,
    default_flow_style=False,
  )

  lines = [
    f"```yaml {REVISION_BLOCK_MARKER}",
    yaml_content.rstrip("\n"),
    "```",
  ]
  return "\n".join(lines)


__all__ = [
  "REVISION_BLOCK_JSON_SCHEMA",
  "REVISION_BLOCK_MARKER",
  "REVISION_BLOCK_SCHEMA_ID",
  "REVISION_BLOCK_VERSION",
  "RevisionBlockValidator",
  "RevisionChangeBlock",
  "ValidationMessage",
  "extract_revision_blocks",
  "load_revision_blocks",
  "render_revision_change_block",
]


# Register schema
from .schema_registry import BlockSchema, register_block_schema  # noqa: E402

register_block_schema(
  "revision.change",
  BlockSchema(
    name="revision.change",
    marker=REVISION_BLOCK_MARKER,
    version=REVISION_BLOCK_VERSION,
    renderer=render_revision_change_block,
    description="Documents changes to specs and requirements in a revision",
  ),
)
