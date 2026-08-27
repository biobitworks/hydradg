import { runtypeApiKeyStatus, envOrDefault } from "./secrets";
import type { ProviderHealthRow } from "./types";

export function runtypeHealth(probed: boolean): ProviderHealthRow {
  const secret = runtypeApiKeyStatus();
  const configured = secret === "PRESENT";
  return {
    provider: "Runtype",
    lane: "SPONSOR",
    secret_state: secret,
    config_state: configured ? "CONFIGURED" : "NOT_CONFIGURED",
    runtime_state: probed
      ? configured
        ? "CONFIGURED"
        : "BLOCKED"
      : "NOT_PROBED",
    panel_state: configured ? "CONFIGURED" : "BLOCKED",
    hosted_on_vercel: true,
    claim_ceiling: "PROBABILISTIC_MODEL_OUTPUT",
    note:
      "Prior HydraLamp LIVE_RUNTYPE lane ERROR preserved. Overnight 4×25 not rerun. Studio remains scientific authority.",
  };
}

export function runtypeBaseUrl(): string {
  return envOrDefault("RUNTYPE_API_URL", "https://api.runtype.com");
}
