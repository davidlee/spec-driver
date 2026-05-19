"""CLI vocabulary constants (POL-002).

Single source of truth for subcommand names, flag literals, and migration
artefact paths/patterns. Typer subcommand decorators, flag declarations,
and (P04) migration orchestrator references resolve against this module
rather than embedding magic strings inline.

Reference: DR-137 §5.4 "CLI vocabulary constants (F-16, POL-002)".
"""

from __future__ import annotations

# Re-exported from the migrations subsystem so the CLI vocabulary stays
# in sync with the canonical definition (Migrations isolation contract
# forbids the reverse direction).
from spec_driver.migrations._folder import MIGRATION_FOLDER_PATTERN

# ---------------------------------------------------------------------------
# Subcommand names
# ---------------------------------------------------------------------------
VALIDATE = "validate"
VALIDATE_WORKSPACE = "workspace"
VALIDATE_FILE = "file"
VALIDATE_TEMPLATES = "templates"

SCHEMA = "schema"
SCHEMA_ENUMS = "enums"

ADMIN = "admin"
ADMIN_MIGRATE = "migrate"
ADMIN_REGENERATE_TEMPLATES = "regenerate-templates"

# ---------------------------------------------------------------------------
# Flag literals
# ---------------------------------------------------------------------------
FLAG_STRICT = "--strict"
FLAG_NO_TOLERATED = "--no-tolerated-aliases"
FLAG_FIX = "--fix"
FLAG_SYNC = "--sync"
FLAG_KIND = "--kind"
FLAG_DRY_RUN = "--dry-run"
FLAG_CHECK = "--check"
FLAG_LIST = "--list"

# ---------------------------------------------------------------------------
# Migration artefact paths and patterns (IP-137-P04)
# MIGRATION_FOLDER_PATTERN re-exported above; log/lock paths owned here.
# ---------------------------------------------------------------------------
MIGRATION_LOG_PATH = ".spec-driver/run/migrations/{timestamp}-{step}.md"
MIGRATION_LOCK_PATH = ".spec-driver/run/migrations/.lock"


__all__ = [
  "ADMIN",
  "ADMIN_MIGRATE",
  "ADMIN_REGENERATE_TEMPLATES",
  "FLAG_CHECK",
  "FLAG_DRY_RUN",
  "FLAG_FIX",
  "FLAG_KIND",
  "FLAG_LIST",
  "FLAG_NO_TOLERATED",
  "FLAG_STRICT",
  "FLAG_SYNC",
  "MIGRATION_FOLDER_PATTERN",
  "MIGRATION_LOCK_PATH",
  "MIGRATION_LOG_PATH",
  "SCHEMA",
  "SCHEMA_ENUMS",
  "VALIDATE",
  "VALIDATE_FILE",
  "VALIDATE_TEMPLATES",
  "VALIDATE_WORKSPACE",
]
