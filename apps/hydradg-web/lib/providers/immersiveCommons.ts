import { redactSecrets } from "./secrets";
import type { ProviderHealthRow } from "./types";

const MCP_MANIFEST = "https://www.immersivecommons.com/.well-known/mcp.json";

export async function immersiveCommonsDiscover(): Promise<{
  status: "PASS" | "ERROR";
  name: string | null;
  version: string | null;
  public_tool_count: number | null;
  error_summary: string | null;
}> {
  try {
    const res = await fetch(MCP_MANIFEST, { cache: "no-store", signal: AbortSignal.timeout(15_000) });
    if (!res.ok) throw new Error(`HTTP_${res.status}`);
    const manifest = (await res.json()) as {
      name?: string;
      version?: string;
      public_tools?: unknown[];
    };
    return {
      status: "PASS",
      name: manifest.name || null,
      version: manifest.version || null,
      public_tool_count: Array.isArray(manifest.public_tools) ? manifest.public_tools.length : null,
      error_summary: null,
    };
  } catch (e) {
    return {
      status: "ERROR",
      name: null,
      version: null,
      public_tool_count: null,
      error_summary: redactSecrets(String((e as Error).message || e)).slice(0, 200),
    };
  }
}

export async function immersiveCommonsHealth(probe: boolean): Promise<ProviderHealthRow> {
  const base: ProviderHealthRow = {
    provider: "Immersive Commons",
    lane: "SPONSOR",
    secret_state: "NOT_APPLICABLE",
    config_state: "CONFIGURED",
    runtime_state: "NOT_PROBED",
    panel_state: "CONFIGURED",
    hosted_on_vercel: true,
    claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
    note: "Public MCP manifest only. Event credentials are not copied into the repo or Vercel env.",
  };
  if (!probe) return base;
  const d = await immersiveCommonsDiscover();
  return {
    ...base,
    runtime_state: d.status,
    panel_state: d.status === "PASS" ? "PASS" : "ERROR",
    note: d.error_summary || base.note,
  };
}
