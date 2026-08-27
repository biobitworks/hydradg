import { daytonaApiKeyStatus, envOrDefault, redactSecrets } from "./secrets";
import { isVercelRuntime } from "./vercelBoundary";
import type { ProviderHealthRow } from "./types";

export function daytonaHealth(probe: boolean): ProviderHealthRow {
  const secret = daytonaApiKeyStatus();
  const configured = secret === "PRESENT";
  return {
    provider: "Daytona",
    lane: "INFRASTRUCTURE",
    secret_state: secret,
    config_state: configured ? "CONFIGURED" : "NOT_CONFIGURED",
    runtime_state: probe ? (configured ? "CONFIGURED" : "BLOCKED") : "NOT_PROBED",
    panel_state: configured ? "CONFIGURED" : "BLOCKED",
    hosted_on_vercel: true,
    claim_ceiling: "DETERMINISTIC_TOOL_OUTPUT",
    note: isVercelRuntime()
      ? "Vercel may call Daytona API. Ephemeral sandbox smoke is Studio-recorded; not a scientific experiment host."
      : "Studio-recorded LIVE_PASS smoke is independent of this health row.",
  };
}

/** Connectivity probe only — does not create a sandbox or run scientific work. */
export async function daytonaConnectivityProbe(): Promise<{
  status: "PASS" | "ERROR" | "BLOCKED";
  http_status: number | null;
  error_summary: string | null;
}> {
  const secret = daytonaApiKeyStatus();
  if (secret !== "PRESENT") {
    return { status: "BLOCKED", http_status: null, error_summary: "DAYTONA_API_KEY " + secret };
  }
  const base = envOrDefault("DAYTONA_API_URL", "https://app.daytona.io/api").replace(/\/$/, "");
  try {
    const res = await fetch(`${base}/sandbox`, {
      headers: {
        Authorization: `Bearer ${process.env.DAYTONA_API_KEY}`,
        Accept: "application/json",
      },
      cache: "no-store",
      signal: AbortSignal.timeout(15_000),
    });
    if (res.status === 401 || res.status === 403) {
      return { status: "ERROR", http_status: res.status, error_summary: "AUTH_REJECTED" };
    }
    if (res.ok || res.status === 404) {
      return { status: "PASS", http_status: res.status, error_summary: null };
    }
    return {
      status: "ERROR",
      http_status: res.status,
      error_summary: `HTTP_${res.status}`,
    };
  } catch (e) {
    return {
      status: "ERROR",
      http_status: null,
      error_summary: redactSecrets(String((e as Error).message || e)).slice(0, 200),
    };
  }
}
