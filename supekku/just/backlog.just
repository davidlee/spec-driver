# create a new issue
[group('factories')]
new-issue +name:
    @uv run python supekku/scripts/backlog/create_entry.py issue "{{name}}"

# create a new problem
[group('factories')]
new-problem +name:
    @uv run python supekku/scripts/backlog/create_entry.py problem "{{name}}"

# create a new improvement
[group('factories')]
new-improvement +name:
    @uv run python supekku/scripts/backlog/create_entry.py improvement "{{name}}"

# create a new risk
[group('factories')]
new-risk +name:
    @uv run python supekku/scripts/backlog/create_entry.py risk "{{name}}"
    
# append missing backlog items
[group('backlog')]
backlog-append:
    @uv run python supekku/scripts/backlog/append.py
    
# append missing backlog items
[group('backlog')]
list-issues:
    @fd ISSUE.*\.md backlog/issues | sort
    
# append missing backlog items
[group('backlog')]
list-problems:
    @fd PROB.*\.md backlog/problems | sort

# append missing backlog items
[group('backlog')]
list-risks:
    @fd RISK.*\.md backlog/risks | sort
    
# append missing backlog items
[group('backlog')]
list-improvements:
    @fd IMPR.*\.md backlog/improvements | sort