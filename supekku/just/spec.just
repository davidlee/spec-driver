# # find specs matching term
# [group('specs')]
# find-package-for-path path="":
#     @uv run python supekku/scripts/list_specs.py --for-path {{path}}

# # find specs matching term
# [group('specs')]
# find-package-spec query:
#     @uv run python supekku/scripts/list_specs.py --package {{query}} --packages --for-path --paths

# # find specs matching term
# [group('specs')]
# find-specs query:
#     @uv run python supekku/scripts/list_specs.py --filter {{query}} --paths

# list
[group('specs')]
list-specs *args:
    @uv run python supekku/scripts/list_specs.py {{args}}

# sync specs *arg (--help to see options)
[group('specs')]
sync-specs *args: && registry-validate
    @uv run python supekku/scripts/sync_specs.py {{args}}

# create a new spec
[group('factories')]
new-spec +name:
    @uv run python supekku/scripts/create_new_spec.py "{{name}}"

# create a new delta
[group('factories')]
new-delta +name:
    @uv run python supekku/scripts/create_delta.py "{{name}}"

# create a new revision
[group('factories')]
new-revision +name:
    @uv run python supekku/scripts/create_revision.py "{{name}}"
