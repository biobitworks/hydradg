/**
 * Server-only Tavily adapter via @tavily/ai-sdk.
 * All outputs are EXTERNALLY_RETRIEVED_EVIDENCE in QUARANTINED custody.
 * Never mutates canonical SeedGraph or FCG.
 */
import { createHash } from "node:crypto";
import { createTavilyAiSdkTools, tavilyApiKeyStatus } from "../sponsors/tavilyAiSdk";
import { redactSecrets } from "./secrets";
import type { QuarantineRecord } from "./types";

export type TavilyOperation = "search" | "extract" | "crawl" | "map";

export type TavilyRetrieveResult = {
  operation: TavilyOperation;
  status: "PASS" | "NEGATIVE" | "ERROR" | "BLOCKED" | "TIMEOUT";
  secret_state: "PRESENT" | "MISSING" | "INVALID_PLACEHOLDER";
  request_id: string | null;
  source_urls: string[];
  raw_sha256: string | null;
  output_hash: string | null;
  evidence_class: "EXTERNALLY_RETRIEVED_EVIDENCE";
  custody_state: "QUARANTINED";
  fcg_append: "NOT_APPENDED";
  seedgraph_canonical_write: false;
  quarantine: QuarantineRecord | null;
  error_code: string | null;
  error_summary: string | null;
  claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE";
};

function sha256Text(value: string): string {
  return createHash("sha256").update(value, "utf8").digest("hex");
}

function canonicalRaw(value: unknown): string {
  return JSON.stringify(value);
}

function collectUrls(payload: unknown): string[] {
  const urls: string[] = [];
  const walk = (v: unknown) => {
    if (!v) return;
    if (typeof v === "string" && /^https?:\/\//i.test(v)) urls.push(v);
    if (Array.isArray(v)) v.forEach(walk);
    if (typeof v === "object") {
      for (const [k, val] of Object.entries(v as Record<string, unknown>)) {
        if (k === "url" && typeof val === "string") urls.push(val);
        else walk(val);
      }
    }
  };
  walk(payload);
  return [...new Set(urls)];
}

function resultCount(payload: unknown, urls: string[]): number {
  if (payload && typeof payload === "object") {
    const rec = payload as Record<string, unknown>;
    if (Array.isArray(rec.results)) return rec.results.length;
    if (typeof rec.raw_content === "string" && rec.raw_content.length > 0) return 1;
    if (typeof rec.content === "string" && rec.content.length > 0) return 1;
    if (Array.isArray(rec.base_url) || typeof rec.base_url === "string") {
      if (urls.length > 0) return urls.length;
    }
  }
  return urls.length;
}

function requestIdOf(payload: unknown): string | null {
  if (payload && typeof payload === "object" && "request_id" in payload) {
    const id = (payload as { request_id?: unknown }).request_id;
    return typeof id === "string" ? id : null;
  }
  return null;
}

export async function tavilyRetrieve(params: {
  operation: TavilyOperation;
  query?: string;
  url?: string;
  urls?: string[];
}): Promise<TavilyRetrieveResult> {
  const secret = tavilyApiKeyStatus();
  const base = {
    operation: params.operation,
    secret_state: secret,
    evidence_class: "EXTERNALLY_RETRIEVED_EVIDENCE" as const,
    custody_state: "QUARANTINED" as const,
    fcg_append: "NOT_APPENDED" as const,
    seedgraph_canonical_write: false as const,
    claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE" as const,
  };

  if (secret !== "PRESENT") {
    return {
      ...base,
      status: "BLOCKED",
      request_id: null,
      source_urls: [],
      raw_sha256: null,
      output_hash: null,
      quarantine: null,
      error_code: "TAVILY_API_KEY_" + secret,
      error_summary: "Tavily API key not usable in this runtime.",
    };
  }

  try {
    const tools = await createTavilyAiSdkTools({ searchDepth: "basic", maxResults: 5 });
    let result: unknown;
    if (params.operation === "search") {
      if (!params.query) throw new Error("query required for search");
      result = await tools.tavilySearch.execute!(
        { query: params.query, searchDepth: "basic" },
        { toolCallId: "hydradg-tavily-search", messages: [] },
      );
    } else if (params.operation === "extract") {
      const urls = params.urls || (params.url ? [params.url] : []);
      if (!urls.length) throw new Error("url(s) required for extract");
      result = await tools.tavilyExtract.execute!(
        { urls },
        { toolCallId: "hydradg-tavily-extract", messages: [] },
      );
    } else if (params.operation === "crawl") {
      if (!params.url) throw new Error("url required for crawl");
      result = await tools.tavilyCrawl.execute!(
        { url: params.url, maxDepth: 1 },
        { toolCallId: "hydradg-tavily-crawl", messages: [] },
      );
    } else {
      if (!params.url) throw new Error("url required for map");
      result = await tools.tavilyMap.execute!(
        { url: params.url, maxDepth: 1 },
        { toolCallId: "hydradg-tavily-map", messages: [] },
      );
    }

    const raw = canonicalRaw(result);
    const raw_sha256 = sha256Text(raw);
    const urls = collectUrls(result);
    const result_count = resultCount(result, urls);
    const empty = result_count < 1;

    const evidence_id = `ext:tavily:${raw_sha256.slice(0, 16)}`;
    const quarantine: QuarantineRecord = {
      quarantine_id: `q:tavily:${raw_sha256}`,
      evidence_id,
      provider: "Tavily",
      operation: params.operation,
      evidence_class: "EXTERNALLY_RETRIEVED_EVIDENCE",
      custody_state: "QUARANTINED",
      source_url: params.url || urls[0] || null,
      request_id: requestIdOf(result),
      retrieved_at: new Date().toISOString(),
      raw_sha256,
      output_hash: raw_sha256,
      result_count,
      raw_bytes: raw,
      fcg_append: "NOT_APPENDED",
      claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
    };

    return {
      ...base,
      status: empty ? "NEGATIVE" : "PASS",
      request_id: quarantine.request_id,
      source_urls: urls,
      raw_sha256,
      output_hash: raw_sha256,
      quarantine,
      error_code: empty ? "EMPTY_RETRIEVAL" : null,
      error_summary: empty ? "Tavily returned no source URLs/results." : null,
    };
  } catch (e) {
    const msg = redactSecrets(String((e as Error).message || e));
    const isTimeout = /timeout/i.test(msg);
    return {
      ...base,
      status: isTimeout ? "TIMEOUT" : "ERROR",
      request_id: null,
      source_urls: [],
      raw_sha256: null,
      output_hash: null,
      quarantine: null,
      error_code: isTimeout ? "TIMEOUT" : "TAVILY_RETRIEVE_FAILED",
      error_summary: msg.slice(0, 240),
    };
  }
}
