/** Sponsor mission registry — reads eval artifacts for UI/API. */
import { readFileSync, existsSync } from "node:fs";
import path from "node:path";
import type { GoldenPathState, SponsorPanelState, SponsorProviderSummary } from "./types";
import { loadGumDoctorReceipt } from "./gumDoctor";

function readJson<T>(abs: string): T | null {
  if (!existsSync(abs)) return null;
  try {
    return JSON.parse(readFileSync(abs, "utf8")) as T;
  } catch {
    return null;
  }
}

function panelFromMission(status: string | undefined, discovery: string): SponsorPanelState {
  if (status === "PASS") return "LIVE_PASS";
  if (status === "ERROR" || status === "TIMEOUT" || status === "NEGATIVE") return "ERROR";
  if (status === "BLOCKED") return "BLOCKED";
  if (status === "SKIPPED" || discovery === "SKIPPED" || discovery === "DEFERRED_NONBLOCKING")
    return "SKIPPED";
  if (discovery === "CONFIGURED") return "CONFIGURED";
  return "DISCOVERED";
}

export function loadSponsorDiscoveryMatrix(repoRoot: string) {
  return readJson<Record<string, unknown>>(
    path.join(repoRoot, "eval", "agent_native_sponsors_20260827", "SPONSOR_DISCOVERY_MATRIX.json"),
  );
}

export function loadSponsorCloseout(repoRoot: string) {
  return readJson<Record<string, unknown>>(
    path.join(repoRoot, "eval", "agent_native_sponsors_20260827", "SPONSOR_INTEGRATION_CLOSEOUT.json"),
  );
}

export function buildProviderSummaries(repoRoot: string): SponsorProviderSummary[] {
  const closeout = loadSponsorCloseout(repoRoot);
  const providers = (closeout?.providers as Record<string, Record<string, string>>) || {};
  const infrastructure = (closeout?.infrastructure as Record<string, Record<string, string>>) || {};
  const order = [
    "Runtype",
    "Tavily",
    "Cortex",
    "Yappy",
    "Immersive Commons",
    "Cotal",
    "Hacker Bob",
    "Tenki",
    "Nebius",
  ];
  const sponsorRows = order.map((provider) => {
    const row = providers[provider] || {};
    return {
      provider,
      priority: (row.priority as SponsorProviderSummary["priority"]) || "P0",
      lane: "SPONSOR" as const,
      panel_state: panelFromMission(row.live_status, row.discovery_state || "DISCOVERED"),
      discovery_state: (row.discovery_state as SponsorProviderSummary["discovery_state"]) || "DISCOVERED",
      live_status: (row.live_status as SponsorProviderSummary["live_status"]) || "NOT_ATTEMPTED",
      claim_ceiling: row.claim_ceiling || "NOT_STATED",
      receipt_path: row.receipt_path || null,
    };
  });
  const infraOrder = ["Daytona"];
  const infraRows = infraOrder.map((provider) => {
    const row = infrastructure[provider] || {};
    const live = row.live_status;
    const discovery = row.discovery_state || "CONFIGURED";
    return {
      provider,
      priority: "INFRASTRUCTURE" as const,
      lane: "INFRASTRUCTURE" as const,
      panel_state: panelFromMission(live, discovery),
      discovery_state: (discovery as SponsorProviderSummary["discovery_state"]) || "CONFIGURED",
      live_status: (live as SponsorProviderSummary["live_status"]) || "NOT_ATTEMPTED",
      claim_ceiling: row.claim_ceiling || "DETERMINISTIC_TOOL_OUTPUT",
      receipt_path: row.receipt_path || null,
    };
  });
  return [...sponsorRows, ...infraRows];
}

export function buildGoldenPath(repoRoot: string): GoldenPathState {
  const closeout = loadSponsorCloseout(repoRoot);
  const gp = (closeout?.golden_path as Record<string, unknown>) || {};
  const notes = Array.isArray(gp.notes) ? (gp.notes as string[]) : [];
  return {
    source: (gp.source as string) || null,
    memory: (gp.memory as string) || null,
    model: (gp.model as string) || null,
    external_actor: (gp.external_actor as string) || null,
    custody: (gp.custody as string) || "HydraDG FCO/FCG",
    projection: (gp.projection as string) || "HydraDB",
    composed_status: (gp.composed_status as GoldenPathState["composed_status"]) || "PARTIAL",
    notes,
  };
}

export function sponsorStatusPayload(repoRoot: string) {
  const gum = loadGumDoctorReceipt(repoRoot);
  const closeout = loadSponsorCloseout(repoRoot);
  return {
    recorded_at_utc: closeout?.recorded_at_utc || new Date().toISOString(),
    GUM_DOCTOR_STATE: gum?.GUM_DOCTOR_STATE || "DEPENDENCY_UNRESOLVED",
    SPONSOR_SECRET_INJECTION: gum?.SPONSOR_SECRET_INJECTION || "BLOCKED",
    providers: buildProviderSummaries(repoRoot),
    golden_path: buildGoldenPath(repoRoot),
    closeout_path: "eval/agent_native_sponsors_20260827/SPONSOR_INTEGRATION_CLOSEOUT.json",
  };
}
