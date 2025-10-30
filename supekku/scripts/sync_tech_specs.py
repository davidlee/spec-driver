#!/usr/bin/env python3
"""Synchronise tech specs with Go packages and generate interface documentation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TECH_DIR = ROOT / "specify" / "tech"
REGISTRY_PATH = TECH_DIR / "registry_v2.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from supekku.scripts.lib.sync_engine import (  # type: ignore
    GomarkdocNotAvailableError,
    SyncOptions,
    TechSpecSyncEngine,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "packages",
        nargs="*",
        help="Specific package paths to sync (module or relative path).",
    )
    parser.add_argument(
        "--existing",
        action="store_true",
        help="Operate on packages already registered in specify/tech/registry_v2.json",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run gomarkdoc in --check mode to verify contracts match code",
    )
    parser.add_argument(
        "--allow-missing-go",
        action="store_true",
        help="Allow spec creation even when no non-test Go files are present",
    )
    args = parser.parse_args()

    if not TECH_DIR.exists():
        sys.exit("Tech spec directory not found. Did paths change?")

    engine = TechSpecSyncEngine(
        root=ROOT,
        tech_dir=TECH_DIR,
        registry_path=REGISTRY_PATH,
    )

    options = SyncOptions(
        packages=args.packages,
        existing=args.existing,
        check=args.check,
        allow_missing_go=args.allow_missing_go,
    )

    try:
        result = engine.synchronize(options)
    except GomarkdocNotAvailableError as exc:
        sys.exit(str(exc))

    if result.created_specs:
        for _pkg, _spec_id in sorted(result.created_specs.items()):
            pass
    else:
        pass

    if result.skipped_packages:
        for _skipped in result.skipped_packages:
            pass

    for _warning in result.warnings:
        pass


if __name__ == "__main__":
    main()
