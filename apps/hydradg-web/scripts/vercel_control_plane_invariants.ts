/**
 * Deterministic Vercel control-plane invariants.
 * Does not call Tavily, Runtype, Daytona, or HydraDB live APIs.
 * Does not rerun HydraLamp overnight experiments.
 */
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readdirSync, readFileSync, statSync } from "node:fs";
import path from "node:path";

import { detectSeedGraphGaps } from "../lib/seedgraph/gap";
import { canonicalSnapshotSha256 } from "../lib/seedgraph/canonicalSnapshot";
import { verifyCandidate } from "../lib/seedgraph/verify";
import { appendSuccessor, canonicalWriteCount } from "../lib/seedgraph/store";
import { buildProviderHealth } from "../lib/providers/health";
import { buildProviderStatus } from "../lib/providers/status";
import { publicQuarantine, type QuarantineRecord } from "../lib/providers/types";
import { redactSecrets, DOCUMENTED_SERVER_ENV } from "../lib/providers/secrets";
import { NOT_HOSTED_ON_VERCEL } from "../lib/providers/vercelBoundary";
import { cortexScaffoldHealth, tenkiScaffoldHealth, nebiusScaffoldHealth } from "../lib/providers/scaffold";
import { TENKI_EXECUTE_GATE } from "../lib/providers/tenki";

const ROOT = path.resolve(__dirname, "..");

function fixtureQuarantine(overrides: Partial<QuarantineRecord> = {}): QuarantineRecord {
  const raw_bytes = JSON.stringify({ results: [{ url: "https://docs.tavily.com/documentation/integrations/vercel" }] });
  const raw_sha256 = createHash("sha256").update(raw_bytes, "utf8").digest("hex");
  return {
    quarantine_id: `q:tavily:${raw_sha256}`,
    evidence_id: `ext:tavily:${raw_sha256.slice(0, 16)}`,
    provider: "Tavily",
    operation: "extract",
    evidence_class: "EXTERNALLY_RETRIEVED_EVIDENCE",
    custody_state: "QUARANTINED",
    source_url: "https://docs.tavily.com/documentation/integrations/vercel",
    request_id: "test",
    retrieved_at: "2026-08-27T00:00:00.000Z",
    raw_sha256,
    output_hash: raw_sha256,
    result_count: 1,
    raw_bytes,
    fcg_append: "NOT_APPENDED",
    claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
    ...overrides,
  };
}

function testGapDeterminism() {
  const a = detectSeedGraphGaps();
  const b = detectSeedGraphGaps();
  assert.equal(JSON.stringify(a), JSON.stringify(b));
  assert.ok(a.length >= 3);
  assert.equal(canonicalSnapshotSha256().length, 64);
  const ids = a.map((g) => g.gap_id);
  const sorted = [...ids].sort((x, y) => x.localeCompare(y));
  assert.deepEqual(ids, sorted);
}

function testVerifyOutcomes() {
  const gaps = detectSeedGraphGaps();
  const noUrl = gaps.find((g) => g.node_id === "sg-internal-policy" && g.kind === "MISSING_SOURCE_URL");
  assert.ok(noUrl);
  assert.equal(verifyCandidate(noUrl!, null).outcome, "ABSTAIN");

  const conflict = gaps.find((g) => g.node_id === "sg-conflict-anchor");
  assert.ok(conflict);
  assert.equal(verifyCandidate(conflict!, fixtureQuarantine()).outcome, "NEGATIVE");

  const repairable = gaps.find(
    (g) => g.node_id === "sg-tavily-vercel-docs" && g.kind === "UNRESOLVED_EXTERNAL_DOC",
  );
  assert.ok(repairable);
  assert.equal(verifyCandidate(repairable!, null, "BLOCKED").outcome, "ABSTAIN");
  assert.equal(verifyCandidate(repairable!, null, "ERROR").outcome, "ERROR");
  assert.equal(verifyCandidate(repairable!, null, "TIMEOUT").outcome, "TIMEOUT");
  assert.equal(
    verifyCandidate(repairable!, fixtureQuarantine({ result_count: 0 }), "NEGATIVE").outcome,
    "NULL",
  );
  const pass = verifyCandidate(repairable!, fixtureQuarantine(), "PASS");
  assert.equal(pass.outcome, "PASS");
  assert.equal(pass.admission.schema_check, "PASS");
  assert.equal(pass.admission.provenance_check, "PASS");
  assert.equal(pass.admission.contradiction_check, "PASS");
  assert.equal(pass.admission.authorization_check, "PASS");

  const badHash = fixtureQuarantine({ raw_sha256: "0".repeat(64) });
  assert.equal(verifyCandidate(repairable!, badHash, "PASS").outcome, "NEGATIVE");
}

function testNoCanonicalWrites() {
  appendSuccessor(
    {
      id: "successor:test",
      parent_canonical_node_id: "sg-tavily-vercel-docs",
      source_url: "https://docs.tavily.com/documentation/integrations/vercel",
      source_sha256: "ab",
      provenance_edge: "retrieved:externally-retrieved-evidence",
      identity: "SUCCESSOR_NOT_CANONICAL",
    },
    {
      identity: "SUCCESSOR_NOT_CANONICAL",
      fcg_id: "fcg-successor-test",
      parent_canonical_graph_id: "seedgraph.hydradg.vercel-control-plane.v1",
      appended_at: "2026-08-27T00:00:00.000Z",
      node_id: "successor:test",
      evidence_sha256: "ab",
    },
  );
  assert.equal(canonicalWriteCount(), 0);
}

function testPublicQuarantineStripsRaw() {
  const pub = publicQuarantine(fixtureQuarantine());
  assert.equal("raw_bytes" in pub, false);
  assert.equal(pub.evidence_class, "EXTERNALLY_RETRIEVED_EVIDENCE");
  assert.equal(pub.custody_state, "QUARANTINED");
}

async function testHealthConfiguredIsNotPass() {
  const health = await buildProviderHealth({ probe: false });
  assert.equal(health.invariant, "CONFIGURED_IS_NOT_PASS");
  for (const row of health.providers) {
    if (row.runtime_state === "NOT_PROBED") {
      assert.notEqual(row.panel_state, "PASS", `${row.provider} CONFIGURED/NOT_PROBED rendered as PASS`);
    }
    if (row.config_state === "CONFIGURED" && row.runtime_state === "NOT_PROBED") {
      assert.equal(row.panel_state, "CONFIGURED");
    }
  }
  const tavily = health.providers.find((p) => p.provider === "Tavily");
  assert.ok(tavily);
  if (tavily!.secret_state === "PRESENT") {
    assert.equal(tavily!.panel_state, "CONFIGURED");
  }
  for (const name of NOT_HOSTED_ON_VERCEL) {
    const row = health.providers.find((p) => p.provider === name);
    assert.ok(row, `missing not-hosted row ${name}`);
    assert.equal(row!.hosted_on_vercel, false);
    assert.equal(row!.panel_state, "SKIPPED");
  }
  assert.equal(cortexScaffoldHealth().panel_state, "SKIPPED");
  const tenki = tenkiScaffoldHealth();
  assert.ok(tenki.panel_state === "SKIPPED" || tenki.panel_state === "CONFIGURED");
  assert.notEqual(tenki.panel_state, "PASS");
  assert.equal(nebiusScaffoldHealth().panel_state, "SKIPPED");
}

function testRedactAndDocumentedEnv() {
  const sample = ["key=tvly-", "ABCDEFG123456 dtn_", "ABCDEFG123 rt_", "ABCDEFG Bearer abc.def"].join("");
  const red = redactSecrets(sample);
  assert.equal(red.includes(["tvly-", "ABCDEFG123456"].join("")), false);
  assert.equal(red.includes(["dtn_", "ABCDEFG123"].join("")), false);
  assert.ok(red.includes("tvly_REDACTED"));
  const expected = [
    "TAVILY_API_KEY",
    "RUNTYPE_API_KEY",
    "RUNTYPE_API_URL",
    "DAYTONA_API_KEY",
    "DAYTONA_API_URL",
    "HYDRA_DB_API_KEY",
    "HYDRADB_DATABASE",
    "HYDRADB_COLLECTION",
    "HYDRADB_API_URL",
    "TENKI_API_KEY",
  ];
  assert.deepEqual([...DOCUMENTED_SERVER_ENV], expected);
}

function walkFiles(dir: string, out: string[]) {
  const skip = new Set(["node_modules", ".next", ".git", ".vercel", "coverage"]);
  for (const name of readdirSync(dir)) {
    if (skip.has(name)) continue;
    const p = path.join(dir, name);
    const st = statSync(p);
    if (st.isDirectory()) walkFiles(p, out);
    else if (/\.(ts|tsx|js|mjs|mts|json|md|example)$/.test(name) && !name.endsWith("package-lock.json")) {
      out.push(p);
    }
  }
}

function testSecretScan() {
  const files: string[] = [];
  walkFiles(ROOT, files);
  const hits: string[] = [];
  const nextPublicKey = /NEXT_PUBLIC_[A-Z0-9_]*(KEY|SECRET|TOKEN|PASSWORD)/;
  const liveTavily = /tvly-(?!your|REDACTED)[A-Za-z0-9_-]{12,}/;
  const liveDaytona = /dtn_(?!your|REDACTED)[A-Za-z0-9]{12,}/;
  const liveRuntype = /(?<![A-Za-z])rt_(?!REDACTED)[A-Za-z0-9_]{12,}/;
  for (const file of files) {
    if (file.includes(`${path.sep}.env.`) && !file.endsWith(".example")) continue;
    const text = readFileSync(file, "utf8");
    if (nextPublicKey.test(text)) hits.push(`${file}: NEXT_PUBLIC secret-shaped var`);
    if (liveTavily.test(text)) hits.push(`${file}: live-looking tvly- token`);
    if (liveDaytona.test(text)) hits.push(`${file}: live-looking dtn_ token`);
    if (liveRuntype.test(text)) hits.push(`${file}: live-looking rt_ token`);
  }
  assert.deepEqual(hits, [], hits.join("\n"));
}

async function testProviderStatusPreserved() {
  const status = await buildProviderStatus();
  assert.equal(status.invariant, "CONFIGURED_IS_NOT_PASS");
  assert.equal(status.preserved_invariants.Tavily, "PASS");
  assert.equal(status.preserved_invariants.Runtype, "ERROR");
  assert.equal(status.preserved_invariants.Cortex, "PASS");
  assert.match(status.preserved_invariants.Daytona, /LIVE_PASS/);
  assert.equal(status.preserved_studio_receipts.Tavily.live_status, "PASS");
  assert.equal(status.preserved_studio_receipts.Runtype.live_status, "ERROR");
  assert.equal(status.preserved_studio_receipts.Cortex.live_status, "PASS");
  assert.equal(status.preserved_studio_receipts.Cortex.error_code, null);
  assert.ok(
    status.preserved_studio_receipts.Daytona.live_status === "LIVE_PASS" ||
      status.preserved_studio_receipts.Daytona.live_status === "PASS",
  );
  assert.equal(TENKI_EXECUTE_GATE.execute_allowed, false);
  for (const row of status.providers) {
    if (row.runtime_state === "NOT_PROBED") {
      assert.notEqual(row.panel_state, "PASS", `${row.provider} rendered PASS from config`);
    }
  }
}

async function main() {
  const tests: Array<[string, () => unknown]> = [
    ["gap detection is deterministic", testGapDeterminism],
    ["verify outcomes PASS/NULL/NEGATIVE/ABSTAIN/ERROR/TIMEOUT", testVerifyOutcomes],
    ["successor append never counts as canonical write", testNoCanonicalWrites],
    ["public quarantine strips raw_bytes", testPublicQuarantineStripsRaw],
    ["health CONFIGURED is not PASS", testHealthConfiguredIsNotPass],
    ["provider status preserves Studio receipts", testProviderStatusPreserved],
    ["redact + documented env", testRedactAndDocumentedEnv],
    ["secret scan of committed-shaped sources", testSecretScan],
  ];

  let failed = 0;
  for (const [name, fn] of tests) {
    try {
      await fn();
      console.log(`PASS ${name}`);
    } catch (e) {
      failed += 1;
      console.error(`FAIL ${name}`);
      console.error(e);
    }
  }
  if (failed) process.exit(1);
  console.log(`OK ${tests.length - failed}/${tests.length}`);
}

void main();
