# PUBLIC_RELEASE_READINESS.md — Antigravity & Hack Hydra Public Release Audit

Version: 1.0 | Status: DRAFT_READY_FOR_VERIFICATION

## Executive Summary
This document defines the release readiness checks for publishing the HydraDG / Hack Hydra public repository and Vercel web application. All scientific claims are grounded in local, tamper-evident computational receipts.

---

## 1. Governance & Provenance Checklist

| Item | Requirement | Status | Evidence / Reference |
|------|-------------|--------|----------------------|
| **Dataset Freeze** | LongMemEval full500 raw source SHA-256 verified (`d6f21ea9...`) | PASS | `RAW_FREEZE_MANIFEST.json` |
| **Pre-Registration** | 2×2 matrix pre-registered with null hypotheses & stopping rules | PASS | `PRE_REGISTRATION_K5_K10_RAW_SEEDGRAPH.json` |
| **SeedGraph Intake** | Governed intake & FCO/FCG materialization complete | PASS | `SEEDGRAPH_TRANSFORM_MANIFEST.json` |
| **2×2 Matrix Execution** | RAW vs SeedGraph under K=5 and K=10 (R1, R2, R3) | IN_PROGRESS | `task-317` running locally |
| **Deterministic Equality** | Canonical payload hash equality gate $H_{0,\text{rep}}$ | PENDING_MATRIX | Matrix output analyzer |
| **Claim Ceilings** | Enforced claim ceilings on all receipts (`RETRIEVAL_SCORED_ABLATION_ONLY`) | PASS | Matrix runner receipts |

---

## 2. Public Export & Link Audit Policy

- [ ] **Secrets & Private Paths Sweep**: Inspect export artifacts for internal paths, credentials, or un-hashed tokens.
- [ ] **Internal Link Auditor**: Run link auditor over website-as-FCG to ensure all external links point to valid public resources.
- [ ] **Website-as-FCG References**: Ensure Next.js app (`apps/hydradg-web`) serves exact FCO/FCG receipt hashes and claim ceilings.

---

## 3. Human Checklist

- [ ] Record and attach video walk-through (`VIDEO_TODO.md`).
- [ ] Fill and submit official Hackathon submission form (`SUBMISSION_FORM_TODO.md`).
