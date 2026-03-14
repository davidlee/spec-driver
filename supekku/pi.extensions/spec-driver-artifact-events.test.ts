/**
 * Tests for spec-driver-artifact-events.ts (DE-094).
 *
 * Ported from supekku/claude.hooks/artifact_event_test.py.
 * Run: node --experimental-strip-types supekku/pi.extensions/spec-driver-artifact-events.test.ts
 */
import { classifyPath, buildEvent, writeLog, sendSocket } from "./spec-driver-artifact-events.ts";
import { readFileSync, mkdtempSync, rmSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { strict as assert } from "node:assert";

let passed = 0;
let failed = 0;

function test(name: string, fn: () => void): void {
  try {
    fn();
    passed++;
  } catch (e: unknown) {
    failed++;
    const msg = e instanceof Error ? e.message : String(e);
    console.error(`  FAIL: ${name}\n    ${msg}`);
  }
}

// --- classifyPath ---

const CLASSIFY_CASES: [string, string, string | null][] = [
  ["/proj/.spec-driver/deltas/DE-060-slug/DE-060.md", "delta", "DE-060"],
  [".spec-driver/deltas/DE-001-foo/notes.md", "delta", "DE-001"],
  ["/proj/.spec-driver/deltas/DE-060-slug/DR-060.md", "design_revision", "DE-060"],
  ["/proj/.spec-driver/deltas/DE-060-slug/IP-060.md", "plan", "DE-060"],
  ["/proj/.spec-driver/deltas/DE-060-slug/phases/phase-01.md", "phase", "DE-060"],
  ["/proj/.spec-driver/tech/SPEC-042/SPEC-042.md", "spec", "SPEC-042"],
  ["/proj/.spec-driver/decisions/ADR-007-some-decision.md", "adr", "ADR-007"],
  ["/proj/.spec-driver/revisions/RE-003.md", "revision", "RE-003"],
  ["/proj/.spec-driver/audits/AUD-001.md", "audit", "AUD-001"],
  ["/proj/.spec-driver/backlog/issues/ISSUE-042.md", "backlog", null],
  ["/proj/.spec-driver/product/PROD-001/PROD-001.md", "product_spec", "PROD-001"],
  ["/proj/.spec-driver/policies/POL-001.md", "policy", "POL-001"],
  ["/proj/.spec-driver/standards/STD-002.md", "standard", "STD-002"],
];

console.log("classifyPath — artifact paths");
for (const [path, expectedType, expectedId] of CLASSIFY_CASES) {
  test(`classifies ${expectedType} (${expectedId ?? "no id"})`, () => {
    const result = classifyPath(path);
    assert.notEqual(result, null, `Expected classification for ${path}`);
    const [type, id] = result!;
    assert.equal(type, expectedType);
    assert.equal(id, expectedId);
  });
}

test("phase before generic delta", () => {
  const result = classifyPath("/proj/.spec-driver/deltas/DE-060-slug/phases/phase-01.md");
  assert.notEqual(result, null);
  assert.equal(result![0], "phase");
});

test("DR before generic delta", () => {
  const result = classifyPath("/proj/.spec-driver/deltas/DE-060-slug/DR-060.md");
  assert.notEqual(result, null);
  assert.equal(result![0], "design_revision");
});

console.log("classifyPath — non-artifact paths");
const NON_ARTIFACT_PATHS = [
  "/proj/supekku/cli/app.py",
  "/proj/README.md",
  "/proj/pyproject.toml",
  "/proj/supekku/tui/track.py",
  "/proj/.claude/settings.json",
  "/proj/tests/test_something.py",
  "",
];

for (const path of NON_ARTIFACT_PATHS) {
  test(`returns null for "${path || "(empty)"}"`, () => {
    assert.equal(classifyPath(path), null);
  });
}

// --- buildEvent ---

console.log("buildEvent — schema");

test("produces valid v1 event", () => {
  const event = buildEvent({
    toolName: "edit",
    filePath: "/proj/.spec-driver/deltas/DE-060-slug/DE-060.md",
    artifactType: "delta",
    artifactId: "DE-060",
    cwd: "/proj",
  });
  assert.equal(event.v, 1);
  assert.equal(event.session, null);
  assert.equal(event.cmd, "artifact.edit");
  assert.deepEqual(event.artifacts, ["DE-060"]);
  assert.equal(event.exit_code, 0);
  assert.equal(event.status, "ok");
  assert.equal(event.artifact_type, "delta");
  assert.ok(typeof event.ts === "string");
  const argv = event.argv as string[];
  assert.equal(argv.length, 2);
  assert.equal(argv[0], "artifact.edit");
});

test("read action", () => {
  const event = buildEvent({
    toolName: "read",
    filePath: "/proj/.spec-driver/tech/SPEC-042/SPEC-042.md",
    artifactType: "spec",
    artifactId: "SPEC-042",
    cwd: "/proj",
  });
  assert.equal(event.cmd, "artifact.read");
});

test("write action", () => {
  const event = buildEvent({
    toolName: "write",
    filePath: "/proj/.spec-driver/decisions/ADR-007.md",
    artifactType: "adr",
    artifactId: "ADR-007",
    cwd: "/proj",
  });
  assert.equal(event.cmd, "artifact.write");
});

test("no artifact id", () => {
  const event = buildEvent({
    toolName: "read",
    filePath: "/proj/.spec-driver/backlog/issues/ISSUE-042.md",
    artifactType: "backlog",
    artifactId: null,
    cwd: "/proj",
  });
  assert.deepEqual(event.artifacts, []);
});

test("cwd used for relativization", () => {
  const event = buildEvent({
    toolName: "read",
    filePath: "/proj/.spec-driver/deltas/DE-061-slug/DE-061.md",
    artifactType: "delta",
    artifactId: "DE-061",
    cwd: "/proj",
  });
  assert.equal((event.argv as string[])[1], ".spec-driver/deltas/DE-061-slug/DE-061.md");
});

// --- writeLog ---

console.log("writeLog — JSONL append");

test("appends JSONL lines", () => {
  const tmp = mkdtempSync(join(tmpdir(), "artifact-events-test-"));
  try {
    const runDir = join(tmp, "run");
    const event = { v: 1, cmd: "artifact.read", ts: "now" };

    writeLog(event, runDir);
    writeLog(event, runDir);

    const logPath = join(runDir, "events.jsonl");
    const lines = readFileSync(logPath, "utf-8").trim().split("\n");
    assert.equal(lines.length, 2);
    for (const line of lines) {
      const parsed = JSON.parse(line);
      assert.equal(parsed.v, 1);
    }
  } finally {
    rmSync(tmp, { recursive: true });
  }
});

test("creates run dir recursively", () => {
  const tmp = mkdtempSync(join(tmpdir(), "artifact-events-test-"));
  try {
    const runDir = join(tmp, "deep", "nested", "run");
    writeLog({ v: 1 }, runDir);
    const content = readFileSync(join(runDir, "events.jsonl"), "utf-8");
    assert.ok(content.includes('"v":1'));
  } finally {
    rmSync(tmp, { recursive: true });
  }
});

// --- sendSocket ---

console.log("sendSocket — pi.exec delegation");

test("calls pi.exec with python3 dgram script", () => {
  const calls: { cmd: string; args: string[] }[] = [];
  const mockPi = {
    exec(cmd: string, args: string[]) {
      calls.push({ cmd, args });
      return Promise.resolve({ exitCode: 0, stdout: "", stderr: "" });
    },
  };

  const event = { v: 1, cmd: "artifact.read" };
  sendSocket(event, "/proj/.spec-driver/run", mockPi as any);

  assert.equal(calls.length, 1);
  assert.equal(calls[0].cmd, "python3");
  assert.equal(calls[0].args[0], "-c");
  // Script should contain AF_UNIX and SOCK_DGRAM
  assert.ok(calls[0].args[1].includes("AF_UNIX"));
  assert.ok(calls[0].args[1].includes("SOCK_DGRAM"));
  // Data and socket path passed as args
  assert.equal(calls[0].args[2], JSON.stringify(event));
  assert.equal(calls[0].args[3], "/proj/.spec-driver/run/tui.sock");
});

test("skips when socket path exceeds max length", () => {
  const calls: unknown[] = [];
  const mockPi = {
    exec(...args: unknown[]) {
      calls.push(args);
      return Promise.resolve({ exitCode: 0, stdout: "", stderr: "" });
    },
  };

  const longDir = "/proj/" + "a".repeat(120) + "/.spec-driver/run";
  sendSocket({ v: 1 }, longDir, mockPi as any);

  assert.equal(calls.length, 0);
});

// --- Summary ---

console.log(`\n${passed + failed} tests: ${passed} passed, ${failed} failed`);
if (failed > 0) process.exit(1);
