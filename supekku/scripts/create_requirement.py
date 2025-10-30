#!/usr/bin/env python3
"""Create a breakout requirement file under a spec."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from supekku.scripts.lib.create_change import (
    create_requirement_breakout,  # type: ignore
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", help="Spec ID (e.g. SPEC-200)")
    parser.add_argument("requirement", help="Requirement code (e.g. FR-010)")
    parser.add_argument("title", help="Requirement title")
    parser.add_argument(
        "--kind",
        choices=["functional", "non-functional", "policy", "standard"],
        help="Requirement kind override",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    path = create_requirement_breakout(
        args.spec,
        args.requirement,
        title=args.title,
        kind=args.kind,
    )
    print(f"Created requirement file at {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
