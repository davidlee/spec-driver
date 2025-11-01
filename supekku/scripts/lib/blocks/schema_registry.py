"""Central registry of block schemas for documentation and tooling."""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class BlockSchema:
  """Schema information for a YAML block type."""

  name: str  # e.g., "delta.relationships"
  marker: str  # e.g., "supekku:delta.relationships@v1"
  version: int  # e.g., 1
  renderer: Callable[..., str]  # The rendering function
  description: str  # Human-readable description

  def get_parameters(self) -> dict[str, Any]:
    """Extract parameters from renderer function signature.

    Returns:
      Dictionary mapping parameter names to their metadata:
        - 'required': bool - whether parameter is required
        - 'type': type annotation or 'Any'
        - 'default': default value or None
    """
    sig = inspect.signature(self.renderer)
    params = {}
    for name, param in sig.parameters.items():
      if name == "self":
        continue
      params[name] = {
        "required": param.default == inspect.Parameter.empty
        and param.kind != inspect.Parameter.VAR_KEYWORD
        and param.kind != inspect.Parameter.VAR_POSITIONAL,
        "type": (
          param.annotation
          if param.annotation != inspect.Parameter.empty
          else "Any"
        ),
        "default": (
          param.default if param.default != inspect.Parameter.empty else None
        ),
      }
    return params


# Registry mapping block type -> schema
BLOCK_SCHEMAS: dict[str, BlockSchema] = {}


def register_block_schema(block_type: str, schema: BlockSchema) -> None:
  """Register a block schema.

  Args:
    block_type: Block type identifier (e.g., "delta.relationships")
    schema: BlockSchema instance to register
  """
  BLOCK_SCHEMAS[block_type] = schema


def get_block_schema(block_type: str) -> BlockSchema | None:
  """Get schema for block type.

  Args:
    block_type: Block type identifier

  Returns:
    BlockSchema instance or None if not found
  """
  return BLOCK_SCHEMAS.get(block_type)


def list_block_types() -> list[str]:
  """List all registered block types.

  Returns:
    Sorted list of block type identifiers
  """
  return sorted(BLOCK_SCHEMAS.keys())


__all__ = [
  "BLOCK_SCHEMAS",
  "BlockSchema",
  "get_block_schema",
  "list_block_types",
  "register_block_schema",
]
