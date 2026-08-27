/**
 * Tenki Sandbox → DETERMINISTIC_TOOL_OUTPUT sponsor adapter.
 * Prefer authenticated `tenki` CLI; never print TENKI_API_KEY.
 * Docs: https://tenki.cloud/docs  |  Sandbox: https://tenki.cloud/docs/sandbox/quickstart
 * Tenki is sponsor/infra demo only — not scientific execution authority.
 */
import { createHash } from "node:crypto";
import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { loadHydraLampServerEnv } from "../hydralamp/env";

export const TENKI_DOCS = "https://tenki.cloud/docs";
export const TENKI_SANDBOX_DOCS = "https://tenki.cloud/docs/sandbox/quickstart";

function sha256Bytes(data: Buffer | string): string {
  return createHash("sha256").update(data).digest("hex");
}

function redact(text: string): string {
  return text
    .replace(/tk_[A-Za-z0-9_-]+/g, "tk_REDACTED")
    .replace(/TENKI_API_KEY=\S+/g, "TENKI_API_KEY=REDACTED");
}

function tenkiBin(): string {
  const r = spawnSync("command", ["-v", "tenki"], {
    encoding: "utf8",
    shell: true,
    env: {
      ...process.env,
      PATH: `${process.env.HOME}/.local/bin:${process.env.PATH || ""}`,
    },
  });
  const p = (r.stdout || "").trim();
  return p || "tenki";
}

export function tenkiCliStatus(): "PRESENT" | "MISSING" {
  const bin = tenkiBin();
  if (bin === "tenki") {
    const r = spawnSync("tenki", ["--version"], {
      encoding: "utf8",
      env: {
        ...process.env,
        PATH: `${process.env.HOME}/.local/bin:${process.env.PATH || ""}`,
      },
    });
    return r.status === 0 ? "PRESENT" : "MISSING";
  }
  return "PRESENT";
}

function isPlaceholder(value: string | undefined): boolean {
  if (!value) return true;
  const v = value.trim();
  if (!v) return true;
  if (/^tk_your/i.test(v)) return true;
  if (/^your_.*_here$/i.test(v)) return true;
  return false;
}

export function tenkiApiKeyStatus(): "PRESENT" | "MISSING" {
  loadHydraLampServerEnv();
  return isPlaceholder(process.env.TENKI_API_KEY) ? "MISSING" : "PRESENT";
}

export function tenkiAuthState(): "PASS" | "FAIL" {
  if (tenkiCliStatus() === "MISSING") return "FAIL";
  const r = spawnSync(tenkiBin(), ["status"], {
    encoding: "utf8",
    timeout: 60_000,
    env: {
      ...process.env,
      PATH: `${process.env.HOME}/.local/bin:${process.env.PATH || ""}`,
    },
  });
  const out = `${r.stdout || ""}\n${r.stderr || ""}`;
  if (/Logged out|not logged|Status\s*:\s*Logged out/i.test(out)) return "FAIL";
  if (r.status === 0 && /Logged in|Status\s*:\s*Logged/i.test(out)) return "PASS";
  // Some versions print "Status : Logged in"
  if (r.status === 0 && !/Logged out/i.test(out) && /API Endpoint/i.test(out)) {
    // Ambiguous — treat missing login as FAIL if "Logged out" not seen but session absent
    if (/Session\s*:\s*<not set>/i.test(out) && /Logged out/i.test(out)) return "FAIL";
  }
  return /Logged out/i.test(out) ? "FAIL" : r.status === 0 ? "PASS" : "FAIL";
}

export type TenkiSandboxMissionReceipt = {
  schema: "sponsor.tenki.sandbox_mission_receipt.v1";
  mission_id: "ANB-SP-TENKI-SANDBOX-001";
  provider: "Tenki";
  operation: "sandbox_create_exec_terminate";
  docs_ref: string;
  sandbox_docs_ref: string;
  scientific_execution_authority: "magicSTUDIObox.local";
  tenki_cli: "PRESENT" | "MISSING";
  TENKI_API_KEY: "PRESENT" | "MISSING";
  auth_state: "PASS" | "FAIL";
  session_id: string | null;
  exec: {
    attempted: boolean;
    command: string[];
    exit_code: number | null;
    stdout_sha256: string | null;
    raw_artifact_path: string | null;
  };
  terminate: {
    attempted: boolean;
    exit_code: number | null;
  };
  fcg_append: "NOT_APPENDED";
  status: "PASS" | "ERROR" | "BLOCKED" | "TIMEOUT" | "SKIPPED";
  error_code: string | null;
  error_summary: string | null;
  claim_ceiling: "DETERMINISTIC_TOOL_OUTPUT";
  signature_state: "NOT_SIGNED";
  recorded_at_utc: string;
};

function runTenki(
  args: string[],
  timeoutMs = 180_000,
): { status: number | null; stdout: string; stderr: string; timedOut: boolean } {
  const child = spawnSync(tenkiBin(), args, {
    encoding: "utf8",
    timeout: timeoutMs,
    maxBuffer: 4 * 1024 * 1024,
    env: {
      ...process.env,
      PATH: `${process.env.HOME}/.local/bin:${process.env.PATH || ""}`,
    },
  });
  const timedOut =
    Boolean(child.error) &&
    (child.error as NodeJS.ErrnoException).code === "ETIMEDOUT";
  return {
    status: child.status,
    stdout: redact(child.stdout || ""),
    stderr: redact(child.stderr || ""),
    timedOut,
  };
}

export function runTenkiSandboxMission(params: {
  repoRoot: string;
}): TenkiSandboxMissionReceipt {
  const recorded_at_utc = new Date().toISOString();
  const outDir = path.join(
    params.repoRoot,
    "eval",
    "agent_native_sponsors_20260827",
    "tenki",
  );
  mkdirSync(path.join(outDir, "raw"), { recursive: true });

  const base = {
    schema: "sponsor.tenki.sandbox_mission_receipt.v1" as const,
    mission_id: "ANB-SP-TENKI-SANDBOX-001" as const,
    provider: "Tenki" as const,
    operation: "sandbox_create_exec_terminate" as const,
    docs_ref: TENKI_DOCS,
    sandbox_docs_ref: TENKI_SANDBOX_DOCS,
    scientific_execution_authority: "magicSTUDIObox.local" as const,
    tenki_cli: tenkiCliStatus(),
    TENKI_API_KEY: tenkiApiKeyStatus(),
    fcg_append: "NOT_APPENDED" as const,
    claim_ceiling: "DETERMINISTIC_TOOL_OUTPUT" as const,
    signature_state: "NOT_SIGNED" as const,
    recorded_at_utc,
  };

  const writeReceipt = (body: TenkiSandboxMissionReceipt) => {
    writeFileSync(
      path.join(outDir, "TENKI_SANDBOX_MISSION_RECEIPT.json"),
      JSON.stringify(body, null, 2) + "\n",
    );
    writeFileSync(
      path.join(outDir, "TENKI_MISSION_RECEIPT.json"),
      JSON.stringify(
        {
          schema: "sponsor.tenki.mission_receipt.v1",
          mission_id: body.mission_id,
          provider: body.provider,
          operation: body.operation,
          status: body.status,
          discovery_state:
            body.status === "PASS"
              ? "CONFIGURED"
              : body.status === "BLOCKED"
                ? "DEFERRED_NONBLOCKING"
                : "ERROR",
          note: body.error_summary,
          claim_ceiling: body.claim_ceiling,
          signature_state: body.signature_state,
          sandbox_receipt_path:
            "eval/agent_native_sponsors_20260827/tenki/TENKI_SANDBOX_MISSION_RECEIPT.json",
          scientific_execution_authority: body.scientific_execution_authority,
          fcg_append: "NOT_APPENDED",
        },
        null,
        2,
      ) + "\n",
    );
    return body;
  };

  if (base.tenki_cli === "MISSING") {
    return writeReceipt({
      ...base,
      auth_state: "FAIL",
      session_id: null,
      exec: {
        attempted: false,
        command: [],
        exit_code: null,
        stdout_sha256: null,
        raw_artifact_path: null,
      },
      terminate: { attempted: false, exit_code: null },
      status: "BLOCKED",
      error_code: "TENKI_CLI_MISSING",
      error_summary: "tenki CLI not on PATH; install via https://tenki.cloud/install.sh",
    });
  }

  const auth = tenkiAuthState();
  if (auth !== "PASS" && base.TENKI_API_KEY === "MISSING") {
    return writeReceipt({
      ...base,
      auth_state: auth,
      session_id: null,
      exec: {
        attempted: false,
        command: [],
        exit_code: null,
        stdout_sha256: null,
        raw_artifact_path: null,
      },
      terminate: { attempted: false, exit_code: null },
      status: "BLOCKED",
      error_code: "TENKI_AUTH_MISSING",
      error_summary:
        "Run `tenki login` or set TENKI_API_KEY=tk_... then re-run npm run sponsor:tenki",
    });
  }

  // If API key present but CLI logged out, try non-interactive login
  if (auth !== "PASS" && base.TENKI_API_KEY === "PRESENT") {
    const login = runTenki(["login", "--api-key", process.env.TENKI_API_KEY || ""]);
    if (login.status !== 0 && tenkiAuthState() !== "PASS") {
      return writeReceipt({
        ...base,
        auth_state: "FAIL",
        session_id: null,
        exec: {
          attempted: false,
          command: [],
          exit_code: null,
          stdout_sha256: null,
          raw_artifact_path: null,
        },
        terminate: { attempted: false, exit_code: null },
        status: "ERROR",
        error_code: "TENKI_LOGIN_FAILED",
        error_summary: "tenki login --api-key failed (details redacted)",
      });
    }
  }

  const name = `hydradg-sponsor-${Date.now().toString(36)}`;
  const create = runTenki([
    "sandbox",
    "create",
    "--name",
    name,
    "--json",
    "--max-duration",
    "10m",
    "--idle-timeout",
    "5m",
  ]);
  if (create.timedOut) {
    return writeReceipt({
      ...base,
      auth_state: "PASS",
      session_id: null,
      exec: {
        attempted: false,
        command: [],
        exit_code: null,
        stdout_sha256: null,
        raw_artifact_path: null,
      },
      terminate: { attempted: false, exit_code: null },
      status: "TIMEOUT",
      error_code: "TENKI_CREATE_TIMEOUT",
      error_summary: "tenki sandbox create timed out",
    });
  }

  writeFileSync(
    path.join(outDir, "raw", "TENKI_CREATE_RAW.json"),
    JSON.stringify({ exit_code: create.status, stdout: create.stdout, stderr: create.stderr }, null, 2) +
      "\n",
  );

  let sessionId: string | null = null;
  try {
    const j = JSON.parse(create.stdout);
    sessionId = j.id || j.session_id || j.sessionId || null;
  } catch {
    const m = create.stdout.match(/[a-z0-9-]{8,}/i);
    sessionId = m ? m[0] : name;
  }

  if (create.status !== 0 || !sessionId) {
    return writeReceipt({
      ...base,
      auth_state: "PASS",
      session_id: sessionId,
      exec: {
        attempted: false,
        command: [],
        exit_code: null,
        stdout_sha256: null,
        raw_artifact_path: null,
      },
      terminate: { attempted: false, exit_code: null },
      status: "ERROR",
      error_code: "TENKI_CREATE_FAILED",
      error_summary: `sandbox create exit=${create.status}`,
    });
  }

  const execCmd = ["sandbox", "exec", "--session", sessionId, "-c", "uname -a && echo HYDRADG_TENKI_OK"];
  const exec = runTenki(execCmd, 120_000);
  const execRaw = path.join(outDir, "raw", "TENKI_EXEC_RAW.json");
  writeFileSync(
    execRaw,
    JSON.stringify({ exit_code: exec.status, stdout: exec.stdout, stderr: exec.stderr }, null, 2) +
      "\n",
  );

  const term = runTenki(["sandbox", "terminate", sessionId, "--json"], 120_000);

  const ok =
    exec.status === 0 &&
    /HYDRADG_TENKI_OK/.test(exec.stdout) &&
    !exec.timedOut;

  return writeReceipt({
    ...base,
    auth_state: "PASS",
    session_id: sessionId,
    exec: {
      attempted: true,
      command: ["tenki", ...execCmd],
      exit_code: exec.status,
      stdout_sha256: sha256Bytes(exec.stdout),
      raw_artifact_path: path.relative(params.repoRoot, execRaw),
    },
    terminate: { attempted: true, exit_code: term.status },
    status: exec.timedOut ? "TIMEOUT" : ok ? "PASS" : "ERROR",
    error_code: ok ? null : exec.timedOut ? "TENKI_EXEC_TIMEOUT" : "TENKI_EXEC_FAILED",
    error_summary: ok
      ? null
      : `exec exit=${exec.status}; terminate exit=${term.status}`,
  });
}
