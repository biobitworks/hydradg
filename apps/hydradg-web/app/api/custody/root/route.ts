import { buildKnowledgeProjection } from "@/lib/knowledgeFcg";
import { buildSiteFcg } from "@/lib/siteFcg";

export const dynamic = "force-dynamic";

export async function GET() {
  const site = buildSiteFcg();
  const knowledge = buildKnowledgeProjection();
  return Response.json({
    schema: "hydradg.release_watch_custody_root.v1",
    read_only: true,
    application_site_fco: site.artifact,
    application_knowledge_fco: knowledge.root,
    canonical_project_fcg_root: null,
    canonical_project_fcg_state: "PENDING_STABLE_DAISY_HANDOFF",
    hydradb_projection_root: null,
    hydradb_projection_state: "PENDING_STABLE_DAISY_HANDOFF",
    claim_ceiling: "APPLICATION_CUSTODY_PROJECTION_ONLY",
    signature_state: "NOT_SIGNED",
    merkle_state: "NOT_MERKLE_COMMITTED",
  }, {
    headers: { "Cache-Control": "no-store", "X-HydraDG-Read-Only": "true" },
  });
}
