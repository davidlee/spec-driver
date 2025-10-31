# supekku.scripts.lib.workspace

Workspace management for organizing specs, changes, and requirements.

## Constants

- `__all__`

## Classes

### Workspace

Unified facade over project registries.

#### Methods

- @property `audit_registry(self) -> ChangeRegistry`
- @property `decisions(self) -> DecisionRegistry` - Decisions --------------------------------------------------
- @property `delta_registry(self) -> ChangeRegistry` - Change registries ------------------------------------------
- @classmethod `from_cwd(cls) -> Workspace`
- `reload_specs(self) -> None`
- @property `requirements(self) -> RequirementsRegistry` - Requirements ------------------------------------------------
- @property `revision_registry(self) -> ChangeRegistry`
- @property `specs(self) -> SpecRegistry` - Spec access -------------------------------------------------
- `sync_change_registries(self) -> None`
- `sync_decisions(self) -> None`
- `sync_requirements(self) -> None`
