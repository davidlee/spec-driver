# Notes for DE-144

## 2026-05-30 — implementation (light hotfix, DR skipped)

Both defects found installing Nix `0.10.0` into a live project.

- **packaging dep**: added `packaging` to `flake.nix` `dependencies` (line ~46). flake list now ⊇ all 10 pyproject runtime deps.
- **read-only dir perms**:
  - `copytree_with_write_permission` now `chmod u+w` directories as well as files.
  - new `remove_tree(path)` in `spec_driver/core/file_ops.py` force-removes read-only trees; re-exported via `supekku` shim.
  - 3 `shutil.rmtree` sites in `supekku/scripts/lib/skills/sync.py` routed through `remove_tree` (self-heals prior bad installs); unused `shutil` import dropped.
- Tests: regression test proven red-on-old/green-on-fix; +2 `remove_tree` tests. 25 file_ops + 62 skills-sync pass. ruff clean, no new pylint.
- Memory: `flake-deps-mirror-pyproject` records the dep-drift footgun.

Follow-up: guard test asserting flake deps ⊇ pyproject deps (see DE-144 §7).

