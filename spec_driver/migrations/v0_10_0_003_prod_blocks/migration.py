"""``ProdBlocksStep`` — DR-139 §3.2 placement for prod artefact kind.

Cuts deprecated FM keys and emits block schemas for non-empty structured
fields. See ``__init__.py`` for scope.

Per DEC-138-12 this module may import only stdlib +
``spec_driver.migrations._helpers`` + ``spec_driver.migrations._protocol``
+ pyyaml.
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

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_HEAD_BYTES = 4096

_FM_CUT_KEYS = (
  "hypotheses",
  "decisions",
  "verification_strategy",
  "scope",
)

_LEGACY_HEAD_PATTERN = re.compile(
  r"^(" + "|".join(re.escape(k) for k in _FM_CUT_KEYS) + r"):",
  re.MULTILINE,
)

# Block markers (frozen-local; shared schema per DEC-139-01).
_HYPOTHESES_MARKER = "supekku:spec.hypotheses@v1"
_HYPOTHESES_SCHEMA = "supekku.spec.hypotheses"
_HYPOTHESES_VERSION = 1

_DECISIONS_MARKER = "supekku:spec.decisions@v1"
_DECISIONS_SCHEMA = "supekku.spec.decisions"
_DECISIONS_VERSION = 1

# Block-presence detectors.
_HYPOTHESES_BLOCK_RE = re.compile(
  r"```(?:yaml|yml)\s+" + re.escape(_HYPOTHESES_MARKER) + r"\n(.*?)```",
  re.DOTALL,
)
_DECISIONS_BLOCK_RE = re.compile(
  r"```(?:yaml|yml)\s+" + re.escape(_DECISIONS_MARKER) + r"\n(.*?)```",
  re.DOTALL,
)

# Body section for scope insertion.
_INTENT_HEADING_RE = re.compile(
  r"(?m)^##[ \t]+(?:\d+\.[ \t]+)?Intent[^\n]*",
)

# Drift kinds.
DRIFT_HYPOTHESES_EMITTED = "hypotheses_block_emitted_from_fm"
DRIFT_DECISIONS_EMITTED = "decisions_block_emitted_from_fm"
DRIFT_SCOPE_MOVED = "scope_moved_to_prose"
DRIFT_VERIFICATION_STRATEGY_CUT = "verification_strategy_cut"


# ---------------------------------------------------------------------------
# Transform result
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _DriftEntry:
  kind: str
  detail: str


@dataclass(frozen=True)
class _Transform:
  text: str
  drift: list[_DriftEntry] = field(default_factory=list)
  changed: bool = False


# ---------------------------------------------------------------------------
# Block emitters (frozen-local)
# ---------------------------------------------------------------------------


def _emit_hypotheses_block(prod_id: str, hypotheses: list[dict[str, Any]]) -> str:
  items = [{k: v for k, v in h.items() if v is not None} for h in hypotheses]
  head = (
    f"```yaml {_HYPOTHESES_MARKER}\n"
    f"schema: {_HYPOTHESES_SCHEMA}\n"
    f"version: {_HYPOTHESES_VERSION}\n"
    f"spec: {prod_id}\n"
  )
  if not items:
    return head + "hypotheses: []\n```"
  body = yaml.safe_dump(
    {"hypotheses": items},
    sort_keys=False,
    allow_unicode=True,
    default_flow_style=False,
  ).rstrip()
  return head + body + "\n```"


def _emit_decisions_block(prod_id: str, decisions: list[dict[str, Any]]) -> str:
  items = [{k: v for k, v in d.items() if v is not None} for d in decisions]
  head = (
    f"```yaml {_DECISIONS_MARKER}\n"
    f"schema: {_DECISIONS_SCHEMA}\n"
    f"version: {_DECISIONS_VERSION}\n"
    f"spec: {prod_id}\n"
  )
  if not items:
    return head + "decisions: []\n```"
  body = yaml.safe_dump(
    {"decisions": items},
    sort_keys=False,
    allow_unicode=True,
    default_flow_style=False,
  ).rstrip()
  return head + body + "\n```"


# ---------------------------------------------------------------------------
# Body helpers
# ---------------------------------------------------------------------------


def _append_block(body: str, block_re: re.Pattern[str], block: str) -> str:
  if block_re.search(body):
    return body
  trimmed = body.rstrip()
  joiner = "\n\n" if trimmed else ""
  return f"{trimmed}{joiner}{block}\n"


def _insert_scope_paragraph(body: str, scope_text: str) -> str:
  match = _INTENT_HEADING_RE.search(body)
  if match:
    end = match.end()
    return f"{body[:end]}\n\n> **Scope**: {scope_text}\n{body[end:]}"
  trimmed = body.lstrip("\n")
  return f"> **Scope**: {scope_text}\n\n{trimmed}"


# ---------------------------------------------------------------------------
# Full transform
# ---------------------------------------------------------------------------


def _transform(text: str) -> _Transform:
  yaml_text, body = split_frontmatter(text)
  if not yaml_text:
    return _Transform(text=text, drift=[], changed=False)

  loaded = yaml.safe_load(yaml_text) or {}
  if not isinstance(loaded, dict):
    return _Transform(text=text, drift=[], changed=False)
  frontmatter: dict[str, Any] = loaded

  if not _has_legacy_keys(yaml_text):
    return _Transform(text=text, drift=[], changed=False)

  drift: list[_DriftEntry] = []
  prod_id = str(frontmatter.get("id") or "")

  # --- Emit blocks for non-empty structured fields ---
  hypotheses = frontmatter.get("hypotheses")
  if hypotheses and isinstance(hypotheses, list) and any(hypotheses):
    block = _emit_hypotheses_block(prod_id, hypotheses)
    body = _append_block(body, _HYPOTHESES_BLOCK_RE, block)
    drift.append(
      _DriftEntry(
        DRIFT_HYPOTHESES_EMITTED,
        f"emitted hypotheses block from FM ({len(hypotheses)} items)",
      )
    )

  decisions = frontmatter.get("decisions")
  if decisions and isinstance(decisions, list) and any(decisions):
    block = _emit_decisions_block(prod_id, decisions)
    body = _append_block(body, _DECISIONS_BLOCK_RE, block)
    drift.append(
      _DriftEntry(
        DRIFT_DECISIONS_EMITTED,
        f"emitted decisions block from FM ({len(decisions)} items)",
      )
    )

  # --- Move scope to prose ---
  scope = frontmatter.get("scope")
  if scope and isinstance(scope, str) and scope.strip():
    body = _insert_scope_paragraph(body, scope.strip())
    drift.append(
      _DriftEntry(
        DRIFT_SCOPE_MOVED,
        f"moved scope to prose body: {scope[:80]!r}",
      )
    )

  # --- Record verification_strategy cut ---
  vs = frontmatter.get("verification_strategy")
  if vs:
    drift.append(
      _DriftEntry(
        DRIFT_VERIFICATION_STRATEGY_CUT,
        f"removed verification_strategy: {vs!r}",
      )
    )

  # --- Strip cut keys from FM ---
  new_fm = {k: v for k, v in frontmatter.items() if k not in _FM_CUT_KEYS}

  new_yaml = yaml.safe_dump(new_fm, sort_keys=False, allow_unicode=True).rstrip()
  new_text = f"---\n{new_yaml}\n---\n{body}"
  return _Transform(text=new_text, drift=drift, changed=new_text != text)


def _has_legacy_keys(yaml_text: str) -> bool:
  return bool(_LEGACY_HEAD_PATTERN.search(yaml_text))


# ---------------------------------------------------------------------------
# Step class
# ---------------------------------------------------------------------------


class ProdBlocksStep(BaseMigrationStep):
  """Forward-only sweep landing DR-139 §3.2 mechanics for prod artefacts."""

  applies_to_kind = "prod"
  description = (
    "DR-139 placement: hypotheses/decisions/scope/verification_strategy "
    "cut; structured fields -> blocks"
  )

  def applies_to(self, file_path: Path) -> bool:
    try:
      head = file_path.read_text(encoding="utf-8")[:_HEAD_BYTES]
    except OSError:
      return False
    return _has_legacy_keys(head)

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
      return StepResult(touched=[], skipped=[file_path], drift_entries=[])
    text = file_path.read_text(encoding="utf-8")
    result = _transform(text)
    if not result.changed:
      return StepResult(touched=[], skipped=[file_path], drift_entries=[])
    atomic_write(file_path, result.text)
    drift_paths = [file_path] if result.drift else []
    return StepResult(
      touched=[file_path],
      skipped=[],
      drift_entries=drift_paths,
    )


step = ProdBlocksStep()

__all__ = ["ProdBlocksStep", "step"]
