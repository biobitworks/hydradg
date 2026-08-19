import JudgeLab from "./JudgeLab";

import { buildDemoFixture } from "@/lib/demoFixture";
import { makeFcoNode } from "@/lib/fco";
import { computeMerkleCheckpoint } from "@/lib/merkle";

export default function JudgePage() {
  const fixture = buildDemoFixture();
  const merkle = computeMerkleCheckpoint(
    fixture.nodes.map(([, node]) => ({ id: node.id, sha256: node.object_sha256 })),
  );
  const checkpointFco = makeFcoNode("MerkleCheckpoint", {
    algorithm: merkle.algorithm,
    ordering: merkle.ordering,
    odd_leaf_rule: merkle.odd_leaf_rule,
    leaf_count: merkle.leaf_count,
    root_sha256: merkle.root_sha256,
    subject_key: fixture.subject_key,
    evidence_class: "DETERMINISTIC_TRANSFORM_OF_FIXTURE_FCO_IDENTITIES",
    claim_ceiling: "DETERMINISTIC_FIXTURE_MERKLE_CHECKPOINT_ONLY",
    signature_state: "NOT_SIGNED",
    hydradb_persistence_state: "NOT_WRITTEN_BY_PAGE_RENDER",
  });
  const goldenPath = [
    fixture.ids.source,
    fixture.ids.evidence_v2,
    fixture.ids.atom_v2,
    fixture.ids.seed_v2,
    fixture.ids.snapshot_restoration,
    fixture.ids.seed_classification,
    checkpointFco.id,
  ];
  const custody = {
    merkle,
    checkpoint_fco: checkpointFco,
    golden_path: goldenPath,
    golden_path_semantics: [
      "Source",
      "Evidence",
      "KnowledgeAtom",
      "SeedOfTruth",
      "StateSnapshot",
      "ClassificationReceipt",
      "MerkleCheckpoint",
    ],
  };

  return <JudgeLab fixture={fixture} custody={custody} />;
}
