/**
 * yappy.biz public Web API — NOT Mitosis Yappy / not mitosislabs.
 * Keyless read-only product metadata API. EXTERNALLY_RETRIEVED_EVIDENCE only.
 * Docs: https://yappy.biz/api/
 */
import { createHash } from "node:crypto";
import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";

export const YAPPY_BIZ_API_BASE = "https://yappy.biz/api/v1";
export const YAPPY_BIZ_DOCS = "https://yappy.biz/api/";
export const YAPPY_BIZ_OPENAPI = "https://yappy.biz/openapi.json";

function sha256Bytes(data: Buffer | string): string {
  return createHash("sha256").update(data).digest("hex");
}

export type YappyBizMissionReceipt = {
  schema: "sponsor.yappy_biz.api_probe_receipt.v1";
  mission_id: "ANB-SP-YAPPY-BIZ-API-001";
  provider: "Yappy.biz";
  product: "Yappy Web API (macOS voice agent product metadata)";
  operation: "public_api_index_and_latest_release";
  identity_note: string;
  docs_ref: string;
  openapi_url: string;
  base_url: string;
  probes: Array<{
    path: string;
    http_status: number | null;
    ok: boolean;
    raw_artifact_path: string | null;
    raw_sha256: string | null;
    error: string | null;
  }>;
  latest_release_version: string | null;
  fcg_append: "NOT_APPENDED";
  status: "PASS" | "ERROR" | "TIMEOUT";
  error_code: string | null;
  error_summary: string | null;
  claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE";
  signature_state: "NOT_SIGNED";
  recorded_at_utc: string;
};

async function fetchProbe(
  url: string,
  timeoutMs = 20_000,
): Promise<{ status: number | null; body: string; timedOut: boolean; error: string | null }> {
  const ac = new AbortController();
  const t = setTimeout(() => ac.abort(), timeoutMs);
  try {
    const res = await fetch(url, {
      headers: { Accept: "application/json" },
      signal: ac.signal,
    });
    const body = await res.text();
    return { status: res.status, body, timedOut: false, error: null };
  } catch (e) {
    const msg = String((e as Error).message || e);
    return {
      status: null,
      body: "",
      timedOut: /abort/i.test(msg),
      error: msg,
    };
  } finally {
    clearTimeout(t);
  }
}

export async function runYappyBizApiMission(params: {
  repoRoot: string;
}): Promise<YappyBizMissionReceipt> {
  const recorded_at_utc = new Date().toISOString();
  const outDir = path.join(
    params.repoRoot,
    "eval",
    "agent_native_sponsors_20260827",
    "yappy_biz",
  );
  const rawDir = path.join(outDir, "raw");
  mkdirSync(rawDir, { recursive: true });

  const endpoints = [
    `${YAPPY_BIZ_API_BASE}`,
    `${YAPPY_BIZ_API_BASE}/releases/latest`,
    YAPPY_BIZ_OPENAPI,
  ];

  const probes: YappyBizMissionReceipt["probes"] = [];
  let timedOut = false;
  let latest: string | null = null;

  for (const url of endpoints) {
    const r = await fetchProbe(url);
    if (r.timedOut) timedOut = true;
    const slug = url.replace(/https?:\/\//, "").replace(/[^\w.-]+/g, "_");
    let raw_artifact_path: string | null = null;
    let raw_sha256: string | null = null;
    if (r.body) {
      const fp = path.join(rawDir, `${slug}.json`);
      writeFileSync(fp, r.body.endsWith("\n") ? r.body : r.body + "\n");
      raw_artifact_path = path.relative(params.repoRoot, fp);
      raw_sha256 = sha256Bytes(r.body);
    }
    if (url.endsWith("/releases/latest") && r.status === 200) {
      try {
        const j = JSON.parse(r.body) as { version?: string };
        latest = j.version || null;
      } catch {
        /* ignore */
      }
    }
    probes.push({
      path: url,
      http_status: r.status,
      ok: r.status === 200,
      raw_artifact_path,
      raw_sha256,
      error: r.error,
    });
  }

  const allOk = probes.every((p) => p.ok);
  const status: YappyBizMissionReceipt["status"] = timedOut
    ? "TIMEOUT"
    : allOk
      ? "PASS"
      : "ERROR";

  const receipt: YappyBizMissionReceipt = {
    schema: "sponsor.yappy_biz.api_probe_receipt.v1",
    mission_id: "ANB-SP-YAPPY-BIZ-API-001",
    provider: "Yappy.biz",
    product: "Yappy Web API (macOS voice agent product metadata)",
    operation: "public_api_index_and_latest_release",
    identity_note:
      "Distinct from Mitosis Yappy (mitosislabs / mi agents). This is yappy.biz public product API only.",
    docs_ref: YAPPY_BIZ_DOCS,
    openapi_url: YAPPY_BIZ_OPENAPI,
    base_url: YAPPY_BIZ_API_BASE,
    probes,
    latest_release_version: latest,
    fcg_append: "NOT_APPENDED",
    status,
    error_code: allOk ? null : timedOut ? "YAPPY_BIZ_TIMEOUT" : "YAPPY_BIZ_HTTP_ERROR",
    error_summary: allOk
      ? null
      : probes
          .filter((p) => !p.ok)
          .map((p) => `${p.path}→${p.http_status || p.error}`)
          .join("; "),
    claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
    signature_state: "NOT_SIGNED",
    recorded_at_utc,
  };

  writeFileSync(
    path.join(outDir, "YAPPY_BIZ_API_MISSION_RECEIPT.json"),
    JSON.stringify(receipt, null, 2) + "\n",
  );
  return receipt;
}
