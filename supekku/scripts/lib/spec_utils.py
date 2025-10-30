"""Utilities for working with specification files and frontmatter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    msg = "PyYAML is required for spec tooling. Install with `pip install PyYAML`."
    raise SystemExit(
        msg,
    ) from exc

try:
    import frontmatter
except ImportError as exc:
    msg = "python-frontmatter is required for spec tooling. Install with `pip install python-frontmatter`."
    raise SystemExit(
        msg,
    ) from exc

from .frontmatter_schema import (
    FrontmatterValidationResult,
    validate_frontmatter,
)


def load_markdown_file(path: Path | str) -> tuple[dict[str, Any], str]:
    """Load markdown file and extract frontmatter and content."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    post = frontmatter.loads(text)
    frontmatter_data: dict[str, Any] = dict(post.metadata or {})
    body = post.content.lstrip("\n")
    if body and text.endswith("\n") and not body.endswith("\n"):
        body = body + "\n"
    return frontmatter_data, body


def dump_markdown_file(
    path: Path | str, frontmatter: dict[str, Any], body: str,
) -> None:
    """Write frontmatter and content to a markdown file."""
    path = Path(path)
    frontmatter_yaml = yaml.safe_dump(frontmatter, sort_keys=False).strip()
    body = body.lstrip("\n")
    if body and not body.endswith("\n"):
        body = body + "\n"
    combined = f"---\n{frontmatter_yaml}\n---\n\n{body}"
    path.write_text(combined, encoding="utf-8")


def ensure_list_entry(frontmatter: dict[str, Any], key: str) -> list[Any]:
    """Ensure a frontmatter key contains a list value."""
    value = frontmatter.setdefault(key, [])
    if not isinstance(value, list):
        msg = f"frontmatter[{key!r}] expected list, got {type(value).__name__}"
        raise TypeError(
            msg,
        )
    return value


def append_unique(values: list[Any], item: Any) -> bool:
    """Append item to list if not already present, return True if added."""
    if item in values:
        return False
    values.append(item)
    return True


def load_validated_markdown_file(
    path: Path | str, *, kind: str | None = None,
) -> tuple[FrontmatterValidationResult, str]:
    """Load a markdown file and validate its frontmatter against the schema.

    Raises FrontmatterValidationError if validation fails.
    """
    frontmatter, body = load_markdown_file(path)
    result = validate_frontmatter(frontmatter, kind=kind)
    return result, body
