export const PROJECT_TERMS = [
  { term: "FCO", slug: "fco" },
  { term: "FCG", slug: "fcg" },
  { term: "SeedGraph", slug: "seedgraph" },
  { term: "HydraDB", slug: "hydradb" },
  { term: "Seed of Truth", slug: "seed-of-truth" },
  { term: "Anticube", slug: "anticube" },
  { term: "SUPERSEDED_BY", slug: "superseded-by" },
  { term: "CONTRADICTS", slug: "contradicts" },
  { term: "current state", slug: "current-state" },
  { term: "perturbation", slug: "perturbation" },
  { term: "antidote", slug: "antidote" },
  { term: "Context Iceberg", slug: "context-iceberg" },
  { term: "Cloud Drift", slug: "cloud-drift" },
  { term: "Jensen-Shannon divergence", slug: "jensen-shannon-divergence" },
  { term: "ΔG*", slug: "delta-g-star" },
  { term: "evidence class", slug: "evidence-class" },
  { term: "claim ceiling", slug: "claim-ceiling" },
  { term: "Merkle checkpoint", slug: "merkle-checkpoint" },
  { term: "LongMemEval", slug: "longmemeval" },
  { term: "EnterpriseRAG-Bench", slug: "enterprise-rag-bench" },
  { term: "HERB", slug: "herb" },
  { term: "BEAM", slug: "beam" },
  { term: "HydraOntology", slug: "hydraontology" },
  { term: "HydraBlast", slug: "hydrablast" },
  { term: "HydraMemory", slug: "hydramemory" },
] as const;

export function knowledgeHref(slug: string) {
  return `/knowledge#${slug}`;
}
