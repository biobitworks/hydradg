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
      canonical_project_fcg_state: "BOUND_TO_CURRENT_APPLICATION_FCO_FCG",
      hydradb_projection_state: "HOSTED_CANONICAL_PROJECT_FCG_READBACK_VERIFIED__WEBSITE_TERM_PROJECTION_IS_APPLICATION_METADATA",
      custody_state: "HASHED",
    }),
  );

  const root = makeFcoNode("WebsiteKnowledgeIndex", {
    project: "HydraDG",
    term_fco_ids: nodes.map((node) => node.id),
    term_count: nodes.length,
    source_order: ["canonical custody", "canonical FCG", "hosted HydraDB readback", "website projection"],
    evidence_class: "DETERMINISTIC_APPLICATION_KNOWLEDGE_INDEX",
    claim_ceiling: "WEBSITE_KNOWLEDGE_NAVIGATION_ONLY",
    hosted_canonical_fcg_readback: "VERIFIED_BY_HOSTED_FCG_READBACK_RECEIPT",
    website_term_projection_scope: "APPLICATION_METADATA_NOT_SEPARATE_HYDRADB_CORRECTNESS_CLAIM",
    custody_state: "HASHED",
    signature_state: "NOT_SIGNED",
    merkle_state: "NOT_MERKLE_COMMITTED",
  });

  return {
    schema: "hydradg.website_knowledge_projection.v2",
    root,
    nodes,
    hydradb_projection_state: "HOSTED_CANONICAL_PROJECT_FCG_READBACK_VERIFIED__WEBSITE_TERM_PROJECTION_IS_APPLICATION_METADATA",
    claim_ceiling: "WEBSITE_KNOWLEDGE_NAVIGATION_ONLY",
    signature_state: "NOT_SIGNED",
    merkle_state: "NOT_MERKLE_COMMITTED",
  };
}
