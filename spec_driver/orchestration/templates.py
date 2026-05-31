"""Template orchestration: kind-aware frontmatter renderer + regenerator.

Shared by `regenerate_template` (templates path) and `dump_markdown_file_create`
(artefact creation path) — both call `render_frontmatter_for_kind` so the
enum-comment hints and per-kind shape stay in one place (POL-001).

`TEMPLATE_PLACEHOLDERS` lives here rather than on `BlockMetadata` (DEC-137-09)
to keep `BlockMetadata` as pure data shape (POL-003).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from difflib import unified_diff
from pathlib import Path
from typing import Any

from spec_driver.core.spec_utils import write_markdown_file
from spec_driver.core.yaml_emit import emit_yaml_block

# Jinja-style placeholder strings emitted when render is invoked in reference
# mode (data=None). These are decorative — the create-path supplies its own
# frontmatter dict; templates carry these so `validate templates` can detect
# metadata drift and authors see a canonical shape with enum hints.
TEMPLATE_PLACEHOLDERS: Mapping[str, Mapping[str, str]] = {
  "delta": {
    "id": "{{ delta_id }}",
    "slug": "{{ slug }}",
    "name": "Delta - {{ name }}",
    "created": "{{ today }}",
    "updated": "{{ today }}",
  },
  "design_revision": {
    "id": "{{ design_revision_id }}",
    "slug": "{{ slug }}",
    "name": "Design Revision - {{ name }}",
    "created": "{{ today }}",
    "updated": "{{ today }}",
    "delta_ref": "{{ delta_id }}",
  },
  "plan": {
    "id": "{{ plan_id }}",
    "slug": "{{ slug }}",
    "name": "Implementation Plan - {{ name }}",
    "created": "{{ today }}",
    "updated": "{{ today }}",
  },
  "phase": {
    "id": "{{ phase_id }}",
    "slug": "{{ slug }}",
    "name": "{{ plan_id }} Phase {{ phase_number }}",
    "created": "{{ today }}",
    "updated": "{{ today }}",
    "plan": "{{ plan_id }}",
    "delta": "{{ delta_id }}",
  },
  "audit": {
    "id": "{{ audit_id }}",
    "slug": "{{ slug }}",
    "name": "Audit - {{ name }}",
    "created": "{{ today }}",
    "updated": "{{ today }}",
  },
  "revision": {
    "id": "{{ revision_id }}",
    "slug": "{{ slug }}",
    "name": "Revision - {{ name }}",
    "created": "{{ today }}",
    "updated": "{{ today }}",
  },
  "spec": {
    "id": "{{ spec_id }}",
    "slug": "{{ slug }}",
    "name": "{{ name }}",
    "created": "{{ today }}",
    "updated": "{{ today }}",
  },
  "prod": {
    "id": "{{ prod_id }}",
    "slug": "{{ slug }}",
    "name": "{{ name }}",
    "created": "{{ today }}",
    "updated": "{{ today }}",
  },
  "memory": {
    "id": "{{ memory_id }}",
    "slug": "{{ slug }}",
    "name": "{{ name }}",
    "created": "{{ today }}",
    "updated": "{{ today }}",
  },
  "issue": {
    "id": "{{ issue_id }}",
    "slug": "{{ slug }}",
    "name": "{{ name }}",
    "created": "{{ today }}",
    "updated": "{{ today }}",
  },
  "problem": {
    "id": "{{ problem_id }}",
    "slug": "{{ slug }}",
    "name": "{{ name }}",
    "created": "{{ today }}",
    "updated": "{{ today }}",
  },
  "risk": {
    "id": "{{ risk_id }}",
    "slug": "{{ slug }}",
    "name": "{{ name }}",
    "created": "{{ today }}",
    "updated": "{{ today }}",
  },
  "policy": {
    "id": "{{ policy_id }}",
    "slug": "{{ slug }}",
    "name": "{{ name }}",
    "created": "{{ today }}",
    "updated": "{{ today }}",
  },
  "standard": {
    "id": "{{ standard_id }}",
    "slug": "{{ slug }}",
    "name": "{{ name }}",
    "created": "{{ today }}",
    "updated": "{{ today }}",
  },
  "adr": {
    "id": "{{ adr_id }}",
    "slug": "{{ slug }}",
    "name": "{{ name }}",
    "created": "{{ today }}",
    "updated": "{{ today }}",
  },
}

_STATUS_DEFAULT = "draft"


class UnknownKindError(ValueError):
  """Raised when a kind has no entry in the frontmatter metadata registry."""


def _build_comment_map(metadata: Any) -> dict[str, str]:
  """Derive the inline `# comment` map from a BlockMetadata.

  - Enum fields: `# one of: a | b | c`.
  - Fields with tolerated aliases: `# tolerated alias: <a> -> <canonical>
    (sunset <after>)` per entry, comma-separated.

  Container values (object/array) are deliberately excluded — `emit_yaml_block`
  only honours scalar-line comments per DR-137 §5.1.
  """
  comments: dict[str, str] = {}
  for name, field in metadata.fields.items():
    parts: list[str] = []
    if field.type == "enum" and field.enum_values:
      parts.append("one of: " + " | ".join(str(v) for v in field.enum_values))
    if field.tolerated_aliases:
      tol = ", ".join(
        f"{alias} -> {entry.canonical} (sunset {entry.sunset_after})"
        for alias, entry in field.tolerated_aliases.items()
      )
      parts.append(f"tolerated: {tol}")
    if parts:
      comments[name] = "; ".join(parts)
  return comments


def _placeholder_value(kind: str, field_name: str, field: Any) -> Any:
  """Resolve the placeholder value for a single field in reference mode.

  Precedence: TEMPLATE_PLACEHOLDERS -> default_value -> typed-blank fallback.
  """
  placeholders = TEMPLATE_PLACEHOLDERS.get(kind, {})
  if field_name in placeholders:
    return placeholders[field_name]
  if field_name == "kind":
    return kind
  if field_name == "status":
    return _STATUS_DEFAULT
  if field.default_value is not None:
    return field.default_value
  if field.type == "array":
    return []
  if field.type == "object":
    return {}
  return ""


def _should_include_in_reference(field_name: str, field: Any, kind: str) -> bool:
  """Decide whether *field_name* appears in placeholder-mode output.

  Conservative: only required fields plus those explicitly listed in
  `TEMPLATE_PLACEHOLDERS[kind]`. Optional fields are omitted from the
  reference template — they'll show up at create time when the caller
  supplies a concrete value, and the validator catches missing required
  fields at the strict layer.
  """
  if field_name in TEMPLATE_PLACEHOLDERS.get(kind, {}):
    return True
  return field.required


def render_frontmatter_for_kind(
  kind: str,
  data: Mapping[str, Any] | None = None,
) -> str:
  """Render YAML frontmatter for *kind* with enum-comment hints inline.

  - When *data* is None (reference mode): emit placeholders (from
    `TEMPLATE_PLACEHOLDERS[kind]` / `default_value` / typed blanks) for the
    required + canonical-persistence fields. Used by `regenerate_template`.
  - When *data* is a Mapping (concrete mode): emit the supplied data using
    the same comment map. Used by `dump_markdown_file_create`.
  - Output omits leading/trailing newlines and `---` markers — the caller
    wraps with delimiters when writing to disk.

  Raises `UnknownKindError` if *kind* has no metadata entry.
  """
  from supekku.scripts.lib.core.frontmatter_metadata import (  # noqa: PLC0415
    FRONTMATTER_METADATA_REGISTRY,
  )

  metadata = FRONTMATTER_METADATA_REGISTRY.get(kind)
  if metadata is None:
    msg = f"Unknown kind for frontmatter render: {kind!r}"
    raise UnknownKindError(msg)

  comments = _build_comment_map(metadata)

  if data is None:
    rendered: dict[str, Any] = {}
    for field_name, field in metadata.fields.items():
      if not _should_include_in_reference(field_name, field, kind):
        continue
      rendered[field_name] = _placeholder_value(kind, field_name, field)
    return emit_yaml_block(rendered, comments=comments)

  return emit_yaml_block(data, comments=comments)


def dump_markdown_file_create(
  path: Path | str,
  frontmatter: Mapping[str, Any],
  body: str,
  *,
  kind: str,
) -> None:
  """Write a NEW artefact at *path*, rendering frontmatter with enum hints.

  Routes through `render_frontmatter_for_kind(kind, data=frontmatter)` so
  enum-comment hints appear inline (POL-001). For kinds without a registered
  metadata entry (e.g. spec testing companions, improvement backlog items)
  falls through to plain `emit_yaml_block` — no hints, but still atomic and
  consistent with the rest of the create path. Errors if *path* already
  exists.
  """
  path = Path(path)
  if path.exists():
    msg = f"refusing to overwrite existing artefact: {path} (use _update)"
    raise FileExistsError(msg)
  try:
    fm_yaml = render_frontmatter_for_kind(kind, data=dict(frontmatter))
  except UnknownKindError:
    fm_yaml = emit_yaml_block(dict(frontmatter))
  write_markdown_file(path, fm_yaml, body)


@dataclass(frozen=True)
class TemplateDrift:
  """Difference between an on-disk template and the canonical rendered shape."""

  path: Path
  kind: str
  diff: str


def _split_frontmatter(text: str) -> tuple[str, str]:
  """Split a markdown file into (frontmatter, body).

  Frontmatter is the content between the first pair of `---` lines. If the
  file does not begin with `---`, returns ("", text). Leading newlines on
  the body (the conventional blank line separating fm from prose) are stripped
  so callers receive the body content directly.
  Raises `ValueError` if a leading `---` is present without a closer.
  """
  if not text.startswith("---"):
    return "", text
  end_idx = text.find("\n---", 3)
  if end_idx == -1:
    msg = "template begins with `---` but no closing `---` was found"
    raise ValueError(msg)
  fm_text = text[3:end_idx].lstrip("\n").rstrip()
  body = text[end_idx + len("\n---") :].lstrip("\n")
  return fm_text, body


def _compose_template(fm_text: str, body: str) -> str:
  """Build the on-disk template text from a frontmatter block and body.

  Canonical layout: `---\\n<fm>\\n---\\n\\n<body>` with a blank line between
  fm and body. Round-tripping through `_split_frontmatter` is idempotent.
  """
  out = f"---\n{fm_text}\n---\n"
  if body:
    out += "\n" + body
  if not out.endswith("\n"):
    out += "\n"
  return out


def _atomic_write(path: Path, text: str) -> None:
  """Write *text* to *path* atomically (temp file in same directory + rename)."""
  tmp = path.with_suffix(path.suffix + ".tmp")
  tmp.write_text(text, encoding="utf-8")
  tmp.replace(path)


def regenerate_template(kind: str, template_path: Path) -> bool:
  """Rewrite *template_path*'s frontmatter from canonical metadata.

  - The body (everything after the closing `---`) is preserved verbatim,
    including any Jinja blocks (`{{ delta_relationships_block }}` etc.).
  - If the template has no frontmatter, a fresh block is inserted.
  - Atomic via temp + rename.
  - Returns True iff bytes changed.

  Raises `ValueError` if the existing frontmatter region is malformed
  (opening `---` without closer); intentional fail-loud per F-13.
  """
  existing = template_path.read_text(encoding="utf-8")
  _, body = _split_frontmatter(existing)
  new_fm = render_frontmatter_for_kind(kind, data=None)
  proposed = _compose_template(new_fm, body)
  if proposed == existing:
    return False
  _atomic_write(template_path, proposed)
  return True


def _template_filename_for(kind: str) -> str:
  """Map a kind to its canonical template filename under `supekku/templates/`."""
  return {
    "adr": "ADR.md",
    "audit": "audit.md",
    "delta": "delta.md",
    "design_revision": "design_revision.md",
    "phase": "phase.md",
    "plan": "plan.md",
    "policy": "policy-template.md",
    "revision": "revision.md",
    "spec": "spec.md",
    "standard": "standard-template.md",
  }.get(kind, f"{kind}.md")


_TEMPLATE_KINDS: tuple[str, ...] = (
  "adr",
  "audit",
  "delta",
  "design_revision",
  "phase",
  "plan",
  "policy",
  "revision",
  "spec",
  "standard",
)


def validate_templates(
  repo_root: Path,
  *,
  kinds: tuple[str, ...] | None = None,
) -> list[TemplateDrift]:
  """Dry-run `regenerate_template` for every kind under `supekku/templates/`.

  Returns the list of drifts; empty list means clean.

  - *kinds* restricts the walk to a subset (default: every kind with a
    template file under `supekku/templates/`).
  - Missing template files are skipped with no diagnostic — `validate
    templates` is a drift gate, not an existence check.
  """
  target_kinds = kinds if kinds is not None else _TEMPLATE_KINDS
  templates_dir = repo_root / "supekku" / "templates"
  drifts: list[TemplateDrift] = []
  for kind in target_kinds:
    path = templates_dir / _template_filename_for(kind)
    if not path.exists():
      continue
    existing = path.read_text(encoding="utf-8")
    _, body = _split_frontmatter(existing)
    new_fm = render_frontmatter_for_kind(kind, data=None)
    proposed = _compose_template(new_fm, body)
    if proposed != existing:
      diff = "".join(
        unified_diff(
          existing.splitlines(keepends=True),
          proposed.splitlines(keepends=True),
          fromfile=str(path),
          tofile=f"{path} (proposed)",
        )
      )
      drifts.append(TemplateDrift(path=path, kind=kind, diff=diff))
  return drifts


__all__ = [
  "TEMPLATE_PLACEHOLDERS",
  "TemplateDrift",
  "UnknownKindError",
  "dump_markdown_file_create",
  "regenerate_template",
  "render_frontmatter_for_kind",
  "validate_templates",
]
