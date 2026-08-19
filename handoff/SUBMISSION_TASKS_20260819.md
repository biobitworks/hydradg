# Hack Hydra completion task list — 2026-08-19

Execution rule: work in batches; each batch ends with a concrete verification gate and FCO/FCG claim boundary. Do not promote a later batch if its load-bearing predecessor fails.

## Batch 0 — eligibility and scope

- [x] Verify official Aug-12 start rule from hackhydra.hydradb.com.
- [x] Confirm repository-visible history begins after Aug 12.
- [x] Create conservative source-content eligibility policy.
- [ ] Final content-origin audit of the public allowlist; exclude/rewrite any ambiguous participant-authored pre-Aug-12 source.
- [x] Add third-party/template/dataset attribution table.
- [x] Define fresh-history public export instead of making the broad private history public.
- [x] Add fail-closed public-export builder with explicit allowlist, size gate, Gitleaks gate and one-commit history gate.

Gate: `ELIGIBLE_SUBMISSION_SCOPE_ESTABLISHED` after final content-origin review.

## Batch 1 — datasets

Track 01
- [ ] Download exact revision of `onyx-dot-app/EnterpriseRAG-Bench`.
- [ ] Generate per-file SHA-256 manifest and pull receipt.
- [ ] Download exact revision of `Salesforce/HERB`.
- [ ] Generate per-file SHA-256 manifest and pull receipt.
- [x] Keep HERB out of public redistribution by default; CC-BY-NC-4.0 recorded.

Track 03
- [x] LongMemEval-S cleaned full500 hydrated and executed.
- [ ] Download exact revision of LongMemEval-V2 core tier.
- [ ] Generate per-file SHA-256 manifest and pull receipt.
- [ ] Download exact revision of BEAM core repository.
- [ ] Generate per-file SHA-256 manifest and pull receipt.
- [x] Defer BEAM-10M until lower tier is useful.

Implementation
- [x] Add one acquisition script for all Track 01 + Track 03 core datasets with exact HF revision resolution and SHA-256 manifests.
- [x] Wire the acquisition step into the one-command MagicStudio release batch runner.

Gate: `DATASET_PULL_COMPLETE` receipts exist for each executed lane.

## Batch 2 — Track 03 freeze

- [x] Pinned local HydraDB structural conformance PASS.
- [x] LongMemEval full500 A/B/C/D execution complete.
- [x] Preserve negative/neutral full500 finding: B/C/D have `NO_POSITIVE_HIT_RATE_SIGNAL`.
- [x] Add full500 receipt/result/stats hashes to website evidence page.
- [x] Implement release writer for original/live injected Fact targets.
- [x] Fix antidote path so poison vertex can be targeted as live HydraDB state.
- [x] Add executable normal → poison → antidote golden-path receipt generator.
- [ ] Execute one complete fresh release golden path and retain receipt.
- [x] Expose current-state trajectory/retrieval controls in Judge Lab.
- [ ] Run deployed/browser E2E for Track 03 golden path.

Gate: `TRACK03_JUDGE_GOLDEN_PATH_GREEN` after fresh execution + browser verification.

## Batch 3 — Track 01 HydraOntology

- [x] Implement fresh post-Aug-12 Track 01 graph canary schema: SourceDocument, EntityMention, CanonicalEntity.
- [x] Implement deterministic expected-set oracle for entity-resolution evidence.
- [x] Implement HydraDB MENTIONS / RESOLVES_TO canary and alias split→merge state sequence.
- [x] Add Track 01 page and claim boundaries.
- [x] Add EnterpriseRAG/HERB acquisition adapters without embedding dataset bytes in Git.
- [ ] Execute local write/read/query canary and retain receipt.
- [ ] Implement bounded real EnterpriseRAG/HERB ingestion adapter after pull receipts exist.
- [ ] Add real-data contradiction/supersession/entity-resolution case.
- [ ] Run bounded EnterpriseRAG benchmark subset before any full ingestion.
- [ ] Scale only if bounded real-data gate is useful.

Gate: `TRACK01_SYNTHETIC_CANARY_GREEN`, then `TRACK01_REAL_DATA_CANARY_GREEN` only if executed.

## Batch 4 — Track 02 HydraBlast — option A

Chosen official option: **Track 02A Supply-chain blast radius**.

- [x] Implement fresh post-Aug-12 structural canary nodes: Service, Lockfile, PackageVersion, Advisory.
- [x] Implement `USES`, `RESOLVED`, `DEPENDS_ON`, `AFFECTS` edges for the bounded canary.
- [x] Implement exact reverse dependency closure in deterministic Python.
- [x] Implement HydraDB reverse one-hop iterative traversal compatible with the pinned runtime.
- [x] Compare HydraDB affected set with deterministic reference closure in code.
- [x] Implement reference → poison → partial repair → full repair sequence with expected exposure counts 0→2→1→0.
- [x] Add Track 02 page and graph explanation.
- [ ] Execute the fresh synthetic canary locally and retain receipt.
- [ ] Build a small real npm/deps.dev/advisory/lockfile canary.
- [ ] Expand real schema with Repository, Package, Maintainer/Publisher, Vulnerability and fixed-version relations only as required by the real canary.
- [ ] Implement real-data edge-removal/version-shift counterfactual.

Gate: `TRACK02_SYNTHETIC_CANARY_GREEN`, then `TRACK02_REAL_BLAST_RADIUS_CANARY_GREEN` if real evidence is executed.

## Batch 5 — COMPUTE template + FCO website

- [x] Exact user-supplied COMPUTE ZIP recovered and hashed.
- [x] Correct archive inventory to 102 files after direct extraction; no standalone LICENSE observed.
- [x] Attribute template in third-party notices and eligibility audit.
- [x] Port selected COMPUTE presentation grammar into HydraDG without replacing graph logic.
- [x] Make every primary section addressable by stable route.
- [x] Make FCO/hash identifiers navigable to object/dependency/source context.
- [x] Make terminology matrix links resolve to how-to + FCG graph query + upstream source.
- [x] Represent the site itself as an application-level FCG with `/api/site-fcg` and content-addressed section objects.
- [x] Add explicit evidence-state wording that separates PASS / negative / implemented / pending / external-blocked.
- [x] Add internal-link crawler and dynamic FCO route check.
- [ ] Execute mobile/desktop browser verification on the release deployment.

Gate: `WEBSITE_FCG_NAVIGATION_GREEN` after executing the release web/link/browser gates.

## Batch 6 — CI and link verification

- [x] Add one-command MagicStudio release runner for static checks → local HydraDB → datasets → Track 01/02 → Track 03 → web → links → Gitleaks → receipt.
- [ ] Execute current release-head typecheck.
- [ ] Execute current release-head production build.
- [ ] Execute static route smoke for `/`, `/judge`, `/graph`, `/knowledge`, `/evidence`, `/eligibility`, `/track01`, `/track02`, `/track03`.
- [x] Internal link crawler implemented.
- [ ] Internal link crawler returns zero broken links on the current release build.
- [ ] External required-link audit or documented browser-only restriction.
- [ ] Execute current release secret scan.
- [ ] GitHub Actions green on release head.

GitHub Actions blocker: current release-head jobs end with `failure` but expose no executed steps/logs/artifacts; rerun reproduced the zero-step condition. Current classification is `GITHUB_ACTIONS_RUNNER_START_FAILURE / CAUSE_NOT_ESTABLISHED`, not an application-test failure or pass.

Gate: `LOCAL_RELEASE_EXECUTION_GREEN` can be established independently; `GITHUB_ACTIONS_GREEN` remains a separate external gate.

## Batch 7 — Vercel

- [ ] Deploy the submission-eligible fresh public/export project.
- [ ] Confirm deployed `/judge` returns 200.
- [ ] Confirm all public static pages and navigation links.
- [ ] Confirm local-only live HydraDB functions are labelled LOCAL_ONLY and fail closed on Vercel.
- [ ] Check Vercel runtime errors after E2E requests.
- [ ] Browser-test mobile and desktop.

Current Vercel state: existing production is an older branch; release deployment has not occurred. The connected deploy wrapper currently rejects invocation because its exposed schema omits backend-required deployment arguments; classify as `VERCEL_DEPLOY_CONNECTOR_SCHEMA_BLOCKER`, not application failure.

Gate: `PUBLIC_WEB_GREEN`.

## Batch 8 — public submission freeze

- [x] Define a fresh-history public repository export surface rather than publishing the broad private history.
- [x] Add open-source MIT LICENSE for original Hack Hydra code and third-party notices.
- [x] README covers problem, architecture, HydraDB role, datasets, negative Track 03 result, setup and demo routes.
- [ ] Run `build_hackhydra_public_export.sh` after local batch receipt is green.
- [ ] Final human content-origin review of export tree.
- [ ] Create/push new public GitHub repository from the one-commit export.
- [ ] Record exact public release commit SHA and export manifest SHA-256.
- [ ] Verify public repo clone/setup from a clean location.
- [ ] Record team contribution boundaries.
- [ ] Prepare and publish <=3-minute demo video.
- [ ] Final public link audit.
- [ ] Complete submission form by Aug 20, 2026 11:59 PM PT.

Do not claim author signature/Merkle/MMR unless those operations are actually executed.

Gate: `READY_TO_SUBMIT`.

## Current known state

- Official build-window rule: VERIFIED from current Hack Hydra site.
- Track 03 full500: EXECUTED; negative/neutral retrieval-ablation result retained.
- Local HydraDB: previously operational and structurally conformant under bounded suite.
- Track 03 fresh live release golden path: IMPLEMENTED; execution receipt pending.
- Track 01: synthetic canary IMPLEMENTED; real dataset pull/execution pending.
- Track 02A HydraBlast: synthetic canary IMPLEMENTED; real package/advisory evidence pending.
- EnterpriseRAG-Bench/HERB/LME-V2/BEAM: upstream metadata confirmed; no admitted local pull receipts yet.
- Website-as-FCG: IMPLEMENTED; current release build/browser execution pending.
- GitHub Actions current release: zero-step runner-start blocker, cause unresolved.
- Vercel production: older webapp deployment; release deployment pending and connector deploy action currently unusable.
- Hosted HydraDB `hydradg`: dashboard-attested active; hosted REST route mismatch unresolved and non-blocking for the local primary demo.
- Public submission repo: must be a fresh-history export; existing broad private repository should not simply be made public.
