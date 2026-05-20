"""``spec-driver admin migrate`` orchestrator.

Discovers migration steps under ``spec_driver/migrations/``, dispatches
them in (version, ordinal) order, and advances the
``[migrations] last_applied`` watermark in ``workflow.toml`` after each
step's full pass completes. DE-137 ships zero steps; DE-138..142
populate the inventory.

Lockfile semantics: ``MIGRATION_LOCK_PATH`` (PID + ISO timestamp +
UUID). POSIX path probes liveness via ``os.kill(pid, 0)`` — stale
locks (dead PID) are overwritten with an info message; live locks
fail-fast. Windows path conservatively treats any existing lock as
held (per DR-137 §9.3).
"""

from __future__ import annotations

import importlib
import importlib.util
import os
import sys
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import tomlkit
import typer

from spec_driver.migrations._folder import (
  ParsedFolder,
  parse_migration_folder,
)
from spec_driver.migrations._protocol import MigrationStep, StepPreview, StepResult
from spec_driver.presentation.cli import constants

# Path to the directory holding migration step packages. Resolved at
# call time so tests can monkey-patch via ``importlib.import_module``.
_MIGRATIONS_PACKAGE = "spec_driver.migrations"


@dataclass(frozen=True)
class _LoadedStep:
  """Discovery result: parsed folder + imported step instance."""

  folder: ParsedFolder
  step: MigrationStep


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def _migrations_dir() -> Path:
  """Return the on-disk path to ``spec_driver/migrations/``."""
  pkg = importlib.import_module(_MIGRATIONS_PACKAGE)
  pkg_path = getattr(pkg, "__path__", None)
  if not pkg_path:
    raise RuntimeError(f"{_MIGRATIONS_PACKAGE} has no __path__")
  return Path(pkg_path[0])


def _registered_kinds() -> set[str]:
  """Snapshot of registered artefact kinds (deferred import)."""
  from supekku.scripts.lib.core.frontmatter_metadata import (  # noqa: PLC0415
    FRONTMATTER_METADATA_REGISTRY,
  )

  return set(FRONTMATTER_METADATA_REGISTRY.keys())


def _discover_steps(migrations_dir: Path | None = None) -> list[_LoadedStep]:
  """Walk migration folders; import each step; return sorted by (version, ordinal).

  Non-parsing folder names are skipped silently. Folders without an
  importable ``step: MigrationStep`` instance raise — that is a step-
  author bug, surfaced loudly at discovery.
  """
  base = migrations_dir or _migrations_dir()
  loaded: list[_LoadedStep] = []
  for child in sorted(base.iterdir()) if base.exists() else []:
    if not child.is_dir():
      continue
    parsed = parse_migration_folder(child.name)
    if parsed is None:
      continue
    module = _import_step_module(child, parsed.name)
    step = getattr(module, "step", None)
    if step is None or not isinstance(step, MigrationStep):
      raise RuntimeError(
        f"admin migrate: step folder {parsed.name} does not export a "
        f"top-level `step: MigrationStep` instance"
      )
    loaded.append(_LoadedStep(folder=parsed, step=step))
  loaded.sort(key=lambda ls: (ls.folder.version, ls.folder.ordinal))
  return loaded


def _import_step_module(folder: Path, folder_name: str):
  """Import ``<folder>/migration.py`` as an attribute-addressable module.

  Always file-based via ``importlib.util.spec_from_file_location`` so
  the orchestrator works uniformly for production steps and tmp_path
  fixtures. Single-process invocation makes the import-cache benefit
  marginal.
  """
  migration_file = folder / "migration.py"
  if not migration_file.exists():
    raise RuntimeError(
      f"admin migrate: step folder {folder_name} is missing migration.py"
    )
  spec = importlib.util.spec_from_file_location(
    f"_sd_migration.{folder_name}", migration_file
  )
  if spec is None or spec.loader is None:
    raise RuntimeError(f"admin migrate: could not load step at {migration_file}")
  module = importlib.util.module_from_spec(spec)
  # Register before exec so dataclass annotation resolution can find the
  # module via ``sys.modules[cls.__module__]`` (Python 3.13 requirement when
  # a step defines its own ``@dataclass`` types under ``from __future__ import
  # annotations``).
  sys.modules[spec.name] = module
  spec.loader.exec_module(module)
  return module


def _validate_step_kinds(loaded: list[_LoadedStep]) -> None:
  """F-26 / VT-CC-031: fail-fast on unregistered ``applies_to_kind``.

  Raises ``typer.Exit(EXIT_FAILURE)`` with the verbatim DR-137 §5.6
  diagnostic on mismatch. No step runs.
  """
  from supekku.cli.common import EXIT_FAILURE  # noqa: PLC0415 — break import cycle

  known = _registered_kinds()
  for entry in loaded:
    kind = entry.step.applies_to_kind
    if kind in known:
      continue
    registered_list = ", ".join(sorted(known))
    typer.echo(
      f"admin migrate: migration step {entry.folder.name} declares\n"
      f"applies_to_kind={kind!r} which is not a registered kind.\n"
      f"Registered kinds: {registered_list}.",
      err=True,
    )
    raise typer.Exit(EXIT_FAILURE)


# ---------------------------------------------------------------------------
# Watermark
# ---------------------------------------------------------------------------


def _read_last_applied(repo_root: Path) -> str | None:
  from supekku.scripts.lib.core.config import (  # noqa: PLC0415
    load_workflow_config,
  )

  config = load_workflow_config(repo_root)
  value = config.get("migrations", {}).get("last_applied")
  if value in (None, ""):
    return None
  return str(value)


def _advance_watermark(repo_root: Path, step_name: str) -> None:
  """Set ``[migrations] last_applied`` atomically (tomlkit + tempfile)."""
  from spec_driver.migrations._helpers import atomic_write  # noqa: PLC0415

  workflow_toml = repo_root / ".spec-driver" / "workflow.toml"
  if workflow_toml.exists():
    doc = tomlkit.parse(workflow_toml.read_text(encoding="utf-8"))
  else:
    doc = tomlkit.document()
  if "migrations" not in doc:
    doc["migrations"] = tomlkit.table()
  doc["migrations"]["last_applied"] = step_name
  atomic_write(workflow_toml, tomlkit.dumps(doc))


def _pending_steps(
  loaded: list[_LoadedStep], last_applied: str | None
) -> list[_LoadedStep]:
  """Return steps whose name is strictly after ``last_applied``."""
  if last_applied is None or last_applied == "":
    return list(loaded)
  out: list[_LoadedStep] = []
  cleared = False
  for entry in loaded:
    if cleared:
      out.append(entry)
      continue
    if entry.folder.name == last_applied:
      cleared = True
  return out


# ---------------------------------------------------------------------------
# Lockfile (F-21 / F-36 / DEC-137-22 / VT-CC-029)
# ---------------------------------------------------------------------------


class _LockHeldError(RuntimeError):
  """Raised when an existing live lock prevents migration."""


def _lockfile_path(repo_root: Path) -> Path:
  return repo_root / constants.MIGRATION_LOCK_PATH


def _pid_alive(pid: int) -> bool:
  """POSIX liveness probe via ``os.kill(pid, 0)``.

  ESRCH ⇒ dead; EPERM ⇒ alive (different user); 0 ⇒ alive.
  Windows callers should short-circuit before reaching here.
  """
  try:
    os.kill(pid, 0)
  except ProcessLookupError:
    return False
  except PermissionError:
    return True
  return True


def _acquire_lock(repo_root: Path) -> Path:
  """Acquire the migration lockfile; raise ``_LockHeldError`` if active.

  POSIX: parse existing PID; if alive ⇒ raise; if dead ⇒ overwrite
  (info message). Windows: treat any existing lock as held.
  """
  lock_path = _lockfile_path(repo_root)
  lock_path.parent.mkdir(parents=True, exist_ok=True)

  if lock_path.exists():
    content = lock_path.read_text(encoding="utf-8").strip().splitlines()
    pid_str = content[0] if content else ""
    started_at = content[1] if len(content) > 1 else "<unknown>"
    uuid_str = content[2] if len(content) > 2 else "<unknown>"
    try:
      held_pid = int(pid_str)
    except ValueError:
      held_pid = -1

    if sys.platform == "win32" or _pid_alive(held_pid):
      raise _LockHeldError(
        f"migrate: concurrent invocation detected "
        f"(lock held by PID {held_pid}; started {started_at}; "
        f"uuid {uuid_str}); aborting"
      )
    typer.echo(
      f"migrate: stale lockfile from dead PID {held_pid}; overwriting",
      err=True,
    )

  lock_path.write_text(
    f"{os.getpid()}\n{datetime.now(tz=UTC).isoformat()}\n{uuid.uuid4()}\n",
    encoding="utf-8",
  )
  return lock_path


def _release_lock(lock_path: Path) -> None:
  if lock_path.exists():
    lock_path.unlink()


# ---------------------------------------------------------------------------
# Per-run log
# ---------------------------------------------------------------------------


def _write_log(repo_root: Path, step: _LoadedStep, results: list[StepResult]) -> Path:
  timestamp = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")
  log_path = repo_root / constants.MIGRATION_LOG_PATH.format(
    timestamp=timestamp, step=step.folder.name
  )
  log_path.parent.mkdir(parents=True, exist_ok=True)
  lines = [
    f"# Migration run — {step.folder.name}",
    "",
    f"- step: {step.folder.name}",
    f"- kind: {step.step.applies_to_kind}",
    f"- description: {step.step.description}",
    "",
    "## Results",
    "",
  ]
  for res in results:
    for path in res.touched:
      lines.append(f"- touched: {path}")
    for path in res.skipped:
      lines.append(f"- skipped: {path}")
  log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
  return log_path


# ---------------------------------------------------------------------------
# Sweep
# ---------------------------------------------------------------------------


def _kind_files(repo_root: Path, kind: str) -> list[Path]:
  """Yield candidate markdown files for *kind* by frontmatter scan.

  Recursive walk through ``.spec-driver/`` filtering on the ``kind:``
  field. Avoids loading the full Workspace registry — keeps the
  orchestrator independent of upstream registries (POL-003).
  """
  sd_root = repo_root / ".spec-driver"
  if not sd_root.exists():
    return []
  candidates: list[Path] = []
  for path in sorted(sd_root.rglob("*.md")):
    try:
      head = path.read_text(encoding="utf-8", errors="replace").splitlines()[:25]
    except OSError:
      continue
    if not head or head[0].strip() != "---":
      continue
    for line in head[1:]:
      stripped = line.strip()
      if stripped == "---":
        break
      if stripped.startswith("kind:"):
        value = stripped.split(":", 1)[1].strip().strip("'\"")
        if value == kind:
          candidates.append(path)
        break
  return candidates


def _run_step(
  repo_root: Path,
  entry: _LoadedStep,
  *,
  dry_run: bool,
) -> tuple[list[StepResult], list[StepPreview]]:
  """Dispatch one step across its kind's candidate files.

  Returns ``(applied_results, previewed)``. Atomicity: the orchestrator
  advances the watermark only after this function returns without
  raising (per-step responsibility for per-file idempotency, F-34).
  """
  results: list[StepResult] = []
  previews: list[StepPreview] = []
  for path in _kind_files(repo_root, entry.step.applies_to_kind):
    if not entry.step.applies_to(path):
      continue
    preview = entry.step.preview(path)
    previews.append(preview)
    if dry_run:
      continue
    result = entry.step.apply(path)
    results.append(result)
  return results, previews


# ---------------------------------------------------------------------------
# Typer entry
# ---------------------------------------------------------------------------


def migrate(
  kind: Annotated[
    str | None,
    typer.Argument(
      help="Artefact kind to sweep, or 'all'. Omit when using --check/--list.",
    ),
  ] = None,
  root: Annotated[
    Path | None,
    typer.Option(
      "--root",
      help="Repository root (auto-detected if omitted)",
      file_okay=False,
      dir_okay=True,
      exists=True,
    ),
  ] = None,
  check: Annotated[
    bool,
    typer.Option(
      constants.FLAG_CHECK,
      help="Preview pending migrations (no writes).",
    ),
  ] = False,
  list_: Annotated[
    bool,
    typer.Option(
      constants.FLAG_LIST,
      help="Show pending + applied migrations.",
    ),
  ] = False,
  dry_run: Annotated[
    bool,
    typer.Option(
      constants.FLAG_DRY_RUN,
      help="Preview the diff for the selected kind; no writes.",
    ),
  ] = False,
  strict: Annotated[
    bool,
    typer.Option(
      constants.FLAG_STRICT,
      help="Flip [validation.strict] <kind> = true after the sweep passes.",
    ),
  ] = False,
) -> None:
  """Run the migration orchestrator. See DR-137 §5.6 for the full contract."""
  from supekku.cli.common import (  # noqa: PLC0415 — break import cycle
    EXIT_FAILURE,
    EXIT_PRECONDITION,
    EXIT_SUCCESS,
  )
  from supekku.scripts.lib.core.repo import find_repo_root  # noqa: PLC0415

  if check and list_:
    typer.echo("admin migrate: --check and --list are mutually exclusive", err=True)
    raise typer.Exit(EXIT_PRECONDITION)

  repo_root = find_repo_root(root)
  loaded = _discover_steps()
  _validate_step_kinds(loaded)
  last_applied = _read_last_applied(repo_root)
  pending = _pending_steps(loaded, last_applied)

  if list_:
    _emit_list(loaded, last_applied)
    raise typer.Exit(EXIT_SUCCESS)

  if check:
    _emit_check(pending)
    raise typer.Exit(EXIT_SUCCESS)

  if kind is None:
    typer.echo(
      "admin migrate: positional <kind> required unless --check or --list",
      err=True,
    )
    raise typer.Exit(EXIT_PRECONDITION)

  selected = _select_pending(pending, kind)
  if not selected:
    typer.echo(f"admin migrate: nothing to do for kind={kind!r}")
    raise typer.Exit(EXIT_SUCCESS)

  try:
    lock_path = _acquire_lock(repo_root)
  except _LockHeldError as exc:
    typer.echo(str(exc), err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  try:
    for entry in selected:
      results, _ = _run_step(repo_root, entry, dry_run=dry_run)
      if dry_run:
        typer.echo(
          f"admin migrate: {entry.folder.name}: dry-run "
          f"(would touch {sum(len(r.touched) for r in results)})"
        )
        continue
      _write_log(repo_root, entry, results)
      _advance_watermark(repo_root, entry.folder.name)
      typer.echo(f"admin migrate: {entry.folder.name}: applied")
    if strict and kind != "all" and not dry_run:
      _flip_strict(repo_root, kind)
      typer.echo(f"admin migrate: [validation.strict] {kind} = true")
  finally:
    _release_lock(lock_path)


def _select_pending(pending: list[_LoadedStep], kind: str) -> list[_LoadedStep]:
  if kind == "all":
    return pending
  return [p for p in pending if p.step.applies_to_kind == kind]


def _emit_list(loaded: list[_LoadedStep], last_applied: str | None) -> None:
  if not loaded:
    typer.echo("admin migrate: no migration steps registered.")
    return
  typer.echo("admin migrate: registered steps:")
  for entry in loaded:
    state = (
      "applied"
      if (
        last_applied is not None
        and (
          entry.folder.name == last_applied
          or _name_is_before_or_at(entry.folder.name, loaded, last_applied)
        )
      )
      else "pending"
    )
    typer.echo(f"  - {entry.folder.name} [{state}] kind={entry.step.applies_to_kind}")


def _name_is_before_or_at(
  candidate: str, loaded: list[_LoadedStep], watermark: str
) -> bool:
  for entry in loaded:
    if entry.folder.name == candidate:
      return False
    if entry.folder.name == watermark:
      return True
  return False


def _emit_check(pending: list[_LoadedStep]) -> None:
  if not pending:
    typer.echo("admin migrate: no pending migrations.")
    return
  typer.echo("admin migrate: pending migrations:")
  for entry in pending:
    typer.echo(
      f"  - {entry.folder.name} kind={entry.step.applies_to_kind} "
      f"description={entry.step.description!r}"
    )


def _flip_strict(repo_root: Path, kind: str) -> None:
  """Set ``[validation.strict] <kind> = true`` atomically."""
  from spec_driver.migrations._helpers import atomic_write  # noqa: PLC0415

  workflow_toml = repo_root / ".spec-driver" / "workflow.toml"
  if workflow_toml.exists():
    doc = tomlkit.parse(workflow_toml.read_text(encoding="utf-8"))
  else:
    doc = tomlkit.document()
  if "validation" not in doc:
    doc["validation"] = tomlkit.table()
  validation_table = doc["validation"]
  if "strict" not in validation_table:
    validation_table["strict"] = tomlkit.table()
  validation_table["strict"][kind] = True
  atomic_write(workflow_toml, tomlkit.dumps(doc))
