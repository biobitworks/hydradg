#!/usr/bin/env npx tsx
/** Tenki Sandbox sponsor mission — never prints TENKI_API_KEY. */
import envModNs from "../lib/hydralamp/env.ts";
import * as fixturesModNs from "../lib/hydralamp/fixtures.ts";
import * as tenkiModNs from "../lib/sponsors/tenkiAdapter.ts";
import { unwrapHydraLampMod } from "./hydralamp_tsx_import.mts";

const { loadHydraLampServerEnv } = unwrapHydraLampMod(envModNs) as {
  loadHydraLampServerEnv: () => void;
};
const { repoRoot } = unwrapHydraLampMod(fixturesModNs as Record<string, unknown>) as {
  repoRoot: () => string;
};
const { runTenkiSandboxMission, tenkiCliStatus, tenkiAuthState, tenkiApiKeyStatus } =
  unwrapHydraLampMod(tenkiModNs as Record<string, unknown>) as typeof import("../lib/sponsors/tenkiAdapter.ts");

loadHydraLampServerEnv();
console.log("TENKI_CLI=" + tenkiCliStatus());
console.log("TENKI_API_KEY=" + tenkiApiKeyStatus());
console.log("TENKI_AUTH=" + tenkiAuthState());

const receipt = runTenkiSandboxMission({ repoRoot: repoRoot() });
console.log("TENKI_MISSION=" + receipt.status);
console.log("TENKI_SESSION=" + (receipt.session_id || "null"));
console.log("ERROR_CODE=" + (receipt.error_code || "null"));
console.log(
  "RECEIPT=eval/agent_native_sponsors_20260827/tenki/TENKI_SANDBOX_MISSION_RECEIPT.json",
);
process.exit(receipt.status === "PASS" ? 0 : receipt.status === "BLOCKED" ? 2 : 1);
