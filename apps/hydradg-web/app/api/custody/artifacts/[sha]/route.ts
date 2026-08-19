import { buildDemoFixture } from "@/lib/demoFixture";
import { buildKnowledgeProjection } from "@/lib/knowledgeFcg";
import { buildSiteFcg } from "@/lib/siteFcg";

export const dynamic = "force-dynamic";

export async function GET(_request: Request, { params }: { params: Promise<{ sha: string }> }) {
  const { sha } = await params;
  const normalized = decodeURIComponent(sha).replace(/^fco:/i, "").toLowerCase();
  if (!/^[0-9a-f]{64}$/.test(normalized)) {
    return Response.json({ error: "Expected a 64-hex SHA-256/FCO object identifier." }, { status: 400 });
  }

  const fixture = buildDemoFixture();
  const site = buildSiteFcg();
  const knowledge = buildKnowledgeProjection();
  const nodes = [
    ...fixture.nodes.map(([, node]) => node),
    ...site.nodes,
    site.artifact,
    ...knowledge.nodes,
    knowledge.root,
  ];
  const match = nodes.find((node) => node.object_sha256.toLowerCase() === normalized);
  if (!match) {
    return Response.json({
      schema: "hydradg.release_watch_artifact_lookup.v1",
      found: false,
      sha256: normalized,
      search_scope: "BOUNDED_APPLICATION_FIXTURE_SITE_AND_KNOWLEDGE_FCOS",
      canonical_scientific_artifact_store_state: "PENDING_STABLE_DAISY_HANDOFF",
      claim_ceiling: "APPLICATION_ARTIFACT_LOOKUP_ONLY",
    }, { status: 404, headers: { "Cache-Control": "no-store", "X-HydraDG-Read-Only": "true" } });
  }

  return Response.json({
    schema: "hydradg.release_watch_artifact_lookup.v1",
    found: true,
    sha256: normalized,
    object: match,
    search_scope: "BOUNDED_APPLICATION_FIXTURE_SITE_AND_KNOWLEDGE_FCOS",
    canonical_scientific_artifact_store_state: "PENDING_STABLE_DAISY_HANDOFF",
    claim_ceiling: "APPLICATION_ARTIFACT_LOOKUP_ONLY",
  }, { headers: { "Cache-Control": "no-store", "X-HydraDG-Read-Only": "true" } });
}
