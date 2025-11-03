"""Backlog item models."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class BacklogItem:
  """Backlog item model representing issues, problems, improvements, and risks."""

  id: str
  kind: str  # issue, problem, improvement, risk
  status: str
  title: str
  path: Path
  frontmatter: dict[str, Any] = field(default_factory=dict)
  tags: list[str] = field(default_factory=list)
  # Kind-specific optional fields
  severity: str = ""
  categories: list[str] = field(default_factory=list)
  impact: str = ""
  likelihood: float = 0.0
  created: str = ""
  updated: str = ""
