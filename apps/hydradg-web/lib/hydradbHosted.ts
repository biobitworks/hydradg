export type HostedHydraDBConfig = {
  apiKey: string;
  tenantId: string;
  subTenantId: string;
  baseUrl: string;
  canarySourceId: string;
};

export function hostedHydraDBConfig(): HostedHydraDBConfig {
  return {
    apiKey: process.env.HYDRA_DB_API_KEY || process.env.HYDRADB_API_KEY || "",
    tenantId: process.env.HYDRADB_TENANT_ID || process.env.HYDRA_DB_TENANT_ID || "",
    subTenantId: process.env.HYDRADB_SUB_TENANT_ID || process.env.HYDRA_DB_SUB_TENANT_ID || "hydradg-judge-demo",
    baseUrl: (process.env.HYDRADB_API_URL || "https://api.hydradb.com").replace(/\/$/, ""),
    canarySourceId: process.env.HYDRADG_PUBLIC_CANARY_SOURCE_ID || "",
  };
}

export async function hostedHydraDBRequest(path: string, method: "GET" | "POST" = "GET", body?: unknown) {
  const cfg = hostedHydraDBConfig();
  if (!cfg.apiKey) throw new Error("HYDRA_DB_API_KEY is not configured");

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

      const message = data?.detail?.message || data?.message || `HydraDB hosted API request failed (${response.status})`;
      if (![429, 500, 503].includes(response.status) || attempt === 3) throw new Error(message);
      await new Promise((resolve) => setTimeout(resolve, 2 ** attempt * 500));
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      if (attempt === 3) break;
    }
  }
  throw lastError || new Error("HydraDB hosted API request failed");
}

export async function hostedHydraDBStatus() {
  const cfg = hostedHydraDBConfig();
  if (!cfg.apiKey) {
    return {
      configured: false as const,
      tenant_configured: Boolean(cfg.tenantId),
      base_url: cfg.baseUrl,
      required: ["HYDRA_DB_API_KEY"],
      optional: ["HYDRADB_TENANT_ID", "HYDRADB_SUB_TENANT_ID", "HYDRADB_API_URL", "HYDRADG_PUBLIC_CANARY_SOURCE_ID"],
      key_value_disclosed: false,
    };
  }

  if (!cfg.tenantId) {
    const tenantIds = await hostedHydraDBRequest("/tenants/tenant_ids");
    return {
      configured: true as const,
      tenant_configured: false,
      base_url: cfg.baseUrl,
      key_present: true,
      key_value_disclosed: false,
      tenant_ids_available: Array.isArray((tenantIds.data as any)?.tenant_ids)
        ? (tenantIds.data as any).tenant_ids.length
        : null,
      claim_ceiling: "HYDRADB_HOSTED_KEY_AND_TENANT_DISCOVERY_ONLY",
    };
  }

  const status = await hostedHydraDBRequest(`/tenants/infra/status?tenant_id=${encodeURIComponent(cfg.tenantId)}`);
  let traceability: Record<string, unknown> = {
    state: "CANARY_SOURCE_NOT_CONFIGURED",
  };

  if (cfg.canarySourceId) {
    const params = new URLSearchParams({ tenant_id: cfg.tenantId, source_id: cfg.canarySourceId });
    if (cfg.subTenantId) params.set("sub_tenant_id", cfg.subTenantId);
    const relations = await hostedHydraDBRequest(`/list/graph_relations_by_id?${params.toString()}`);
    traceability = {
      state: "READBACK_REQUEST_SUCCEEDED",
      source_id: cfg.canarySourceId,
      response_status: relations.status,
      relation_payload_present: relations.data != null,
    };
  }

  return {
    configured: true as const,
    tenant_configured: true,
    tenant_id: cfg.tenantId,
    sub_tenant_id: cfg.subTenantId,
    base_url: cfg.baseUrl,
    key_present: true,
    key_value_disclosed: false,
    tenant_status_http: status.status,
    tenant_status: status.data,
    traceability,
    claim_ceiling: "REMOTE_HYDRADB_CONNECTIVITY_AND_OPTIONAL_CANARY_READBACK_ONLY",
  };
}
