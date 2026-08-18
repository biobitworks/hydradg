"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

type Status = {
  graph: { backend: string; configured: boolean; reachable: boolean; error: string | null };
  providers: Record<string, boolean>;
  hydradb_pin: { repository: string; commit: string; claim_ceiling: string };
  sources: Array<{ name: string; url: string; status: string; role: string }>;
};

type QueryAction = "memory" | "current" | "history" | "provenance";
type FixtureReceipt = {
  subject_key?: string;
  ids?: Record<string, string>;
  [key: string]: unknown;
};

function StatusPill({ ok, children }: { ok: boolean; children: React.ReactNode }) {
  return <span className={`pill ${ok ? "pillGood" : "pillMuted"}`}>{children}</span>;
}

export default function Home() {
  const [status, setStatus] = useState<Status | null>(null);
  const [action, setAction] = useState<QueryAction>("memory");
  const [term, setTerm] = useState("");
  const [queryResult, setQueryResult] = useState<unknown>(null);
  const [queryBusy, setQueryBusy] = useState(false);
  const [fixture, setFixture] = useState<FixtureReceipt | null>(null);
  const [fixtureBusy, setFixtureBusy] = useState(false);
  const [exaTerm, setExaTerm] = useState("");
  const [exaIngest, setExaIngest] = useState(true);
  const [exaResult, setExaResult] = useState<unknown>(null);
  const [exaBusy, setExaBusy] = useState(false);

  useEffect(() => {
    fetch("/api/status", { cache: "no-store" })
      .then((response) => response.json())
      .then(setStatus)
      .catch((error) => setQueryResult({ error: String(error) }));
  }, []);

  const providerEntries = useMemo(() => Object.entries(status?.providers || {}), [status]);

  async function loadFixture() {
    setFixtureBusy(true);
    try {
      const response = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "fixture" }),
      });
      const data = (await response.json()) as { fixture?: FixtureReceipt; error?: string };
      setFixture(data.fixture || data);
      if (data.fixture?.subject_key) {
        setAction("current");
        setTerm(data.fixture.subject_key);
      }
    } finally {
      setFixtureBusy(false);
    }
  }

  function chooseFixtureId(key: string, nextAction: QueryAction) {
    const id = fixture?.ids?.[key];
    if (!id) return;
    setAction(nextAction);
    setTerm(id);
  }

  async function submitGraph(event: FormEvent) {
    event.preventDefault();
    setQueryBusy(true);
    setQueryResult(null);
    try {
      const payload =
        action === "memory"
          ? { action, term }
          : action === "current"
            ? { action, subject_key: term }
            : { action, id: term };
      const response = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      setQueryResult(await response.json());
    } finally {
      setQueryBusy(false);
    }
  }

  async function submitExa(event: FormEvent) {
    event.preventDefault();
    setExaBusy(true);
    setExaResult(null);
    try {
      const response = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "exa", term: exaTerm, ingest: exaIngest }),
      });
      setExaResult(await response.json());
    } finally {
      setExaBusy(false);
    }
  }

  return (
    <main>
      <nav>
        <a href="/demo">Demo + video</a>
        <a href="/eligibility">Submission custody</a>
      </nav>

      <header className="hero">
        <div>
          <p className="eyebrow">Hack Hydra · Track 03 — Memory + Context Retrieval</p>
          <h1>HydraDG</h1>
          <p className="lede">
            Custody-aware persistent memory: retrieve the current state, reconstruct history,
            traverse provenance, and show exactly where evidence changed.
          </p>
        </div>
        <div className="heroStatus">
          <StatusPill ok={Boolean(status?.graph.reachable)}>
            graph {status?.graph.reachable ? "online" : "offline"}
          </StatusPill>
          <span className="mono small">{status?.graph.backend || "loading"}</span>
        </div>
      </header>

      <section className="metrics" aria-label="Runtime status">
        <article className="metric">
          <span className="metricLabel">Graph</span>
          <strong>{status?.graph.reachable ? "Reachable" : status?.graph.configured ? "Configured" : "Unconfigured"}</strong>
          <span className="small muted">HydraDB HTTP or Neo4j-compatible Bolt</span>
        </article>
        <article className="metric">
          <span className="metricLabel">HydraDB pin</span>
          <strong className="mono compact">{status?.hydradb_pin.commit.slice(0, 12) || "loading"}</strong>
          <span className="small muted">source revision pin</span>
        </article>
        <article className="metric">
          <span className="metricLabel">Custody</span>
          <strong>SHA-256 FCO/FCG</strong>
          <span className="small muted">claim ceilings preserved</span>
        </article>
        <article className="metric">
          <span className="metricLabel">Temporal memory</span>
          <strong>Current + history</strong>
          <span className="small muted">append-only supersession fixture</span>
        </article>
      </section>

      <section className="panel architecture">
        <div className="panelHead">
          <div>
            <p className="eyebrow">Deterministic end-to-end fixture</p>
            <h2>Seed the complete graph path</h2>
          </div>
          <StatusPill ok={Boolean(status?.graph.reachable)}>HydraDB required</StatusPill>
        </div>
        <p className="muted">
          Loads two synthetic temporal states with source → evidence → atom → Seed of Truth lineage.
          The fixture is explicitly claim-bounded and its Anticube adapter remains fail-closed until a
          public contract is pinned.
        </p>
        <div className="actions">
          <button className="primary" onClick={loadFixture} disabled={fixtureBusy || !status?.graph.reachable}>
            {fixtureBusy ? "Loading…" : "Load deterministic fixture"}
          </button>
          <button className="secondary" onClick={() => chooseFixtureId("seed_v1", "history")} disabled={!fixture?.ids?.seed_v1}>
            Trace seed history
          </button>
          <button className="secondary" onClick={() => chooseFixtureId("seed_v2", "provenance")} disabled={!fixture?.ids?.seed_v2}>
            Trace current provenance
          </button>
        </div>
        <ResultBox value={fixture} empty="Load the fixture to get deterministic object IDs and FCG edge receipts." />
      </section>

      <section className="grid twoCol">
        <article className="panel">
          <div className="panelHead">
            <div>
              <p className="eyebrow">Memory graph</p>
              <h2>Explore state and lineage</h2>
            </div>
            <StatusPill ok={Boolean(status?.graph.reachable)}>live query</StatusPill>
          </div>

          <div className="tabs" role="tablist" aria-label="Graph query mode">
            {(["memory", "current", "history", "provenance"] as QueryAction[]).map((mode) => (
              <button key={mode} type="button" className={action === mode ? "tab active" : "tab"} onClick={() => setAction(mode)}>
                {mode}
              </button>
            ))}
          </div>

          <form onSubmit={submitGraph} className="stack">
            <label>
              {action === "memory" ? "Text or exact FCO id" : action === "current" ? "Subject key" : "Exact FCO id"}
              <input
                value={term}
                onChange={(event) => setTerm(event.target.value)}
                placeholder={action === "current" ? "hydradg.demo.memory" : action === "memory" ? "demo state" : "fco:…"}
                required
              />
            </label>
            <button className="primary" disabled={queryBusy || !term.trim() || !status?.graph.reachable}>
              {queryBusy ? "Querying…" : action === "memory" ? "Search memory" : action === "current" ? "Get current state" : `Trace ${action}`}
            </button>
          </form>

          <ResultBox value={queryResult} empty="Query results appear here." />
        </article>

        <article className="panel">
          <div className="panelHead">
            <div>
              <p className="eyebrow">External evidence</p>
              <h2>Retrieve → hash → admit</h2>
            </div>
            <StatusPill ok={Boolean(status?.providers.exa)}>Exa</StatusPill>
          </div>
          <p className="muted">
            URL mode uses Exa Contents; query mode uses Exa Search. External retrieval is optional
            and remains separate from the deterministic HydraDB fixture.
          </p>
          <form onSubmit={submitExa} className="stack">
            <label>
              Query or URL
              <textarea rows={4} value={exaTerm} onChange={(event) => setExaTerm(event.target.value)} placeholder="Public source URL or research query" required />
            </label>
            <label className="checkRow">
              <input type="checkbox" checked={exaIngest} onChange={(event) => setExaIngest(event.target.checked)} />
              Admit retrieved evidence to FCO/FCG graph
            </label>
            <button className="primary" disabled={exaBusy || !exaTerm.trim() || !status?.providers.exa}>
              {exaBusy ? "Retrieving…" : exaIngest ? "Retrieve and admit" : "Retrieve only"}
            </button>
          </form>
          <ResultBox value={exaResult} empty="External retrieval results appear here." />
        </article>
      </section>

      <section className="grid twoCol">
        <article className="panel">
          <p className="eyebrow">Execution providers</p>
          <h2>Bounded compute adapters</h2>
          <div className="providerList">
            {providerEntries.map(([name, configured]) => (
              <div className="provider" key={name}>
                <strong>{name}</strong>
                <StatusPill ok={configured}>{configured ? "configured" : "optional / unconfigured"}</StatusPill>
              </div>
            ))}
          </div>
          <p className="small muted note">Provider presence is not treated as proof of a successful live call.</p>
        </article>

        <article className="panel">
          <p className="eyebrow">Source registry</p>
          <h2>Inputs and unresolved evidence</h2>
          <div className="sourceList">
            {(status?.sources || []).map((source) => (
              <a href={source.url} target="_blank" rel="noreferrer" className="source" key={source.url}>
                <div><strong>{source.name}</strong><p className="small muted">{source.role}</p></div>
                <span className={`sourceStatus ${source.status === "verified-doc" ? "verified" : "unresolved"}`}>{source.status}</span>
              </a>
            ))}
          </div>
        </article>
      </section>

      <section className="panel architecture">
        <div>
          <p className="eyebrow">MVP path</p>
          <h2>Evidence becomes queryable memory without losing lineage</h2>
        </div>
        <div className="flow mono">
          <span>source</span><b>→</b><span>evidence</span><b>→</b><span>atom</span><b>→</b>
          <span>Seed of Truth</span><b>→</b><span>temporal state</span><b>→</b><span>HydraDB query</span>
        </div>
      </section>
    </main>
  );
}

function ResultBox({ value, empty }: { value: unknown; empty: string }) {
  if (value === null) return <div className="result empty">{empty}</div>;
  return <pre className="result">{JSON.stringify(value, null, 2)}</pre>;
}
