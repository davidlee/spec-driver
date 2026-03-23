"""Re-export shim — canonical location is spec_driver.domain.relations.manager."""

# ruff: noqa: F401
from spec_driver.domain.relations.manager import (
  add_relation,
  list_relations,
  remove_relation,
)

__all__ = [
  "add_relation",
  "list_relations",
  "remove_relation",
]
