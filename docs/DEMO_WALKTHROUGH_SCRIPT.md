# HydraDG — Replacement Golden-Path Video Script

Target: **2:20–2:40**, maximum under 3 minutes.

Recording format: **1920×1080, 16:9, browser full-screen**.

Primary recording surface: the current pinned judge backup deployment at commit `60120da604f3bb6f30edfadc1d609018089beaef`.

Open the temporary judge-access URL once to establish the Vercel preview session:

`https://hydradg-4u209xn67-biobitworks.vercel.app/?_vercel_share=B5GJZ77ZGBvnnTPP3G6xalyCEs4vzYMT`

Temporary share access expires **2026-08-21 21:16 UTC / 14:16 PDT**. If it has expired, use the production site after redeployment or generate a fresh share URL for the same pinned preview.

Local fallback for recording: `http://127.0.0.1:3012/`.

## Recording rule

The video should show the executed evidence and current claim boundaries exactly as rendered. Do **not** claim hosted canonical parity while the BYOG readback is still indexing/pending. Do **not** call any Git commit signed unless a verified signature exists.

## Golden-path pacing

| Time | Screen | What to show |
|---|---|---|
| 0:00–0:15 | `/` | Problem and governed-context thesis |
| 0:15–0:55 | `/judge` | Reference → Poison → Antidote |
| 0:55–1:25 | `/track03` then `/eligibility` | Executed null result + K=5/10/100 matrix |
| 1:25–1:45 | `/atom-heatmap` | Local vs hosted FCO status; indexing/readback boundary |
| 1:45–2:10 | `/evidence` and `/knowledge` | FCO/FCG lineage, source, transformation, evidence, claim ceiling |
| 2:10–2:35 | `/eligibility` | Final governed chain, 0/9 Holm result, closing sentence |

## 1. Home — problem and thesis (0:00–0:15)

Action:
- Start at `/`.
- Keep the cursor near the Context Iceberg / governed state visualization.

Narration:

> Long-lived AI memory can silently overwrite changing facts and erase the evidence that came before. HydraDG uses HydraDB plus Fractal Custody Objects and Graphs to keep state changes, contradictions, provenance, and null results navigable instead of flattening them.

## 2. Judge Lab — Reference → Poison → Antidote (0:15–0:55)

Action:
- Open `/judge`.
- Load the reference state.
- Trigger the poison/mutation state.
- Apply the antidote/restoration state.
- Pause briefly on each color/state transition.

Narration:

> This is the golden path. We start from a governed reference state, introduce a controlled poison or contradictory state, and then apply an antidote. HydraDG changes the declared current state without deleting the divergent history. The graph retains supersession, contradiction, and provenance so we can identify where a bad dependency entered and whether recovery actually occurred.

If H, G*, ΔG*, or Cloud Drift values are visible, describe them as **state diagnostics**. Do not imply that lower G* means better retrieval accuracy.

## 3. Executed evidence — Track 03 and Daisy matrix (0:55–1:25)

Action:
- Open `/track03`.
- Show the LongMemEval execution scale and the historical K=5 comparison.
- Move to `/eligibility`.
- Show the cross-track K=5/10/100 Daisy Train matrix and the Holm result.

Narration:

> On LongMemEval, the graph was actually constructed and queried. The original K=5 ablation did not establish a positive graph-route Hit@5 advantage over the flat reference route. We then expanded the evaluation across three datasets, three model lanes, and K equals 5, 10, and 100. At the co-primary K=10 family, zero of nine model-versus-control tests were significant after Holm-Bonferroni correction. The claim ceiling is therefore NO_MODEL_BENEFIT_OBSERVED.

Optional, if clearly visible and time allows:

> The secondary depth analysis shows that retrieval can improve as K increases, with saturation or dilution at high depth. That is a depth observation, not a model-superiority result.

## 4. Atom heat map — local vs hosted state (1:25–1:45)

Action:
- Open `/atom-heatmap`.
- Show canonical FCO IDs and local/hosted status columns.
- Pause on the hosted status legend or representative rows.

Narration:

> This view compares the canonical local FCO identities with their hosted HydraDB projection. The upload has been accepted, but the current canonical 653-object and 1,692-edge readback is still bounded by indexing and parity verification. HydraDG displays that uncertainty instead of turning an accepted upload into a false parity claim.

Do not say `653/653` or `1692/1692` unless the current page and receipt actually establish those values at recording time.

## 5. Evidence and knowledge — trace one claim backward (1:45–2:10)

Action:
- Open `/evidence`.
- Select one FCO or evidence item if the UI supports it.
- Show hash/evidence class/claim ceiling.
- Open `/knowledge` and show source citations.

Narration:

> Every material result can resolve backward from the claim to derived evidence, transformation, and source custody object. SHA-256 gives content identity where recorded; it is not the same thing as a signature. G-star is an application-defined dimensionless information-state diagnostic, while Jensen-Shannon divergence is used separately for Cloud Drift.

## 6. Eligibility — closing claim boundary (2:10–2:35)

Action:
- Return to `/eligibility`.
- Show the governed chain from Atom → Seed → FCO → FCG → HydraDB → experiments → claim ceiling.
- Point to the `0 / 9` Holm result and `NO_MODEL_BENEFIT_OBSERVED`.

Closing sentence:

> HydraDG is not a leaderboard claim. It is a governed memory experiment: change state, find the first divergence, preserve custody, test recovery, and keep positive, null, negative, and abstaining evidence in the same graph.

## Before recording

- Confirm the preview or production site loads without an unexpected login prompt.
- Test `/judge`, `/track03`, `/eligibility`, `/atom-heatmap`, `/evidence`, and `/knowledge` immediately before recording.
- Close unrelated tabs and notifications.
- Use 100% browser zoom unless labels are unreadable.
- Do not show API keys, `.env` files, terminal secrets, or Vercel environment values.
- Keep the repository visible only if useful; the video should prioritize the product and executed evidence.
- After upload, replace `PENDING_USER_RECORDING_AND_UPLOAD` in `SUBMISSION.md` and `docs/RESUBMISSION_COPY_20260820.md` with the actual video URL only after verifying it opens publicly.