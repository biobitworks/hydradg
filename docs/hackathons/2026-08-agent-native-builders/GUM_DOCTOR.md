# GUM Doctor — HydraDG / Agent Native Builders Hackathon Intake

## Mission

Act as the execution doctor for **HydraDG** and prepare/submit the strongest truthful application for the **Agent Native Builders Hackathon @ Cloudflare HQ, San Francisco, August 26–27, 2026**, using the official Immersive Commons MCP application path.

The objective is **admission**, but never fabricate qualifications, event roles, membership state, product capabilities, partner integrations, usage, metrics, or prior approvals. Do not attempt to bypass Luma or Immersive Commons admission controls.

This run must be **self-saving and resumable**. Persist every non-secret artifact and exact decision state in the HydraDG repository so another agent can resume without relying on chat history.

---

## Operating constraints

1. Find the HydraDG repository root.
2. Before substantive work, read and follow:
   - `PROJECT_CONTROL.yaml`
   - `AGENTS.md`
   - any hackathon-, custody-, security-, or contribution-specific control files referenced by them.
3. Report before changes:
   - `REPO=`
   - `BRANCH=`
   - `HEAD=`
   - `STATUS=`
   - `REMOTES=`
   - `DEFAULT_REMOTE_BRANCH=`
4. Preserve existing uncommitted work. Do not reset, clean, stash, overwrite, or delete unrelated changes.
5. Never print, echo, log, commit, or serialize secret values.
6. The Immersive Commons bearer token must come from:
   - `FLOOR10_AGENT_TOKEN`
7. If the token is missing, stop at the credential gate and save a failure receipt. Do not ask for the token value and do not put a placeholder secret into Git.
8. Do not claim `SIGNED` unless an authorized private-key signature actually occurs.
9. SHA-256 hashes are integrity receipts, not signatures.
10. Use the project’s FCO/FCG conventions when present.

---

## Custody model

Maintain:

`source/evidence -> transformation/tool -> derived evidence -> claim -> artifact`

Label evidence as one of:

- direct human evidence
- repository/canonical evidence
- externally retrieved evidence
- deterministic computation
- MCP/API returned evidence
- model-generated proposal
- inference/hypothesis
- verified empirical result
- null/negative/failed/timeout/contradictory evidence

Never promote a claim above its supporting evidence.

For material agent work, record:

`OFFER -> ACCEPT -> EXECUTE -> VERIFY -> CLOSEOUT`

The user's instruction to run this GUM Doctor is the human ACCEPT for the bounded application workflow below.

---

# Phase 0 — Create a durable workspace

Create or reuse:

```text
docs/hackathons/2026-08-agent-native-builders/
custody/hackathons/2026-08-agent-native-builders/
```

At minimum persist:

```text
docs/hackathons/2026-08-agent-native-builders/
  README.md
  HYDRADG_APPLICATION_DOSSIER.md
  TRACK_DECISION.md
  PARTNER_FIT_MATRIX.md
  APPLICATION_ANSWERS.md
  APPLICATION_STATUS.md
  DEMO_GOLDEN_PATH.md

custody/hackathons/2026-08-agent-native-builders/
  00_RUN_CONTEXT.json
  01_REPO_EVIDENCE.json
  02_IC_SETUP_CHECK.json
  03_IC_TOOL_SCHEMA.json
  04_HACKATHON_EVENT.json
  05_APPLICATION_FORM.json
  06_PRE_APPLICATION_STATUS.json
  07_APPLICATION_PAYLOAD_REDACTED.json
  08_APPLICATION_RESPONSE.json
  09_POST_APPLICATION_STATUS.json
  10_CLOSEOUT.json
  SHA256SUMS
```

If an artifact already exists, preserve it and version the new output instead of silently overwriting canonical evidence.

---

# Phase 1 — Repository evidence first

Inspect the actual HydraDG repository and derive the application from what exists now.

Find evidence for:

- what HydraDG is
- current public or agent-facing interfaces
- MCP/A2A/REST/API surfaces, if any
- FCO/FCG provenance or custody mechanisms
- discovery mechanisms
- agent identity/access controls
- multi-agent handoff support
- audit logs / deterministic receipts
- data/model/tool provenance
- current deployment state
- demoable workflows
- security controls
- accessibility characteristics
- payments capability, if any
- integrations already implemented
- integrations merely proposed

Do not use conversational memory as canonical proof when repository evidence exists.

Save evidence pointers with paths, commit SHA, and where useful SHA-256 hashes.

---

# Phase 2 — Immersive Commons credential gate

Verify only that the credential exists:

```bash
test -n "${FLOOR10_AGENT_TOKEN:-}"
```

Never run:

```bash
echo "$FLOOR10_AGENT_TOKEN"
env | grep FLOOR10
set
printenv FLOOR10_AGENT_TOKEN
```

Use the official MCP endpoint:

```text
https://www.immersivecommons.com/api/mcp
```

Authentication:

```text
Authorization: Bearer $FLOOR10_AGENT_TOKEN
```

If an official deterministic setup-check endpoint is available from the current IC documentation/tooling, call it and save the **redacted** response.

---

# Phase 3 — Discover, do not invent, the live MCP contract

Connect to Immersive Commons MCP and run `tools/list`.

Do not assume tool names, event IDs, argument schemas, enum values, or response fields from this prompt.

Locate the current tools corresponding to:

- hackathon event discovery/get
- current user's hackathon state
- application form/schema
- application status
- application submission
- registration/seat claiming
- NDA
- teams
- submission

Expected names may include, but must be verified live:

```text
ic_hack_get
ic_hack_me
ic_hack_application_form
ic_hack_application_status
ic_hack_apply
ic_hack_register
ic_hack_sign_nda
ic_hack_team_list
ic_hack_team_create
ic_hack_team_join
ic_hack_submit
```

Save the exact relevant tool schemas to:

```text
custody/hackathons/2026-08-agent-native-builders/03_IC_TOOL_SCHEMA.json
```

If the live schema differs, the live schema wins.

---

# Phase 4 — Identify the exact event

Identify the event matching:

```text
Agent Native Builders Hackathon
Cloudflare HQ
101 Townsend St, San Francisco
August 26–27, 2026
```

Persist the exact event identifier and returned event metadata.

Do not use a guessed slug or ID.

---

# Phase 5 — Inspect admission state before writing

Call the live equivalents of:

```text
ic_hack_application_status
ic_hack_application_form
ic_hack_me
ic_hack_get
```

Record separately:

```text
LUMA_STATE=
IC_APPLICATION_STATE=
IC_EVENT_ROLE=
IC_PARTICIPANT_SEAT=
IC_NDA_STATE=
IC_TEAM_STATE=
```

Do not equate Luma `Pending` with IC application status.

If an application already exists:

- do not create a duplicate;
- inspect whether it can be updated using an authorized live tool;
- otherwise preserve it and proceed to a status/host-follow-up dossier.

If already accepted:

- do not reapply;
- proceed only with explicitly authorized registration/seat-claim actions supported by the live API.

If rejected:

- preserve the rejection exactly;
- do not attempt to evade or create alternate identities/tokens;
- prepare a concise human follow-up based on corrected/new factual evidence only.

---

# Phase 6 — Choose the strongest truthful HydraDG track

Evaluate both hackathon tracks against repository evidence:

## EXTERNAL — customer facing

Score HydraDG on:

- agent/service discovery
- secure agent access
- usability for people bringing their own agent/fleet
- multi-agent coordination
- payments, if currently implemented
- accessibility
- deployability in two days
- partner leverage
- demo clarity

## INTERNAL — team facing

Score HydraDG on:

- orchestration
- provenance across agents/tools
- handoff integrity
- source-to-claim custody
- policy/authorization boundaries
- multi-agent logs
- repeatability
- auditability
- deployability in two days
- partner leverage
- demo clarity

Use a table with:

```text
criterion
evidence
current state
gap
two-day build
success condition
failure condition
neutral/null outcome
```

Select one primary track only if no canonical human decision already locks the track.

If a prior project file locks the track, do not silently change it. Record any recommendation as a proposed change.

---

# Phase 7 — Partner-fit matrix

Evaluate only partners actually relevant to a shippable HydraDG demo.

Consider the current event list, but verify current partner/sponsor details from authoritative event/IC sources when available:

- Immersive Commons
- Runtype
- Cotal.ai
- Cloudflare
- Tavily
- Mitosis Labs
- Hacker Bob
- HUD
- Nebius
- Tenki
- other live event partners discovered through the event record

For each:

```text
partner
problem solved
HydraDG integration point
existing integration?
two-day integration?
evidence
demo payoff
risk
required credentials
cost/credit dependency
fallback
```

Do not claim integrations that are only planned.

Prefer the smallest set producing the clearest end-to-end story.

---

# Phase 8 — Build the application thesis

The application must explain HydraDG in hackathon-native language without inflating it.

The strongest framing should be derived from repo evidence and may resemble:

> HydraDG is an agent-native scientific provenance and coordination layer where multiple agents can discover governed tools/data, hand work off, preserve source-to-claim custody, and produce auditable outputs rather than unaudited chat transcripts.

Only use this if repository evidence supports it.

The application should directly address:

1. **Existing product/platform**
   - What HydraDG already is today.

2. **Why this hackathon**
   - What becomes agent-native over the two days.

3. **Fleet behavior**
   - At least 2–3 differentiated agents.
   - Discovery.
   - Access/authorization.
   - Handoff.
   - Verification.
   - Final artifact.

4. **Why the work matters**
   - Specific problem solved.
   - Why ordinary single-agent workflows are inadequate.

5. **Shippable demo**
   - One bounded golden path that can run by the end of day two.

6. **Partner usage**
   - Only specific partners with credible integration points.

7. **Builder fit**
   - Use only verified information supplied by the user or canonical project/event evidence.

---

# Phase 9 — Recommended demo golden path

Derive the final path from current HydraDG capabilities, but aim for something structurally like:

```text
Agent A — DISCOVER
finds HydraDG's machine-readable service/capability surface

        ↓

Agent B — EXECUTE
performs a bounded research/data/tool task

        ↓

HydraDG — CUSTODY
records sources, tool/model transformations, hashes, claims and artifacts

        ↓

Agent C — VERIFY
checks evidence/receipt consistency and rejects unsupported promotion

        ↓

HANDOFF
ordered, attributable message/task transfer

        ↓

FINAL ARTIFACT
human-readable result + machine-readable provenance graph/receipt
```

Include:

- success case
- negative/null case
- unauthorized action case
- contradictory evidence case
- recovery/resume case

Do not build speculative breadth at the expense of a working demo.

---

# Phase 10 — Fill the live application form

Use `ic_hack_application_form` to obtain the exact questions.

Create:

```text
docs/hackathons/2026-08-agent-native-builders/APPLICATION_ANSWERS.md
```

For each field save:

```text
QUESTION:
LIMIT:
PROPOSED ANSWER:
EVIDENCE:
CLAIM CEILING:
```

Respect every character limit deterministically.

Before submission, calculate and record exact character counts for constrained fields.

Do not include:

- unsupported metrics
- fake customers
- fake deployments
- unbuilt integrations described as live
- organizer/host status unless returned by the live event role API
- guaranteed admission language
- claims that Cloudflare is a sponsor if the event says it is only the venue host

---

# Phase 11 — Submit through the authorized MCP application path

If and only if:

- no duplicate application exists;
- the live MCP exposes an authorized application-write method;
- required fields are complete;
- all answers remain within evidence ceilings;

then call the live equivalent of:

```text
ic_hack_apply
```

This execution is authorized by the user through this GUM Doctor assignment.

Do **not** call an admin decision tool.

Do **not** grant yourself organizer/host/event-admin status.

Do **not** use `ic_hack_register` as a way to bypass application approval.

Save a redacted copy of the exact submitted payload and exact server response.

---

# Phase 12 — Verify after submission

Immediately call the application-status and current-user/event-state tools again.

Record:

```text
APPLICATION_SUBMITTED=
APPLICATION_ID=
APPLICATION_STATUS=
EVENT_ROLE=
PARTICIPANT_SEAT=
NDA_STATE=
NEXT_REQUIRED_ACTION=
SERVER_TIMESTAMP=
```

If status is pending/waitlisted, preserve that exactly.

If accepted and the API explicitly says the user is eligible to claim a seat, record the available registration action. Do not assume acceptance from a 2xx response to the application itself.

---

# Phase 13 — Human follow-up artifact

If still pending after the MCP application, create a short host follow-up in:

```text
docs/hackathons/2026-08-agent-native-builders/HOST_FOLLOWUP.md
```

It should state factually:

- the user is an Immersive Commons member only if verified by IC;
- the agent-native application has been submitted only if verified;
- HydraDG is the proposed project;
- one-sentence hackathon fit;
- availability for both days if known;
- request for consideration of the pending builder seat.

Do not imply insider entitlement or ask for a bypass.

---

# Phase 14 — SHA-256 custody receipt

Generate SHA-256 hashes for every non-secret artifact in the hackathon workspace.

Write:

```text
custody/hackathons/2026-08-agent-native-builders/SHA256SUMS
```

Use exact file bytes.

Do not label this a cryptographic signature.

---

# Phase 15 — Git handling

Before committing:

1. Run repository tests relevant to changed files.
2. Run the repository's secret scanner if configured.
3. Verify no token appears in:
   - tracked files
   - staged diff
   - generated receipts
   - logs
4. Show:
   - `git status --short`
   - `git diff --stat`
   - changed-file list

Commit only bounded hackathon planning/application/custody artifacts.

Suggested commit message:

```text
docs(hackathon): add governed HydraDG agent-native application dossier
```

Push only if project controls authorize pushing from the current branch.

Never merge without explicit authorization if project controls prohibit it.

---

# Required terminal closeout

Return exactly these fields, followed by a short evidence-backed summary:

```text
REPO=
BRANCH=
HEAD_BEFORE=
HEAD_AFTER=
EVENT_ID=
IC_MEMBERSHIP_STATE=
LUMA_STATE=
IC_APPLICATION_STATE_BEFORE=
IC_APPLICATION_STATE_AFTER=
IC_EVENT_ROLE=
PARTICIPANT_SEAT=
PRIMARY_TRACK=
APPLICATION_SUBMITTED=
APPLICATION_ID=
NDA_STATE=
FILES_CREATED=
FILES_UPDATED=
SHA256SUMS_PATH=
TEST_RESULT=
SECRET_SCAN_RESULT=
COMMIT=
PUSH=
EARLIEST_DIVERGENT_DEPENDENCY=
NEXT_ACTION=
TERMINAL_STATE=
```

Allowed terminal states:

```text
APPLICATION_SUBMITTED_PENDING
ALREADY_APPLIED
ACCEPTED_NEEDS_REGISTRATION
REGISTERED_PARTICIPANT
BLOCKED_MISSING_TOKEN
BLOCKED_MCP_AUTH
BLOCKED_SCHEMA
BLOCKED_APPLICATION_CLOSED
REJECTED
NO_WRITE_PERFORMED
```

---

# Stop conditions

Stop safely and save evidence if:

- `PROJECT_CONTROL.yaml` or `AGENTS.md` forbids the intended write;
- the token is missing/invalid;
- the hackathon application is closed;
- the live MCP schema no longer exposes the expected authorized path;
- an existing application would be duplicated;
- the only apparent route requires admin/organizer privilege;
- a required factual claim cannot be supported;
- project state is dirty in a way that makes bounded writes unsafe.

In every blocked case, preserve the null/negative evidence and identify the earliest divergent dependency.

---

# Success definition

Success is **not** "claiming we got in."

Success is:

1. HydraDG repository evidence inspected.
2. Exact live IC hackathon schema discovered.
3. Existing application state verified.
4. Strongest evidence-bounded application produced.
5. Application submitted once through the authorized path if permitted.
6. Post-submit status verified.
7. All non-secret evidence saved locally in the repo.
8. Hash receipts generated.
9. No credentials exposed.
10. A resumable closeout exists for the next agent or human.
