"""Tests for artifact_event.py hook script (DE-060).

VT-060-01: Path classification correctness
VT-060-02: Non-artifact paths silently ignored
VT-060-03: Event schema correctness
"""

from __future__ import annotations

import importlib.util
import io
import json
import socket
from pathlib import Path
from unittest.mock import patch

import pytest

# Load module by file path (directory name contains a dot, not importable normally)
_MODULE_PATH = Path(__file__).parent / "artifact_event.py"
_spec = importlib.util.spec_from_file_location("artifact_event", _MODULE_PATH)
assert _spec and _spec.loader
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

classify_path = _mod.classify_path
build_event = _mod.build_event
main = _mod.main
write_log = _mod.write_log
send_socket = _mod.send_socket


# --- VT-060-01: Path classification ---


class TestClassifyPath:
  """classify_path correctly identifies spec-driver artifact types."""

  @pytest.mark.parametrize(
    "path, expected_type, expected_id",
    [
      # Deltas
      (
        "/proj/.spec-driver/deltas/DE-060-slug/DE-060.md",
        "delta",
        "DE-060",
      ),
      (
        ".spec-driver/deltas/DE-001-foo/notes.md",
        "delta",
        "DE-001",
      ),
      # Design revisions
      (
        "/proj/.spec-driver/deltas/DE-060-slug/DR-060.md",
        "design_revision",
        "DE-060",
      ),
      # Implementation plans
      (
        "/proj/.spec-driver/deltas/DE-060-slug/IP-060.md",
        "plan",
        "DE-060",
      ),
      # Phase sheets
      (
        "/proj/.spec-driver/deltas/DE-060-slug/phases/phase-01.md",
        "phase",
        "DE-060",
      ),
      # Specs
      (
        "/proj/.spec-driver/tech/SPEC-042/SPEC-042.md",
        "spec",
        "SPEC-042",
      ),
      # ADRs
      (
        "/proj/.spec-driver/decisions/ADR-007-some-decision.md",
        "adr",
        "ADR-007",
      ),
      # Revisions
      (
        "/proj/.spec-driver/revisions/RE-003.md",
        "revision",
        "RE-003",
      ),
      # Audits
      (
        "/proj/.spec-driver/audits/AUD-001.md",
        "audit",
        "AUD-001",
      ),
      # Backlog (no specific ID)
      (
        "/proj/.spec-driver/backlog/issues/ISSUE-042.md",
        "backlog",
        None,
      ),
      # Product specs
      (
        "/proj/.spec-driver/product/PROD-001/PROD-001.md",
        "product_spec",
        "PROD-001",
      ),
      # Policies
      (
        "/proj/.spec-driver/policies/POL-001.md",
        "policy",
        "POL-001",
      ),
      # Standards
      (
        "/proj/.spec-driver/standards/STD-002.md",
        "standard",
        "STD-002",
      ),
    ],
  )
  def test_classifies_artifact(
    self, path: str, expected_type: str, expected_id: str | None
  ) -> None:
    result = classify_path(path)
    assert result is not None
    artifact_type, artifact_id = result
    assert artifact_type == expected_type
    assert artifact_id == expected_id

  def test_phase_before_generic_delta(self) -> None:
    """Phase sheets match the phase pattern, not the generic delta pattern."""
    result = classify_path("/proj/.spec-driver/deltas/DE-060-slug/phases/phase-01.md")
    assert result is not None
    assert result[0] == "phase"

  def test_dr_before_generic_delta(self) -> None:
    """DR files match the design_revision pattern, not the generic delta."""
    result = classify_path("/proj/.spec-driver/deltas/DE-060-slug/DR-060.md")
    assert result is not None
    assert result[0] == "design_revision"


# --- VT-060-02: Non-artifact paths ignored ---


class TestNonArtifactPaths:
  """Non-spec-driver paths return None."""

  @pytest.mark.parametrize(
    "path",
    [
      "/proj/supekku/cli/app.py",
      "/proj/README.md",
      "/proj/pyproject.toml",
      "/proj/supekku/tui/track.py",
      "/proj/.claude/settings.json",
      "/proj/tests/test_something.py",
      "",
    ],
  )
  def test_non_artifact_returns_none(self, path: str) -> None:
    assert classify_path(path) is None


# --- VT-060-03: Event schema correctness ---


class TestBuildEvent:
  """build_event produces a valid v1 event dict."""

  def test_event_schema(self) -> None:
    event = build_event(
      session_id="sess-123",
      tool_name="Edit",
      file_path="/proj/.spec-driver/deltas/DE-060-slug/DE-060.md",
      artifact_type="delta",
      artifact_id="DE-060",
    )
    assert event["v"] == 1
    assert event["session"] == "sess-123"
    assert event["cmd"] == "artifact.edit"
    assert event["artifacts"] == ["DE-060"]
    assert event["exit_code"] == 0
    assert event["status"] == "ok"
    assert event["artifact_type"] == "delta"
    assert "ts" in event
    assert isinstance(event["argv"], list)
    assert len(event["argv"]) == 2
    assert event["argv"][0] == "artifact.edit"

  def test_read_action(self) -> None:
    event = build_event(
      session_id=None,
      tool_name="Read",
      file_path="/proj/.spec-driver/tech/SPEC-042/SPEC-042.md",
      artifact_type="spec",
      artifact_id="SPEC-042",
    )
    assert event["cmd"] == "artifact.read"
    assert event["session"] is None

  def test_write_action(self) -> None:
    event = build_event(
      session_id="s1",
      tool_name="Write",
      file_path="/proj/.spec-driver/decisions/ADR-007.md",
      artifact_type="adr",
      artifact_id="ADR-007",
    )
    assert event["cmd"] == "artifact.write"

  def test_no_artifact_id(self) -> None:
    event = build_event(
      session_id="s1",
      tool_name="Read",
      file_path="/proj/.spec-driver/backlog/issues/ISSUE-042.md",
      artifact_type="backlog",
      artifact_id=None,
    )
    assert event["artifacts"] == []

  def test_cwd_used_for_relativization(self) -> None:
    """build_event uses explicit cwd instead of Path.cwd() (DEC-061-04)."""
    event = build_event(
      session_id="s1",
      tool_name="Read",
      file_path="/proj/.spec-driver/deltas/DE-061-slug/DE-061.md",
      artifact_type="delta",
      artifact_id="DE-061",
      cwd="/proj",
    )
    assert event["argv"][1] == ".spec-driver/deltas/DE-061-slug/DE-061.md"

  def test_cwd_none_falls_back_to_process_cwd(self) -> None:
    """build_event without cwd still works (backward-compatible)."""
    event = build_event(
      session_id="s1",
      tool_name="Read",
      file_path="/unlikely/path/.spec-driver/deltas/DE-001/DE-001.md",
      artifact_type="delta",
      artifact_id="DE-001",
      cwd=None,
    )
    # Path can't be made relative to actual cwd, so stays absolute
    assert "DE-001.md" in event["argv"][1]


class TestWriteLog:
  """write_log appends JSONL to the log file."""

  def test_appends_jsonl(self, tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    event = {"v": 1, "cmd": "artifact.read", "ts": "now"}

    write_log(event, run_dir)
    write_log(event, run_dir)

    log_path = run_dir / "events.jsonl"
    assert log_path.exists()
    lines = log_path.read_text().strip().split("\n")
    assert len(lines) == 2
    for line in lines:
      parsed = json.loads(line)
      assert parsed["v"] == 1

  def test_creates_run_dir(self, tmp_path: Path) -> None:
    run_dir = tmp_path / "deep" / "nested" / "run"
    event = {"v": 1}

    write_log(event, run_dir)

    assert run_dir.exists()
    assert (run_dir / "events.jsonl").exists()


class TestSendSocket:
  """send_socket sends a datagram to the Unix socket."""

  def test_sends_datagram(self, tmp_path: Path) -> None:
    sock_path = tmp_path / "tui.sock"
    server = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    server.bind(str(sock_path))
    try:
      event = {"v": 1, "cmd": "artifact.read"}
      send_socket(event, tmp_path)

      server.settimeout(1.0)
      data = server.recv(4096)
      parsed = json.loads(data)
      assert parsed["cmd"] == "artifact.read"
    finally:
      server.close()

  def test_raises_on_missing_socket(self, tmp_path: Path) -> None:
    """send_socket raises when socket doesn't exist (caller suppresses)."""
    event = {"v": 1}
    with pytest.raises(FileNotFoundError):
      send_socket(event, tmp_path)


class TestMain:
  """Integration: main() reads stdin JSON and emits events."""

  def _run_main(self, hook_input: dict, cwd: str) -> Path:
    """Run main() with mocked stdin, return run_dir."""
    hook_input.setdefault("cwd", cwd)
    stdin_data = json.dumps(hook_input)

    with patch("sys.stdin", io.StringIO(stdin_data)):
      main()

    return Path(cwd) / ".spec-driver" / "run"

  def test_artifact_emits_event(self, tmp_path: Path) -> None:
    hook_input = {
      "session_id": "test-sess",
      "tool_name": "Edit",
      "tool_input": {
        "file_path": f"{tmp_path}/.spec-driver/deltas/DE-060-slug/DE-060.md",
      },
      "tool_response": {"success": True},
    }

    run_dir = self._run_main(hook_input, str(tmp_path))

    log_path = run_dir / "events.jsonl"
    assert log_path.exists()
    event = json.loads(log_path.read_text().strip())
    assert event["cmd"] == "artifact.edit"
    assert event["artifacts"] == ["DE-060"]
    assert event["session"] == "test-sess"
    assert event["artifact_type"] == "delta"

  def test_non_artifact_no_event(self, tmp_path: Path) -> None:
    hook_input = {
      "session_id": "test-sess",
      "tool_name": "Read",
      "tool_input": {
        "file_path": f"{tmp_path}/supekku/cli/app.py",
      },
      "tool_response": {},
    }

    run_dir = self._run_main(hook_input, str(tmp_path))

    log_path = run_dir / "events.jsonl"
    assert not log_path.exists()

  def test_missing_file_path_no_event(self, tmp_path: Path) -> None:
    hook_input = {
      "session_id": "test-sess",
      "tool_name": "Bash",
      "tool_input": {"command": "ls"},
      "tool_response": {},
    }

    run_dir = self._run_main(hook_input, str(tmp_path))

    log_path = run_dir / "events.jsonl"
    assert not log_path.exists()
