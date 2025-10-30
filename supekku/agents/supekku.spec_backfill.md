# supekku.spec_backfill

Guidance for backfilling or fleshing out spec documents when you are given either a Go package path or a SPEC identifier.

## 1. Locate the Specification

- **If you have a package path (e.g. `internal/infrastructure/git`)**
  ```bash
  uv run python supekku/scripts/list_specs.py --for-path "<package-path>" --paths --packages
  ```
  - The command returns the owning SPEC ID and the markdown path. Prefer absolute package paths when available; the command resolves relative paths against the repo root.

- **If you have a SPEC ID or slug (e.g. `SPEC-147` or `gitgo`)**
  ```bash
  uv run python supekku/scripts/list_specs.py --filter "<id-or-slug>" --paths --packages
  ```
  - Use `--packages` to confirm declared package coverage.

- Capture the spec path (second column when `--paths` is supplied) for editing. Example:
  ```bash
  spec_path=$(uv run python supekku/scripts/list_specs.py --for-path . --paths | cut -f2)
  nvim "$spec_path"
  ```

## 2. Create the Spec (only if missing)

If no existing spec is returned for the package:
```bash
just supekku::new-spec "<Readable Name>" -- --type tech --slug <slug>
```
- Fill the prompts using the Tech Spec template. After creation, re-run the locator command to confirm the new spec is associated with the package.

## 3. Frontmatter Expectations

When editing frontmatter:
- Ensure `packages:` lists every Go package the spec covers (absolute repo-relative paths).
- Keep `id`, `slug`, `name`, `status`, and `kind: spec` intact.
- Add/update `responsibilities`, `aliases`, and any lifecycle metadata needed by downstream tooling.
- Maintain the structured YAML blocks immediately after the title:
  - `supekku:spec.relationships@v1` records primary/collaborator requirements and spec interactions.
  - `supekku:spec.capabilities@v1` describes capabilities, the responsibilities they satisfy, and linked requirements.
  Edit the YAML directly; do not attempt to hand-edit rendered summaries.

Example frontmatter snippet:
```yaml
---
id: SPEC-003
slug: git-infrastructure
name: Git Infrastructure
status: draft
kind: spec
packages:
  - internal/infrastructure/git
responsibilities:
  - repository_persistence
---
```

## 4. Body Structure

- Follow the sections from the Tech Spec template (`.spec-driver/templates/tech-spec-template.md`). You can copy section scaffolding with:
  ```bash
  rg "^##" .spec-driver/templates/tech-spec-template.md
  ```
- Cover intent, responsibilities, interfaces, invariants, testing, and change history.
- Link to supporting artefacts (requirements, deltas, audits) when available.

## 5. Validation & Follow-up

After edits:
- Run `uv run python supekku/scripts/list_specs.py --filter <SPEC-ID> --packages` to verify package declarations render as expected.
- Double-check the structured blocks remain valid YAML (copy into `yamllint` or rely on agent tooling); regenerate any rendered tables if a helper script exists.
- If requirements were moved or introduced, follow up with registry sync:
  ```bash
  just supekku::sync-requirements
  ```
- For major structural changes, update or create accompanying revision/delta artefacts using `just supekku::new-revision` / `just supekku::new-delta` as appropriate.

Keep commits spec-specific: avoid mixing template changes, registry syncs, and spec prose in a single change unless instructed otherwise.