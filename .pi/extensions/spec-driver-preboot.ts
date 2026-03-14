/**
 * Ensure spec-driver preboot context is fresh before pi reads AGENTS.md.
 *
 * Hooks session_shutdown, which fires before /reload re-reads resources.
 * Also fires on actual exit (harmless — preboot is idempotent, ~100ms).
 *
 * Design: DE-093, DR-093 (DEC-093-01, DEC-093-02).
 */
import type { ExtensionFactory } from "@mariozechner/pi-coding-agent";

const extension: ExtensionFactory = (pi) => {
  pi.on("session_shutdown", async (_event, ctx) => {
    await pi.exec("spec-driver", ["admin", "preboot", ctx.cwd]);
  });
};

export default extension;
