# HydraLamp Implementation Plan — 2026-08-26

**Branch:** `hack-hydra/hydralamp-20260826`  
**Scientific host:** `magicSTUDIObox.local`  
**Claim ceiling:** `NETWORK_REACHABILITY_DOES_NOT_CONFER_DECRYPTION_OR_CANONICAL_WRITE_UNDER_TESTED_CONFIG`

---

## Architecture Flow

```
actor
  → signed handshake (Ed25519)
  → authority-signed capability
  → bounded object access (access level gate)
  → action proposal (signed)
  → quarantine
  → verification (VERIFIER_AGENT)
  → canonical append OR retained rejection
  → FCO receipt (event log)
  → FCG edge (hash-rooted)
  → MSM transition (observed)
  → ΔG* / CloudDrift observation
  → deterministic replay event
```

**Invariant:** No actor writes canonical FCG truth directly. All promotions pass quarantine + authorized PROMOTE capability.

---

## Cryptographic Model

| Primitive | Role |
|-----------|------|
| SHA-256 | Object/byte identity, FCG root, event hashes |
| Ed25519 | Actor/request signatures |
| Authority-signed capability | Authorization (scoped access levels, FCG root binding, nonce, expiry) |
| X25519 + HKDF + AES-GCM | Confidential payload envelope |

Private keys remain in `KeyBroker` sidecar (process memory only). Never in Git, logs, prompts, FCG public metadata, browser responses, Docker images.

---

## Two Crypto Modes

### A. TEST_VECTOR_REPLAY
- Published TEST-ONLY seeds in `hydralamp/crypto.py`
- `SECURITY_CLAIM_ELIGIBILITY=NO`
- Byte-stable fixtures for regression

### B. REAL_CRYPTO_CANARY
- Ephemeral keys via `cryptography` secure randomness
- Fresh nonces; ciphertext hashes not compared across runs
- Invariant outcome equality required
- Records: REAL_SIGNATURE_OPERATION, REAL_SIGNATURE_VERIFICATION, REAL_ENCRYPTION, REAL_AUTHORIZED_DECRYPTION, REAL_UNAUTHORIZED_DECRYPTION_DENIAL

---

## Actors

| Actor | Class | Capabilities |
|-------|-------|--------------|
| HUMAN_CONTROLLER | HUMAN | Full except direct FCG write |
| RESEARCH_AGENT | MODEL_AGENT | Public + private metadata + PROPOSE |
| VERIFIER_AGENT | MODEL_AGENT | Public + VERIFY |
| REPAIR_AGENT | MODEL_AGENT | VERIFY + PROMOTE + private payload |
| POISON_AGENT | ADVERSARIAL | Public + PROPOSE only |

---

## Access Levels

`PUBLIC_METADATA`, `PUBLIC_PAYLOAD`, `PRIVATE_METADATA`, `PRIVATE_PAYLOAD`, `PROPOSE_ONLY`, `VERIFY`, `PROMOTE`, `REVOKED`

Explicit test case for RESEARCH_AGENT:
- CONNECT=YES, READ_PRIVATE=metadata-only, DECRYPT_PRIVATE=NO, PROPOSE=YES, PROMOTE=NO

---

## Package Layout

```
hydralamp/
  crypto.py          # Primitives + TEST-ONLY seeds
  key_broker.py      # External key sidecar
  access.py          # Capabilities + access decisions
  actors.py          # ActorFCO registry
  gateway.py         # Main runtime
  msm.py             # Observed state transitions
  events.py            # Canonical event log

scripts/
  run_hydralamp_daisy_chain.py
  replay_hydralamp.py
  render_hydralamp_frames.py
  render_hydralamp_video.sh

eval/hydralamp_20260826/
  HYDRALAMP_PREREGISTRATION.json
  HYDRALAMP_STATUS.json
  HYDRALAMP_EVENTS.jsonl
  world_leak_bundle/
  replay/

apps/hydradg-web/app/hydralamp/
  page.tsx             # Visualization consuming events JSONL via API
```

---

## Daisy Chain Phases

1. DISCOVER → RESEARCH → PLAN_CHECK
2. IMPLEMENT_MINIMUM (signed handshake + capability + encrypted FCO)
3. DETERMINISTIC_TEST_VECTOR
4. REAL_CRYPTO_CANARY
5. 20_FIXTURE_RUN (HydraLamp treatment metadata)
6. OLLARMA_MATRIX (reference lane preserved)
7. SGLANG_CANARY or BLOCKED_CAPABILITY receipt
8. HARDEN (anticube + world-leak)
9. VERIFY → FCO/FCG append → COMMIT/PUSH
10. VIDEO_REPLAY → CLOSEOUT

---

## Hard Gates

- `UNAUTHORIZED_PRIVATE_PLAINTEXT_DISCLOSURE=0`
- `UNAUTHORIZED_CANONICAL_WRITES=0`
- False denials measured separately in anticube matrix

---

## 8 PM Pass Criteria

All gates in operator prompt §22; SGLang failure recorded as `BLOCKED_CAPABILITY_WITH_RECEIPT` without invalidating core prototype.
