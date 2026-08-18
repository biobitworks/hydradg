import { NextRequest, NextResponse } from "next/server";

import { buildDemoFixture } from "@/lib/demoFixture";
import { canonicalJson, hydraNumericId, makeFcoNode, sha256Text } from "@/lib/fco";
import { graphConfigured, runGraph } from "@/lib/graph";

export const runtime = "nodejs";

type Action = "memory" | "current" | "history" | "provenance" | "fixture" | "exa";

type ExaResult = {
  id?: string;
  title?: string;
  url?: string;
  publishedDate?: string;
  author?: string;
  text?: string;
  highlights?: string[];
};

type ExaResponse = {
  requestId?: string;
  results?: ExaResult[];
  statuses?: unknown[];
};

const nodeLabels = [
  "ToolAction",
  "Source",
  "Evidence",
  "KnowledgeAtom",
  "SeedOfTruth",
  "ClassificationReceipt",
] as const;
const nodeLabelSet = new Set<string>(nodeLabels);
const edgeTypes = [
  "PRODUCED",
  "DERIVED_FROM",
  "SUPPORTED_BY",
  "SUPERSEDED_BY",
  "CONTRADICTS",
  "CLASSIFIES",
] as const;
const edgeTypeSet = new Set<string>(edgeTypes);

type NodeLabel = (typeof nodeLabels)[number];
type EdgeType = (typeof edgeTypes)[number];

async function upsertNode(label: string, node: ReturnType<typeof makeFcoNode>) {
  if (!nodeLabelSet.has(label)) throw new Error(`unsupported node label: ${label}`);
  const numericId = hydraNumericId(node.id);

  // The native HydraDB vertex id is u64; FCO identity remains the full hash string.
  // Detect the extremely unlikely adapter-key collision before writing properties.
  const existing = await runGraph(
    `MATCH (n {id: $id}) RETURN n.fco_id AS fco_id LIMIT 1`,
    { id: numericId },
  );
  const existingFcoId = typeof existing[0]?.fco_id === "string" ? existing[0].fco_id : "";
  if (existingFcoId && existingFcoId !== node.id) {
    throw new Error(`HydraDB numeric-address collision for ${node.id}`);
  }

  // HydraDB mutations are intentionally separate from reads/RETURN clauses.
  await runGraph(`MERGE (n:${label} {id: $id})`, { id: numericId });

  const subjectKey = typeof node.payload.subject_key === "string" ? node.payload.subject_key : "";
  const isCurrent = typeof node.payload.is_current === "boolean" ? node.payload.is_current : false;
  const version = typeof node.payload.version === "number" ? node.payload.version : 0;
  const observedAt = typeof node.payload.observed_at === "string" ? node.payload.observed_at : "";
  await runGraph(
    `MATCH (n:${label} {id: $id})
     SET n.fco_id = $fco_id,
         n.object_sha256 = $object_sha256,
         n.type = $type,
         n.payload_json = $payload_json,
         n.claim_ceiling = $claim_ceiling,
         n.evidence_class = $evidence_class,
         n.subject_key = $subject_key,
         n.is_current = $is_current,
         n.version = $version,
         n.observed_at = $observed_at`,
    {
      id: numericId,
      fco_id: node.id,
      object_sha256: node.object_sha256,
      type: node.type,
      payload_json: canonicalJson(node.payload),
      claim_ceiling: String(node.payload.claim_ceiling || "PROVENANCE_ONLY"),
      evidence_class: String(node.payload.evidence_class || "UNSPECIFIED"),
      subject_key: subjectKey,
      is_current: isCurrent,
      version,
      observed_at: observedAt,
    },
  );
}

async function upsertEdge(srcFcoId: string, rel: string, dstFcoId: string) {
  if (!edgeTypeSet.has(rel)) throw new Error(`unsupported edge type: ${rel}`);
  const edgeBody = { src: srcFcoId, rel, dst: dstFcoId, payload: {} };
  const fcgId = `fcg:${sha256Text(canonicalJson(edgeBody))}`;
  const edgeId = hydraNumericId(fcgId);
  const src = hydraNumericId(srcFcoId);
  const dst = hydraNumericId(dstFcoId);

  await runGraph(
    `MATCH (a {id: $src}), (b {id: $dst})
     MERGE (a)-[r:${rel} {id: $edge_id}]->(b)`,
    { src, dst, edge_id: edgeId },
  );
  await runGraph(
    `MATCH (a {id: $src})-[r:${rel} {id: $edge_id}]->(b {id: $dst})
     SET r.fcg_id = $fcg_id,
         r.src_fco_id = $src_fco_id,
         r.dst_fco_id = $dst_fco_id`,
    { src, dst, edge_id: edgeId, fcg_id: fcgId, src_fco_id: srcFcoId, dst_fco_id: dstFcoId },
  );
  return fcgId;
}

async function loadDemoFixture() {
  if (!graphConfigured()) throw new Error("graph backend is not configured");
  const fixture = buildDemoFixture();
  for (const [label, node] of fixture.nodes) await upsertNode(label, node);
  const edgeIds: string[] = [];
  for (const [src, rel, dst] of fixture.edges) edgeIds.push(await upsertEdge(src, rel, dst));
  return {
    fixture_state: "DETERMINISTIC_SYNTHETIC_TEST_FIXTURE",
    claim_ceiling: "DEMO_FIXTURE_ONLY",
    classification_state: "IMPLEMENTATION_PENDING_PUBLIC_CONTRACT",
    subject_key: fixture.subject_key,
    ids: fixture.ids,
    edge_ids: edgeIds,
  };
}

async function readLabel(label: NodeLabel, limit = 50) {
  return runGraph(
    `MATCH (n:${label})
     RETURN n.id AS hydra_id, n.fco_id AS id, n.type AS type,
            n.subject_key AS subject_key, n.is_current AS is_current,
            n.claim_ceiling AS claim_ceiling, n.evidence_class AS evidence_class,
            n.payload_json AS payload, n.version AS version, n.observed_at AS observed_at
     LIMIT ${Math.max(1, Math.min(limit, 100))}`,
  );
}

async function traceOneRelation(fromFcoId: string, relation: EdgeType) {
  const id = hydraNumericId(fromFcoId);
  return runGraph(
    `MATCH (a {id: $id})-[:${relation}]->(b)
     RETURN a.fco_id AS from_id, b.fco_id AS to_id, b.type AS to_type,
            b.claim_ceiling AS claim_ceiling, b.payload_json AS payload`,
    { id },
  );
}

async function traceProvenance(startFcoId: string, maxDepth = 4) {
  const allowed: EdgeType[] = ["DERIVED_FROM", "SUPPORTED_BY", "PRODUCED", "CLASSIFIES"];
  const seen = new Set<string>([startFcoId]);
  let frontier = [startFcoId];
  const hops: Array<Record<string, unknown>> = [];

  for (let depth = 0; depth < maxDepth && frontier.length; depth += 1) {
    const next: string[] = [];
    for (const fromId of frontier) {
      for (const relation of allowed) {
        const rows = await traceOneRelation(fromId, relation);
        for (const row of rows) {
          const enriched = { depth: depth + 1, relation, ...row };
          hops.push(enriched);
          const toId = typeof row.to_id === "string" ? row.to_id : null;
          if (toId && !seen.has(toId)) {
            seen.add(toId);
            next.push(toId);
          }
        }
      }
    }
    frontier = next;
  }
  return hops;
}

async function exaRetrieve(term: string): Promise<ExaResponse> {
  const apiKey = process.env.EXA_API_KEY;
  if (!apiKey) throw new Error("EXA_API_KEY is not configured");

  const isUrl = /^https?:\/\//i.test(term);
  const endpoint = isUrl ? "https://api.exa.ai/contents" : "https://api.exa.ai/search";
  const body = isUrl
    ? {
        urls: [term],
        text: { maxCharacters: 8000 },
        highlights: { query: "key factual claims and implementation details", maxCharacters: 1600 },
        maxAgeHours: 0,
      }
    : {
        query: term,
        type: "auto",
        numResults: 6,
        contents: {
          text: { maxCharacters: 4000 },
          highlights: { query: term, maxCharacters: 1200 },
        },
      };

  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json", "x-api-key": apiKey },
    body: JSON.stringify(body),
    cache: "no-store",
  });

  const data = (await response.json()) as ExaResponse & { error?: string };
  if (!response.ok) throw new Error(data.error || `Exa request failed (${response.status})`);
  return data;
}

async function ingestExa(term: string, response: ExaResponse) {
  if (!graphConfigured()) throw new Error("graph backend is not configured");
  const retrievedAt = new Date().toISOString();
  const tool = makeFcoNode("ToolAction", {
    provider: "Exa",
    operation: /^https?:\/\//i.test(term) ? "contents" : "search",
    request_term: term,
    request_id: response.requestId || null,
    retrieved_at: retrievedAt,
    observed_at: retrievedAt,
    evidence_class: "EXTERNALLY_RETRIEVED_EVIDENCE",
    claim_ceiling: "RETRIEVAL_PROVENANCE_ONLY",
    custody_state: "HASHED",
  });
  await upsertNode("ToolAction", tool);

  const admitted: Array<{ source_id: string; evidence_id: string; edge_ids: string[] }> = [];
  for (const result of response.results || []) {
    if (!result.url) continue;
    const source = makeFcoNode("Source", {
      source_ref: result.url,
      title: result.title || null,
      author: result.author || null,
      published_date: result.publishedDate || null,
      provider: "Exa",
      observed_at: retrievedAt,
      evidence_class: "EXTERNALLY_RETRIEVED_EVIDENCE",
      claim_ceiling: "SOURCE_CONTENT_ONLY",
      custody_state: "HASHED",
    });
    const extractedText = result.text || "";
    const evidence = makeFcoNode("Evidence", {
      source_ref: result.url,
      exa_document_id: result.id || null,
      text: extractedText,
      text_sha256: sha256Text(extractedText),
      highlights: result.highlights || [],
      observed_at: retrievedAt,
      evidence_class: "EXTERNALLY_RETRIEVED_EVIDENCE",
      claim_ceiling: "EXTRACTED_SOURCE_EVIDENCE",
      custody_state: "HASHED",
    });
    await upsertNode("Source", source);
    await upsertNode("Evidence", evidence);
    const produced = await upsertEdge(tool.id, "PRODUCED", evidence.id);
    const derived = await upsertEdge(evidence.id, "DERIVED_FROM", source.id);
    admitted.push({ source_id: source.id, evidence_id: evidence.id, edge_ids: [produced, derived] });
  }
  return { tool_action_id: tool.id, admitted };
}

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json()) as {
      action?: Action;
      term?: string;
      id?: string;
      subject_key?: string;
      ingest?: boolean;
    };
    const action = body.action;

    if (action === "fixture") {
      return NextResponse.json({ action, fixture: await loadDemoFixture() });
    }

    if (action === "memory") {
      const term = body.term?.trim().toLowerCase();
      if (!term) return NextResponse.json({ error: "term is required" }, { status: 400 });
      const batches = await Promise.all(nodeLabels.map((label) => readLabel(label, 50)));
      const rows = batches
        .flat()
        .filter((row) => JSON.stringify(row).toLowerCase().includes(term))
        .slice(0, 30);
      return NextResponse.json({ action, rows, search_mode: "BOUNDED_CLIENT_FILTER_OVER_TYPED_HYDRADB_READS" });
    }

    if (action === "current") {
      const subjectKey = body.subject_key?.trim() || body.term?.trim();
      if (!subjectKey) return NextResponse.json({ error: "subject_key is required" }, { status: 400 });
      const queries: NodeLabel[] = ["SeedOfTruth", "KnowledgeAtom"];
      const rows = (
        await Promise.all(
          queries.map((label) =>
            runGraph(
              `MATCH (n:${label})
               WHERE n.subject_key = $subject_key AND n.is_current = true
               RETURN n.id AS hydra_id, n.fco_id AS id, n.type AS type,
                      n.claim_ceiling AS claim_ceiling, n.evidence_class AS evidence_class,
                      n.payload_json AS payload, n.version AS version`,
              { subject_key: subjectKey },
            ),
          ),
        )
      ).flat();
      return NextResponse.json({ action, subject_key: subjectKey, rows });
    }

    if (action === "history") {
      const fcoId = body.id?.trim();
      if (!fcoId) return NextResponse.json({ error: "id is required" }, { status: 400 });
      const rows: Array<Record<string, unknown>> = [];
      for (const relation of ["SUPERSEDED_BY", "CONTRADICTS"] as EdgeType[]) {
        for (const row of await traceOneRelation(fcoId, relation)) rows.push({ relation, ...row });
      }
      return NextResponse.json({ action, rows });
    }

    if (action === "provenance") {
      const fcoId = body.id?.trim();
      if (!fcoId) return NextResponse.json({ error: "id is required" }, { status: 400 });
      return NextResponse.json({ action, start_id: fcoId, hops: await traceProvenance(fcoId) });
    }

    if (action === "exa") {
      const term = body.term?.trim();
      if (!term) return NextResponse.json({ error: "term or URL is required" }, { status: 400 });
      const exa = await exaRetrieve(term);
      const custody = body.ingest ? await ingestExa(term, exa) : null;
      return NextResponse.json({
        action,
        request_id: exa.requestId || null,
        results: exa.results || [],
        statuses: exa.statuses || [],
        custody,
      });
    }

    return NextResponse.json({ error: "unsupported action" }, { status: 400 });
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : String(error) },
      { status: 500 },
    );
  }
}
