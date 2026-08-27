/**
 * Factual provider status for the Vercel control plane.
 * Studio receipt live_status values are frozen constants — never rewritten by key presence.
 * CONFIGURED (key presence) is never PASS.
 */
import { tavilyApiKeyStatus } from "../sponsors/tavilyAiSdk";
import { runtypeApiKeyStatus, daytonaApiKeyStatus, secretPresence, DOCUMENTED_SERVER_ENV } from "./secrets";
import {
  NOT_HOSTED_ON_VERCEL,
  SCIENTIFIC_EXECUTION_AUTHORITY,
  isVercelRuntime,
  vercelHostingNote,
} from "./vercelBoundary";
import { tenkiScaffoldHealth } from "./tenki";
import type { ProviderHealthRow, ProviderHealthState } from "./types";

/** Frozen Studio evidence pointers — do not mutate these receipt files. */
export const PRESERVED_STUDIO_RECEIPTS = {
  Tavily: {
    receipt_path: "eval/agent_native_sponsors_20260827/tavily/TAVILY_MISSION_RECEIPT.json",
    live_status: "PASS",
    error_code: null as string | null,
    lane: "SPONSOR",
  },
  Runtype: {
    receipt_path: "eval/agent_native_sponsors_20260827/runtype/RUNTYPE_MISSION_RECEIPT.json",
    live_status: "ERROR",
    error_code: null as string | null,
    lane: "SPONSOR",
  },
  Cortex: {
    receipt_path: "eval/agent_native_sponsors_20260827/cortex/CORTEX_MISSION_RECEIPT.json",
    live_status: "ERROR",
    error_code: "CORTEX_TRIAL_EXPIRED",
    lane: "SPONSOR",
  },
  Daytona: {
    receipt_path: "eval/agent_native_sponsors_20260827/daytona/DAYTONA_SMOKE_RECEIPT.json",
    live_status: "LIVE_PASS",
    error_code: null as string | null,
    lane: "INFRASTRUCTURE",
  },
} as const;

function runtimeConfigRow(
  provider: string,
  lane: ProviderHealthRow["lane"],
  secret: "PRESENT" | "MISSING" | "INVALID_PLACEHOLDER" | "NOT_APPLICABLE",
  claim_ceiling: string,
  note: string,
  hosted = true,
): ProviderHealthRow {
  return {
    provider,
    lane,
    secret_state: secret,
    config_state:
      secret === "NOT_APPLICABLE"
        ? "NOT_APPLICABLE"
        : secret === "PRESENT"
          ? "CONFIGURED"
          : "NOT_CONFIGURED",
    runtime_state: "NOT_PROBED",
    panel_state: secret === "PRESENT" ? "CONFIGURED" : secret === "NOT_APPLICABLE" ? "SKIPPED" : "BLOCKED",
    hosted_on_vercel: hosted,
    claim_ceiling,
    note,
  };
}

export async function buildProviderStatus() {
  const preserved_studio_receipts = Object.fromEntries(
    Object.entries(PRESERVED_STUDIO_RECEIPTS).map(([name, row]) => [
      name,
      {
        ...row,
        receipt_present: true,
        note: "Frozen Studio receipt. Vercel key presence does not rewrite this live_status.",
      },
    ]),
  );

  const vercel_runtime_config: ProviderHealthRow[] = [
    runtimeConfigRow(
      "Tavily",
      "SPONSOR",
      tavilyApiKeyStatus(),
      "EXTERNALLY_RETRIEVED_EVIDENCE",
      "Vercel runtime key presence only. Studio mission remains PASS. CONFIGURED ≠ PASS.",
    ),
    runtimeConfigRow(
      "Runtype",
      "SPONSOR",
      runtypeApiKeyStatus(),
      "PROBABILISTIC_MODEL_OUTPUT",
      "Studio Runtype ERROR preserved. Overnight 4×25 not rerun. CONFIGURED ≠ PASS.",
    ),
    {
      provider: "Cortex",
      lane: "SCAFFOLD",
      secret_state: "NOT_APPLICABLE",
      config_state: "NOT_APPLICABLE",
      runtime_state: "SKIPPED",
      panel_state: "SKIPPED",
      hosted_on_vercel: false,
      claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
      note:
        "Scaffold only on Vercel. Preserve Studio ERROR / CORTEX_TRIAL_EXPIRED. " +
        vercelHostingNote("Mitosis Cortex / mi CLI"),
    },
    runtimeConfigRow(
      "Daytona",
      "INFRASTRUCTURE",
      daytonaApiKeyStatus(),
      "DETERMINISTIC_TOOL_OUTPUT",
      "Studio INFRASTRUCTURE / LIVE_PASS smoke preserved. CONFIGURED ≠ PASS.",
    ),
    tenkiScaffoldHealth(),
    runtimeConfigRow(
      "Immersive Commons",
      "SPONSOR",
      "NOT_APPLICABLE",
      "EXTERNALLY_RETRIEVED_EVIDENCE",
      "Public MCP manifest only. No event credentials on Vercel.",
    ),
    runtimeConfigRow(
      "HydraDB",
      "INFRASTRUCTURE",
      secretPresence("HYDRA_DB_API_KEY") === "PRESENT"
        ? "PRESENT"
        : secretPresence("HYDRADB_API_KEY"),
      "REMOTE_HYDRADB_V2_CONNECTIVITY_AND_REQUEST_LEVEL_TRACEABILITY_ONLY",
      "Projection/readback only. Not canonical FCG.",
    ),
    {
      provider: "Nebius",
      lane: "SCAFFOLD",
      secret_state: "NOT_APPLICABLE",
      config_state: "NOT_APPLICABLE",
      runtime_state: "SKIPPED",
      panel_state: "SKIPPED",
      hosted_on_vercel: false,
      claim_ceiling: "NOT_APPLICABLE",
      note: "Scaffold only. Not claimed working.",
    },
    ...NOT_HOSTED_ON_VERCEL.map(
      (provider): ProviderHealthRow => ({
        provider,
        lane: "NOT_HOSTED",
        secret_state: "NOT_APPLICABLE",
        config_state: "NOT_APPLICABLE",
        runtime_state: "SKIPPED",
        panel_state: "SKIPPED",
        hosted_on_vercel: false,
        claim_ceiling: "NOT_APPLICABLE",
        note: vercelHostingNote(provider),
      }),
    ),
  ];

  const allowed: ProviderHealthState[] = ["CONFIGURED", "PASS", "ERROR", "BLOCKED", "SKIPPED"];
  for (const row of vercel_runtime_config) {
    if (row.runtime_state === "NOT_PROBED" && row.secret_state === "PRESENT") {
      row.panel_state = "CONFIGURED";
    }
    if (row.panel_state === "PASS" && row.runtime_state === "NOT_PROBED") {
      row.panel_state = "CONFIGURED";
      row.note = `${row.note} Coerced PASS→CONFIGURED (key presence is not PASS).`;
    }
    if (!allowed.includes(row.panel_state)) {
      row.panel_state = "ERROR";
    }
  }

  return {
    schema: "hydradg.provider_status.v1",
    recorded_at_utc: new Date().toISOString(),
    scientific_execution_authority: SCIENTIFIC_EXECUTION_AUTHORITY,
    vercel_runtime: isVercelRuntime(),
    invariant: "CONFIGURED_IS_NOT_PASS",
    documented_server_env: [...DOCUMENTED_SERVER_ENV],
    not_hosted_on_vercel: [...NOT_HOSTED_ON_VERCEL],
    preserved_studio_receipts,
    preserved_invariants: {
      Tavily: "PASS",
      Runtype: "ERROR",
      Cortex: "ERROR / CORTEX_TRIAL_EXPIRED",
      Daytona: "INFRASTRUCTURE / LIVE_PASS",
      Tenki: "SKIPPED until tenki login && tenki status",
    },
    providers: vercel_runtime_config,
    note: "Factual status. Studio receipt live_status is authoritative for PASS/ERROR/LIVE_PASS. Vercel key presence is CONFIGURED only.",
  };
}
