# Hackathon Submission FCO Protocol

Governed workflow for agent-native hackathon evidence delivery. Extends GSD/FCO orchestration from `docs/GSD_GSIGMAD_FCO_ORCHESTRATION_PROFILE.md`.

## Pipeline

```
EVENT_CONTEXT_FCO
  → RUBRIC_FCO
  → BUILD_PLAN
  → EVIDENCE_REQUIREMENT_GRAPH
  → BUILD/TEST
  → MEDIA_CAPTURE
  → ORIGIN_PROVENANCE
  → RED_TEAM
  → SCORECARD_SIMULATION
  → VAULT_BUNDLE
  → SIGNED_SUBMISSION_WHEN_AVAILABLE
  → PLATFORM_ACK
  → ORIGIN_MMR
  → CLOSEOUT
```

## Phase contracts

### 1. EVENT_CONTEXT_FCO

- `ic_hack_get` → freeze event, rubric_url, bounties, phase
- Archive raw response + SHA-256
- Record sponsor bounty text verbatim

### 2. RUBRIC_FCO

- Fetch rubric URL content; map each dimension to required evidence
- Declare track (01 or 02) in build plan
- **Gate:** No build without rubric snapshot on disk

### 3. BUILD_PLAN

Per rubric dimension, pre-specify:

| Field | Required |
| --- | --- |
| claim | What we assert |
| required_evidence | Receipt class |
| expected_artifact | Path |
| media_required | yes/no |
| machine_verifiable_receipt | yes/no |
| judge_visible_location | vault path or submit field |

### 4. EVIDENCE_REQUIREMENT_GRAPH

DAG: rubric dimension → artifact → media → receipt → vault file

### 5–7. BUILD / MEDIA / ORIGIN

- Origin doc: substrate vs new work with commit SHAs
- Negative/null results preserved
- Media captured before submission freeze

### 8. RED_TEAM

Mandatory gates before submit:

- **90-second judge** (RED_TEAM_A)
- **Reuse skeptic** (RED_TEAM_B)
- **Agent-native meta** (RED_TEAM_C)
- **Sponsor accuracy** (RED_TEAM_D)
- **Provenance chain** (RED_TEAM_E)

### 9. SCORECARD_SIMULATION

Fill `RUBRIC_SCORECARD_TEMPLATE.json` with ranges from red-team evidence.

### 10. VAULT_BUNDLE

```
ic_folder_create → ic_files_put × N → record folder_id
```

Curated package (~15–25 files), not repo dump.

### 11. SIGNED_SUBMISSION

- `ic_hack_submit` with all fields + `folder_id`
- RFC9421 signed mode when operator key available
- `ic_hack_me` verify

### 12–14. ACK / ORIGIN_MMR / CLOSEOUT

- Freeze payload bytes + hash
- Origin MMR separate from scientific MMR
- FCG append only with authorized signing

## Hard gate

```
NO_SUBMISSION_WHILE_JUDGE_RELEVANT_EVIDENCE_IS_AVAILABLE_BUT_UNSURFACED
```

Unless explicitly waived by human operator with recorded waiver in `OPERATOR_APPROVAL_PACKET.json`.

## Immersive Commons-specific checklist

- [ ] `ic_hack_get` archived
- [ ] Track declared in blurb
- [ ] `folder_id` populated with vault
- [ ] `00_START_HERE.md` in vault
- [ ] `02_WHAT_IS_NEW_VS_PRIOR_WORK.md` in vault
- [ ] Origin date in blurb
- [ ] Repo URL includes branch
- [ ] Demo URL points to golden path
- [ ] Video + contact sheet in vault
- [ ] Sponsor receipts with LIVE/ERROR labels
- [ ] Agent demonstrated IC MCP submit chain
- [ ] 90-second red-team PASS
- [ ] Payload SHA-256 matches seal

## Custody

Every phase emits handoff receipt per `schemas/agent_model_handoff_receipt.schema.json`. Hash ≠ signature. `SIG-*` = legacy label only.
