#!/usr/bin/env npx tsx
/** Wire/verify Tavily + Vercel AI SDK tools; optional live extract if TAVILY_API_KEY set. */
import * as fixturesModNs from "../lib/hydralamp/fixtures.ts";
import * as tavilyAiModNs from "../lib/sponsors/tavilyAiSdk.ts";
import { unwrapHydraLampMod } from "./hydralamp_tsx_import.mts";

const { repoRoot } = unwrapHydraLampMod(fixturesModNs as Record<string, unknown>) as {
  repoRoot: () => string;
};
const { runTavilyAiSdkMission } = unwrapHydraLampMod(
  tavilyAiModNs as Record<string, unknown>,
) as typeof import("../lib/sponsors/tavilyAiSdk.ts");

const receipt = await runTavilyAiSdkMission({ repoRoot: repoRoot() });
console.log("TAVILY_AISDK_PACKAGE=" + receipt.package_import);
console.log("TAVILY_API_KEY=" + receipt.TAVILY_API_KEY);
console.log("TAVILY_AISDK_TOOLS=" + receipt.tools.map((t) => t.name).join(","));
console.log("TAVILY_AISDK_LIVE_EXTRACT=" + receipt.live_extract.status);
console.log("TAVILY_AISDK_MISSION=" + receipt.status);
console.log(
  "RECEIPT=eval/agent_native_sponsors_20260827/tavily/TAVILY_AISDK_MISSION_RECEIPT.json",
);
process.exit(receipt.status === "ERROR" ? 1 : 0);
