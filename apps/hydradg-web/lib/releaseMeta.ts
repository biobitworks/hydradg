import { buildDemoFixture } from "@/lib/demoFixture";
import { makeFcoNode } from "@/lib/fco";
import { buildKnowledgeProjection } from "@/lib/knowledgeFcg";
import { buildSiteFcg } from "@/lib/siteFcg";

export const RELEASE_LINE = "HydraDG Judge Release 2026.08.20";
export const RELEASE_BASE_MAIN_SHA = "abccbd3695f6f1a81d10bc352631beba009b3ce1";
export const HOSTED_DATABASE = "hydradg";
export const HOSTED_COLLECTION = "default";

function deployedGitSha() {
  return (
    process.env.VERCEL_GIT_COMMIT_SHA ||
    process.env.GITHUB_SHA ||
    process.env.HYDRADG_RELEASE_GIT_SHA ||
    "LOCAL_UNRESOLVED"
  );
}

function validateSingleHashPerFco() {
  const fixture = buildDemoFixture();
  const site = buildSiteFcg();
  const knowledge = buildKnowledgeProjection();
  const nodes = [
    ...fixture.nodes.map(([, node]) => node),
    ...site.nodes,
    site.artifact,
    ...knowledge.nodes,
    knowledge.root,
  ];

  const seen = new Map<string, string>();
  const problems: string[] = [];
  for (const node of nodes) {
    const expectedId = `fco:${node.object_sha256}`;
    if (node.id !== expectedId) problems.push(`id/hash mismatch:${node.id}`);
    if (!/^[0-9a-f]{64}$/i.test(node.object_sha256)) problems.push(`invalid sha256:${node.id}`);
    const prior = seen.get(node.id);
    const serialized = JSON.stringify(node);
    if (prior && prior !== serialized) problems.push(`conflicting duplicate:${node.id}`);
    seen.set(node.id, serialized);
  }

  return {
    status: problems.length === 0 ? "PASS" : "FAIL",
    unique_fco_count: seen.size,
    problems,
    identity_rule: "ONE_CANONICAL_SHA256_PER_FCO",
  } as const;
}

export function buildReleaseManifest() {
  const gitSha = deployedGitSha();
  const site = buildSiteFcg();
  const knowledge = buildKnowledgeProjection();
  const identityValidation = validateSingleHashPerFco();
  const version = `${RELEASE_LINE}+${gitSha === "LOCAL_UNRESOLVED" ? "local" : gitSha.slice(0, 12)}`;

  const fco = makeFcoNode("WebsiteRelease", {
    project: "HydraDG",
    release_version: version,
    release_line: RELEASE_LINE,
    deployed_git_sha: gitSha,
    release_base_main_sha: RELEASE_BASE_MAIN_SHA,
    site_artifact_fco_id: site.artifact.id,
    knowledge_root_fco_id: knowledge.root.id,
    hosted_database: HOSTED_DATABASE,
    hosted_collection: HOSTED_COLLECTION,
    hosted_canonical_parity_receipt: "eval/hosted_migration_20260820/HOSTED_PARITY.json",
    hosted_readback_receipt: "eval/hosted_migration_20260820/HOSTED_FCG_READBACK.json",
    context_contract: "T0_T2_SYNTHETIC_GSTAR_TAU_0_35__CLOUD_DRIFT_100X_JSD_BASE2__T3_T5_NO_SCALAR_WITHOUT_DECLARED_DISTRIBUTION",
    fco_identity_validation: identityValidation,
    custody_state: "HASHED",
    evidence_class: "DETERMINISTIC_BUILD_AND_RELEASE_METADATA",
    claim_ceiling: "DEPLOYED_VERSION_IDENTITY_AND_RELEASE_CUSTODY_ONLY",
    signature_state: "NOT_SIGNED",
    merkle_state: "NOT_MERKLE_COMMITTED",
  });

  return {
    schema: "hydradg.website_release.v1",
    version,
    git_sha: gitSha,
    release_fco: fco,
    fco_identity_validation: identityValidation,
    signature_state: "NOT_SIGNED",
    merkle_state: "NOT_MERKLE_COMMITTED",
  };
}
