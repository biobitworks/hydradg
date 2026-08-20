# Figure — HydraDG as a Regenerative Hydra

This is a **conceptual text figure** for HydraDG. It uses the anatomy and regenerative behavior of the freshwater *Hydra* polyp as a visual metaphor for persistent governed memory.

Biological inspiration: *Hydra* has a tubular body attached by a basal disc, a mouth/hypostome surrounded by tentacles, can reproduce by lateral budding, and is well known for regeneration. Reports of negligible/non-senescence motivate the persistence metaphor, but this figure does **not** claim that every *Hydra* species or individual is literally immortal under every condition.

```text
                         HYDRADG — THE REGENERATIVE HYDRA
                    persistent state through governed renewal

                                      CONTEXT / TIME →

          evidence        memory        provenance       contradiction
              \              |              |               /
               \        \    |    /         |        /     /
                \        \   |   /          |       /     /
                 \        \  |  /           |      /     /
                  \        \ | /            |     /     /
                   \        \|/             |    /     /
                    \    .--( )--.           |   /     /
                     \  /   MOUTH \          |  /     /
                      \/  / HYPOSTOME\________|_/     /
                      /\      │      /\             /
                     /  \_____│_____/  \___________/
                            CURRENT
                             STATE
                               │
                               │
                         ╭─────┴─────╮
                         │           │
                         │   BODY    │
                         │  COLUMN   │
                         │           │
      SENESCENCE /       │ persistent│        MAINTENANCE
      CONTEXT DRIFT ───► │ identity  │ ◄────  reference basin
      ΔG* > 0            │ + custody │        ΔG* ≈ 0
      Cloud Drift ↑      │           │
                         │           │
                         │       o───┼──────╮
                         │      /    │      │
                         │     /     │      │
                         │    ( BUD  )      │
                         │     \     /       │  REJUVENATION
                         │      \___/        │  repair / successor
                         │        │          │  ΔG* < 0 relative
                         │        └──────────┘  to damaged state
                         │
                         │
                         ╰─────┬─────╯
                               │
                         ______│______
                        /             \
                       /  BASAL DISC   \
                      /_________________\
                         CUSTODY ROOT
                    source / version / SHA


           REFERENCE ──► POISON / DIVERGENCE ──► ANTIDOTE / REPAIR
                ▲                                         │
                │                                         │
                └────────────── PERSISTENCE ◄─────────────┘

                 old state is retained; repair does not erase history
```

## How to read the animal

| Hydra anatomy / behavior | HydraDG metaphor |
|---|---|
| Tentacles | Multiple evidence, memory, provenance, and contradiction paths queried through the graph |
| Mouth / hypostome | Current working context where retrieved evidence is assembled |
| Body column | Persistent identity maintained across changing states |
| Continuous cell renewal | Ongoing maintenance of governed context rather than a frozen state |
| Lateral bud | Rejuvenated/successor state derived from prior custody rather than replacing its history |
| Regeneration after injury | Reference → perturbation/poison → traced divergence → repair/antidote |
| Basal disc | Source/version/custody root that anchors the visible state |
| Apparent negligible senescence in some studies | Inspiration for a persistent regenerative attractor; **not** a literal immortality claim for HydraDG or biology |

## State interpretation

The conceptual cycle is:

```text
SENESCENCE / DRIFT
        │
        │ detect earliest divergent dependency
        ▼
MAINTENANCE / CUSTODY
        │
        │ governed repair
        ▼
REJUVENATION
        │
        │ restored current state; prior state retained
        └──────────────────────────────► MAINTENANCE
```

The intended idea is:

> **Persistence is not the absence of damage. It is the capacity to detect divergence, preserve its history, regenerate a valid state, and continue without breaking custody.**

## `G*` / Gibbs boundary

HydraDG uses an application-defined, dimensionless information-state diagnostic inspired by information-theoretic/free-energy reasoning. A project form is:

```text
G* = U* - τ S_useful + γ S_irrelevant

ΔG*_t = G*_t - G*_reference
```

In this figure, `ΔG* > 0`, `≈ 0`, and `< 0` are **conceptual HydraDG state labels relative to a declared reference**, not physical thermodynamic measurements.

They do **not** mean:

- joules or kcal/mol;
- literal organismal Gibbs free energy;
- physical temperature;
- proof that lower `G*` causes better retrieval;
- proof of better Hit@K, Recall@K, or end-to-end QA.

`Cloud Drift`, Hit@K, and Recall@K remain separate empirical/diagnostic quantities.

## Sources and lineage

- Biological morphology/regeneration inspiration: [Hydra (genus), Wikipedia](https://en.wikipedia.org/wiki/Hydra_(genus)).
- Information-theoretic Gibbs/free-energy lineage: Enßlin & Weig (2010), *Inference with minimal Gibbs free energy in information field theory*, Physical Review E 82, 051112, DOI `10.1103/PhysRevE.82.051112`.
- HydraDG's `G*` is a project-defined analogy/design diagnostic, **not** a reproduction of the exact Enßlin–Weig functional.

## Claim ceiling

`CONCEPTUAL_HYDRA_REGENERATION_AND_INFORMATION_STATE_METAPHOR_ONLY`
