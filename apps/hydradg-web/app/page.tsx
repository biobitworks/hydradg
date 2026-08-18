"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

type Status = {
  graph: { backend: string; configured: boolean; reachable: boolean; error: string | null };
  providers: Record<string, boolean>;
  hydradb_pin: { repository: string; commit: string; claim_ceiling: string };
  sources: Array<{ name: string; url: string; status: string; role: string }>;
};

type QueryAction = "memory" | "history" | "provenance";

function StatusPill({ ok, children }: { ok: boolean; children: React.ReactNode }) {
  return <span className={`pill ${ok ? "pillGood" : "pillMuted"}`}>{children}</span>;
}

export default function Home() {
  const [status, setStatus] = useState<Status | null>(null);
  const [action, setAction] = useState<QueryAction>("memory");
  const [term, setTerm] = useState("");
  const [queryResult, setQueryResult] = useState<unknown>(null);
  const [queryBusy, setQueryBusy] = useState(false);
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

  const providerEntries = useMemo(
    () => Object.entries(status?.providers || {}),
    [status],
  );

  async function submitGraph(event: FormEvent) {
    event.preventDefault();
    setQueryBusy(true);
    setQueryResult(null);
    try {
      const payload = action === "memory" ? { action, term } : { action, id: term };
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
      <header className="hero">
        <div>
          <p className="eyebrow">Hack Hydra · Track 03</p>
          <h1>HydraDG</h1>
          <p className="lede">
            Custody-aware persistent memory: retrieve the current fact, reconstruct history,
            traverse provenance, and show where evidence diverged or recovered.
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
          <span className="small muted">source revision only</span>
        </article>
        <article className="metric">
          <span className="metricLabel">Custody</span>
          <strong>SHA-256 FCO/FCG</strong>
          <span className="small muted">claim ceilings preserved</span>
        </article>
        <article className="metric">
          <span className="metricLabel">Benchmark target</span>
          <strong>LongMemEval-S</strong>
          <span className="small muted">smoke80 → full500</span>
        </article>
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
            {(["memory", "history", "provenance"] as QueryAction[]).map((mode) => (
              <button
                key={mode}
                type="button"
                className={action === mode ? "tab active" : "tab"}
                onClick={() => setAction(mode)}
              >
                {mode}
              </button>
            ))}
          </div>

          <form onSubmit={submitGraph} className="stack">
            <label>
              {action === "memory" ? "Text or exact FCO id" : "Exact FCO id"}
              <input
                value={term}
                onChange={(event) => setTerm(event.target.value)}
                placeholder={action === "memory" ? "e.g. Vithia or fco:…" : "fco:…"}
                required
              />
            </label>
            <button className="primary" disabled={queryBusy || !term.trim()}>
              {queryBusy ? "Querying…" : action === "memory" ? "Search memory" : `Trace ${action}`}
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
            Enter a research query or a URL. URL mode uses Exa Contents; query mode uses Exa Search.
            Admission creates hashed ToolAction, Source, and Evidence FCOs plus typed FCG edges.
          </p>
          <form onSubmit={submitExa} className="stack">
            <label>
              Query or URL
              <textarea
                rows={4}
                value={exaTerm}
                onChange={(event) => setExaTerm(event.target.value)}
                placeholder="https://share.google/aimode/… or a research question"
                required
              />
            </label>
            <label className="checkRow">
              <input
                type="checkbox"
                checked={exaIngest}
                onChange={(event) => setExaIngest(event.target.checked)}
              />
              Admit retrieved evidence to FCO/FCG graph
            </label>
            <button className="primary" disabled={exaBusy || !exaTerm.trim()}>
              {exaBusy ? "Retrieving…" : exaIngest ? "Retrieve and admit" : "Retrieve only"}
            </button>
          </form>
          <ResultBox value={exaResult} empty="External retrieval results appear here." />
        </article>
      </section>

      <section className="grid twoCol">
        <article className="panel">
          <div className="panelHead">
            <div>
              <p className="eyebrow">Execution providers</p>
              <h2>Bounded compute adapters</h2>
            </div>
          </div>
          <div className="providerList">
            {providerEntries.map(([name, configured]) => (
              <div className="provider" key={name}>
                <div>
                  <strong>{name}</strong>
                  <p className="small muted">
                    {name === "daytona" && "isolated sandbox execution"}
                    {name === "gmi" && "container / GPU compute"}
                    {name === "modal" && "remote functions and model endpoints"}
                    {name === "exa" && "search and URL content retrieval"}
                  </p>
                </div>
                <StatusPill ok={configured}>{configured ? "configured" : "not configured"}</StatusPill>
              </div>
            ))}
          </div>
          <p className="small muted note">
            MVP exposes provider readiness only. Paid or destructive compute invocation remains disabled
            until its run contract, limits, and receipt schema are pinned.
          </p>
        </article>

        <article className="panel">
          <div className="panelHead">
            <div>
              <p className="eyebrow">Source registry</p>
              <h2>Inputs and unresolved evidence</h2>
            </div>
          </div>
          <div className="sourceList">
            {(status?.sources || []).map((source) => (
              <a href={source.url} target="_blank" rel="noreferrer" className="source" key={source.url}>
                <div>
                  <strong>{source.name}</strong>
                  <p className="small muted">{source.role}</p>
                </div>
                <span className={`sourceStatus ${source.status === "verified-doc" ? "verified" : "unresolved"}`}>
                  {source.status}
                </span>
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
          <span>source</span><b>→</b><span>retrieval</span><b>→</b><span>SHA-256 FCO</span><b>→</b>
          <span>FCG edges</span><b>→</b><span>HydraDB</span><b>→</b><span>answer + provenance</span>
        </div>
      </section>
    </main>
  );
}

function ResultBox({ value, empty }: { value: unknown; empty: string }) {
  if (value === null) return <div className="result empty">{empty}</div>;
  return <pre className="result">{JSON.stringify(value, null, 2)}</pre>;
}
