# Hack Hydra completion task list — 2026-08-19

Execution rule: work in batches; each batch ends with a concrete verification gate and FCO/FCG claim boundary. Do not promote a later batch if its load-bearing predecessor fails.

## Batch 0 — eligibility and scope

- [x] Verify official Aug-12 start rule from hackhydra.hydradb.com.
- [x] Confirm repository visible history begins after Aug 12.
- [x] Create conservative source-content eligibility policy.
- [ ] Audit submission tree for participant-authored pre-Aug-12 source and exclude/rewrite any ambiguous files.
- [ ] Add final third-party/template/dataset attribution table.

Gate: ELIGIBLE_SUBMISSION_SCOPE_ESTABLISHED.

## Batch 1 — datasets

Track 01
- [ ] Download exact revision of onyx-dot-app/EnterpriseRAG-Bench.
- [ ] Generate per-file SHA-256 manifest and pull receipt.
- [ ] Download exact revision of Salesforce/HERB.
- [ ] Generate per-file SHA-256 manifest and pull receipt.
- [ ] Keep HERB out of public redistribution pending license review.

Track 03
- [x] LongMemEval-S cleaned full500 hydrated and executed.
- [ ] Download exact revision of LongMemEval-V2 core tier.
- [ ] Generate per-file SHA-256 manifest and pull receipt.
- [ ] Download exact revision of BEAM core repository.
- [ ] Generate per-file SHA-256 manifest and pull receipt.
- [ ] Defer BEAM-10M until lower tier works.

Gate: DATASET_PULL_COMPLETE receipts exist for each executed lane.

## Batch 2 — Track 03 freeze

- [x] Pinned local HydraDB structural conformance PASS.
- [x] LongMemEval full500 A/B/C/D execution complete.
- [x] Preserve negative/neutral full500 finding: B/C/D have NO_POSITIVE_HIT_RATE_SIGNAL.
- [ ] Add full500 receipt/result/stats hashes to website evidence page.
- [ ] Execute one complete live normal → poison → antidote case and retain FCGDelta + Anticube receipt.
- [ ] Expose current-state trajectory and retrieval before/after/recovery in Judge Lab.
- [ ] Run browser E2E for Track 03 golden path.

Gate: TRACK03_JUDGE_GOLDEN_PATH_GREEN.

## Batch 3 — Track 01 HydraOntology

- [ ] Implement fresh post-Aug-12 Track 01 graph schema.
- [ ] Implement EnterpriseRAG/HERB adapters without copying pre-hackathon participant code.
- [ ] Ingest a bounded deterministic canary first.
- [ ] Run write/read/query round-trip in local HydraDB.
- [ ] Implement entity resolution, provenance, contradiction and supersession relations.
- [ ] Add Anticube edge-removal/reversal falsification case.
- [ ] Run a bounded EnterpriseRAG benchmark subset before full ingestion.
- [ ] Scale to full dataset only after canary gate passes.

Gate: TRACK01_REAL_DATA_CANARY_GREEN, then TRACK01_FULL only if executed.

## Batch 4 — Track 02 HydraBlast — choose A

Chosen official option: Track 02A Supply-chain blast radius.

- [ ] Implement fresh post-Aug-12 graph schema: Service, Repository, Lockfile, Package, PackageVersion, Maintainer, Publisher, Advisory, Vulnerability.
- [ ] Implement DEPENDS_ON, RESOLVED, USES, VERSION_OF, AFFECTS, FIXED_BY and related graph edges.
- [ ] Build a small real npm/dependency/advisory canary.
- [ ] Implement exact reverse dependency closure.
- [ ] Independently recompute expected affected set in deterministic Python.
- [ ] Compare HydraDB affected set with reference closure.
- [ ] Implement poison → patch/relock → recovery case.
- [ ] Implement Anticube edge removal/version shift counterfactual.
- [ ] Add Track 02 page and graph visualization.

Gate: TRACK02_BLAST_RADIUS_CANARY_GREEN.

## Batch 5 — COMPUTE template + FCO website

- [x] Exact user-supplied COMPUTE ZIP recovered and hashed.
- [ ] Port selected COMPUTE layout primitives into HydraDG rather than replacing graph logic.
- [ ] Attribute template in README.
- [ ] Make every primary section addressable by stable anchor/route.
- [ ] Make FCO/hash identifiers navigable to object/dependency/source context.
- [ ] Make terminology matrix links resolve to how-to + FCG graph query + upstream source.
- [ ] Make the site itself present its route as an FCG: source → evidence → transform → claim → artifact.
- [ ] Add explicit evidence-state badges; never use green to imply scientific verification when only availability is known.
- [ ] Verify desktop/mobile readability and accessibility.

Gate: WEBSITE_FCG_NAVIGATION_GREEN.

## Batch 6 — CI and link verification

- [ ] Typecheck.
- [ ] Production build.
- [ ] Static route smoke for /, /judge, /graph, /knowledge, /evidence, /eligibility and track pages.
- [ ] API fail-closed tests.
- [ ] Internal link crawler returns zero broken internal links.
- [ ] External required-link checks return expected status or documented redirect.
- [ ] Secret-pattern scan.
- [ ] GitHub Actions green on release head.

Gate: RELEASE_CI_GREEN.

## Batch 7 — Vercel

- [ ] Deploy submission-eligible branch/project.
- [ ] Confirm deployed /judge returns 200.
- [ ] Confirm all public static pages and navigation links.
- [ ] Confirm local-only live HydraDB functions are labelled LOCAL_ONLY and fail closed on Vercel.
- [ ] Check Vercel runtime errors after E2E requests.
- [ ] Browser-test mobile and desktop.

Gate: PUBLIC_WEB_GREEN.

## Batch 8 — public submission freeze

- [ ] Ensure public repository contains only eligible participant code plus attributed upstream/template/dependencies.
- [ ] Add open-source LICENSE appropriate for original project code and third-party notices.
- [ ] README: problem, architecture, HydraDB use, what is lost without HydraDB, datasets, results, negative results, setup, demo.
- [ ] Record exact release commit SHA.
- [ ] Hash release evidence artifacts.
- [ ] Do not claim author signature/Merkle/MMR unless operations are actually executed.
- [ ] Record team contribution boundaries.
- [ ] Prepare <=3-minute demo script/video checklist.
- [ ] Final submission link audit.

Gate: READY_TO_SUBMIT.

## Current known state

- Track 03 full500: EXECUTED, negative/neutral retrieval-ablation result retained.
- Local HydraDB: operational and structurally conformant under the bounded suite.
- Track 01 datasets: acquisition script exists; actual local pull receipt not yet observed.
- Track 03 LongMemEval-V2/BEAM: acquisition script exists; actual local pull receipt not yet observed.
- Track 02: design selected (A); implementation not yet established.
- Vercel production: older webapp deployment; Judge Lab release not yet deployed.
- Hosted HydraDB hydradg database: dashboard-attested active; hosted REST route mismatch unresolved and non-blocking for local submission demo.
