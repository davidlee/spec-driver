#!/usr/bin/env python3
"""List change artefacts (deltas, revisions, audits) with optional filters."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from typing import TYPE_CHECKING

from supekku.scripts.lib.change_registry import ChangeRegistry  # type: ignore
from supekku.scripts.lib.cli_utils import add_root_argument

if TYPE_CHECKING:
    from collections.abc import Iterable

KIND_CHOICES = ["delta", "revision", "audit", "all"]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    add_root_argument(parser)
    parser.add_argument(
        "--kind",
        choices=KIND_CHOICES,
        default="all",
        help="Change artefact kind to list",
    )
    parser.add_argument(
        "--filter",
        dest="substring",
        help="Substring to match against ID, slug, or name (case-insensitive)",
    )
    parser.add_argument(
        "--status",
        help="Filter by status (exact match)",
    )
    parser.add_argument(
        "--applies-to",
        dest="applies_to",
        help="Filter artefacts that reference a requirement (applies_to or relation target)",
    )
    parser.add_argument(
        "--paths",
        action="store_true",
        help="Include relative file paths",
    )
    parser.add_argument(
        "--relations",
        action="store_true",
        help="Include relation tuples (type:target)",
    )
    parser.add_argument(
        "--applies",
        action="store_true",
        help="Include applies_to.requirements list",
    )
    parser.add_argument(
        "--plan",
        action="store_true",
        help="Include plan overview for deltas (plan_id and phases)",
    )
    return parser.parse_args(argv)


def iter_artifacts(root: Path, kinds: Iterable[str]):
    for kind in kinds:
        registry = ChangeRegistry(root=root, kind=kind)
        yield from registry.collect().values()


def matches_filters(
    artifact, *, substring: str | None, status: str | None, applies_to: str | None,
) -> bool:
    if substring:
        text = substring.lower()
        if not (
            text in artifact.id.lower()
            or text in artifact.slug.lower()
            or text in artifact.name.lower()
        ):
            return False
    if status and artifact.status.lower() != status.lower():
        return False
    if applies_to:
        match = applies_to.lower()
        applies_list = []
        reqs = artifact.applies_to.get("requirements") if artifact.applies_to else []
        if isinstance(reqs, list):
            applies_list.extend(str(item).lower() for item in reqs)
        for relation in artifact.relations:
            target = str(relation.get("target", "")).lower()
            if target:
                applies_list.append(target)
        if not any(match in item for item in applies_list):
            return False
    return True


def format_artifact(
    artifact,
    *,
    root: Path,
    include_paths: bool,
    include_relations: bool,
    include_applies: bool,
    include_plan: bool,
) -> str:
    fields: list[str] = [artifact.id, artifact.kind, artifact.status, artifact.slug]
    if include_paths:
        try:
            rel = artifact.path.relative_to(root)
        except ValueError:
            rel = artifact.path
        fields.append(rel.as_posix())
    if include_applies:
        reqs = []
        if artifact.applies_to:
            values = artifact.applies_to.get("requirements")
            if isinstance(values, list):
                reqs = [str(item) for item in values]
        fields.append(",".join(reqs))
    if include_relations:
        relations = []
        for relation in artifact.relations:
            rel_type = str(relation.get("type", ""))
            target = str(relation.get("target", ""))
            if rel_type or target:
                relations.append(f"{rel_type}:{target}" if rel_type else target)
        fields.append(",".join(relations))
    if include_plan:
        if getattr(artifact, "plan", None):
            plan_id = artifact.plan.get("id", "")
            phases = artifact.plan.get("phases") or []
            summaries = []
            for phase in phases:
                phase_id = phase.get("phase") or phase.get("id") or ""
                objective = str(phase.get("objective", "")).strip()
                if objective:
                    objective = objective.splitlines()[0]
                    if len(objective) > 60:
                        objective = objective[:57] + "..."
                    summaries.append(f"{phase_id}:{objective}")
                elif phase_id:
                    summaries.append(str(phase_id))
            plan_field = plan_id
            if summaries:
                plan_field += " [" + "; ".join(summaries) + "]"
        else:
            plan_field = ""
        fields.append(plan_field)
    return "\t".join(fields)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root

    kinds = [args.kind] if args.kind != "all" else ["delta", "revision", "audit"]

    artifacts = list(iter_artifacts(root, kinds))
    artifacts.sort(key=lambda art: art.id)

    substring = (args.substring or "").strip().lower() or None
    status = (args.status or "").strip() or None
    applies_to = (args.applies_to or "").strip() or None

    for artifact in artifacts:
        if not matches_filters(
            artifact, substring=substring, status=status, applies_to=applies_to,
        ):
            continue
        print(
            format_artifact(
                artifact,
                root=root,
                include_paths=args.paths,
                include_relations=args.relations,
                include_applies=args.applies,
                include_plan=args.plan,
            ),
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
