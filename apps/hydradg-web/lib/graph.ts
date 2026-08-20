type GraphParameters = Record<string, unknown>;
export type GraphRow = Record<string, unknown>;

function decodeHydraValue(value: unknown): unknown {
  if (!value || typeof value !== "object") return value;
  const record = value as { type?: string; value?: unknown };
  if (!("type" in record)) return value;
  if (record.type === "list" && Array.isArray(record.value)) {
    return record.value.map(decodeHydraValue);
  }
  if (record.type === "null") return null;
  return record.value;
}

async function runHydraDbHttp(
  query: string,
  parameters: GraphParameters,
): Promise<GraphRow[]> {
  const baseUrl = process.env.HYDRADB_HTTP_URL?.replace(/\/$/, "");
  const token = process.env.HYDRADB_AUTH_TOKEN;
  const graphId = process.env.HYDRADB_GRAPH_ID || "hydradg-judge-repro";
  const namespace = process.env.HYDRADB_GRAPH_NAMESPACE || "hydradg-judge-repro";
  const cellId = process.env.HYDRADB_CELL_ID || "cell-0";

  if (!baseUrl || !token) throw new Error("HydraDB HTTP backend is not configured");

  const response = await fetch(`${baseUrl}/v1/graphs/${encodeURIComponent(graphId)}/query`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      "X-Graph-Namespace": namespace,
    },
    body: JSON.stringify({ cell_id: cellId, query, parameters, page_size: 256 }),
    cache: "no-store",
  });

  const body = (await response.json()) as {
    columns?: string[];
    rows?: unknown[][];
    error?: { code?: string; message?: string };
  };
  if (!response.ok) throw new Error(body.error?.message || `HydraDB query failed (${response.status})`);

  const columns = body.columns || [];
  return (body.rows || []).map((row) =>
    Object.fromEntries(columns.map((column, index) => [column, decodeHydraValue(row[index])])),
  );
}

export function graphBackend(): "hydradb-http" {
  return "hydradb-http";
}

export function graphConfigured(): boolean {
  return Boolean(process.env.HYDRADB_HTTP_URL && process.env.HYDRADB_AUTH_TOKEN);
}

export async function runGraph(query: string, parameters: GraphParameters = {}): Promise<GraphRow[]> {
  return runHydraDbHttp(query, parameters);
}

export async function probeGraph(): Promise<{ ok: boolean; error?: string }> {
  if (!graphConfigured()) return { ok: false, error: "not configured" };
  try {
    // HydraDB requires a node-only MATCH to carry an id, label, or property
    // predicate. A labeled read is valid even when no such node exists.
    await runGraph("MATCH (n:HydraDGHealth) RETURN n.id AS id LIMIT 1");
    return { ok: true };
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : String(error) };
  }
}
