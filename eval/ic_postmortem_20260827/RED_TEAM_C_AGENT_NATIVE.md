# RED TEAM C — "Agent-Native or Web Demo?"

**IC principle:** *The logistics are the demo* — application, context, team formation, submission, judging are agent tool calls.

## What submission demonstrates

| Agent-native signal | Present in submission? |
| --- | --- |
| MCP server exposed | DESCRIBED in agent_surface (HydraDG APIs) |
| HydraLamp used IC MCP for its own submit | **No** |
| folder_id vault with evidence | **No** |
| Agent discovers IC surface | Not demonstrated |
| Agent uploads own evidence | Not demonstrated |
| Agent verifies submission state | Not demonstrated |
| RFC9421 signed request | **No** |

## Track 01 cold-start criterion alignment

Official question: *Can an agent nobody briefed discover, credential, and transact?*

- HydraLamp **describes** agent APIs — strong agent_surface prose.
- HydraLamp **does not demonstrate** using IC's agent surface for submission logistics.
- Meta-failure: we told judges we are agent-native via HTTP APIs while submitting through a human-operated text form without vault.

## Score (diagnostic)

| Dimension | Assessment |
| --- | --- |
| Product agent-native | Moderate–strong (APIs, SSE, evidence gateway) |
| Submission agent-native | **Weak** (text form, no folder, no IC MCP proof) |
| IC principle alignment | **Failed meta-demo** |

## Counterfactual

Record a 2-minute receipt chain: agent calls `ic_hack_get` → `ic_folder_create` → `ic_files_put` × N → `ic_hack_submit` → `ic_hack_me`. Attach receipt JSONL to vault.
