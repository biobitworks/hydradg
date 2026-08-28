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
      name: "dispatch-probe",
      model: "qwen/qwen3.6-27b",
      systemPrompt: "Reply exactly.",
      temperature: 0,
      tools: { runtimeTools: [], maxToolCalls: 0 },
    },
    messages: [{ role: "user", content: "Return exactly: HYDRALAMP_RUNTYPE_LIVE_OK" }],
    streamResponse: false,
  } as never,
  {} as never,
  { cache: false } as never,
);
console.log("type", result?.constructor?.name);
console.log("keys", Object.keys(result as object));
console.log("proto", Object.getOwnPropertyNames(Object.getPrototypeOf(result as object)));
for (const k of Object.keys(result as object)) {
  console.log(k, typeof (result as Record<string, unknown>)[k], String((result as Record<string, unknown>)[k]).slice(0, 120));
}