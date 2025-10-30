"""Supekku library modules for spec management and documentation generation."""

from .backlog import (
    append_backlog_summary,
    create_backlog_entry,
    find_repo_root,
)
from .change_registry import ChangeRegistry
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
from .paths import (
    SPEC_DRIVER_DIR,
    get_about_dir,
    get_registry_dir,
    get_spec_driver_root,
    get_templates_dir,
)
from .relations import (
    add_relation,
    list_relations,
    remove_relation,
)
from .spec_models import Spec
from .spec_registry import SpecRegistry
from .spec_utils import (
    append_unique,
    dump_markdown_file,
    ensure_list_entry,
    load_markdown_file,
    load_validated_markdown_file,
)
from .workspace import Workspace

__all__ = [
    "ChangeRegistry",
    "CreateSpecOptions",
    "CreateSpecResult",
    "FrontmatterValidationError",
    "FrontmatterValidationResult",
    "Relation",
    "SPEC_DRIVER_DIR",
    "Spec",
    "SpecCreationError",
    "SpecRegistry",
    "Workspace",
    "add_relation",
    "append_backlog_summary",
    "append_unique",
    "create_backlog_entry",
    "create_spec",
    "dump_markdown_file",
    "ensure_list_entry",
    "find_repo_root",
    "get_about_dir",
    "get_registry_dir",
    "get_spec_driver_root",
    "get_templates_dir",
    "list_relations",
    "load_markdown_file",
    "load_validated_markdown_file",
    "remove_relation",
    "validate_frontmatter",
]
