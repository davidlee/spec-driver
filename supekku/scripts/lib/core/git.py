"""Legacy re-export shim — see spec_driver.core.git."""

from spec_driver.core.git import (
  DEFAULT_SHORT_SHA_LENGTH,
  SHA_HEX_PATTERN,
  get_branch,
  get_changed_files,
  get_head_sha,
  has_staged_changes,
  has_uncommitted_changes,
  short_sha,
)

__all__ = [
  "DEFAULT_SHORT_SHA_LENGTH",
  "SHA_HEX_PATTERN",
  "get_branch",
  "get_changed_files",
  "get_head_sha",
  "has_staged_changes",
  "has_uncommitted_changes",
  "short_sha",
]
