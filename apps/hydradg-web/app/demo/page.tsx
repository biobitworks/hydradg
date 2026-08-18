"use client";

import { useState } from "react";

export default function DemoPage() {
  const [result, setResult] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);

  async function loadFixture() {
    setBusy(true);
    try {
      const response = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "fixture" }),
      });
      setResult(await response.json());
    } finally {
      setBusy(false);
    }
  }

  return (
    <main>
      <nav>
        <a href="/">MVP</a>
        <a href="/eligibility">Submission custody</a>
      </nav>

      <header className="hero">
        <div>
          <p className="eyebrow">Hack Hydra 2026 · Track 03 demo</p>
          <h1>HydraDG demo</h1>
          <p className="lede">
            This stable route is the landing page for the final pitch video and the deterministic
            end-to-end graph fixture. The video can be replaced without changing this URL.
          </p>
        </div>
      </header>

      <section className="grid twoCol">
        <article className="panel">
          <p className="eyebrow">Working fixture</p>
          <h2>Load two temporal states</h2>
          <p className="muted">
            The fixture writes synthetic, claim-bounded FCO/FCG objects to the configured graph.
            It includes source → evidence → atom → Seed of Truth lineage, a supersession edge,
            and fail-closed Anticube adapter receipts.
          </p>
          <div className="actions">
            <button className="primary" onClick={loadFixture} disabled={busy}>
              {busy ? "Loading…" : "Load deterministic fixture"}
            </button>
            <a className="secondary" href="/">Open query console</a>
          </div>
          <pre className="result">{result ? JSON.stringify(result, null, 2) : "Fixture receipt appears here."}</pre>
        </article>

        <article className="panel">
          <p className="eyebrow">3-minute submission video</p>
          <h2>Video slot</h2>
          <p className="muted">
            The required YouTube link will be added here after the backend and demo sequence pass
            end-to-end testing. Until then this page deliberately does not claim a video exists.
          </p>
          <div className="result empty">FINAL_YOUTUBE_URL_PENDING</div>
        </article>
      </section>

      <section className="panel architecture">
        <div>
          <p className="eyebrow">Judge flow</p>
          <h2>What the final demo will show</h2>
        </div>
        <div className="flow mono">
          <span>load fixture</span><b>→</b><span>current state</span><b>→</b>
          <span>history</span><b>→</b><span>provenance</span><b>→</b>
          <span>first changed dependency</span><b>→</b><span>custody receipt</span>
        </div>
      </section>
    </main>
  );
}
