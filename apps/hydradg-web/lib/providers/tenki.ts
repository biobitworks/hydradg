/**
 * Tenki scaffold — @tenkicloud/sandbox wiring only.
 * Do NOT execute sandboxes until the operator has completed:
 *   tenki login
 *   tenki status
 */
import { secretPresence } from "./secrets";
import type { ProviderHealthRow } from "./types";

export const TENKI_EXECUTE_GATE = {
  required_operator_steps: ["tenki login", "tenki status"] as const,
  execute_allowed: false,
  reason: "Operator has not completed tenki login + tenki status for this control-plane phase.",
};

export function tenkiScaffoldHealth(): ProviderHealthRow {
  const secret = secretPresence("TENKI_API_KEY");
  const configured = secret === "PRESENT";
  return {
    provider: "Tenki",
    lane: "SCAFFOLD",
    secret_state: secret,
    config_state: configured ? "CONFIGURED" : "NOT_CONFIGURED",
    runtime_state: "SKIPPED",
    panel_state: configured ? "CONFIGURED" : "SKIPPED",
    hosted_on_vercel: true,
    claim_ceiling: "DETERMINISTIC_TOOL_OUTPUT",
    note:
      "Scaffold only (@tenkicloud/sandbox). CONFIGURED is not PASS. " +
      "Execution blocked until operator completes: tenki login; tenki status.",
  };
}

export function tenkiScaffoldInfo() {
  return {
    provider: "Tenki",
    package: "@tenkicloud/sandbox",
    TENKI_API_KEY: secretPresence("TENKI_API_KEY"),
    execute_gate: TENKI_EXECUTE_GATE,
    claim_ceiling: "DETERMINISTIC_TOOL_OUTPUT",
    scientific_execution_authority: "magicSTUDIObox.local",
    status: "SKIPPED" as const,
  };
}

/** Never call the Tenki SDK execute path from Vercel in this phase. */
export function assertTenkiNotExecuted(): never {
  throw new Error(
    "TENKI_EXECUTE_BLOCKED: complete `tenki login` and `tenki status` before any sandbox execution.",
  );
}
