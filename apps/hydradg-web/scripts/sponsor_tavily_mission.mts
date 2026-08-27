#!/usr/bin/env npx tsx
/** C. Tavily custody adapter — one bounded extract (or load existing artifact). */
import path from "node:path";
import { writeFileSync, mkdirSync } from "node:fs";
import * as fixturesModNs from "../lib/hydralamp/fixtures.ts";
import * as tavilyModNs from "../lib/sponsors/tavilyAdapter.ts";
import { unwrapHydraLampMod } from "./hydralamp_tsx_import.mts";

const { loadTavilyExtractFromFile, runTavilyExtractMission } = unwrapHydraLampMod(
  tavilyModNs as Record<string, unknown>,
) as typeof import("../lib/sponsors/tavilyAdapter.ts");

const { repoRoot } = unwrapHydraLampMod(fixturesModNs as Record<string, unknown>) as {
  repoRoot: () => string;
};

const root = repoRoot();
const existingRel =
  "eval/agent_native_sponsors_20260827/tavily/raw/TAVILY_EXTRACT_CORTEX_DOCS.json";
const existing = loadTavilyExtractFromFile(root, existingRel);

if (existing && existing.status === "PASS") {
  const receiptPath = path.join(root, "eval", "agent_native_sponsors_20260827", "tavily", "TAVILY_MISSION_RECEIPT.json");
  mkdirSync(path.dirname(receiptPath), { recursive: true });
  writeFileSync(receiptPath, JSON.stringify(existing, null, 2) + "\n");
  console.log("TAVILY_STATE=CONFIGURED");
  console.log("TAVILY_MISSION=" + existing.status);
  console.log("RAW_SHA256=" + existing.raw_artifact_sha256);
  console.log("REQUEST_ID=" + (existing.request_id || "null"));
  process.exit(0);
}

const { mission } = runTavilyExtractMission({
  repoRoot: root,
  sourceUrl: "https://docs.cortexmemory.dev/getting-started/introduction",
});
console.log("TAVILY_STATE=" + mission.discovery_state);
console.log("TAVILY_MISSION=" + mission.status);
console.log("RAW_SHA256=" + (mission.raw_artifact_sha256 || "null"));
process.exit(mission.status === "PASS" ? 0 : 1);
