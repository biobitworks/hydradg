# Verify that Antigravity is actually using FCO/FCG

There are three separate claims:

1. **FCO skill present** — a `SKILL.md` exists.
2. **FCO skill loaded** — Antigravity `/skills` lists it in the active Project.
3. **FCO custody executed** — Agent/Model/Turn objects and valid hashes were appended.

Do not collapse these claims.

## A. Verify loaded customization in Antigravity

In the active Antigravity conversation run:

`/skills`

Confirm the exact FCO skill appears.

Then run:

`/hooks`

if hooks are configured.

For the workspace rule:
`.agents/rules/FCO_CUSTODY_REQUIRED.md`

open Project Customizations → Rules and set it to **Always On**.

The file's existence alone is not evidence that the rule activation mode is Always On.

## B. Snapshot before one test interaction

```bash
source /Users/byron/projects/active/hydradg-knowledge-graph/env.sh
python scripts/snapshot_fco_runtime.py --out /tmp/fco-before.json
```

Perform one substantive Antigravity interaction that should update the graph.

Then:

```bash
python scripts/snapshot_fco_runtime.py --out /tmp/fco-after.json
python scripts/verify_live_custody.py --require-agent --require-model --require-turn
```

The proof condition is:
- Turn count increases;
- nodes SHA-256 changes;
- edges SHA-256 changes;
- verifier status is `PASS`;
- new Turn has input/output/model/session relations.

If the interaction changed project knowledge, `KnowledgeUpdate` count should also increase.

## C. One-command audit

```bash
bash scripts/verify_fco_runtime.sh
```

Interpretation:
- `FCO_SKILL_FILESYSTEM=PASS`: candidate FCO skill file was found.
- `FCO_TURN_KG=PASS`: the durable graph contains structurally valid Agent/Model/Turn custody.
- Neither proves the skill itself caused those writes.

## D. What proves the skill caused the update?

For strict attribution, require the FCO skill to write a small per-turn receipt containing:
- exact skill path;
- SKILL.md SHA-256;
- conversation/session identifier;
- emitted Turn FCO ID;
- nodes/edges journal hashes after emission.

Then link that receipt as a `ToolAction`/`Artifact`.

Until that receipt exists, use:
`FCO_CUSTODY_EXECUTED`
and
`FCO_SKILL_LOADED`
as separate claims, not `FCO_SKILL_EXECUTED`.
