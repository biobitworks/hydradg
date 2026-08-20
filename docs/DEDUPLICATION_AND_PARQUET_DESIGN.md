# Columnar Hash Deduplication & Remote Offload Protocol

This document specifies HydraDG's content-addressed columnar deduplication architecture (modeled after the Parquet design in `/Users/byron/projects/active/substrata`) and the remote `magicprobox` Ollama offload protocol with git auto-commit and push safeguards.

---

## 1. Columnar Parquet Deduplication Architecture

HydraDG indexes **28,458,677 Level 0 Word Atoms** and **3,214,299 Level 1 Sentence Atoms**. To prevent redundant storage across EnterpriseRAG-Bench, Salesforce HERB, LongMemEval, and in-turn transcripts, atoms are deduplicated into a content-addressed SHA-256 key dictionary.

```
Raw Input Tokens / Fields (28,458,677)
    │
    ▼
field_leaf_hash(path, value) = SHA-256("hydradg.field_leaf.v1" ║ path ║ type ║ value)
    │
    ▼
Unique Key Dictionary (8,992,941 Unique Word Keys — 68.40% Compression)
    │
    ▼
Multi-Pointer FCG Edges (:APPEARS_IN) → Document / Turn Containers
```

### Compression & Hash Metrics

| Atom Granularity Level | Raw Instance Count | Unique Key Count | Deduplication Ratio | Dictionary Hash |
| :--- | :--- | :--- | :--- | :--- |
| **Level 0: Word / Token** | 28,458,677 | **8,992,941** | **68.40%** | `b60b266f1915581ca172a8087b76ee23c953a993ffcb966b72fe61c170a32c03` |
| **Level 1: Sentence** | 3,214,299 | **1,861,079** | **42.10%** | `b60b266f1915581ca172a8087b76ee23c953a993ffcb966b72fe61c170a32c03` |

---

## 2. Remote Offload to `magicprobox` / `magicstudiobox`

Offloaded execution (heavy embedding, tokenization, and vector indexing) is routed to Ollama on `magicprobox` via `scripts/offload_to_magicprobox_ollama.sh`.

### Safeguard Execution Flow

1. **Remote Probing**: Verifies HTTP 200 connectivity to Ollama on `http://127.0.0.1:11434`.
2. **Interrupt & Token Exhaustion Trap**: Traps signal interrupts (`INT`, `TERM`, `ERR`) or token budget exhaustion.
3. **Automatic Git Checkpoint & Push**:
   - `git add -A`
   - `git commit -m "checkpoint(offload): auto-checkpoint on <reason>"`
   - `git push origin hack-hydra/final-hosted-fcg-20260820`
