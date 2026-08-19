# HydraDG website MVP + fallback design — 2026-08-19

## Public information architecture

Primary navigation:

```text
Overview | Demo | Results | Experiments | Try the demo
                                ↓
                            Deep dive
                       Graph / Knowledge / Eligibility
```

The public narrative is deliberately progressive:

1. **Problem** — see what changed, trace why, test the repair.
2. **Golden path** — reference → poison → antidote.
3. **Executed result** — show the completed LongMemEval full500 outcome, including the absence of a positive retrieval signal.
4. **Experiments** — Track 01 identity, Track 02 blast radius, Track 03 memory.
5. **Deep dive** — FCO/FCG, hashes, SeedGraph, HydraDB relations, evidence receipts and claim ceilings.

## Iceberg model

The UI uses an iceberg / hot-to-cold metaphor for depth of information:

```text
TIP / HOT
current answer
recent state
live explanation

WATERLINE / WARM
experiment
relationships
first divergence
recovery

DEEP / COLD
source hashes
record FCOs
FCG dependency routes
SeedGraph custody
HydraDB retained state
receipts
negative/null history
```

This is a UI metaphor, not a thermodynamic measurement.

If `ΔG*` is shown, it must be labelled as an application-defined information-state metric. It must not be described as physical Gibbs free energy or use thermodynamic units unless a separate physical derivation and evidence support that claim.

## Knowledge-link rule

Every project-specific or plausibly unfamiliar term should be linkable to the backend knowledge layer.

Target interaction:

```text
term
 ↓
knowledge definition
 ↓
FCO identity
 ↓
FCG neighbors / dependency route
 ↓
source/version or execution receipt
 ↓
claim ceiling
```

Examples include:

- FCO
- FCG
- SeedGraph
- HydraDB
- Seed of Truth
- Anticube
- SUPERSEDED_BY
- CONTRADICTS
- current state
- perturbation
- antidote
- `ΔG*`
- evidence class
- claim ceiling
- Merkle checkpoint
- LongMemEval
- EnterpriseRAG-Bench
- HERB
- BEAM
- HydraOntology
- HydraBlast
- HydraMemory

A term-coverage audit should fail the public release if a project-specific term appears in core explanatory copy without either a knowledge entry or a deliberate exemption for ordinary/common language.

## Live artifact

The preferred surface is the current Next.js application deployed to Vercel.

At this documentation point, the connected Vercel project still reports a production deployment from the older `hack-hydra/webapp-mvp-20260818` branch. Therefore the current release candidate is not yet the public production artifact.

## Backup artifact

A self-contained static fallback is stored at:

```text
apps/hydradg-web/public/backup/hydradg.html
```

It contains:

- the simple HydraDG value proposition;
- reference → poison → antidote;
- the completed full500 negative/neutral result;
- the iceberg progressive-disclosure model;
- Track 01/02/03 descriptions;
- executed Track 03 hashes and claim boundaries.

It has no backend dependency and can be:

- opened directly from disk;
- served from the Next.js public directory;
- attached to a fresh public GitHub release;
- hosted on a static service if the Vercel release remains blocked.

The fallback must never label local-only controls as live.

## Video fallback

If the live release cannot be promoted before recording, the video may use:

1. static fallback for the public story;
2. local Judge Lab for the actually running HydraDB perturbation path;
3. Results/Evidence or terminal receipts for executed evidence;
4. public repository for source and reproducibility instructions.

The video should clearly distinguish the local execution environment from the static/public presentation artifact.

## Release gates

```text
LOCAL_RELEASE_EXECUTION_GREEN
→ PUBLIC_EXPORT_GREEN
→ LIVE_VERCEL_GREEN OR STATIC_FALLBACK_GREEN
→ VIDEO_RECORDED
→ PUBLIC_LINK_AUDIT_GREEN
→ READY_TO_SUBMIT
```

A Vercel outage or connector limitation changes the delivery route, not the experimental result or FCO/FCG claim ceiling.
