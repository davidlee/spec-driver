"""Legacy re-export shim — see spec_driver.core.events."""

from spec_driver.core.events import (  # noqa: F401
  LOG_FILENAME,
  MAX_SOCKET_PATH_LEN,
  SOCKET_FILENAME,
  command_was_invoked,
  emit_event,
  mark_command_invoked,
  record_artifact,
)

__all__ = [
  "LOG_FILENAME",
  "MAX_SOCKET_PATH_LEN",
  "SOCKET_FILENAME",
  "command_was_invoked",
  "emit_event",
  "mark_command_invoked",
  "record_artifact",
]
