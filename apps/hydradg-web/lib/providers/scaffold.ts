import type { ProviderHealthRow } from "./types";
import { vercelHostingNote } from "./vercelBoundary";

/** Scaffold only — do not claim working on Vercel. */
export function cortexScaffoldHealth(): ProviderHealthRow {
  return {
    provider: "Cortex",
    lane: "SCAFFOLD",
    secret_state: "NOT_APPLICABLE",
    config_state: "NOT_APPLICABLE",
    runtime_state: "SKIPPED",
    panel_state: "SKIPPED",
    hosted_on_vercel: false,
    claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
    note:
      "Scaffold only on Vercel. Preserve Studio Cortex trial-lock ERROR (CORTEX_TRIAL_EXPIRED). " +
      vercelHostingNote("Mitosis Cortex / mi CLI"),
  };
}

export function tenkiScaffoldHealth(): ProviderHealthRow {
  return {
    provider: "Tenki",
    lane: "SCAFFOLD",
    secret_state: "NOT_APPLICABLE",
    config_state: "NOT_APPLICABLE",
    runtime_state: "SKIPPED",
    panel_state: "SKIPPED",
    hosted_on_vercel: false,
    claim_ceiling: "DETERMINISTIC_TOOL_OUTPUT",
    note: "Scaffold only. Not claimed working. Not scientific execution authority.",
  };
}

export function nebiusScaffoldHealth(): ProviderHealthRow {
  return {
    provider: "Nebius",
    lane: "SCAFFOLD",
    secret_state: "NOT_APPLICABLE",
    config_state: "NOT_APPLICABLE",
    runtime_state: "SKIPPED",
    panel_state: "SKIPPED",
    hosted_on_vercel: false,
    claim_ceiling: "NOT_APPLICABLE",
    note: "Scaffold only. Optional non-blocking. Not claimed working.",
  };
}
