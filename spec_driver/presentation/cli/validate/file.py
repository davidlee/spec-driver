"""``spec-driver validate file <path>`` — single-file authoring-time validation.

Implements DR-137 §5.4 "validate file path handling (F-41)" + DEC-137-21
dotted-path diagnostic format. Output is single-line per diagnostic to
enable downstream parsing.

Exit codes (F-46):
- 0 — no error-severity diagnostics surfaced (warnings allowed unless
  ``--strict``).
- 1 — error-severity diagnostic surfaced.
- 2 — usage error: missing path, binary file, unreadable file.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Annotated, Any

import typer
import yaml

from spec_driver.presentation.cli import constants
from spec_driver.presentation.cli.validate import app
from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS
from supekku.scripts.lib.blocks.metadata.validator import (
  FIX_KIND_RENAME_KEY,
  FIX_KIND_REWRITE_VALUE,
  MetadataValidator,
  ValidationError,
)
from supekku.scripts.lib.core.config import (
  get_strict_map,
  load_workflow_config,
)
from supekku.scripts.lib.core.frontmatter_metadata import (
  FRONTMATTER_METADATA_REGISTRY,
)
from supekku.scripts.lib.core.repo import find_repo_root
from supekku.scripts.lib.core.spec_utils import (
  dump_markdown_file_update,
  load_markdown_file,
)

USAGE_ERROR_EXIT = 2

# Path-based kind inference. Keep narrow: only patterns that genuinely
# carry no ``kind:`` in legacy frontmatter benefit from inference. Other
# location-based inferences are deferred.
_PHASE_PATH_RE = re.compile(r"/phases/phase-\d{2}\.md$")


def _infer_kind_from_path(path: Path) -> str | None:
  if _PHASE_PATH_RE.search(str(path)):
    return "phase"
  return None


def _is_likely_binary(path: Path) -> bool:
  """Heuristic: a NUL byte in the first 8 KiB suggests binary content."""
  try:
    with path.open("rb") as fh:
      chunk = fh.read(8192)
  except OSError:
    return False
  return b"\x00" in chunk


def _parse_frontmatter(
  text: str,
) -> tuple[dict[str, Any] | None, list[str]]:
  """Return ``(frontmatter_dict_or_None, parse_errors)``.

  ``frontmatter_dict_or_None`` is ``None`` when no ``---`` block is
  present (no-frontmatter case). ``parse_errors`` is a list of
  pre-formatted diagnostic lines (``path:line:col: parse-error: …``)
  when YAML parsing fails; in that case the dict is also ``None``.
  """
  if not text.startswith("---\n") and not text.startswith("---\r\n"):
    return None, []

  # Locate closing fence
  lines = text.splitlines()
  closing = None
  for idx in range(1, len(lines)):
    if lines[idx].rstrip("\r") == "---":
      closing = idx
      break
  if closing is None:
    return None, ["parse-error: opening '---' not terminated"]

  yaml_text = "\n".join(lines[1:closing])
  try:
    parsed = yaml.safe_load(yaml_text)
  except yaml.YAMLError as exc:
    mark = getattr(exc, "problem_mark", None)
    if mark is not None:
      # mark.line/column are 0-based; YAML offsets are inside the
      # frontmatter region. Add +1 for the opening ``---`` line.
      line = mark.line + 1 + 1
      col = mark.column + 1
      msg = getattr(exc, "problem", str(exc)) or str(exc)
      return None, [f"{line}:{col}: parse-error: {msg}"]
    return None, [f"parse-error: {exc}"]

  if parsed is None:
    return {}, []
  if not isinstance(parsed, dict):
    return None, ["parse-error: frontmatter root must be a mapping"]
  return parsed, []


def _format_diagnostic(path: Path, error: ValidationError) -> str:
  """Format a single ValidationError per DEC-137-21 dotted-path shape."""
  severity = error.severity
  primary = f"{path}: {severity}: {error.path}: {error.message}"
  if error.expected:
    primary += f"  Allowed: {error.expected}"
  if error.actual and "got" not in error.message.lower():
    primary += f"  Got: {error.actual}"
  hint_line = ""
  if error.fix_kind == "rewrite_value" and error.fix_hint:
    hint_line = f"\n  Did you mean: {error.fix_hint}"
  elif error.fix_kind == "rename_key" and error.fix_hint:
    hint_line = "\n  Run `spec-driver validate workspace --fix` to canonicalise"
  return primary + hint_line


def _apply_fix(
  path: Path, errors: list[ValidationError]
) -> tuple[int, list[ValidationError]]:
  """Apply ``rename_key`` / ``rewrite_value`` fixes to *path*.

  Returns ``(applied_count, unapplied_errors)``. Unapplied errors are
  those whose ``fix_kind`` is not handled (or carries no ``fix_hint``);
  they remain in the diagnostic stream.
  """
  try:
    frontmatter, body = load_markdown_file(path)
  except (OSError, ValueError):
    return 0, errors

  applied = 0
  unapplied: list[ValidationError] = []
  for err in errors:
    if err.fix_hint is None or err.fix_kind is None:
      unapplied.append(err)
      continue
    # ``err.path`` for top-level fields is the field name; nested paths
    # carry dots / brackets. P03 fixes only top-level scalar rewrites.
    if "." in err.path or "[" in err.path:
      unapplied.append(err)
      continue
    if err.fix_kind == FIX_KIND_RENAME_KEY and err.path in frontmatter:
      frontmatter[err.fix_hint] = frontmatter.pop(err.path)
      applied += 1
      continue
    if err.fix_kind == FIX_KIND_REWRITE_VALUE and err.path in frontmatter:
      frontmatter[err.path] = err.fix_hint
      applied += 1
      continue
    unapplied.append(err)

  if applied > 0:
    dump_markdown_file_update(path, frontmatter, body)
  return applied, unapplied


@app.command(constants.VALIDATE_FILE)
def file_cmd(
  path: Annotated[
    Path,
    typer.Argument(
      help="Markdown file to validate (frontmatter + body)",
      exists=False,  # checked manually so we can emit the F-46 exit code
      file_okay=True,
      dir_okay=False,
      readable=False,
    ),
  ],
  strict: Annotated[
    bool,
    typer.Option(
      constants.FLAG_STRICT,
      help="Promote warnings to errors",
    ),
  ] = False,
  no_tolerated_aliases: Annotated[
    bool,
    typer.Option(
      constants.FLAG_NO_TOLERATED,
      help="Reject tolerated aliases",
    ),
  ] = False,
  fix: Annotated[
    bool,
    typer.Option(
      constants.FLAG_FIX,
      help="Apply rename_key / rewrite_value fixes via dump_markdown_file_update",
    ),
  ] = False,
) -> None:
  """Validate a single markdown artefact's frontmatter.

  Path handling:
  - Markdown with ``kind:`` in frontmatter ⇒ dispatch to that kind.
  - Markdown without ``kind:`` matching ``<delta>/phases/phase-NN.md``
    ⇒ inferred as ``phase`` and dispatched.
  - Markdown without ``---`` block ⇒ exit 0 with a no-op message.
  - Missing/unreadable/binary ⇒ exit 2.

  ``--fix`` applies ``rename_key`` / ``rewrite_value`` rewrites for
  diagnostics carrying ``fix_hint`` / ``fix_kind`` at top-level scalar
  paths (DEC-137-15 / F-1 update path). After rewrite, the validator
  re-runs to confirm the diagnostic was resolved (VT-CC-014).
  """
  if not path.exists():
    typer.echo(f"Error: path does not exist: {path}", err=True)
    raise typer.Exit(USAGE_ERROR_EXIT)
  if not path.is_file():
    typer.echo(f"Error: not a regular file: {path}", err=True)
    raise typer.Exit(USAGE_ERROR_EXIT)
  if _is_likely_binary(path):
    typer.echo(f"Error: binary file: {path}", err=True)
    raise typer.Exit(USAGE_ERROR_EXIT)

  try:
    text = path.read_text(encoding="utf-8")
  except (OSError, UnicodeDecodeError) as e:
    typer.echo(f"Error: cannot read {path}: {e}", err=True)
    raise typer.Exit(USAGE_ERROR_EXIT) from e

  frontmatter_data, parse_errors = _parse_frontmatter(text)

  if parse_errors:
    for err in parse_errors:
      typer.echo(f"{path}:{err}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  if frontmatter_data is None:
    typer.echo(f"validate file: {path}: no frontmatter — nothing to validate")
    raise typer.Exit(EXIT_SUCCESS)

  kind = frontmatter_data.get("kind") or _infer_kind_from_path(path)
  if not kind:
    typer.echo(
      f"validate file: {path}: no kind in frontmatter and path does not "
      "match a known inference pattern — nothing to validate"
    )
    raise typer.Exit(EXIT_SUCCESS)

  metadata = FRONTMATTER_METADATA_REGISTRY.get(kind)
  if metadata is None:
    typer.echo(
      f"Error: unknown kind '{kind}' in {path} (not in FRONTMATTER_METADATA_REGISTRY)",
      err=True,
    )
    raise typer.Exit(EXIT_FAILURE)

  # F-48: per-kind strict default from workflow.toml; CLI --strict overrides.
  try:
    repo_root = find_repo_root(path.parent)
    strict_map = get_strict_map(load_workflow_config(repo_root))
  except (OSError, ValueError):
    strict_map = {}
  effective_strict = strict or strict_map.get(kind, False)

  validator = MetadataValidator(metadata)
  errors = validator.validate(
    frontmatter_data,
    strict=effective_strict,
    accept_tolerated=not no_tolerated_aliases,
  )

  if fix and errors:
    applied, errors = _apply_fix(path, errors)
    if applied > 0:
      typer.echo(f"validate file: {path}: applied {applied} fix(es)")

  if not errors:
    typer.echo(f"validate file: {path}: clean")
    raise typer.Exit(EXIT_SUCCESS)

  has_error_severity = False
  for err in errors:
    if effective_strict and err.severity == "warning":
      err = ValidationError(  # noqa: PLW2901
        path=err.path,
        message=err.message,
        expected=err.expected,
        actual=err.actual,
        severity="error",
        fix_hint=err.fix_hint,
        fix_kind=err.fix_kind,
      )
    if err.severity == "error":
      has_error_severity = True
    typer.echo(_format_diagnostic(path, err), err=True)

  if has_error_severity:
    raise typer.Exit(EXIT_FAILURE)
  raise typer.Exit(EXIT_SUCCESS)
