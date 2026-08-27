/**
 * Independent HydraDG recompute of the Daytona smoke payload hash.
 * Does not call Daytona. Does not read secrets.
 */
import assert from "node:assert/strict";
import { createHash } from "node:crypto";

const expected = createHash("sha256").update("hydradg-daytona-smoke").digest("hex");
assert.equal(expected, "3e4e33cb4ad0a5c951dd46a73ca611a308bb250f04bc48dee85dde317c4318a0");
console.log("daytona_payload_recompute=PASS");
console.log("EXPECTED_SMOKE_HASH=" + expected);
