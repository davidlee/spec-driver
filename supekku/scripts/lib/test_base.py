"""Base classes for test utilities to reduce code duplication."""

import os
import tempfile
import unittest
from pathlib import Path


class RepoTestCase(unittest.TestCase):
    """Base test case that handles directory context and creates temporary repos."""

    def setUp(self) -> None:
        """Save current directory for restoration in tearDown."""
        self._cwd = os.getcwd()

    def tearDown(self) -> None:
        """Restore original directory."""
        os.chdir(self._cwd)

    def _make_repo(self) -> Path:
        """Create a temporary repository for testing."""
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        root = Path(tmpdir.name)
        (root / ".git").mkdir()
        return root

    def _create_repo(self) -> Path:
        """Alias for _make_repo for backward compatibility."""
        return self._make_repo()

    def _make_spec(self) -> Path:
        """Create a temporary spec repository for testing."""
        return self._make_repo()
