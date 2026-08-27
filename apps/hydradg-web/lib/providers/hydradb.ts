import { hostedHydraDBStatus } from "../hydradbHosted";
import { hydraDbApiKeyStatus, redactSecrets } from "./secrets";
import type { ProviderHealthRow } from "./types";

export async function hydradbHealth(probe: boolean): Promise<ProviderHealthRow> {
  const secret = hydraDbApiKeyStatus();
  const configured = secret === "PRESENT";
  const base: ProviderHealthRow = {
    provider: "HydraDB",
    lane: "INFRASTRUCTURE",
    secret_state: secret,
    config_state: configured ? "CONFIGURED" : "NOT_CONFIGURED",
    runtime_state: "NOT_PROBED",
    panel_state: configured ? "CONFIGURED" : "BLOCKED",
    hosted_on_vercel: true,
    claim_ceiling: "REMOTE_HYDRADB_V2_CONNECTIVITY_AND_REQUEST_LEVEL_TRACEABILITY_ONLY",
    note: "HydraDB is projection/readback, not canonical FCG.",
  };
  if (!probe) return base;
  if (!configured) {
    return { ...base, runtime_state: "BLOCKED", panel_state: "BLOCKED" };
  }
  try {
    const st = await hostedHydraDBStatus();
    const connected = (st as { backend_connectivity?: string }).backend_connectivity === "PASS";
    if (connected) {
      return { ...base, runtime_state: "PASS", panel_state: "PASS" };
    }
    return {
      ...base,
      runtime_state: "CONFIGURED",
      panel_state: "CONFIGURED",
      note: "Key/database discovery only. CONFIGURED is not PASS.",
    };
  } catch (e) {
    return {
      ...base,
      runtime_state: "ERROR",
      panel_state: "ERROR",
      note: redactSecrets(String((e as Error).message || e)).slice(0, 200),
    };
  }
}
