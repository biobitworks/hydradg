# Final OpenReview Operator Packet (Human-Side Only)

**Updated:** 2026-08-29T06:12:38Z  
**Selection:** SUCCESSOR_V3  
**Git SHA (Action-tested):** `cfee4ee7a6a8c418f9c71a37ca96031518d895bc`  
**Action run:** `33237699604` — PASS

| Field | Value |
|-------|-------|
| Title | HydraDG: Governed Context Interventions with Fractal Custody for Agent Experiments |
| Workshop | NewInML @ NeurIPS 2026 |
| Deadline (operational) | 2026-08-29T08:59:00Z |
| Deadline (official AoE) | August 29, 2026 AoE |
| PDF (submit this) | `paper/newinml2026_solo/manuscript/build/main.pdf` |
| PDF SHA256 | `0b096ccec7c6c1a630e4308abacea89a59620e410bfaff705409ce884a93c1ad` |
| Content pages | 4 (5 total incl. references) |
| Supplement ZIP (if field exists) | `paper/newinml2026_solo/HYDRADG_NEWINML_ANON_FCO_VERIFY.zip` |
| Supplement SHA256 | `687b3a060ddddf07a7affdc984cff90105c05ff51ba74e54657ca348a316513d` |
| Public submission root | `387e7e1431037c46816b00e03f703965af731363b3bd7e958380b9f562d838ac` |
| Fallback V2 (do not submit unless V3 fails) | `6578d37eeb28a7f2bdadb967939e68b816174491df3932a792601d09aaa14c60` |
| Auto-submit | **NO** — human operator only |

## Pre-submit verify (optional, 30s)

```bash
shasum -a 256 paper/newinml2026_solo/manuscript/build/main.pdf
# expect: 0b096ccec7c6c1a630e4308abacea89a59620e410bfaff705409ce884a93c1ad

python3 paper/newinml2026_solo/reviewer_artifact/verify_submission.py
# expect: VERIFICATION=PASS
```

## Portal steps

1. Open logged-in NewInML OpenReview submission form.
2. Upload **main.pdf** (V3 SHA above).
3. Check for supplementary-material field:
   - **YES** → upload `HYDRADG_NEWINML_ANON_FCO_VERIFY.zip`
   - **NO** → PDF only; retain ZIP for reviewer/rebuttal
4. Enter authors, conflicts, eligibility, AI-use attestations manually.
5. Submit. Record submission ID + timestamp.

## Attestations (verify on portal)

- Non-archival workshop submission
- Double-blind anonymization
- Author responsible for all content
- AI-assisted preparation disclosed in manuscript Setup section

## Do not submit

- INTERNAL future-direction maps (`FUTURE_DIRECTIONS_CAMERA_READY_MAP.md`)
- cellARCH / BiobitWorks / repo-identifying material in anonymous PDF
- Protein Hinge artifacts (admission = 0)
- V2 fallback PDF unless V3 gate failure near deadline

## Post-submit

Create `paper/newinml2026_solo/final_v3/OPENREVIEW_SUBMISSION_RECEIPT.json` with:

- submission ID, timestamp, title
- submitted PDF SHA256 (must match above)
- supplement uploaded YES/NO + supplement SHA256 if yes
- public submission root, Git tested SHA, Action run ID
