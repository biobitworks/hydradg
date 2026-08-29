# CURSOR — FINAL SOLO PACKAGE CLOSEOUT CONTROLLER

Date: 2026-08-29
Host: `magicSTUDIObox.local` only
Repository: `biobitworks/hydradg`
Lane: **SOLO HydraDG / NewInML only**

This is the controlling closeout prompt for the solo package. Protein Hinge is a separate team project and MUST NOT be admitted into the solo evidence graph, result tables, manuscript claims, figures, or submission package. Protein Hinge may appear only in an explicit EXTERNAL_REFERENCE / CROSS_PROJECT_TRANSFER section if needed, with zero evidentiary weight for the solo submission.

## Objective

Establish whether experiments are genuinely running or terminal, stop starting work that cannot finish before the live submission cutoff, reconcile all material predecessor gates, execute only the bounded remaining work needed for the solo package, produce paired machine-language (ML) and human-language (HL) documentation for every package artifact/script/experiment, run security/path/machine-name scans, generate validated deterministic figures only from admitted receipts, build the successor paper/package, and stop at a human final-review gate.

Do not optimize nulls/negatives away. Historical `NULL`, `NEGATIVE`, `UNDERPOWERED`, `FAILED`, `TIMEOUT`, `BLOCKED`, `ABSTAINED`, or `CONTRADICTORY` states remain historical. A successor can resolve an execution/integrity blocker, but predecessor evidence remains in the FCG.

---

## 0. Reconfirm authority and deadline

First print:

```bash
hostname
whoami
pwd
date -u +%Y-%m-%dT%H:%M:%SZ
git branch --show-current
git rev-parse HEAD
git status --porcelain=v1 -uall
git remote -v
```

Require:

```text
hostname = magicSTUDIObox.local
```

Read in authority order, if present:

```text
PROJECT_CONTROL.yaml
AGENTS.md
FCO_FCG_CANONICAL_SPEC.md
CLAIM_CEILINGS.md
EVIDENCE_LEVELS.md
FCO_SCHEMA.json
FCG_SCHEMA.json
SIGNING_AND_KEYS.md
```

Then read fully:

```text
docs/EXP012_ANTICUBE_ESCALATION_PREREGISTRATION_20260829.md
docs/CURSOR_EXP012_ANTICUBE_FIGURES_MASTER_PROMPT_20260829.md
docs/CURSOR_FINAL_SOLO_PACKAGE_CLOSEOUT_20260829.md
```

Live deadline must be rechecked from the actual OpenReview venue before final freeze. The last externally verified configured NewInML cutoff was `2026-08-30T07:59:00Z`; do not assume it stayed unchanged.

Create:

```text
eval/final_solo_closeout_20260829/DEADLINE_RECEIPT.json
```

with source, observed deadline, retrieval timestamp, and operator buffer policy.

Deadline policy:

- no new long-running experiment may be launched if its bounded worst-case completion + verification + paper build would threaten the final review/upload buffer;
- incomplete optional experiments are preserved and excluded rather than rushed;
- existing positive/null/negative evidence is sufficient if claim ceilings are honest.

---

## 1. SOLO / TEAM contamination gate — P0

Before scientific execution, search the current solo branch/package/manuscript/eval/figures for Protein Hinge/team-only material.

Search at minimum for:

```text
protein-hinge
protein_hinge
Protein Hinge
ANTIGENCE_MODEL_MANIFEST
AUD-FCG-ATOM-SOT-SEMANTIC-003
B4 comparator
```

Classify every hit:

```text
SOLO_ADMITTED
EXTERNAL_REFERENCE_ONLY
TEAM_ONLY_EXCLUDE
AMBIGUOUS_BLOCK
```

Require:

```text
TEAM_ONLY_PRIMARY_EVIDENCE_COUNT=0
TEAM_ONLY_MANUSCRIPT_RESULT_COUNT=0
TEAM_ONLY_FIGURE_DATA_COUNT=0
```

Write both:

```text
eval/final_solo_closeout_20260829/SOLO_TEAM_BOUNDARY_ML.json
docs/final_solo/SOLO_TEAM_BOUNDARY_HL.md
```

If contamination exists, remove it only from the successor solo package/branch while preserving historical custody; do not rewrite the team repository or prior evidence.

---

## 2. Prove whether experiments are actually running

Do not infer `RUNNING` from a receipt, PID file, model residency, or directory name.

Inspect actual processes:

```bash
ps -axo pid,ppid,lstart,etime,%cpu,%mem,command | grep -E 'python|ollama|ollarma|seedgraph|exp012|daisy|qwen' | grep -v grep
pgrep -af 'exp012|daisy|seedgraph|run_.*matrix|ollama|ollarma' || true
curl -sS http://127.0.0.1:11434/api/version || true
curl -sS http://127.0.0.1:11434/api/ps || true
ollama list || true
```

For every candidate experiment/runtime identify:

```text
experiment_id
pid
ppid
runner_path
runner_sha256
branch
commit_sha
start_time
elapsed
cpu
memory
latest_output
latest_receipt
last_receipt_timestamp
expected_terminal_receipt
process_state
scientific_state
```

Allowed `process_state`:

```text
RUNNING_VERIFIED
IDLE
EXITED_SUCCESS
EXITED_FAILURE
STALE_PID
UNKNOWN_BLOCKED
```

Allowed `scientific_state` is independent:

```text
NOT_STARTED
IN_PROGRESS
COMPLETE_POSITIVE
COMPLETE_NULL
COMPLETE_NEGATIVE
UNDERPOWERED
FAILED
BLOCKED
PARTIAL_NONTERMINAL
```

Create paired outputs:

```text
eval/final_solo_closeout_20260829/EXPERIMENT_RUNTIME_STATUS_ML.json
docs/final_solo/EXPERIMENT_RUNTIME_STATUS_HL.md
```

No process is `RUNNING_VERIFIED` without live process evidence.

---

## 3. Build the single authoritative closeout matrix

Enumerate every material solo experiment/work unit needed for the paper/package, including at minimum current canonical evidence for:

- EXP-008
- EXP-009
- Stage-2 failure learning, if admitted in solo manifest
- HydraLamp solo-admitted deterministic systems evidence, if admitted by current paper boundary
- SeedGraph forensic predecessor
- piecewise SeedGraph real-evidence batches
- Qwen3.8 successor lane
- EXP-011 if actually implemented/executed
- EXP-012
- deterministic figure pipeline
- manuscript build / submission packet

Do not add Protein Hinge team experiments.

For each row record:

```text
work_unit_id
purpose
source_branch
source_sha
status
result_class
execution_integrity
admitted_to_paper
admitted_to_package
claim_ceiling
blocking_dependency
successor_needed
can_finish_before_cutoff
next_action
```

Output:

```text
eval/final_solo_closeout_20260829/SOLO_COMPLETION_MATRIX_ML.json
docs/final_solo/SOLO_COMPLETION_MATRIX_HL.md
```

Then classify remaining work:

```text
P0_SUBMISSION_BLOCKER
P1_HIGH_VALUE_FINISH_NOW
P2_INCLUDE_IF_ALREADY_TERMINAL
P3_DEFER_POST_SUBMISSION
```

Do not execute P3 work before submission.

---

## 4. Reconcile predecessor execution/integrity blocks

For every historical execution/integrity failure/blocker, identify the earliest divergent dependency and successor evidence.

Examples include, if still material:

- interrupted/corrupt SeedGraph V1A output;
- incomplete/partial Q38 lane;
- missing terminal receipts;
- stale/dirty Git state;
- source/hash mismatch;
- missing model identity/digest;
- missing readback;
- figure/manuscript build failure;
- security/path leak;
- incomplete package documentation.

Use successor state only where actual evidence supports it:

```text
OPEN_BLOCKER
RESOLVED_BY_SUCCESSOR
NOT_REQUIRED_FOR_SUBMISSION
DEFERRED_WITH_CLAIM_CEILING
```

Historical result classification itself does not change.

Write:

```text
eval/final_solo_closeout_20260829/PREDECESSOR_RECONCILIATION_ML.json
docs/final_solo/PREDECESSOR_RECONCILIATION_HL.md
```

---

## 5. Execute EXP-012 only if the time gate permits

If EXP-012 has not started, estimate its bounded work from actual case counts/model inventory and enforce the deadline policy. Prefer a preregistered bounded minimal matrix over an unfinishable long matrix only if the preregistration already permits it; otherwise preserve `NOT_RUN_DEADLINE_GATED` rather than silently changing N/models.

Follow the committed EXP-012 preregistration exactly.

Core policies:

```text
B0 largest available model / reference policy
B1 single large local model
B2 size cascade
B3 + FCG/provenance
B4 + AntiCube trajectory
B5 + ΔG*/CFMO/context deltas
```

Escalation rungs:

```text
R0 deterministic
R1 tiny
R2 small
R3 medium
R4 large
R5 largest local / true frontier only if actually available
R6 human only if residual material uncertainty remains
```

Every rung allows:

```text
ACCEPT
REJECT
ABSTAIN
ESCALATE
```

Joint success requires reduced expensive escalation AND no violation of the frozen quality/safety envelope.

Preserve null/negative/mixed results.

---

## 6. AntiCube / FCG / CFMO / ΔG trajectory

Maintain canonical AntiCube classification:

```text
X = SELF ↔ NON-SELF
Y = NON-SAFE ↔ SAFE
Z = time / governed state index
```

Do not invent continuous self/safety values if canonical output is categorical.

`ΔG*` is separate from the Z/time axis:

```text
ΔG*(t) = G*(t) - G*(t-1)
```

For each selected real trajectory produce:

```text
new_source_or_observation
new_atoms
fcg_root_before
fcg_root_after
delta_fcg
cfmo_before
cfmo_after
delta_cfmo
context_before
context_after
delta_context
anticube_before
anticube_after
anticube_movement
g_star_before
g_star_after
delta_g_star
priority_before
priority_after
routing_action
terminal_state
```

Inventory every distinct G*/ΔG-style formula from actual repository sources. Distinguish formula definitions from per-condition instances. Do not count Cloud Drift/JSD, TV mutation distance, restoration gain, entropy, or U* components as separate ΔG formulas unless the canonical source explicitly defines them as such.

Output:

```text
eval/final_solo_closeout_20260829/DG_SCORE_REGISTRY_ML.json
docs/final_solo/DG_SCORE_REGISTRY_HL.md
eval/final_solo_closeout_20260829/ANTICUBE_TRAJECTORIES_ML.jsonl
docs/final_solo/ANTICUBE_TRAJECTORIES_HL.md
```

---

## 7. Deterministic paper figures — no generated art

Use only deterministic code and receipt-owned values.

Generate only figures supported by completed evidence and relevant to the solo paper:

- AntiCube 3D time trajectory;
- source → atoms → ΔFCG → ΔCFMO → Δcontext → AntiCube → ΔG* → routing decision;
- hierarchical escalation funnel, if EXP-012 executed enough to support it;
- one selected real trajectory / FCG state-change figure.

Every dynamic figure element must map to:

```text
figure_element_id
visible_value
source_receipt
json_pointer
source_sha256
renderer_sha256
```

Generate SVG first, then deterministic PDF/PNG derivatives using pinned tooling.

Rebuild twice in clean temp directories and compare canonical SVG bytes.

Create:

```text
figures/final_solo/FIGURE_EVIDENCE_MAP_ML.json
docs/final_solo/FIGURE_EVIDENCE_MAP_HL.md
```

Do not include a figure whose evidence map fails.

---

## 8. ML + HL paired documentation for the final package

Every material file, script, experiment, figure, and package artifact included in the final solo package must have one machine-readable catalog record and one human-readable catalog entry keyed by the same `artifact_id`.

Do not duplicate every source byte into documentation. Instead create complete paired catalogs.

Machine catalog:

```text
package/final_solo/SOLO_PACKAGE_CATALOG_ML.jsonl
```

Required fields:

```text
artifact_id
path
type
sha256
role
source_or_generated
producer
producer_sha256
inputs
outputs
evidence_class
experiment_id
completion_state
claim_ceiling
solo_team_scope
security_scan_state
included_in_submission
```

Human catalog:

```text
docs/final_solo/SOLO_PACKAGE_CATALOG_HL.md
```

For each artifact answer simply:

- What is this?
- Why is it in the package?
- How was it produced?
- What does it prove?
- What does it NOT prove?
- How do I reproduce/verify it?
- Is it complete, partial, failed, or deferred?

Create also:

```text
docs/final_solo/HOW_TO_REPRODUCE.md
docs/final_solo/KNOWLEDGE_BASE.md
```

Knowledge Base must cover at least:

```text
FCO
FCG
AOK
SOT
SeedGraph
CFMO
AntiCube
Self / Non-self
Safe / Non-safe
G*
ΔG*
Cloud Drift
abstention
contradiction
supersession
claim ceiling
evidence class
routing rung
frontier vs largest-local
human escalation
SHA-256
signature state
Merkle/MMR state
```

---

## 9. Security / machine / hard-path scan — mandatory before package freeze

Run Gitleaks on the exact successor commit/package lineage. Preserve a machine-readable receipt.

Also scan final package, docs, manuscript source, generated figures, and tracked files for:

### Secrets / credentials

Patterns and actual scanners for:

```text
API keys
tokens
passwords
private keys
.env values
authorization headers
provider credentials
```

Never print secret values in receipts.

### Hard local paths

At minimum:

```text
/Users/
/Volumes/
file://
127.0.0.1
localhost
magicSTUDIObox.local
magicPRObox.local
```

Local hostnames may remain in internal scientific receipts where scientifically material, but must not leak into anonymized paper/public package fields unless explicitly intended. Classify each hit.

### Machine/person naming / double-blind leakage

Scan public/anonymized package for personal names, usernames, organization-specific private labels, hostnames, home directories, email addresses, and team-only project names.

Write:

```text
eval/final_solo_closeout_20260829/SECURITY_PUBLICATION_SCAN_ML.json
docs/final_solo/SECURITY_PUBLICATION_SCAN_HL.md
```

Required gate:

```text
GITLEAKS=PASS
SECRET_DISCLOSURE=0
UNAPPROVED_HARD_PATHS=0
UNAPPROVED_MACHINE_NAMES=0
DOUBLE_BLIND_IDENTITY_LEAKS=0
TEAM_ONLY_PRIMARY_EVIDENCE=0
```

If a public artifact fails, repair the successor artifact and preserve the failed pre-repair receipt.

---

## 10. Manuscript and package freeze

Do not overwrite a previously frozen PDF/manuscript.

Build a successor only after evidence, figures, and scope gates pass.

Verify:

```text
2–8 pages excluding references
NeurIPS 2026 workshop template
fully anonymized
citations resolve
figures legible
claims map to admitted evidence
no Protein Hinge team evidence
no unsupported completion claims
no 'SIGNED' unless actually signed
no 'MMR COMMITTED' unless actually committed
```

Run deterministic build twice where possible and record hashes.

Create final package root containing at minimum:

```text
paper PDF
paper source necessary for reproduction
figures + evidence map
SOLO_PACKAGE_CATALOG_ML.jsonl
SOLO_PACKAGE_CATALOG_HL.md
HOW_TO_REPRODUCE.md
KNOWLEDGE_BASE.md
SOLO_COMPLETION_MATRIX_ML.json
SOLO_COMPLETION_MATRIX_HL.md
SECURITY_PUBLICATION_SCAN_ML.json
SECURITY_PUBLICATION_SCAN_HL.md
terminal closeout receipt
SHA256SUMS
```

---

## 11. Git / custody closeout

Before commit:

```bash
git diff --check
git status --porcelain=v1 -uall
```

Run all relevant tests and final validation scripts.

Hash exact final bytes with SHA-256.

Do not claim digital signatures or Merkle/MMR commitment unless actual authorized operations occurred and receipts exist.

Commit/push bounded final work to the current successor branch. Do not merge to main automatically.

Update the draft PR with the exact final head and summary if appropriate.

---

## 12. Required terminal report

Print and write machine-readable + human-readable closeout:

```text
eval/final_solo_closeout_20260829/FINAL_SOLO_CLOSEOUT_ML.json
docs/final_solo/FINAL_SOLO_CLOSEOUT_HL.md
```

It must answer:

```text
OPENREVIEW_DEADLINE_VERIFIED=
CURRENT_TIME_UTC=
TIME_GATE_STATE=

CURRENT_BRANCH=
CURRENT_SHA=
ORIGIN_PARITY=

SOLO_SCOPE=PASS|FAIL
TEAM_PRIMARY_EVIDENCE_COUNT=

EXPERIMENTS_RUNNING_VERIFIED=
EXPERIMENTS_TERMINAL=
EXPERIMENTS_PARTIAL=
EXPERIMENTS_DEFERRED=

EXP012_STATE=
EXP012_CLAIM_CEILING=

PREDECESSOR_OPEN_BLOCKERS=
PREDECESSOR_RESOLVED_BY_SUCCESSOR=

ANTICUBE_TRAJECTORY_STATE=
DG_SCORE_DEFINITION_COUNT=
FCG_DELTA_STATE=
CFMO_DELTA_STATE=

FIGURES_VALIDATED=
FIGURE_EVIDENCE_MAP=PASS|FAIL

ML_CATALOG=PASS|FAIL
HL_CATALOG=PASS|FAIL
HOW_TO=PASS|FAIL
KB=PASS|FAIL

GITLEAKS=
SECRET_DISCLOSURE_COUNT=
UNAPPROVED_HARD_PATH_COUNT=
UNAPPROVED_MACHINE_NAME_COUNT=
DOUBLE_BLIND_LEAK_COUNT=

PAPER_BUILD=
PAPER_SHA256=
PACKAGE_ROOT_SHA256=

SIGNATURE_STATE=
MERKLE_MMR_STATE=

EVIDENCE_STATE=
EXPERIMENT_STATE=
FCO_STATE=
FCG_STATE=
HYDRADB_STATE=
EARLIEST_DIVERGENCE=
CLAIM_CEILING=
NEXT_SAFE_ACTION=
FINAL_REVIEW_GATE=REQUIRED
```

Stop at `FINAL_REVIEW_GATE=REQUIRED`. Do not submit to OpenReview automatically and do not merge main automatically.