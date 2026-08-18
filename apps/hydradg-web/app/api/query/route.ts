import { NextRequest, NextResponse } from "next/server";

import { buildDemoFixture } from "@/lib/demoFixture";
import { canonicalJson, makeFcoNode, sha256Text } from "@/lib/fco";
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

const nodeLabels = new Set([
  "ToolAction",
  "Source",
  "Evidence",
  "KnowledgeAtom",
  "SeedOfTruth",
  "ClassificationReceipt",
]);
const edgeTypes = new Set([
  "PRODUCED",
  "DERIVED_FROM",
  "SUPPORTED_BY",
  "SUPERSEDED_BY",
  "CONTRADICTS",
  "CLASSIFIES",
]);

async function upsertNode(label: string, node: ReturnType<typeof makeFcoNode>) {
  if (!nodeLabels.has(label)) throw new Error(`unsupported node label: ${label}`);
  const subjectKey = typeof node.payload.subject_key === "string" ? node.payload.subject_key : null;
  const isCurrent = typeof node.payload.is_current === "boolean" ? node.payload.is_current : null;
  await runGraph(
    `MERGE (n:${label} {id: $id})
     SET n.object_sha256 = $object_sha256,
         n.type = $type,
         n.payload_json = $payload_json,
         n.claim_ceiling = $claim_ceiling,
         n.evidence_class = $evidence_class,
         n.subject_key = $subject_key,
         n.is_current = $is_current
     RETURN n.id AS id`,
    {
      id: node.id,
      object_sha256: node.object_sha256,
      type: node.type,
      payload_json: canonicalJson(node.payload),
      claim_ceiling: String(node.payload.claim_ceiling || "PROVENANCE_ONLY"),
      evidence_class: String(node.payload.evidence_class || "UNSPECIFIED"),
      subject_key: subjectKey,
      is_current: isCurrent,
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

async function traceProvenance(startId: string, maxDepth = 4) {
  const allowed = ["DERIVED_FROM", "SUPPORTED_BY", "PRODUCED", "CLASSIFIES"];
  const seen = new Set<string>([startId]);
  let frontier = [startId];
  const hops: Array<Record<string, unknown>> = [];

  for (let depth = 0; depth < maxDepth && frontier.length; depth += 1) {
    const next: string[] = [];
    for (const id of frontier) {
      const rows = await runGraph(
        `MATCH (a)-[r]->(b)
         WHERE a.id = $id AND type(r) IN $allowed
         RETURN a.id AS from_id, type(r) AS relation, b.id AS to_id,
                b.type AS to_type, b.claim_ceiling AS claim_ceiling,
                b.payload_json AS payload`,
        { id, allowed },
      );
      for (const row of rows) {
        hops.push({ depth: depth + 1, ...row });
        const toId = typeof row.to_id === "string" ? row.to_id : null;
        if (toId && !seen.has(toId)) {
          seen.add(toId);
          next.push(toId);
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
      subject_key?: string;
      ingest?: boolean;
    };
    const action = body.action;

    if (action === "fixture") {
      return NextResponse.json({ action, fixture: await loadDemoFixture() });
    }

    if (action === "memory") {
      const term = body.term?.trim();
      if (!term) return NextResponse.json({ error: "term is required" }, { status: 400 });
      const rows = await runGraph(
        `MATCH (n)
         WHERE n.id = $term OR toLower(n.payload_json) CONTAINS toLower($term)
         RETURN n.id AS id, n.type AS type, n.subject_key AS subject_key,
                n.is_current AS is_current, n.claim_ceiling AS claim_ceiling,
                n.evidence_class AS evidence_class, n.payload_json AS payload
         LIMIT 30`,
        { term },
      );
      return NextResponse.json({ action, rows });
    }

    if (action === "current") {
      const subjectKey = body.subject_key?.trim() || body.term?.trim();
      if (!subjectKey) return NextResponse.json({ error: "subject_key is required" }, { status: 400 });
      const rows = await runGraph(
        `MATCH (n)
         WHERE n.subject_key = $subject_key AND n.is_current = true
         RETURN n.id AS id, n.type AS type, n.claim_ceiling AS claim_ceiling,
                n.evidence_class AS evidence_class, n.payload_json AS payload
         LIMIT 20`,
        { subject_key: subjectKey },
      );
      return NextResponse.json({ action, subject_key: subjectKey, rows });
    }

    if (action === "history") {
      const id = body.id?.trim();
      if (!id) return NextResponse.json({ error: "id is required" }, { status: 400 });
      const rows = await runGraph(
        `MATCH (a)-[r]->(b)
         WHERE a.id = $id AND type(r) IN $relations
         RETURN a.id AS from_id, type(r) AS relation, b.id AS to_id,
                b.type AS to_type, b.payload_json AS payload
         LIMIT 50`,
        { id, relations: ["SUPERSEDED_BY", "CONTRADICTS"] },
      );
      return NextResponse.json({ action, rows });
    }

    if (action === "provenance") {
      const id = body.id?.trim();
      if (!id) return NextResponse.json({ error: "id is required" }, { status: 400 });
      return NextResponse.json({ action, start_id: id, hops: await traceProvenance(id) });
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
