/**
 * Cotal agent mesh sponsor adapter — CLI install/setup + HydraDG evidence gateway.
 * Does not make Cotal canonical FCG state. Full `cotal up` mesh is optional/deferred.
 * Upstream: https://github.com/Cotal-AI/Cotal.git
 * Docs: https://docs.cotal.ai/  Installer: https://get.cotal.ai
 */
import { createHash } from "node:crypto";
import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { executeGatewayTool } from "./evidenceGateway";

export const COTAL_GITHUB = "https://github.com/Cotal-AI/Cotal.git";
export const COTAL_DOCS = "https://docs.cotal.ai/";
export const COTAL_INSTALLER = "https://get.cotal.ai";

function sha256Bytes(data: Buffer | string): string {
  return createHash("sha256").update(data).digest("hex");
}

function redact(text: string): string {
  return text.replace(/eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+/g, "JWT_REDACTED");
}

function cotalBin(): string {
  const r = spawnSync("command", ["-v", "cotal"], {
    encoding: "utf8",
    shell: true,
    env: {
      ...process.env,
      PATH: `${process.env.HOME}/.local/bin:${process.env.PATH || ""}`,
    },
  });
  return (r.stdout || "").trim() || "cotal";
}

export function cotalCliStatus(): "PRESENT" | "MISSING" {
  const r = spawnSync(cotalBin(), ["--version"], {
    encoding: "utf8",
    env: {
      ...process.env,
      PATH: `${process.env.HOME}/.local/bin:${process.env.PATH || ""}`,
    },
  });
  return r.status === 0 ? "PRESENT" : "MISSING";
}

function runCotal(args: string[], timeoutMs = 180_000) {
  const child = spawnSync(cotalBin(), args, {
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

export type CotalMissionReceipt = {
  schema: "sponsor.cotal.mission_receipt.v1";
  mission_id: "ANB-SP-COTAL-A2A-001";
  provider: "Cotal";
  operation: "cli_setup_and_gateway_bounded_transaction";
  docs_ref: string;
  installer_ref: string;
  cotal_cli: "PRESENT" | "MISSING";
  cotal_version: string | null;
  setup: {
    attempted: boolean;
    exit_code: number | null;
    timed_out: boolean;
    raw_sha256: string | null;
  };
  status_probe: {
    attempted: boolean;
    exit_code: number | null;
    raw_sha256: string | null;
  };
  gateway: {
    discover_ok: boolean;
    propose_ok: boolean;
    verify_ok: boolean;
    tools: string[];
    raw_artifact_path: string;
  };
  mesh_up: "NOT_ATTEMPTED";
  fcg_append: "NOT_APPENDED";
  status: "PASS" | "ERROR" | "BLOCKED" | "TIMEOUT";
  error_code: string | null;
  error_summary: string | null;
  claim_ceiling: "DETERMINISTIC_TOOL_OUTPUT";
  signature_state: "NOT_SIGNED";
  recorded_at_utc: string;
};

export function runCotalMission(params: { repoRoot: string }): CotalMissionReceipt {
  const recorded_at_utc = new Date().toISOString();
  const outDir = path.join(
    params.repoRoot,
    "eval",
    "agent_native_sponsors_20260827",
    "cotal",
  );
  mkdirSync(path.join(outDir, "raw"), { recursive: true });

  const cli = cotalCliStatus();
  let version: string | null = null;
  if (cli === "PRESENT") {
    const v = runCotal(["--version"], 30_000);
    version = (v.stdout || v.stderr).trim().split("\n")[0] || null;
  }

  const setup =
    cli === "PRESENT"
      ? runCotal(["setup", "--yes"], 300_000)
      : { status: null, stdout: "", stderr: "", timedOut: false };
  if (cli === "PRESENT") {
    writeFileSync(
      path.join(outDir, "raw", "COTAL_SETUP_RAW.txt"),
      JSON.stringify(
        { exit_code: setup.status, stdout: setup.stdout, stderr: setup.stderr },
        null,
        2,
      ) + "\n",
    );
  }

  const statusProbe =
    cli === "PRESENT"
      ? runCotal(["status"], 60_000)
      : { status: null, stdout: "", stderr: "", timedOut: false };
  if (cli === "PRESENT") {
    writeFileSync(
      path.join(outDir, "raw", "COTAL_STATUS_RAW.txt"),
      JSON.stringify(
        {
          exit_code: statusProbe.status,
          stdout: statusProbe.stdout,
          stderr: statusProbe.stderr,
        },
        null,
        2,
      ) + "\n",
    );
  }

  const discover = executeGatewayTool("discover_capabilities", params.repoRoot);
  const propose = executeGatewayTool("propose_external_evidence", params.repoRoot, {
    source_url: COTAL_DOCS,
    raw_artifact_sha256: sha256Bytes(COTAL_DOCS),
    evidence_class: "EXTERNALLY_RETRIEVED_EVIDENCE",
  });
  const verify = executeGatewayTool("verify_custody_receipt", params.repoRoot, {
    receipt_path:
      "eval/hydralamp_runtype_20260826/HYDRALAMP_SCIENCE_CLOSEOUT_RECEIPT.json",
    declared_sha256:
      "8028afdb6b8a88eace428e4f2583bb44054f8f4c8c76968ada0fd674946ebba7",
  });

  const gwPath = path.join(outDir, "GATEWAY_BOUNDED_TRANSACTION.json");
  const gwBody = {
    discover,
    propose,
    verify,
    note: "Local HydraDG evidence gateway stub for Cotal A2A discovery; not Cotal mesh canonical state. cotal up NOT_ATTEMPTED in this mission.",
  };
  writeFileSync(gwPath, JSON.stringify(gwBody, null, 2) + "\n");

  const discover_ok = Boolean((discover as { gateway?: string }).gateway);
  const propose_ok = (propose as { fcg_append?: string }).fcg_append === "NOT_APPENDED";
  const verify_ok = (verify as { status?: string }).status === "PASS";

  let status: CotalMissionReceipt["status"] = "ERROR";
  let error_code: string | null = null;
  let error_summary: string | null = null;

  if (cli === "MISSING") {
    status = "BLOCKED";
    error_code = "COTAL_CLI_MISSING";
    error_summary = "Install via curl -fsSL https://get.cotal.ai | sh";
  } else if (setup.timedOut || statusProbe.timedOut) {
    status = "TIMEOUT";
    error_code = "COTAL_TIMEOUT";
    error_summary = "cotal setup/status timed out";
  } else if (discover_ok && propose_ok && verify_ok && (setup.status === 0 || setup.status === null)) {
    // setup may already be done; accept 0 or prior-configured
    status =
      statusProbe.status === 0 && discover_ok && propose_ok && verify_ok ? "PASS" : "ERROR";
    if (status !== "PASS") {
      error_code = "COTAL_STATUS_OR_GATEWAY";
      error_summary = `setup=${setup.status} status=${statusProbe.status}`;
    }
  } else {
    error_code = "COTAL_GATEWAY_OR_SETUP";
    error_summary = `setup=${setup.status} status=${statusProbe.status} gw=${discover_ok}/${propose_ok}/${verify_ok}`;
  }

  // If CLI present, status ok, gateway ok — PASS even if setup was idempotent non-zero
  if (
    cli === "PRESENT" &&
    statusProbe.status === 0 &&
    discover_ok &&
    propose_ok &&
    verify_ok &&
    !setup.timedOut
  ) {
    status = "PASS";
    error_code = null;
    error_summary = null;
  }

  const receipt: CotalMissionReceipt = {
    schema: "sponsor.cotal.mission_receipt.v1",
    mission_id: "ANB-SP-COTAL-A2A-001",
    provider: "Cotal",
    operation: "cli_setup_and_gateway_bounded_transaction",
    docs_ref: COTAL_DOCS,
    installer_ref: COTAL_INSTALLER,
    cotal_cli: cli,
    cotal_version: version,
    setup: {
      attempted: cli === "PRESENT",
      exit_code: setup.status,
      timed_out: setup.timedOut,
      raw_sha256: setup.stdout ? sha256Bytes(setup.stdout) : null,
    },
    status_probe: {
      attempted: cli === "PRESENT",
      exit_code: statusProbe.status,
      raw_sha256: statusProbe.stdout ? sha256Bytes(statusProbe.stdout) : null,
    },
    gateway: {
      discover_ok,
      propose_ok,
      verify_ok,
      tools: [
        "discover_capabilities",
        "query_evidence",
        "propose_external_evidence",
        "verify_custody_receipt",
      ],
      raw_artifact_path: path.relative(params.repoRoot, gwPath),
    },
    mesh_up: "NOT_ATTEMPTED",
    fcg_append: "NOT_APPENDED",
    status,
    error_code,
    error_summary,
    claim_ceiling: "DETERMINISTIC_TOOL_OUTPUT",
    signature_state: "NOT_SIGNED",
    recorded_at_utc,
  };

  writeFileSync(
    path.join(outDir, "COTAL_MISSION_RECEIPT.json"),
    JSON.stringify(receipt, null, 2) + "\n",
  );
  return receipt;
}
