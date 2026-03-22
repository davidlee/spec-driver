---
id: mem.gotcha.pydantic.migration
name: Pydantic BaseModel migration gotchas
kind: memory
status: active
memory_type: fact
created: '2026-03-22'
updated: '2026-03-22'
verified: '2026-03-22'
confidence: high
tags:
- pydantic
- migration
- models
summary: 'Three gotchas when converting @dataclass to Pydantic BaseModel'
scope:
  globs:
    - "supekku/scripts/lib/*/models.py"
provenance:
  sources:
    - kind: delta
      ref: DE-107
---

# Pydantic BaseModel migration gotchas

## Summary

Three gotchas discovered during DE-107 @dataclass → Pydantic BaseModel migration. Apply to all future model conversions (DE-111, etc).

## Gotchas

1. **TYPE_CHECKING guard on Path breaks Pydantic.** If `Path` is imported inside `if TYPE_CHECKING:`, Pydantic cannot resolve the type at runtime even with `from __future__ import annotations`. Move `Path` imports to unconditional imports for any model that uses `Path` as a field type.

2. **Frozen models raise ValidationError, not AttributeError.** `@dataclass(frozen=True)` raises `AttributeError` on mutation. Pydantic `frozen=True` raises `pydantic.ValidationError`. Tests using `pytest.raises(AttributeError)` must be updated.

3. **No positional construction.** Dataclasses accept positional arguments. Pydantic `BaseModel.__init__()` only accepts keyword arguments. All call sites using positional construction must be updated.

## Established Pattern

```python
class MyModel(BaseModel):
    model_config = ConfigDict(extra="ignore")  # absorbs unknown frontmatter fields
    # fields with defaults for permissive parsing
    id: str = ""
    tags: list[str] = []  # Pydantic handles mutable defaults safely
    created: date | None = None

    @field_validator("created", mode="before")
    @classmethod
    def _coerce_date(cls, v): ...  # permissive, returns None on bad input

    def to_dict(self, root: Path) -> dict[str, Any]:
        # explicit logic preferred over model_dump() wrapper
        # when selective inclusion rules apply
        ...
```

For frozen value objects: `class MyModel(BaseModel, frozen=True):` — no `ConfigDict` needed for just frozen.
