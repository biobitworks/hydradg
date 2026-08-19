import { makeFcoNode } from "@/lib/fco";
import { KNOWLEDGE_TERMS } from "@/lib/knowledgeLinks";

export function buildKnowledgeProjection() {
  const nodes = KNOWLEDGE_TERMS.map((item) =>
    makeFcoNode("WebsiteKnowledgeTerm", {
      slug: item.slug,
      term: item.term,
      definition: item.short,
      how_to: item.howTo,
      graph_query: item.graphQuery,
      external_source: item.external || null,
      knowledge_href: `/knowledge#${item.slug}`,
      graph_href: `/graph?q=${encodeURIComponent(item.graphQuery)}`,
      evidence_class: "DETERMINISTIC_APPLICATION_KNOWLEDGE_METADATA",
      claim_ceiling: "WEBSITE_KNOWLEDGE_NAVIGATION_ONLY",
      canonical_project_fcg_state: "PENDING_CANONICAL_BINDING_WHERE_REQUIRED",
      hydradb_projection_state: "PENDING_SAFE_ISOLATED_DAISY_HANDOFF",
    }),
  );

  const root = makeFcoNode("WebsiteKnowledgeIndex", {
    project: "HydraDG",
    term_fco_ids: nodes.map((node) => node.id),
    term_count: nodes.length,
    source_order: ["canonical custody", "canonical FCG", "HydraDB projection", "website projection"],
    evidence_class: "DETERMINISTIC_APPLICATION_KNOWLEDGE_INDEX",
    claim_ceiling: "WEBSITE_KNOWLEDGE_NAVIGATION_ONLY",
    signature_state: "NOT_SIGNED",
    merkle_state: "NOT_MERKLE_COMMITTED",
  });

  return {
    schema: "hydradg.website_knowledge_projection.v1",
    root,
    nodes,
    hydradb_projection_state: "PENDING_SAFE_ISOLATED_DAISY_HANDOFF",
    claim_ceiling: "WEBSITE_KNOWLEDGE_NAVIGATION_ONLY",
    signature_state: "NOT_SIGNED",
    merkle_state: "NOT_MERKLE_COMMITTED",
  };
}
