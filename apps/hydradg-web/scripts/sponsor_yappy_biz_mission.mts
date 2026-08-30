#!/usr/bin/env npx tsx
/** yappy.biz public API probe — distinct from Mitosis Yappy. */
import * as fixturesModNs from "../lib/hydralamp/fixtures.ts";
import * as yappyModNs from "../lib/sponsors/yappyBizAdapter.ts";
import { unwrapHydraLampMod } from "./hydralamp_tsx_import.mts";

const { repoRoot } = unwrapHydraLampMod(fixturesModNs as Record<string, unknown>) as {
  repoRoot: () => string;
};
const { runYappyBizApiMission } = unwrapHydraLampMod(
  yappyModNs as Record<string, unknown>,
) as typeof import("../lib/sponsors/yappyBizAdapter.ts");

const receipt = await runYappyBizApiMission({ repoRoot: repoRoot() });
console.log("YAPPY_BIZ_MISSION=" + receipt.status);
console.log("YAPPY_BIZ_LATEST=" + (receipt.latest_release_version || "null"));
console.log(
  "RECEIPT=eval/agent_native_sponsors_20260827/yappy_biz/YAPPY_BIZ_API_MISSION_RECEIPT.json",
);
process.exit(receipt.status === "PASS" ? 0 : 1);
