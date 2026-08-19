export type JudgeGuide = {
  id: string;
  title: string;
  hydradbPattern: string;
  why: string;
  how: string[];
  example: string;
  hydradgExpansion: string;
  falsifier: string;
  evidenceState: string;
};

export const JUDGE_GUIDES: JudgeGuide[] = [
  {
    id: "fixture",
    title: "Deterministic fixture",
    hydradbPattern: "Self-hosted graph write + read",
    why: "A judge needs a known-answer control before seeing real benchmark state. This proves the application can materialize typed FCO/FCG objects without depending on a model or external API.",
    how: [
      "Click Load deterministic fixture.",
      "Open the Golden Path graph and move the time slider from reference to perturbation to restoration.",
      "Inspect the recomputed fixture Merkle checkpoint. It is a demo commitment over fixture FCO identities only.",
    ],
    example: "No text input required. The fixture is intentionally frozen.",
    hydradgExpansion: "Source → Evidence → KnowledgeAtom → SeedOfTruth → StateSnapshot → ClassificationReceipt → deterministic Merkle checkpoint.",
    falsifier: "If repeated fixture loads produce different FCO identities or a different Merkle root, deterministic custody failed.",
    evidenceState: "DETERMINISTIC_SYNTHETIC_TEST_FIXTURE",
  },
  {
    id: "case",
    title: "Real LongMemEval case",
    hydradbPattern: "Persistent memory / contextual graph",
    why: "This moves from a synthetic smoke control to a public memory benchmark with real multi-session histories and update questions.",
    how: [
      "Click Refresh cases to read available LongMemEval rows from the local Best Use server.",
      "Select a question_id and use the heuristic extractor for the most deterministic path.",
      "Click Load case. The response includes Fact and Entity rows actually written to HydraDB.",
    ],
    example: "Select any returned question_id; prefer a knowledge-update case when available.",
    hydradgExpansion: "The benchmark session history becomes typed Session, Entity and Fact nodes with NEXT/PREV, ASSERTS, SUPERSEDED_BY and CONTRADICTS relations.",
    falsifier: "If the same source case cannot be reloaded into an equivalent typed graph, the graph-materialization claim fails.",
    evidenceState: "REAL_DATA_EXECUTION_REQUIRES_LOCAL_SERVER",
  },
  {
    id: "retrieve",
    title: "Graph-aware retrieval",
    hydradbPattern: "full_recall / graph_context analogue",
    why: "HydraDB cookbooks emphasize useful context rather than isolated semantic similarity. HydraDG exposes the retrieval reasons and graph contribution instead of hiding them behind a final answer.",
    how: [
      "Load a case first.",
      "Leave Query blank to use the benchmark question, or enter a counterfactual query.",
      "Compare method A (flat lexical baseline) with D (typed graph expansion).",
      "Keep K=5 for the judge demo, then inspect hit@K, recall, latency and evidence-path coverage.",
    ],
    example: "What is the user's current preference after the later update?",
    hydradgExpansion: "A/B/C/D is an ablation ladder: lexical → chronology → provenance/entity → supersession/contradiction traversal.",
    falsifier: "If graph edges are removed or reversed and retrieval does not change where the edge is load-bearing, the claimed graph mechanism is not demonstrated.",
    evidenceState: "LIVE_RETRIEVAL_INSPECTION",
  },
  {
    id: "perturb",
    title: "Normal / poison / antidote",
    hydradbPattern: "Memory update + temporal graph",
    why: "The strongest Best Use demo is causal: change one Fact, preserve history, classify the event, and observe the downstream retrieval/current-state effect.",
    how: [
      "Choose a Fact returned by Load case; Subject, Predicate and target vertex are auto-filled.",
      "Normal writes the same object as a negative control.",
      "Poison writes a deliberately different object and marks NONSELF/NONSAFE for this operator-scoped demo.",
      "Antidote targets the most recent injected Fact and restores the original object.",
      "Run Current state after each step to traverse the live SUPERSEDED_BY trajectory.",
    ],
    example: "Poison object: POISON::<original object>. Antidote object: the exact original object.",
    hydradgExpansion: "Every intervention creates Fact + Perturbation + FCGDelta + ClassificationEvent nodes; the old Fact remains present rather than being destructively overwritten.",
    falsifier: "A load-bearing poison should create first divergence and changed current state; an unrelated/normal control should not create a contradictory value change.",
    evidenceState: "LIVE_HYDRADB_FCG_PERTURBATION_DEMO_ONLY",
  },
  {
    id: "current",
    title: "Current-state traversal",
    hydradbPattern: "Temporal reasoning / graph relations",
    why: "Vector similarity alone does not encode which authentic fact is current. This query resolves the leaf of the explicit supersession chain for one subject/predicate.",
    how: [
      "Load a case and select a Fact.",
      "Subject and Predicate are populated from that Fact.",
      "Click Resolve current state before poison, after poison and after antidote.",
      "Compare the returned trajectory and SUPERSEDED_BY edges.",
    ],
    example: "subject=user, predicate=lives_in (actual values depend on the loaded case)",
    hydradgExpansion: "Returns both the selected current leaf and the full ordered trajectory so the explanation is auditable.",
    falsifier: "If a superseded predecessor is returned as current despite a reachable successor, traversal semantics are wrong.",
    evidenceState: "RECOMPUTED_LIVE_HYDRADB_TRAVERSAL",
  },
  {
    id: "cloud",
    title: "Official HydraDB cookbook conformance",
    hydradbPattern: "Tenant + Memories + Recall + graph_context + List/Relations",
    why: "The hackathon backend uses pinned self-hosted HydraDB directly. This independent lane checks that our product concepts also map cleanly onto HydraDB's documented hosted API contract.",
    how: [
      "Configure HYDRADB_API_KEY and HYDRADB_TENANT_ID locally; never paste the key into the page.",
      "Run Tenant status first; this is read-only.",
      "Run Full recall with graph_context enabled and inspect chunks/graph context.",
      "Use Store demo memory only in the dedicated hydradg-judge-demo sub-tenant, then Recall preferences.",
      "Use List and Relations to inspect the resulting source/graph surface when IDs are available.",
    ],
    example: "Memory: The HydraDG judge demo prefers graph paths with explicit provenance and current-state explanations.",
    hydradgExpansion: "Adds FCO/FCG custody, explicit perturbation events, Anticube admission and matched causal controls around the documented HydraDB memory/retrieval primitives.",
    falsifier: "If the hosted API rejects our documented request shapes or fails the add→recall/list relation, we mark cookbook conformance failed rather than treating local graph success as equivalent.",
    evidenceState: "EXECUTION_PENDING_API_CREDENTIAL",
  },
];

export const COOKBOOK_MATRIX = [
  {
    cookbook: "Onboarding / Perplexity",
    hydradb: "Multi-source knowledge + full_recall + graph_context + cited provenance",
    hydradg: "LongMemEval real case → typed graph → explicit evidence path → FCO/FCG receipt",
    test: "Compare baseline vs graph method and inspect source/session path",
  },
  {
    cookbook: "Persistent memories",
    hydradb: "add_memory(infer true/false) + recall_preferences",
    hydradg: "Normal/poison/antidote Fact updates with immutable history and Anticube event",
    test: "Add → recall; then perturb → current-state traversal → recovery",
  },
  {
    cookbook: "Chief of Staff / function routing",
    hydradb: "Recall candidate functions, graph_context, user preferences, execution/audit memories",
    hydradg: "Independent Anticube policy/admission event + FCG delta before claim/action promotion",
    test: "Safe/unsafe declaration changes admission route while preserving candidate provenance",
  },
  {
    cookbook: "Travel / complex planning",
    hydradb: "thinking mode + graph relations/query paths",
    hydradg: "Method-D graph reasons + visible golden dependency path",
    test: "Inspect path reasons and counterfactual edge ablation",
  },
  {
    cookbook: "Metadata / deterministic control",
    hydradb: "Tenant/sub-tenant and metadata filtering constrain retrieval",
    hydradg: "Project/case/session identity and claim ceilings constrain traversal/admission",
    test: "Wrong scope must fail closed rather than silently cross contexts",
  },
];
