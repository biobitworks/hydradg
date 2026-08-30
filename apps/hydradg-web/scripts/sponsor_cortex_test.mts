#!/usr/bin/env npx tsx
/** Targeted Cortex adapter + gateway verify tests (no live mi required for pure unit paths). */
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync, existsSync } from "node:fs";
import path from "node:path";
import * as fixturesModNs from "../lib/hydralamp/fixtures.ts";
import * as cortexModNs from "../lib/sponsors/cortexAdapter.ts";
import * as gwModNs from "../lib/sponsors/evidenceGateway.ts";
import { unwrapHydraLampMod } from "./hydralamp_tsx_import.mts";

const { repoRoot } = unwrapHydraLampMod(fixturesModNs as Record<string, unknown>) as {
  repoRoot: () => string;
};
const { PUBLIC_SAFE_RECEIPT_REL, miCliStatus } = unwrapHydraLampMod(
  cortexModNs as Record<string, unknown>,
) as typeof import("../lib/sponsors/cortexAdapter.ts");
const { verifyCustodyReceipt, executeGatewayTool } = unwrapHydraLampMod(
  gwModNs as Record<string, unknown>,
) as typeof import("../lib/sponsors/evidenceGateway.ts");

const root = repoRoot();
const abs = path.join(root, PUBLIC_SAFE_RECEIPT_REL);
assert.ok(existsSync(abs), "public-safe receipt must exist");
const sha = createHash("sha256").update(readFileSync(abs)).digest("hex");

const v = verifyCustodyReceipt(root, PUBLIC_SAFE_RECEIPT_REL, sha);
assert.equal(v.status, "PASS");
assert.equal(v.verified, true);

const fail = verifyCustodyReceipt(root, PUBLIC_SAFE_RECEIPT_REL, "0".repeat(64));
assert.equal(fail.status, "FAIL");
assert.equal(fail.verified, false);

const gw = executeGatewayTool("verify_custody_receipt", root, {
  receipt_path: PUBLIC_SAFE_RECEIPT_REL,
  declared_sha256: sha,
});
assert.equal((gw as { status: string }).status, "PASS");

assert.ok(miCliStatus() === "PRESENT" || miCliStatus() === "MISSING");

console.log("sponsor_cortex_tests=PASS");
console.log("PUBLIC_SAFE_RECEIPT_SHA256=" + sha);
