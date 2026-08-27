#!/usr/bin/env npx tsx
/** Cotal CLI setup + HydraDG evidence gateway bounded transaction. */
import * as fixturesModNs from "../lib/hydralamp/fixtures.ts";
import * as cotalModNs from "../lib/sponsors/cotalAdapter.ts";
import { unwrapHydraLampMod } from "./hydralamp_tsx_import.mts";

const { repoRoot } = unwrapHydraLampMod(fixturesModNs as Record<string, unknown>) as {
  repoRoot: () => string;
};
const { runCotalMission, cotalCliStatus } = unwrapHydraLampMod(
  cotalModNs as Record<string, unknown>,
) as typeof import("../lib/sponsors/cotalAdapter.ts");

console.log("COTAL_CLI=" + cotalCliStatus());
const receipt = runCotalMission({ repoRoot: repoRoot() });
console.log("COTAL_VERSION=" + (receipt.cotal_version || "null"));
console.log("COTAL_MISSION=" + receipt.status);
console.log("COTAL_MESH_UP=" + receipt.mesh_up);
console.log("ERROR_CODE=" + (receipt.error_code || "null"));
console.log("RECEIPT=eval/agent_native_sponsors_20260827/cotal/COTAL_MISSION_RECEIPT.json");
process.exit(receipt.status === "PASS" ? 0 : receipt.status === "BLOCKED" ? 2 : 1);
