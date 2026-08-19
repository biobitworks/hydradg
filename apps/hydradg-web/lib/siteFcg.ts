import { makeFcoNode } from "@/lib/fco";

const SECTION_SPECS = [
  { route: "/", label: "HydraDG", role: "project-entry-and-context-iceberg", claim: "APPLICATION_OVERVIEW_AND_READ_ONLY_DRIFT_VISUALIZATION" },
  { route: "/judge", label: "Judge Lab", role: "interactive-golden-path", claim: "DEMO_AND_LOCAL_EXECUTION_SURFACE" },
  { route: "/graph", label: "4D FCG", role: "custody-graph-visualization", claim: "EVIDENCE_LINKED_VISUALIZATION" },
  { route: "/knowledge", label: "Knowledge", role: "terminology-and-how-to", claim: "DOCUMENTATION_AND_SOURCE_NAVIGATION" },
  { route: "/evidence", label: "Evidence", role: "receipt-and-result-index", claim: "EVIDENCE_STATUS_INDEX" },
  { route: "/track01", label: "Track 01", role: "enterprise-context-ontology", claim: "TRACK01_IMPLEMENTATION_STATUS" },
  { route: "/track02", label: "Track 02", role: "dependency-blast-radius", claim: "TRACK02_IMPLEMENTATION_STATUS" },
  { route: "/track03", label: "Track 03", role: "temporal-memory-retrieval", claim: "TRACK03_EXECUTED_EVIDENCE_STATUS" },
  { route: "/eligibility", label: "Eligibility", role: "rules-custody-and-release-gate", claim: "SUBMISSION_ELIGIBILITY_AUDIT" },
] as const;

export function buildSiteFcg() {
  const nodes = SECTION_SPECS.map((spec) =>
    makeFcoNode("SiteSection", {
      ...spec,
      project: "HydraDG",
      evidence_class: "DETERMINISTIC_APPLICATION_METADATA",
      custody_state: "HASHED",
      claim_ceiling: spec.claim,
      hackathon_authorship_window: "2026-08-12_OR_LATER_REQUIRED",
    }),
  );
  const byRoute = new Map(SECTION_SPECS.map((spec, index) => [spec.route, nodes[index]]));

  const edgeSpecs = [
    ["/", "NAVIGATES_TO", "/judge"],
    ["/", "VISUALIZES_WITH", "/graph"],
    ["/", "NAVIGATES_TO", "/track01"],
    ["/", "NAVIGATES_TO", "/track02"],
    ["/", "NAVIGATES_TO", "/track03"],
    ["/judge", "EXPLAINS_WITH", "/knowledge"],
    ["/judge", "VISUALIZES_WITH", "/graph"],
    ["/judge", "SUPPORTED_BY", "/evidence"],
    ["/track01", "SUPPORTED_BY", "/evidence"],
    ["/track02", "SUPPORTED_BY", "/evidence"],
    ["/track03", "SUPPORTED_BY", "/evidence"],
    ["/knowledge", "OPENS_IN", "/graph"],
    ["/evidence", "BOUNDED_BY", "/eligibility"],
    ["/", "BOUNDED_BY", "/eligibility"],
  ] as const;

  const edges = edgeSpecs.map(([sourceRoute, relation, targetRoute]) => ({
    source: byRoute.get(sourceRoute)!.id,
    relation,
    target: byRoute.get(targetRoute)!.id,
    source_route: sourceRoute,
    target_route: targetRoute,
  }));

  const artifact = makeFcoNode("SiteArtifact", {
    project: "HydraDG",
    section_fco_ids: nodes.map((node) => node.id),
    edge_count: edges.length,
    representation: "APPLICATION_LEVEL_FCO_FCG",
    presentation_projection: {
      name: "CONTEXT_ICEBERG_4D_V1",
      source_order: "CANONICAL_CUSTODY_TO_FCG_TO_HYDRADB_PROJECTION_TO_UI",
      delta_g_star_semantics: "DIRECTION_ONLY_NOT_ACCURACY",
      cloud_drift_semantics: "MAGNITUDE_100X_JENSEN_SHANNON_DIVERGENCE",
      hero_api: "/api/iceberg",
      live_state_contract: "HYDRADG_ICEBERG_STATE_PATH_READ_ONLY",
    },
    claim_ceiling: "WEBSITE_NAVIGATION_AND_CUSTODY_REPRESENTATION_ONLY",
    signature_state: "NOT_SIGNED",
    merkle_state: "NOT_MERKLE_COMMITTED",
  });

  return {
    schema: "hydradg.site_fcg.v1",
    artifact,
    nodes,
    edges,
    claim_ceiling: "WEBSITE_NAVIGATION_AND_CUSTODY_REPRESENTATION_ONLY",
    signature_state: "NOT_SIGNED",
    merkle_state: "NOT_MERKLE_COMMITTED",
  };
}
