# Columnar Hash Deduplication & Spatiotemporal Pointer Protocol

This document specifies HydraDG's content-addressed columnar deduplication architecture (modeled after the Parquet design in `/Users/byron/projects/active/substrata`) and the **Spatiotemporal Pointer Protocol (`SpatiotemporalPointerFCO`)**.

---

## 1. Spatiotemporal Pointer Architecture

When two or more atoms or text fragments across EnterpriseRAG-Bench, Salesforce HERB, LongMemEval, or in-turn conversation logs produce the **exact same content hash (`content_sha256`)**:
1. **Deduplicated Content Atom**: The underlying payload is stored exactly once as a canonical `KnowledgeAtom` FCO.
2. **Spatiotemporal Pointer Nodes (`SpatiotemporalPointerFCO`)**: Every occurrence of that atom in different spatial locations (file path, dataset slug, 4D graph coordinates $x, y, z$) and temporal locations (timestamp, turn index, evaluation timepoint $t$) creates an explicit `SpatiotemporalPointerFCO`.

```
                  ┌─────────────────────────────────────────────────────────┐
                  │ Unique Canonical KnowledgeAtom (content_sha256)        │
                  └────────────────────────────┬────────────────────────────┘
                                               │
             ┌─────────────────────────────────┼─────────────────────────────────┐
             │ :LOCATED_AT                     │ :LOCATED_AT                     │ :LOCATED_AT
             ▼                                 ▼                                 ▼
┌─────────────────────────┐       ┌─────────────────────────┐       ┌─────────────────────────┐
│ SpatiotemporalPointer 1 │       │ SpatiotemporalPointer 2 │       │ SpatiotemporalPointer 3 │
│ Path: slack/channel_04  │       │ Path: docs/spec.md      │       │ Path: turn_42_transcript│
│ Space: (12.4, -4.2, 8.1)│       │ Space: (-3.1, 1.5, 0.0) │       │ Space: (0.0, 0.0, 2.5)  │
│ Time: t=0, 12:00:00Z    │       │ Time: t=1, 12:05:00Z    │       │ Time: t=2, 12:10:00Z    │
└─────────────────────────┘       └─────────────────────────┘       └─────────────────────────┘
```

---

## 2. Spatiotemporal Pointer Schema (`SpatiotemporalPointerFCO`)

```json
{
  "type": "SpatiotemporalPointerFCO",
  "id": "fco:c6877b8bcfe785803787264dfa18dbf8d2e368b6a3f3aa5ff80c5fd115dad713",
  "object_sha256": "c6877b8bcfe785803787264dfa18dbf8d2e368b6a3f3aa5ff80c5fd115dad713",
  "payload": {
    "content_sha256": "b60b266f1915581ca172a8087b76ee23c953a993ffcb966b72fe61c170a32c03",
    "spatial_location": {
      "dataset_id": "hydradg-track01-enterpriserag",
      "file_path": "slack/engineering/channel_04.json",
      "x": 12.4,
      "y": -4.2,
      "z": 8.1
    },
    "temporal_location": {
      "timepoint_t": 2.0,
      "timestamp_iso": "2026-08-20T12:00:00Z"
    },
    "fcg_relation": "LOCATED_AT_SPATIOTEMPORAL_POINTER",
    "license": "CC-BY-NC-ND-4.0"
  }
}
```

---

## 3. Storage Efficiency & Traceability

| Atom Level | Raw Occurrences | Unique Keys | Spatiotemporal Pointers | Traceability |
| :--- | :--- | :--- | :--- | :--- |
| **Level 0: Word / Token** | 28,458,677 | **8,992,941** | **19,465,736 Pointers** | **100.00% Exact** |
| **Level 1: Sentence** | 3,214,299 | **1,861,079** | **1,353,220 Pointers** | **100.00% Exact** |
| **Total Graph Scale** | **31,672,976** | **10,854,020** | **20,818,956 Pointers** | **Zero Loss of Spatial/Temporal Provenance** |
