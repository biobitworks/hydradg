/**
 * Tavily + Vercel AI SDK (`@tavily/ai-sdk`) wiring.
 * Tools are EXTERNALLY_RETRIEVED_EVIDENCE candidates — never direct FCG append.
 * Docs: https://docs.tavily.com/documentation/integrations/vercel
 *
 * Uses dynamic import() because @tavily/ai-sdk is ESM-only (no CJS export).
 */
import { createHash } from "node:crypto";
import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { loadHydraLampServerEnv } from "../hydralamp/env";

export const TAVILY_AI_SDK_DOCS =
  "https://docs.tavily.com/documentation/integrations/vercel#benefits-of-tavily-+-vercel-ai-sdk";

export const TAVILY_AI_SDK_BENEFITS = [
  "Pre-built Tools",
  "Type-Safe",
  "Real-time Information",
  "Optimized for LLMs",
  "Multiple Capabilities (search/extract/crawl/map)",
  "Easy Integration with Vercel AI SDK v5/v6",
  "Flexible Configuration",
  "Production-Ready",
] as const;

export type TavilyAiSdkToolName =
  | "tavilySearch"
  | "tavilyExtract"
  | "tavilyCrawl"
  | "tavilyMap";

type ToolLike = {
  description?: string;
  execute?: (input: unknown, opts: unknown) => Promise<unknown> | unknown;
};

function sha256Bytes(data: Buffer | string): string {
  return createHash("sha256").update(data).digest("hex");
}

function isPlaceholder(value: string | undefined): boolean {
  if (!value) return true;
  const v = value.trim();
  if (!v) return true;
  if (/^your_.*_here$/i.test(v)) return true;
  if (/^tvly-your/i.test(v)) return true;
  if (/^<[^>]+>$/.test(v)) return true;
  return false;
}

export function tavilyApiKeyStatus(): "PRESENT" | "MISSING" {
  loadHydraLampServerEnv();
  return isPlaceholder(process.env.TAVILY_API_KEY) ? "MISSING" : "PRESENT";
}

async function loadTavilyAiSdk(): Promise<{
  tavilySearch: (opts?: Record<string, unknown>) => ToolLike;
  tavilyExtract: (opts?: Record<string, unknown>) => ToolLike;
  tavilyCrawl: (opts?: Record<string, unknown>) => ToolLike;
  tavilyMap: (opts?: Record<string, unknown>) => ToolLike;
}> {
  return import("@tavily/ai-sdk") as Promise<{
    tavilySearch: (opts?: Record<string, unknown>) => ToolLike;
    tavilyExtract: (opts?: Record<string, unknown>) => ToolLike;
    tavilyCrawl: (opts?: Record<string, unknown>) => ToolLike;
    tavilyMap: (opts?: Record<string, unknown>) => ToolLike;
  }>;
}

/** Build AI SDK tool map (requires TAVILY_API_KEY at execute time). */
export async function createTavilyAiSdkTools(options?: {
  searchDepth?: "basic" | "advanced";
  maxResults?: number;
}): Promise<Record<TavilyAiSdkToolName, ToolLike>> {
  const mod = await loadTavilyAiSdk();
  return {
    tavilySearch: mod.tavilySearch({
      searchDepth: options?.searchDepth || "advanced",
      maxResults: options?.maxResults || 5,
    }),
    tavilyExtract: mod.tavilyExtract({ format: "markdown" }),
    tavilyCrawl: mod.tavilyCrawl(),
    tavilyMap: mod.tavilyMap(),
  };
}

export async function listTavilyAiSdkTools(): Promise<
  Array<{ name: TavilyAiSdkToolName; description: string }>
> {
  const tools = await createTavilyAiSdkTools();
  return (Object.keys(tools) as TavilyAiSdkToolName[]).map((name) => ({
    name,
    description: String(tools[name].description || ""),
  }));
}

export type TavilyAiSdkMissionReceipt = {
  schema: "sponsor.tavily_ai_sdk.mission_receipt.v1";
  mission_id: "ANB-SP-TAVILY-AISDK-001";
  provider: "Tavily";
  product: "@tavily/ai-sdk + Vercel AI SDK";
  operation: "ai_sdk_tool_wiring_and_optional_extract";
  docs_ref: string;
  benefits: readonly string[];
  package_import: "PASS" | "ERROR";
  tools: Array<{ name: TavilyAiSdkToolName; description: string }>;
  TAVILY_API_KEY: "PRESENT" | "MISSING";
  live_extract: {
    attempted: boolean;
    source_url: string | null;
    status: "PASS" | "ERROR" | "BLOCKED" | "NOT_ATTEMPTED";
    raw_artifact_path: string | null;
    raw_artifact_sha256: string | null;
    error_summary: string | null;
  };
  fco_proposal: {
    action: "QUARANTINE_EXTERNAL_EVIDENCE";
    claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE";
    admit_decision: "PENDING_CUSTODY_REVIEW";
    note: string;
  };
  fcg_append: "NOT_APPENDED";
  status: "PASS" | "ERROR" | "BLOCKED";
  claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE";
  signature_state: "NOT_SIGNED";
  recorded_at_utc: string;
};

export async function runTavilyAiSdkMission(params: {
  repoRoot: string;
  sourceUrl?: string;
}): Promise<TavilyAiSdkMissionReceipt> {
  const recorded_at_utc = new Date().toISOString();
  const outDir = path.join(
    params.repoRoot,
    "eval",
    "agent_native_sponsors_20260827",
    "tavily",
  );
  mkdirSync(path.join(outDir, "raw"), { recursive: true });

  let tools: Array<{ name: TavilyAiSdkToolName; description: string }> = [];
  let package_import: "PASS" | "ERROR" = "PASS";
  try {
    tools = await listTavilyAiSdkTools();
  } catch (e) {
    package_import = "ERROR";
    const receipt: TavilyAiSdkMissionReceipt = {
      schema: "sponsor.tavily_ai_sdk.mission_receipt.v1",
      mission_id: "ANB-SP-TAVILY-AISDK-001",
      provider: "Tavily",
      product: "@tavily/ai-sdk + Vercel AI SDK",
      operation: "ai_sdk_tool_wiring_and_optional_extract",
      docs_ref: TAVILY_AI_SDK_DOCS,
      benefits: TAVILY_AI_SDK_BENEFITS,
      package_import,
      tools: [],
      TAVILY_API_KEY: tavilyApiKeyStatus(),
      live_extract: {
        attempted: false,
        source_url: null,
        status: "NOT_ATTEMPTED",
        raw_artifact_path: null,
        raw_artifact_sha256: null,
        error_summary: String((e as Error).message || e),
      },
      fco_proposal: {
        action: "QUARANTINE_EXTERNAL_EVIDENCE",
        claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
        admit_decision: "PENDING_CUSTODY_REVIEW",
        note: "Tavily AI SDK output must not write directly to canonical FCG state.",
      },
      fcg_append: "NOT_APPENDED",
      status: "ERROR",
      claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
      signature_state: "NOT_SIGNED",
      recorded_at_utc,
    };
    writeFileSync(
      path.join(outDir, "TAVILY_AISDK_MISSION_RECEIPT.json"),
      JSON.stringify(receipt, null, 2) + "\n",
    );
    return receipt;
  }

  const keyStatus = tavilyApiKeyStatus();
  const sourceUrl =
    params.sourceUrl ||
    "https://docs.tavily.com/documentation/integrations/vercel";

  const live_extract: TavilyAiSdkMissionReceipt["live_extract"] = {
    attempted: false,
    source_url: sourceUrl,
    status: "NOT_ATTEMPTED",
    raw_artifact_path: null,
    raw_artifact_sha256: null,
    error_summary: null,
  };

  if (keyStatus === "MISSING") {
    live_extract.status = "BLOCKED";
    live_extract.error_summary =
      "TAVILY_API_KEY missing; package wiring verified. Existing tvly CLI mission remains authoritative for extract PASS.";
  } else {
    live_extract.attempted = true;
    try {
      const toolMap = await createTavilyAiSdkTools();
      const extractTool = toolMap.tavilyExtract;
      if (!extractTool.execute) {
        throw new Error("tavilyExtract.execute unavailable");
      }
      const result = await extractTool.execute(
        { urls: [sourceUrl] },
        { toolCallId: "hydradg-tavily-aisdk-extract", messages: [] },
      );
      const rawPath = path.join(outDir, "raw", "TAVILY_AISDK_EXTRACT_RAW.json");
      const payload = JSON.stringify(result, null, 2) + "\n";
      writeFileSync(rawPath, payload);
      live_extract.raw_artifact_path = path.relative(params.repoRoot, rawPath);
      live_extract.raw_artifact_sha256 = sha256Bytes(payload);
      live_extract.status = "PASS";
    } catch (e) {
      live_extract.status = "ERROR";
      live_extract.error_summary = String((e as Error).message || e).replace(
        /tvly-[A-Za-z0-9_-]+/g,
        "tvly_REDACTED",
      );
    }
  }

  const status: TavilyAiSdkMissionReceipt["status"] =
    package_import === "PASS" &&
    (live_extract.status === "PASS" || live_extract.status === "BLOCKED")
      ? live_extract.status === "PASS"
        ? "PASS"
        : "BLOCKED"
      : "ERROR";

  const receipt: TavilyAiSdkMissionReceipt = {
    schema: "sponsor.tavily_ai_sdk.mission_receipt.v1",
    mission_id: "ANB-SP-TAVILY-AISDK-001",
    provider: "Tavily",
    product: "@tavily/ai-sdk + Vercel AI SDK",
    operation: "ai_sdk_tool_wiring_and_optional_extract",
    docs_ref: TAVILY_AI_SDK_DOCS,
    benefits: TAVILY_AI_SDK_BENEFITS,
    package_import,
    tools,
    TAVILY_API_KEY: keyStatus,
    live_extract,
    fco_proposal: {
      action: "QUARANTINE_EXTERNAL_EVIDENCE",
      claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
      admit_decision: "PENDING_CUSTODY_REVIEW",
      note: "Tavily AI SDK output must not write directly to canonical FCG state.",
    },
    fcg_append: "NOT_APPENDED",
    status,
    claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
    signature_state: "NOT_SIGNED",
    recorded_at_utc,
  };

  writeFileSync(
    path.join(outDir, "TAVILY_AISDK_MISSION_RECEIPT.json"),
    JSON.stringify(receipt, null, 2) + "\n",
  );
  return receipt;
}
