#!/usr/bin/env npx tsx
/** A. GUM Doctor discovery + B. sponsor discovery matrix bootstrap */
import { writeFileSync, mkdirSync } from "node:fs";
import path from "node:path";
import * as gumModNs from "../lib/sponsors/gumDoctor.ts";
import * as fixturesModNs from "../lib/hydralamp/fixtures.ts";
import { unwrapHydraLampMod } from "./hydralamp_tsx_import.mts";

const { discoverGumDoctor } = unwrapHydraLampMod(gumModNs as Record<string, unknown>) as {
  discoverGumDoctor: typeof import("../lib/sponsors/gumDoctor.ts").discoverGumDoctor;
};

const { repoRoot } = unwrapHydraLampMod(fixturesModNs as Record<string, unknown>) as {
  repoRoot: () => string;
};

const root = repoRoot();
const evalDir = path.join(root, "eval", "agent_native_sponsors_20260827");
mkdirSync(evalDir, { recursive: true });

const gum = discoverGumDoctor(root);
console.log("GUM_DOCTOR_STATE=" + gum.GUM_DOCTOR_STATE);
console.log("SPONSOR_SECRET_INJECTION=" + gum.SPONSOR_SECRET_INJECTION);

const matrix = {
  schema: "sponsor.discovery_matrix.v1",
  recorded_at_utc: new Date().toISOString(),
  execution_host: "magicSTUDIObox.local",
  gum_doctor_state: gum.GUM_DOCTOR_STATE,
  sponsor_secret_injection: gum.SPONSOR_SECRET_INJECTION,
  providers: [
    {
      provider: "Runtype",
      priority: "P0",
      product: "Runtype API / @runtypelabs/sdk",
      official_docs: "https://www.npmjs.com/package/@runtypelabs/sdk",
      auth_mechanism: "API key (RUNTYPE_API_KEY)",
      required_secret_names: ["RUNTYPE_API_KEY"],
      sdk_or_cli: "@runtypelabs/sdk",
      minimal_operation: "modelConfigs.list or runWithLocalTools CONTROL lane",
      state: "CONFIGURED",
      evidence_notes: "HydraLamp integration exists; prior PROBE_CONTROL_SMOKE lane ERROR preserved.",
    },
    {
      provider: "Tavily",
      priority: "P0",
      product: "Tavily Agent / tvly CLI + @tavily/ai-sdk (Vercel AI SDK)",
      official_docs: "https://docs.tavily.com/documentation/integrations/vercel#benefits-of-tavily-+-vercel-ai-sdk",
      auth_mechanism: "OAuth via tvly login (CLI); TAVILY_API_KEY for @tavily/ai-sdk tools",
      required_secret_names: ["TAVILY_API_KEY"],
      sdk_or_cli: "tvly CLI, @tavily/ai-sdk, ai@6",
      minimal_operation: "tvly extract <url> and/or @tavily/ai-sdk tavilyExtract tool",
      state: "CONFIGURED",
      evidence_notes: "CLI extract PASS preserved; AI SDK package wired (peer ai@6). Live AI SDK extract blocked until TAVILY_API_KEY set.",
    },
    {
      provider: "Mitosis Cortex",
      priority: "P0",
      product: "Cortex memory / mi cortex / @mitosislabs/sdk",
      official_docs: "https://mitosislabs.ai/developers/cli/overview",
      auth_mechanism: "mi login OAuth or MI_API_KEY=mi_... (dashboard user menu); optional MI_OFFICE_ID from mi offices list",
      required_secret_names: ["MI_API_KEY"],
      sdk_or_cli: "mi CLI v0.26.0, @mitosislabs/sdk",
      minimal_operation: "mi cortex remember + recall roundtrip against verified HydraDG receipt (--office)",
      state: "CONFIGURED",
      evidence_notes: "mi auth PASS; office resolved; Cortex memory may still be trial-locked — roundtrip mission records ERROR/MISS without mutating FCG.",
    },
    {
      provider: "Mitosis Yappy",
      priority: "P1",
      product: "Yappy computer-use agents (mitosislabs / mi agents)",
      official_docs: "https://mitosislabs.ai/developers/cli/overview",
      auth_mechanism: "mi login OAuth or MI_API_KEY; office/agent workspace",
      required_secret_names: ["MI_API_KEY"],
      sdk_or_cli: "mi CLI v0.26.0, @mitosislabs/sdk",
      minimal_operation: "mi agents list + bounded interaction with hired agent",
      state: "CONFIGURED",
      evidence_notes:
        "Auth PASS; office agents list empty — computer-use blocked until hire. Distinct from yappy.biz.",
    },
    {
      provider: "Yappy.biz",
      priority: "P1",
      product: "Yappy Web API (macOS voice agent product metadata)",
      official_docs: "https://yappy.biz/api/",
      auth_mechanism: "None for reads (keyless); optional OAuth raises rate limit",
      required_secret_names: [],
      sdk_or_cli: "HTTPS REST / OpenAPI / MCP https://yappy.biz/mcp",
      minimal_operation: "GET /api/v1 + /releases/latest",
      state: "CONFIGURED",
      evidence_notes: "Public product API probe; NOT Mitosis Yappy computer-use.",
    },
    {
      provider: "Immersive Commons",
      priority: "P1",
      product: "IC MCP / A2A agent surface (event anb-hack-01)",
      official_docs: "https://www.immersivecommons.com/developers",
      auth_mechanism: "agt_ bearer token via device-code flow; 10 public MCP tools without token",
      required_secret_names: [],
      sdk_or_cli: "@immersivecommons/sdk",
      minimal_operation: "MCP manifest discovery + public tool probe",
      state: "DISCOVERED",
      evidence_notes: "Event credentials not copied to repo; MCP manifest fetchable without agt_ token.",
    },
    {
      provider: "Cotal",
      priority: "P1",
      product: "Cotal agent mesh (NATS/A2A)",
      official_docs: "https://docs.cotal.ai/",
      auth_mechanism: "JWT mesh auth via cotal up (mesh launch deferred)",
      required_secret_names: [],
      sdk_or_cli: "cotal CLI 0.33.1 (get.cotal.ai)",
      minimal_operation: "cotal setup --yes + HydraDG evidence gateway bounded transaction",
      state: "CONFIGURED",
      evidence_notes: "CLI installed + setup complete; cotal up mesh NOT_ATTEMPTED in bounded mission.",
    },
    {
      provider: "Hacker Bob",
      priority: "P2",
      product: "hacker-bob MCP security runtime",
      official_docs: "https://www.npmjs.com/package/hacker-bob",
      auth_mechanism: "local MCP install; authorized testing only",
      required_secret_names: [],
      sdk_or_cli: "hacker-bob / hacker-bob-cc",
      minimal_operation: "one bounded security scan with raw report hash",
      state: "DISCOVERED",
      evidence_notes: "Package documented; full hunt not run without explicit scoped authorization.",
    },
    {
      provider: "Tenki",
      priority: "P2",
      product: "Tenki Sandbox microVM",
      official_docs: "https://tenki.cloud/docs",
      auth_mechanism: "tenki login or TENKI_API_KEY=tk_...",
      required_secret_names: ["TENKI_API_KEY"],
      sdk_or_cli: "tenki CLI v1.3.5, @tenkicloud/sandbox",
      minimal_operation: "sandbox create → exec uname → terminate with receipt",
      state: "CONFIGURED",
      evidence_notes: "tenki CLI + sandbox mission PASS when TENKI_API_KEY present. Infra demo only — not scientific execution authority.",
    },
    {
      provider: "Nebius",
      priority: "OPTIONAL",
      product: "Nebius Serverless GPU / inference",
      official_docs: "https://nebius.com/",
      auth_mechanism: "Nebius account API credentials",
      required_secret_names: ["NEBIUS_API_KEY"],
      sdk_or_cli: "Nebius API",
      minimal_operation: "one bounded API/compute smoke",
      state: "SKIPPED",
      evidence_notes: "Non-blocking; discovery only.",
    },
    {
      provider: "Ultimate Fighting Agents",
      priority: "SUBMISSION_ONLY",
      product: "Hackathon track submission",
      official_docs: "https://luma.com/agentnativebuildershackathon",
      auth_mechanism: "NOT_APPLICABLE",
      required_secret_names: [],
      sdk_or_cli: "NOT_APPLICABLE",
      minimal_operation: "submission readiness artifact from existing HydraLamp perturbations",
      state: "NOT_APPLICABLE",
      evidence_notes: "Guaranteed approval track; $15,000 prize pool — no API integration.",
    },
  ],
  infrastructure: [
    {
      provider: "Daytona",
      lane: "INFRASTRUCTURE",
      anb_sponsor: false,
      product: "Daytona isolated sandboxes",
      official_docs: "https://www.daytona.io/docs/en/python-sdk/",
      auth_mechanism: "API key (DAYTONA_API_KEY) against DAYTONA_API_URL",
      required_secret_names: ["DAYTONA_API_KEY"],
      sdk_or_cli: "daytona Python SDK",
      minimal_operation: "create ephemeral sandbox, exec deterministic python smoke, delete",
      state: "CONFIGURED",
      evidence_notes:
        "Not recorded as an Agent Natives sponsor. External compute demonstration only; magicSTUDIObox.local remains scientific execution authority.",
    },
  ],
};

writeFileSync(
  path.join(evalDir, "SPONSOR_DISCOVERY_MATRIX.json"),
  JSON.stringify(matrix, null, 2) + "\n",
);
console.log("WROTE SPONSOR_DISCOVERY_MATRIX.json");
