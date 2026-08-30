import envMod from "../lib/hydralamp/env.ts";
import { unwrapHydraLampMod } from "./hydralamp_tsx_import.mts";
const { loadHydraLampServerEnv } = unwrapHydraLampMod(envMod);
loadHydraLampServerEnv();
const { RuntypeClient } = await import("@runtypelabs/sdk");
const client = new RuntypeClient({
  apiKey: process.env.RUNTYPE_API_KEY!,
  baseUrl: process.env.RUNTYPE_API_URL || "https://api.runtype.com",
});

// flow builder path
const flowResult = await client
  .flow("HydraLamp R2 probe")
  .prompt({
    name: "Echo",
    model: "qwen/qwen3.6-27b",
    systemPrompt: "Reply exactly as asked.",
    userPrompt: "Return exactly: HYDRALAMP_RUNTYPE_LIVE_OK",
    temperature: 0,
  })
  .run({ streamResponse: false } as never);

console.log("flow keys", Object.getOwnPropertyNames(Object.getPrototypeOf(flowResult)));
try {
  const echo = await flowResult.getResult("Echo");
  console.log("Echo result", echo);
} catch (e) {
  console.log("getResult err", e);
}
try {
  const summary = await flowResult.getSummary();
  console.log("summary", JSON.stringify(summary, (k, v) => (v instanceof Map ? Object.fromEntries(v) : v)).slice(0, 800));
} catch (e) {
  console.log("summary err", e);
}
