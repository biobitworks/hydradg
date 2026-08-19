import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";

type LiveAction =
  | "health"
  | "cases"
  | "graph_stats"
  | "live_stats"
  | "recent"
  | "load_case"
  | "retrieve"
  | "perturb"
  | "current";

type HydraEnvelope = { columns?: string[]; rows?: unknown[][]; error?: unknown };

function baseUrl(): string | null {
  return process.env.BEST_USE_SERVER_URL?.replace(/\/$/, "") || "http://127.0.0.1:8787";
}

function decodeHydra(value: unknown): unknown {
  if (!value || typeof value !== "object") return value;
  const record = value as { type?: string; value?: unknown };
  if (!("type" in record)) return value;
  if (record.type === "list" && Array.isArray(record.value)) return record.value.map(decodeHydra);
  if (record.type === "null") return null;
  return record.value;
}

function table(envelope: HydraEnvelope): Array<Record<string, unknown>> {
  const columns = envelope.columns || [];
  return (envelope.rows || []).map((row) =>
    Object.fromEntries(columns.map((column, index) => [column, decodeHydra(row[index])])),
  );
}

async function backend(path: string, method: "GET" | "POST", body?: unknown) {
  const base = baseUrl();
  if (!base) throw new Error("BEST_USE_SERVER_URL is not configured");
  const response = await fetch(`${base}${path}`, {
    method,
    headers: method === "POST" ? { "Content-Type": "application/json" } : undefined,
    body: method === "POST" ? JSON.stringify(body || {}) : undefined,
    cache: "no-store",
    signal: AbortSignal.timeout(15_000),
  });
  const data = await response.json();
  if (!response.ok) {
    const message = typeof data?.error === "string" ? data.error : `Best Use server failed (${response.status})`;
    throw new Error(message);
  }
  return data;
}

async function resolveCurrent(questionId: string, subject: string, predicate: string) {
  const parameters = { qid: questionId, subject, predicate };
  const factsEnvelope = (await backend("/cypher", "POST", {
    query:
      "MATCH (f:Fact) WHERE f.qid = $qid AND f.subject = $subject AND f.predicate = $predicate " +
      "RETURN f.id AS id, f.subject AS subject, f.predicate AS predicate, f.object AS object, " +
      "f.position AS position, f.observed_at AS observed_at, f.evidence_class AS evidence_class LIMIT 100",
    parameters,
  })) as HydraEnvelope;
  const edgeEnvelope = (await backend("/cypher", "POST", {
    query:
      "MATCH (a:Fact)-[:SUPERSEDED_BY]->(b:Fact) WHERE a.qid = $qid AND a.subject = $subject AND a.predicate = $predicate " +
      "RETURN a.id AS from_id, b.id AS to_id LIMIT 100",
    parameters,
  })) as HydraEnvelope;

  const facts = table(factsEnvelope);
  const edges = table(edgeEnvelope);
  const superseded = new Set(edges.map((edge) => String(edge.from_id)));
  const leaves = facts.filter((fact) => !superseded.has(String(fact.id)));
  const current = [...leaves].sort((a, b) => Number(b.position || 0) - Number(a.position || 0))[0] || null;
  return {
    schema: "hydradg.live_current_state.v1",
    question_id: questionId,
    subject,
    predicate,
    current,
    trajectory: facts.sort((a, b) => Number(a.position || 0) - Number(b.position || 0)),
    supersession_edges: edges,
    evidence_class: "RECOMPUTED_LIVE_HYDRADB_TRAVERSAL",
    claim_ceiling: "CURRENT_STATE_TRAVERSAL_FOR_LOADED_CASE_ONLY",
  };
}

export async function GET() {
  const configured = Boolean(baseUrl());
  if (!configured) {
    return NextResponse.json(
      {
        configured: false,
        mode: "PUBLIC_FIXTURE_ONLY",
        error: "BEST_USE_SERVER_URL is not configured. Run the judge surface locally for LIVE mode.",
      },
      { status: 503 },
    );
  }
  try {
    const health = await backend("/health", "GET");
    return NextResponse.json({ configured: true, mode: "LIVE_LOCAL_HYDRADB", health });
  } catch (error) {
    return NextResponse.json(
      { configured: true, mode: "LIVE_BACKEND_UNREACHABLE", error: error instanceof Error ? error.message : String(error) },
      { status: 503 },
    );
  }
}

export async function POST(request: NextRequest) {
  if (!baseUrl()) {
    return NextResponse.json(
      { error: "BEST_USE_SERVER_URL is not configured; LIVE mode is intentionally local-only." },
      { status: 503 },
    );
  }

  try {
    const body = (await request.json()) as Record<string, unknown> & { action?: LiveAction };
    switch (body.action) {
      case "health":
        return NextResponse.json(await backend("/health", "GET"));
      case "cases":
        return NextResponse.json(await backend(`/cases?limit=${Math.max(1, Math.min(100, Number(body.limit || 100)))}`, "GET"));
      case "graph_stats":
        return NextResponse.json(await backend("/graph/stats", "GET"));
      case "live_stats":
        return NextResponse.json(await backend("/live/stats", "GET"));
      case "recent":
        return NextResponse.json(await backend(`/live/recent?limit=${Math.max(1, Math.min(100, Number(body.limit || 20)))}`, "GET"));
      case "load_case":
        return NextResponse.json(
          await backend("/case/load", "POST", {
            question_id: body.question_id,
            extractor: body.extractor || "heuristic",
          }),
        );
      case "retrieve":
        return NextResponse.json(
          await backend("/retrieve", "POST", {
            question_id: body.question_id,
            question: body.question || "",
            method: body.method || "D",
            k: Number(body.k || 5),
            extractor: body.extractor || "heuristic",
          }),
        );
      case "perturb":
        return NextResponse.json(
          await backend("/live/perturb", "POST", {
            question_id: body.question_id,
            target_fact_vertex: body.target_fact_vertex,
            object: body.object,
            identity_class: body.identity_class || "UNKNOWN",
            safety_class: body.safety_class || "UNKNOWN",
            extractor: body.extractor || "heuristic",
          }),
        );
      case "current": {
        const questionId = String(body.question_id || "").trim();
        const subject = String(body.subject || "").trim();
        const predicate = String(body.predicate || "").trim();
        if (!questionId || !subject || !predicate) {
          return NextResponse.json({ error: "question_id, subject, and predicate are required" }, { status: 400 });
        }
        return NextResponse.json(await resolveCurrent(questionId, subject, predicate));
      }
      default:
        return NextResponse.json({ error: "unsupported live action" }, { status: 400 });
    }
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : String(error) },
      { status: 500 },
    );
  }
}
