"""Supekku library modules for spec management and documentation generation."""

from .spec_utils import (
    load_markdown_file,
    dump_markdown_file,
    ensure_list_entry,
    append_unique,
    load_validated_markdown_file,
)
from .create_spec import (
    CreateSpecOptions,
    CreateSpecResult,
    SpecCreationError,
    create_spec,
)
from .frontmatter_schema import (
    FrontmatterValidationError,
    FrontmatterValidationResult,
    Relation,
    validate_frontmatter,
)
from .backlog import (
    append_backlog_summary,
    create_backlog_entry,
    find_repo_root,
)
from .relations import (
    add_relation,
    list_relations,
    remove_relation,
)
from .spec_models import Spec
from .spec_registry import SpecRegistry
from .change_registry import ChangeRegistry
from .workspace import Workspace

__all__ = [
    "load_markdown_file",
    "dump_markdown_file",
    "ensure_list_entry",
    "append_unique",
    "load_validated_markdown_file",
    "CreateSpecOptions",
    "CreateSpecResult",
    "SpecCreationError",
    "create_spec",
    "append_backlog_summary",
    "create_backlog_entry",
    "find_repo_root",
    "add_relation",
    "list_relations",
    "remove_relation",
    "Spec",
    "SpecRegistry",
    "ChangeRegistry",
    "Workspace",
    "FrontmatterValidationError",
    "FrontmatterValidationResult",
    "Relation",
    "validate_frontmatter",
]
