# Context / Route Gate

Status: ACTIVE_PROJECT_CONTROL
Scope: HydraDG / Hack Hydra substantive work

## Purpose

Prevent project drift caused by acting in the wrong conversation, repository, branch, host, or task lane.

Before every substantive HydraDG turn or execution instruction, record and compare the declared context tuple:

- project: FCO/FCG — Verifiable Research & AI
- active_workstream: HydraDG / Hack Hydra Track 03
- primary repository: biobitworks/hydradg
- HydraDB review repository: biobitworks/hydradb-hackhydra
- local HydraDG path: /Users/byron/projects/active/hydradg
- local HydraDB path: /Users/byron/projects/active/hydradb
- control host: magicPRObox
- persistent execution host: magicSTUDIObox
- transport: ordinary SSH over Tailscale; Ollarma is a model/API bridge, not the shell administration boundary

## Turn-start gate

For each material turn, compare the user request and current conversation against the expected context tuple. If the request appears to belong to another project (for example LessWrong article work), mark `CONTEXT_MISMATCH` and do not issue repository-changing or execution commands until the intended workstream is re-established.

Minimum route fields:

- conversation/workstream identity
- target repository
- target branch
- target host
- target local path
- task class (research, code, benchmark, release, article, infrastructure)

## Git execution gate

Every bounded implementation step uses:

1. fetch
2. pull --ff-only
3. verify local == remote baseline
4. execute/edit
5. test
6. receipt/hash
7. secret/claim gates
8. commit
9. push
10. fetch/pull
11. verify local == remote
12. review before the next bounded step

## Hashing / custody gate

For each material visible turn:

1. preserve the visible input/output scope that can actually be captured;
2. SHA-256 the captured bytes;
3. create a Turn FCO;
4. link to the prior Turn when the prior hash is actually available;
5. label any non-recomputed historical hash claim as `UNVERIFIED_PREVIOUS_TURN_HASH_CLAIM`;
6. do not call a turn signed or MMR-committed unless those operations actually occurred.

Failure to hash does not invalidate the underlying technical work. It lowers the custody/provenance ceiling and must be recorded as a custody gap.

## Recovery rule

When a context mismatch is detected:

- stop the wrong workstream;
- preserve what was actually changed;
- identify the earliest divergent dependency;
- classify affected and unaffected artifacts;
- re-establish the correct repository/branch/host tuple;
- resume from the last verified checkpoint rather than rewriting history.

This control is an FCO/FCG staging policy. It is not evidence of HydraDB ingestion until the same immutable objects are written to a pinned HydraDB instance and a write/read receipt is preserved.
