
# create a new requirement 
[group('factories')]
new-requirement spec requirement +title:
    @uv run python supekku/scripts/create_requirement.py {{spec}} {{requirement}} "{{title}}"
    
# sync
[group('requirements')]
sync-requirements: && registry-validate
    @uv run python supekku/scripts/requirements.py sync

# list
[group('requirements')]
list-requirements *args:
    @uv run python supekku/scripts/requirements.py list {{args}}

# set status -- uid status
[group('requirements')]
set-requirement-status uid status:
    @uv run python supekku/scripts/requirements.py set-status {{uid}} {{status}}