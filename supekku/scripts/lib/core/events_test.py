"""Tests for CLI event emission infrastructure (DE-052).

VT-052-01 through VT-052-08 — verification tests for core/events.py
and the process-boundary wrapper in cli/main.py.
"""

from __future__ import annotations

import json
import os
import socket
import unittest
from pathlib import Path
from unittest.mock import patch

import click
import typer
from typer.testing import CliRunner

from supekku.scripts.lib.core import events

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_runner = CliRunner()


def _make_test_app() -> typer.Typer:
  """Create a minimal typer app with a group and a leaf command."""
  app = typer.Typer(name="test-cli", no_args_is_help=True)

  grp = typer.Typer(name="grp", no_args_is_help=True)

  @grp.command("leaf")
  def leaf_cmd() -> None:
    raise typer.Exit(0)

  @grp.command("fail")
  def fail_cmd() -> None:
    raise typer.Exit(1)

  @grp.command("crash")
  def crash_cmd() -> None:
    raise RuntimeError("boom")

  @grp.command("click-err")
  def click_err_cmd() -> None:
    raise click.ClickException("bad input")

  app.add_typer(grp, name="grp")
  return app


# ---------------------------------------------------------------------------
# VT-052-01: emit_event writes correct JSONL, appends, sends to socket
# ---------------------------------------------------------------------------


class TestEmitEventJsonl(unittest.TestCase):
  """VT-052-01: emit_event produces correct JSONL and appends to file."""

  def setUp(self) -> None:
    events._reset()

  def test_jsonl_fields(self, tmp_path: Path | None = None) -> None:
    """Event has all required fields with correct types."""
    if tmp_path is None:
      import tempfile  # noqa: PLC0415

      with tempfile.TemporaryDirectory() as td:
        self._run_jsonl_fields(Path(td))
    else:
      self._run_jsonl_fields(tmp_path)

  def _run_jsonl_fields(self, tmp_path: Path) -> None:
    run_dir = tmp_path / ".spec-driver" / "run"
    log_path = run_dir / "events.jsonl"

    with patch.object(events, "_get_run_dir", return_value=run_dir):
      events.emit_event(
        argv=["create", "delta", "--from-backlog", "IMPR-009"],
        exit_code=0,
        status="ok",
      )

    assert log_path.exists()
    record = json.loads(log_path.read_text().strip())

    assert record["v"] == 1
    assert isinstance(record["ts"], str)
    assert record["cmd"] == "create delta"
    assert record["argv"] == ["create", "delta", "--from-backlog", "IMPR-009"]
    assert record["artifacts"] == []
    assert record["exit_code"] == 0
    assert record["status"] == "ok"
    assert "session" in record

  def test_append_semantics(self) -> None:
    """Multiple emit_event calls append lines to the same file."""
    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as td:
      run_dir = Path(td) / ".spec-driver" / "run"
      with patch.object(events, "_get_run_dir", return_value=run_dir):
        events.emit_event(argv=["list", "specs"], exit_code=0, status="ok")
        events.emit_event(argv=["show", "spec", "SPEC-001"], exit_code=0, status="ok")

      lines = run_dir.joinpath("events.jsonl").read_text().strip().split("\n")
      assert len(lines) == 2
      assert json.loads(lines[0])["cmd"] == "list specs"
      assert json.loads(lines[1])["cmd"] == "show spec"

  def test_socket_send(self) -> None:
    """emit_event sends JSON datagram to socket when available."""
    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as td:
      run_dir = Path(td) / ".spec-driver" / "run"
      run_dir.mkdir(parents=True)
      sock_path = run_dir / "tui.sock"

      # Create a listening datagram socket
      srv = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
      try:
        srv.bind(str(sock_path))
        with patch.object(events, "_get_run_dir", return_value=run_dir):
          events.emit_event(argv=["sync"], exit_code=0, status="ok")

        data = srv.recv(4096)
        record = json.loads(data.decode())
        assert record["cmd"] == "sync"
        assert record["v"] == 1
      finally:
        srv.close()


# ---------------------------------------------------------------------------
# VT-052-02: Socket silent failure
# ---------------------------------------------------------------------------


class TestSocketSilentFailure(unittest.TestCase):
  """VT-052-02: Socket send silently fails when socket missing or path too long."""

  def setUp(self) -> None:
    events._reset()

  def test_missing_socket(self) -> None:
    """No error when socket file does not exist."""
    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as td:
      run_dir = Path(td) / ".spec-driver" / "run"
      with patch.object(events, "_get_run_dir", return_value=run_dir):
        events.emit_event(argv=["list", "specs"], exit_code=0, status="ok")
      # Should have written log but not crashed on socket
      assert run_dir.joinpath("events.jsonl").exists()

  def test_overlong_socket_path(self) -> None:
    """Socket send is skipped when path exceeds 104 chars."""
    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as td:
      # Create a deeply nested path that exceeds socket limit
      deep = Path(td) / ("x" * 80) / ("y" * 80) / ".spec-driver" / "run"
      with patch.object(events, "_get_run_dir", return_value=deep):
        # Should not raise
        events.emit_event(argv=["sync"], exit_code=0, status="ok")


# ---------------------------------------------------------------------------
# VT-052-03: Session detection
# ---------------------------------------------------------------------------


class TestSessionDetection(unittest.TestCase):
  """VT-052-03: _detect_session reads env vars correctly."""

  def test_spec_driver_session_env(self) -> None:
    """SPEC_DRIVER_SESSION takes priority."""
    with patch.dict(os.environ, {"SPEC_DRIVER_SESSION": "ses-abc123"}, clear=False):
      assert events._detect_session() == "ses-abc123"

  def test_claudecode_fallback(self) -> None:
    """CLAUDECODE=1 falls back to 'claude' when SPEC_DRIVER_SESSION unset."""
    env = {"CLAUDECODE": "1"}
    with patch.dict(os.environ, env, clear=False):
      # Ensure SPEC_DRIVER_SESSION is not set
      os.environ.pop("SPEC_DRIVER_SESSION", None)
      assert events._detect_session() == "claude"

  def test_no_env_returns_none(self) -> None:
    """Returns None when neither env var is set."""
    with patch.dict(os.environ, {}, clear=True):
      assert events._detect_session() is None


# ---------------------------------------------------------------------------
# VT-052-04: Config merge for [events] section
# ---------------------------------------------------------------------------


class TestEventsConfig(unittest.TestCase):
  """VT-052-04: [events] section in config merges correctly with defaults."""

  def test_default_events_enabled(self) -> None:
    """DEFAULT_CONFIG includes events.enabled = True."""
    from supekku.scripts.lib.core.config import DEFAULT_CONFIG  # noqa: PLC0415

    assert DEFAULT_CONFIG["events"]["enabled"] is True

  def test_user_override_disables(self) -> None:
    """User can set events.enabled = false in workflow.toml."""
    import tempfile  # noqa: PLC0415

    from supekku.scripts.lib.core.config import load_workflow_config  # noqa: PLC0415
    from supekku.scripts.lib.core.paths import SPEC_DRIVER_DIR  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as td:
      tmp_path = Path(td)
      toml_path = tmp_path / SPEC_DRIVER_DIR / "workflow.toml"
      toml_path.parent.mkdir(parents=True)
      toml_path.write_text(
        "[events]\nenabled = false\n",
        encoding="utf-8",
      )
      config = load_workflow_config(tmp_path)
      assert config["events"]["enabled"] is False

  def test_missing_events_section_uses_default(self) -> None:
    """Missing [events] section yields enabled=True."""
    import tempfile  # noqa: PLC0415

    from supekku.scripts.lib.core.config import load_workflow_config  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as td:
      config = load_workflow_config(Path(td))
      assert config["events"]["enabled"] is True


# ---------------------------------------------------------------------------
# VT-052-05: Process-boundary wrapper — all exit paths (NON-NEGOTIABLE)
# ---------------------------------------------------------------------------


class TestProcessBoundaryWrapper(unittest.TestCase):
  """VT-052-05: Wrapper emits correct events for all exit paths."""

  def setUp(self) -> None:
    events._reset()
    self._test_app = _make_test_app()
    self._original_invoke = click.Command.invoke

    original = self._original_invoke

    def _tracking_invoke(cmd_self, ctx):
      if not isinstance(cmd_self, click.Group):
        events.mark_command_invoked()
      return original(cmd_self, ctx)

    click.Command.invoke = _tracking_invoke

  def tearDown(self) -> None:
    click.Command.invoke = self._original_invoke
    events._reset()

  def _run_with_wrapper(self, args: list[str], run_dir: Path) -> dict | None:
    """Run the test app with the process-boundary wrapper pattern."""
    events._reset()
    with patch.object(events, "_get_run_dir", return_value=run_dir):
      result = _runner.invoke(self._test_app, args)
      # Simulate the main() wrapper behavior
      exit_code = result.exit_code
      if events.command_was_invoked():
        code = exit_code if isinstance(exit_code, int) else (1 if exit_code else 0)
        status = "ok" if code == 0 else "error"
        events.emit_event(argv=args, exit_code=code, status=status)

    log = run_dir / "events.jsonl"
    if log.exists():
      lines = log.read_text().strip().split("\n")
      return json.loads(lines[-1])
    return None

  def test_typer_exit_0(self) -> None:
    """typer.Exit(0) → status ok, exit_code 0."""
    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as td:
      run_dir = Path(td) / ".spec-driver" / "run"
      ev = self._run_with_wrapper(["grp", "leaf"], run_dir)
      assert ev is not None
      assert ev["exit_code"] == 0
      assert ev["status"] == "ok"

  def test_typer_exit_1(self) -> None:
    """typer.Exit(1) → status error, exit_code 1."""
    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as td:
      run_dir = Path(td) / ".spec-driver" / "run"
      ev = self._run_with_wrapper(["grp", "fail"], run_dir)
      assert ev is not None
      assert ev["exit_code"] == 1
      assert ev["status"] == "error"

  def test_click_exception(self) -> None:
    """ClickException → status error."""
    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as td:
      run_dir = Path(td) / ".spec-driver" / "run"
      ev = self._run_with_wrapper(["grp", "click-err"], run_dir)
      assert ev is not None
      assert ev["status"] == "error"
      assert ev["exit_code"] == 1

  def test_unhandled_exception(self) -> None:
    """Unhandled RuntimeError → status error."""
    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as td:
      run_dir = Path(td) / ".spec-driver" / "run"
      ev = self._run_with_wrapper(["grp", "crash"], run_dir)
      assert ev is not None
      assert ev["status"] == "error"
      assert ev["exit_code"] == 1


# ---------------------------------------------------------------------------
# VT-052-06: record_artifact + _drain_artifacts lifecycle
# ---------------------------------------------------------------------------


class TestArtifactCollector(unittest.TestCase):
  """VT-052-06: record_artifact populates artifacts field in emitted events."""

  def setUp(self) -> None:
    events._reset()

  def test_record_and_drain(self) -> None:
    """record_artifact appends; _drain_artifacts returns and clears."""
    events.record_artifact("DE-052")
    events.record_artifact("DR-052")
    drained = events._drain_artifacts()
    assert drained == ["DE-052", "DR-052"]
    # After drain, list is empty
    assert events._drain_artifacts() == []

  def test_artifacts_in_emitted_event(self) -> None:
    """Recorded artifacts appear in emitted event."""
    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as td:
      run_dir = Path(td) / ".spec-driver" / "run"
      events.record_artifact("SPEC-042")
      with patch.object(events, "_get_run_dir", return_value=run_dir):
        events.emit_event(argv=["create", "spec"], exit_code=0, status="ok")

      record = json.loads(
        run_dir.joinpath("events.jsonl").read_text().strip()
      )
      assert record["artifacts"] == ["SPEC-042"]
      # Artifacts drained after emit
      assert events._drain_artifacts() == []


# ---------------------------------------------------------------------------
# VT-052-07: No event for help/no-args/invalid (NON-NEGOTIABLE)
# ---------------------------------------------------------------------------


class TestNoEventForNonCommands(unittest.TestCase):
  """VT-052-07: No event emitted when _command_invoked flag is not set."""

  def setUp(self) -> None:
    events._reset()
    self._test_app = _make_test_app()
    self._original_invoke = click.Command.invoke

    original = self._original_invoke

    def _tracking_invoke(cmd_self, ctx):
      if not isinstance(cmd_self, click.Group):
        events.mark_command_invoked()
      return original(cmd_self, ctx)

    click.Command.invoke = _tracking_invoke

  def tearDown(self) -> None:
    click.Command.invoke = self._original_invoke
    events._reset()

  def _assert_no_event(self, args: list[str]) -> None:
    """Run the test app and assert no event is emitted."""
    events._reset()
    _runner.invoke(self._test_app, args)
    assert not events.command_was_invoked(), (
      f"command_was_invoked() should be False for args={args}"
    )

  def test_help_flag(self) -> None:
    """--help does not set the command_invoked flag."""
    self._assert_no_event(["--help"])

  def test_group_help(self) -> None:
    """Group --help does not set the flag."""
    self._assert_no_event(["grp", "--help"])

  def test_bare_program(self) -> None:
    """Bare program (no_args_is_help) does not set the flag."""
    self._assert_no_event([])

  def test_group_no_subcommand(self) -> None:
    """Group with no subcommand (no_args_is_help) does not set the flag."""
    self._assert_no_event(["grp"])

  def test_invalid_command(self) -> None:
    """Invalid command does not set the flag."""
    self._assert_no_event(["nonexistent"])


# ---------------------------------------------------------------------------
# VT-052-08: No workspace → no-op
# ---------------------------------------------------------------------------


class TestNoWorkspaceNoop(unittest.TestCase):
  """VT-052-08: emit_event is a no-op when no workspace/run dir resolves."""

  def setUp(self) -> None:
    events._reset()

  def test_no_workspace_no_error(self) -> None:
    """emit_event succeeds silently when _get_run_dir returns None."""
    with patch.object(events, "_get_run_dir", return_value=None):
      # Must not raise
      events.emit_event(argv=["list", "specs"], exit_code=0, status="ok")

  def test_no_workspace_no_file_created(self) -> None:
    """No events.jsonl created when workspace is absent."""
    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as td:
      ghost = Path(td) / "nonexistent" / ".spec-driver" / "run"
      with patch.object(events, "_get_run_dir", return_value=None):
        events.emit_event(argv=["sync"], exit_code=0, status="ok")
      assert not ghost.exists()


# ---------------------------------------------------------------------------
# _resolve_cmd helper
# ---------------------------------------------------------------------------


class TestResolveCmd(unittest.TestCase):
  """_resolve_cmd extracts command path from argv."""

  def test_simple_command(self) -> None:
    assert events._resolve_cmd(["sync"]) == "sync"

  def test_verb_noun(self) -> None:
    assert events._resolve_cmd(["create", "delta"]) == "create delta"

  def test_strips_flags(self) -> None:
    argv = ["create", "delta", "--from-backlog", "IMPR-009"]
    assert events._resolve_cmd(argv) == "create delta"

  def test_deep_command(self) -> None:
    assert events._resolve_cmd(["show", "spec", "SPEC-001"]) == "show spec"

  def test_empty_argv(self) -> None:
    assert events._resolve_cmd([]) == ""

  def test_three_tokens(self) -> None:
    """Three alpha tokens are all treated as command path."""
    assert events._resolve_cmd(["list", "specs", "all"]) == "list specs all"


if __name__ == "__main__":
  unittest.main()
