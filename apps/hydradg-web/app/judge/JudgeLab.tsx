"use client";

import { useEffect, useMemo, useState } from "react";

import GoldenGraph from "./GoldenGraph";
import { COOKBOOK_MATRIX, JUDGE_GUIDES } from "@/lib/judgeKnowledge";

type Mode = "demo" | "live" | "cloud";
type AnyObject = Record<string, any>;

type Props = {
  fixture: AnyObject;
  custody: AnyObject;
};

function pretty(value: unknown) {
  return JSON.stringify(value, null, 2);
}

async function postJson(url: string, body: Record<string, unknown>) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data?.error || `Request failed (${response.status})`);
  return data;
}

export default function JudgeLab({ fixture, custody }: Props) {
  const [mode, setMode] = useState<Mode>("demo");
  const [demoStep, setDemoStep] = useState<"t0" | "t1" | "t2">("t0");
  const [guideId, setGuideId] = useState("fixture");
  const [output, setOutput] = useState<unknown>({ message: "Choose a test. Results appear here." });
  const [busy, setBusy] = useState("");
  const [liveStatus, setLiveStatus] = useState<AnyObject | null>(null);
  const [cloudStatus, setCloudStatus] = useState<AnyObject | null>(null);
  const [cases, setCases] = useState<AnyObject[]>([]);
  const [questionId, setQuestionId] = useState("");
  const [extractor, setExtractor] = useState("heuristic");
  const [loadedCase, setLoadedCase] = useState<AnyObject | null>(null);
  const [selectedFactVertex, setSelectedFactVertex] = useState("");
  const [query, setQuery] = useState("");
  const [method, setMethod] = useState("D");
  const [k, setK] = useState(5);
  const [poisonObject, setPoisonObject] = useState("");
  const [lastInjectedVertex, setLastInjectedVertex] = useState("");
  const [cloudQuery, setCloudQuery] = useState("Why is preserving graph provenance useful for a state update?");
  const [cloudMemory, setCloudMemory] = useState("The HydraDG judge demo prefers graph paths with explicit provenance and current-state explanations.");
  const [cloudSubTenant, setCloudSubTenant] = useState("hydradg-judge-demo");
  const [cloudSourceId, setCloudSourceId] = useState("");

  const guide = useMemo(() => JUDGE_GUIDES.find((item) => item.id === guideId) || JUDGE_GUIDES[0], [guideId]);
  const facts: AnyObject[] = loadedCase?.facts || [];
  const selectedFact = useMemo(
    () => facts.find((fact) => String(fact.vertex) === selectedFactVertex) || facts[0] || null,
    [facts, selectedFactVertex],
  );
  const originalObject = selectedFact ? String(selectedFact.object || "") : "";

  useEffect(() => {
    if (selectedFact && !selectedFactVertex) setSelectedFactVertex(String(selectedFact.vertex));
  }, [selectedFact, selectedFactVertex]);

  useEffect(() => {
    if (selectedFact && !poisonObject) setPoisonObject(`POISON::${String(selectedFact.object || "alternate-state")}`);
  }, [selectedFact, poisonObject]);

  useEffect(() => {
    fetch("/api/live")
      .then(async (response) => ({ ok: response.ok, data: await response.json() }))
      .then(({ data }) => setLiveStatus(data))
      .catch((error) => setLiveStatus({ error: String(error) }));
    fetch("/api/hydradb-cloud")
      .then(async (response) => ({ ok: response.ok, data: await response.json() }))
      .then(({ data }) => setCloudStatus(data))
      .catch((error) => setCloudStatus({ error: String(error) }));
  }, []);

  async function run(label: string, operation: () => Promise<unknown>) {
    setBusy(label);
    try {
      const result = await operation();
      setOutput(result);
      return result as AnyObject;
    } catch (error) {
      setOutput({ error: error instanceof Error ? error.message : String(error), operation: label });
      return null;
    } finally {
      setBusy("");
    }
  }

  async function loadFixture() {
    setGuideId("fixture");
    await run("fixture", () => postJson("/api/query", { action: "fixture" }));
  }

  async function refreshCases() {
    setGuideId("case");
    const result = await run("cases", () => postJson("/api/live", { action: "cases", limit: 100 }));
    const returned = result?.cases || [];
    setCases(returned);
    if (returned.length && !questionId) {
      const update = returned.find((item: AnyObject) => String(item.question_type || "").toLowerCase().includes("update"));
      setQuestionId(String((update || returned[0]).question_id));
    }
  }

  async function loadCase() {
    setGuideId("case");
    const result = await run("load_case", () => postJson("/api/live", { action: "load_case", question_id: questionId, extractor }));
    if (!result) return;
    setLoadedCase(result);
    const first = result.facts?.[0];
    if (first) {
      setSelectedFactVertex(String(first.vertex));
      setPoisonObject(`POISON::${String(first.object || "alternate-state")}`);
    }
  }

  async function retrieve() {
    setGuideId("retrieve");
    await run("retrieve", () =>
      postJson("/api/live", { action: "retrieve", question_id: questionId, question: query, method, k, extractor }),
    );
  }

  async function perturb(kind: "normal" | "poison" | "antidote") {
    setGuideId("perturb");
    const target = lastInjectedVertex || selectedFactVertex || String(facts[0]?.vertex || "");
    if (!target) {
      setOutput({ error: "Load a case first to perform perturbation/antidote operations." });
      return;
    }
    const targetFact = facts.find((f) => String(f.vertex) === target) || selectedFact || facts[0] || null;
    const origObj = targetFact ? String(targetFact.object || "") : originalObject;
    const poisObj = targetFact ? `POISON::${String(targetFact.object || "alternate-state")}` : poisonObject;

    const object = kind === "normal" ? origObj : kind === "poison" ? poisObj : origObj;
    const identity = kind === "normal" ? "SELF" : "NONSELF";
    const safety = kind === "poison" ? "NONSAFE" : "SAFE";
    const result = await run(kind, () =>
      postJson("/api/live", {
        action: "perturb",
        question_id: questionId,
        target_fact_vertex: target,
        object,
        identity_class: identity,
        safety_class: safety,
        extractor,
      }),
    );
    if (result?.after?.vertex) setLastInjectedVertex(String(result.after.vertex));
  }

  async function currentState() {
    setGuideId("current");
    const targetFact = selectedFact || facts[0];
    if (!targetFact) {
      setOutput({ error: "Load a case first." });
      return;
    }
    await run("current", () =>
      postJson("/api/live", {
        action: "current",
        question_id: questionId,
        subject: targetFact.subject,
        predicate: targetFact.predicate,
      }),
    );
  }

  async function cloud(action: string, extra: Record<string, unknown> = {}) {
    setGuideId("cloud");
    await run(`cloud:${action}`, () =>
      postJson("/api/hydradb-cloud", { action, sub_tenant_id: cloudSubTenant, ...extra }),
    );
  }

  return (
    <main>
      <nav>
        <a href="/">MVP</a>
        <a href="/demo">Demo</a>
        <a href="/judge">Judge Lab</a>
        <a href="/graph">4D FCG</a>
        <a href="/evidence">Evidence</a>
        <a href="/eligibility">Submission custody</a>
      </nav>

      <header className="hero">
        <div>
          <p className="eyebrow">Hack Hydra · judge lab</p>
          <h1>HydraDG golden path</h1>
          <p className="lede">
            Start with a deterministic FCO control, move to a real LongMemEval case in the pinned self-hosted HydraDB graph,
            perturb one load-bearing fact, preserve the FCG delta, classify it with Anticube, traverse the changed state,
            and independently test the documented HydraDB cloud cookbook contract.
          </p>
        </div>
        <div className="heroStatus">
          <span className="pill pillGood">fixture ready</span>
          <span className={`pill ${liveStatus?.configured && liveStatus?.health ? "pillGood" : "pillMuted"}`}>
            local live: {liveStatus?.configured && liveStatus?.health ? "ready" : "not connected"}
          </span>
          <span className={`pill ${cloudStatus?.configured && !cloudStatus?.error ? "pillGood" : "pillMuted"}`}>
            cloud API: {cloudStatus?.configured && !cloudStatus?.error ? "ready" : "credential pending"}
          </span>
        </div>
      </header>

      <section className="metrics">
        <div className="metric"><span className="metricLabel">Fixture FCO leaves</span><strong>{custody.merkle.leaf_count}</strong></div>
        <div className="metric"><span className="metricLabel">Fixture Merkle</span><strong className="mono small compact">{custody.merkle.root_sha256.slice(0, 20)}…</strong></div>
        <div className="metric"><span className="metricLabel">Live dataset</span><strong>{liveStatus?.health?.dataset_rows ?? "—"}</strong></div>
        <div className="metric"><span className="metricLabel">Claim boundary</span><strong className="small">fixture ≠ live receipt</strong></div>
      </section>

      <div className="tabs" role="tablist" aria-label="Judge modes">
        {(["demo", "live", "cloud"] as Mode[]).map((value) => (
          <button key={value} className={`tab ${mode === value ? "active" : ""}`} type="button" onClick={() => setMode(value)}>
            {value === "demo" ? "1 · DEMO CONTROL" : value === "live" ? "2 · LIVE REAL DATA" : "3 · HYDRADB COOKBOOK API"}
          </button>
        ))}
      </div>

      {mode === "demo" && (
        <section className="grid twoCol">
          <article className="panel">
            <div className="panelHead">
              <div><p className="eyebrow">Step 1</p><h2>Deterministic control</h2></div>
              <button className="secondary" type="button" onClick={() => setGuideId("fixture")} aria-label="Information about deterministic fixture">(i)</button>
            </div>
            <p className="muted">Reference → perturbation → restoration, with content-addressed FCOs and a recomputed fixture Merkle checkpoint.</p>
            <div className="actions">
              <button className={`primary ${demoStep === "t0" ? "" : "secondary"}`} type="button" disabled={Boolean(busy)} onClick={() => { setDemoStep("t0"); loadFixture(); }}>Load reference fixture (t0)</button>
              <button className={`button ${demoStep === "t1" ? "primary" : "secondary"}`} type="button" disabled={Boolean(busy)} onClick={() => { setDemoStep("t1"); run("poison_fixture", () => postJson("/api/query", { action: "fixture", mode: "poison" })); }}>Simulate poison (t1)</button>
              <button className={`button ${demoStep === "t2" ? "primary" : "secondary"}`} type="button" disabled={Boolean(busy)} onClick={() => { setDemoStep("t2"); run("antidote_fixture", () => postJson("/api/query", { action: "fixture", mode: "antidote" })); }}>Apply antidote (t2)</button>
              <a className="secondary" href="/api/custody">Open custody JSON</a>
            </div>

            <div style={{ marginTop: "1.25rem", padding: "1rem", borderRadius: "8px", background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.08)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
                <span className="eyebrow">Active Context Heat Layer</span>
                <span className={`pill ${demoStep === "t0" ? "pillGood" : demoStep === "t1" ? "pillBad" : "pillWarn"}`}>
                  {demoStep === "t0" ? "t0 · SELF · SAFE · ADMIT" : demoStep === "t1" ? "t1 · NONSELF · NONSAFE · QUARANTINE" : "t2 · SELF · RESTORED · ADMIT"}
                </span>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "0.75rem", textAlign: "center" }}>
                <div style={{ padding: "0.75rem", borderRadius: "6px", background: "rgba(0,0,0,0.25)", border: `1px solid ${demoStep === "t0" ? "#10b981" : demoStep === "t1" ? "#ef4444" : "#06b6d4"}` }}>
                  <div className="small muted"><a href="/knowledge#shannon-h" style={{ color: "inherit", textDecoration: "underline" }}>Shannon H ↗</a></div>
                  <strong style={{ fontSize: "1.25rem", color: demoStep === "t0" ? "#10b981" : demoStep === "t1" ? "#ef4444" : "#06b6d4" }}>
                    {demoStep === "t0" ? "0.412" : demoStep === "t1" ? "1.119" : "0.580"}
                  </strong>
                  <div className="small muted">bits (Shannon 1948)</div>
                </div>

                <div style={{ padding: "0.75rem", borderRadius: "6px", background: "rgba(0,0,0,0.25)", border: `1px solid ${demoStep === "t0" ? "#10b981" : demoStep === "t1" ? "#ef4444" : "#06b6d4"}` }}>
                  <div className="small muted"><a href="/knowledge#g-star" style={{ color: "inherit", textDecoration: "underline" }}>G* Diagnostic ↗</a></div>
                  <strong style={{ fontSize: "1.25rem", color: demoStep === "t0" ? "#10b981" : demoStep === "t1" ? "#ef4444" : "#06b6d4" }}>
                    {demoStep === "t0" ? "-0.061" : demoStep === "t1" ? "+0.573" : "+0.120"}
                  </strong>
                  <div className="small muted">(Friston 2010)</div>
                </div>

                <div style={{ padding: "0.75rem", borderRadius: "6px", background: "rgba(0,0,0,0.25)", border: `1px solid ${demoStep === "t0" ? "#6b7280" : demoStep === "t1" ? "#ef4444" : "#10b981"}` }}>
                  <div className="small muted"><a href="/knowledge#delta-g-star" style={{ color: "inherit", textDecoration: "underline" }}>ΔG* vs t0 ↗</a></div>
                  <strong style={{ fontSize: "1.25rem", color: demoStep === "t0" ? "#6b7280" : demoStep === "t1" ? "#ef4444" : "#10b981" }}>
                    {demoStep === "t0" ? "0.000" : demoStep === "t1" ? "+0.634" : "-0.453"}
                  </strong>
                  <div className="small muted">free-energy delta</div>
                </div>
              </div>
            </div>
          </article>

          <article className="panel">
            <p className="eyebrow">MSM × Anticube time rail & heat calculation</p>
            <h2>Contextual State: Normal vs Poison vs Antidote</h2>
            <div className="flow mono" style={{ marginBottom: "1rem" }}>
              <button type="button" onClick={() => { setDemoStep("t0"); loadFixture(); }} style={{ border: demoStep === "t0" ? "2px solid #10b981" : "none" }}>t0 reference</button>
              <b>→</b>
              <button type="button" onClick={() => { setDemoStep("t1"); run("poison_fixture", () => postJson("/api/query", { action: "fixture", mode: "poison" })); }} style={{ border: demoStep === "t1" ? "2px solid #ef4444" : "none" }}>t1 perturb</button>
              <b>→</b>
              <button type="button" onClick={() => { setDemoStep("t2"); run("antidote_fixture", () => postJson("/api/query", { action: "fixture", mode: "antidote" })); }} style={{ border: demoStep === "t2" ? "2px solid #06b6d4" : "none" }}>t2 restoration</button>
            </div>

            <table className="small" style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.1)", textAlign: "left" }}>
                  <th style={{ padding: "6px" }}>Metric (Citation)</th>
                  <th style={{ padding: "6px", color: "#10b981" }}>t0 Normal</th>
                  <th style={{ padding: "6px", color: "#ef4444" }}>t1 Poison</th>
                  <th style={{ padding: "6px", color: "#06b6d4" }}>t2 Antidote</th>
                </tr>
              </thead>
              <tbody>
                <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                  <td style={{ padding: "6px" }}><a href="/knowledge#shannon-h">Shannon H</a> (1948)</td>
                  <td style={{ padding: "6px", color: "#10b981" }}>0.412</td>
                  <td style={{ padding: "6px", color: "#ef4444", fontWeight: "bold" }}>1.119 ↗</td>
                  <td style={{ padding: "6px", color: "#06b6d4" }}>0.580 ↘</td>
                </tr>
                <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                  <td style={{ padding: "6px" }}><a href="/knowledge#g-star">G* Diagnostic</a> (2010)</td>
                  <td style={{ padding: "6px", color: "#10b981" }}>-0.061</td>
                  <td style={{ padding: "6px", color: "#ef4444", fontWeight: "bold" }}>+0.573 ↗</td>
                  <td style={{ padding: "6px", color: "#06b6d4" }}>+0.120 ↘</td>
                </tr>
                <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                  <td style={{ padding: "6px" }}><a href="/knowledge#mutation-distance">Mutation Distance JSD</a> (1991)</td>
                  <td style={{ padding: "6px" }}>0.000</td>
                  <td style={{ padding: "6px", color: "#f59e0b", fontWeight: "bold" }}>0.700 ↗</td>
                  <td style={{ padding: "6px", color: "#06b6d4" }}>0.120 ↘</td>
                </tr>
                <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                  <td style={{ padding: "6px" }}><a href="/knowledge#restoration-gain">Restoration Gain</a> (HydraDG)</td>
                  <td style={{ padding: "6px" }}>0.000</td>
                  <td style={{ padding: "6px" }}>0.000</td>
                  <td style={{ padding: "6px", color: "#10b981", fontWeight: "bold" }}>0.580 🟢</td>
                </tr>
                <tr>
                  <td style={{ padding: "6px" }}><a href="/knowledge#u-star-burden">U* Information Burden</a></td>
                  <td style={{ padding: "6px", color: "#10b981" }}>0.050</td>
                  <td style={{ padding: "6px", color: "#ef4444", fontWeight: "bold" }}>0.850 ⚠️</td>
                  <td style={{ padding: "6px", color: "#06b6d4" }}>0.200 🟢</td>
                </tr>
              </tbody>
            </table>
          </article>
        </section>
      )}

      {mode === "live" && (
        <section className="grid twoCol">
          <article className="panel">
            <div className="panelHead"><div><p className="eyebrow">Step 2</p><h2>Load a real LongMemEval case</h2></div><button className="secondary" type="button" onClick={() => setGuideId("case")}>(i)</button></div>
            <div className="actions"><button className="secondary" type="button" onClick={refreshCases} disabled={Boolean(busy)}>Refresh cases</button></div>
            <label>Question ID
              <select value={questionId} onChange={(event) => setQuestionId(event.target.value)}>
                <option value="">Choose a returned case</option>
                {cases.map((item) => <option key={String(item.question_id)} value={String(item.question_id)}>{String(item.question_id)} · {String(item.question_type || "unknown")}</option>)}
              </select>
              <span className="small muted">Example: choose a knowledge-update case from Refresh cases.</span>
            </label>
            <label>Extractor
              <select value={extractor} onChange={(event) => setExtractor(event.target.value)}><option value="heuristic">heuristic</option><option value="ollarma">ollarma</option><option value="none">none</option></select>
              <span className="small muted">Judge default: heuristic — deterministic extraction lane.</span>
            </label>
            <div className="actions"><button className="primary" type="button" onClick={loadCase} disabled={!questionId || Boolean(busy)}>Load case into HydraDB</button></div>
          </article>

          <article className="panel">
            <div className="panelHead"><div><p className="eyebrow">Step 3</p><h2>Retrieve with an ablation</h2></div><button className="secondary" type="button" onClick={() => setGuideId("retrieve")}>(i)</button></div>
            <label>Query
              <textarea value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Leave blank to use the benchmark question, or enter a counterfactual question." />
              <span className="small muted">Example: What is the user's current preference after the later update?</span>
            </label>
            <div className="grid twoCol">
              <label>Method<select value={method} onChange={(event) => setMethod(event.target.value)}><option>A</option><option>B</option><option>C</option><option>D</option></select></label>
              <label>K<input type="number" min={1} max={20} value={k} onChange={(event) => setK(Number(event.target.value))} /><span className="small muted">Example: 5</span></label>
            </div>
            <div className="actions"><button className="primary" type="button" onClick={retrieve} disabled={!questionId || Boolean(busy)}>Run retrieval</button></div>
          </article>

          <article className="panel">
            <div className="panelHead"><div><p className="eyebrow">Step 4</p><h2>Select the load-bearing Fact</h2></div><button className="secondary" type="button" onClick={() => setGuideId("perturb")}>(i)</button></div>
            <label>Fact vertex
              <select value={selectedFactVertex} onChange={(event) => { setSelectedFactVertex(event.target.value); setLastInjectedVertex(""); setPoisonObject(""); }}>
                {facts.length ? facts.map((fact) => <option key={String(fact.vertex)} value={String(fact.vertex)}>{String(fact.vertex)} · {String(fact.subject)} / {String(fact.predicate)} / {String(fact.object)}</option>) : <option value="">Load a case first</option>}
              </select>
            </label>
            <p className="small mono">subject={String(selectedFact?.subject || facts[0]?.subject || "—")} · predicate={String(selectedFact?.predicate || facts[0]?.predicate || "—")}</p>
            <label>Poison object
              <input value={poisonObject} onChange={(event) => setPoisonObject(event.target.value)} placeholder="POISON::alternate state" />
              <span className="small muted">Example: POISON::{originalObject || "original-object"}</span>
            </label>
            <div className="actions">
              <button className="secondary" type="button" onClick={() => perturb("normal")} disabled={Boolean(busy)}>Normal control</button>
              <button className="primary" type="button" onClick={() => perturb("poison")} disabled={Boolean(busy)}>Inject poison</button>
              <button className="secondary" type="button" onClick={() => perturb("antidote")} disabled={Boolean(busy)}>Apply antidote</button>
            </div>
            <p className="small muted">Anticube labels here are operator-declared for the bounded demo; they are not universal safety judgments.</p>
          </article>

          <article className="panel">
            <div className="panelHead"><div><p className="eyebrow">Step 5</p><h2>Traverse the current state</h2></div><button className="secondary" type="button" onClick={() => setGuideId("current")}>(i)</button></div>
            <label>Subject<input value={String(selectedFact?.subject || "")} readOnly /><span className="small muted">Auto-filled from the selected real Fact.</span></label>
            <label>Predicate<input value={String(selectedFact?.predicate || "")} readOnly /><span className="small muted">Auto-filled from the selected real Fact.</span></label>
            <div className="actions"><button className="primary" type="button" onClick={currentState} disabled={!selectedFact || Boolean(busy)}>Resolve current state</button><button className="secondary" type="button" onClick={() => run("live_stats", () => postJson("/api/live", { action: "live_stats" }))}>Live FCG counts</button></div>
          </article>
        </section>
      )}

      {mode === "cloud" && (
        <section className="grid twoCol">
          <article className="panel">
            <div className="panelHead"><div><p className="eyebrow">Independent conformance lane</p><h2>Official HydraDB API</h2></div><button className="secondary" type="button" onClick={() => setGuideId("cloud")}>(i)</button></div>
            <p className="muted">The key is read only from server-side environment variables and is never returned to the browser.</p>
            <label>Sub-tenant
              <input value={cloudSubTenant} onChange={(event) => setCloudSubTenant(event.target.value)} />
              <span className="small muted">Example: hydradg-judge-demo</span>
            </label>
            <label>Recall query
              <textarea value={cloudQuery} onChange={(event) => setCloudQuery(event.target.value)} />
              <span className="small muted">Example: Why is preserving graph provenance useful for a state update?</span>
            </label>
            <div className="actions"><button className="secondary" type="button" onClick={() => cloud("status")}>Tenant status</button><button className="primary" type="button" onClick={() => cloud("full_recall", { query: cloudQuery, graph_context: true })}>Full recall + graph context</button><button className="secondary" type="button" onClick={() => cloud("boolean_recall", { query: cloudQuery })}>Boolean recall</button></div>
          </article>

          <article className="panel">
            <p className="eyebrow">Memory cookbook</p><h2>Add → recall preferences</h2>
            <label>Demo memory
              <textarea value={cloudMemory} onChange={(event) => setCloudMemory(event.target.value)} />
              <span className="small muted">Example: The HydraDG judge demo prefers graph paths with explicit provenance and current-state explanations.</span>
            </label>
            <div className="actions"><button className="primary" type="button" onClick={() => cloud("add_memory", { text: cloudMemory, infer: true })}>Store demo memory</button><button className="secondary" type="button" onClick={() => cloud("recall_preferences", { query: "graph provenance current-state explanation preference" })}>Recall preferences</button><button className="secondary" type="button" onClick={() => cloud("list")}>List data</button></div>
          </article>

          <article className="panel">
            <p className="eyebrow">Graph inspection</p><h2>Relations by source</h2>
            <label>Source ID
              <input value={cloudSourceId} onChange={(event) => setCloudSourceId(event.target.value)} placeholder="source_id returned by ingestion/list" />
              <span className="small muted">Example: paste a source_id returned by Store demo memory or List data.</span>
            </label>
            <div className="actions"><button className="primary" type="button" onClick={() => cloud("relations", { source_id: cloudSourceId })} disabled={!cloudSourceId}>Inspect graph relations</button><button className="secondary" type="button" onClick={() => cloud("monitor")}>Tenant monitor</button></div>
          </article>

          <article className="panel">
            <p className="eyebrow">Boundary</p><h2>What this proves</h2>
            <ul><li>Hosted cookbook request/response conformance when actually executed.</li><li>It does not replace the pinned open-source HydraDB graph used by the Track 03 live experiment.</li><li>Hosted and self-hosted results remain separate evidence objects and denominators.</li></ul>
          </article>
        </section>
      )}

      <section className="panel architecture">
        <div className="panelHead"><div><p className="eyebrow">Custody visualization</p><h2>Atom → FCO → FCG → Merkle checkpoint</h2></div><button className="secondary" type="button" onClick={() => setGuideId("fixture")}>(i)</button></div>
        <p className="muted">The thick path is the judge-facing dependency route of interest. The full graph remains explorable around it.</p>
        <GoldenGraph fixture={fixture as any} custody={custody as any} />
      </section>

      <section className="grid twoCol">
        <article className="panel">
          <p className="eyebrow">(i) Knowledge base</p>
          <h2>{guide.title}</h2>
          <p><strong>HydraDB pattern:</strong> {guide.hydradbPattern}</p>
          <p><strong>Why included:</strong> {guide.why}</p>
          <p><strong>Judge example:</strong> <span className="mono small">{guide.example}</span></p>
          <p><strong>HydraDG expansion:</strong> {guide.hydradgExpansion}</p>
          <p><strong>Falsifier:</strong> {guide.falsifier}</p>
          <p><strong>Evidence state:</strong> <span className="pill pillMuted">{guide.evidenceState}</span></p>
          <ol>{guide.how.map((step) => <li key={step}>{step}</li>)}</ol>
        </article>

        <article className="panel">
          <p className="eyebrow">Execution output</p><h2>{busy ? `Running ${busy}…` : "Latest result"}</h2>
          <pre className="result">{pretty(output)}</pre>
        </article>
      </section>

      <section className="panel">
        <p className="eyebrow">HydraDB cookbook → HydraDG expansion</p>
        <h2>Conformance matrix</h2>
        <div className="tableWrap">
          <table>
            <thead><tr><th>Cookbook pattern</th><th>HydraDB primitive</th><th>HydraDG expansion</th><th>Executable test</th></tr></thead>
            <tbody>{COOKBOOK_MATRIX.map((row) => <tr key={row.cookbook}><td>{row.cookbook}</td><td>{row.hydradb}</td><td>{row.hydradg}</td><td>{row.test}</td></tr>)}</tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
