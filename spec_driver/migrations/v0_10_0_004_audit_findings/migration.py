"""AuditFindingsStep — findings FM → block migration (DR-141 §6).

Isolation: stdlib + _helpers + _protocol + pyyaml only (DEC-138-12).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from spec_driver.migrations._helpers import atomic_write, split_frontmatter
from spec_driver.migrations._protocol import (
  BaseMigrationStep,
  StepPreview,
  StepResult,
)

_HEAD_BYTES = 4096

_FINDINGS_KEY_RE = re.compile(r"^findings:", re.MULTILINE)

_VALID_OUTCOMES = {"aligned", "drift", "risk"}

# Block constants (frozen-local copy; DEC-138-12 forbids supekku imports)
_MARKER = "supekku:audit.findings@v1"
_SCHEMA = "supekku.audit.findings"
_VERSION = 1

_BLOCK_DETECT_RE = re.compile(
  r"```(?:yaml|yml)\s+" + re.escape(_MARKER) + r"\n(.*?)```",
  re.DOTALL,
)

DRIFT_FINDINGS_EMITTED = "findings_block_emitted_from_fm"
DRIFT_INVALID_OUTCOME = "invalid_finding_outcome"


@dataclass(frozen=True)
class _DriftEntry:
  kind: str
  detail: str


@dataclass(frozen=True)
class _Transform:
  text: str
  drift: list[_DriftEntry] = field(default_factory=list)
  changed: bool = False


def _emit_findings_block(
  audit_id: str,
  findings: list[dict[str, Any]],
) -> str:
  """Render audit findings as code-fenced block (frozen-local emitter)."""
  head = (
    f"```yaml {_MARKER}\n"
    f"schema: {_SCHEMA}\n"
    f"version: {_VERSION}\n"
    f"audit: {audit_id}\n"
  )
  if not findings:
    return head + "findings: []\n```"

  cleaned = []
  for f in findings:
    entry: dict[str, Any] = {}
    for k in ("id", "description", "summary", "outcome"):
      if k in f and f[k] is not None:
        entry[k] = f[k]
    for k in ("linked_issue", "linked_delta"):
      if k in f and f[k]:
        entry[k] = f[k]
    if "disposition" in f and f["disposition"]:
      entry["disposition"] = f["disposition"]
    if "refs" in f and f["refs"]:
      entry["refs"] = f["refs"]
    cleaned.append(entry)

  body = yaml.safe_dump(
    {"findings": cleaned},
    sort_keys=False,
    allow_unicode=True,
    default_flow_style=False,
  ).rstrip()
  return head + body + "\n```"


def _append_block(body: str, block: str) -> str:
  """Append block to body. Skip if block marker already present."""
  if _BLOCK_DETECT_RE.search(body):
    return body
  trimmed = body.rstrip()
  joiner = "\n\n" if trimmed else ""
  return f"{trimmed}{joiner}{block}\n"


def _has_findings_key(text: str) -> bool:
  return bool(_FINDINGS_KEY_RE.search(text))


def _transform(text: str) -> _Transform:
  yaml_text, body = split_frontmatter(text)
  if not yaml_text:
    return _Transform(text=text)

  loaded = yaml.safe_load(yaml_text) or {}
  if not isinstance(loaded, dict):
    return _Transform(text=text)
  frontmatter: dict[str, Any] = loaded

  has_fm_findings = "findings" in frontmatter
  has_block = bool(_BLOCK_DETECT_RE.search(body))

  if not has_fm_findings and not has_block:
    return _Transform(text=text)

  if has_block and not has_fm_findings:
    return _Transform(text=text)

  drift: list[_DriftEntry] = []
  audit_id = str(frontmatter.get("id") or "")

  # Check for invalid outcomes before emitting block
  findings = frontmatter.get("findings", [])
  if isinstance(findings, list):
    for f in findings:
      if isinstance(f, dict):
        outcome = f.get("outcome", "")
        if outcome and outcome not in _VALID_OUTCOMES:
          drift.append(
            _DriftEntry(
              DRIFT_INVALID_OUTCOME,
              f"{audit_id}/{f.get('id', '?')}: "
              f"outcome '{outcome}' not in {sorted(_VALID_OUTCOMES)}",
            )
          )

  # Emit block from FM findings (if no block exists yet)
  if not has_block and isinstance(findings, list):
    block = _emit_findings_block(audit_id, findings)
    body = _append_block(body, block)
    drift.append(
      _DriftEntry(
        DRIFT_FINDINGS_EMITTED,
        f"emitted findings block from FM ({len(findings)} items)",
      )
    )

  # Cut FM findings key (block is now canonical)
  new_fm = {k: v for k, v in frontmatter.items() if k != "findings"}

  new_yaml = yaml.safe_dump(
    new_fm, sort_keys=False, allow_unicode=True,
  ).rstrip()
  new_text = f"---\n{new_yaml}\n---\n{body}"
  return _Transform(text=new_text, drift=drift, changed=new_text != text)


class AuditFindingsStep(BaseMigrationStep):
  """Forward-only sweep: findings FM → block (DR-141 §6)."""

  applies_to_kind = "audit"
  description = (
    "DR-141 placement: findings FM array → "
    "supekku:audit.findings@v1 block"
  )

  def applies_to(self, file_path: Path) -> bool:
    try:
      head = file_path.read_text(encoding="utf-8")[:_HEAD_BYTES]
    except OSError:
      return False
    return _has_findings_key(head)

  def preview(self, file_path: Path) -> StepPreview:
    if not self.applies_to(file_path):
      return StepPreview(touched=[], skipped=[file_path], drift=[])
    text = file_path.read_text(encoding="utf-8")
    result = _transform(text)
    if not result.changed:
      return StepPreview(
        touched=[],
        skipped=[file_path],
        drift=[f"{e.kind}: {e.detail}" for e in result.drift],
      )
    return StepPreview(
      touched=[file_path],
      skipped=[],
      drift=[f"{e.kind}: {e.detail}" for e in result.drift],
    )

  def apply(self, file_path: Path) -> StepResult:
    if not self.applies_to(file_path):
      return StepResult(touched=[], skipped=[file_path])
    text = file_path.read_text(encoding="utf-8")
    result = _transform(text)
    if not result.changed:
      return StepResult(touched=[], skipped=[file_path])
    atomic_write(file_path, result.text)
    drift_paths = [file_path] if result.drift else []
    return StepResult(
      touched=[file_path],
      skipped=[],
      drift_entries=drift_paths,
    )


step = AuditFindingsStep()

__all__ = ["AuditFindingsStep", "step"]
