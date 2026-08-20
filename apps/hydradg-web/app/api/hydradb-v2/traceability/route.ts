import { NextResponse } from "next/server";

import { hostedHydraDBConfig, hostedHydraDBRequest } from "@/lib/hydradbHosted";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function discoveredCollections(payload: any): string[] {
  const data = payload?.data;
  const values = data?.collections || data?.sub_tenant_ids || payload?.collections || [];
  return Array.isArray(values) ? values.map(String).filter(Boolean) : [];
}

export async function GET() {
  const cfg = hostedHydraDBConfig();
  if (!cfg.apiKey || !cfg.database) {
    return NextResponse.json(
      {
        configured: false,
        state: "NOT_CONFIGURED",
        database: cfg.database || null,
        secret_disclosure: "HYDRADB_CREDENTIAL_VALUES_NEVER_RETURNED",
      },
      { status: 503, headers: { "Cache-Control": "no-store, max-age=0", "X-HydraDG-Read-Only": "true" } },
    );
  }

  try {
    let collection = cfg.collection;
    let collectionSource = collection ? "EXPLICIT_ENV" : "DISCOVERED";
    if (!collection) {
      const discovery = await hostedHydraDBRequest(`/databases/collections?database=${encodeURIComponent(cfg.database)}`);
      collection = discoveredCollections(discovery.data)[0] || "";
      if (!collection) collectionSource = "DATABASE_DEFAULT_UNRESOLVED";
    }

    const payload: Record<string, unknown> = {
      database: cfg.database,
      query: "HydraDG FCO FCG provenance context",
      type: "knowledge",
      query_by: "hybrid",
      mode: "fast",
      max_results: 3,
      alpha: "auto",
      recency_bias: 0.2,
      graph_context: true,
      query_apps: true,
    };
    if (collection) payload.collection = collection;

    const query = await hostedHydraDBRequest("/query", "POST", payload);
    const body: any = query.data;
    const apiSuccess = body?.success !== false;
    const resultData = body?.data ?? body;
    const resultPayloadPresent = resultData != null;

    return NextResponse.json(
      {
        configured: true,
        state: apiSuccess && resultPayloadPresent ? "PASS_QUERY_LEVEL" : "FAIL_QUERY_LEVEL",
        database: cfg.database,
        collection: collection || null,
        collection_source: collectionSource,
        query_http: query.status,
        query_apps: true,
        graph_context: true,
        result_payload_present: resultPayloadPresent,
        source_specific_relation_traceability: cfg.canarySourceId ? "SEPARATE_CANARY_CONFIGURED" : "NOT_CLAIMED_BY_THIS_ROUTE",
        secret_disclosure: "HYDRADB_CREDENTIAL_VALUES_NEVER_RETURNED",
        claim_ceiling: "HYDRADB_V2_LIVE_QUERY_REQUEST_LEVEL_TRACEABILITY_ONLY",
      },
      { status: apiSuccess && resultPayloadPresent ? 200 : 502, headers: { "Cache-Control": "no-store, max-age=0", "X-HydraDG-Read-Only": "true" } },
    );
  } catch (error) {
    return NextResponse.json(
      {
        configured: true,
        state: "FAIL_QUERY_LEVEL",
        database: cfg.database,
        error: error instanceof Error ? error.message : String(error),
        secret_disclosure: "HYDRADB_CREDENTIAL_VALUES_NEVER_RETURNED",
        claim_ceiling: "NO_LIVE_QUERY_TRACEABILITY_CLAIM",
      },
      { status: 502, headers: { "Cache-Control": "no-store, max-age=0", "X-HydraDG-Read-Only": "true" } },
    );
  }
}
