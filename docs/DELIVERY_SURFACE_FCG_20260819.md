# Delivery surface FCG — 2026-08-19

Conceptual delivery graph:

```text
ReleaseCandidate
├── LIVE_DEPLOYMENT → VercelArtifact
└── STATIC_EXPORT → StaticFallbackArtifact

ExecutionEvidence
└── PRESENTED_BY → both delivery artifacts
```

The live and static surfaces are presentation siblings. Neither may overwrite the source evidence state.
