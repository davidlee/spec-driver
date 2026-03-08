"""Dependency availability checks.

Checks core dependencies and per-language contract generation toolchains.
Python contract generation uses built-in AST and needs no external tool.
"""

from __future__ import annotations

import sys
from shutil import which
from typing import TYPE_CHECKING

from supekku.scripts.lib.core.npm_utils import is_npm_package_available
from supekku.scripts.lib.diagnostics.models import DiagnosticResult

if TYPE_CHECKING:
  from supekku.scripts.lib.workspace import Workspace

CATEGORY = "deps"


def check_deps(ws: Workspace) -> list[DiagnosticResult]:
  """Check availability of required and optional dependencies."""
  results: list[DiagnosticResult] = []

  # Core
  results.append(_check_python())
  results.append(_check_git())

  # Go contract generation
  results.append(
    _check_binary(
      "go",
      "Go toolchain",
      "Install Go from https://go.dev/dl/",
    )
  )
  results.append(
    _check_binary(
      "gomarkdoc",
      "Go doc generator",
      "go install github.com/princjef/gomarkdoc/cmd/gomarkdoc@latest",
    )
  )

  # Zig contract generation
  results.append(
    _check_binary(
      "zig",
      "Zig toolchain",
      "Install Zig from https://ziglang.org/download/",
    )
  )
  results.append(
    _check_binary(
      "zigmarkdoc",
      "Zig doc generator",
      "Install from https://github.com/davidlee/zigmarkdoc",
    )
  )

  # TypeScript contract generation
  results.append(
    _check_binary(
      "node",
      "Node.js runtime",
      "Install Node.js from https://nodejs.org/",
    )
  )
  results.append(_check_ts_doc_extract(ws))

  return results


def _check_python() -> DiagnosticResult:
  vi = sys.version_info
  version = f"{vi.major}.{vi.minor}.{vi.micro}"
  return DiagnosticResult(
    category=CATEGORY,
    name="python",
    status="pass",
    message=f"Python {version}",
  )


def _check_git() -> DiagnosticResult:
  if which("git"):
    return DiagnosticResult(
      category=CATEGORY,
      name="git",
      status="pass",
      message="git available",
    )
  if which("jj"):
    return DiagnosticResult(
      category=CATEGORY,
      name="git",
      status="pass",
      message="jj available (git alternative)",
    )
  return DiagnosticResult(
    category=CATEGORY,
    name="git",
    status="warn",
    message="Neither git nor jj found",
    suggestion="Install git or jujutsu for VCS operations",
  )


def _check_binary(name: str, label: str, install_hint: str) -> DiagnosticResult:
  """Check if a binary is available in PATH."""
  if which(name):
    return DiagnosticResult(
      category=CATEGORY,
      name=name,
      status="pass",
      message=f"{label} available",
    )
  return DiagnosticResult(
    category=CATEGORY,
    name=name,
    status="warn",
    message=f"{label} not found (optional)",
    suggestion=install_hint,
  )


def _check_ts_doc_extract(ws: Workspace) -> DiagnosticResult:
  if is_npm_package_available("ts-doc-extract", package_root=ws.root):
    return DiagnosticResult(
      category=CATEGORY,
      name="ts-doc-extract",
      status="pass",
      message="ts-doc-extract available",
    )
  return DiagnosticResult(
    category=CATEGORY,
    name="ts-doc-extract",
    status="warn",
    message="ts-doc-extract not found (optional: TS sync)",
    suggestion="Install with: npm install -g ts-doc-extract",
  )
