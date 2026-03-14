/**
 * Emit events when the agent touches spec-driver artifacts.
 *
 * Hooks `tool_result` for read/edit/write tools, classifies file paths
 * against spec-driver artifact patterns, and emits v1 events to
 * `.spec-driver/run/events.jsonl` + `tui.sock` Unix datagram.
 *
 * JSONL is written synchronously (append). Socket datagram is sent via
 * `pi.exec("python3", ...)` because Node.js dgram lacks AF_UNIX support.
 * Socket send is async, fire-and-forget, fail-silent.
 *
 * Fail-silent: all exceptions are swallowed (DEC-094-02).
 *
 * Design: DE-094, DR-094.
 *
 * SYNC: classification patterns mirrored from
 *       supekku/claude.hooks/artifact_event.py (_ARTIFACT_PATTERNS)
 *       see mem.artifact-pattern-sync
 */
import type {
  ExtensionAPI,
  ExtensionFactory,
} from "@mariozechner/pi-coding-agent";
import { appendFileSync, mkdirSync } from "node:fs";
import { join, relative } from "node:path";

// --- Artifact path patterns ---
// SYNC: mirrored from supekku/claude.hooks/artifact_event.py
//       see mem.artifact-pattern-sync

const ARTIFACT_PATTERNS: [RegExp, string][] = [
  [/\.spec-driver\/deltas\/(DE-\d+)[^/]*\/phases\//, "phase"],
  [/\.spec-driver\/deltas\/(DE-\d+)[^/]*\/DR-\d+/, "design_revision"],
  [/\.spec-driver\/deltas\/(DE-\d+)[^/]*\/IP-\d+/, "plan"],
  [/\.spec-driver\/deltas\/(DE-\d+)/, "delta"],
  [/\.spec-driver\/tech\/(SPEC-\d+)/, "spec"],
  [/\.spec-driver\/decisions\/(ADR-\d+)/, "adr"],
  [/\.spec-driver\/revisions\/(RE-\d+)/, "revision"],
  [/\.spec-driver\/audits\/(AUD-\d+)/, "audit"],
  [/\.spec-driver\/backlog\//, "backlog"],
  [/\.spec-driver\/product\/(PROD-\d+)/, "product_spec"],
  [/\.spec-driver\/policies\/(POL-\d+)/, "policy"],
  [/\.spec-driver\/standards\/(STD-\d+)/, "standard"],
];

const TOOL_TO_ACTION: Record<string, string> = {
  read: "read",
  edit: "edit",
  write: "write",
};

const EVENT_SCHEMA_VERSION = 1;
const LOG_FILENAME = "events.jsonl";
const SOCKET_FILENAME = "tui.sock";
const MAX_SOCKET_PATH_LEN = 104;

// --- Pure functions ---

export function classifyPath(filePath: string): [string, string | null] | null {
  for (const [pattern, artifactType] of ARTIFACT_PATTERNS) {
    const m = pattern.exec(filePath);
    if (m) {
      return [artifactType, m[1] ?? null];
    }
  }
  return null;
}

export function buildEvent(opts: {
  toolName: string;
  filePath: string;
  artifactType: string;
  artifactId: string | null;
  cwd: string;
}): Record<string, unknown> {
  const action = TOOL_TO_ACTION[opts.toolName] ?? opts.toolName;
  let relPath: string;
  try {
    relPath = relative(opts.cwd, opts.filePath);
  } catch {
    relPath = opts.filePath;
  }

  return {
    v: EVENT_SCHEMA_VERSION,
    ts: new Date().toISOString(),
    session: null,
    cmd: `artifact.${action}`,
    argv: [`artifact.${action}`, relPath],
    artifacts: opts.artifactId ? [opts.artifactId] : [],
    exit_code: 0,
    status: "ok",
    artifact_type: opts.artifactType,
  };
}

export function writeLog(event: Record<string, unknown>, runDir: string): void {
  mkdirSync(runDir, { recursive: true });
  const line = JSON.stringify(event) + "\n";
  appendFileSync(join(runDir, LOG_FILENAME), line, "utf-8");
}

/**
 * Send a JSON datagram to the TUI Unix socket via python3.
 *
 * Node.js dgram lacks AF_UNIX support, so we shell out to Python.
 * Async, fire-and-forget — errors are silently ignored.
 */
export function sendSocket(
  event: Record<string, unknown>,
  runDir: string,
  pi: ExtensionAPI,
): void {
  const sockPath = join(runDir, SOCKET_FILENAME);
  if (sockPath.length > MAX_SOCKET_PATH_LEN) return;

  const data = JSON.stringify(event);
  // One-liner: open AF_UNIX DGRAM socket, send, close.
  const script =
    "import socket,sys;" +
    "s=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM);" +
    "s.sendto(sys.argv[1].encode(),sys.argv[2]);" +
    "s.close()";

  // Fire-and-forget — don't await, don't check result
  pi.exec("python3", ["-c", script, data, sockPath]).catch(() => {});
}

// --- Extension entry point ---

const extension: ExtensionFactory = (pi) => {
  pi.on("tool_result", (event, ctx) => {
    try {
      const action = TOOL_TO_ACTION[event.toolName];
      if (!action) return;

      const filePath = (event.input as Record<string, unknown>).path;
      if (typeof filePath !== "string" || !filePath) return;

      const classification = classifyPath(filePath);
      if (!classification) return;

      const [artifactType, artifactId] = classification;
      const ev = buildEvent({
        toolName: event.toolName,
        filePath,
        artifactType,
        artifactId,
        cwd: ctx.cwd,
      });

      const runDir = join(ctx.cwd, ".spec-driver", "run");
      writeLog(ev, runDir);
      sendSocket(ev, runDir, pi);
    } catch {
      /* fail-silent: never interfere with pi operation (DEC-094-02) */
    }
  });
};

export default extension;
