# HydraDG Live ↔ Static Judge Navigation Contract v1

## Goal

A judge or presenter should always know:

1. whether they are on the LIVE site or STATIC fallback;
2. where to click next;
3. how to return to the hero;
4. how to switch to the fallback;
5. how to return from fallback to live;
6. what each click is proving.

## Persistent top navigation

Every live page should include:

`Overview | Judge Demo | Results | Graph | Knowledge | Eligibility | Static Fallback`

The active page must be visually highlighted.

The far-right status cluster should show:

- `LIVE` or `STATIC FALLBACK`
- `FCG <compact root>`
- `HydraDB CONNECTED` only if traceability canary passed
- `Signature <actual state>`

### Required live routes

- `/` → Overview / interactive Context Iceberg
- `/judge` → Reference → Poison → Antidote
- `/track03` → Track 03 executed results
- `/graph` → live FCG graph explorer
- `/knowledge` → project terms / FCO knowledge
- `/eligibility` → release/custody state
- `/backup/hydradg.html` → static fallback

## Live → static traversal

Every LIVE page should expose a clearly labeled:

`Open Static Fallback`

link to:

`/backup/hydradg.html`

The static fallback header should show:

`STATIC FALLBACK — NOT LIVE HYDRADB`

and contain:

`Return to Live Demo`

link to:

`/`

Do not hide this in a footer.

## Judge click path

The judge should be able to self-navigate:

1. `/`
   Click `Start Judge Walkthrough`
2. `/judge`
   Click `See Executed Result`
3. `/track03`
   Click `Trace One Result`
4. `/graph`
   Click a highlighted real FCO node
5. `/fco/<actual-id>`
   Click `Open Source / Evidence`
6. `/knowledge` or evidence target
   Click `Check Eligibility`
7. `/eligibility`
   Optional click `Open Static Fallback`
8. `/backup/hydradg.html`
   Click `Return to Live Demo`

Each CTA should use exactly these or similarly explicit labels.

## Presenter click path for video

The presenter should use only the primary CTAs; avoid browser back-button dependence.

### Shot A — Hero
URL: `/`

Actions:
- drag graph left/right;
- wheel zoom;
- click `Pause/Play` once if visible;
- move time slider one step;
- return to latest;
- point to Hit@K and Recall@K.

Then click:
`Start Judge Walkthrough`

### Shot B — Judge
URL: `/judge`

Actions:
- click Reference;
- click Poison;
- click Antidote;
- show old state retained.

Then click:
`See Executed Result`

### Shot C — Track 03
URL: `/track03`

Actions:
- point to Cases / Sessions / Entities / Facts;
- point to Hit@K, Recall@K, ΔHit@K, ΔRecall@K;
- point to negative/null result wording.

Then click:
`Trace One Result`

### Shot D — Graph
URL: `/graph`

Actions:
- click the highlighted demo FCO;
- inspector opens;
- point to FCO ID, claim ceiling, source/projection root.

Then click:
`Open Full FCO`

### Shot E — FCO
URL: `/fco/<actual-id>`

Actions:
- point to source SHA;
- transformation;
- evidence class;
- claim ceiling;
- HydraDB readback/traceability.

Then click:
`Check Eligibility`

### Shot F — Eligibility
URL: `/eligibility`

Actions:
- point to hash state;
- signature state;
- Merkle/MMR state;
- push state.

Then click:
`Open Static Fallback`

### Shot G — Static
URL: `/backup/hydradg.html`

Actions:
- point to `STATIC FALLBACK — NOT LIVE HYDRADB`;
- show same narrative sections;
- click `Return to Live Demo`.

### Shot H — Return live
URL: `/`

End on:
- LIVE badge;
- FCG root;
- HydraDB traceability state;
- interactive graph.

## UX constraints

- No route should require typing a URL during the video.
- No primary route should depend on browser Back.
- Every page must have a clear next-step CTA.
- Every page must have `Overview`.
- Every page must expose Static Fallback.
- Static fallback must expose Return to Live Demo.
- External links should open in a new tab.
- Internal judge flow stays in the same tab.

## Screenshot naming

- `01-live-overview.png`
- `02-live-judge-reference-poison-antidote.png`
- `03-live-track03-metrics.png`
- `04-live-graph-selected-fco.png`
- `05-live-fco-provenance.png`
- `06-live-eligibility.png`
- `07-static-fallback.png`
- `08-return-live.png`

## Acceptance checks

- `live_nav_complete = true`
- `static_nav_complete = true`
- `live_to_static_click = true`
- `static_to_live_click = true`
- `judge_flow_no_manual_url_entry = true`
- `judge_flow_no_browser_back_required = true`
- `presenter_flow_no_dead_end = true`
- `active_route_highlight = true`
- `live_static_badge_correct = true`
