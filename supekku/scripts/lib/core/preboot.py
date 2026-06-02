"""Re-export shim — see spec_driver.core.preboot."""

from spec_driver.core.preboot import (
  BOOT_SEQUENCE,
  GENERATED_HEADER,
  GOVERNANCE_LISTINGS,
  PI_OUTPUT_DIR,
  PI_OUTPUT_FILE,
  PREBOOT_OUTPUT_DIR,
  PREBOOT_OUTPUT_FILE,
  generate_preboot_content,
  write_preboot_file,
)

__all__ = [
  "BOOT_SEQUENCE",
  "GENERATED_HEADER",
  "GOVERNANCE_LISTINGS",
  "PI_OUTPUT_DIR",
  "PI_OUTPUT_FILE",
  "PREBOOT_OUTPUT_DIR",
  "PREBOOT_OUTPUT_FILE",
  "generate_preboot_content",
  "write_preboot_file",
]
