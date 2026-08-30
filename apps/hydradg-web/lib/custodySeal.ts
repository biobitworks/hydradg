export const CUSTODY_SEAL = {
  object_identity: {
    algorithm: "SHA-256",
    rule: "ONE_CANONICAL_SHA256_PER_FCO",
    meaning: "Byte/object identity only; not authorship, truth, or verification.",
  },
  hydradg_project: {
    signing_algorithm: "Ed25519",
    signature_state: "PENDING_EXTERNAL_PRIVATE_KEY_OPERATION",
    public_key_state: "NO_CURRENT_PROJECT_PUBLIC_KEY_RECEIPT_ADMITTED_IN_THIS_RELEASE",
    private_key_policy: "EXTERNAL_SECRET_NOT_IN_GIT_HYDRADB_BROWSER_HTML_OR_PIXELS",
    detached_signature_state: "NOT_PRESENT_FOR_EACH_CURRENT_PROJECT_FCO_FCG",
    merkle_state: "NOT_PROJECT_COMMITTED",
    claim_ceiling: "HASHED_PROJECT_CUSTODY_OBJECTS_NOT_CURRENTLY_PROJECT_SIGNED_OR_MERKLE_COMMITTED",
  },
  fco_publication_v1: {
    doi: "10.5281/zenodo.21210575",
    signature_scope: "PUBLICATION_FCG_ROOT_ONLY_NOT_HYDRADG_PROJECT_GRAPH",
    signing_algorithm: "Ed25519",
    public_key_sha256_fingerprint: "f496a067808026d45fbbad785bf83c6acd66429c2d257d246cc103c6d7ff460d",
    signed_fcg_root_prefix: "741d12de",
    external_authority: "Zenodo public record and project publication lineage",
  },
} as const;

export const PROJECT_SIGNING_FLOW = [
  "canonical FCO/FCG bytes",
  "SHA-256 identity",
  "authorized external Ed25519 private-key operation",
  "detached signature",
  "public-key verification",
  "SigningReceiptFCO",
  "FCG successor edge",
] as const;
