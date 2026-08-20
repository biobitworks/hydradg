import { NextRequest, NextResponse } from "next/server";

import { hostedHydraDBConfig, hostedHydraDBRequest } from "@/lib/hydradbHosted";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  const cfg = hostedHydraDBConfig();
  if (!cfg.apiKey || !cfg.database) {
    return NextResponse.json(
      {
        configured: false,
        database: cfg.database || null,
        required: ["HYDRA_DB_API_KEY", "HYDRADB_DATABASE"],
        secret_disclosure: "HYDRADB_CREDENTIAL_VALUES_NEVER_RETURNED",
      },
      { status: 503 },
    );
  }

  try {
    const body = (await request.json()) as Record<string, unknown>;
    const query = String(body.query || "").trim();
    if (!query) return NextResponse.json({ error: "query is required" }, { status: 400 });

    const requestedCollection = String(body.collection || cfg.collection || "").trim();
    const payload: Record<string, unknown> = {
      database: cfg.database,
      query,
      type: body.type === "memory" || body.type === "all" ? body.type : "knowledge",
      query_by: body.query_by === "text" ? "text" : "hybrid",
      mode: body.mode === "fast" ? "fast" : "thinking",
      max_results: Math.max(1, Math.min(20, Number(body.max_results || 8))),
      alpha: body.alpha ?? "auto",
      recency_bias: body.recency_bias ?? 0.2,
      graph_context: body.graph_context !== false,
    };
    if (requestedCollection) payload.collection = requestedCollection;

    const response = await hostedHydraDBRequest("/query", "POST", payload);
    return NextResponse.json({
      configured: true,
      database: cfg.database,
      collection: requestedCollection || null,
      hydradb: response.data,
      secret_disclosure: "HYDRADB_CREDENTIAL_VALUES_NEVER_RETURNED",
      claim_ceiling: "HYDRADB_V2_QUERY_AND_GRAPH_CONTEXT_READBACK_ONLY",
    });
  } catch (error) {
    return NextResponse.json(
      {
        configured: true,
        database: cfg.database,
        error: error instanceof Error ? error.message : String(error),
        secret_disclosure: "HYDRADB_CREDENTIAL_VALUES_NEVER_RETURNED",
      },
      { status: 500 },
    );
  }
}
