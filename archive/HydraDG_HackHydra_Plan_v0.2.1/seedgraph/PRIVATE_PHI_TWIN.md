# Parallel PHI-private SeedGraph design

## Rule
The public Hack Hydra graph contains only public benchmark data, synthetic data, and non-PHI project evidence.

A private PHI graph may share the **schema and software**, but not the data store, credentials, identifiers, embeddings, logs, hashes, caches, or exported graph.

## Two-store topology

PUBLIC:
`LongMemEval/public project sources -> public SeedGraph JSONL -> public HydraDB/demo`

PRIVATE:
`PHI/ePHI -> private ingestion -> private FCO/FCG -> private graph -> private retrieval`

There is no automatic PUBLIC <-> PRIVATE edge.

## PHI identifier policy
- Do not publish content-derived identifiers or hashes of raw PHI.
- Use random internal object IDs for portable references.
- If exact content hashes are needed for internal custody, keep them inside the private security boundary.
- Do not export re-identification mappings.
- De-identified exports require a documented de-identification pathway appropriate to the applicable context.

## Cloud boundary
If a cloud service creates, receives, maintains, or transmits ePHI for a HIPAA-regulated entity, HHS guidance treats it as a business associate and requires an appropriate BAA and risk-management posture. Encryption without the provider holding the key does not by itself remove business-associate status.

## Public demo
Use LongMemEval + synthetic clinical-shaped examples with no real patient data.

## Private twin evaluation
Evaluate the same mechanical properties:
- provenance completeness
- temporal supersession
- first divergence
- claim/admission gating
- recovery
- access isolation
but keep all patient-derived data/results within the private environment unless properly de-identified/authorized.

**This is an architecture plan, not a statement that any deployment is HIPAA compliant.**
