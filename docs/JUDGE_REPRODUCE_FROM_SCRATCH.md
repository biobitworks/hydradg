# Judge Reproduction Guide — HydraDG from Scratch

This guide reconstructs the **HydraDG website and its HydraDB-backed graph projection** from the public repository without requiring access to the original magicSTUDIObox.

The canonical custody data is stored in this repository. HydraDB is treated as a query/projection layer, not as the source of canonical identity.

## 0. What you are reproducing

You will recreate:

1. the public HydraDG FCO/FCG graph snapshot;
2. its projection into an isolated HydraDB graph namespace;
3. deterministic readback/count verification;
4. the Next.js judge website;
5. the Context Iceberg / 4D FCG presentation layer;
6. the Track 03 result and provenance surfaces.

You do **not** need the original developer machine or its database directory.

## 1. Repository layout used by the reproduction

```text
apps/hydradg-web/                  Next.js / React website source
apps/hydradg-web/.env.example      local configuration template
custody/graph/live/nodes.jsonl     canonical public FCG node snapshot
custody/graph/live/edges.jsonl     canonical public FCG edge snapshot
custody/                            public-safe custody / lineage receipts
scripts/project_fcg_snapshot_to_hydradb.py
                                    deterministic FCG -> HydraDB importer
scripts/project_website_knowledge_to_hydradb.py
                                    Knowledge FCO projection helper
scripts/release_gate.sh             release verifier
.github/workflows/gitleaks-release.yml
                                    full-history secret scan
HydraDG_DaisyTrain_v0.3.7/         Track 03 evaluation / reproduction tools
SUBMISSION.md                       submission-specific scope and claims
```

## 2. Prerequisites

- Git
- Python 3.10+
- Node.js 20+ and npm
- a working HydraDB graph endpoint compatible with the Hack Hydra local graph API, or the HydraDB environment supplied by the hackathon
- an isolated HydraDB namespace

For the website itself, dependencies are pinned by `apps/hydradg-web/package-lock.json`.

HydraDB is an upstream dependency and is not vendored into this repository. Use the official Hack Hydra / HydraDB distribution supplied by HydraDB. HydraDG-specific graph data and projection logic are included here.

## 3. Clone the exact submission repository

```bash
git clone https://github.com/biobitworks/hydradg.git
cd hydradg
```

For pre-publication review, the authoritative release branch is:

```bash
git checkout hack-hydra/public-product-final-20260819
```

Once `main` is fast-forwarded for submission, judges can remain on `main`.

## 4. Inspect the canonical FCG snapshot

The graph projection source is:

```text
custody/graph/live/nodes.jsonl
custody/graph/live/edges.jsonl
```

Every node retains its public-safe payload, type/schema metadata, and claim boundary where applicable. Edges retain explicit predicates and evidence classes.

The executed Track 03 experiment root used as the readback canary is:

```text
experiment:fa170ab51cdfba46f9a24979c9be9b90fdc4ccedcdb292f313aa4439a92b08d8
```

## 5. Start HydraDB

Start the HydraDB environment provided by the Hack Hydra project and expose the graph-query endpoint expected by HydraDG.

The local demo contract is:

```text
HTTP base:  http://127.0.0.1:8443
Graph ID:   default
Cell ID:    cell-0
Namespace:  choose an isolated namespace such as hydradg-judge-repro
```

Do not reuse a shared/default production namespace for reproduction.

Store the HydraDB bearer token in a local file outside Git. Example:

```bash
mkdir -p ~/.local/share/hydradg-repro
printf '%s' "$HYDRADB_AUTH_TOKEN" > ~/.local/share/hydradg-repro/hydradb-auth-token
chmod 600 ~/.local/share/hydradg-repro/hydradb-auth-token
```

Never commit that token.

## 6. Recreate the HydraDB graph from the canonical snapshot

Run the included deterministic importer:

```bash
python3 scripts/project_fcg_snapshot_to_hydradb.py \
  --nodes custody/graph/live/nodes.jsonl \
  --edges custody/graph/live/edges.jsonl \
  --endpoint http://127.0.0.1:8443/v1/graphs/default/query \
  --token-file ~/.local/share/hydradg-repro/hydradb-auth-token \
  --namespace hydradg-judge-repro \
  --allow-write \
  --out repro/receipts/HYDRADB_FCG_IMPORT_RECEIPT.json
```

The importer fails closed if:

- either JSONL file is malformed;
- a node ID is duplicated;
- an edge references a missing node;
- an edge predicate is not a safe canonical token;
- the namespace is default/shared/production;
- the readback node/edge counts do not match;
- the expected Track 03 experiment root cannot be read back.

Expected terminal state:

```text
HYDRADB_FCG_IMPORT=PASS
```

The generated receipt records SHA-256 identifiers for the source JSONL files, expected/observed node and edge counts, the FCG root canary, and the reproduction claim ceiling.

## 7. Configure the website

```bash
cd apps/hydradg-web
cp .env.example .env.local
```

Edit `.env.local` for your isolated reproduction environment:

```dotenv
GRAPH_BACKEND=hydradb-http
HYDRADB_HTTP_URL=http://127.0.0.1:8443
HYDRADB_GRAPH_ID=default
HYDRADB_GRAPH_NAMESPACE=hydradg-judge-repro
HYDRADB_CELL_ID=cell-0
HYDRADB_AUTH_TOKEN=<local token only>
```

Leave optional third-party integrations unset unless you are explicitly testing them.

## 8. Build and run the website

From `apps/hydradg-web`:

```bash
npm ci
npm run typecheck
npm run build
npm run start -- -p 3012
```

Open:

```text
http://127.0.0.1:3012/
```

Judge routes:

```text
/
/judge
/track03
/graph
/knowledge
/how-to
/eligibility
/backup/hydradg.html
```

The static fallback is presentation-only and must not be interpreted as a live HydraDB surface.

## 9. What to verify in the UI

A successful reconstruction should let you inspect:

- Context Iceberg / 4D FCG presentation;
- G* / delta-G* as application-defined dimensionless information-state diagnostics;
- structural Cloud Drift separately from retrieval metrics;
- Hit@K and Recall@K separately from G*;
- the Reference -> Poison -> Antidote state-transition concept;
- Track 03 null/negative result preservation;
- FCO/FCG provenance and claim boundaries;
- the Ensslin & Weig -> HydraDG G* lineage with the explicit nonphysical boundary.

## 10. Reproduce the full Track 03 evaluation (optional, slower)

The website reconstruction above replays the public canonical graph snapshot. To recompute the Track 03 experiment rather than only project its accepted output, use the scripts under:

```text
HydraDG_DaisyTrain_v0.3.7/scripts/
```

Primary relevant entry points include:

```text
pull_track01_track03_datasets.sh
run_best_use_longmemeval.py
run_best_use_typed_longmemeval.py
run_submission_daisy_track03.sh
run_track03_live_golden_path.py
```

Dataset rights, source identities, and evaluation claim ceilings must be respected. The submission claim remains bounded to the executed retrieval ablation; it is not an end-to-end QA superiority claim.

## 11. Security verification before publishing or trusting a checkout

The release repository includes a fail-closed Gitleaks workflow:

```text
.github/workflows/gitleaks-release.yml
```

For a local checkout with Gitleaks installed:

```bash
gitleaks git --redact=100 --no-banner .
```

A public-release decision requires an actual zero-finding result on the exact release commit. A historical or partial scan is not sufficient.

## 12. Claim boundaries

Reconstructing the site and successfully projecting/readback-verifying the FCG establishes only that the public graph snapshot and application can be reproduced under the documented interface.

It does **not** by itself establish:

- benchmark superiority;
- end-to-end QA improvement;
- physical thermodynamic meaning for G*;
- causal linkage between lower G* and better retrieval;
- independent scientific replication of every experiment;
- cryptographic signature or Merkle commitment unless the corresponding receipts exist.

## 13. Demo video

Current Hack Hydra demo video:

```text
https://youtu.be/7EDb6q-loPA
```

The video demonstrates the local HydraDB-backed application. The GitHub repository provides the reconstruction materials.
