"""Legacy re-export shim — see spec_driver.core.artifact_ids."""

from spec_driver.core.artifact_ids import (
  NormalizationResult,
  classify_artifact_id,
  is_artifact_id,
  is_kind,
  normalize_artifact_id,
)

__all__ = [
  "NormalizationResult",
  "classify_artifact_id",
  "is_artifact_id",
  "is_kind",
  "normalize_artifact_id",
]
