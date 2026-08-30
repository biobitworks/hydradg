import envMod from "../lib/hydralamp/env.ts";
import { unwrapHydraLampMod } from "./hydralamp_tsx_import.mts";
const { loadHydraLampServerEnv } = unwrapHydraLampMod(envMod);
loadHydraLampServerEnv();
const { RuntypeClient } = await import("@runtypelabs/sdk");
const client = new RuntypeClient({
  apiKey: process.env.RUNTYPE_API_KEY!,
  baseUrl: process.env.RUNTYPE_API_URL || "https://api.runtype.com",
});
let deltas = "";
const events: unknown[] = [];
await client.runWithLocalTools(
  {
    agent: {
      name: "stream-probe",
      model: "qwen/qwen3.6-27b",
      systemPrompt: "Reply exactly.",
      temperature: 0,
      tools: { runtimeTools: [], maxToolCalls: 0 },
    },
    messages: [{ role: "user", content: "Return exactly: HYDRALAMP_RUNTYPE_LIVE_OK" }],
    streamResponse: true,
  } as never,
  {} as never,
  {
    onFlowStart: (e) => events.push({ type: "flow_start", e }),
    onStepStart: (e) => events.push({ type: "step_start", e }),
    onStepDelta: (t, e) => {
      deltas += t;
      events.push({ type: "delta", t, e });
    },
    onStepComplete: (r, e) => events.push({ type: "step_complete", r, e }),
    onFlowComplete: (e) => events.push({ type: "flow_complete", e }),
  } as never,
);
console.log("deltas", deltas);
console.log("events", JSON.stringify(events, null, 2).slice(0, 3000));