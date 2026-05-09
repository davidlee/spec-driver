"""Tests for BlockSchema and schema registry helpers."""

from __future__ import annotations

import unittest

from .metadata.schema import BlockMetadata, FieldMetadata
from .schema_registry import BlockSchema


def _stub_renderer(spec_id: str) -> str:
  """Trivial renderer for tests: returns the spec id."""
  return f"spec: {spec_id}"


class BlockSchemaRendererOptionalTest(unittest.TestCase):
  """BlockSchema accepts ``renderer=None`` for validate-only schemas (DEC-005)."""

  def test_default_renderer_is_none(self) -> None:
    """Renderer defaults to ``None``."""
    schema = BlockSchema(name="x", marker="m", version=1, description="d")
    assert schema.renderer is None

  def test_get_parameters_returns_empty_when_renderer_none(self) -> None:
    """``get_parameters()`` short-circuits to ``{}`` when renderer is None."""
    schema = BlockSchema(name="x", marker="m", version=1, description="d")
    assert schema.get_parameters() == {}

  def test_get_parameters_inspects_renderer_when_present(self) -> None:
    """When a renderer is supplied, ``get_parameters()`` inspects its signature."""
    schema = BlockSchema(
      name="x",
      marker="m",
      version=1,
      description="d",
      renderer=_stub_renderer,
    )
    params = schema.get_parameters()
    assert "spec_id" in params
    assert params["spec_id"]["required"] is True

  def test_metadata_only_schema_constructs(self) -> None:
    """A validate-only schema (metadata supplied, renderer None) constructs."""
    metadata = BlockMetadata(
      version=1,
      schema_id="x.example",
      fields={"name": FieldMetadata(type="string", required=True)},
    )
    schema = BlockSchema(
      name="x.example",
      marker="supekku:x.example@v1",
      version=1,
      description="d",
      metadata=metadata,
    )
    assert schema.renderer is None
    assert schema.metadata is metadata


if __name__ == "__main__":
  unittest.main()
