# HydraDG Daisy K5/K10 × Representation Matrix

Primary question: what changes when the exact same frozen LongMemEval-S full500 corpus is
retrieved at K=5 vs K=10, before and after deterministic SeedGraph/FCO/FCG materialization?

Primary 2×2 cells:

| Representation | K=5 | K=10 |
|---|---|---|
| RAW / no semantic extraction | RAW_K5 | RAW_K10 |
| SeedGraph/FCO/FCG deterministic materialization | SG_K5 | SG_K10 |

Each cell is repeated 3 times. Each replicate uses an isolated HydraDB namespace.

Scientific nulls:
1. Determinism: within a cell, canonical result hashes are identical across replicates.
2. Representation effect: H0_rep(k): metric(SG_k) - metric(RAW_k) = 0.
3. Directional promotion gate: H0_adv(k): metric(SG_k) - metric(RAW_k) <= 0.
4. Retrieval-depth effect: H0_k(rep): metric(rep,K10) - metric(rep,K5) <= 0.
5. Interaction: H0_int: [SG_K10-RAW_K10] - [SG_K5-RAW_K5] = 0.

Primary metrics: hit@k and mean session recall@k.
Evidence-path coverage is mechanistic/secondary.
Latency is operational and excluded from deterministic payload equality.

Important:
- The historical K=5 heuristic run is retained as LEGACY_K5_HEURISTIC and is not relabeled
  as the clean SG_K5 cell.
- RAW uses extractor=none.
- SeedGraph/FCO/FCG uses one frozen deterministic materialization cache generated once and
  reused by K5/K10 and all replicates.
- Ollarma is not in the primary matrix. It is a future probabilistic augmentation lane.
  If later used, generate once, cache/freeze prompt+response hashes, and replay from cache.
- Held-out LongMemEval answer_session_ids remain evaluation-only and are not used in graph
  construction or ranking.

Order:
1. Preserve dirty work and create a local experiment branch from the exact historical run commit.
2. Freeze LongMemEval-S bytes and manifest.
3. Materialize deterministic SeedGraph/FCO/FCG sidecars and extraction cache.
4. Use isolated namespaces and run 4 cells × 3 repeats.
5. Canonicalize/hashes are produced by the matrix runner.
6. Require replicate hash equality before cross-cell statistics.
7. Append experiment objects/edges to the local FCG.
8. Build a matrix root and sign it offline on magicPRObox with the project Ed25519 key.
