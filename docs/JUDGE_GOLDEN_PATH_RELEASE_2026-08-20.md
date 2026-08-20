# HydraDG Judge Golden Path Release — 2026-08-20

## Purpose

This successor release improves judge navigation, accessibility, model transparency, cryptographic-status transparency, citations, and licensing presentation without changing historical scientific receipts or promoting claims beyond executed evidence.

Release custody FCO:

`fco:527736a0e8da9cee769201969f67c455b79dce882b08467a60077c69deb287c2`

Direct human-instruction SHA-256:

`338ef7159f8b83b50028d0812e43c891194b01fdf3be161b311d1cf3255ed021`

Base Git SHA:

`73c20c13da27c2410007347eb68ded6180abbeb8`

Claim ceiling:

`WEBSITE_JUDGE_UX_AND_CUSTODY_STATUS_DOCUMENTATION_ONLY`

## Golden path

The persistent judge path is:

```text
HOME
→ CHANGE STATE
→ READ RESULT
→ TRACE FCO
→ MODELS USED
→ VERIFY CUSTODY
→ EVIDENCE
```

Gold is reserved for prescribed judge navigation and linked callouts. It does not encode scientific correctness, positive results, pass/fail state, retrieval accuracy, G*, ΔG*, or Cloud Drift.

## Navigation and accessibility changes

- `HydraDG` in the persistent header links to the home MVP (`/`).
- Primary navigation is available on every dynamic route through the root layout.
- An `All pages` menu exposes the complete judge/deep-dive route set.
- A persistent linked golden-path rail appears on every dynamic route.
- The static fallback carries live-route links plus local in-document golden-path anchors.
- The static fallback no longer removes all navigation on mobile.
- A skip link targets `#main-content`.
- Keyboard focus uses a visible high-contrast focus ring.
- Navigation controls have minimum interaction heights.
- `prefers-reduced-motion` disables nonessential smooth/animated behavior.
- Long identifiers use wrapping rules rather than overflowing their containers.
- Global footer content is supplied by the root layout rather than relying on page-local footers.

The gold foreground selected for the judge path is `#e7c86d` on the near-black `#08090b` surface. A deterministic local contrast calculation gives approximately 12.2:1 for that pair. This is a color-pair calculation, not a claim that the complete site has passed WCAG, axe, or Lighthouse accessibility certification.

## Cryptographic status

### Current HydraDG project FCO/FCG

- Object identity: SHA-256 content addressing.
- Project Ed25519 signature state: `PENDING_EXTERNAL_PRIVATE_KEY_OPERATION` / not presently established for every current project object.
- Project Merkle/MMR state: `NOT_PROJECT_COMMITTED`.
- Authentic private-key policy: external secret; never put it in Git, HydraDB, browser JavaScript, HTML, CSS, public environment variables, or image pixels.

A SHA-256 object identity is not a digital signature. A publication signature is not inherited by a later project FCO.

### Signed FCO publication lineage

For the FCO v1 publication lineage, the retained public-key SHA-256 fingerprint is:

`f496a067808026d45fbbad785bf83c6acd66429c2d257d246cc103c6d7ff460d`

Retained signed-FCG-root prefix:

`741d12de…`

Scope: publication FCG only. This does not establish that the current HydraDG project graph is signed.

## Model disclosure

### Primary submitted Track 03 experiment

LongMemEval-S full500 K=5 used:

```text
extractor=heuristic
model=null
ollarma_url=null
```

Therefore the primary submitted retrieval evidence does not depend on a language model.

### Local diagnostic lane

Approved local reference families used for post-freeze probabilistic diagnosis/prospective prediction:

- `qwen2.5:7b`
- `qwen2.5-coder:7b`

The site links the corresponding upstream Hugging Face reference cards:

- `Qwen/Qwen2.5-7B-Instruct`
- `Qwen/Qwen2.5-Coder-7B-Instruct`

A Hugging Face family/card URL does not establish the exact Ollama execution digest. A claimed run must retain the actual local tag/digest, prompt, configuration, raw response, parsed response, and timing/receipt evidence.

### Vithia / Pythia lane

The site links:

- `biobitworks/fco-vithia-fmo-076`
- `EleutherAI/pythia-14m`

The connected Hugging Face metadata reports the Biobitworks repository as gated and tagged for FCO/FCG, Vithia, custody and provenance. The current EleutherAI card identifies a 14.1M GPT-NeoX model and notes a 2026-02-27 correction: the `pythia-14m` URL now refers to the standard-Pile model, while the prior deduplicated model moved to `EleutherAI/pythia-14m-deduped`.

This is a separate small-model/training evidence lane; it is not the model driving the primary Track 03 retrieval result.

### Frontier comparison

`FUTURE_FRONTIER_COMPARISON_NOT_RUN`

No controlled local-vs-frontier superiority comparison has been established under a common frozen dataset, context, prompt, token budget, provider/model snapshot, sampling configuration and scoring protocol. Synthetic multi-model design rows are not model-execution evidence.

## Judge lenses

Primary submission: Track 03 — Memory + Context Retrieval.

The judge page also exposes the architecture through the other Hack Hydra graph lenses:

- Track 01: enterprise context + ontology; core data is downloaded/hashed but real-data ingestion/evaluation remains pending.
- Track 02: repository/dependency blast radius; synthetic structural canary remains bounded and real-data evaluation remains pending.
- Track 03: full500 run executed; null/negative retrieval outcome retained.

The official Hack Hydra judging criteria presented in the UI are:

1. Technical execution.
2. Use of HydraDB and graph-native approaches.
3. Product completeness and usability.
4. Quality of results.
5. Originality.

Best Use of HydraDB remains a separate judging lens.

## Current publication citations presented in the site

Externally verified FCO publication records:

- FCO v1 — https://doi.org/10.5281/zenodo.21210575
- FCO v3 — https://doi.org/10.5281/zenodo.21420906

Current project-supplied August 2026 publication links:

- FCO v4/v5 + Vithia companion evidence — https://doi.org/10.5281/zenodo.21829929
- Self/Non-Self × Safe/Unsafe classification — https://doi.org/10.5281/zenodo.21830287
- Shadow Dogma — https://doi.org/10.5281/zenodo.21830361
- XenoDisorder — https://doi.org/10.5281/zenodo.21830386

The four August links are presented as current project-supplied citation identities unless separately externally verified in the release runtime.

## Licensing footer invariant

Every dynamic page inherits the global footer. The static fallback carries the same licensing boundary:

```text
HydraDG software / website / scripts
→ Apache License 2.0

Designated FCO/FCG research publications and designated Byron P. Lee / Biobitworks research content
→ CC BY-NC-ND 4.0

Earlier FCO/FCG CC BY 4.0 metadata
→ SUPERSEDED_METADATA_ERROR
→ historical custody evidence only

third-party datasets, models, papers and APIs
→ upstream rights
```

## Release verification required before production claim

This document does not itself establish a successful production deployment. The successor SHA must separately pass the available typecheck/build/judge/release/security gates. After deployment, the production URL and release API must be inspected on that exact deployed SHA.

Do not call this release project-signed, sealed, Merkle-committed, accessibility-certified, frontier-superior, or expanded-FCG-parity-verified unless the corresponding operation and evidence are subsequently produced.
