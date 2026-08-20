// HydraDG MVP logical graph schema (OpenCypher-oriented)
// Keep application-level FCO/FCG object identifiers explicit.

CREATE CONSTRAINT seed_id_unique IF NOT EXISTS
FOR (n:SeedObject) REQUIRE n.id IS UNIQUE;

// Suggested labels:
// Source, Session, Turn, Atom, Fact, Claim, Run, TensorState,
// Perturbation, Recovery, Answer, Evaluation, Artifact
//
// Suggested relationships:
// CONTAINS, DERIVED_FROM, DEPENDS_ON, SUPPORTS, CONTRADICTS,
// SUPERSEDES, UPDATES, PERTURBS, FIRST_DIVERGED_AT, AFFECTS,
// INVALIDATES, RECOVERS_FROM, VALIDATED_BY, ANSWERED_BY
//
// Temporal properties:
// transaction_time, valid_from, valid_to, observed_at
//
// FCO/FCG properties:
// evidence_class, claim_ceiling, visibility, custody_state
//
// Do not use this file as evidence that HydraDB accepted these exact DDL statements.
// Validate against the pinned HydraDB commit/runtime used for the hackathon.
