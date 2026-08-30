import { makeFcoNode } from "@/lib/fco";
import { buildKnowledgeProjection } from "@/lib/knowledgeFcg";

const SECTION_SPECS = [
  { route: "/", label: "HydraDG", role: "project-entry-and-context-iceberg", claim: "APPLICATION_OVERVIEW_AND_READ_ONLY_DRIFT_VISUALIZATION" },
  { route: "/judge", label: "Judge Lab", role: "golden-path-judge-walkthrough", claim: "PUBLIC_READ_ONLY_DEMO_AND_EVIDENCE_NAVIGATION" },
  { route: "/track03", label: "Track 03", role: "temporal-memory-retrieval", claim: "TRACK03_EXECUTED_EVIDENCE_STATUS" },
  { route: "/best-use", label: "Best Use of HydraDB", role: "graph-native-use-case-scale-economics-and-deterministic-accounting", claim: "DEDUP_ACCOUNTING_K_DEPTH_AND_HYDRADB_USE_CASE_WITH_EXPLICIT_MEASUREMENT_BOUNDARIES" },
  { route: "/graph", label: "4D FCG", role: "custody-graph-visualization", claim: "EVIDENCE_LINKED_VISUALIZATION" },
  { route: "/models", label: "Models Used", role: "model-lane-and-runtime-boundaries", claim: "MODEL_INVOLVEMENT_AND_CLAIM_BOUNDARY_DOCUMENTATION" },
  { route: "/custody", label: "Custody", role: "hash-signature-and-key-boundary", claim: "CRYPTOGRAPHIC_STATUS_AND_SIGNING_SCOPE_DOCUMENTATION" },
  { route: "/evidence", label: "Evidence", role: "receipt-and-result-index", claim: "EVIDENCE_STATUS_INDEX" },
  { route: "/results/context-vs-entropy", label: "Context vs Entropy", role: "secret-context-classification-result", claim: "MEASURED_CONTEXT_CLASSIFICATION_RESULT" },
  { route: "/knowledge", label: "Knowledge", role: "terminology-and-how-to", claim: "DOCUMENTATION_AND_SOURCE_NAVIGATION" },
  { route: "/how-to", label: "How to Use", role: "judge-operator-guide", claim: "DOCUMENTATION_AND_REPRODUCTION_GUIDE" },
  { route: "/evolution", label: "Evolution", role: "presentation-and-release-lineage", claim: "PRESENTATION_LINEAGE_ONLY" },
  { route: "/track01", label: "Track 01", role: "enterprise-context-ontology", claim: "TRACK01_IMPLEMENTATION_STATUS" },
  { route: "/track02", label: "Track 02", role: "dependency-blast-radius", claim: "TRACK02_IMPLEMENTATION_STATUS" },
  { route: "/eligibility", label: "Eligibility", role: "rules-custody-and-release-gate", claim: "SUBMISSION_ELIGIBILITY_AUDIT" },
  { route: "/submission", label: "Submission", role: "immersive-commons-submission-hero", claim: "SUBMISSION_HERO_NAVIGATION_AND_CUSTODY_RECEIPT_ONLY" },
] as const;

export function buildSiteFcg() {
  const knowledge = buildKnowledgeProjection();
  const nodes = SECTION_SPECS.map((spec) =>
    makeFcoNode("SiteSection", {
      ...spec,
      project: "HydraDG",
      evidence_class: "DETERMINISTIC_APPLICATION_METADATA",
      custody_state: "HASHED",
      signature_state: "NOT_SIGNED",
      claim_ceiling: spec.claim,
      hackathon_authorship_window: "2026-08-12_OR_LATER_REQUIRED",
    }),
  );
  const byRoute = new Map(SECTION_SPECS.map((spec, index) => [spec.route, nodes[index]]));

  const edgeSpecs = [
    ["/", "GOLDEN_PATH_NEXT", "/judge"],
    ["/judge", "GOLDEN_PATH_NEXT", "/track03"],
    ["/track03", "GOLDEN_PATH_NEXT", "/best-use"],
    ["/best-use", "GOLDEN_PATH_NEXT", "/graph"],
    ["/graph", "GOLDEN_PATH_NEXT", "/models"],
    ["/models", "GOLDEN_PATH_NEXT", "/custody"],
    ["/custody", "GOLDEN_PATH_NEXT", "/evidence"],
    ["/", "NAVIGATES_TO", "/results/context-vs-entropy"],
    ["/", "EXPLAINS_WITH", "/knowledge"],
    ["/", "EXPLAINS_WITH", "/how-to"],
    ["/", "HAS_LINEAGE_VIEW", "/evolution"],
    ["/judge", "INSPECTS_TRACK_LENS", "/track01"],
    ["/judge", "INSPECTS_TRACK_LENS", "/track02"],
    ["/judge", "INSPECTS_TRACK_LENS", "/track03"],
    ["/judge", "EXPLAINS_WITH", "/knowledge"],
    ["/judge", "SUPPORTED_BY", "/evidence"],
    ["/best-use", "SUPPORTED_BY", "/evidence"],
    ["/best-use", "BOUNDED_BY", "/custody"],
    ["/track01", "SUPPORTED_BY", "/evidence"],
    ["/track02", "SUPPORTED_BY", "/evidence"],
    ["/track03", "SUPPORTED_BY", "/evidence"],
    ["/results/context-vs-entropy", "SUPPORTED_BY", "/evidence"],
    ["/models", "BOUNDED_BY", "/custody"],
    ["/knowledge", "OPENS_IN", "/graph"],
    ["/how-to", "RESOLVES_TERMS_WITH", "/knowledge"],
    ["/evolution", "BOUNDED_BY", "/eligibility"],
    ["/evidence", "BOUNDED_BY", "/eligibility"],
    ["/", "BOUNDED_BY", "/eligibility"],
    ["/submission", "NAVIGATES_TO", "/judge"],
    ["/submission", "VISUALIZES_WITH", "/graph"],
    ["/submission", "SUPPORTED_BY", "/evidence"],
    ["/submission", "BOUNDED_BY", "/eligibility"],
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
    knowledge_root_fco_id: knowledge.root.id,
    knowledge_term_fco_count: knowledge.nodes.length,
    knowledge_api: "/api/knowledge",
    release_api: "/api/release",
    knowledge_hydradb_projection_state: knowledge.hydradb_projection_state,
    representation: "APPLICATION_LEVEL_FCO_FCG",
    golden_path: ["/", "/judge", "/track03", "/best-use", "/graph", "/models", "/custody", "/evidence"],
    presentation_projection: {
      name: "CONTEXT_ICEBERG_4D_V2",
      source_order: "CANONICAL_CUSTODY_TO_FCG_TO_HYDRADB_PROJECTION_TO_UI",
      state_colors: {
        reference_normal: "VIOLET",
        poison_mutation: "ORANGE",
        antidote_restoration: "BLUE",
      },
      delta_g_star_semantics: "SIGNED_DIRECTION_NOT_ACCURACY",
      cloud_drift_semantics: "MAGNITUDE_100X_JENSEN_SHANNON_DIVERGENCE",
      hero_api: "/api/iceberg",
      live_state_contract: "READ_ONLY_RECEIPT_OR_DETERMINISTIC_FIXTURE",
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
    knowledge_root: knowledge.root,
    knowledge_projection_state: knowledge.hydradb_projection_state,
    claim_ceiling: "WEBSITE_NAVIGATION_AND_CUSTODY_REPRESENTATION_ONLY",
    signature_state: "NOT_SIGNED",
    merkle_state: "NOT_MERKLE_COMMITTED",
  };
}
