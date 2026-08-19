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
        <a href="/evidence">Recorded evidence</a>
        <a href="/graph">4D FCG</a>
        <a href="/eligibility">Submission custody</a>
      </nav>

      <header className="hero">
        <div>
          <p className="eyebrow">Hack Hydra 2026 · Track 03 demo</p>
          <h1>HydraDG demo</h1>
          <p className="lede">
            Stable submission landing page for the deterministic backend proof, interactive 4D FCG,
            recorded benchmark evidence, and final pitch video. The video and final full500 receipt can
            change without changing this URL.
          </p>
        </div>
      </header>

      <section className="grid twoCol">
        <article className="panel">
          <p className="eyebrow">Working fixture</p>
          <h2>Reference → mutation → restoration</h2>
          <p className="muted">
            The fixture writes claim-bounded FCO/FCG objects to HydraDB: source → evidence → atom →
            Seed of Truth plus three StateSnapshot FCOs. It preserves temporal supersession,
            provenance, and deterministic information-state metrics.
          </p>
          <div className="actions">
            <button className="primary" onClick={loadFixture} disabled={busy}>
              {busy ? "Loading…" : "Load deterministic fixture"}
            </button>
            <a className="secondary" href="/graph">Explore 4D FCG</a>
            <a className="secondary" href="/evidence">Inspect evidence ledger</a>
            <a className="secondary" href="/">Open query console</a>
          </div>
          <pre className="result">{result ? JSON.stringify(result, null, 2) : "Fixture receipt appears here when a graph backend is configured."}</pre>
        </article>

        <article className="panel">
          <p className="eyebrow">3-minute submission video</p>
          <h2>Video slot</h2>
          <p className="muted">
            The required YouTube link will be added here only after the backend, graph, custody,
            and demo sequence pass end-to-end testing.
          </p>
          <div className="result empty">FINAL_YOUTUBE_URL_PENDING</div>
        </article>
      </section>

      <section className="panel architecture">
        <div>
          <p className="eyebrow">Judge flow</p>
          <h2>Three-minute path</h2>
        </div>
        <div className="flow mono">
          <span>recorded evidence</span><b>→</b><span>load fixture</span><b>→</b>
          <span>4D state field</span><b>→</b><span>current state</span><b>→</b>
          <span>history</span><b>→</b><span>provenance</span><b>→</b>
          <span>custody / claim ceiling</span>
        </div>
      </section>
    </main>
  );
}
