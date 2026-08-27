import Link from "next/link";

const SOURCE_SHA = "44e9d3dc7014b9b2c410a9e1e2c9b35a72cd269e4e561eba40414081ca81690d";

export default function ReconciliationDeltaCard() {
  return (
    <section className="computeSection" id="reconciliation-delta">
      <span className="sectionNumber">06E / RECONCILIATION DELTA</span>
      <h2 className="displayTitle">Why the delta matters.</h2>
      <p className="sectionLead">
        HydraLamp does not merely record that something changed. It records which frozen state was the source, which deterministic transform recomputed the measurement, which dimension changed, which did not, and whether a claim is strengthened, unchanged, weakened, or blocked.
      </p>
      <div className="flow mono">
        <span>frozen source</span><b>→</b><span>recompute</span><b>→</b><span>reconciliation delta</span><b>→</b><span>claim boundary</span><b>→</b><span>judge projection</span>
      </div>
      <article className="panel">
        <p className="eyebrow">RECONCILIATION DELTA · PROJECTION_ONLY</p>
        <div className="mono small compact stack">
          <p>SOURCE · 46 frozen events · {SOURCE_SHA.slice(0, 8)}…{SOURCE_SHA.slice(-5)}</p>
          <p>SECURITY · private leaks 0 · unauthorized writes 0 · replays accepted 0 · poison canonicalized 0</p>
          <p>RESTORATION · PASS · QUARANTINE_RESOLVED · PASS</p>
          <p>TOPOLOGY · FCG root changes 6 (custody/topology — not accuracy)</p>
          <p>ENGINEERING · ΔG* scoped · CloudDrift implementation-dependent · restoration_gain NOT_COMPUTED</p>
          <p>CLAIM · GOVERNED_MECHANISM_PASS · NO_STATISTICAL_MODEL_SUPERIORITY</p>
        </div>
        <div className="actions">
          <a className="secondary" href="/demo/reconciliation-delta-use-case.json">View projection JSON</a>
          <a className="secondary" href="/api/hydralamp/reconciliation-delta">API projection</a>
          <Link className="secondary" href="/hydralamp">Open HydraLamp</Link>
        </div>
        <p className="small muted note">CANONICAL_FCG_APPEND=NOT_PERFORMED. Model panel outputs remain PROBABILISTIC_MODEL_OUTPUT; this card is DERIVED_RECONCILIATION_EVIDENCE.</p>
      </article>
    </section>
  );
}
