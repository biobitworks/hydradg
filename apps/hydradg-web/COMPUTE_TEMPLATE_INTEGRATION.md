# COMPUTE template integration

Design reference:

- v0 template: `COMPUTE - The Platform to Build & Ship AI Agents`
- author: `kerroudj`
- public template page: `https://v0.app/templates/compute-the-platform-to-build-ship-ai-agents-Auw4otwlr20`
- public preview: `https://v0-compute-11.vercel.app/`
- observed template update date: 2026-03-31

## Current integration state

`DESIGN_REFERENCE_CAPTURED / EXACT_V0_SOURCE_NOT_IMPORTED`

The connected Vercel project named `compute-the-platform-to-build` currently has no deployment. The Vercel project record therefore does not provide a deployed source tree that can be pulled into `apps/hydradg-web` through the current Vercel integration.

Do not describe the current HydraDG web app as an exact copy/fork of the COMPUTE template.

## Design mapping

The public COMPUTE preview uses a strong sequence that maps well to HydraDG:

1. large minimal hero
2. headline metrics
3. numbered capabilities
4. define/deploy/monitor process
5. infrastructure/state visualization
6. live metrics
7. integrations
8. security / auditability
9. developer surface
10. final action

HydraDG adaptation:

1. **Hero** — HydraDG: temporal graph memory with FCO/FCG custody
2. **Metrics** — current dataset, graph state, fixture Merkle checkpoint, claim boundary
3. **Capabilities** — Track 01 ontology / Track 03 memory / Best Use custody overlay
4. **Process** — source → graph → retrieve → perturb → classify → recover
5. **Infrastructure** — local pinned HydraDB + Ollarma + optional hosted HydraDB conformance
6. **Live metrics** — A/B/C/D retrieval, current-state traversal, FCG delta counts
7. **Integrations** — HydraDB, Hugging Face datasets, GitHub, Ollarma, Vercel
8. **Security** — local tokens stay local; hashes/signatures/claim ceilings are separate evidence layers
9. **Developer** — Judge Lab APIs, data pull scripts, reproducibility receipts
10. **Action** — run deterministic control, then live real-data golden path

## Exact-source import route

If the v0 workspace exposes **Add to Codebase**, use the generated v0/shadcn command from that authenticated workspace in `apps/hydradg-web`. Do not invent a project token or component ID.

Typical v0 route:

```bash
cd /Users/byron/projects/active/hydradg/apps/hydradg-web
npx v0@latest init
# Then use the exact Add-to-Codebase command produced by the authenticated v0 workspace.
```

Any exact template import should be a separate commit so the transformation from upstream template → HydraDG adaptation remains auditable.
