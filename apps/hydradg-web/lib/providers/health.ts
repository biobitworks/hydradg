import type { ProviderHealthRow } from "./types";
import { tavilyApiKeyStatus } from "../sponsors/tavilyAiSdk";
import { runtypeHealth } from "./runtype";
import { immersiveCommonsHealth } from "./immersiveCommons";
import { daytonaHealth, daytonaConnectivityProbe } from "./daytona";
import { hydradbHealth } from "./hydradb";
import { cortexScaffoldHealth, tenkiScaffoldHealth, nebiusScaffoldHealth } from "./scaffold";
import {
  NOT_HOSTED_ON_VERCEL,
  SCIENTIFIC_EXECUTION_AUTHORITY,
  isVercelRuntime,
  vercelHostingNote,
} from "./vercelBoundary";
import type { ProviderHealthState } from "./types";

function tavilyRow(probe: boolean): ProviderHealthRow {
  const secret = tavilyApiKeyStatus();
  const configured = secret === "PRESENT";
  return {
    provider: "Tavily",
    lane: "SPONSOR",
    secret_state: secret,
    config_state: configured ? "CONFIGURED" : "NOT_CONFIGURED",
    runtime_state: probe ? (configured ? "CONFIGURED" : "BLOCKED") : "NOT_PROBED",
    panel_state: configured ? "CONFIGURED" : "BLOCKED",
    hosted_on_vercel: true,
    claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
    note: "Key presence is CONFIGURED, not PASS. Live retrieve is a separate endpoint.",
  };
}

export async function buildProviderHealth(opts: { probe?: boolean } = {}) {
  const probe = Boolean(opts.probe);
  const tavily = tavilyRow(probe);
  const runtype = runtypeHealth(probe);
  const ic = await immersiveCommonsHealth(probe);
  let daytona = daytonaHealth(probe);
  if (probe && daytona.config_state === "CONFIGURED") {
    const d = await daytonaConnectivityProbe();
    daytona = {
      ...daytona,
      runtime_state: d.status,
      panel_state: d.status === "PASS" ? "PASS" : d.status,
      note: d.error_summary || daytona.note,
    };
  }
  const hydradb = await hydradbHealth(probe);

  const notHosted: ProviderHealthRow[] = NOT_HOSTED_ON_VERCEL.map((provider) => ({
    provider,
    lane: "NOT_HOSTED",
    secret_state: "NOT_APPLICABLE",
    config_state: "NOT_APPLICABLE",
    runtime_state: "SKIPPED",
    panel_state: "SKIPPED",
    hosted_on_vercel: false,
    claim_ceiling: "NOT_APPLICABLE",
    note: vercelHostingNote(provider),
  }));

  const rows: ProviderHealthRow[] = [
    tavily,
    runtype,
    ic,
    daytona,
    hydradb,
    cortexScaffoldHealth(),
    tenkiScaffoldHealth(),
    nebiusScaffoldHealth(),
    ...notHosted,
  ];

  // Invariant: CONFIGURED must never be rewritten to PASS solely because a key exists.
  const allowedPanel: ProviderHealthState[] = ["CONFIGURED", "PASS", "ERROR", "BLOCKED", "SKIPPED"];
  for (const row of rows) {
    if (row.secret_state === "PRESENT" && row.runtime_state === "NOT_PROBED") {
      row.panel_state = "CONFIGURED";
    }
    if (row.config_state === "CONFIGURED" && row.runtime_state === "NOT_PROBED") {
      row.panel_state = "CONFIGURED";
    }
    if (!allowedPanel.includes(row.panel_state)) {
      row.panel_state = "ERROR";
      row.note = `${row.note} Invalid panel_state coerced to ERROR.`;
    }
  }

  return {
    schema: "hydradg.provider_health.v1",
    recorded_at_utc: new Date().toISOString(),
    scientific_execution_authority: SCIENTIFIC_EXECUTION_AUTHORITY,
    vercel_runtime: isVercelRuntime(),
    probe,
    not_hosted_on_vercel: [...NOT_HOSTED_ON_VERCEL],
    invariant: "CONFIGURED_IS_NOT_PASS",
    providers: rows,
  };
}
