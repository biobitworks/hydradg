# Multi-Model x Multi-Dataset Matrix Comparison Architecture (Extended 100-Cell Matrix)

This document specifies HydraDG's **Extended Multi-Model x Multi-Dataset Matrix Comparison Architecture**, evaluating **10 Popular LLM/Classifier Models** across 10 datasets spanning Track 01, Track 02, and Track 03 ($10 \times 10 = 100$ evaluation cells).

---

## 1. Matrix Overview & Evaluation Dimensions

The evaluation matrix evaluates $10 \times 10 = 100$ discrete evaluation cells. Each cell evaluates:
1. **Context State Metrics**: Shannon Entropy ($H$), Free-Energy Diagnostic ($G^*$), Free-Energy Delta ($\Delta G^*$), and Jensen-Shannon Cloud Drift.
2. **Information Energy Savings ($\Delta E_{\text{compute}}$)**: FLOPs saved ($2 \times N_{\text{params}} \times \Delta N_{\text{dedup\_tokens}}$) and Watt-hours saved (~100 TFLOPS/W GPU efficiency).
3. **Explicit Null Hypothesis Documentation**: Records exact null hypothesis state (`RETAINED_NO_SUPERIORITY_CLAIMED` or `REJECTED_CONTRADICTION_FOUND`) and description.
4. **Public Key Digital Signature**: Signed with author public key `HYDRADG_PUBLIC_CANARY_SOURCE_ID = fco:303b3fab6fd8831b84a37f789aa4ef1f1ab78a808572eddf8632d1b88f97e1d5`.

---

## 2. Evaluated Models (10 Popular Models)

1. **Vithia Baseline** (`hydradg-vithia-cfmo-v0.1` / `fco-vithia-fmo-076` — 7B params): Vitalogy & FCO baseline model evaluated against decomposed Vitalogy FCG graph.
2. **Anticube Contradiction Classifier** (`hydradg-anticube-classifier` — 3B params): Assigns `SAFE`/`ADMIT` vs `NONSAFE`/`QUARANTINE` labels to graph edges.
3. **Qwen 2.5 Coder** (`qwen2.5-coder-7b` — 7B params): Code-aware transformer for repo FCG graph execution.
4. **Qwen 3 Coder (Ollama)** (`qwen3-coder-7b` — 7B params): Next-generation code transformer in Ollama.
5. **Qwen 3 Reasoning (Ollama)** (`qwen3-reasoning-14b` — 14B params): Advanced multi-step reasoning model in Ollama.
6. **DeepSeek R1 / V3 (Ollama)** (`deepseek-r1-7b` — 7B params): Popular open-weights reasoning model. **[NEW]**
7. **IBM Granite 3.1 Dense** (`granite-3.1-dense-8b` — 8B params): Enterprise code and reasoning model. **[NEW]**
8. **GPT-4o Mini Baseline** (`gpt-4o-mini-baseline` — 8B params): Reference frontier baseline model. **[NEW]**
9. **Phi-4 Reasoning** (`phi-4-reasoning` — 14B params): Multi-step reasoning model for temporal memory evaluation.
10. **Ollama Standard** (`ollama-standard` — 7B params): Generalist Ollama bridge model.

---

## 3. Evaluated Datasets (10 Track Corpora)

| Track ID | Dataset ID | Dataset Name | Document Count | Raw Token Atoms |
| :--- | :--- | :--- | :--- | :--- |
| **Track 01** | `enterpriserag_bench` | EnterpriseRAG-Bench (Onyx) | 500,000 docs | 26,000,000 tokens |
| **Track 01** | `salesforce_herb` | Salesforce HERB Benchmark | 10,000 docs | 1,200,000 tokens |
| **Track 01** | `beam_benchmark` | BEAM Retrieval Benchmark | 5,000 docs | 600,000 tokens |
| **Track 01** | `finance_bench` | FinanceBench Financial QA | 2,500 docs | 350,000 tokens |
| **Track 02** | `hydradb_repo` | HydraDB OSS Repository | 1,250 files | 485,000 tokens |
| **Track 02** | `seedgraph_ledger` | SeedGraph Custody Ledger | 450 files | 180,000 tokens |
| **Track 02** | `daisytrain_logs` | DaisyTrain v0.3.7 Logs | 320 files | 140,000 tokens |
| **Track 02** | `inturn_transcripts` | Antigravity In-Turn Transcripts | 500 FCOs | 50,677 tokens |
| **Track 03** | `longmemeval_full500` | LongMemEval-S full500 | 500 cases | 1,200,000 tokens |
| **Track 03** | `longmemeval_v2` | LongMemEval-V2 Benchmark | 350 cases | 850,000 tokens |

---

## 4. Aggregate Matrix Performance & Receipts

- **Master Matrix Receipt**: [`eval/hosted_migration_20260820/daisy_train/EXTENDED_100_CELL_MATRIX_RECEIPT.json`](file:///Users/byron/projects/active/hydradg/eval/hosted_migration_20260820/daisy_train/EXTENDED_100_CELL_MATRIX_RECEIPT.json)
- **Total Aggregate Energy Saved**: **$3.48 \times 10^{18}$ FLOPs (~9,676.96 Watt-hours)**
- **Public Key Signature Verification**: **100.00% Cell Signature Coverage** (`SIGNED_WITH_AUTHOR_PUBLIC_KEY`)
- **Git Commit Hash**: `75cc7393`
