# HydraDG Agent-Native Evidence Gateway — Preregistered Hackathon Plan & 20-Fixture Benchmark

**Submission Concept**: HydraDG Agent-Native Evidence Gateway  
**Fallback Concept**: Custody Operations Fleet  
**Branch**: `hack-hydra/agent-native-builders-20260826`  
**Scientific Base SHA**: `4b3066e7700334f646a757b2e5197522d7921da3`  
**Execution Host**: `magicSTUDIObox.local`  

---

## 1. Overview & Golden Path

The **HydraDG Agent-Native Evidence Gateway** provides an agentic runtime boundary that governs tool interactions, query retrieval, external evidence proposal, and claim ceilings.

### The Four-Tool Golden Path (MVP Surface)
1. `discover_capabilities`: Query supported host models, ontologies, and claim ceilings.
2. `query_evidence`: Perform typed graph / context-aware evidence retrieval.
3. `propose_external_evidence`: Submit external evidence candidates under strict quarantine and hash binding.
4. `verify_custody_receipt`: Verify cryptographic custody handoff receipts and claim ceilings.

### Bounded Agent Roles
1. `evidence scout`: Discovers and retrieves evidence candidates.
2. `provenance curator`: Validates source line-of-custody and pointer integrity.
3. `claim auditor`: Verifies claim ceilings and isolates evaluation-only fields.
4. `receipt verifier`: Audits FCO/FCG handoff receipts.

---

## 2. Experimental Comparison: CONTROL vs. TREATMENT

- **CONTROL**: Protocol-only / ordinary un-governed agent surface (flat text retrieval, no claim ceiling enforcement, no disclosure boundaries).
- **TREATMENT**: Protocol + HydraDG evidence/claim custody (typed graph retrieval, strict claim ceilings, unauthorized disclosure quarantine, custody receipts).

---

## 3. Preregistered 20-Fixture Suite

The 20 frozen fixtures evaluate:
- Positive graph matches (ANB-FIX-001, 002, 012, 015)
- Contradictory evidence (ANB-FIX-003)
- Null / out-of-corpus queries (ANB-FIX-004, 014, 016)
- Unauthorized disclosure prevention (ANB-FIX-005, 013)
- Abstention preservation (ANB-FIX-006)
- Stratum classification (ANB-FIX-007)
- External evidence quarantine (ANB-FIX-008, 009)
- Custody failure / bad pointer (ANB-FIX-010)
- Governance ceiling violation prevention (ANB-FIX-011)
- Schema failure / error handling (ANB-FIX-017)
- FCG Merkle/MMR state verification (ANB-FIX-018)
- Handoff receipt validation (ANB-FIX-019)
- Resource timeout / budget boundary (ANB-FIX-020)

---

## 4. Preregistered Acceptance Gates (20/20 Target)

- `EVIDENCE_CLASS_CORRECT = 20/20`
- `CLAIM_CEILING_CORRECT = 20/20`
- `NULL_CONTRADICTION_PRESERVED = 20/20`
- `UNAUTHORIZED_PLAINTEXT_DISCLOSURE = 0/20`
- `RECEIPT_HASH_VERIFICATION = 20/20`
