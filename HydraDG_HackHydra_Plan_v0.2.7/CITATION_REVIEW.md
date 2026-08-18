# Citation / related-work review

Primary or near-primary sources used for planning:

1. LongMemEval official repository — benchmark definitions, data schema, evaluation harness, MIT license.
2. LongMemEval-V2 official repository — agentic long-term memory, 451 questions, up to 115M tokens, accuracy/latency evaluation, Apache-2.0.
3. HydraDB official research/blog — versioned bitemporal graph and reported LongMemEval-S results.
4. SodaMem arXiv — evidence-grounded temporal graph memory with provenance and supersession/contradiction/update relations.
5. MAP-Graph arXiv — provenance-aware shared memory with access/trust/action gating.
6. RepDL arXiv + Microsoft repository — bit-level reproducible deep learning.
7. NVIDIA Megatron Core docs — rerun state machine and same-/different-GPU diagnostic logic.
8. FLARE / USENIX NSDI 2026 — divergent LLM-training diagnostics.
9. HHS OCR — HIPAA de-identification and cloud/ePHI guidance.

## Review rule
Company-reported benchmark scores (HydraDB, Mem0, Zep, etc.) are treated as externally attested unless independently rerun under our harness. Cross-system scores should not be merged into one table unless judge, reader, dataset version, retrieval budget and cost accounting are aligned.
