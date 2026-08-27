#!/usr/bin/env npx tsx
/** H. Immersive Commons MCP discovery (public manifest; no event secrets in repo). */
import { writeFileSync, mkdirSync } from "node:fs";
import path from "node:path";
import * as fixturesModNs from "../lib/hydralamp/fixtures.ts";
import { unwrapHydraLampMod } from "./hydralamp_tsx_import.mts";

const { repoRoot, sha256Text } = unwrapHydraLampMod(fixturesModNs as Record<string, unknown>) as {
  repoRoot: () => string;
  sha256Text: (s: string) => string;
};

const MCP_MANIFEST_URL = "https://www.immersivecommons.com/.well-known/mcp.json";
const EVENT_ID = "anb-hack-01";

async function main() {
  const root = repoRoot();
  const outDir = path.join(root, "eval", "agent_native_sponsors_20260827", "immersive_commons");
  mkdirSync(outDir, { recursive: true });
  const started = new Date().toISOString();

  let manifest: Record<string, unknown> | null = null;
  let fetchError: string | null = null;
  try {
    const res = await fetch(MCP_MANIFEST_URL);
    if (!res.ok) throw new Error(`HTTP_${res.status}`);
    manifest = (await res.json()) as Record<string, unknown>;
  } catch (e) {
    fetchError = String((e as Error).message || e).slice(0, 200);
  }

  const tools = Array.isArray(manifest?.tools)
    ? manifest!.tools
    : [];
  const publicTools = Array.isArray(manifest?.public_tools)
    ? manifest!.public_tools
    : [];

  const receipt = {
    schema: "sponsor.immersive_commons.discovery_receipt.v1",
    mission_id: "ANB-SP-IC-MCP-DISCOVERY-001",
    provider: "Immersive Commons",
    event_reference: EVENT_ID,
    operation: "mcp_manifest_discovery",
    started_at: started,
    completed_at: new Date().toISOString(),
    mcp_url: "https://www.immersivecommons.com/api/mcp",
    manifest_url: MCP_MANIFEST_URL,
    status: manifest ? "PASS" : "ERROR",
    error_summary: fetchError,
    capabilities: {
      manifest_name: manifest?.name ?? null,
      manifest_version: manifest?.version ?? null,
      tool_count: tools.length,
      public_tool_count: publicTools.length,
      public_tools_sample: publicTools.slice(0, 5),
    },
    unknown_agent_discovery: {
      can_discover_hydradg_via_ic: "NOT_TESTED",
      note: "HydraDG evidence gateway exposed separately; IC MCP is event-native surface.",
    },
    bounded_transaction: "NOT_ATTEMPTED",
    event_credentials_in_repo: false,
    claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
    signature_state: "NOT_SIGNED",
  };

  const receiptPath = path.join(outDir, "IMMERSIVE_COMMONS_MISSION_RECEIPT.json");
  writeFileSync(receiptPath, JSON.stringify(receipt, null, 2) + "\n");
  if (manifest) {
    writeFileSync(path.join(outDir, "MCP_MANIFEST_SNAPSHOT.json"), JSON.stringify(manifest, null, 2) + "\n");
  }
  writeFileSync(path.join(outDir, "RECEIPT.sha256"), sha256Text(JSON.stringify(receipt)) + "\n");

  console.log("IMMERSIVE_COMMONS_STATE=" + (manifest ? "DISCOVERED" : "ERROR"));
  console.log("PUBLIC_TOOLS=" + publicTools.length);
  process.exit(manifest ? 0 : 1);
}

void main();
