# Synthetic Multi-Model x Multi-Dataset Matrix Experimental Design

This document specifies HydraDG's **Synthetic Multi-Model x Multi-Dataset Matrix Experimental Design**, defining a 10-Model $\times$ 10-Dataset ($10 \times 10 = 100$ cell) evaluation design matrix.

> [!IMPORTANT]
> - **Claim Ceiling**: `SYNTHETIC_100_CELL_MULTI_MODEL_DATASET_MATRIX_DESIGN_ONLY_NOT_MODEL_EXECUTION`
> - **Execution Status**: This artifact represents an **experimental design matrix**. Cells are marked `NOT_EXECUTED_SYNTHETIC_DESIGN` and do **not** claim empirical model execution.
> - **Signature State**: `NOT_SIGNED`. The author identity FCO ID (`fco:303b3fab6fd8831b84a37f789aa4ef1f1ab78a808572eddf8632d1b88f97e1d5`) is incorporated into the cell SHA-256 digest string (`cell_digest_sha256`) as an identity anchor, not a digital signature.
> - **Energy Unit Math**: Aggregate theoretical FLOPs ($3.177 \times 10^{18}$ FLOPs) under an assumed hardware efficiency of $100 \text{ TFLOPS/W}$ evaluates to a theoretical energy equivalent of **$\approx 8.8261 \text{ Watt-hours}$** ($\text{Watt-seconds} / 3600$). Real energy measurement is marked `NOT_MEASURED`.

---

## 1. Evaluated Models (10 Model Design Rows)

1. **Vithia Baseline** (`hydradg-vithia-cfmo-v0.1` — 7B params): Vitalogy & FCO baseline model.
2. **Anticube Contradiction Classifier** (`hydradg-anticube-classifier` — 3B params): Edge classifier.
3. **Qwen 2.5 Coder 7B** (`qwen2.5-coder:7b` — 7B params): Code transformer in Ollama.
4. **Qwen 3 Coder 7B** (`qwen3-coder:7b` — 7B params): Next-gen code model in Ollama.
5. **Qwen 3 Reasoning 14B** (`qwen3-reasoning:14b` — 14B params): Multi-step reasoning model in Ollama.
6. **DeepSeek-R1-Distill-Qwen-7B** (`deepseek-r1:7b` — 7.62B params): Open-weights reasoning model in Ollama.
7. **IBM Granite 3.1 Dense 8B** (`granite3.1-dense:8b` — 8.17B params): Enterprise code & reasoning model.
8. **GPT-4o Mini Baseline** (`gpt-4o-mini` — `params_b = null`): Reference API model; parameter FLOPs reported as `NOT_APPLICABLE_PROVIDER_PARAMETERS_UNDISCLOSED`.
9. **Phi-4 Reasoning 14B** (`phi4:14b` — 14B params): Reasoning model in Ollama.
10. **Ollama Standard 7B** (`qwen2.5:7b` — 7B params): Generalist model tag in Ollama.

---

## 2. Declared Track Datasets (10 Dataset Design Columns)

- **Track 01**: EnterpriseRAG-Bench (500k docs), Salesforce HERB (10k docs), BEAM Benchmark (5k docs), FinanceBench (2.5k docs)
- **Track 02**: HydraDB OSS Repo (1,250 files), SeedGraph Custody Ledger (450 files), DaisyTrain Logs (320 files), Transcripts (500 FCOs)
- **Track 03**: LongMemEval-S full500 (500 cases), LongMemEval-V2 (350 cases)
- **Declared Total Document Count**: **520,870 Documents** (`DECLARED_CORPUS_ESTIMATE`)

---

## 3. Receipt & Custody Anchors

- **Master Matrix Design Receipt**: [`eval/hosted_migration_20260820/daisy_train/EXTENDED_100_CELL_MATRIX_RECEIPT.json`](file:///Users/byron/projects/active/hydradg/eval/hosted_migration_20260820/daisy_train/EXTENDED_100_CELL_MATRIX_RECEIPT.json)
- **Live Expanded Merkle Root**: `bb0adb5a6453a6493e51363f33e7782b3d79dd82b27ceb8678173ce53f1ce72b` (653 FCO Nodes / 1,692 FCG Edges)
- **Git Commit Hash**: `695805cb`
