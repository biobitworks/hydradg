import type { ProviderHealthRow } from "./types";
import { vercelHostingNote } from "./vercelBoundary";
export { tenkiScaffoldHealth, tenkiScaffoldInfo, TENKI_EXECUTE_GATE } from "./tenki";

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
      "Scaffold only on Vercel. Studio Mitosis Cortex roundtrip PASS (MagicStudioBox). " +
      vercelHostingNote("Mitosis Cortex / mi CLI"),
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
