# RED TEAM A — "I Have 90 Seconds"

**Persona:** Track 01 judge, Thursday 4:00 PM, twenty teams queued.

## Friction log (timed)

| Second | Action | Result |
| --- | --- | --- |
| 0–10 | Read title + blurb on IC submission card | "Agent-native zero-trust control plane" — generic; no "what's new today" |
| 10–20 | Click demo URL | Lands on hydralamp.vercel.app — unclear where golden path is |
| 20–40 | Skim agent_surface | Wall of text; six API paths; no curl example |
| 40–55 | Click repo | biobitworks/hydradg — **513+ commits since Aug 18**; looks like months of work, not 26h hackathon |
| 55–70 | Search for video/screenshots | **None in IC submission**; must hunt demo site |
| 70–90 | Decision | "Impressive substrate, unclear what's new, no attached walkthrough" |

## Scores (diagnostic, not official)

| Question | Score (0–5) |
| --- | --- |
| What does it do? | 3 — blurb explains custody concept |
| Why does it matter? | 3 — FCO/FCG angle visible |
| What is new? | **1** — indistinguishable from prior Hack Hydra |
| What is real? | 4 — demo URL works |
| Where to click? | 2 — no START_HERE, no golden shortcut in payload |

**Mean friction:** High on origin and navigation.

## Missing asset that would fix 90s comprehension

`00_START_HERE.md` in vault + blurb sentence: *"Built Aug 26–27; repo branch hack-hydra/hydralamp-20260826; start at /golden"*
