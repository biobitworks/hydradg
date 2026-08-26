# HydraLamp Research — 2026-08-26

**Branch:** `hack-hydra/hydralamp-20260826`  
**Retrieval window:** 2026-08-26 (America/Los_Angeles)  
**Evidence classification:** OFFICIAL_DOCUMENTATION_PRIMARY  

---

## 1. SGLang Breakable CUDA Graph

| Topic | Finding | Source | Retrieved |
|-------|---------|--------|-----------|
| `SGLANG_USE_BREAKABLE_CUDA_GRAPH` | Env var `=1` enables breakable CUDA graph without full debug mode; required for `@eager_on_graph` | https://docs.sglang.io/advanced_features/breakable_cuda_graph.html | 2026-08-26 |
| `@eager_on_graph` | Decorator marks functions to run eagerly between captured graph segments during decode | https://docs.sglang.io/advanced_features/breakable_cuda_graph.html | 2026-08-26 |
| `break_graph()` | Bare graph break insertion point via `@eager_on_graph(True)` wrapper | https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/model_executor/runner_backend_utils/breakable_cuda_graph/breakable_cuda_graph.py | 2026-08-26 |
| `--debug-cuda-graph` | Wraps entire decode forward in graph break; all ops eager through capture/replay path | https://docs.sglang.io/advanced_features/breakable_cuda_graph.html | 2026-08-26 |
| Performance | BCG preserves most CUDA graph benefit; overhead minimal if no breaks inserted (PR #19102) | https://www.lmsys.org/blog/2026-08-17-advanced-cuda-graph/ | 2026-08-26 |
| Hardware | CUDA and ROCm/HIP supported; NPU/CPU/MPS/XPU unsupported (debug auto-disabled) | https://docs.sglang.io/advanced_features/breakable_cuda_graph.html | 2026-08-26 |
| Deterministic inference | Not guaranteed by BCG; graph breaks introduce eager segments that may vary timing | EVIDENCE_LEVEL: INFERENCE_FROM_DOCS | 2026-08-26 |
| Observability | `--debug-cuda-graph` provides debugging boundary; benchmark via server metrics/TTFT/ITL | https://github.com/sgl-project/sglang/pull/19102 | 2026-08-26 |

**HydraLamp note:** Graph breaking is an audit probe only — not an authorization mechanism. Selective audit emits trace ID, actor ID hash, request hash, model/runtime ID, policy root, FCG root, segment ID only.

---

## 2. Qwen Model Family (SGLang-compatible)

| Tier | Model ID | Notes | Source | Retrieved |
|------|----------|-------|--------|-----------|
| TINY | `Qwen/Qwen2.5-1.5B-Instruct` | Smallest common Qwen instruct | https://github.com/QwenLM/Qwen3 | 2026-08-26 |
| SMALL | `Qwen/Qwen3-8B` | SGLang launch example; `--reasoning-parser qwen3` | https://github.com/QwenLM/Qwen3/blob/main/docs/source/deployment/sglang.md | 2026-08-26 |
| MEDIUM | `Qwen/Qwen3-30B-A3B-Instruct-2507` | MoE instruct variant | https://github.com/QwenLM/Qwen3 | 2026-08-26 |
| LARGE | `Qwen/Qwen3.8-27B` (conceptual) | Qwen3.8 family referenced in operator ladder; verify digest at pull time | EVIDENCE_LEVEL: OPERATOR_PREREG | 2026-08-26 |

**Requirement:** `sglang>=0.4.6.post1` per Qwen deployment docs.

---

## 3. Mistral / Ministral 3 Family

| Model | HuggingFace ID | Variant | Source | Retrieved |
|-------|----------------|---------|--------|-----------|
| Ministral 3 3B | `mistralai/Ministral-3-3B-Instruct-2512` | Instruct | https://docs.sglang.io/cookbook/autoregressive/Mistral/Ministral-3 | 2026-08-26 |
| Ministral 3 8B | `mistralai/Ministral-3-8B-Instruct-2512` | Instruct | https://docs.sglang.io/cookbook/autoregressive/Mistral/Ministral-3 | 2026-08-26 |
| Ministral 3 14B | `mistralai/Ministral-3-14B-Instruct-2512` | Instruct | https://docs.sglang.io/cookbook/autoregressive/Mistral/Ministral-3 | 2026-08-26 |

**Compatibility caveat:** Ministral3 requires pinned transformers/cudnn versions; KeyError `ministral3` reported with version skew (issue #18819, PR #14251). Text-only variants recommended for stability.

---

## 4. Cloudflare Workers Web Crypto

| Primitive | Supported | Public-only verifier feasible | Source | Retrieved |
|-----------|-----------|--------------------------------|--------|-----------|
| Ed25519 verify | Yes (`Ed25519`, legacy `NODE-ED25519`) | Yes — verify with public key only | https://developers.cloudflare.com/workers/runtime-apis/web-crypto/ | 2026-08-26 |
| X25519 ECDH | Yes (`deriveBits`/`deriveKey`) | Yes for shared secret derivation | https://developers.cloudflare.com/workers/runtime-apis/web-crypto/ | 2026-08-26 |
| AES-GCM | Yes | Yes with derived key | https://developers.cloudflare.com/workers/runtime-apis/web-crypto/ | 2026-08-26 |
| HKDF | Yes | Yes for key derivation | https://developers.cloudflare.com/workers/runtime-apis/web-crypto/ | 2026-08-26 |
| SHA-256 | Yes (`digest`) | Yes | https://developers.cloudflare.com/workers/runtime-apis/web-crypto/ | 2026-08-26 |

**HydraLamp note:** Cloudflare account auth is NOT required for prototype crypto verification. A public verifier worker can hold only public keys and capability schemas.

---

## 5. Existing HydraDG Surfaces

| Component | Location | HydraLamp reuse |
|-----------|----------|-----------------|
| FCO identity | `apps/hydradg-web/lib/fco.ts` | Content-addressed FCO nodes |
| FCG metrics (G*, ΔG*) | `apps/hydradg-web/lib/fcg4d.ts` | Information-state diagnostics |
| CloudDrift | `apps/hydradg-web/lib/contextIceberg.ts` | JSD-based drift |
| Agent-native 20 fixtures | `eval/agent_native_builders_20260826/` | Frozen manifest, HydraLamp treatment wrapper |
| Handoff schema | `schemas/agent_model_handoff_receipt.schema.json` | Custody receipts |
| Live FCG | `custody/graph/live/` | Public graph snapshot for world-leak bundle |
| Ollarma bridge | `scripts/ollama_bridge_watcher.py`, external Ollarma repo | Bounded model message exchange |
| MSM bridge schema | `HydraDG_DaisyTrain_v0.3.7/seedgraph/bridge_schema.json` | SeedGraph interchange |
| Deterministic rendering | `scripts/video_ready_gate.sh`, judge demo | Replay frame pipeline |

**Unresolved authority files (not in checkout):** `FCO_SCHEMA.json`, `FCG_SCHEMA.json`, `SIGNING_AND_KEYS.md` — recorded as `DEPENDENCY_UNRESOLVED`.

---

## Evidence Classification Summary

- **OFFICIAL_DOCUMENTATION:** SGLang, Cloudflare, Qwen, Ministral docs
- **OPERATOR_PREREG:** Model ladder exact digests frozen at execution time
- **INFERENCE_FROM_DOCS:** Performance/determinism claims bounded to documented behavior
- **DEPENDENCY_UNRESOLVED:** Missing canonical schema files in this checkout

Research did not silently change experiment variables.
