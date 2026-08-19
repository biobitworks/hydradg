import ContextIcebergHero from "@/components/ContextIcebergHero";
import PublicBackendStatus from "@/components/PublicBackendStatus";

export default function GraphPage() {
  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">4D Fractal Custody Graph</p>
          <h1>State field</h1>
          <p className="lede">
            Drag to rotate x/y/z, scroll or pinch to change scale, scrub time through graph history,
            and select an FCO to inspect the governed context state. The visualization consumes the
            same read-only Context Iceberg state as the public overview.
          </p>
        </div>
      </header>

      <PublicBackendStatus />

      <section style={{ marginTop: 18 }}>
        <ContextIcebergHero />
      </section>

      <section className="panel architecture" style={{ marginTop: 18 }}>
        <p className="eyebrow">Why this page exists</p>
        <h2>Traverse the evidence graph without changing it</h2>
        <p className="muted">
          HydraDB is the queryable graph projection; FCO/FCG custody remains the canonical provenance
          and claim-boundary layer. Cloud Drift and ΔG* describe context state. Hit@K and Recall@K are
          empirical retrieval outcomes and must remain separate from those diagnostics.
        </p>
        <div className="actions">
          <a className="secondary" href="/knowledge">Open Knowledge Base</a>
          <a className="secondary" href="/how-to">How to use HydraDG</a>
          <a className="secondary" href="/eligibility">Check custody state</a>
          <a className="secondary" href="/backup/hydradg.html">Open Static Fallback</a>
        </div>
      </section>
    </main>
  );
}
