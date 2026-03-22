# supekku.cli.workflow_integration_test

End-to-end integration tests for workflow orchestration (DR-102 §12).

Verifies the full workflow cycle and regression safety.

## Functions

- `_create_delta_bundle(root, delta_id, slug, plan_id) -> Path`: Create a delta bundle for integration testing.

## Classes

### BlockUnblockCycleTest

Test block/unblock in a workflow cycle.

**Inherits from:** _IntegrationTestBase

#### Methods

- `test_block_and_unblock(self) -> None`

### ClaimGuardCycleTest

Test claim guard in realistic scenarios.

**Inherits from:** _IntegrationTestBase

#### Methods

- `test_claim_guard_prevents_double_accept(self) -> None`

### ExistingDeltasRegressionTest

VA-103-002: Existing deltas without workflow/ continue to work.

**Inherits from:** _IntegrationTestBase

#### Methods

- `test_delta_files_untouched(self) -> None`: Starting workflow doesn't modify existing delta files.
- `test_status_without_workflow_dir(self) -> None`: workflow status for a delta without workflow/ shows no state.

### FullWorkflowCycleTest

VA-103-001: Full workflow cycle per DR-102 §12.

Cycle: start → implement → handoff → review → changes_requested →
handoff → review → approve.

**Inherits from:** _IntegrationTestBase

#### Methods

- `test_full_cycle(self) -> None`

### PhaseCompleteCycleTest

Test phase complete with auto-handoff in a full cycle.

**Inherits from:** _IntegrationTestBase

#### Methods

- `test_phase_complete_auto_handoff(self) -> None`

### _IntegrationTestBase

Common setup for integration tests.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `_run(self) -> str`
