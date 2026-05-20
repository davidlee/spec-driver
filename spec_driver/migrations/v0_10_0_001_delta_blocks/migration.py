"""``DeltaBlocksStep`` — propagate ADR-010 placement to delta artefact kind.

See ``__init__.py`` and DR-138 §7 for the full contract. Per DEC-138-12 this
module may import only stdlib + ``spec_driver.migrations._helpers`` +
``spec_driver.migrations._protocol`` + this package's own sibling modules.
``yaml`` is consumed via stdlib-bridge style import (``import yaml``); it is
neither ``supekku.*`` nor a forbidden ``spec_driver`` subtree.
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
from spec_driver.migrations.v0_10_0_001_delta_blocks._emitters import (
  DELTA_CONTEXT_INPUTS_MARKER,
  DELTA_RELATIONSHIPS_MARKER,
  DELTA_RISK_REGISTER_MARKER,
  render_context_inputs_block,
  render_relationships_block,
  render_risk_register_block,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_HEAD_BYTES = 4096

_FM_CUT_KEYS = (
  "applies_to",
  "context_inputs",
  "risk_register",
  "outcome_summary",
)
_UNIVERSAL_CUT_KEYS = ("lifecycle", "aliases", "auditers", "source")

# Head-of-file detection regex (DR-138 §7.2). Matches any of the cut keys when
# they appear at the start of a frontmatter line. Universal-cut set per DR-136
# §4 (``owners`` and ``summary`` are kept; F-138-28).
_LEGACY_HEAD_PATTERN = re.compile(
  r"^(" + "|".join(re.escape(k) for k in (*_FM_CUT_KEYS, *_UNIVERSAL_CUT_KEYS)) + r"):",
  re.MULTILINE,
)

# Block-presence detectors (mirror of ``make_block_pattern`` from supekku).
_RELATIONSHIPS_BLOCK_RE = re.compile(
  r"```(?:yaml|yml)\s+" + re.escape(DELTA_RELATIONSHIPS_MARKER) + r"\n(.*?)```",
  re.DOTALL,
)
_CONTEXT_INPUTS_BLOCK_RE = re.compile(
  r"```(?:yaml|yml)\s+" + re.escape(DELTA_CONTEXT_INPUTS_MARKER) + r"\n(.*?)```",
  re.DOTALL,
)
_RISK_REGISTER_BLOCK_RE = re.compile(
  r"```(?:yaml|yml)\s+" + re.escape(DELTA_RISK_REGISTER_MARKER) + r"\n(.*?)```",
  re.DOTALL,
)

# Body section markers.
_RISKS_SECTION_RE = re.compile(
  r"(?ms)^##[ \t]+\d*\.?[ \t]*risks?(?:[ \t]*&[ \t]*mitigations?)?[ \t]*\n.*?"
  r"(?=^##[ \t]|\Z)",
  re.IGNORECASE,
)
_TOP_LEVEL_HEADING_RE = re.compile(r"(?m)^##[ \t]+(?P<num>\d+)\.")
_OUTCOME_HEADING_RE = re.compile(r"(?m)^##[ \t]+Outcome[ \t]*$")
_IMPL_NOTES_HEADING_RE = re.compile(
  r"(?m)^##[ \t]+(?:\d+\.[ \t]+)?Implementation[ \t]+Notes[ \t]*$"
)

# Context-input type handling per DR-138 §5.1.
_CTX_TYPE_CANONICAL = frozenset(
  {
    "delta",
    "revision",
    "audit",
    "phase",
    "plan",
    "spec",
    "prod",
    "adr",
    "issue",
    "problem",
    "improvement",
    "risk",
    "memory",
    "decision",
    "policy",
    "standard",
    "document",
    "code",
    "research",
  }
)
_CTX_TYPE_ALIASES: dict[str, str] = {
  "reference": "document",
  "brief": "document",
  "external": "document",
  "investigation": "research",
}
_CTX_TYPE_TOLERATED = "unknown"

_RISK_LIKELIHOOD = frozenset({"low", "medium", "high"})
_RISK_IMPACT = frozenset({"low", "medium", "high"})

# Drift kinds (stable strings; consumed by orchestrator log + VT assertions).
DRIFT_RELATIONSHIPS_SYNTH = "relationships_block_synthesised_from_fm"
DRIFT_FM_BLOCK_DISAGREEMENT = "fm_block_disagreement"
DRIFT_FM_SPECS_UNMATCHED = "fm_specs_unmatched"
DRIFT_FM_REQS_UNMATCHED = "fm_requirements_unmatched"
DRIFT_CTX_UNMAPPED_TYPE = "context_input_unmapped_type"
DRIFT_RISK_MISSING_LIKELIHOOD = "risk_missing_likelihood"
DRIFT_RISK_MISSING_IMPACT = "risk_missing_impact"
DRIFT_OUTCOME_CONFLICT = "outcome_overwrite_conflict"
DRIFT_BODY_RISK_NARRATIVE = "body_risk_narrative"
DRIFT_BODY_RENUMBER = "body_renumber"


# ---------------------------------------------------------------------------
# Transform result
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _DriftEntry:
  """Single drift observation captured during a transform."""

  kind: str
  detail: str


@dataclass(frozen=True)
class _Transform:
  """Pure transform result: new text + drift entries + change flag."""

  text: str
  drift: list[_DriftEntry] = field(default_factory=list)
  changed: bool = False


# ---------------------------------------------------------------------------
# Block extraction
# ---------------------------------------------------------------------------


def _extract_block(text: str, pattern: re.Pattern[str]) -> dict[str, Any] | None:
  match = pattern.search(text)
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
# Normalisation helpers
# ---------------------------------------------------------------------------


def _normalise_ctx_type(raw_type: str | None) -> tuple[str, _DriftEntry | None]:
  if raw_type is None or not isinstance(raw_type, str):
    return _CTX_TYPE_TOLERATED, _DriftEntry(
      DRIFT_CTX_UNMAPPED_TYPE, f"missing or non-string type: {raw_type!r}"
    )
  value = raw_type.strip()
  if value in _CTX_TYPE_CANONICAL:
    return value, None
  if value in _CTX_TYPE_ALIASES:
    return _CTX_TYPE_ALIASES[value], None
  return _CTX_TYPE_TOLERATED, _DriftEntry(
    DRIFT_CTX_UNMAPPED_TYPE, f"unmapped type: {value!r}"
  )


def _normalise_context_input(
  entry: Any,
) -> tuple[dict[str, Any], list[_DriftEntry]]:
  """Apply DR-138 §5.3 normalisation to a single context_inputs entry."""
  drift: list[_DriftEntry] = []
  if isinstance(entry, str):
    return (
      {"type": _CTX_TYPE_TOLERATED, "id": entry},
      [
        _DriftEntry(
          DRIFT_CTX_UNMAPPED_TYPE,
          f"plain-string entry promoted to tolerated type 'unknown': {entry!r}",
        )
      ],
    )
  if not isinstance(entry, dict):
    return (
      {"type": _CTX_TYPE_TOLERATED, "id": str(entry)},
      [
        _DriftEntry(
          DRIFT_CTX_UNMAPPED_TYPE,
          f"non-mapping entry coerced to id-string: {entry!r}",
        )
      ],
    )

  out: dict[str, Any] = {}
  ctx_type, drift_type = _normalise_ctx_type(entry.get("type"))
  out["type"] = ctx_type
  if drift_type:
    drift.append(drift_type)

  identifier = entry.get("id") or entry.get("ref")
  if identifier is not None:
    out["id"] = str(identifier)

  summary = entry.get("summary") or entry.get("note") or entry.get("annotation")
  if summary is not None and summary != "":
    out["summary"] = summary

  return out, drift


def _normalise_risk(entry: Any) -> tuple[dict[str, Any], list[_DriftEntry]]:
  """Apply DR-138 §5.3 normalisation to a single risk_register entry."""
  if not isinstance(entry, dict):
    return {}, [
      _DriftEntry(DRIFT_CTX_UNMAPPED_TYPE, f"non-mapping risk entry skipped: {entry!r}")
    ]

  drift: list[_DriftEntry] = []
  out: dict[str, Any] = {}
  for key in ("id",):
    if entry.get(key) is not None:
      out[key] = str(entry[key])

  title = entry.get("title") or entry.get("description")
  if title:
    out["title"] = title

  likelihood = entry.get("likelihood")
  if likelihood is None or likelihood not in _RISK_LIKELIHOOD:
    drift.append(
      _DriftEntry(
        DRIFT_RISK_MISSING_LIKELIHOOD,
        f"risk {entry.get('id') or entry.get('title') or '<unknown>'!r}: "
        f"likelihood missing or invalid ({likelihood!r})",
      )
    )
  else:
    out["likelihood"] = likelihood

  impact = entry.get("impact")
  if impact is None or impact not in _RISK_IMPACT:
    drift.append(
      _DriftEntry(
        DRIFT_RISK_MISSING_IMPACT,
        f"risk {entry.get('id') or entry.get('title') or '<unknown>'!r}: "
        f"impact missing or invalid ({impact!r})",
      )
    )
  else:
    out["impact"] = impact

  for key in ("exposure", "mitigation"):
    if entry.get(key) is not None:
      out[key] = entry[key]

  status = entry.get("status")
  out["status"] = status if status is not None else "open"

  return out, drift


# ---------------------------------------------------------------------------
# Body transforms
# ---------------------------------------------------------------------------


def _delete_risks_section(body: str) -> tuple[str, str | None]:
  """Strip a top-level ``## N. Risks (& Mitigations)`` section.

  Returns (new_body, deleted_section_content_or_None).
  """
  match = _RISKS_SECTION_RE.search(body)
  if not match:
    return body, None
  section = match.group(0)
  new_body = body[: match.start()] + body[match.end() :]
  return new_body, section


def _renumber_top_headings(body: str) -> tuple[str, list[tuple[int, int]]]:
  """Shift top-level ``## N.`` headings down by one for N >= 8.

  Returns (new_body, list_of_(old_num, new_num)). Sub-headings (``### N.M``)
  are left untouched (F-138-D — cross-refs typically point at top-level
  sections).
  """
  shifts: list[tuple[int, int]] = []

  def _shift(match: re.Match[str]) -> str:
    num = int(match.group("num"))
    if num >= 8:
      new_num = num - 1
      shifts.append((num, new_num))
      return match.group(0).replace(f"{num}.", f"{new_num}.", 1)
    return match.group(0)

  new_body = _TOP_LEVEL_HEADING_RE.sub(_shift, body)
  return new_body, shifts


def _insert_outcome_section(body: str, outcome: str) -> tuple[str, bool, str | None]:
  """Insert a ``## Outcome`` section.

  Returns (new_body, inserted, conflict_detail). When body already has a
  ``## Outcome`` section and the supplied outcome differs from the existing
  content, ``conflict_detail`` carries a drift message; the existing section
  is preserved (no auto-overwrite).
  """
  existing = _OUTCOME_HEADING_RE.search(body)
  if existing is not None:
    return body, False, _existing_outcome_conflict(body, existing, outcome)

  text = outcome.rstrip("\n")
  section = f"## Outcome\n\n{text}\n"

  impl_match = _IMPL_NOTES_HEADING_RE.search(body)
  if impl_match is not None:
    insert_at = impl_match.start()
    prefix = body[:insert_at].rstrip()
    suffix = body[insert_at:]
    new_body = f"{prefix}\n\n{section}\n{suffix}"
    return new_body, True, None

  trimmed = body.rstrip()
  new_body = f"{trimmed}\n\n{section}" if trimmed else section
  if not new_body.endswith("\n"):
    new_body = f"{new_body}\n"
  return new_body, True, None


def _existing_outcome_conflict(
  body: str, existing_match: re.Match[str], new_outcome: str
) -> str | None:
  start = existing_match.end()
  next_heading = re.search(r"(?m)^##[ \t]", body[start:])
  end = start + next_heading.start() if next_heading else len(body)
  existing_text = body[start:end].strip()
  if existing_text == new_outcome.strip():
    return None
  return (
    "body ## Outcome already present and differs from frontmatter "
    "outcome_summary; keeping body content"
  )


# ---------------------------------------------------------------------------
# Block synthesis from frontmatter
# ---------------------------------------------------------------------------


def _synthesise_relationships(
  delta_id: str, frontmatter: dict[str, Any]
) -> tuple[str | None, list[_DriftEntry]]:
  fm_applies_to = frontmatter.get("applies_to") or {}
  specs = list(fm_applies_to.get("specs") or [])
  reqs = list(fm_applies_to.get("requirements") or [])
  if not specs and not reqs:
    return None, []
  rendered = render_relationships_block(
    delta_id,
    primary_specs=[str(s) for s in specs] or None,
    implements_requirements=[str(r) for r in reqs] or None,
  )
  return rendered, [
    _DriftEntry(
      DRIFT_RELATIONSHIPS_SYNTH,
      f"synthesised relationships block from FM applies_to "
      f"(specs={specs}, requirements={reqs}); operator review needed for "
      f"primary/collaborators + implements/updates/verifies splits",
    )
  ]


def _synthesise_context_inputs(
  frontmatter: dict[str, Any],
) -> tuple[str, list[_DriftEntry]]:
  raw_entries = frontmatter.get("context_inputs") or []
  drift: list[_DriftEntry] = []
  entries: list[dict[str, Any]] = []
  for raw in raw_entries:
    entry, entry_drift = _normalise_context_input(raw)
    drift.extend(entry_drift)
    entries.append(entry)
  return render_context_inputs_block(entries=entries), drift


def _synthesise_risk_register(
  frontmatter: dict[str, Any],
) -> tuple[str, list[_DriftEntry]]:
  raw_entries = frontmatter.get("risk_register") or []
  drift: list[_DriftEntry] = []
  risks: list[dict[str, Any]] = []
  for raw in raw_entries:
    risk, entry_drift = _normalise_risk(raw)
    drift.extend(entry_drift)
    if risk:
      risks.append(risk)
  return render_risk_register_block(risks=risks), drift


# ---------------------------------------------------------------------------
# Reconciliation (FM ↔ block specs / requirements)
# ---------------------------------------------------------------------------


def _reconcile_applies_to(
  frontmatter: dict[str, Any], block: dict[str, Any] | None
) -> list[_DriftEntry]:
  if block is None:
    return []
  fm_applies_to = frontmatter.get("applies_to") or {}
  fm_specs = {str(s) for s in (fm_applies_to.get("specs") or [])}
  fm_reqs = {str(r) for r in (fm_applies_to.get("requirements") or [])}

  spec_groups = block.get("specs") or {}
  block_specs = {
    str(s) for key in ("primary", "collaborators") for s in (spec_groups.get(key) or [])
  }
  req_groups = block.get("requirements") or {}
  block_reqs = {
    str(r)
    for key in ("implements", "updates", "verifies")
    for r in (req_groups.get(key) or [])
  }

  drift: list[_DriftEntry] = []
  unmatched_specs = sorted(fm_specs - block_specs)
  if unmatched_specs:
    drift.append(
      _DriftEntry(
        DRIFT_FM_SPECS_UNMATCHED,
        f"FM applies_to.specs entries absent from block specs.primary ∪ "
        f"specs.collaborators: {unmatched_specs}",
      )
    )
  unmatched_reqs = sorted(fm_reqs - block_reqs)
  if unmatched_reqs:
    drift.append(
      _DriftEntry(
        DRIFT_FM_REQS_UNMATCHED,
        f"FM applies_to.requirements entries absent from block "
        f"requirements.{{implements,updates,verifies}}: {unmatched_reqs}",
      )
    )
  return drift


# ---------------------------------------------------------------------------
# Frontmatter scalar cleanup
# ---------------------------------------------------------------------------


def _strip_cut_keys(frontmatter: dict[str, Any]) -> dict[str, Any]:
  """Return frontmatter dict with cut keys removed (in declaration order).

  ``yaml.safe_dump`` with ``sort_keys=False`` preserves insertion order, so we
  rebuild a fresh dict in the original key order skipping the cut set.
  """
  drop = set(_FM_CUT_KEYS) | set(_UNIVERSAL_CUT_KEYS)
  return {k: v for k, v in frontmatter.items() if k not in drop}


# ---------------------------------------------------------------------------
# Block insertion into body
# ---------------------------------------------------------------------------


def _ensure_block_in_body(body: str, marker_re: re.Pattern[str], block: str) -> str:
  """Append ``block`` to ``body`` if no matching marker is present."""
  if marker_re.search(body):
    return body
  trimmed = body.rstrip()
  joiner = "\n\n" if trimmed else ""
  result = f"{trimmed}{joiner}{block}\n"
  if not result.endswith("\n"):
    result = f"{result}\n"
  return result


def _replace_block(body: str, marker_re: re.Pattern[str], block: str) -> str:
  """Replace the first matching block in ``body``; raise if no match."""
  match = marker_re.search(body)
  if match is None:
    msg = "block marker not found for replacement"
    raise ValueError(msg)
  return body[: match.start()] + block + body[match.end() :]


# ---------------------------------------------------------------------------
# Full transform
# ---------------------------------------------------------------------------


def _transform(text: str) -> _Transform:
  """Apply DR-138 §7.3 mechanics to ``text``; return a ``_Transform`` result."""
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
  delta_id = str(frontmatter.get("id") or "")

  rel_block = _extract_block(body, _RELATIONSHIPS_BLOCK_RE)
  drift.extend(_reconcile_applies_to(frontmatter, rel_block))

  body, drift_rel = _ensure_relationships_block(body, delta_id, frontmatter)
  drift.extend(drift_rel)

  body, drift_ctx = _ensure_context_inputs_block(body, frontmatter)
  drift.extend(drift_ctx)

  body, drift_risk = _ensure_risk_register_block(body, frontmatter)
  drift.extend(drift_risk)

  outcome = frontmatter.get("outcome_summary")
  if outcome:
    body, _inserted, conflict = _insert_outcome_section(body, str(outcome))
    if conflict:
      drift.append(_DriftEntry(DRIFT_OUTCOME_CONFLICT, conflict))

  body, deleted_risks = _delete_risks_section(body)
  if deleted_risks:
    drift.append(_DriftEntry(DRIFT_BODY_RISK_NARRATIVE, deleted_risks))

  body, shifts = _renumber_top_headings(body)
  if shifts:
    drift.append(
      _DriftEntry(
        DRIFT_BODY_RENUMBER,
        "shifted top-level headings: "
        + ", ".join(f"{old}->{new}" for old, new in shifts),
      )
    )

  new_fm = _strip_cut_keys(frontmatter)
  new_yaml = yaml.safe_dump(new_fm, sort_keys=False, allow_unicode=True).rstrip()
  new_text = f"---\n{new_yaml}\n---\n{body}"
  return _Transform(text=new_text, drift=drift, changed=new_text != text)


def _ensure_relationships_block(
  body: str, delta_id: str, frontmatter: dict[str, Any]
) -> tuple[str, list[_DriftEntry]]:
  existing = _extract_block(body, _RELATIONSHIPS_BLOCK_RE)
  if existing is not None:
    return body, []
  rendered, drift = _synthesise_relationships(delta_id, frontmatter)
  if rendered is None:
    return body, drift
  return _ensure_block_in_body(body, _RELATIONSHIPS_BLOCK_RE, rendered), drift


def _ensure_context_inputs_block(
  body: str, frontmatter: dict[str, Any]
) -> tuple[str, list[_DriftEntry]]:
  existing = _extract_block(body, _CONTEXT_INPUTS_BLOCK_RE)
  rendered, drift = _synthesise_context_inputs(frontmatter)
  if existing is None:
    return _ensure_block_in_body(body, _CONTEXT_INPUTS_BLOCK_RE, rendered), drift
  if frontmatter.get("context_inputs"):
    drift.append(
      _DriftEntry(
        DRIFT_FM_BLOCK_DISAGREEMENT,
        "FM context_inputs and block both present; keeping block, "
        f"discarding FM payload: {frontmatter.get('context_inputs')!r}",
      )
    )
  return body, drift


def _ensure_risk_register_block(
  body: str, frontmatter: dict[str, Any]
) -> tuple[str, list[_DriftEntry]]:
  existing = _extract_block(body, _RISK_REGISTER_BLOCK_RE)
  rendered, drift = _synthesise_risk_register(frontmatter)
  if existing is None:
    return _ensure_block_in_body(body, _RISK_REGISTER_BLOCK_RE, rendered), drift
  if frontmatter.get("risk_register"):
    drift.append(
      _DriftEntry(
        DRIFT_FM_BLOCK_DISAGREEMENT,
        "FM risk_register and block both present; keeping block, "
        f"discarding FM payload: {frontmatter.get('risk_register')!r}",
      )
    )
  return body, drift


def _has_legacy_keys(yaml_text: str) -> bool:
  return bool(_LEGACY_HEAD_PATTERN.search(yaml_text))


# ---------------------------------------------------------------------------
# Step class
# ---------------------------------------------------------------------------


class DeltaBlocksStep(BaseMigrationStep):
  """Forward-only sweep landing the DR-138 §7 mechanics for delta artefacts."""

  applies_to_kind = "delta"
  description = (
    "ADR-010 placement: applies_to derived; context_inputs / risk_register -> "
    "blocks; outcome_summary -> body ## Outcome"
  )

  def applies_to(self, file_path: Path) -> bool:
    try:
      head = file_path.read_text(encoding="utf-8")[:_HEAD_BYTES]
    except OSError:
      return False
    return bool(_LEGACY_HEAD_PATTERN.search(head))

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


step = DeltaBlocksStep()

__all__ = ["DeltaBlocksStep", "step"]
