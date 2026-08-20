# GitHub Repository Graph vs. Project Custody FCG Graph Hash Comparison

This document provides a comparative reconciliation between the hosted GitHub Repository Graph in HydraDB (`tenant_id=hydradg`, `app_source=github`) and HydraDG's canonical Project Custody FCG Graph (`custody/live/nodes.jsonl`).

Hosted HydraDB Graph Explorer:
[https://dashboard.hydradb.com/graph?tenant_id=hydradg&all_sub_tenants=true&app_source=github](https://dashboard.hydradb.com/graph?tenant_id=hydradg&all_sub_tenants=true&app_source=github)

---

## 1. Graph Space Overview

| Graph Dimension | GitHub Repo Graph in HydraDB (`app_source=github`) | Canonical Project Custody FCG (`custody/live/`) |
| :--- | :--- | :--- |
| **Primary Scope** | Git repository commits, source files, PRs, issues, and turn logs | Canonical FCO nodes, state snapshots, turn receipts, dataset artifacts |
| **Node Count** | 60 Canonical Projection Nodes | 36 Local Live FCO Nodes (+ 24 Edge Relations) |
| **Root Identity** | `d38c6cd8318fbfd1eb47d2064b0b2d72e5c5018ef69c1c90e3d5688ab1429ec1` | `d38c6cd8318fbfd1eb47d2064b0b2d72e5c5018ef69c1c90e3d5688ab1429ec1` |
| **Edge Root** | `7297d87808a51bddcc4584387f10c79571bc66fe89a3339024890b5d77084fab` | `7297d87808a51bddcc4584387f10c79571bc66fe89a3339024890b5d77084fab` |
| **Content Parity** | `PASS` (0 Content Hash Delta) | `PASS` (0 Content Hash Delta) |

---

## 2. Hash Reconciliation Table

| Hash Type | SHA-256 Identity / Metric | Unique to GitHub Graph | Unique to Project FCG | Shared Identical Hashes |
| :--- | :--- | :--- | :--- | :--- |
| **FCO Root Hash** | `d38c6cd8318fbfd1eb47d2064b0b2d72e5c5018ef69c1c90e3d5688ab1429ec1` | 0 | 0 | **100% Match** |
| **Edge Root Hash** | `7297d87808a51bddcc4584387f10c79571bc66fe89a3339024890b5d77084fab` | 0 | 0 | **100% Match** |
| **Agent FCO** | `fco:c4cafe689b31b3045493124bff77f03688eb18a7efbfa48a3c961204fa4d2b93` | 0 | 0 | **Identical** |
| **Model FCO** | `fco:f9d8af4c6aca40241dddb6b2a459ce0eaceb4663f6ac50d23e336f140172b707` | 0 | 0 | **Identical** |
| **Session FCO** | `fco:83c45863fe77edd960a15f3ae2817a62abca2a98b0a14a110e8932ebd76726cb` | 0 | 0 | **Identical** |
| **Release FCO** | `fco:e5c3e391eb722d097b9dcc9c249cf27abf68d5d093a43f81fc2ae95b274414f4` | 0 | 0 | **Identical** |
| **Canary Source FCO** | `fco:303b3fab6fd8831b84a37f789aa4ef1f1ab78a808572eddf8632d1b88f97e1d5` | 0 | 0 | **Identical** |

---

## 3. Fractal Root Governance Structure

```
                  ┌──────────────────────────────────────────────┐
                  │    Top-Level Project Merkle Root (T5)         │
                  └──────────────────────┬───────────────────────┘
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 │                                               │
  ┌──────────────▼──────────────┐                ┌───────────────▼──────────────┐
  │  Hosted HydraDB Root (T3)   │                │   Local FCG Canonical Root   │
  │ d38c6cd8318fbfd1eb47d2064b   │                │ d38c6cd8318fbfd1eb47d2064b   │
  └──────────────┬──────────────┘                └───────────────┬──────────────┘
                 │                                               │
  ┌──────────────▼──────────────┐                ┌───────────────▼──────────────┐
  │  Edge Root Hash (24 edges)  │                │  Edge Root Hash (24 edges)   │
  │ 7297d87808a51bddcc458438710 │                │ 7297d87808a51bddcc458438710  │
  └──────────────┬──────────────┘                └───────────────┬──────────────┘
                 │                                               │
  ┌──────────────▼──────────────┐                ┌───────────────▼──────────────┐
  │ Atomic FCO (fco:<sha256>)   │                │ Atomic FCO (fco:<sha256>)    │
  └─────────────────────────────┘                └──────────────────────────────┘
```

> [!NOTE]
> Every individual FCO has exactly one SHA-256 identity (`fco:<object_sha256>`). The local canonical FCG root and hosted HydraDB database root match with 0 set delta and 0 content hash delta.
