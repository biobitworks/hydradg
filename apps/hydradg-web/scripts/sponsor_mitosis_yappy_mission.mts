#!/usr/bin/env npx tsx
/** Mitosis Yappy (mi agents) — distinct from yappy.biz. */
import envModNs from "../lib/hydralamp/env.ts";
import * as fixturesModNs from "../lib/hydralamp/fixtures.ts";
import * as yappyModNs from "../lib/sponsors/mitosisYappyAdapter.ts";
import { unwrapHydraLampMod } from "./hydralamp_tsx_import.mts";

const { loadHydraLampServerEnv } = unwrapHydraLampMod(envModNs) as {
  loadHydraLampServerEnv: () => void;
};
const { repoRoot } = unwrapHydraLampMod(fixturesModNs as Record<string, unknown>) as {
  repoRoot: () => string;
};
const { runMitosisYappyMission } = unwrapHydraLampMod(
  yappyModNs as Record<string, unknown>,
) as typeof import("../lib/sponsors/mitosisYappyAdapter.ts");

loadHydraLampServerEnv();
const receipt = runMitosisYappyMission({ repoRoot: repoRoot() });
console.log("MITOSIS_YAPPY_AUTH=" + receipt.auth_state);
console.log("MITOSIS_YAPPY_AGENTS=" + receipt.agents_listed);
console.log("MITOSIS_YAPPY_MISSION=" + receipt.status);
console.log("ERROR_CODE=" + (receipt.error_code || "null"));
console.log("RECEIPT=eval/agent_native_sponsors_20260827/yappy/YAPPY_MISSION_RECEIPT.json");
process.exit(receipt.status === "PASS" ? 0 : 2);
