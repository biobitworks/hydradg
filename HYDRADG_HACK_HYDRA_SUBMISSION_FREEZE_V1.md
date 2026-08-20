# HydraDG Hack Hydra Submission Freeze Contract v1

## Mandatory submission deliverables

Only these three items are treated as submission-critical:

1. Public GitHub repository
2. Demo video of 3 minutes or less
3. Submission form

A live public website is NOT required by the supplied submission requirement.

## Product/demo architecture for submission

LOCAL DEMO
magicSTUDIObox
→ local HydraDB
→ local HydraDG Next.js
→ interactive Context Iceberg / FCG / Judge Demo
→ screen-recorded demo video

PUBLIC EVIDENCE
GitHub public repository
→ code
→ README
→ architecture
→ Track 03 results
→ FCO/FCG custody receipts
→ KB / How-To docs
→ static screenshots if useful

SUBMISSION
form
→ public GitHub URL
→ demo video URL
→ project/team/track/description fields

## Stop-work rule

Do not block submission on:
- Vercel deployment
- hosted HydraDB API
- public live website
- Cloudflare tunnel
- remote HydraDB tenant
- real-time off-network graph backend

These may be completed later only if they do not delay the three mandatory deliverables.

## Local demo gates

Before recording:
- local HydraDB connected
- local graph route working
- Context Iceberg interactive
- Hit@K visible
- Recall@K visible
- ΔHit@K visible where receipt-owned
- ΔRecall@K visible where receipt-owned
- Knowledge Base available
- How-To available
- static fallback available locally
- Enßlin & Weig G*/ΔG* lineage restored
- custody completeness gate passes
- no unsupported claims

## GitHub public-release gates

Before making repository public:
- current release branch pushed
- README explains what/why/how
- component map present
- submission document present
- no secrets
- no private keys
- no restricted private data
- rights/release scan passed
- local absolute paths removed from judge-facing docs where unnecessary
- current scientific null/negative result preserved
- Enßlin & Weig citation/source lineage included
- FCO/FCG custody repair receipts included where public-safe

## Video target

Keep final video under 3 minutes.

Recommended ~2:20–2:40 structure:

0:00–0:20
Problem + what HydraDG is.

0:20–0:55
Interactive 4D Context Iceberg.
Rotate, zoom, scrub time.
Show ΔG*, Cloud Drift, Hit@K, Recall@K separately.

0:55–1:25
Reference → Poison → Antidote.
Show supersession/contradiction and retained history.

1:25–1:55
Track 03 executed result.
500 cases / 23,867 sessions / 4,776 entities / 3,506 facts.
Show actual null/negative retrieval result.

1:55–2:20
Trace one FCO backward:
source → transformation → evidence → claim ceiling.
Show HydraDB local readback.

2:20–2:35
KB / G* lineage:
Enßlin & Weig → HydraDG design analogy → G* → ΔG*.
State nonphysical boundary.

2:35–2:45
Close:
HydraDG preserves state, provenance, contradiction, recovery, and null/negative outcomes.

Leave 15 seconds of safety margin.

## Submission form content to prepare

- Project name: HydraDG
- Primary track: Track 03 — Memory + Context Retrieval
- Public GitHub URL
- Demo video URL
- Short problem statement
- Short solution statement
- Meaningful HydraDB use
- Track 03 result
- Team names/roles
- originality/reuse disclosure
- rules/accuracy confirmation
- optional artifact/hash/root references

## Claim boundary

Do not claim:
- benchmark superiority
- end-to-end QA improvement
- that lower G* causes higher recall
- that Cloud Drift is accuracy
- signed/Merkle-committed unless receipts establish it
- independent replication unless actually performed

## Definition of done

PUBLIC_GITHUB=PASS
VIDEO_UNDER_3_MIN=PASS
VIDEO_PUBLIC_OR_JUDGE_ACCESSIBLE=PASS
SUBMISSION_FORM_COMPLETE=PASS
ALL_THREE_SUBMITTED_BEFORE_DEADLINE=PASS

Then:
SUBMISSION_READY=YES
