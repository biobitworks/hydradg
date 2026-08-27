#!/usr/bin/env npx tsx
/**
 * Mitosis Cortex sponsor mission — external memory roundtrip.
 * Prefer authenticated `mi` CLI; never print MITOSIS_API_KEY / MI_API_KEY.
 */
import envModNs from "../lib/hydralamp/env.ts";
import * as fixturesModNs from "../lib/hydralamp/fixtures.ts";
import * as cortexModNs from "../lib/sponsors/cortexAdapter.ts";
import { unwrapHydraLampMod } from "./hydralamp_tsx_import.mts";

const { loadHydraLampServerEnv } = unwrapHydraLampMod(envModNs) as {
  loadHydraLampServerEnv: () => void;
};
const { repoRoot } = unwrapHydraLampMod(fixturesModNs as Record<string, unknown>) as {
  repoRoot: () => string;
};
const {
  runCortexMemoryRoundtripMission,
  resolveMitosisOfficeId,
  mitosisAuthState,
} = unwrapHydraLampMod(cortexModNs as Record<string, unknown>) as typeof import("../lib/sponsors/cortexAdapter.ts");

loadHydraLampServerEnv();

const auth = mitosisAuthState();
const office = resolveMitosisOfficeId();
console.log("MITOSIS_AUTH=" + auth);
console.log("MITOSIS_OFFICE_ID=" + (office || "MISSING"));
console.log("CORTEX_OFFER=FREECORTEX");

const receipt = runCortexMemoryRoundtripMission({
  repoRoot: repoRoot(),
  officeId: office,
  offerCode: "FREECORTEX",
});

console.log("CORTEX_MEMORY_ROUNDTRIP=" + receipt.CORTEX_MEMORY_ROUNDTRIP);
console.log("HYDRADG_RECEIPT_VERIFICATION=" + receipt.HYDRADG_RECEIPT_VERIFICATION);
console.log("CORTEX_MISSION_STATUS=" + receipt.status);
console.log("ERROR_CODE=" + (receipt.error_code || "null"));
console.log(
  "RECEIPT=eval/agent_native_sponsors_20260827/cortex/CORTEX_MEMORY_ROUNDTRIP_RECEIPT.json",
);

process.exit(receipt.status === "PASS" ? 0 : 1);
