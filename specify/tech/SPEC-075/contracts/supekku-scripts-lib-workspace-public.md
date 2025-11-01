# supekku.scripts.lib.workspace

Workspace management for organizing specs, changes, and requirements.

## Classes

### Workspace

Unified facade over project registries.

#### Methods

- @property `audit_registry(self) -> ChangeRegistry`: Get or create audit change registry.

Returns:
  ChangeRegistry instance for audits.
- @property `decisions(self) -> DecisionRegistry`: Get or create decision registry.

Returns:
  DecisionRegistry instance for this workspace. - Decisions --------------------------------------------------
- @property `delta_registry(self) -> ChangeRegistry`: Get or create delta change registry.

Returns:
  ChangeRegistry instance for deltas. - Change registries ------------------------------------------
- @classmethod `from_cwd(cls) -> Workspace`: Create workspace from current working directory.

Returns:
  Workspace instance rooted at repository root.
- `reload_specs(self) -> None`: Reload spec registry from disk.
- @property `requirements(self) -> RequirementsRegistry`: Get or create requirements registry.

Returns:
  RequirementsRegistry instance for this workspace. - Requirements ------------------------------------------------
- @property `revision_registry(self) -> ChangeRegistry`: Get or create revision change registry.

Returns:
  ChangeRegistry instance for revisions.
- @property `specs(self) -> SpecRegistry`: Get or create spec registry.

Returns:
  SpecRegistry instance for this workspace. - Spec access -------------------------------------------------
- `sync_change_registries(self) -> None`: Synchronize change registries of specified kinds.

Args:
  kinds: List of registry kinds to sync. Defaults to all kinds.

Raises:
  ValueError: If an unsupported registry kind is specified.
- `sync_decisions(self) -> None`: Synchronize decision registry with symlinks.
- `sync_requirements(self) -> None`: Synchronize requirements registry from specs and changes.
