#!/usr/bin/env bash
# migrate_to_consolidated_layout.sh
#
# Migrate a spec-driver workspace from the legacy scattered layout
# (specify/, change/, backlog/, memory/) to the consolidated flat
# layout under .spec-driver/.
#
# Creates backward-compat symlinks so old paths keep resolving.
#
# Prerequisites:
#   - Git repo with clean working tree
#   - .spec-driver/ directory exists (from spec-driver install)
#   - Content dirs exist at old locations
#
# Usage:
#   ./migrate_to_consolidated_layout.sh [--dry-run]
#
# Reference: DE-049, DR-049, ADR-006

set -euo pipefail

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
  echo "=== DRY RUN — no changes will be made ==="
  echo
fi

run() {
  echo "  $*"
  if ! $DRY_RUN; then
    "$@"
  fi
}

# --- Preflight checks ---

if ! git rev-parse --is-inside-work-tree &>/dev/null; then
  echo "ERROR: not inside a git repository" >&2
  exit 1
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "ERROR: working tree is not clean — commit or stash first" >&2
  exit 1
fi

if [[ ! -d .spec-driver ]]; then
  echo "ERROR: .spec-driver/ does not exist — run spec-driver install first" >&2
  exit 1
fi

# Check at least one old-layout dir exists
if [[ ! -d specify && ! -d change && ! -d backlog && ! -d memory ]]; then
  echo "Nothing to migrate — no legacy directories found."
  exit 0
fi

echo "=== Phase 1: Delete derived symlinks ==="

# Spec index directories (SpecIndexBuilder)
for dir in specify/tech/by-slug specify/tech/by-package specify/tech/by-language \
           specify/tech/by-category specify/tech/by-c4-level; do
  if [[ -d "$dir" ]]; then
    run git rm -rf "$dir"
  fi
done

# Alias symlinks
for link in specify/tech/assemblies specify/tech/units specify/tech/c4; do
  if [[ -L "$link" ]]; then
    run git rm "$link"
  fi
done

# Contract mirror symlinks (ContractMirrorTreeBuilder)
if compgen -G "specify/tech/SPEC-*/contracts" > /dev/null 2>&1; then
  for cdir in specify/tech/SPEC-*/contracts; do
    if [[ -d "$cdir" ]]; then
      run git rm -rf "$cdir"
    fi
  done
fi

# Decision status symlinks
for dir in specify/decisions/accepted specify/decisions/draft \
           specify/decisions/superseded specify/decisions/deprecated; do
  if [[ -d "$dir" ]]; then
    run git rm -rf "$dir"
  fi
done

# Derived registry file
if [[ -f specify/tech/registry_v2.json ]]; then
  run git rm specify/tech/registry_v2.json
fi

if ! $DRY_RUN && [[ -n "$(git status --porcelain)" ]]; then
  run git commit -m "spec-driver: delete derived symlinks before structural migration"
  echo
fi

echo "=== Phase 2: git mv content into .spec-driver/ ==="

# Content directories to move: source → dest
declare -A MOVES=(
  [specify/tech]=.spec-driver/tech
  [specify/product]=.spec-driver/product
  [specify/decisions]=.spec-driver/decisions
  [specify/policies]=.spec-driver/policies
  [specify/standards]=.spec-driver/standards
  [change/deltas]=.spec-driver/deltas
  [change/revisions]=.spec-driver/revisions
  [change/audits]=.spec-driver/audits
)

for src in "${!MOVES[@]}"; do
  dest="${MOVES[$src]}"
  if [[ -d "$src" && ! -L "$src" ]]; then
    if [[ -d "$dest" ]]; then
      echo "  SKIP: $dest already exists" >&2
    else
      run git mv "$src" "$dest"
    fi
  fi
done

# backlog and memory are top-level (not inside a grouping dir)
if [[ -d backlog && ! -L backlog ]]; then
  if [[ -d .spec-driver/backlog ]]; then
    echo "  SKIP: .spec-driver/backlog already exists" >&2
  else
    run git mv backlog .spec-driver/backlog
  fi
fi

if [[ -d memory && ! -L memory ]]; then
  if [[ -d .spec-driver/memory ]]; then
    echo "  SKIP: .spec-driver/memory already exists" >&2
  else
    run git mv memory .spec-driver/memory
  fi
fi

# Remove empty parent dirs
for dir in specify change; do
  if [[ -d "$dir" ]] && [[ -z "$(ls -A "$dir")" ]]; then
    run rmdir "$dir"
  fi
done

if ! $DRY_RUN && [[ -n "$(git status --porcelain)" ]]; then
  run git commit -m "spec-driver: git mv content directories into .spec-driver/"
  echo
fi

echo "=== Phase 3: Create backward-compat symlinks ==="

# specify/ — real dir with targeted symlinks
if [[ ! -d specify ]]; then
  run mkdir specify
fi
for sub in tech product decisions policies standards; do
  if [[ -d ".spec-driver/$sub" && ! -e "specify/$sub" ]]; then
    run ln -s "../.spec-driver/$sub" "specify/$sub"
  fi
done

# change/ — real dir with targeted symlinks
if [[ ! -d change ]]; then
  run mkdir change
fi
for sub in deltas revisions audits; do
  if [[ -d ".spec-driver/$sub" && ! -e "change/$sub" ]]; then
    run ln -s "../.spec-driver/$sub" "change/$sub"
  fi
done

# backlog, memory — direct symlinks
if [[ -d .spec-driver/backlog && ! -e backlog ]]; then
  run ln -s .spec-driver/backlog backlog
fi
if [[ -d .spec-driver/memory && ! -e memory ]]; then
  run ln -s .spec-driver/memory memory
fi

if ! $DRY_RUN && [[ -n "$(git status --porcelain)" ]]; then
  run git add specify/ change/ backlog memory 2>/dev/null || true
  run git commit -m "spec-driver: create backward-compat symlinks"
  echo
fi

echo "=== Phase 4: Verify ==="

FAIL=0
verify() {
  local path="$1"
  if [[ -e "$path" ]]; then
    echo "  OK: $path"
  else
    echo "  FAIL: $path does not resolve" >&2
    FAIL=1
  fi
}

# Spot-check a few paths through symlinks
verify specify/tech
verify specify/decisions
verify change/deltas
if [[ -L backlog ]]; then verify backlog; fi
if [[ -L memory ]]; then verify memory; fi

if [[ "$FAIL" -eq 0 ]]; then
  echo
  echo "Migration complete. Working tree:"
  git status --short
  echo
  echo "Next steps:"
  echo "  - Run 'uv run spec-driver sync' to rebuild registries and derived symlinks"
  echo "  - Update path defaults in code (see DR-049 phases 2-3)"
else
  echo
  echo "ERROR: some paths failed to resolve — check symlinks" >&2
  exit 1
fi
