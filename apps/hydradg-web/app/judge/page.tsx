import Link from "next/link";

import PublicBackendStatus from "@/components/PublicBackendStatus";
import { RELEASE_TIMEPOINTS } from "@/lib/releaseTimepoints";

const STATES = [
  { label: "Reference", query: "T0_REFERENCE", relation: "CURRENT", body: "Begin with one declared current fact and its source/evidence path.", why: "Freeze the comparison state before perturbation." },
  { label: "Poison", query: "T1_MUTATION", relation: "CONTRADICTS / SUPERSEDED_BY", body: "Introduce one controlled conflicting state while retaining predecessor provenance.", why: "Expose the first divergent relationship without overwriting history." },
  { label: "Antidote", query: "T2_RESTORATION", relation: "RESTORES / CURRENT", body: "Represent recovery as a new state while the perturbation remains traversable.", why: "Test restoration without deleting counterevidence." },
] as const;

const CRITERIA = ["Technical execution", "HydraDB + graph-native use", "Product completeness + usability", "Quality of results", "Originality"] as const;

function score(point: (typeof RELEASE_TIMEPOINTS)[number]) {
  if (point.score_state !== "MEASURED") return <span className="pill pillMuted">N/A BY CONTRACT</span>;
  return <><strong>G*: {point.g_star?.toFixed(6)}</strong><br /><span className="small muted">ΔG*: {(point.delta_g_star ?? 0) > 0 ? "+" : ""}{point.delta_g_star?.toFixed(6)}<br />Cloud Drift: {point.cloud_drift?.toFixed(4)}</span></>;
}

export default function JudgePage() {
  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow goldText">Judge Demo · public read-only walkthrough · Golden path</p>
          <h1>Change state. Keep the history.</h1>
          <p className="lede">HydraDG makes reference → poison → antidote explicit graph transitions, then keeps migration, experiment and release states as separate FCG timepoints. The judge path separates deterministic evidence, probabilistic model interpretation and unexecuted future comparisons.</p>
          <div className="actions"><a className="primary goldenCta" href="#golden-states">Start with reference</a><Link className="secondary" href="/track03">Executed Track 03 result</Link><Link className="secondary" href="/models">Models used</Link></div>
        </div>
      </header>

      <PublicBackendStatus />

      <section className="computeSection" id="golden-states">
        <span className="sectionNumber goldenSectionLabel">01 / GOLDEN PATH</span>
        <h2 className="displayTitle">Reference → poison → antidote.</h2>
        <p className="sectionLead">Gold marks the judge navigation path only. Violet = reference/normal, Orange = poison/mutation, Blue = antidote/restoration. Those scientific state colors do not encode pass/fail or retrieval accuracy.</p>
        <div className="grid threeCol">
          {STATES.map((state, index) => (
            <article className="panel goldenPanel" key={state.label}>
              <p className="eyebrow">0{index + 1} · {state.relation}</p>
              <h2><Link className="goldLink" href={`/graph?q=${state.query}`}>{state.label}</Link></h2>
              <p>{state.body}</p><p className="small muted"><strong>Why:</strong> {state.why}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="computeSection" id="model-boundary">
        <span className="sectionNumber goldenSectionLabel">02 / WHAT USED A MODEL?</span>
        <h2 className="displayTitle">The submitted K=5 experiment did not.</h2>
        <div className="statusGrid">
          <article className="statusCard gold"><p className="eyebrow">Track 03 full500 K=5</p><strong>MODEL = NONE</strong><p className="mono small">extractor=heuristic · model=null · ollarma_url=null</p><p className="muted">Primary executed retrieval evidence.</p></article>
          <article className="statusCard"><p className="eyebrow">Local analyst lane</p><strong>Qwen2.5 7B + Qwen2.5-Coder 7B</strong><p className="muted">Optional loopback diagnostic models after deterministic output freeze. Their responses are probabilistic model-output FCOs.</p></article>
          <article className="statusCard"><p className="eyebrow">Frontier-cloud comparison</p><strong>NOT CONTROLLED / NOT RUN</strong><p className="muted">No local-vs-frontier superiority claim is established. Synthetic design rows are not model-execution evidence.</p></article>
        </div>
        <div className="actions"><Link className="secondary" href="/models">Open full model protocol + HF cards</Link></div>
      </section>

      <section className="computeSection" id="timepoints">
        <span className="sectionNumber goldenSectionLabel">03 / TIMEPOINT EVIDENCE LANES · T0–T5</span>
        <h2 className="displayTitle">Do not copy a score into a state that never declared one.</h2>
        <p className="sectionLead">T0–T2 use declared synthetic distributions for G*, ΔG* and Cloud Drift. T3–T5 have no declared scoring distribution and instead carry bounded migration, classification and release evidence.</p>
        <div className="tableWrap">
          <table className="small">
            <thead><tr><th>Timepoint</th><th>Classification</th><th>Scientific score</th><th>Evidence</th></tr></thead>
            <tbody>{RELEASE_TIMEPOINTS.map((tp) => <tr key={tp.id}>
              <td><strong>{tp.id}</strong><br />{tp.label}</td>
              <td className="mono small">{tp.classification}</td>
              <td>{score(tp)}</td>
              <td>{tp.evidence}</td>
            </tr>)}</tbody>
          </table>
        </div>
        <p className="small muted note">The retained T3 hosted-parity statement is bounded to the historical receipt that produced it. It must not be generalized to expanded current FCG parity without a fresh reconciliation receipt.</p>
      </section>

      <section className="computeSection" id="judge-lenses">
        <span className="sectionNumber goldenSectionLabel">04 / JUDGE LENSES</span>
        <h2 className="displayTitle">Primary Track 03; architecture inspected from all three graph problems.</h2>
        <div className="grid threeCol">
          <article className="panel"><p className="eyebrow">Track 01 · Enterprise context + ontology</p><h2><Link className="goldLink" href="/track01">Identity resolution</Link></h2><p className="muted">Inspect canonical entities, aliases, provenance and contradiction handling. Core data is downloaded/hashed; real-data ontology ingestion/evaluation remains pending.</p></article>
          <article className="panel"><p className="eyebrow">Track 02 · Repos + dependencies</p><h2><Link className="goldLink" href="/track02">Blast-radius traversal</Link></h2><p className="muted">Inspect transitive graph reasoning and fail-closed canary boundaries. Real npm/dependency evaluation remains pending.</p></article>
          <article className="panel goldenPanel"><p className="eyebrow">Track 03 · Primary submission</p><h2><Link className="goldLink" href="/track03">Memory + context retrieval</Link></h2><p className="muted">500-case full500 run executed; null/negative retrieval result retained. This is the submitted empirical lane.</p></article>
        </div>
      </section>

      <section className="computeSection" id="official-criteria">
        <span className="sectionNumber goldenSectionLabel">05 / OFFICIAL HACK HYDRA JUDGING CRITERIA</span>
        <h2 className="displayTitle">Make the evaluation surface explicit.</h2>
        <div className="judgeCriteria">{CRITERIA.map((criterion, index) => <div className="judgeCriterion" key={criterion}><span className="sectionNumber">0{index + 1}</span><strong>{criterion}</strong></div>)}</div>
        <p className="small muted note">Hack Hydra evaluates submissions within their selected track first and then compares finalists across tracks; Best Use of HydraDB is a separate lens. <a className="goldLink" href="https://hackhydra.hydradb.com/">Official hackathon page</a>.</p>
      </section>

      <section className="computeSection">
        <span className="sectionNumber goldenSectionLabel">06 / CONTINUE THE GOLDEN PATH</span>
        <h2 className="displayTitle">Follow the evidence, not a sales claim.</h2>
        <div className="actions"><Link className="primary goldenCta" href="/track03">Read executed result</Link><Link className="secondary" href="/graph">Trace one FCO</Link><Link className="secondary" href="/models">Models used</Link><Link className="secondary" href="/custody">Verify custody</Link><Link className="secondary" href="/evidence">Evidence ledger</Link><a className="secondary" href="/backup/hydradg.html">Static fallback</a></div>
        <p className="small muted note">The public walkthrough is read-only. It demonstrates declared state-transition and custody contracts; it does not claim that clicking presentation states mutates a judge-visible HydraDB tenant.</p>
      </section>
    </main>
  );
}
