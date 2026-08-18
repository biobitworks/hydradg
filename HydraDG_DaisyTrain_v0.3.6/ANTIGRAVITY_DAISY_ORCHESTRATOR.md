# Antigravity HydraDG Multi-Backend Daisy Orchestrator

You are operating Byron's HydraDG / Hack Hydra Track 03 project.

## Authority and terminology

Do not invent project names, experiment IDs, files, routes, or terminology.

Before using a project-specific term, confirm it in one of:
1. the current HydraDG package,
2. the local `fractal-custody-objects` repository,
3. the local `gtm-cellico` repository,
4. an executed receipt/result artifact,
5. direct user instruction.

Important exact repository name: `gtm-cellico`, not GEM/Cellico.

Search for the literal term `ollarma` locally before assuming what it means:
- project files;
- executables;
- shell aliases/functions;
- services;
- local repositories.
If no actual object named `ollarma` exists, record `OLLARMA_NOT_FOUND` and treat the intended runtime as `Ollama`. Do not silently rename it.

## Project root

Expected current package:
`/Users/byron/projects/active/hydradg/HydraDG_DaisyTrain_v0.3.4`

If this exact directory does not exist, locate the newest `HydraDG_DaisyTrain_v0.3.*` directory and report the actual path before changing anything.

Read first:
- `README.md`
- `PLAN.md`
- `DAISY_TRAIN.md`
- `EVALUATION_MATRIX.md`
- `CLAIM_LEDGER.md`
- `FCO_REPO_AUDIT_STATUS.md`
- `LOGGING_PROTOCOL.md`
- `RUNBOOK_MAGICPROBOX_MODAL.md`

## Non-negotiable evidence rules

Use FCO/FCG claim discipline.

Never state:
- verified,
- reproduced,
- deterministic,
- signed,
- Merkle committed,
- MMR committed,
- HydraDB-ingested,
- independent replication

unless the corresponding operation actually ran and a receipt/result exists.

Keep distinct:
- content/file identity;
- canonical scientific/model state identity;
- deterministic replay;
- provenance;
- correctness;
- empirical observation;
- independent replication.

No signatures or MMR roots unless actually computed.

Do not modify or rewrite frozen historical results.

## Security rules

Do NOT:
- print credential values;
- run `env`, `printenv`, `modal token info`, `cat ~/.kaggle/*`, or commands that dump secrets;
- put secrets in logs, Git, notebooks, kernel metadata, prompts, JSON receipts, or handoff files;
- expose Ollama directly to the public Internet;
- bind Ollama to `0.0.0.0` merely for convenience;
- perform broad LAN/network scans;
- delete Modal volumes, Kaggle kernels, Git branches, historical result files, or local checkpoints;
- force-push;
- commit files larger than 25 MB;
- upload PHI/private biological data to public services.

For every operational command use:
`bash scripts/run_logged.sh LABEL -- <command...>`
or a sequence via:
`bash scripts/run_sequence.sh LABEL <command-file>`

If a command fails, stop that lane and preserve:
`logs/LAST_ERROR_FOR_CHAT.txt`

## Current evidence state

The source-stable ECA quick canary on Modal has already succeeded under v0.3.3/v0.3.4 lineage with:
- total trajectories = 8
- perturbed trajectories = 6
- exact first-divergence localizations = 6
- oracle-repair trajectories = 2
- state-exact recoveries = 2

Treat this only as the quick Modal canary. The full80 multi-backend comparison remains to be executed.

Existing Vithia/Pythia receipts already establish bounded same-SKU T4 reproducibility and controlled/cross-SKU gradient-divergence observations. Do not rerun them unless a later comparison explicitly requires it.

#

# Durable KG home and SeedGraph review

Before spawning substantive agents, run:

`bash scripts/run_sequence.sh KG_BOOTSTRAP commands/00_bootstrap_kg.txt`

Then source:

`/Users/byron/projects/active/hydradg-knowledge-graph/env.sh`

All Agent/Model/Turn/ToolAction/KnowledgeUpdate records must use
`$HYDRADG_LIVE_GRAPH_DIR`.

Do not keep the authoritative live journal inside only the versioned Daisy Train folder.

Read `SEEDGRAPH_SUBMISSION_REVIEW.md`.
Treat SeedGraph's reviewed evidence-atom/provenance schema as implementation lineage.
Do not create a competing ontology where a mapping to EvidenceSeed/Sentence/Claim/
Evidence/ProvenanceRecord/Packet is sufficient.

The local durable KG must preserve:
- internal author-facing graph;
- anonymous submission derivative;
- SeedGraph review and bridge schema;
- HydraDB pin/ingestion receipts;
- agents/models/turns/actions/knowledge updates;
- submission claim/evidence links.

The anonymous graph must be generated from the internal graph by explicit redaction,
not independently hand-authored.


# Mandatory FCO/FCG registration for agents, models and turns

Read `AGENT_MODEL_TURN_FCO_POLICY.md`.

Every Antigravity subagent is a first-class `Agent` FCO.
Every distinct underlying model/tag/version is a first-class `Model` FCO.
Every material visible input/output interaction is a `Turn` FCO.
Every external command/tool operation is a `ToolAction` FCO.
Every proposed knowledge-graph change is a separate `KnowledgeUpdate` FCO.

Do not record or request private chain-of-thought. Record only visible prompt/output
artifacts, tool receipts, declared parameters, and bounded knowledge updates.

Before a subagent begins substantive work, preserve its initial task text to a file.
After the agent produces a visible result/handoff, preserve that output to a file and run:

`python scripts/record_agent_turn.py ...`

with the exact Agent and Model identity available from the runtime. If the model
version/digest is unavailable, use `UNRESOLVED`; do not guess.

For each command/tool action, run `scripts/record_tool_action.py` against its logged
receipt.

For each graph-memory change, construct a bounded knowledge-update JSON and run:
`scripts/record_knowledge_update.py`.

After a material batch:
`python scripts/finalize_live_fcg.py`

The current local graph lives under `custody/live/`.
Do not call it HydraDB-ingested until the pinned HydraDB adapter performs and records
a successful write/read round trip.

When HydraDB becomes live, preserve the existing FCO IDs and ingest them rather than
minting semantically equivalent replacement identities.


# Objective

Run a parallel daisy train across:

A. `magicstudiobox` local lane
B. Kaggle independent-provider lane
C. Modal cloud lane
D. HydraDB/LongMemEval preparation lane

Then aggregate all small evidence artifacts on `magicPRObox`.

The immediate cross-backend scientific target is `ECA-EXT80`:
- 4 rules: 30, 90, 110, 184
- 5 deterministic seeds
- 4 conditions
- 80 total trajectories
- 60 perturbed trajectories
- expected exact first-divergence denominator = 60
- oracle repair denominator = 20

Do not call this the historical FCO ECA experiment. It is the new `ECA-EXT80` extension.

---

# AGENT A — magicstudiobox / Ollama

## A1. Locate the machine without scanning

Inspect only known local configuration:
- `~/.ssh/config`
- project documentation
- `ssh -G magicstudiobox`
- `ssh -G magicstudiobox.local` if needed

Do not scan subnets.

Resolve a usable SSH host alias. If no configured/reachable host exists, write the failure to the handoff and stop this lane.

## A2. Determine whether `ollarma` exists

Search literal `ollarma` in:
- shell PATH / aliases;
- `/Users/byron/projects`;
- relevant configuration;
- services.

Record exact paths/results.

If absent, set:
`ollarma_status = OLLARMA_NOT_FOUND`
and continue with Ollama.

## A3. Ollama health

On magicstudiobox, determine:
- `ollama --version`
- whether the service is running;
- `ollama list`
- local API health at `http://127.0.0.1:11434/api/tags`;
- model names/tags already installed;
- available disk space.

Do not pull a large new model yet.

Ollama must remain loopback-bound unless the user has already configured a secure authenticated proxy.

Preferred access from magicPRObox:
SSH local forwarding, for example:
`127.0.0.1:11434 -> magicstudiobox:127.0.0.1:11434`

Create a reusable script:
`scripts/open_magicstudiobox_ollama_tunnel.sh`

The script must not expose Ollama publicly.

Verify the tunnel from magicPRObox with `/api/tags`.

Write:
`handoff/OLLAMA_STATUS.json`

including:
- actual hostname/SSH alias;
- `ollarma` lookup status;
- Ollama version;
- installed model tags;
- tunnel method;
- endpoint used;
- no secrets.

## A4. ECA local full80

Transfer or access only the exact v0.3.4 ECA implementation.

Run `ECA-EXT80` on magicstudiobox.

Return:
- `eca_extension_80_magicstudiobox.json`
- receipt with Python/platform information;
- result-body SHA-256.

Do not alter the ECA algorithm to make hashes match another backend.

---

# AGENT B — Kaggle independent replication

## B1. Preflight

Check:
- `kaggle --version`
- whether authentication works without printing credentials.

Prefer:
- existing OAuth/session;
- existing secure access-token file;
- otherwise stop and request user authentication.

Never print token contents.

## B2. Create a private Kaggle Script kernel

Create under:
`work/kaggle_eca_ext80/`

Contents:
- one self-contained Python script implementing the exact ECA-EXT80 algorithm;
- `kernel-metadata.json`.

Make the kernel private.

Do not require Internet during execution.

CPU is sufficient for ECA. Do not consume Kaggle GPU quota for this conformance run unless required by the platform.

Output at minimum:
- `eca_extension_80.json`
- `backend_receipt.json`

The result-body object must use the same canonicalization used by v0.3.4.

Push and run the kernel with the official Kaggle CLI.

Monitor with `kaggle kernels status`.

On completion, download only required output files.

Write local results under:
`eval/kaggle/`

If the run fails, preserve the Kaggle status/error and stop the Kaggle lane.

## B3. Do not claim independent verification prematurely

A different cloud provider is evidence of a different execution environment, but label it:
`CROSS_PROVIDER_REPLICATION_OBSERVED`
only if the result is actually rerun and compared.

Use `INDEPENDENT_VERIFICATION` only if the declared independence criteria in the project are satisfied.

---

# AGENT C — Modal full ECA

The quick source-stable canary passed.

Run the full source-stable v0.3.4/v032 ECA job.

Use:

`bash scripts/run_sequence.sh MODAL_ECA_FULL commands/02_modal_eca_full.txt`

Expected target:
- 80 trajectories
- 60 perturbed
- 60 exact first-divergence localizations
- 20 oracle repair
- 20 state-exact recovery

Do not assume these values before the full job completes.

Retrieve the JSON receipt, validate it, and render figures.

Store:
- `eval/eca/eca_extension_80.json`
- figures under `figures/generated/`
- logged execution evidence.

If Modal fails, do not continue dependent Modal commands.

---

# AGENT D — HydraDB / LongMemEval preparation

This lane is preparation only until exact APIs and dataset bytes are pinned.

## D1. HydraDB

Inspect the current official/local HydraDB repository.

Record:
- exact commit SHA;
- build/runtime instructions;
- graph ingestion API actually present at that commit;
- query API actually present at that commit;
- any current Track 03-specific examples.

Write:
`config/hydradb_pin.json`

Do not fabricate Cypher/API calls that are not supported by the pinned runtime.

Do not claim HydraDB ingestion until an actual write/read round trip succeeds.

## D2. LongMemEval-S

Use the project's existing verified downloader/hash contract.

Obtain/verify the official cleaned LongMemEval-S artifact.

Do not silently substitute another LongMemEval file.

Prepare:
- `smoke80`
- later full500

Do not launch the full500 until smoke80 graph construction/query/scoring is frozen.

## D3. Ollama evaluation route

Once Agent A has a working local Ollama endpoint, create an inference adapter whose configuration records:
- exact model tag;
- model metadata/digest if available;
- endpoint type;
- generation parameters;
- context length;
- deterministic/seeding settings when actually supported.

Do not call Ollama deterministic unless repeated evidence establishes that property under the bounded configuration.

Use this adapter later for the same A/B/C/D LongMemEval ablations.

---

# AGGREGATION AGENT

After A/B/C complete or fail independently:

## Compare ECA results

Collect:
- magicstudiobox result
- Kaggle result
- Modal result
- existing local v0.3.4 self-test result

Run exact comparison.

First compare:
`result_body_sha256`.

If hashes differ:
- do not normalize away the difference;
- identify the first differing JSON path;
- identify the first differing trajectory;
- identify the first differing step;
- compare state hashes and hamming values;
- record environment differences.

Create:
`eval/eca_cross_backend_comparison.json`

Classify each pair as:
- `CONTENT_EXACT`
- `SCIENTIFIC_RESULT_EQUIVALENT`
- `DIVERGED_AT_<object>`
- `NOT_EXECUTED`

No claim promotion beyond the evidence.

## Build handoff

Always maintain these small files:

`handoff/LAST_STATUS.md`
`handoff/EVIDENCE_INDEX.json`
`handoff/BACKEND_MATRIX.json`
`handoff/NEXT_COMMAND.txt`

If there is a failure:
`handoff/LAST_ERROR_FOR_CHAT.txt`

`LAST_STATUS.md` must contain:
- what actually completed;
- exact denominators;
- result hashes;
- what failed;
- what remains;
- claim ceiling for each lane.

`EVIDENCE_INDEX.json` must list every result/log/figure path and SHA-256.

---

# Git handoff for ChatGPT

Inspect the current HydraDG project's `git remote -v`.

If a user-owned GitHub origin already exists:
1. create a new non-destructive branch:
   `hack-hydra/antigravity-daisy-20260817`
2. commit only:
   - source/config changes;
   - small JSON/CSV/MD receipts;
   - small figures;
   - handoff files;
3. never commit:
   - secrets;
   - raw credentials;
   - `.pt` checkpoints;
   - large datasets;
   - PHI;
   - files >25 MB.
4. push that branch.

If no GitHub origin exists:
- do not create a repository without user approval;
- leave the handoff files locally.

When done, make `handoff/LAST_STATUS.md` the final human-readable output.

---

# Priority order

Run these in parallel where safe:

1. Modal ECA full80.
2. magicstudiobox host/Ollama preflight + ECA full80.
3. Kaggle ECA full80.
4. HydraDB pin + LongMemEval-S data verification.

After the three ECA lanes:
5. cross-backend exact comparison.
6. freeze evidence/figures.
7. XenoDisorder local→Modal replay only after its exact frozen-assets contract passes.
8. HydraDB smoke80.
9. A/B/C/D smoke80 ablation.
10. full500 only after smoke80 is frozen.

Do not spend time repairing the unrelated Daytona `compdef` startup warning unless it prevents a required command.

## End-state success criteria for this Antigravity session

Minimum successful session:
- Modal full80 executed and validated;
- magicstudiobox/Ollama status established;
- Kaggle lane either executed or has a precise authentication blocker;
- HydraDB exact commit/API pin recorded;
- `handoff/LAST_STATUS.md` generated.

Strong success:
- all three ECA backends executed;
- exact cross-backend comparison generated;
- secure Ollama tunnel operational;
- LongMemEval-S source verified;
- smoke80 ready to ingest.

Stop rather than inventing or silently substituting if any required dependency cannot be established.
