"""Tests for npm_utils module."""

from unittest.mock import patch

from supekku.scripts.lib.core.npm_utils import (
  PackageManager,
  PackageManagerInfo,
  detect_package_manager,
  get_install_instructions,
  get_package_manager_info,
  is_bun_available,
  is_npm_available,
  is_npm_package_available,
  is_pnpm_available,
)


class TestModuleImports:
  """Test that module imports successfully."""

  def test_package_manager_type_alias(self):
    """Test PackageManager type alias is available."""
    # Type alias exists and can be used in type hints
    pm: PackageManager = "npm"
    assert pm in ("npm", "pnpm", "bun")


class TestIsNpmAvailable:
  """Test is_npm_available function."""

  @patch("supekku.scripts.lib.core.npm_utils.which")
  def test_npm_available(self, mock_which):
    """Test when npm is available in PATH."""
    mock_which.return_value = "/usr/bin/npm"
    assert is_npm_available() is True
    mock_which.assert_called_once_with("npm")

  @patch("supekku.scripts.lib.core.npm_utils.which")
  def test_npm_not_available(self, mock_which):
    """Test when npm is not available in PATH."""
    mock_which.return_value = None
    assert is_npm_available() is False
    mock_which.assert_called_once_with("npm")


class TestIsPnpmAvailable:
  """Test is_pnpm_available function."""

  @patch("supekku.scripts.lib.core.npm_utils.which")
  def test_pnpm_available(self, mock_which):
    """Test when pnpm is available in PATH."""
    mock_which.return_value = "/usr/bin/pnpm"
    assert is_pnpm_available() is True
    mock_which.assert_called_once_with("pnpm")

  @patch("supekku.scripts.lib.core.npm_utils.which")
  def test_pnpm_not_available(self, mock_which):
    """Test when pnpm is not available in PATH."""
    mock_which.return_value = None
    assert is_pnpm_available() is False
    mock_which.assert_called_once_with("pnpm")


class TestIsBunAvailable:
  """Test is_bun_available function."""

  @patch("supekku.scripts.lib.core.npm_utils.which")
  def test_bun_available(self, mock_which):
    """Test when bun is available in PATH."""
    mock_which.return_value = "/usr/bin/bun"
    assert is_bun_available() is True
    mock_which.assert_called_once_with("bun")

  @patch("supekku.scripts.lib.core.npm_utils.which")
  def test_bun_not_available(self, mock_which):
    """Test when bun is not available in PATH."""
    mock_which.return_value = None
    assert is_bun_available() is False
    mock_which.assert_called_once_with("bun")


class TestDetectPackageManager:
  """Test detect_package_manager function."""

  def test_detect_pnpm_from_lockfile(self, tmp_path):
    """Test detection of pnpm from pnpm-lock.yaml."""
    lockfile = tmp_path / "pnpm-lock.yaml"
    lockfile.write_text("# pnpm lockfile")

    result = detect_package_manager(tmp_path)
    assert result == "pnpm"

  def test_detect_bun_from_lockfile(self, tmp_path):
    """Test detection of bun from bun.lockb."""
    lockfile = tmp_path / "bun.lockb"
    lockfile.write_bytes(b"bun binary lockfile")

    result = detect_package_manager(tmp_path)
    assert result == "bun"

  def test_detect_npm_from_package_lock(self, tmp_path):
    """Test detection of npm from package-lock.json."""
    lockfile = tmp_path / "package-lock.json"
    lockfile.write_text("{}")

    result = detect_package_manager(tmp_path)
    assert result == "npm"

  def test_detect_npm_from_yarn_lock(self, tmp_path):
    """Test detection of npm from yarn.lock (yarn uses npm)."""
    lockfile = tmp_path / "yarn.lock"
    lockfile.write_text("# yarn lockfile")

    result = detect_package_manager(tmp_path)
    assert result == "npm"

  def test_defaults_to_npm_when_no_lockfile(self, tmp_path):
    """Test that npm is returned as default when no lockfile found."""
    result = detect_package_manager(tmp_path)
    assert result == "npm"

  def test_walks_up_directory_tree(self, tmp_path):
    """Test that detection walks up to find lockfile in parent."""
    # Create lockfile in parent
    lockfile = tmp_path / "pnpm-lock.yaml"
    lockfile.write_text("# pnpm lockfile")

    # Create nested directory
    nested = tmp_path / "src" / "components"
    nested.mkdir(parents=True)

    # Detect from nested directory should find parent lockfile
    result = detect_package_manager(nested)
    assert result == "pnpm"

  def test_priority_order_pnpm_over_bun(self, tmp_path):
    """Test that pnpm takes priority over bun when both lockfiles exist."""
    (tmp_path / "pnpm-lock.yaml").write_text("# pnpm")
    (tmp_path / "bun.lockb").write_bytes(b"bun")

    result = detect_package_manager(tmp_path)
    assert result == "pnpm"

  def test_priority_order_bun_over_npm(self, tmp_path):
    """Test that bun takes priority over npm when both lockfiles exist."""
    (tmp_path / "bun.lockb").write_bytes(b"bun")
    (tmp_path / "package-lock.json").write_text("{}")

    result = detect_package_manager(tmp_path)
    assert result == "bun"

  def test_detects_from_file_path(self, tmp_path):
    """Test detection when given a file path (should use parent directory)."""
    lockfile = tmp_path / "pnpm-lock.yaml"
    lockfile.write_text("# pnpm")

    test_file = tmp_path / "index.ts"
    test_file.write_text("// typescript")

    result = detect_package_manager(test_file)
    assert result == "pnpm"


class TestGetPackageManagerInfo:
  """Test get_package_manager_info function and PackageManagerInfo dataclass."""

  @patch("supekku.scripts.lib.core.npm_utils.is_npm_available")
  @patch("supekku.scripts.lib.core.npm_utils.detect_package_manager")
  def test_returns_npm_info_when_npm_detected(self, mock_detect, mock_is_npm, tmp_path):
    """Test npm PackageManagerInfo returned for npm project."""
    mock_detect.return_value = "npm"
    mock_is_npm.return_value = True

    info = get_package_manager_info(tmp_path)

    assert isinstance(info, PackageManagerInfo)
    assert info.name == "npm"
    assert info.install_global_command == ["npm", "install", "-g"]
    assert info.install_local_command == ["npm", "install", "--save-dev"]

    # Test build_npx_command callable
    cmd = info.build_npx_command("ts-doc-extract")
    assert cmd == ["npx", "--yes", "ts-doc-extract"]

  @patch("supekku.scripts.lib.core.npm_utils.is_pnpm_available")
  @patch("supekku.scripts.lib.core.npm_utils.detect_package_manager")
  def test_returns_pnpm_info_when_pnpm_detected_and_available(
    self, mock_detect, mock_is_pnpm, tmp_path
  ):
    """Test pnpm PackageManagerInfo returned when pnpm detected and available."""
    mock_detect.return_value = "pnpm"
    mock_is_pnpm.return_value = True

    info = get_package_manager_info(tmp_path)

    assert info.name == "pnpm"
    assert info.install_global_command == ["pnpm", "add", "-g"]
    assert info.install_local_command == ["pnpm", "add", "--save-dev"]

    # Test build_npx_command callable - pnpm requires package twice
    cmd = info.build_npx_command("ts-doc-extract")
    assert cmd == ["pnpm", "dlx", "--package=ts-doc-extract", "ts-doc-extract"]

  @patch("supekku.scripts.lib.core.npm_utils.is_bun_available")
  @patch("supekku.scripts.lib.core.npm_utils.detect_package_manager")
  def test_returns_bun_info_when_bun_detected_and_available(
    self, mock_detect, mock_is_bun, tmp_path
  ):
    """Test bun PackageManagerInfo returned when bun detected and available."""
    mock_detect.return_value = "bun"
    mock_is_bun.return_value = True

    info = get_package_manager_info(tmp_path)

    assert info.name == "bun"
    assert info.install_global_command == ["bun", "add", "-g"]
    assert info.install_local_command == ["bun", "add", "--save-dev"]

    # Test build_npx_command callable
    cmd = info.build_npx_command("ts-doc-extract")
    assert cmd == ["bunx", "--yes", "ts-doc-extract"]

  @patch("supekku.scripts.lib.core.npm_utils.is_pnpm_available")
  @patch("supekku.scripts.lib.core.npm_utils.detect_package_manager")
  def test_falls_back_to_npm_when_pnpm_not_available(
    self, mock_detect, mock_is_pnpm, tmp_path
  ):
    """Test falls back to npm when pnpm detected but not available."""
    mock_detect.return_value = "pnpm"
    mock_is_pnpm.return_value = False

    info = get_package_manager_info(tmp_path)

    assert info.name == "npm"
    cmd = info.build_npx_command("pkg")
    assert cmd == ["npx", "--yes", "pkg"]

  @patch("supekku.scripts.lib.core.npm_utils.is_bun_available")
  @patch("supekku.scripts.lib.core.npm_utils.detect_package_manager")
  def test_falls_back_to_npm_when_bun_not_available(
    self, mock_detect, mock_is_bun, tmp_path
  ):
    """Test falls back to npm when bun detected but not available."""
    mock_detect.return_value = "bun"
    mock_is_bun.return_value = False

    info = get_package_manager_info(tmp_path)

    assert info.name == "npm"
    cmd = info.build_npx_command("pkg")
    assert cmd == ["npx", "--yes", "pkg"]


class TestIsNpmPackageAvailable:
  """Test is_npm_package_available function."""

  def test_package_available_locally(self, tmp_path):
    """Test package found in local node_modules/.bin/."""
    # Create node_modules/.bin/ts-doc-extract
    node_modules_bin = tmp_path / "node_modules" / ".bin"
    node_modules_bin.mkdir(parents=True)
    package_bin = node_modules_bin / "ts-doc-extract"
    package_bin.write_text("#!/usr/bin/env node")
    package_bin.chmod(0o755)


    result = is_npm_package_available("ts-doc-extract", tmp_path)
    assert result is True

  @patch("supekku.scripts.lib.core.npm_utils.which")
  def test_package_not_executable_local(self, mock_which, tmp_path):
    """Test package exists locally but is not executable (should be False)."""
    # Create node_modules/.bin/ts-doc-extract without execute permission
    node_modules_bin = tmp_path / "node_modules" / ".bin"
    node_modules_bin.mkdir(parents=True)
    package_bin = node_modules_bin / "ts-doc-extract"
    package_bin.write_text("#!/usr/bin/env node")
    package_bin.chmod(0o644)  # Not executable

    # Mock which to return None (not in global PATH either)
    mock_which.return_value = None


    result = is_npm_package_available("ts-doc-extract", tmp_path)
    assert result is False
    mock_which.assert_called_once_with("ts-doc-extract")

  @patch("supekku.scripts.lib.core.npm_utils.which")
  def test_package_available_globally(self, mock_which, tmp_path):
    """Test package found globally via which() when not in local node_modules."""
    mock_which.return_value = "/usr/local/bin/ts-doc-extract"


    result = is_npm_package_available("ts-doc-extract", tmp_path)
    assert result is True
    mock_which.assert_called_once_with("ts-doc-extract")

  @patch("supekku.scripts.lib.core.npm_utils.which")
  def test_package_not_available_anywhere(self, mock_which, tmp_path):
    """Test package not found locally or globally."""
    mock_which.return_value = None


    result = is_npm_package_available("ts-doc-extract", tmp_path)
    assert result is False

  @patch("supekku.scripts.lib.core.npm_utils.which")
  def test_package_check_global_only_when_no_root(self, mock_which):
    """Test only checks global when package_root is None."""
    mock_which.return_value = "/usr/local/bin/pkg"


    result = is_npm_package_available("pkg", None)
    assert result is True
    mock_which.assert_called_once_with("pkg")

  @patch("supekku.scripts.lib.core.npm_utils.which")
  def test_local_takes_priority_over_global(self, mock_which, tmp_path):
    """Test local installation found first, global check never called."""
    # Create local installation
    node_modules_bin = tmp_path / "node_modules" / ".bin"
    node_modules_bin.mkdir(parents=True)
    package_bin = node_modules_bin / "ts-doc-extract"
    package_bin.write_text("#!/usr/bin/env node")
    package_bin.chmod(0o755)


    result = is_npm_package_available("ts-doc-extract", tmp_path)
    assert result is True
    # which() should not be called since local found
    mock_which.assert_not_called()


class TestGetInstallInstructions:
  """Test get_install_instructions function."""

  def test_npm_install_instructions_global_first(self):
    """Test npm installation instructions with global shown first."""
    pm_info = PackageManagerInfo(
      name="npm",
      build_npx_command=lambda pkg: ["npx", "--yes", pkg],
      install_global_command=["npm", "install", "-g"],
      install_local_command=["npm", "install", "--save-dev"],
    )

    result = get_install_instructions("ts-doc-extract", pm_info, prefer_local=False)

    # Should contain both global and local options, global first
    assert "npm install -g ts-doc-extract" in result
    assert "npm install --save-dev ts-doc-extract" in result
    # Check ordering: global appears before local
    global_pos = result.index("npm install -g")
    local_pos = result.index("npm install --save-dev")
    assert global_pos < local_pos

  def test_npm_install_instructions_local_first(self):
    """Test npm installation instructions with local shown first."""
    pm_info = PackageManagerInfo(
      name="npm",
      build_npx_command=lambda pkg: ["npx", "--yes", pkg],
      install_global_command=["npm", "install", "-g"],
      install_local_command=["npm", "install", "--save-dev"],
    )

    result = get_install_instructions("ts-doc-extract", pm_info, prefer_local=True)

    # Should contain both options, local first
    assert "npm install --save-dev ts-doc-extract" in result
    assert "npm install -g ts-doc-extract" in result
    # Check ordering: local appears before global
    local_pos = result.index("npm install --save-dev")
    global_pos = result.index("npm install -g")
    assert local_pos < global_pos

  def test_pnpm_install_instructions(self):
    """Test pnpm installation instructions use correct syntax."""
    pm_info = PackageManagerInfo(
      name="pnpm",
      build_npx_command=lambda pkg: ["pnpm", "dlx", f"--package={pkg}", pkg],
      install_global_command=["pnpm", "add", "-g"],
      install_local_command=["pnpm", "add", "--save-dev"],
    )

    result = get_install_instructions("ts-doc-extract", pm_info)

    # Should use pnpm commands
    assert "pnpm add -g ts-doc-extract" in result
    assert "pnpm add --save-dev ts-doc-extract" in result
    # Should NOT contain npm commands
    assert "npm install" not in result

  def test_bun_install_instructions(self):
    """Test bun installation instructions use correct syntax."""
    pm_info = PackageManagerInfo(
      name="bun",
      build_npx_command=lambda pkg: ["bunx", "--yes", pkg],
      install_global_command=["bun", "add", "-g"],
      install_local_command=["bun", "add", "--save-dev"],
    )

    result = get_install_instructions("prettier", pm_info)

    # Should use bun commands
    assert "bun add -g prettier" in result
    assert "bun add --save-dev prettier" in result
    # Should NOT contain npm commands
    assert "npm install" not in result

  def test_instructions_are_multiline(self):
    """Test that instructions span multiple lines for readability."""
    pm_info = PackageManagerInfo(
      name="npm",
      build_npx_command=lambda pkg: ["npx", "--yes", pkg],
      install_global_command=["npm", "install", "-g"],
      install_local_command=["npm", "install", "--save-dev"],
    )

    result = get_install_instructions("pkg", pm_info)

    # Should have multiple lines
    lines = result.strip().split("\n")
    assert len(lines) >= 2  # At least 2 lines for global and local options
