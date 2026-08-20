# HydraDB Hosted Deployment Status — 2026-08-20

## Scope

This document records deployment state only. It does not contain or disclose any credential value.

## Current hosted wiring

- GitHub repository source: `biobitworks/hydradg`
- HydraDB hosted database: `hydradg`
- HydraDB API key: configured in Vercel by the project owner; value intentionally not recorded here
- Canonical hosted API vocabulary: `database` / `collection`
- `HYDRADB_COLLECTION`: intentionally unset unless the HydraDB connector/import was explicitly scoped to a named collection
- HydraDB API base: `https://api.hydradb.com`
- Vercel server must use `API-Version: 2`
- Browser-facing responses must never expose HydraDB credential values

## Deployment sequence

1. GitHub content is indexed into hosted HydraDB database `hydradg` through the HydraDB GitHub connector.
2. Vercel receives `HYDRA_DB_API_KEY` and `HYDRADB_DATABASE=hydradg` as server-side environment variables.
3. The curated web build exposes read-only server routes for:
   - database/collection discovery,
   - HydraDB v2 query with `graph_context=true`,
   - public-safe hosted status/readback.
4. The exact collection must be discovered from hosted HydraDB or matched to the connector configuration before collection-scoped readback is claimed.
5. A successful readback establishes hosted connectivity/context return only; it does not establish scientific correctness.

## Local → hosted parity boundary

The canonical FCO/FCG remains backend-independent. Moving its projection from local HydraDB to hosted HydraDB should not itself change canonical FCO identity, FCG edge identity, or the backend-independent Context Iceberg state. Retrieval ranking, latency, graph paths, Hit@K and Recall@K are measured separately as service-level deltas.

## Current claim state

- `HYDRADB_API_KEY_CONFIGURED_IN_VERCEL`: USER_ATTESTED
- `CURATED_BRANCH_DEPLOYED_WITH_KEY`: PENDING
- `HOSTED_DATABASE_READBACK`: PENDING
- `HOSTED_COLLECTION_IDENTIFIED`: PENDING
- `LOCAL_TO_HOSTED_PARITY`: NOT_ESTABLISHED
- `SIGNATURE_STATE`: NOT_SIGNED
- `MERKLE_STATE`: NOT_MERKLE_COMMITTED
