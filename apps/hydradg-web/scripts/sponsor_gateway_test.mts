/** Unit tests for sponsor evidence gateway (deterministic, no secrets). */
import assert from "node:assert/strict";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as gwModNs from "../lib/sponsors/evidenceGateway.ts";
import { unwrapHydraLampMod } from "./hydralamp_tsx_import.mts";

const {
  discoverCapabilities,
  executeGatewayTool,
  proposeExternalEvidence,
} = unwrapHydraLampMod(gwModNs as Record<string, unknown>) as typeof import("../lib/sponsors/evidenceGateway.ts");

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "..", "..", "..");

const caps = discoverCapabilities();
assert.equal(caps.tools.length, 4);
assert.ok(caps.tools.some((t) => t.tool === "verify_custody_receipt"));

const propose = proposeExternalEvidence({
  source_url: "https://example.com",
  raw_artifact_sha256: "abc",
  evidence_class: "EXTERNALLY_RETRIEVED_EVIDENCE",
});
assert.equal(propose.fcg_append, "NOT_APPENDED");
assert.equal(propose.quarantine_state, "PENDING_CUSTODY_REVIEW");

const discover = executeGatewayTool("discover_capabilities", repoRoot);
assert.ok((discover as { gateway?: string }).gateway);

console.log("sponsor_gateway_tests=PASS");
