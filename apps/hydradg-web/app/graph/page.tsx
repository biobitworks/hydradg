"use client";

import {
  PointerEvent as ReactPointerEvent,
  WheelEvent as ReactWheelEvent,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import StateCalculationPanel, { AnticubeConsideration, STATE_VISUALS } from "@/components/StateCalculationPanel";
import { addContextIcebergScores } from "@/lib/contextIceberg";
import { knowledgeTerm } from "@/lib/knowledgeLinks";

type SceneNode = {
  id: string;
  label: string;
  x: number;
  y: number;
  z: number;
  t: number;
  access: "public" | "toy-locked";
  payload: Record<string, unknown>;
};

type SceneLink = { source: string; target: string; relation: string };
type Timeline = {
  t: number;
  label: string;
  distribution: readonly number[];
  shannon_entropy: number;
  normalized_entropy: number;
  g_star: number;
  delta_g_star: number;
  mutation_distance: number;
  restoration_gain: number;
  burden: number;
};

type FixtureResponse = {
  fixture?: {
    state_field_contract: string;
    scene: { nodes: SceneNode[]; links: SceneLink[] };
    timeline: Timeline[];
  };
  error?: string;
};

type Projected = { id: string; px: number; py: number; depth: number };
type HeatMode = "mutation" | "restoration" | "delta";

function fcoHash(id: string) {
  return id.startsWith("fco:") && /^[0-9a-f]{64}$/i.test(id.slice(4)) ? id.slice(4) : "";
}

function metricHeat(metric: ReturnType<typeof addContextIcebergScores<Timeline>>[number], mode: HeatMode) {
  if (mode === "mutation") return metric.mutation_distance;
  if (mode === "restoration") return metric.restoration_gain;
  return Math.min(1, Math.abs(metric.delta_g_star));
}

function anticubeConsideration(selected: SceneNode | null, data: FixtureResponse["fixture"] | null): AnticubeConsideration {
  if (!selected || !data) return { status: "UNKNOWN / NOT_EVALUATED", note: "Select an FCO to inspect whether an Anticube ClassificationReceipt exists." };
  const receipt = selected.label === "ClassificationReceipt"
    ? selected
    : data.scene.nodes.find((candidate) => candidate.label === "ClassificationReceipt" && String(candidate.payload.subject_id || "") === selected.id);

  if (!receipt) {
    return {
      status: "UNKNOWN / NOT_EVALUATED",
      note: "No ClassificationReceipt is attached to this FCO in the bounded demo graph. No SELF/NONSELF or SAFE/NONSAFE class is inferred from its state, label, or color.",
    };
  }

  const classifierState = String(receipt.payload.classifier_state || "UNKNOWN");
  const claimCeiling = String(receipt.payload.claim_ceiling || "UNDECLARED");
  const executed = claimCeiling !== "CLASSIFICATION_NOT_EXECUTED" && !classifierState.includes("PENDING");
  const recorded = String(receipt.payload.classification || receipt.payload.anticube_classification || "");
  return {
    status: executed && recorded ? recorded : "UNKNOWN / NOT_EXECUTED",
    receiptId: receipt.id,
    classifierState,
    claimCeiling,
    note: executed
      ? "An explicit Anticube classification receipt is attached; inspect the receipt before reusing the classification."
      : "Anticube was considered through an explicit ClassificationReceipt, but the fixture records classification as not executed. HydraDG therefore retains UNKNOWN instead of inferring safety from Reference/Poison/Antidote state labels.",
  };
}

export default function GraphPage() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const projectedRef = useRef<Projected[]>([]);
  const dragRef = useRef({ active: false, moved: false, x: 0, y: 0 });
  const [data, setData] = useState<FixtureResponse["fixture"] | null>(null);
  const [error, setError] = useState("");
  const [time, setTime] = useState(2);
  const [yaw, setYaw] = useState(0.45);
  const [pitch, setPitch] = useState(-0.25);
  const [zoom, setZoom] = useState(260);
  const [selectedId, setSelectedId] = useState("");
  const [query, setQuery] = useState("");
  const [heatMode, setHeatMode] = useState<HeatMode>("mutation");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setQuery(params.get("q") || "");
    setSelectedId(params.get("node") || "");
  }, []);

  useEffect(() => {
    fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "fixture" }),
    })
      .then(async (response) => {
        const payload = (await response.json()) as FixtureResponse;
        if (!response.ok || payload.error || !payload.fixture) throw new Error(payload.error || "fixture unavailable");
        return payload.fixture;
      })
      .then((fixture) => {
        setData(fixture);
        setTime(Math.max(...fixture.timeline.map((state) => state.t)));
        setError("");
      })
      .catch((caught) => setError(caught instanceof Error ? caught.message : String(caught)));
  }, []);

  const timeline = useMemo(() => (data ? addContextIcebergScores(data.timeline) : []), [data]);
  const maxTime = timeline.length ? Math.max(...timeline.map((state) => state.t)) : 2;
  const current = timeline.find((state) => state.t === time) || null;
  const selected = data?.scene.nodes.find((node) => node.id === selectedId) || null;
  const selectedState = selected ? timeline.find((state) => state.t === selected.t) || null : null;
  const selectedHash = selected ? fcoHash(selected.id) : "";
  const selectedTerm = selected ? knowledgeTerm(selected.label) : undefined;
  const selectedLinks = selected && data
    ? data.scene.links.filter((link) => link.source === selected.id || link.target === selected.id)
    : [];
  const selectedAnticube = anticubeConsideration(selected, data);

  const matching = useMemo(() => {
    if (!data) return new Set<string>();
    const needle = query.trim().toLowerCase();
    if (!needle) return new Set(data.scene.nodes.map((node) => node.id));
    return new Set(data.scene.nodes.filter((node) => JSON.stringify(node).toLowerCase().includes(needle)).map((node) => node.id));
  }, [data, query]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !data || !current) return;
    const context = canvas.getContext("2d");
    if (!context) return;

    const ratio = Math.max(1, window.devicePixelRatio || 1);
    const width = canvas.clientWidth || 900;
    const height = canvas.clientHeight || 560;
    canvas.width = Math.floor(width * ratio);
    canvas.height = Math.floor(height * ratio);
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.clearRect(0, 0, width, height);

    const activeVisual = STATE_VISUALS[time] || STATE_VISUALS[0];
    const ambient = context.createRadialGradient(width / 2, height / 2, 30, width / 2, height / 2, Math.max(width, height) * 0.55);
    ambient.addColorStop(0, `hsla(${activeVisual.hue}, 80%, 55%, ${0.06 + current.cloud_drift_0_100 / 1200})`);
    ambient.addColorStop(1, `hsla(${activeVisual.hue}, 70%, 30%, 0)`);
    context.fillStyle = ambient;
    context.fillRect(0, 0, width, height);

    const visible = data.scene.nodes.filter((node) => node.t <= time);
    const visibleIds = new Set(visible.map((node) => node.id));
    const projected = new Map<string, Projected>();

    for (const node of visible) {
      const cosY = Math.cos(yaw);
      const sinY = Math.sin(yaw);
      const x1 = node.x * cosY - node.z * sinY;
      const z1 = node.x * sinY + node.z * cosY;
      const cosP = Math.cos(pitch);
      const sinP = Math.sin(pitch);
      const y2 = node.y * cosP - z1 * sinP;
      const z2 = node.y * sinP + z1 * cosP;
      const perspective = zoom / Math.max(1.2, 3.2 - z2);
      projected.set(node.id, { id: node.id, px: width / 2 + x1 * perspective, py: height / 2 + y2 * perspective, depth: z2 });
    }

    for (const link of data.scene.links) {
      if (!visibleIds.has(link.source) || !visibleIds.has(link.target)) continue;
      const a = projected.get(link.source);
      const b = projected.get(link.target);
      if (!a || !b) continue;
      context.globalAlpha = 0.3;
      context.strokeStyle = "#82909f";
      context.lineWidth = 1;
      context.beginPath();
      context.moveTo(a.px, a.py);
      context.lineTo(b.px, b.py);
      context.stroke();
    }

    const ordered = [...visible].sort((a, b) => (projected.get(a.id)?.depth || 0) - (projected.get(b.id)?.depth || 0));
    const hits: Projected[] = [];
    for (const node of ordered) {
      const point = projected.get(node.id);
      if (!point) continue;
      const state = timeline.find((candidate) => candidate.t === node.t) || current;
      const visual = STATE_VISUALS[node.t] || STATE_VISUALS[0];
      const heat = Math.max(0, Math.min(1, metricHeat(state, heatMode)));
      const selectedNode = selectedId === node.id;
      const isMatch = matching.has(node.id);
      const radius = selectedNode ? 11 : node.label === "StateSnapshot" ? 9 : 6;
      const halo = radius + 5 + heat * 18;

      context.globalAlpha = isMatch ? 0.12 + heat * 0.18 : 0.04;
      context.fillStyle = visual.color;
      context.beginPath();
      context.arc(point.px, point.py, halo, 0, Math.PI * 2);
      context.fill();

      context.globalAlpha = selectedNode ? 1 : isMatch ? 0.92 : 0.22;
      context.fillStyle = visual.color;
      context.beginPath();
      context.arc(point.px, point.py, radius, 0, Math.PI * 2);
      context.fill();

      if (selectedNode) {
        context.strokeStyle = "#ffffff";
        context.lineWidth = 2.5;
        context.stroke();
      }
      if (isMatch && (selectedNode || node.label === "StateSnapshot")) {
        context.globalAlpha = 0.96;
        context.fillStyle = "#ffffff";
        context.font = "11px ui-monospace, SFMono-Regular, Menlo, monospace";
        context.fillText(`${node.label} · t${node.t}`, point.px + 12, point.py - 8);
      }
      hits.push(point);
    }
    context.globalAlpha = 1;
    projectedRef.current = hits;
  }, [data, current, timeline, time, yaw, pitch, zoom, selectedId, matching, heatMode]);

  function onPointerDown(event: ReactPointerEvent<HTMLCanvasElement>) {
    event.currentTarget.setPointerCapture(event.pointerId);
    dragRef.current = { active: true, moved: false, x: event.clientX, y: event.clientY };
  }

  function onPointerMove(event: ReactPointerEvent<HTMLCanvasElement>) {
    if (!dragRef.current.active) return;
    const dx = event.clientX - dragRef.current.x;
    const dy = event.clientY - dragRef.current.y;
    if (Math.abs(dx) + Math.abs(dy) > 2) dragRef.current.moved = true;
    dragRef.current.x = event.clientX;
    dragRef.current.y = event.clientY;
    setYaw((value) => value + dx * 0.008);
    setPitch((value) => Math.max(-1.3, Math.min(1.3, value + dy * 0.008)));
  }

  function onPointerUp(event: ReactPointerEvent<HTMLCanvasElement>) {
    const moved = dragRef.current.moved;
    dragRef.current.active = false;
    if (moved) return;
    const rect = event.currentTarget.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    const hit = projectedRef.current
      .map((point) => ({ point, distance: Math.hypot(point.px - x, point.py - y) }))
      .filter(({ distance }) => distance <= 18)
      .sort((a, b) => a.distance - b.distance)[0];
    if (!hit) return;
    setSelectedId(hit.point.id);
    const clicked = data?.scene.nodes.find((node) => node.id === hit.point.id);
    if (clicked) setTime(clicked.t);
  }

  function onWheel(event: ReactWheelEvent<HTMLCanvasElement>) {
    event.preventDefault();
    setZoom((value) => Math.max(120, Math.min(650, value - event.deltaY * 0.35)));
  }

  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">4D Fractal Custody Graph</p>
          <h1>Reference, poison and antidote stay distinguishable.</h1>
          <p className="lede">Rotate x/y/z, scrub time, click one FCO, and inspect its state calculations, classification color, Anticube consideration, canonical SHA-256 identity, and graph relationships together.</p>
          <div className="actions">
            <a className="secondary" href="/how-to">How to use</a>
            <a className="secondary" href="/knowledge">Knowledge Base</a>
            <a className="secondary" href="/track-fit">Why Graph? + math</a>
            <a className="secondary" href="/graph?q=KnowledgeAtom">KnowledgeAtom</a>
            <a className="secondary" href="/graph?q=SeedOfTruth">SeedOfTruth</a>
          </div>
        </div>
      </header>

      {error ? <section className="panel"><strong>Graph unavailable:</strong> {error}</section> : null}

      <section className="panel">
        <p className="eyebrow">State color contract</p>
        <div className="grid threeCol">
          {Object.entries(STATE_VISUALS).map(([key, state]) => (
            <article key={key} className="panel">
              <div style={{ width: 20, height: 20, borderRadius: "50%", background: state.color, marginBottom: 8 }} aria-hidden="true" />
              <strong style={{ color: state.color }}>t{key} · {state.name}</strong>
              <p className="small muted">{state.meaning}</p>
            </article>
          ))}
        </div>
        <p className="small muted note">Color identifies declared Reference/Poison/Antidote state. Heat intensity is selected separately. Anticube SELF/NONSELF × SAFE/NONSAFE classification is an independent receipt-based lane and is never inferred from these colors.</p>
      </section>

      <section className="grid twoCol">
        <article className="panel">
          <div className="panelHead"><div><p className="eyebrow">FCG navigation</p><h2>x · y · z · time</h2></div><span className="pill pillMuted">deterministic fixture</span></div>
          <label>Search visible FCOs<input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="KnowledgeAtom, SeedOfTruth, source…" /></label>
          <div className="actions">
            <button className={heatMode === "mutation" ? "tab active" : "tab"} onClick={() => setHeatMode("mutation")}>mutation distance</button>
            <button className={heatMode === "restoration" ? "tab active" : "tab"} onClick={() => setHeatMode("restoration")}>restoration gain</button>
            <button className={heatMode === "delta" ? "tab active" : "tab"} onClick={() => setHeatMode("delta")}>|ΔG*|</button>
          </div>
          <canvas
            ref={canvasRef}
            aria-label="Interactive four-dimensional FCG projection with violet reference, orange poison and blue antidote states"
            style={{ width: "100%", height: 560, border: "1px solid var(--line)", borderRadius: 12, touchAction: "none", background: "#090c10" }}
            onPointerDown={onPointerDown}
            onPointerMove={onPointerMove}
            onPointerUp={onPointerUp}
            onPointerCancel={() => { dragRef.current.active = false; }}
            onWheel={onWheel}
          />
          <label style={{ marginTop: 14 }}>Time / graph state: t{time} — {STATE_VISUALS[time]?.name || current?.label || "state"}<input type="range" min={0} max={maxTime} step={1} value={time} onChange={(event) => setTime(Number(event.target.value))} /></label>
        </article>

        <article className="panel">
          <p className="eyebrow">Selected FCO</p>
          <h2>{selected?.label || "Select a node"}</h2>
          {selected ? (
            <>
              <div className="actions">
                <a className="secondary" href={`/fco/${encodeURIComponent(selected.id)}`}>Open FCO inspector</a>
                {selectedTerm ? <a className="secondary" href={`/knowledge#${selectedTerm.slug}`}>KB: {selectedTerm.term}</a> : null}
                {selectedHash ? <a className="secondary" href={`/evidence?sha=${selectedHash}`}>Evidence by hash</a> : null}
              </div>
              <p className="mono small compact">{selected.id}</p>
              <p className="mono small compact">object_sha256={selectedHash || "noncanonical-demo-id"}</p>
              <p className="small muted">state={STATE_VISUALS[selected.t]?.name || `t${selected.t}`} · context scope={selected.label === "StateSnapshot" ? "OBJECT_STATE_SNAPSHOT" : "STATE_INHERITED"} · FCG degree={selectedLinks.length}</p>
              {selectedState ? <StateCalculationPanel state={selectedState} scope={selected.label === "StateSnapshot" ? "OBJECT_STATE_SNAPSHOT" : "STATE_INHERITED"} anticube={selectedAnticube} /> : null}
              <details style={{ marginTop: 14 }}>
                <summary>Declared FCO payload</summary>
                <pre className="result">{selected.access === "public" ? JSON.stringify(selected.payload, null, 2) : "TOY_LOCKED — demonstration payload intentionally hidden; not production cryptography."}</pre>
              </details>
            </>
          ) : <div className="result empty">Click a node. The inspector will show state math, classification color, Anticube consideration, one FCO ID and one matching object SHA-256.</div>}
        </article>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">STATE TABLE</span>
        <h2 className="displayTitle">The walkthrough calculations are visible beside the 4D state.</h2>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead><tr><th align="left">State</th><th>H</th><th>G*</th><th>ΔG*</th><th>Cloud Drift</th><th>TV mutation</th><th>Restoration gain</th><th>U*</th></tr></thead>
            <tbody>
              {timeline.map((state) => {
                const color = STATE_VISUALS[state.t]?.color || "#d8e0e8";
                const valueStyle = { color, fontWeight: 700, background: `${color}12` } as const;
                return (
                  <tr key={state.t} style={{ borderLeft: `3px solid ${color}` }}>
                    <td><strong style={{ color }}>{STATE_VISUALS[state.t]?.name || state.label}</strong></td>
                    <td align="center" style={valueStyle}>{state.shannon_entropy.toFixed(4)}</td>
                    <td align="center" style={valueStyle}>{state.g_star.toFixed(6)}</td>
                    <td align="center" style={valueStyle}>{state.delta_g_star >= 0 ? "+" : ""}{state.delta_g_star.toFixed(6)}</td>
                    <td align="center" style={valueStyle}>{state.cloud_drift_0_100.toFixed(4)}</td>
                    <td align="center" style={valueStyle}>{state.mutation_distance.toFixed(4)}</td>
                    <td align="center" style={valueStyle}>{state.restoration_gain.toFixed(4)}</td>
                    <td align="center" style={valueStyle}>{state.burden.toFixed(2)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <p className="small muted note">T0–T2 are synthetic distribution-state calculations. T3–T5 use migration/experiment/release measurements instead of copying the T2 scalar forward; see Why Graph? and Evolution for those measured production lanes.</p>
      </section>

      <section className="panel architecture">
        <p className="eyebrow">Claim boundary</p>
        <h2>Visualization is evidence-linked, not evidence-generating.</h2>
        <p className="muted">G* = U* - 0.35 × Hnorm. Cloud Drift = 100 × base-2 JSD. Mutation distance and restoration gain use the separate total-variation lane. Anticube classification is receipt-based and separate. None of these is physical Gibbs free energy or an end-to-end QA score.</p>
        <div className="actions"><a className="secondary" href="/knowledge#g-star">KB: G*</a><a className="secondary" href="/knowledge#cloud-drift">KB: Cloud Drift</a><a className="secondary" href="/knowledge#anticube">KB: Anticube</a><a className="secondary" href="/track-fit">Show the project math</a></div>
      </section>
    </main>
  );
}
