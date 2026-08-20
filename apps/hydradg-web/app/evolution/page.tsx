import Link from "next/link";

import PresentationEvolution from "@/components/PresentationEvolution";
import { PRESENTATION_CLAIM_BOUNDARY, PRESENTATION_HISTORY } from "@/lib/presentationLineage";
import { RELEASE_TIMEPOINTS } from "@/lib/releaseTimepoints";

export default function EvolutionPage() {
  return (
    <main>
      <header className="hero curatedTextHero">
        <div>
          <p className="eyebrow">FCG presentation + release lineage</p>
          <h1>Keep every version. Bind the deployed one to one release FCO.</h1>
          <p className="lede">HydraDG treats the website itself as a custody-bearing projection. Historical views remain linked while the deployed release exposes its exact Git SHA and deterministic WebsiteRelease FCO hash.</p>
          <div className="actions"><Link className="primary" href="/judge">Current judge view</Link><Link className="secondary" href="/graph">Inspect FCG</Link><a className="secondary" href="/api/release">Release JSON</a></div>
        </div>
      </header>

      <section className="computeSection" style={{ marginTop: 42 }}>
        <span className="sectionNumber">01 / PRESENTATION EVOLUTION</span>
        <h2 className="displayTitle">Supersession is lineage, not erasure.</h2>
        <p className="sectionLead">The current interface gets primary presentation priority because it is the intended judge surface. Historical interfaces remain linked to immutable Git commits and may still carry evidence relevant to later interpretation.</p>
        <PresentationEvolution history={PRESENTATION_HISTORY} />
      </section>

      <section className="computeSection">
        <span className="sectionNumber">02 / FCG TIME + SPACE</span>
        <h2 className="displayTitle">T0–T5 distinguish scientific state from infrastructure/release state.</h2>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead><tr><th align="left">Timepoint</th><th align="left">Class</th><th align="left">Context score state</th><th align="left">Evidence</th></tr></thead>
            <tbody>
              {RELEASE_TIMEPOINTS.map((point) => (
                <tr key={point.id}>
                  <td><strong style={{ color: point.color }}>{point.id} · {point.label}</strong></td>
                  <td>{point.classification}</td>
                  <td>{point.score_state === "MEASURED" ? `G* ${point.g_star?.toFixed(6)} · ΔG* ${point.delta_g_star?.toFixed(6)} · Drift ${point.cloud_drift?.toFixed(4)}` : "N/A — no declared distribution"}</td>
                  <td className="small">{point.evidence}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="small muted note">A release-time change can alter project/retrieval context without mutating canonical scientific FCO identity. Scalar G*/Cloud Drift remains N/A for T3–T5 unless a governed distribution is declared.</p>
      </section>

      <footer className="computeSection"><p className="eyebrow">Claim boundary</p><p className="small muted">{PRESENTATION_CLAIM_BOUNDARY}</p></footer>
    </main>
  );
}
