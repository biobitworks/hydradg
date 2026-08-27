/**
 * Discover usable Runtype models and freeze MODEL_INVENTORY.json.
 * Never prints secret values. Fails closed if RUNTYPE_API_KEY missing.
 */
import { writeFileSync } from "node:fs";
import path from "node:path";
import envModNs from "../lib/hydralamp/env.ts";
import * as fixturesModNs from "../lib/hydralamp/fixtures.ts";
import { unwrapHydraLampMod } from "./hydralamp_tsx_import.mts";

const { loadHydraLampServerEnv, runtypeApiKeyStatus } = unwrapHydraLampMod(envModNs);
const { repoRoot } = unwrapHydraLampMod(fixturesModNs as Record<string, unknown>) as {
  repoRoot: () => string;
};

async function main() {
  loadHydraLampServerEnv();
  const status = runtypeApiKeyStatus();
  const outPath = path.join(repoRoot(), "eval", "hydralamp_runtype_20260826", "MODEL_INVENTORY.json");

  if (status !== "PRESENT") {
    const inv = {
      schema: "hydralamp.runtype.model_inventory.v1",
      recorded_at_utc: new Date().toISOString(),
      runtype_api_key_present: false,
      runtype_state: "NOT_CONFIGURED",
      selected_models: [],
      discovery_note:
        "RUNTYPE_API_KEY MISSING. No models selected. Do not silently substitute.",
      minimum_required: 1,
      preferred: 3,
    };
    writeFileSync(outPath, JSON.stringify(inv, null, 2) + "\n");
    console.log("RUNTYPE_API_KEY=MISSING");
    console.log("RUNTYPE_STATE=NOT_CONFIGURED");
    console.log("MODEL_INVENTORY_WRITTEN", outPath);
    process.exit(2);
  }

  const { RuntypeClient } = await import("@runtypelabs/sdk");
  const client = new RuntypeClient({
    apiKey: process.env.RUNTYPE_API_KEY!,
    baseUrl: process.env.RUNTYPE_API_URL || "https://api.runtype.com",
  });

  let discovered: Array<Record<string, unknown>> = [];
  let discovery_method = "NONE";
  try {
    // Prefer official modelConfigs listing when available
    const anyClient = client as unknown as {
      modelConfigs?: { list?: () => Promise<unknown> };
      get?: (path: string) => Promise<unknown>;
    };
    if (anyClient.modelConfigs?.list) {
      const listed = await anyClient.modelConfigs.list();
      discovered = Array.isArray(listed)
        ? (listed as Record<string, unknown>[])
        : Array.isArray((listed as { data?: unknown }).data)
          ? ((listed as { data: Record<string, unknown>[] }).data)
          : [];
      discovery_method = "modelConfigs.list";
    } else if (anyClient.get) {
      const listed = await anyClient.get("/v1/model-configs");
      discovered = Array.isArray((listed as { data?: unknown }).data)
        ? ((listed as { data: Record<string, unknown>[] }).data)
        : Array.isArray(listed)
          ? (listed as Record<string, unknown>[])
          : [];
      discovery_method = "GET /v1/model-configs";
    }
  } catch (e) {
    discovery_method = `FAILED:${String((e as Error).message || e).slice(0, 80)}`;
  }

  // Prefer Qwen/Mistral families when present; otherwise first available distinct IDs.
  const ids: string[] = [];
  for (const row of discovered) {
    const id = String(row.model || row.modelId || row.id || row.name || "").trim();
    if (!id) continue;
    if (!ids.includes(id)) ids.push(id);
  }

  const preferred = ids.filter((id) => /qwen|mistral|mixtral/i.test(id));
  const pool = preferred.length ? preferred : ids;
  // small / medium / different-family heuristic: first three distinct
  const chosen = pool.slice(0, 3);
  if (chosen.length === 0) {
    const inv = {
      schema: "hydralamp.runtype.model_inventory.v1",
      recorded_at_utc: new Date().toISOString(),
      runtype_api_key_present: true,
      runtype_state: "CONFIGURED_BUT_NO_MODELS_DISCOVERED",
      selected_models: [],
      discovery_method,
      discovery_count: discovered.length,
      discovery_note:
        "Credential accepted or present, but no usable model IDs discovered. Do not silently substitute.",
      minimum_required: 1,
      preferred: 3,
    };
    writeFileSync(outPath, JSON.stringify(inv, null, 2) + "\n");
    console.log("RUNTYPE_API_KEY=PRESENT");
    console.log("RUNTYPE_STATE=CONFIGURED_BUT_NO_MODELS_DISCOVERED");
    process.exit(3);
  }

  const lanes = ["agent-a", "agent-b", "agent-c"] as const;
  const selected_models = chosen.map((model_id, i) => ({
    lane: lanes[i],
    provider: "runtype",
    model_id,
    config_id: `hydralamp-live-${lanes[i]}-temp0`,
    temperature: 0,
    cache: false,
    recorded_at_utc: new Date().toISOString(),
  }));

  const inv = {
    schema: "hydralamp.runtype.model_inventory.v1",
    recorded_at_utc: new Date().toISOString(),
    runtype_api_key_present: true,
    runtype_state: "CONFIGURED",
    selected_models,
    discovery_method,
    discovery_count: discovered.length,
    discovery_note:
      "Frozen before experiment. Do not mutate after CONTROL/INVALID_PROOF start.",
    minimum_required: 1,
    preferred: 3,
    secret_value_recorded: false,
  };
  writeFileSync(outPath, JSON.stringify(inv, null, 2) + "\n");
  console.log("RUNTYPE_API_KEY=PRESENT");
  console.log("RUNTYPE_STATE=CONFIGURED");
  console.log("SELECTED_MODELS", selected_models.map((m) => m.model_id).join(","));
  console.log("MODEL_INVENTORY_WRITTEN", outPath);
}

void main();
