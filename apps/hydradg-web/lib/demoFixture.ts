import { computeStateField, deterministicPoint } from "@/lib/fcg4d";
import { makeFcoNode } from "@/lib/fco";

export const DEMO_SUBJECT_KEY = "hydradg.demo.memory";

export function buildDemoFixture() {
  const source = makeFcoNode("Source", {
    source_ref: "fixture://hydradg-track03",
    title: "HydraDG deterministic Track 03 demo fixture",
    source_type: "SYNTHETIC_TEST_FIXTURE",
    project_license: "CC-BY-NC-ND-4.0",
    evidence_class: "DIRECTLY_SUPPLIED_TEST_FIXTURE",
    admission_state: "SYNTHETIC_TEST_FIXTURE",
    claim_ceiling: "DEMO_FIXTURE_ONLY",
    custody_state: "HASHED",
    observed_at: "2026-08-18T00:00:00Z",
  });

  const evidenceV1 = makeFcoNode("Evidence", {
    source_ref: source.id,
    version: 1,
    statement: "The demo memory state is alpha.",
    evidence_class: "DIRECTLY_SUPPLIED_TEST_FIXTURE",
    claim_ceiling: "DEMO_FIXTURE_ONLY",
    custody_state: "HASHED",
    observed_at: "2026-08-18T00:00:01Z",
  });

  const evidenceMutation = makeFcoNode("Evidence", {
    source_ref: source.id,
    version: 2,
    statement: "A synthetic perturbation changes the demo state away from the reference.",
    evidence_class: "DIRECTLY_SUPPLIED_TEST_FIXTURE",
    claim_ceiling: "DEMO_FIXTURE_ONLY",
    custody_state: "HASHED",
    observed_at: "2026-08-18T00:00:02Z",
  });

  const evidenceV2 = makeFcoNode("Evidence", {
    source_ref: source.id,
    version: 3,
    statement: "Corrected evidence restores the graph toward its reference basin and establishes beta as current.",
    evidence_class: "DIRECTLY_SUPPLIED_TEST_FIXTURE",
    claim_ceiling: "DEMO_FIXTURE_ONLY",
    custody_state: "HASHED",
    observed_at: "2026-08-18T00:00:03Z",
  });

  const atomV1 = makeFcoNode("KnowledgeAtom", {
    subject_key: DEMO_SUBJECT_KEY,
    version: 1,
    is_current: false,
    statement: "HydraDG demo state = alpha",
    evidence_class: "DETERMINISTIC_TRANSFORM",
    claim_ceiling: "DEMO_FIXTURE_ONLY",
    custody_state: "HASHED",
    observed_at: "2026-08-18T00:00:01Z",
  });

  const atomMutation = makeFcoNode("KnowledgeAtom", {
    subject_key: DEMO_SUBJECT_KEY,
    version: 2,
    is_current: false,
    statement: "HydraDG demo state = perturbed",
    evidence_class: "DETERMINISTIC_TRANSFORM",
    claim_ceiling: "DEMO_FIXTURE_ONLY",
    custody_state: "HASHED",
    observed_at: "2026-08-18T00:00:02Z",
  });

  const atomV2 = makeFcoNode("KnowledgeAtom", {
    subject_key: DEMO_SUBJECT_KEY,
    version: 3,
    is_current: true,
    statement: "HydraDG demo state = beta",
    evidence_class: "DETERMINISTIC_TRANSFORM",
    claim_ceiling: "DEMO_FIXTURE_ONLY",
    custody_state: "HASHED",
    observed_at: "2026-08-18T00:00:03Z",
  });

  const seedV1 = makeFcoNode("SeedOfTruth", {
    subject_key: DEMO_SUBJECT_KEY,
    version: 1,
    is_current: false,
    statement: "Reference demo state is alpha.",
    evidence_class: "INFERENCE_FROM_TEST_FIXTURE",
    claim_ceiling: "DEMO_FIXTURE_ONLY",
    custody_state: "HASHED",
    observed_at: "2026-08-18T00:00:01Z",
  });

  const seedMutation = makeFcoNode("SeedOfTruth", {
    subject_key: DEMO_SUBJECT_KEY,
    version: 2,
    is_current: false,
    statement: "Synthetic perturbation state is active.",
    evidence_class: "INFERENCE_FROM_TEST_FIXTURE",
    claim_ceiling: "DEMO_FIXTURE_ONLY",
    custody_state: "HASHED",
    observed_at: "2026-08-18T00:00:02Z",
  });

  const seedV2 = makeFcoNode("SeedOfTruth", {
    subject_key: DEMO_SUBJECT_KEY,
    version: 3,
    is_current: true,
    statement: "Current demo state is beta after restoration/correction.",
    evidence_class: "INFERENCE_FROM_TEST_FIXTURE",
    claim_ceiling: "DEMO_FIXTURE_ONLY",
    custody_state: "HASHED",
    observed_at: "2026-08-18T00:00:03Z",
  });

  const stateMetrics = computeStateField([
    { t: 0, label: "reference", distribution: [0.88, 0.08, 0.04], burden: 0.08 },
    { t: 1, label: "mutation", distribution: [0.18, 0.72, 0.10], burden: 0.82 },
    { t: 2, label: "restoration", distribution: [0.76, 0.14, 0.10], burden: 0.20 },
  ]);

  const snapshots = stateMetrics.map((metric, index) =>
    makeFcoNode("StateSnapshot", {
      subject_key: DEMO_SUBJECT_KEY,
      version: index + 1,
      is_current: index === stateMetrics.length - 1,
      state_label: metric.label,
      t_index: metric.t,
      state_distribution: metric.distribution,
      shannon_entropy_bits: metric.shannon_entropy,
      normalized_shannon_entropy: metric.normalized_entropy,
      perturbation_burden_u_star: metric.burden,
      g_star: metric.g_star,
      delta_g_star: metric.delta_g_star,
      mutation_distance: metric.mutation_distance,
      restoration_gain: metric.restoration_gain,
      metric_contract: "DIMENSIONLESS_INFORMATION_STATE_ABSTRACTION",
      physical_gibbs_free_energy: false,
      claim_ceiling: "SYNTHETIC_INFORMATION_STATE_VISUALIZATION_ONLY",
      evidence_class: "DETERMINISTIC_TRANSFORM_OF_DECLARED_FIXTURE_DISTRIBUTION",
      custody_state: "HASHED",
      observed_at: `2026-08-18T00:00:0${index + 1}Z`,
    }),
  );

  const atomClassification = makeFcoNode("ClassificationReceipt", {
    subject_id: atomV2.id,
    classifier: "Anticube adapter",
    classifier_state: "IMPLEMENTATION_PENDING_PUBLIC_CONTRACT",
    evidence_class: "DETERMINISTIC_TRANSFORM",
    claim_ceiling: "CLASSIFICATION_NOT_EXECUTED",
    custody_state: "HASHED_FAIL_CLOSED",
    observed_at: "2026-08-18T00:00:03Z",
  });

  const seedClassification = makeFcoNode("ClassificationReceipt", {
    subject_id: seedV2.id,
    classifier: "Anticube adapter",
    classifier_state: "IMPLEMENTATION_PENDING_PUBLIC_CONTRACT",
    evidence_class: "DETERMINISTIC_TRANSFORM",
    claim_ceiling: "CLASSIFICATION_NOT_EXECUTED",
    custody_state: "HASHED_FAIL_CLOSED",
    observed_at: "2026-08-18T00:00:03Z",
  });

  const nodes = [
    ["Source", source],
    ["Evidence", evidenceV1],
    ["Evidence", evidenceMutation],
    ["Evidence", evidenceV2],
    ["KnowledgeAtom", atomV1],
    ["KnowledgeAtom", atomMutation],
    ["KnowledgeAtom", atomV2],
    ["SeedOfTruth", seedV1],
    ["SeedOfTruth", seedMutation],
    ["SeedOfTruth", seedV2],
    ["StateSnapshot", snapshots[0]],
    ["StateSnapshot", snapshots[1]],
    ["StateSnapshot", snapshots[2]],
    ["ClassificationReceipt", atomClassification],
    ["ClassificationReceipt", seedClassification],
  ] as const;

  const edges = [
    [evidenceV1.id, "DERIVED_FROM", source.id],
    [evidenceMutation.id, "DERIVED_FROM", source.id],
    [evidenceV2.id, "DERIVED_FROM", source.id],
    [atomV1.id, "DERIVED_FROM", evidenceV1.id],
    [atomMutation.id, "DERIVED_FROM", evidenceMutation.id],
    [atomV2.id, "DERIVED_FROM", evidenceV2.id],
    [seedV1.id, "SUPPORTED_BY", atomV1.id],
    [seedMutation.id, "SUPPORTED_BY", atomMutation.id],
    [seedV2.id, "SUPPORTED_BY", atomV2.id],
    [atomV1.id, "SUPERSEDED_BY", atomMutation.id],
    [atomMutation.id, "SUPERSEDED_BY", atomV2.id],
    [seedV1.id, "SUPERSEDED_BY", seedMutation.id],
    [seedMutation.id, "SUPERSEDED_BY", seedV2.id],
    [snapshots[0].id, "OBSERVES", seedV1.id],
    [snapshots[1].id, "OBSERVES", seedMutation.id],
    [snapshots[2].id, "OBSERVES", seedV2.id],
    [snapshots[0].id, "TRANSITIONS_TO", snapshots[1].id],
    [snapshots[1].id, "TRANSITIONS_TO", snapshots[2].id],
    [atomClassification.id, "CLASSIFIES", atomV2.id],
    [seedClassification.id, "CLASSIFIES", seedV2.id],
  ] as const;

  const tById = new Map<string, number>([
    [source.id, 0],
    [evidenceV1.id, 0],
    [atomV1.id, 0],
    [seedV1.id, 0],
    [snapshots[0].id, 0],
    [evidenceMutation.id, 1],
    [atomMutation.id, 1],
    [seedMutation.id, 1],
    [snapshots[1].id, 1],
    [evidenceV2.id, 2],
    [atomV2.id, 2],
    [seedV2.id, 2],
    [snapshots[2].id, 2],
    [atomClassification.id, 2],
    [seedClassification.id, 2],
  ]);

  const scene = {
    nodes: nodes.map(([label, node]) => ({
      id: node.id,
      label,
      ...deterministicPoint(node.id, tById.get(node.id) || 0),
      access: label === "ClassificationReceipt" ? "toy-locked" : "public",
      payload: node.payload,
    })),
    links: edges.map(([sourceId, relation, targetId]) => ({ source: sourceId, target: targetId, relation })),
  };

  return {
    subject_key: DEMO_SUBJECT_KEY,
    nodes,
    edges,
    timeline: stateMetrics,
    scene,
    ids: {
      source: source.id,
      evidence_v1: evidenceV1.id,
      evidence_mutation: evidenceMutation.id,
      evidence_v2: evidenceV2.id,
      atom_v1: atomV1.id,
      atom_mutation: atomMutation.id,
      atom_v2: atomV2.id,
      seed_v1: seedV1.id,
      seed_mutation: seedMutation.id,
      seed_v2: seedV2.id,
      snapshot_v1: snapshots[0].id,
      snapshot_mutation: snapshots[1].id,
      snapshot_restoration: snapshots[2].id,
      atom_classification: atomClassification.id,
      seed_classification: seedClassification.id,
    },
  };
}
