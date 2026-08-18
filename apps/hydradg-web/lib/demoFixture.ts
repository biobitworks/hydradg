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
  });

  const evidenceV1 = makeFcoNode("Evidence", {
    source_ref: source.id,
    version: 1,
    statement: "The demo memory state is alpha.",
    evidence_class: "DIRECTLY_SUPPLIED_TEST_FIXTURE",
    claim_ceiling: "DEMO_FIXTURE_ONLY",
    custody_state: "HASHED",
  });

  const evidenceV2 = makeFcoNode("Evidence", {
    source_ref: source.id,
    version: 2,
    statement: "The demo memory state is beta after revised evidence.",
    evidence_class: "DIRECTLY_SUPPLIED_TEST_FIXTURE",
    claim_ceiling: "DEMO_FIXTURE_ONLY",
    custody_state: "HASHED",
  });

  const atomV1 = makeFcoNode("KnowledgeAtom", {
    subject_key: DEMO_SUBJECT_KEY,
    version: 1,
    is_current: false,
    statement: "HydraDG demo state = alpha",
    evidence_class: "DETERMINISTIC_TRANSFORM",
    claim_ceiling: "DEMO_FIXTURE_ONLY",
    custody_state: "HASHED",
  });

  const atomV2 = makeFcoNode("KnowledgeAtom", {
    subject_key: DEMO_SUBJECT_KEY,
    version: 2,
    is_current: true,
    statement: "HydraDG demo state = beta",
    evidence_class: "DETERMINISTIC_TRANSFORM",
    claim_ceiling: "DEMO_FIXTURE_ONLY",
    custody_state: "HASHED",
  });

  const seedV1 = makeFcoNode("SeedOfTruth", {
    subject_key: DEMO_SUBJECT_KEY,
    version: 1,
    is_current: false,
    statement: "Current demo state is alpha.",
    evidence_class: "INFERENCE_FROM_TEST_FIXTURE",
    claim_ceiling: "DEMO_FIXTURE_ONLY",
    custody_state: "HASHED",
  });

  const seedV2 = makeFcoNode("SeedOfTruth", {
    subject_key: DEMO_SUBJECT_KEY,
    version: 2,
    is_current: true,
    statement: "Current demo state is beta.",
    evidence_class: "INFERENCE_FROM_TEST_FIXTURE",
    claim_ceiling: "DEMO_FIXTURE_ONLY",
    custody_state: "HASHED",
  });

  const atomClassification = makeFcoNode("ClassificationReceipt", {
    subject_id: atomV2.id,
    classifier: "Anticube adapter",
    classifier_state: "IMPLEMENTATION_PENDING_PUBLIC_CONTRACT",
    evidence_class: "DETERMINISTIC_TRANSFORM",
    claim_ceiling: "CLASSIFICATION_NOT_EXECUTED",
    custody_state: "HASHED_FAIL_CLOSED",
  });

  const seedClassification = makeFcoNode("ClassificationReceipt", {
    subject_id: seedV2.id,
    classifier: "Anticube adapter",
    classifier_state: "IMPLEMENTATION_PENDING_PUBLIC_CONTRACT",
    evidence_class: "DETERMINISTIC_TRANSFORM",
    claim_ceiling: "CLASSIFICATION_NOT_EXECUTED",
    custody_state: "HASHED_FAIL_CLOSED",
  });

  const nodes = [
    ["Source", source],
    ["Evidence", evidenceV1],
    ["Evidence", evidenceV2],
    ["KnowledgeAtom", atomV1],
    ["KnowledgeAtom", atomV2],
    ["SeedOfTruth", seedV1],
    ["SeedOfTruth", seedV2],
    ["ClassificationReceipt", atomClassification],
    ["ClassificationReceipt", seedClassification],
  ] as const;

  const edges = [
    [evidenceV1.id, "DERIVED_FROM", source.id],
    [evidenceV2.id, "DERIVED_FROM", source.id],
    [atomV1.id, "DERIVED_FROM", evidenceV1.id],
    [atomV2.id, "DERIVED_FROM", evidenceV2.id],
    [seedV1.id, "SUPPORTED_BY", atomV1.id],
    [seedV2.id, "SUPPORTED_BY", atomV2.id],
    [atomV1.id, "SUPERSEDED_BY", atomV2.id],
    [seedV1.id, "SUPERSEDED_BY", seedV2.id],
    [atomClassification.id, "CLASSIFIES", atomV2.id],
    [seedClassification.id, "CLASSIFIES", seedV2.id],
  ] as const;

  return {
    subject_key: DEMO_SUBJECT_KEY,
    nodes,
    edges,
    ids: {
      source: source.id,
      evidence_v1: evidenceV1.id,
      evidence_v2: evidenceV2.id,
      atom_v1: atomV1.id,
      atom_v2: atomV2.id,
      seed_v1: seedV1.id,
      seed_v2: seedV2.id,
      atom_classification: atomClassification.id,
      seed_classification: seedClassification.id,
    },
  };
}
