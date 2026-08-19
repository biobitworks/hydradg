export type KnowledgeTerm = {
  slug: string;
  term: string;
  short: string;
  howTo: string;
  graphQuery: string;
  external?: string;
};

export const KNOWLEDGE_TERMS: KnowledgeTerm[] = [
  {
    slug: "fco",
    term: "FCO",
    short: "Fractal Custody Object: a content-addressed logical custody object with explicit evidence and claim boundaries.",
    howTo: "Inspect an FCO ID, its object SHA-256, payload, evidence class, claim ceiling, and source/dependency edges rather than treating a hash as truth.",
    graphQuery: "FCO",
  },
  {
    slug: "fcg",
    term: "FCG",
    short: "Fractal Custody Graph: the dependency and transformation graph connecting sources, evidence, derived state, claims, and artifacts.",
    howTo: "Follow DERIVED_FROM, SUPPORTED_BY, SUPERSEDED_BY, CONTRADICTS, CLASSIFIES, TARGETS, PRODUCES, and RECORDS edges to locate the route behind a result.",
    graphQuery: "DERIVED_FROM",
  },
  {
    slug: "knowledge-atom",
    term: "KnowledgeAtom",
    short: "A bounded context-bearing evidence fragment produced from an exact source span or deterministic transform.",
    howTo: "Open the source/evidence node first, then follow DERIVED_FROM into the atom; do not collapse the source bytes and semantic atom into one identity.",
    graphQuery: "KnowledgeAtom",
  },
  {
    slug: "seed-of-truth",
    term: "SeedOfTruth",
    short: "A bounded admitted proposition supported by explicit atoms/evidence; not an absolute-truth label.",
    howTo: "Follow SUPPORTED_BY edges back to the admitted atoms and inspect the claim ceiling before reusing the seed.",
    graphQuery: "SeedOfTruth",
  },
  {
    slug: "msm",
    term: "MSM",
    short: "Mechanical Scientific Method: executable observation → hypothesis → experiment → measurement → comparison/falsification → update.",
    howTo: "Use normal/poison/antidote or other declared perturbations to make the next experiment a mechanically inspectable state transition.",
    graphQuery: "StateSnapshot",
  },
  {
    slug: "anticube",
    term: "Anticube",
    short: "Independent SELF/NONSELF × SAFE/NONSAFE + UNKNOWN admission/classification surface.",
    howTo: "Treat classification as an event with a declared task/operator scope. It may admit, challenge, quarantine, abstain, or reject without overwriting provenance.",
    graphQuery: "ClassificationReceipt",
  },
  {
    slug: "superseded-by",
    term: "SUPERSEDED_BY",
    short: "Temporal edge preserving an older authentic state while pointing toward a later state.",
    howTo: "Traverse the chain to the reachable leaf when resolving current state; do not delete the predecessor.",
    graphQuery: "SUPERSEDED_BY",
  },
  {
    slug: "contradicts",
    term: "CONTRADICTS",
    short: "Explicit relation between incompatible values or claims retained simultaneously in the graph.",
    howTo: "Use contradiction as a retrieval/reasoning signal and preserve both sides with their source/provenance context.",
    graphQuery: "CONTRADICTS",
  },
  {
    slug: "claim-ceiling",
    term: "Claim ceiling",
    short: "Maximum assertion strength supported by the current load-bearing evidence dependencies.",
    howTo: "A hash, replay, model output, or signature can only promote the specific property it actually establishes.",
    graphQuery: "claim_ceiling",
  },
  {
    slug: "merkle-checkpoint",
    term: "MerkleCheckpoint",
    short: "Deterministic commitment over a declared ordered leaf set; distinct from signing, correctness, and live HydraDB graph state.",
    howTo: "Inspect leaf ordering, odd-leaf rule, root SHA-256, and exact scope before describing a checkpoint as committed.",
    graphQuery: "MerkleCheckpoint",
  },
  {
    slug: "hydradb",
    term: "HydraDB",
    short: "Operational graph substrate used by HydraDG for typed state, relations, traversal, retrieval, and perturbation.",
    howTo: "Use the local pinned graph for the reproducible hackathon lane and keep hosted HydraDB conformance as a separately evidenced surface.",
    graphQuery: "HydraDB",
    external: "https://github.com/hydra-db/hydradb",
  },
  {
    slug: "longmemeval",
    term: "LongMemEval",
    short: "Primary public Track 03 memory benchmark used by the current full500 Daisy run.",
    howTo: "Use answer_session_ids for evaluation only; never graph construction or ranking.",
    graphQuery: "LongMemEval",
    external: "https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned",
  },
  {
    slug: "enterprise-rag-bench",
    term: "EnterpriseRAG-Bench",
    short: "Primary Track 01 synthetic enterprise retrieval/reasoning corpus.",
    howTo: "Model source artifacts, entities, conflicting/stale claims, current state, and evidence paths; keep benchmark data evaluation-only.",
    graphQuery: "EnterpriseRAG-Bench",
    external: "https://huggingface.co/datasets/onyx-dot-app/EnterpriseRAG-Bench",
  },
  {
    slug: "herb",
    term: "HERB",
    short: "Heterogeneous enterprise deep-search benchmark used as the Track 01 stress dataset.",
    howTo: "Use as a private/local evaluation source unless the intended public use passes the CC-BY-NC-4.0 release-license review.",
    graphQuery: "HERB",
    external: "https://huggingface.co/datasets/Salesforce/HERB",
  },
  {
    slug: "longmemeval-v2",
    term: "LongMemEval-V2",
    short: "Track 03 environment-experience memory benchmark with trajectories, haystacks, and optional screenshots.",
    howTo: "Start with released question/trajectory/haystack objects; pull screenshot archives only when the visual evidence lane is needed.",
    graphQuery: "LongMemEval-V2",
    external: "https://huggingface.co/datasets/xiaowu0162/longmemeval-v2",
  },
  {
    slug: "beam",
    term: "BEAM",
    short: "Long-context memory benchmark across 100K/500K/1M and separately 10M-token-scale conversations.",
    howTo: "Keep probing questions/ideal answers evaluation-only and ingest conversation turns as the memory substrate.",
    graphQuery: "BEAM",
    external: "https://huggingface.co/datasets/Mohammadta/BEAM",
  },
];

export function knowledgeTerm(term: string) {
  return KNOWLEDGE_TERMS.find((item) => item.term.toLowerCase() === term.toLowerCase());
}
