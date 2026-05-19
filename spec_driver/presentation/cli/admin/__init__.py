"""Presentation-layer admin commands (DE-137 migrations etc.).

User-facing wiring lives at ``supekku/cli/admin.py`` — this package
just hosts the orchestrator implementation modules. ``supekku.cli.admin``
imports ``migrate`` (and any future admin command callbacks) directly
and registers them via ``@app.command(...)``.
"""

from __future__ import annotations
