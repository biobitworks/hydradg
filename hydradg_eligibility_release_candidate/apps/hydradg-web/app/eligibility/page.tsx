import Link from "next/link";

import {
  eligibilityClaimCeiling,
  eligibilityProofDoc,
  hackHydraEligibility,
} from "@/lib/eligibility";

const LIVE_MATRIX = [
  ["Live Vercel hosted HydraDB", "DEGRADED / NOT_CONFIGURED", "The current deployment cannot run a live server-side HydraDB canary until server-only endpoint/token/namespace configuration is present and verified."],
  ["Track 03 local HydraDB evidence", "EXECUTED", "LongMemEval-S full500 graph/evaluation evidence is retained: 23,867 sessions, 4,776 entities, 3,506 facts, 470 scored cases, 30 abstentions."],
  ["Historical hosted parity", "PASS · BOUNDED HISTORICAL SCOPE", "36 canonical FCOs and 24 edges matched in the recorded historical scope. This does not establish parity for the expanded current FCG."],
  ["Expanded hosted parity", "NOT_ESTABLISHED", "A non-200 hosted readback must fail closed. Local expected counts cannot substitute for hosted observations."],
  ["Expanded public FCG repro", "PROCEDURE_PRESENT / RECEIPT_PENDING", "The repository contains a real fail-closed FCG→HydraDB importer; a fresh expanded import/readback receipt is still required."],
  ["20.82M-scale local writeback", "NOT_ESTABLISHED", "The current legacy generator derives intended counts but does not perform HydraDB network writes."],
  ["SeedGraph 653/1,692 bundle", "CANDIDATE_HASHED / ADMISSION_NOT_ESTABLISHED", "The current receipt hashes/counts the bundle but does not invoke a SeedGraph admission operation."],
] as const;

const TRACKS = [
  ["Track 03 · Memory + context", "STRONGEST EXECUTED FIT", "LongMemEval-S full500; chronology, supersession, contradiction, abstention; K5/K10 depth ablation.", "Primary award case"],
  ["Track 01 · Enterprise ontology", "STRONG ARCHITECTURE FIT / REAL BENCHMARK PENDING", "EnterpriseRAG-Bench + HERB source lanes; identity/provenance/contradiction design; real full-corpus ontology evaluation pending.", "Future / distinct submission lane"],
  ["Track 02 · Dependency/code graph", "STRUCTURAL CANARY ONLY / REAL SNAPSHOT PENDING", "Reference 0 → poison 2 → partial repair 1 → full repair 0; real npm/PyPI + OSV/GHSA evaluation pending.", "Future / distinct submission lane"],
  ["Best Use of HydraDB", "STRONGEST CROSS-CUTTING CASE", "Content identity + typed graph context + temporal traversal + deterministic failure receipts + model-agnostic retrieval layers.", "Special-award case"],
] as const;

const TERMINOLOGY = [
  ["Semantic / vector retrieval", "Hybrid retrieval / semantic candidate ranking", "Similarity is a candidate signal; exact SHA identity and graph custody remain separate.", "PARTIAL / EXECUTED IN RETRIEVAL LANES"],
  ["Knowledge graph / ontology", "Typed graph nodes + relationships", "FCO nodes + FCG typed provenance, contradiction, supersession, state and release edges.", "IMPLEMENTED"],
  ["Entity resolution", "Context graph / identity resolution", "Aliases or occurrences can resolve to one canonical content/entity identity while retaining source edges.", "TRACK01 DESIGN; REAL BENCHMARK PENDING"],
  ["Temporal/versioned graph", "Versioned temporal context", "SUPERSEDED_BY, contradiction, chronology, state snapshots and historical/current separation.", "EXECUTED IN TRACK03 / SYNTHETIC STATE FIXTURE"],
  ["Graph traversal", "OpenCypher/path traversal", "Memory evidence paths, provenance paths, and dependency reverse-closure canaries.", "TRACK03 EXECUTED; TRACK02 REAL DATA PENDING"],
  ["Abstention / uncertainty", "Recognize absent/insufficient context", "Explicit abstentions and unexplained-candidate states are retained instead of forced answers.", "30 TRACK03 + 12 CONTEXT-ENTROPY ABSTENTIONS"],
  ["Dedup / canonicalization", "Entity/context consolidation", "SHA-256 exact identity plus many spatiotemporal/context pointers.", "DETERMINISTIC COUNT ACCOUNTING; BYTE SAVINGS PENDING"],
  ["Model-agnostic context", "Context layer independent of one LLM", "No-model deterministic baseline; optional Qwen and Vithia lanes are separated from canonical custody.", "IMPLEMENTED BOUNDARY; MODEL BENEFIT NOT ESTABLISHED"],
  ["Deterministic replay", "Reproducible graph/query workflow", "Canonical input hash → calculation contract hash → receipt hash; HydraDB importer readback gate.", "IMPLEMENTED; FRESH EXPANDED REPRO RECEIPT PENDING"],
  ["Context-state diagnostics", "Not a standard database metric", "Information-State Heat Layer: H, Hnorm, G*, ΔG*, JSD Cloud Drift and TV restoration.", "NOVEL SYNTHETIC DIAGNOSTIC / BACKEND-AGNOSTIC MATH"],
] as const;

const K_ROWS = [
  ["K=5", "A", "0.96383", "0.90660", "0.63787", "≈453/470 Hit"],
  ["K=5", "B", "0.94681", "0.85383", "—", "≈445/470 Hit"],
  ["K=5", "C", "0.94681", "0.85259", "—", "≈445/470 Hit"],
  ["K=5", "D", "0.94468", "0.84603", "0.63787", "≈444/470 Hit"],
  ["K=10", "A", "0.97872", "0.94535", "0.51511", "≈460/470 Hit"],
  ["K=10", "D", "0.97021", "0.92273", "0.51511", "≈456/470 Hit"],
] as const;

const HEAT = [
  ["T0 reference", "[0.88, 0.08, 0.04]", "0.08", "0.639556", "0.403515", "-0.061230", "0", "0", "0"],
  ["T1 mutation", "[0.18, 0.72, 0.10]", "0.82", "1.118731", "0.705841", "0.572956", "0.634186", "40.362864", "0.70"],
  ["T2 restoration", "[0.76, 0.14, 0.10]", "0.20", "1.030209", "0.649989", "-0.027496", "-0.600452", "1.872865", "0.12"],
] as const;

const EXPERIMENTS = [
  ["LongMemEval-S full500 K=5", "EXECUTED", "500 cases; 470 scored; 30 abstentions; B/C/D did not establish positive Hit@5 advantage over A.", "LONGMEMEVAL_FULL500_RETRIEVAL_ABLATION_ONLY_NOT_END_TO_END_QA"],
  ["K=5 → K=10 depth ablation", "RETAINED LOCAL EXECUTION", "K10 improved Hit@K/Recall@K; evidence-path coverage density declined; RAW=SeedGraph at fixed K.", "K_DEPTH_EFFECT_ONLY_NOT_MODEL_BENEFIT"],
  ["Context vs Entropy", "HYDRADB READBACK SUCCESS", "18,567 raw findings; 18,555 classified; 12 abstentions; 99.9354% coverage.", "CONTEXT_AWARE_CLASSIFICATION_ONLY"],
  ["Track 02 0→2→1→0 canary", "SYNTHETIC STRUCTURAL CANARY", "Independent closure-vs-HydraDB design; no real npm exposure claim.", "SYNTHETIC_TRACK02_STRUCTURAL_CANARY_ONLY"],
  ["Track 01 ontology", "DATA/HASH + DESIGN", "Source lanes and ontology design present; real full-corpus ingestion/evaluation pending.", "TRACK01_REAL_BENCHMARK_NOT_ESTABLISHED"],
  ["100-cell model×dataset matrix", "SYNTHETIC DESIGN", "100 cells are a preregistration/design surface, not model executions.", "SYNTHETIC_100_CELL_MULTI_MODEL_DATASET_MATRIX_DESIGN_ONLY_NOT_MODEL_EXECUTION"],
  ["20.82M local HydraDB writeback", "NOT_ESTABLISHED", "Legacy generator counts intended nodes/relations but does not send HydraDB writes.", "DO_NOT_PROMOTE"],
  ["Expanded hosted parity", "NOT_ESTABLISHED", "Historical 36/24 parity cannot inherit into the expanded graph; non-200 must fail closed.", "ROOT_SCOPE_RECONCILIATION_REQUIRED"],
] as const;

const MODELS = [
  ["No model", "PRIMARY DETERMINISTIC BASELINE", "Heuristic extraction/retrieval; primary K5/K10 depth comparison.", "EXECUTED"],
  ["Qwen 2.5 local", "OPTIONAL CONTROLLED MODEL LANE", "qwen2.5-coder:7b / qwen2.5:7b only after exact Ollama digest, tokenizer, prompt and output receipt are bound.", "MODEL BENEFIT NOT ESTABLISHED"],
  ["Vithia companion", "NOVEL PROJECT MODEL LANE", "Use exact `biobitworks/fco-vithia-fmo-076` and actual Pythia-14M lineage; do not relabel as 7B without evidence.", "SUPPLEMENTARY / FUTURE CONTROLLED ABLATION"],
  ["Frontier model", "OPTIONAL / NOT REQUIRED", "Only compare under identical frozen evidence, prompt, context budget, provider snapshot and scoring.", "NOT RUN"],
] as const;

const GAPS = [
  ["Live hosted HydraDB canary", "Current Vercel deployment lacks verified server-side hosted configuration.", "Configure server-only endpoint/token/namespace; call /api/graph/status; retain readback receipt.", "NOT_ESTABLISHED"],
  ["Expanded hosted parity", "Historical 36/24 scope only; legacy fallback verifier is unsafe.", "Fail on non-200; compare actual IDs, edges and hashes; bind root scope.", "NOT_ESTABLISHED"],
  ["Full local writeback", "Legacy receipt is derived-count only.", "Use real HydraDB POST/Bolt writes + count/root readback.", "NOT_ESTABLISHED"],
  ["SeedGraph admission", "Candidate bundle is hashed but generator does not call SeedGraph.", "Execute SeedGraph admission/readback and retain operation receipt.", "NOT_ESTABLISHED"],
  ["Track 01", "Real full-corpus ontology benchmark missing.", "Atomize real frozen sources; evaluate entity resolution, contradiction, multi-hop, abstention.", "PENDING"],
  ["Track 02", "Real npm/PyPI graph benchmark missing.", "Freeze registry/advisory snapshot; compare HydraDB closure with independent graph oracle.", "PENDING"],
  ["Model benefit", "Primary matrix used no LLM.", "Heuristic vs Qwen vs Vithia extraction with K fixed and exact model receipts.", "NOT_ESTABLISHED"],
  ["Download-byte savings", "Full acquisition byte manifest not yet frozen.", "Run build_download_byte_manifest.py on real acquired roots, then calculator --verify.", "NOT_MEASURED"],
  ["Measured time/energy", "Only theoretical FLOP/Wh scenario exists.", "Instrument tokens/s, latency and electrical energy; retain raw measurements.", "NOT_MEASURED"],
  ["Signing / Merkle", "Project graph is hashed but current project-level signature/MMR commitment is absent.", "External authorized Ed25519 operation + verification receipt; explicit commitment operation if desired.", "NOT_SIGNED / NOT_MERKLE_COMMITTED"],
] as const;

export default function EligibilityPage() {
  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow goldText">Golden path · Final step · Eligibility + award case</p>
          <h1>What worked, what failed, what HydraDB changed, and what remains to prove.</h1>
          <p className="lede">
            HydraDG is strongest when the failures stay visible. This page separates live-deployment
            degradation from executed HydraDB evidence, maps the work to the official tracks, shows
            the deterministic math, and keeps every unexecuted promotion gate red.
          </p>
          <div className="actions">
            <Link className="primary goldenCta" href="/best-use">Why HydraDB + math</Link>
            <Link className="secondary" href="/evidence">Evidence ledger</Link>
            <Link className="secondary" href="/track03">Track 03 result</Link>
            <a className="secondary" href={eligibilityProofDoc}>Eligibility custody doc ↗</a>
          </div>
        </div>
        <div className="heroStatus">
          <span className="pill pillGood">HYDRADB USE ESTABLISHED IN BOUNDED EXECUTED LANES</span>
          <span className="pill pillWarn">LIVE HOSTED CANARY DEGRADED</span>
          <span className="pill pillWarn">EXPANDED PARITY PENDING</span>
          <span className="pill pillMuted">FAILURE DATA RETAINED</span>
        </div>
      </header>

      <section className="computeSection" id="live-vs-local">
        <span className="sectionNumber goldenSectionLabel">01 / LIVE PRODUCTION VS LOCAL / HISTORICAL</span>
        <h2 className="displayTitle">A failed live canary does not erase executed HydraDB work.</h2>
        <div className="tableWrap">
          <table>
            <thead><tr><th>Lane</th><th>State</th><th>Meaning</th></tr></thead>
            <tbody>{LIVE_MATRIX.map(([lane,state,meaning]) => <tr key={lane}><td>{lane}</td><td className="mono small">{state}</td><td>{meaning}</td></tr>)}</tbody>
          </table>
        </div>
        <p className="small muted note">
          Promotion rule: a server-side deployment failure is reported as deployment degradation.
          It must not be rewritten as “HydraDB was never used,” and prior bounded evidence must not be
          rewritten as proof of the current expanded hosted graph.
        </p>
      </section>

      <section className="computeSection" id="track-fit">
        <span className="sectionNumber goldenSectionLabel">02 / TRACK + AWARD FIT</span>
        <h2 className="displayTitle">Track 03 is the strongest executed fit; Best Use is the strongest cross-cutting case.</h2>
        <div className="tableWrap">
          <table>
            <thead><tr><th>Award/track</th><th>Current fit</th><th>Evidence</th><th>Position</th></tr></thead>
            <tbody>{TRACKS.map(([track,fit,evidence,position]) => <tr key={track}><td>{track}</td><td>{fit}</td><td>{evidence}</td><td>{position}</td></tr>)}</tbody>
          </table>
        </div>
        <p className="small muted note">
          Hack Hydra permits multiple tracks only for meaningfully distinct submissions. This page
          is a fit/gap analysis; it does not relabel one HydraDG build as three separate eligible submissions.
        </p>
      </section>

      <section className="computeSection" id="terminology">
        <span className="sectionNumber goldenSectionLabel">03 / INDUSTRY TERMINOLOGY MATRIX</span>
        <h2 className="displayTitle">Standard context-engineering concepts, HydraDB primitives, HydraDG extensions.</h2>
        <div className="tableWrap">
          <table>
            <thead><tr><th>Industry standard</th><th>HydraDB capability</th><th>HydraDG integration</th><th>Evidence state</th></tr></thead>
            <tbody>{TERMINOLOGY.map(([a,b,c,d]) => <tr key={a}><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>)}</tbody>
          </table>
        </div>
      </section>

      <section className="computeSection" id="experiments">
        <span className="sectionNumber goldenSectionLabel">04 / EXECUTED · NULL · SYNTHETIC · FUTURE</span>
        <h2 className="displayTitle">A PASS label is not enough; the operation underneath decides the evidence class.</h2>
        <div className="tableWrap">
          <table>
            <thead><tr><th>Experiment</th><th>State</th><th>Result</th><th>Claim ceiling</th></tr></thead>
            <tbody>{EXPERIMENTS.map(([a,b,c,d]) => <tr key={a}><td>{a}</td><td>{b}</td><td>{c}</td><td className="mono small">{d}</td></tr>)}</tbody>
          </table>
        </div>
      </section>

      <section className="computeSection" id="k-depth">
        <span className="sectionNumber goldenSectionLabel">05 / K=5 VS K=10</span>
        <h2 className="displayTitle">K is a retrieval/context budget, not a model score.</h2>
        <p className="sectionLead">
          The frozen Track 03 set contains 500 cases. 470 are retrieval-scored and 30 are abstentions.
          K=5 tests a tight five-item context budget. K=10 tests whether useful evidence was ranked just below
          that cutoff. The primary matrix used no language model.
        </p>
        <div className="tableWrap">
          <table>
            <thead><tr><th>Depth</th><th>Method</th><th>Hit@K</th><th>Recall@K</th><th>Evidence-path coverage</th><th>Approx hit count</th></tr></thead>
            <tbody>{K_ROWS.map((row) => <tr key={`${row[0]}-${row[1]}`}>{row.map((v,i) => <td key={i}>{v}</td>)}</tr>)}</tbody>
          </table>
        </div>
        <div className="grid twoCol" style={{marginTop:24}}>
          <article className="panel"><p className="eyebrow">Depth effect</p><h2>K10 improved retrieval metrics.</h2><p>A Hit +1.489 pp · A Recall +3.875 pp · D Hit +2.553 pp · D Recall +7.670 pp.</p></article>
          <article className="panel"><p className="eyebrow">Trade-off / null</p><h2>Graph representation was not the win.</h2><p>Evidence-path coverage fell 12.276 pp, and RAW equaled SeedGraph at fixed K in the retained matrix. Model benefit is not established.</p></article>
        </div>
        <p className="mono small">K_DEPTH_EFFECT_OBSERVED · RAW_EQUALS_SEEDGRAPH_AT_FIXED_K · MODEL_BENEFIT_NOT_ESTABLISHED · NOT_END_TO_END_QA</p>
      </section>

      <section className="computeSection" id="heat-layer">
        <span className="sectionNumber goldenSectionLabel">06 / INFORMATION-STATE HEAT LAYER</span>
        <h2 className="displayTitle">A backend-agnostic state diagnostic over a preregistered distribution.</h2>
        <div className="panel goldenPanel">
          <p className="mono">H(P) = −Σ pᵢ log₂(pᵢ)</p>
          <p className="mono">Hnorm(P) = H(P) / log₂(n)</p>
          <p className="mono">G* = U* − 0.35 × Hnorm</p>
          <p className="mono">ΔG*(t) = G*(t) − G*(t−1)</p>
          <p className="mono">Cloud Drift = 100 × JSD_base2(Pₜ || P_reference)</p>
          <p className="mono">TV(Pₜ,P_ref) = ½ Σ |pₜᵢ − p_refᵢ|</p>
        </div>
        <div className="tableWrap" style={{marginTop:24}}>
          <table>
            <thead><tr><th>State</th><th>P</th><th>U*</th><th>H bits</th><th>Hnorm</th><th>G*</th><th>ΔG*</th><th>Cloud Drift</th><th>TV</th></tr></thead>
            <tbody>{HEAT.map((row) => <tr key={row[0]}>{row.map((v,i) => <td key={i}>{v}</td>)}</tr>)}</tbody>
          </table>
        </div>
        <p className="small muted note">
          T2 restoration gain = 0.58 TV units. These T0–T2 values are a deterministic synthetic fixture.
          G* is dimensionless and is not thermodynamic Gibbs free energy. The equations can run over any
          backend if the state categories and U* rule are fixed before evaluation; HydraDB supplies the
          versioned graph state in this hackathon implementation.
        </p>
      </section>

      <section className="computeSection" id="scale">
        <span className="sectionNumber goldenSectionLabel">07 / DATA · COMPUTE · ENERGY ACCOUNTING</span>
        <h2 className="displayTitle">Count what is counted. Measure what is measured. Leave the rest null.</h2>
        <div className="grid twoCol">
          <article className="panel"><p className="eyebrow">Identity reuse</p><h2>31,672,976 = 10,854,020 + 20,818,956</h2><p className="mono">reuse = 65.730975%</p><p className="muted">Deterministic arithmetic over retained accounting inputs; some corpus components are declared estimates, not a fresh full enumeration.</p></article>
          <article className="panel"><p className="eyebrow">Canonical Parquet footprint</p><h2>1,101,473,790 bytes</h2><p className="muted">Declared canonical output footprint. This is not a measured download-saving number.</p></article>
          <article className="panel"><p className="eyebrow">Whole-download byte savings</p><h2>NOT_MEASURED</h2><p className="muted">Requires a frozen path + size_bytes + sha256 manifest over the actual acquired files.</p></article>
          <article className="panel"><p className="eyebrow">Theoretical 7B compute</p><h2>291,465,384,000,000,000 FLOPs</h2><p className="mono">0.809626 Wh theoretical equivalent</p><p className="muted">Measured energy = NULL · measured time savings = NOT_MEASURED.</p></article>
        </div>
      </section>

      <section className="computeSection" id="models">
        <span className="sectionNumber goldenSectionLabel">08 / HEURISTIC · OPEN MODEL · VITHIA · FRONTIER</span>
        <h2 className="displayTitle">The graph experiment and the model experiment are separate axes.</h2>
        <div className="tableWrap">
          <table>
            <thead><tr><th>Lane</th><th>Role</th><th>Contract</th><th>State</th></tr></thead>
            <tbody>{MODELS.map(([a,b,c,d]) => <tr key={a}><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>)}</tbody>
          </table>
        </div>
      </section>

      <section className="computeSection" id="reproduce">
        <span className="sectionNumber goldenSectionLabel">09 / RECREATE HYDRADB FROM GITHUB</span>
        <h2 className="displayTitle">The public FCG is portable; HydraDB is the operational query projection.</h2>
        <div className="flow mono">
          <span>custody/graph/live/nodes.jsonl</span><b>+</b><span>edges.jsonl</span><b>→</b>
          <span>project_fcg_snapshot_to_hydradb.py</span><b>→</b><span>isolated hydradg-* namespace</span><b>→</b>
          <span>node/edge/root readback</span><b>→</b><span>receipt</span>
        </div>
        <pre className="panel mono small" style={{overflowX:"auto"}}>{`python3 scripts/project_fcg_snapshot_to_hydradb.py \\
  --nodes custody/graph/live/nodes.jsonl \\
  --edges custody/graph/live/edges.jsonl \\
  --endpoint http://127.0.0.1:8443/v1/graphs/default/query \\
  --token-file ~/.local/share/hydradg-repro/hydradb-auth-token \\
  --namespace hydradg-judge-repro \\
  --allow-write \\
  --out repro/receipts/HYDRADB_FCG_IMPORT_RECEIPT.json`}</pre>
        <p className="small muted note">Current state: PROCEDURE_PRESENT; FRESH_EXPANDED_IMPORT_RECEIPT_PENDING.</p>
      </section>

      <section className="computeSection" id="gaps">
        <span className="sectionNumber goldenSectionLabel">10 / GAP → PROMOTION GATE</span>
        <h2 className="displayTitle">The roadmap is a matrix of falsifiable gates, not promises.</h2>
        <div className="tableWrap">
          <table>
            <thead><tr><th>Gap</th><th>Why red</th><th>How it turns green</th><th>Current state</th></tr></thead>
            <tbody>{GAPS.map(([a,b,c,d]) => <tr key={a}><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>)}</tbody>
          </table>
        </div>
      </section>

      <section className="computeSection" id="award-case">
        <span className="sectionNumber goldenSectionLabel">11 / WHY THIS SHOULD SCORE WELL</span>
        <h2 className="displayTitle">The product is not “a better benchmark number.” It is a graph-native way to keep context inspectable as it changes.</h2>
        <div className="grid twoCol">
          <article className="panel"><p className="eyebrow">Track 03</p><h2>Strongest current track case</h2><p>Real full500 retrieval, chronology, overwritten state, contradiction and abstention, with the negative K5 result preserved and the K10 cutoff effect separately measured.</p></article>
          <article className="panel"><p className="eyebrow">Best Use of HydraDB</p><h2>Strongest special-award case</h2><p>HydraDB is used as a graph query/traversal projection for versioned custody/context. Exact identity, temporal edges, null evidence, deterministic calculators and reproducible readback make failures auditable.</p></article>
          <article className="panel"><p className="eyebrow">Originality</p><h2>Information-State Heat Layer</h2><p>A dimensionless, backend-agnostic context-state diagnostic can compare reference, degradation and restoration without pretending the score is physical energy or model accuracy.</p></article>
          <article className="panel"><p className="eyebrow">Scientific rigor</p><h2>Failure data stays data.</h2><p>RAW=SeedGraph at fixed K, B/C/D fail to beat A at K5, hosted canary degradation, 12 unexplained secret candidates, and legacy overclaim receipts remain visible rather than deleted.</p></article>
        </div>
      </section>

      <section className="computeSection" id="eligibility-custody">
        <span className="sectionNumber goldenSectionLabel">12 / FORM ELIGIBILITY CUSTODY</span>
        <h2 className="displayTitle">The final submission attestations remain bounded by their evidence.</h2>
        <div className="panel"><p className="mono small">claim_ceiling={eligibilityClaimCeiling}</p></div>
        <div className="grid twoCol" style={{marginTop:24}}>
          {hackHydraEligibility.map((item) => (
            <article className="panel" key={item.key}>
              <p className="eyebrow">{item.state}</p>
              <h2>{item.label}</h2>
              <p className="note">“{item.formConfirmation}”</p>
              <ul>{item.evidence.map((e) => <li key={e}>{e}</li>)}</ul>
              <p className="small muted">Boundary: {item.limitation}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
