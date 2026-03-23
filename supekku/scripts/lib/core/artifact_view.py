"""Re-export shim — canonical location is spec_driver.orchestration.artifact_view."""

# ruff: noqa: F401
from spec_driver.orchestration.artifact_view import (
  _ID_ATTR,
  _REGISTRY_FACTORIES,
  _STATUS_ATTR,
  _TITLE_ATTR,
  ARTIFACT_TYPE_META,
  ArtifactEntry,
  ArtifactGroup,
  ArtifactSnapshot,
  ArtifactType,
  ArtifactTypeMeta,
  _collect_safe,
  _detect_bundle_dir,
  adapt_record,
  path_to_artifact_type,
)

__all__ = [
  "_ID_ATTR",
  "_REGISTRY_FACTORIES",
  "_STATUS_ATTR",
  "_TITLE_ATTR",
  "_collect_safe",
  "_detect_bundle_dir",
  "ARTIFACT_TYPE_META",
  "ArtifactEntry",
  "ArtifactGroup",
  "ArtifactSnapshot",
  "ArtifactType",
  "ArtifactTypeMeta",
  "adapt_record",
  "path_to_artifact_type",
]
