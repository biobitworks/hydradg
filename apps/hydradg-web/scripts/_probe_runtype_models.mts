import envMod from "../lib/hydralamp/env.ts";
import { unwrapHydraLampMod } from "./hydralamp_tsx_import.mts";
const { loadHydraLampServerEnv } = unwrapHydraLampMod(envMod);
loadHydraLampServerEnv();
const { RuntypeClient } = await import("@runtypelabs/sdk");
const client = new RuntypeClient({
  apiKey: process.env.RUNTYPE_API_KEY!,
  baseUrl: process.env.RUNTYPE_API_URL || "https://api.runtype.com",
});
const listed = await client.modelConfigs.list();
const rows = Array.isArray(listed) ? listed : (listed as { data?: unknown[] }).data || [];
for (const row of rows as Record<string, unknown>[]) {
  console.log(row.model || row.modelId || row.id, row.provider || row.providerId || "");
}