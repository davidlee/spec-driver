# change registry entry
[group('registry')]
list-changes *args:
    @uv run python supekku/scripts/list_changes.py {{args}}

# list deltas with status grouping
[group('registry')]
list-deltas *args:
    @uv run python supekku/scripts/list_deltas.py {{args}}

# change registry entry - by default sync all changes
[group('registry')]
registry-change +kind="all":
    @uv run python supekku/scripts/change_registry.py --kind {{kind}}

# validate workspace (all registry entries)
[group('registry')]
registry-validate:
    @uv run python supekku/scripts/validate_workspace.py --sync

# access the decision registry
[group('registry')]
decision-registry *args:
    @uv run python supekku/scripts/decision_registry.py {{args}}

# complete a delta and transition requirements to live
[group('registry')]
complete-delta delta_id *args:
    @uv run python supekku/scripts/complete_delta.py {{delta_id}} {{args}}
