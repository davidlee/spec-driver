"""RevisionMetadataStep — revision FM cleanup + block synthesis (DE-142 P04).

Cuts universal + hand-rolled FM keys and, for FM-only records, synthesises a
``supekku:revision.change@v1`` block (action ``modify``, no move/lifecycle/
origin — DEC-142-09; ``specs[]`` from ``destination_specs`` only — DEC-142-12).
Existing blocks win (no re-synthesis); the step never emits drift (DEC-142-10).

Isolation: stdlib + _helpers + _protocol + pyyaml only (DEC-138-12). Block
schema/marker/version and the cut-key list are frozen-local copies.
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

# Block constants (frozen-local copy; DEC-138-12 forbids supekku imports).
_MARKER = "supekku:revision.change@v1"
_SCHEMA = "supekku.revision.change"
_VERSION = 1

# FM keys removed during migration: ADR-010 universal cuts + DE-118 hand-rolled
# scope keys now carried canonically by the block.
_CUT_KEYS = (
  "lifecycle",
  "aliases",
  "auditers",
  "source",
  "source_specs",
  "destination_specs",
  "requirements",
)

_BLOCK_DETECT_RE = re.compile(
  r"```(?:yaml|yml)\s+" + re.escape(_MARKER) + r"\n(.*?)```",
  re.DOTALL,
)

# Top-level cut-key presence; anchored so "source" does not match "source_specs".
_CUT_KEY_RE = re.compile(
  r"(?m)^(?:" + "|".join(re.escape(k) for k in _CUT_KEYS) + r"):",
)


@dataclass(frozen=True)
class _Transform:
  text: str
  drift: list[str] = field(default_factory=list)
  changed: bool = False


def _requirement_kind(requirement_id: str) -> str:
  """FR -> functional; NF/NFR -> non-functional (frozen-local token heuristic)."""
  _, _, tail = requirement_id.partition(".")
  token = tail.split("-", 1)[0]
  if token in ("NF", "NFR"):
    return "non-functional"
  return "functional"


def _requirement_container(requirement_id: str) -> str:
  """The spec/container prefix of a requirement_id (text before the first dot)."""
  container, _, _ = requirement_id.partition(".")
  return container


def _as_str_list(value: Any) -> list[str]:
  if not isinstance(value, list):
    return []
  return [str(v) for v in value if v is not None]


def _synthesise_block(
  revision_id: str,
  destination_specs: list[str],
  requirements: list[str],
) -> str:
  """Render a faithful modify-only revision.change block (frozen-local emitter)."""
  block_data: dict[str, Any] = {
    "schema": _SCHEMA,
    "version": _VERSION,
    "metadata": {"revision": revision_id},
    "specs": [{"spec_id": s, "action": "updated"} for s in destination_specs],
    "requirements": [
      {
        "requirement_id": r,
        "kind": _requirement_kind(r),
        "action": "modify",
        "destination": {"spec": _requirement_container(r)},
      }
      for r in requirements
    ],
  }
  body = yaml.safe_dump(
    block_data,
    sort_keys=False,
    allow_unicode=True,
    default_flow_style=False,
  ).rstrip()
  return f"```yaml {_MARKER}\n{body}\n```"


def _append_block(body: str, block: str) -> str:
  """Append block to body. Skip if a block marker is already present."""
  if _BLOCK_DETECT_RE.search(body):
    return body
  trimmed = body.rstrip()
  joiner = "\n\n" if trimmed else ""
  return f"{trimmed}{joiner}{block}\n"


def _transform(text: str) -> _Transform:
  yaml_text, body = split_frontmatter(text)
  if not yaml_text:
    return _Transform(text=text)

  loaded = yaml.safe_load(yaml_text) or {}
  if not isinstance(loaded, dict):
    return _Transform(text=text)
  frontmatter: dict[str, Any] = loaded

  if not any(k in frontmatter for k in _CUT_KEYS):
    return _Transform(text=text)

  # Synthesise a block for FM-only records that carry scope (no block yet).
  if not _BLOCK_DETECT_RE.search(body):
    destination_specs = _as_str_list(frontmatter.get("destination_specs"))
    requirements = _as_str_list(frontmatter.get("requirements"))
    if destination_specs or requirements:
      block = _synthesise_block(
        str(frontmatter.get("id") or ""),
        destination_specs,
        requirements,
      )
      body = _append_block(body, block)

  new_fm = {k: v for k, v in frontmatter.items() if k not in _CUT_KEYS}
  new_yaml = yaml.safe_dump(new_fm, sort_keys=False, allow_unicode=True).rstrip()
  new_text = f"---\n{new_yaml}\n---\n{body}"
  return _Transform(text=new_text, changed=new_text != text)


class RevisionMetadataStep(BaseMigrationStep):
  """Forward-only sweep: revision FM cleanup + block synthesis (DE-142 P04)."""

  applies_to_kind = "revision"
  description = (
    "DE-142: cut universal/hand-rolled FM keys; synthesise "
    "supekku:revision.change@v1 block for FM-only revisions"
  )

  def applies_to(self, file_path: Path) -> bool:
    try:
      head = file_path.read_text(encoding="utf-8")[:_HEAD_BYTES]
    except OSError:
      return False
    yaml_text, _ = split_frontmatter(head)
    return bool(yaml_text) and bool(_CUT_KEY_RE.search(yaml_text))

  def preview(self, file_path: Path) -> StepPreview:
    if not self.applies_to(file_path):
      return StepPreview(touched=[], skipped=[file_path], drift=[])
    result = _transform(file_path.read_text(encoding="utf-8"))
    if not result.changed:
      return StepPreview(touched=[], skipped=[file_path], drift=result.drift)
    return StepPreview(touched=[file_path], skipped=[], drift=result.drift)

  def apply(self, file_path: Path) -> StepResult:
    if not self.applies_to(file_path):
      return StepResult(touched=[], skipped=[file_path])
    result = _transform(file_path.read_text(encoding="utf-8"))
    if not result.changed:
      return StepResult(touched=[], skipped=[file_path])
    atomic_write(file_path, result.text)
    return StepResult(touched=[file_path], skipped=[], drift_entries=[])


step = RevisionMetadataStep()

__all__ = ["RevisionMetadataStep", "step"]
