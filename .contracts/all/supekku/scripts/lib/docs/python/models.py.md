# supekku.scripts.lib.docs.python.models

Data models for Python documentation generation API.

## Classes

### DocResult

Result of documentation generation for a single file/variant combination.

**Inherits from:** BaseModel

#### Methods

- @property `success(self) -> bool`: Whether generation was successful.

### VariantSpec

Specification for a documentation variant.

**Inherits from:** BaseModel

#### Methods

- @classmethod `all_symbols(cls) -> VariantSpec`: Create ALL variant spec.
- @classmethod `public(cls) -> VariantSpec`: Create PUBLIC variant spec.
- @classmethod `tests(cls) -> VariantSpec`: Create TESTS variant spec.

### VariantType

Documentation variant types.

**Inherits from:** Enum
