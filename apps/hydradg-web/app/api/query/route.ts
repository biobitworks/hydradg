import { NextRequest, NextResponse } from "next/server";

import { canonicalJson, makeFcoNode, sha256Text } from "@/lib/fco";
import { graphConfigured, runGraph } from "@/lib/graph";

export const runtime = "nodejs";

type Action = "memory" | "history" | "provenance" | "exa";

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

const nodeLabels = new Set(["ToolAction", "Source", "Evidence"]);
const edgeTypes = new Set(["PRODUCED", "DERIVED_FROM"]);

async function upsertNode(label: string, node: ReturnType<typeof makeFcoNode>) {
  if (!nodeLabels.has(label)) throw new Error(`unsupported node label: ${label}`);
  await runGraph(
    `MERGE (n:${label} {id: $id})
     SET n.object_sha256 = $object_sha256,
         n.type = $type,
         n.payload_json = $payload_json,
         n.claim_ceiling = $claim_ceiling,
         n.evidence_class = $evidence_class
     RETURN n.id AS id`,
    {
      id: node.id,
      object_sha256: node.object_sha256,
      type: node.type,
      payload_json: canonicalJson(node.payload),
      claim_ceiling: String(node.payload.claim_ceiling || "PROVENANCE_ONLY"),
      evidence_class: String(node.payload.evidence_class || "UNSPECIFIED"),
    },
  );
}

async function upsertEdge(src: string, rel: string, dst: string) {
  if (!edgeTypes.has(rel)) throw new Error(`unsupported edge type: ${rel}`);
  const edgeBody = { src, rel, dst, payload: {} };
  const id = `fcg:${sha256Text(canonicalJson(edgeBody))}`;
  await runGraph(
    `MATCH (a {id: $src}), (b {id: $dst})
     MERGE (a)-[r:${rel} {id: $id}]->(b)
     RETURN r.id AS id`,
    { src, dst, id },
  );
  return id;
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
    headers: {
      "Content-Type": "application/json",
      "x-api-key": apiKey,
    },
    body: JSON.stringify(body),
    cache: "no-store",
  });

  const data = (await response.json()) as ExaResponse & { error?: string };
  if (!response.ok) {
    throw new Error(data.error || `Exa request failed (${response.status})`);
  }
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
      ingest?: boolean;
    };
    const action = body.action;

    if (action === "memory") {
      const term = body.term?.trim();
      if (!term) return NextResponse.json({ error: "term is required" }, { status: 400 });
      const rows = await runGraph(
        `MATCH (n)
         WHERE n.id = $term OR toLower(n.payload_json) CONTAINS toLower($term)
         RETURN n.id AS id, n.type AS type, n.claim_ceiling AS claim_ceiling,
                n.evidence_class AS evidence_class, n.payload_json AS payload
         LIMIT 30`,
        { term },
      );
      return NextResponse.json({ action, rows });
    }

    if (action === "history") {
      const id = body.id?.trim();
      if (!id) return NextResponse.json({ error: "id is required" }, { status: 400 });
      const rows = await runGraph(
        `MATCH (a)-[r]->(b)
         WHERE a.id = $id AND (type(r) = 'SUPERSEDED_BY' OR type(r) = 'CONTRADICTS')
         RETURN a.id AS from_id, type(r) AS relation, b.id AS to_id,
                b.type AS to_type, b.payload_json AS payload
         LIMIT 50`,
        { id },
      );
      return NextResponse.json({ action, rows });
    }

    if (action === "provenance") {
      const id = body.id?.trim();
      if (!id) return NextResponse.json({ error: "id is required" }, { status: 400 });
      const rows = await runGraph(
        `MATCH (a)-[r]->(b)
         WHERE a.id = $id AND
               (type(r) = 'DERIVED_FROM' OR type(r) = 'SUPPORTED_BY' OR type(r) = 'PRODUCED')
         RETURN a.id AS from_id, type(r) AS relation, b.id AS to_id,
                b.type AS to_type, b.claim_ceiling AS claim_ceiling,
                b.payload_json AS payload
         LIMIT 80`,
        { id },
      );
      return NextResponse.json({ action, rows });
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
