import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";

type CloudAction =
  | "tenant_ids"
  | "status"
  | "monitor"
  | "list"
  | "full_recall"
  | "recall_preferences"
  | "boolean_recall"
  | "add_memory"
  | "relations";

function config() {
  return {
    apiKey: process.env.HYDRADB_API_KEY || process.env.HYDRA_DB_API_KEY || "",
    tenantId: process.env.HYDRADB_TENANT_ID || process.env.HYDRA_DB_TENANT_ID || "",
    subTenantId: process.env.HYDRADB_SUB_TENANT_ID || process.env.HYDRA_DB_SUB_TENANT_ID || "hydradg-judge-demo",
    baseUrl: (process.env.HYDRADB_API_URL || "https://api.hydradb.com").replace(/\/$/, ""),
  };
}

async function hydra(path: string, method: "GET" | "POST", body?: unknown) {
  const cfg = config();
  if (!cfg.apiKey) throw new Error("HYDRADB_API_KEY is required");

  let lastError: Error | null = null;
  for (let attempt = 1; attempt <= 3; attempt += 1) {
    try {
      const response = await fetch(`${cfg.baseUrl}${path}`, {
        method,
        headers: {
          Authorization: `Bearer ${cfg.apiKey}`,
          ...(method === "POST" ? { "Content-Type": "application/json" } : {}),
        },
        body: method === "POST" ? JSON.stringify(body || {}) : undefined,
        cache: "no-store",
        signal: AbortSignal.timeout(20_000),
      });
      const data = await response.json().catch(() => ({ status: response.status }));
      if (response.ok) return { status: response.status, data };
      const message = data?.detail?.message || data?.message || `HydraDB cloud request failed (${response.status})`;
      if (![429, 500, 503].includes(response.status) || attempt === 3) throw new Error(message);
      await new Promise((resolve) => setTimeout(resolve, 2 ** attempt * 500));
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      if (attempt === 3) break;
    }
  }
  throw lastError || new Error("HydraDB cloud request failed");
}

function scope(body: Record<string, unknown>) {
  const cfg = config();
  const tenantId = String(body.tenant_id || cfg.tenantId || "").trim();
  if (!tenantId) throw new Error("tenant_id is required for this operation");
  return {
    tenant_id: tenantId,
    sub_tenant_id: String(body.sub_tenant_id || cfg.subTenantId || ""),
  };
}

export async function GET() {
  const cfg = config();
  if (!cfg.apiKey) {
    return NextResponse.json(
      {
        configured: false,
        base_url: cfg.baseUrl,
        required: ["HYDRADB_API_KEY"],
        optional: ["HYDRADB_TENANT_ID", "HYDRADB_SUB_TENANT_ID", "HYDRADB_API_URL"],
        secret_disclosure: "API_KEY_VALUE_NEVER_RETURNED",
      },
      { status: 503 },
    );
  }

  try {
    if (!cfg.tenantId) {
      const tenantIds = await hydra("/tenants/tenant_ids", "GET");
      return NextResponse.json({
        configured: true,
        tenant_configured: false,
        tenant_ids: tenantIds,
        base_url: cfg.baseUrl,
        key_present: true,
        key_value_disclosed: false,
        claim_ceiling: "HYDRADB_CLOUD_KEY_AND_TENANT_DISCOVERY_ONLY",
      });
    }
    const status = await hydra(`/tenants/infra/status?tenant_id=${encodeURIComponent(cfg.tenantId)}`, "GET");
    return NextResponse.json({
      configured: true,
      tenant_configured: true,
      tenant_id: cfg.tenantId,
      sub_tenant_id: cfg.subTenantId,
      base_url: cfg.baseUrl,
      key_present: true,
      key_value_disclosed: false,
      status,
      claim_ceiling: "HYDRADB_CLOUD_CONNECTIVITY_AND_TENANT_STATUS_ONLY",
    });
  } catch (error) {
    return NextResponse.json(
      { configured: true, key_present: true, key_value_disclosed: false, error: error instanceof Error ? error.message : String(error) },
      { status: 503 },
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json()) as Record<string, unknown> & { action?: CloudAction };
    const action = body.action;

    if (action === "tenant_ids") {
      return NextResponse.json(await hydra("/tenants/tenant_ids", "GET"));
    }

    const scoped = scope(body);
    if (action === "status") {
      return NextResponse.json(await hydra(`/tenants/infra/status?tenant_id=${encodeURIComponent(scoped.tenant_id)}`, "GET"));
    }
    if (action === "monitor") {
      return NextResponse.json(await hydra(`/tenants/monitor?tenant_id=${encodeURIComponent(scoped.tenant_id)}`, "GET"));
    }
    if (action === "list") {
      return NextResponse.json(
        await hydra("/list/data", "POST", {
          ...scoped,
          page: Number(body.page || 1),
          page_size: Math.max(1, Math.min(50, Number(body.page_size || 10))),
        }),
      );
    }
    if (action === "full_recall") {
      return NextResponse.json(
        await hydra("/recall/full_recall", "POST", {
          ...scoped,
          query: String(body.query || ""),
          max_results: Math.max(1, Math.min(20, Number(body.max_results || 8))),
          mode: String(body.mode || "thinking"),
          alpha: body.alpha ?? 0.5,
          recency_bias: body.recency_bias ?? 0.5,
          graph_context: body.graph_context !== false,
        }),
      );
    }
    if (action === "recall_preferences") {
      return NextResponse.json(
        await hydra("/recall/recall_preferences", "POST", {
          ...scoped,
          query: String(body.query || ""),
          mode: String(body.mode || "thinking"),
          alpha: body.alpha ?? 0.5,
          recency_bias: body.recency_bias ?? 0.5,
        }),
      );
    }
    if (action === "boolean_recall") {
      return NextResponse.json(
        await hydra("/recall/boolean_recall", "POST", {
          ...scoped,
          query: String(body.query || ""),
        }),
      );
    }
    if (action === "add_memory") {
      const text = String(body.text || "").trim();
      if (!text) return NextResponse.json({ error: "text is required" }, { status: 400 });
      return NextResponse.json(
        await hydra("/memories/add_memory", "POST", {
          ...scoped,
          memories: [
            {
              text,
              infer: body.infer !== false,
              user_name: String(body.user_name || "hydradg-judge"),
            },
          ],
          upsert: true,
        }),
      );
    }
    if (action === "relations") {
      const sourceId = String(body.source_id || "").trim();
      if (!sourceId) return NextResponse.json({ error: "source_id is required" }, { status: 400 });
      const params = new URLSearchParams({ tenant_id: scoped.tenant_id, source_id: sourceId });
      if (scoped.sub_tenant_id) params.set("sub_tenant_id", scoped.sub_tenant_id);
      return NextResponse.json(await hydra(`/list/graph_relations_by_id?${params.toString()}`, "GET"));
    }
    return NextResponse.json({ error: "unsupported HydraDB cloud action" }, { status: 400 });
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : String(error) }, { status: 500 });
  }
}
