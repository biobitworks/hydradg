# HydraDG — Hosted Judge Deployment

Status record for the Hack Hydra 2026 judge-facing hosted application.

## Submission surface

- Project: **HydraDG — Graph-Native Governed Context Engine**
- Primary track: **Track 03 — Memory + Context Retrieval**
- Repository: `https://github.com/biobitworks/hydradg`
- Vercel project: `hydradg`
- Vercel application root: `apps/hydradg-web`
- Hosted HydraDB API: `https://api.hydradb.com`
- HydraDB database: `hydradg`
- HydraDB collection: discovered/read from the connector scope; no collection is guessed when unset.
- HydraDB credential: configured server-side in Vercel; credential value is never committed or returned to the browser.

## Judge URL state

The final public judge URL is promoted only after the current curated deployment passes build, route, and hosted HydraDB readback checks.

Expected judge routes:

- `/`
- `/judge`
- `/track03`
- `/graph`
- `/knowledge`
- `/how-to`
- `/eligibility`
- `/backup/hydradg.html`
- `/api/graph/status`
- `/api/hydradb-v2/collections`
- `/api/hydradb-v2/query`

## Hosted data path

```text
GitHub repository
  -> HydraDB GitHub connector
  -> database: hydradg
  -> Vercel server-only HydraDB v2 adapter
  -> graph_context readback
  -> public-safe curated judge UI
```

The canonical FCO/FCG custody state remains distinct from the hosted projection. Moving local governed context to hosted HydraDB must not silently redefine canonical object identity or scientific results. Local-to-hosted custody parity and service/retrieval drift are measured separately.

## Claim boundary

A successful hosted readback establishes that the Vercel server can query the configured HydraDB database and return the bounded public-safe result. It does not by itself establish benchmark superiority, scientific correctness, independent replication, signing, or Merkle commitment.

Current cryptographic vocabulary remains separated:

- SHA-256: object/byte identity.
- Signature: authenticity only when an authorized signing key actually signs the object.
- Sealing/encryption: confidentiality when actually implemented and verified.

This document contains no credential values.
