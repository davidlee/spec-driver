# supekku.scripts.lib.requirements.models_test

Tests for requirement data models.

## Classes

### TestRequirementRecordToDict

Tests for RequirementRecord.to_dict() serialization.

**Inherits from:** unittest.TestCase

#### Methods

- `test_to_dict_ext_id_only(self) -> None`: ext_id without ext_url — only ext_id appears.
- `test_to_dict_includes_ext_id_ext_url_when_set(self) -> None`: Populated ext_id/ext_url should appear in serialized dict.
- `test_to_dict_omits_ext_id_ext_url_when_empty(self) -> None`: Empty ext_id/ext_url should not appear in serialized dict.
