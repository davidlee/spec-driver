"""Bridge block extraction and rendering for workflow orchestration.

Handles notes-bridge (§7.1) and phase-bridge (§7.2) fenced YAML blocks
in markdown files.

Design authority: DR-102 §7.
"""

from __future__ import annotations

import re
from typing import Any

import yaml

from supekku.scripts.lib.blocks.workflow_metadata import (
  NOTES_BRIDGE_MARKER,
  PHASE_BRIDGE_MARKER,
)

# ---------------------------------------------------------------------------
# Extraction patterns
# ---------------------------------------------------------------------------

_NOTES_BRIDGE_PATTERN = re.compile(
  r"```(?:yaml|yml)\s+" + re.escape(NOTES_BRIDGE_MARKER) + r"\n(.*?)```",
  re.DOTALL,
)

_PHASE_BRIDGE_PATTERN = re.compile(
  r"```(?:yaml|yml)\s+" + re.escape(PHASE_BRIDGE_MARKER) + r"\n(.*?)```",
  re.DOTALL,
)


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------


def extract_phase_bridge(text: str) -> dict[str, Any] | None:
  """Extract phase-bridge block from phase sheet markdown.

  Returns parsed dict or None if no block found.
  """
  match = _PHASE_BRIDGE_PATTERN.search(text)
  if not match:
    return None
  raw = match.group(1)
  try:
    data = yaml.safe_load(raw)
  except yaml.YAMLError:
    return None
  if not isinstance(data, dict):
    return None
  return data


def extract_notes_bridge(text: str) -> dict[str, Any] | None:
  """Extract notes-bridge block from notes.md.

  Returns parsed dict or None if no block found.
  """
  match = _NOTES_BRIDGE_PATTERN.search(text)
  if not match:
    return None
  raw = match.group(1)
  try:
    data = yaml.safe_load(raw)
  except yaml.YAMLError:
    return None
  if not isinstance(data, dict):
    return None
  return data


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def render_notes_bridge(
  *,
  artifact_id: str,
  workflow_state: str = "workflow/state.yaml",
  current_handoff: str | None = None,
  review_index: str | None = None,
  review_findings: str | None = None,
  review_bootstrap: str | None = None,
) -> str:
  """Render a notes-bridge fenced YAML block.

  Returns the full fenced block string ready for insertion into notes.md.
  """
  data: dict[str, Any] = {
    "schema": "supekku.workflow.notes-bridge",
    "version": 1,
    "artifact": artifact_id,
    "workflow_state": workflow_state,
  }
  if current_handoff:
    data["current_handoff"] = current_handoff
  if review_index:
    data["review_index"] = review_index
  if review_findings:
    data["review_findings"] = review_findings
  if review_bootstrap:
    data["review_bootstrap"] = review_bootstrap

  yaml_content = yaml.dump(data, default_flow_style=False, sort_keys=False)
  return f"```yaml {NOTES_BRIDGE_MARKER}\n{yaml_content}```"


def render_phase_bridge(
  *,
  phase_id: str,
  status: str = "complete",
  handoff_ready: bool = True,
  review_required: bool = False,
  current_handoff: str | None = None,
) -> str:
  """Render a phase-bridge fenced YAML block.

  Returns the full fenced block string ready for insertion into phase sheets.
  """
  data: dict[str, Any] = {
    "schema": "supekku.workflow.phase-bridge",
    "version": 1,
    "phase": phase_id,
    "status": status,
    "handoff_ready": handoff_ready,
  }
  if review_required:
    data["review_required"] = review_required
  if current_handoff:
    data["current_handoff"] = current_handoff

  yaml_content = yaml.dump(data, default_flow_style=False, sort_keys=False)
  return f"```yaml {PHASE_BRIDGE_MARKER}\n{yaml_content}```"
