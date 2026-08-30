import envMod from "../lib/hydralamp/env.ts";
import { unwrapHydraLampMod } from "./hydralamp_tsx_import.mts";
const { loadHydraLampServerEnv } = unwrapHydraLampMod(envMod);
loadHydraLampServerEnv();
const { RuntypeClient } = await import("@runtypelabs/sdk");
const client = new RuntypeClient({
  apiKey: process.env.RUNTYPE_API_KEY!,
  baseUrl: process.env.RUNTYPE_API_URL || "https://api.runtype.com",
});
const result = await client.runWithLocalTools(
  {
    agent: {
      name: "probe",
      model: "qwen/qwen3.6-27b",
      systemPrompt: "Reply exactly as asked.",
      temperature: 0,
      tools: { runtimeTools: [], maxToolCalls: 0 },
    },
    messages: [{ role: "user", content: "Return exactly: HYDRALAMP_RUNTYPE_LIVE_OK" }],
    streamResponse: false,
  } as never,
  {} as never,
  { cache: false } as never,
);
import { writeFileSync } from "node:fs";
const serialized: Record<string, unknown> = {};
for (const k of Object.keys(result as object)) {
  const v = (result as Record<string, unknown>)[k];
  serialized[k] = typeof v === "function" ? "[function]" : v;
}
if (typeof (result as { getResult?: unknown }).getResult === "function") {
  try {
    serialized._getResult_default = await (result as { getResult: () => Promise<unknown> }).getResult();
  } catch (e) {
    serialized._getResult_error = String(e);
  }
}
writeFileSync("/tmp/runtype_probe.json", JSON.stringify(serialized, null, 2));
console.log("WROTE /tmp/runtype_probe.json keys:", Object.keys(serialized).join(","));
