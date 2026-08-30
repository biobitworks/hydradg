/**
 * Mitosis Cortex → EXTERNALLY_RETRIEVED_EVIDENCE adapter.
 * Uses authenticated `mi` CLI session; never prints or persists API keys.
 * Cortex is external noncanonical memory — never mutates FCG.
 */
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { verifyCustodyReceipt } from "./evidenceGateway";

export const PUBLIC_SAFE_RECEIPT_REL =
  "eval/hydralamp_runtype_20260826/HYDRALAMP_SCIENCE_CLOSEOUT_RECEIPT.json";

export type CortexRoundtripOutcome =
  | "PASS"
  | "MISS"
  | "STALE"
  | "CONTRADICTORY"
  | "ERROR"
  | "TIMEOUT"
  | "ABSTAIN"
  | "BLOCKED"
  | "NOT_ATTEMPTED";

export type CortexMemoryRoundtripReceipt = {
  schema: "sponsor.cortex.memory_roundtrip_receipt.v1";
  mission_id: "ANB-SP-CORTEX-ROUNDTRIP-001";
  provider: "Mitosis Cortex";
  operation: "memory_roundtrip";
  recorded_at_utc: string;
  execution_host: string;
  offer_code_metadata: "FREECORTEX";
  offer_is_api_credential: false;
  architectural_boundary: string;
  docs_ref: string;
  office_id: string | null;
  auth_state: "PASS" | "FAIL";
  underlying_receipt_ref: string;
  underlying_receipt_sha256: string | null;
  remember: {
    attempted: boolean;
    command: string[];
    exit_code: number | null;
    timed_out: boolean;
    raw_stdout_sha256: string | null;
    raw_stderr_sha256: string | null;
    raw_artifact_path: string | null;
    note: string;
  };
  ask: {
    attempted: boolean;
    command: string[];
    exit_code: number | null;
    timed_out: boolean;
    raw_response_sha256: string | null;
    raw_artifact_path: string | null;
    recovered_receipt_ref: string | null;
    recovery_state: CortexRoundtripOutcome;
  };
  hydradg_verify: ReturnType<typeof verifyCustodyReceipt> & {
    recovered_ref_used: string | null;
  };
  CORTEX_MEMORY_ROUNDTRIP: CortexRoundtripOutcome;
  HYDRADG_RECEIPT_VERIFICATION: CortexRoundtripOutcome;
  fcg_append: "NOT_APPENDED";
  status: "PASS" | "ERROR" | "BLOCKED" | "TIMEOUT" | "ABSTAIN";
  error_code: string | null;
  error_summary: string | null;
  claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE";
  secret_state: "PRESENT" | "MISSING" | "BLOCKED" | "NOT_APPLICABLE";
  signature_state: "NOT_SIGNED";
};

function sha256Bytes(data: Buffer | string): string {
  return createHash("sha256").update(data).digest("hex");
}

function redactSecrets(text: string): string {
  return text
    .replace(/mi_[0-9a-fA-F]{16,}/g, "mi_REDACTED")
    .replace(/dtn_[A-Za-z0-9]+/g, "dtn_REDACTED")
    .replace(/sk_live_[A-Za-z0-9._-]+/g, "sk_live_REDACTED")
    .replace(/rt_[A-Za-z0-9_]+/g, "rt_REDACTED");
}

export function miCliStatus(): "PRESENT" | "MISSING" {
  const r = spawnSync("command", ["-v", "mi"], { encoding: "utf8", shell: true });
  return r.status === 0 ? "PRESENT" : "MISSING";
}

export function resolveMitosisOfficeId(): string | null {
  const fromEnv =
    process.env.MITOSIS_OFFICE_ID?.trim() ||
    process.env.MI_OFFICE_ID?.trim() ||
    process.env.OFFICE_ID?.trim() ||
    "";
  if (fromEnv && /^[0-9a-f-]{36}$/i.test(fromEnv)) return fromEnv;

  if (miCliStatus() === "MISSING") return fromEnv || null;

  const listed = spawnSync("mi", ["offices", "list"], {
    encoding: "utf8",
    timeout: 60_000,
    maxBuffer: 2 * 1024 * 1024,
  });
  if (listed.status !== 0 || !listed.stdout) {
    // Name-like env fallback only if UUID list fails
    return fromEnv || null;
  }
  try {
    const arr = JSON.parse(listed.stdout) as Array<{ id?: string; name?: string }>;
    if (fromEnv) {
      const byName = arr.find((o) => o.name === fromEnv || o.id === fromEnv);
      if (byName?.id) return byName.id;
    }
    return arr[0]?.id || null;
  } catch {
    return fromEnv || null;
  }
}

export function mitosisAuthState(): "PASS" | "FAIL" {
  if (miCliStatus() === "MISSING") return "FAIL";
  const r = spawnSync("mi", ["whoami"], {
    encoding: "utf8",
    timeout: 60_000,
    maxBuffer: 1024 * 1024,
  });
  const out = `${r.stdout || ""}\n${r.stderr || ""}`;
  if (r.status === 0 && /Logged in as/i.test(out) && !/Not logged in/i.test(out)) {
    return "PASS";
  }
  return "FAIL";
}

function extractReceiptRef(text: string): string | null {
  const needle = PUBLIC_SAFE_RECEIPT_REL;
  if (text.includes(needle)) return needle;
  const m = text.match(
    /eval\/hydralamp_runtype_20260826\/HYDRALAMP_SCIENCE_CLOSEOUT_RECEIPT\.json/,
  );
  return m ? m[0] : null;
}

function classifyAskRecovery(params: {
  timedOut: boolean;
  exitCode: number | null;
  stdout: string;
  stderr: string;
  recovered: string | null;
  expectedSha: string;
}): CortexRoundtripOutcome {
  if (params.timedOut) return "TIMEOUT";
  const blob = `${params.stdout}\n${params.stderr}`;
  if (/trial_expired|memory is locked/i.test(blob)) return "ERROR";
  if (/abstain/i.test(blob)) return "ABSTAIN";
  if (params.exitCode !== 0 && !params.recovered) return "ERROR";
  if (!params.recovered) return "MISS";
  if (params.recovered !== PUBLIC_SAFE_RECEIPT_REL) return "CONTRADICTORY";
  // recovered path matches; SHA freshness checked via independent HydraDG verify
  if (!params.expectedSha) return "STALE";
  return "PASS";
}

export function runCortexMemoryRoundtripMission(params: {
  repoRoot: string;
  officeId?: string | null;
  offerCode?: "FREECORTEX";
}): CortexMemoryRoundtripReceipt {
  const started = new Date().toISOString();
  const outDir = path.join(
    params.repoRoot,
    "eval",
    "agent_native_sponsors_20260827",
    "cortex",
  );
  const rawDir = path.join(outDir, "raw");
  mkdirSync(rawDir, { recursive: true });

  const receiptAbs = path.join(params.repoRoot, PUBLIC_SAFE_RECEIPT_REL);
  const underlyingSha = existsSync(receiptAbs)
    ? sha256Bytes(readFileSync(receiptAbs))
    : null;

  const auth = mitosisAuthState();
  const officeId = params.officeId || resolveMitosisOfficeId();

  const base: Omit<
    CortexMemoryRoundtripReceipt,
    | "remember"
    | "ask"
    | "hydradg_verify"
    | "CORTEX_MEMORY_ROUNDTRIP"
    | "HYDRADG_RECEIPT_VERIFICATION"
    | "status"
    | "error_code"
    | "error_summary"
    | "secret_state"
    | "recorded_at_utc"
  > = {
    schema: "sponsor.cortex.memory_roundtrip_receipt.v1",
    mission_id: "ANB-SP-CORTEX-ROUNDTRIP-001",
    provider: "Mitosis Cortex",
    operation: "memory_roundtrip",
    execution_host: "magicSTUDIObox.local",
    offer_code_metadata: params.offerCode || "FREECORTEX",
    offer_is_api_credential: false,
    architectural_boundary:
      "Cortex is external agent memory; FCG remains canonical HydraDG custody. Mission never appends to FCG.",
    docs_ref: "https://mitosislabs.ai/developers/cli/overview",
    office_id: officeId,
    auth_state: auth,
    underlying_receipt_ref: PUBLIC_SAFE_RECEIPT_REL,
    underlying_receipt_sha256: underlyingSha,
    fcg_append: "NOT_APPENDED",
    claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
    signature_state: "NOT_SIGNED",
  };

  if (miCliStatus() === "MISSING") {
    return finalize({
      ...base,
      recorded_at_utc: started,
      remember: emptyRemember("mi CLI missing"),
      ask: emptyAsk("mi CLI missing"),
      hydradg_verify: {
        ...verifyCustodyReceipt(params.repoRoot, PUBLIC_SAFE_RECEIPT_REL, underlyingSha || ""),
        recovered_ref_used: null,
      },
      CORTEX_MEMORY_ROUNDTRIP: "BLOCKED",
      HYDRADG_RECEIPT_VERIFICATION: underlyingSha ? "PASS" : "ERROR",
      status: "BLOCKED",
      error_code: "MI_CLI_MISSING",
      error_summary: "mi CLI not on PATH",
      secret_state: "MISSING",
      outDir,
      rawDir,
    });
  }

  if (auth !== "PASS" || !officeId) {
    return finalize({
      ...base,
      recorded_at_utc: started,
      remember: emptyRemember("auth or office missing"),
      ask: emptyAsk("auth or office missing"),
      hydradg_verify: {
        ...verifyCustodyReceipt(params.repoRoot, PUBLIC_SAFE_RECEIPT_REL, underlyingSha || ""),
        recovered_ref_used: null,
      },
      CORTEX_MEMORY_ROUNDTRIP: "BLOCKED",
      HYDRADG_RECEIPT_VERIFICATION: underlyingSha ? "PASS" : "ERROR",
      status: "BLOCKED",
      error_code: "MI_AUTH_OR_OFFICE_MISSING",
      error_summary: "Require MITOSIS_AUTH=PASS and MITOSIS_OFFICE_ID / MI_OFFICE_ID",
      secret_state: "BLOCKED",
      outDir,
      rawDir,
    });
  }

  if (!underlyingSha) {
    return finalize({
      ...base,
      recorded_at_utc: started,
      remember: emptyRemember("underlying receipt missing"),
      ask: emptyAsk("underlying receipt missing"),
      hydradg_verify: {
        status: "NULL" as const,
        verified: false,
        computed: null,
        declared: "",
        recovered_ref_used: null,
      },
      CORTEX_MEMORY_ROUNDTRIP: "ERROR",
      HYDRADG_RECEIPT_VERIFICATION: "ERROR",
      status: "ERROR",
      error_code: "UNDERLYING_RECEIPT_MISSING",
      error_summary: `Missing ${PUBLIC_SAFE_RECEIPT_REL}`,
      secret_state: "NOT_APPLICABLE",
      outDir,
      rawDir,
    });
  }

  const fact =
    `HydraDG public-safe custody receipt reference (external memory only; not canonical FCG): ` +
    `${PUBLIC_SAFE_RECEIPT_REL} sha256=${underlyingSha}`;

  // remember: CLI has no --json flag (as of mi 0.26); capture raw stdout/stderr instead.
  const rememberArgs = [
    "cortex",
    "remember",
    fact,
    "--office",
    officeId,
    "--kind",
    "decision",
    "--confidence",
    "0.7",
    "--source",
    "hydradg-public-custody-receipt",
  ];
  const remember = spawnSync("mi", rememberArgs, {
    encoding: "utf8",
    timeout: 120_000,
    maxBuffer: 4 * 1024 * 1024,
  });
  const rememberTimedOut =
    Boolean(remember.error) &&
    (remember.error as NodeJS.ErrnoException).code === "ETIMEDOUT";
  const rememberOut = redactSecrets(remember.stdout || "");
  const rememberErr = redactSecrets(remember.stderr || "");
  const rememberRawPath = path.join(rawDir, "CORTEX_REMEMBER_RAW.txt");
  writeFileSync(
    rememberRawPath,
    JSON.stringify(
      {
        note: "mi cortex remember does not support --json; raw CLI streams captured.",
        exit_code: remember.status,
        timed_out: rememberTimedOut,
        stdout: rememberOut,
        stderr: rememberErr,
      },
      null,
      2,
    ) + "\n",
  );

  // Separate retrieval operation
  const askQuery =
    "What is the HydraDG public-safe custody receipt reference path that was stored for " +
    "HYDRALAMP_SCIENCE_CLOSEOUT_RECEIPT? Return the exact eval/... path.";
  const askArgs = [
    "cortex",
    "ask",
    askQuery,
    "--office",
    officeId,
    "--json",
    "--limit",
    "8",
  ];
  const ask = spawnSync("mi", askArgs, {
    encoding: "utf8",
    timeout: 120_000,
    maxBuffer: 4 * 1024 * 1024,
  });
  const askTimedOut =
    Boolean(ask.error) && (ask.error as NodeJS.ErrnoException).code === "ETIMEDOUT";
  const askOut = redactSecrets(ask.stdout || "");
  const askErr = redactSecrets(ask.stderr || "");
  const askRawPath = path.join(rawDir, "CORTEX_ASK_RAW.json");
  writeFileSync(
    askRawPath,
    JSON.stringify(
      {
        exit_code: ask.status,
        timed_out: askTimedOut,
        stdout: askOut,
        stderr: askErr,
      },
      null,
      2,
    ) + "\n",
  );

  const recovered = extractReceiptRef(`${askOut}\n${askErr}`);
  const askRecovery = classifyAskRecovery({
    timedOut: askTimedOut,
    exitCode: ask.status,
    stdout: askOut,
    stderr: askErr,
    recovered,
    expectedSha: underlyingSha,
  });

  // Independent HydraDG verify on recovered reference (or NULL if unrecovered)
  let hydradg: ReturnType<typeof verifyCustodyReceipt>;
  let hydradgOutcome: CortexRoundtripOutcome;
  if (!recovered) {
    hydradg = {
      status: "NULL",
      verified: false,
      computed: null,
      declared: underlyingSha,
    };
    hydradgOutcome = "MISS";
  } else {
    hydradg = verifyCustodyReceipt(params.repoRoot, recovered, underlyingSha);
    if (hydradg.status === "PASS" && hydradg.verified) {
      hydradgOutcome = "PASS";
    } else if (hydradg.status === "FAIL") {
      hydradgOutcome = "CONTRADICTORY";
    } else {
      hydradgOutcome = "ERROR";
    }
  }

  const locked = /trial_expired|memory is locked/i.test(`${rememberOut}\n${rememberErr}\n${askOut}\n${askErr}`);
  let cortexRoundtrip: CortexRoundtripOutcome = askRecovery;
  if (rememberTimedOut || askTimedOut) cortexRoundtrip = "TIMEOUT";
  else if (locked) cortexRoundtrip = "ERROR";
  else if (remember.status !== 0 && askRecovery !== "PASS") cortexRoundtrip = "ERROR";
  else if (askRecovery === "PASS" && hydradgOutcome === "PASS") cortexRoundtrip = "PASS";

  const bothPass = cortexRoundtrip === "PASS" && hydradgOutcome === "PASS";
  let status: CortexMemoryRoundtripReceipt["status"] = bothPass
    ? "PASS"
    : locked
      ? "ERROR"
      : rememberTimedOut || askTimedOut
        ? "TIMEOUT"
        : "ERROR";
  let error_code: string | null = null;
  let error_summary: string | null = null;
  if (!bothPass) {
    if (locked) {
      error_code = "CORTEX_TRIAL_EXPIRED";
      error_summary =
        "Cortex office memory locked (trial_expired). Auth PASS; remember/ask blocked until plan unlock.";
    } else if (rememberTimedOut || askTimedOut) {
      error_code = "CORTEX_TIMEOUT";
      error_summary = "mi cortex command timed out";
    } else {
      error_code = "CORTEX_ROUNDTRIP_INCOMPLETE";
      error_summary = `CORTEX_MEMORY_ROUNDTRIP=${cortexRoundtrip}; HYDRADG_RECEIPT_VERIFICATION=${hydradgOutcome}`;
    }
  }

  return finalize({
    ...base,
    recorded_at_utc: new Date().toISOString(),
    remember: {
      attempted: true,
      command: ["mi", ...rememberArgs],
      exit_code: remember.status,
      timed_out: rememberTimedOut,
      raw_stdout_sha256: sha256Bytes(rememberOut),
      raw_stderr_sha256: sha256Bytes(rememberErr),
      raw_artifact_path: path.relative(params.repoRoot, rememberRawPath),
      note: "remember has no --json flag on mi CLI; streams hashed after secret redaction",
    },
    ask: {
      attempted: true,
      command: ["mi", ...askArgs],
      exit_code: ask.status,
      timed_out: askTimedOut,
      raw_response_sha256: sha256Bytes(askOut || askErr),
      raw_artifact_path: path.relative(params.repoRoot, askRawPath),
      recovered_receipt_ref: recovered,
      recovery_state: askRecovery,
    },
    hydradg_verify: { ...hydradg, recovered_ref_used: recovered },
    CORTEX_MEMORY_ROUNDTRIP: cortexRoundtrip,
    HYDRADG_RECEIPT_VERIFICATION: hydradgOutcome,
    status,
    error_code,
    error_summary,
    secret_state: "PRESENT",
    outDir,
    rawDir,
  });
}

function emptyRemember(note: string): CortexMemoryRoundtripReceipt["remember"] {
  return {
    attempted: false,
    command: [],
    exit_code: null,
    timed_out: false,
    raw_stdout_sha256: null,
    raw_stderr_sha256: null,
    raw_artifact_path: null,
    note,
  };
}

function emptyAsk(note: string): CortexMemoryRoundtripReceipt["ask"] {
  return {
    attempted: false,
    command: [],
    exit_code: null,
    timed_out: false,
    raw_response_sha256: null,
    raw_artifact_path: null,
    recovered_receipt_ref: null,
    recovery_state: "NOT_ATTEMPTED",
  };
}

function finalize(
  receipt: CortexMemoryRoundtripReceipt & { outDir: string; rawDir: string },
): CortexMemoryRoundtripReceipt {
  const { outDir, rawDir: _raw, ...body } = receipt;
  const roundtripPath = path.join(outDir, "CORTEX_MEMORY_ROUNDTRIP_RECEIPT.json");
  const missionPath = path.join(outDir, "CORTEX_MISSION_RECEIPT.json");
  writeFileSync(roundtripPath, JSON.stringify(body, null, 2) + "\n");
  writeFileSync(
    missionPath,
    JSON.stringify(
      {
        schema: "sponsor.cortex.mission_receipt.v1",
        mission_id: body.mission_id,
        provider: body.provider,
        operation: body.operation,
        status: body.status,
        error_code: body.error_code,
        error_summary: body.error_summary,
        offer_code_metadata: body.offer_code_metadata,
        offer_is_api_credential: false,
        architectural_boundary: body.architectural_boundary,
        roundtrip: {
          CORTEX_MEMORY_ROUNDTRIP: body.CORTEX_MEMORY_ROUNDTRIP,
          UNDERLYING_HYDRADG_RECEIPT_VERIFICATION: body.HYDRADG_RECEIPT_VERIFICATION,
        },
        underlying_receipt_ref: body.underlying_receipt_ref,
        underlying_receipt_sha256: body.underlying_receipt_sha256,
        roundtrip_receipt_path:
          "eval/agent_native_sponsors_20260827/cortex/CORTEX_MEMORY_ROUNDTRIP_RECEIPT.json",
        claim_ceiling: body.claim_ceiling,
        secret_state: body.secret_state,
        signature_state: body.signature_state,
        docs_ref: body.docs_ref,
        office_id: body.office_id,
        auth_state: body.auth_state,
        fcg_append: "NOT_APPENDED",
      },
      null,
      2,
    ) + "\n",
  );
  return body;
}
