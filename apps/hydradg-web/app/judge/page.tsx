import PublicBackendStatus from "@/components/PublicBackendStatus";

const STATES = [
  {
    label: "Reference",
    relation: "CURRENT",
    body: "Begin with one declared current fact and its source/evidence path.",
    why: "Establish the frozen comparison state before any perturbation.",
  },
  {
    label: "Poison",
    relation: "CONTRADICTS / SUPERSEDED_BY",
    body: "Introduce a controlled conflicting state while retaining the predecessor and its provenance.",
    why: "Expose the first divergent relationship without overwriting history.",
  },
  {
    label: "Antidote",
    relation: "RESTORES / CURRENT",
    body: "Represent recovery as a new state while the perturbation remains traversable.",
    why: "Test restoration without deleting counterevidence.",
  },
] as const;

export default function JudgePage() {
  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">Judge Demo · public read-only walkthrough</p>
          <h1>Change state. Keep the history.</h1>
          <p className="lede">
            HydraDG models reference → poison → antidote as explicit graph state transitions. The hosted judge surface is read-only; local mutation controls remain on magicSTUDIObox.
          </p>
        </div>
      </header>

      <PublicBackendStatus />

      <section className="computeSection">
        <span className="sectionNumber">01 / GOLDEN PATH</span>
        <h2 className="displayTitle">Reference → poison → antidote.</h2>
        <div className="grid threeCol">
          {STATES.map((state, index) => (
            <article className="panel" key={state.label}>
              <p className="eyebrow">0{index + 1} · {state.relation}</p>
              <h2>{state.label}</h2>
              <p>{state.body}</p>
              <p className="small muted"><strong>Why:</strong> {state.why}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">02 / WHAT TO CLICK NEXT</span>
        <h2 className="displayTitle">Follow the evidence, not a sales claim.</h2>
        <div className="actions">
          <a className="primary" href="/track03">See Executed Result</a>
          <a className="secondary" href="/graph">Trace One Result</a>
          <a className="secondary" href="/knowledge">Need a term? Open Knowledge Base</a>
          <a className="secondary" href="/backup/hydradg.html">Open Static Fallback</a>
        </div>
        <p className="small muted note">
          This page demonstrates the state-transition contract. It does not claim that clicking these presentation states mutates the public HydraDB tenant.
        </p>
      </section>
    </main>
  );
}
