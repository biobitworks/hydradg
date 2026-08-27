"use client";

import { PointerEvent, WheelEvent, useEffect, useMemo, useRef, useState } from "react";

import Breadcrumbs from "@/components/Breadcrumbs";
import { KNOWLEDGE_TERMS, knowledgeTerm } from "@/lib/knowledgeLinks";

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

function fcoHash(id: string) {
  return id.startsWith("fco:") && /^[0-9a-f]{64}$/i.test(id.slice(4)) ? id.slice(4) : "";
}

export default function GraphPage() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const canvasWrapRef = useRef<HTMLDivElement | null>(null);
  const projectedRef = useRef<Projected[]>([]);
  const dragRef = useRef({ active: false, moved: false, x: 0, y: 0 });
  const [data, setData] = useState<FixtureResponse["fixture"] | null>(null);
  const [error, setError] = useState("");
  const [time, setTime] = useState(2);
  const [yaw, setYaw] = useState(0.45);
  const [pitch, setPitch] = useState(-0.25);
  const [zoom, setZoom] = useState(260);
  const [canvasHeight, setCanvasHeight] = useState(560);
  const [viewportNarrow, setViewportNarrow] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);
  const [selectedId, setSelectedId] = useState<string>("");
  const [unlocked, setUnlocked] = useState<Set<string>>(new Set());
  const [query, setQuery] = useState("");
  const [heatMode, setHeatMode] = useState<"mutation" | "restoration" | "delta">("mutation");

  useEffect(() => {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams(window.location.search);
    const q = params.get("q");
    const node = params.get("node");
    if (q) setQuery(q);
    if (node) setSelectedId(node);
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReducedMotion(mq.matches);
    const fn = () => setReducedMotion(mq.matches);
    mq.addEventListener("change", fn);
    return () => mq.removeEventListener("change", fn);
  }, []);

  useEffect(() => {
    const el = canvasWrapRef.current;
    if (!el || typeof ResizeObserver === "undefined") return;
    const measure = () => {
      const w = el.clientWidth;
      setViewportNarrow(w < 720);
      setCanvasHeight(w < 520 ? 300 : w < 900 ? 420 : 560);
    };
    measure();
    const ro = new ResizeObserver(() => measure());
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  function resetView() {
    setYaw(0.45);
    setPitch(-0.25);
    setZoom(viewportNarrow ? 200 : 260);
  }

  useEffect(() => {
    fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "fixture" }),
    })
      .then((response) => response.json())
      .then((response: FixtureResponse) => {
        if (response.error || !response.fixture) throw new Error(response.error || "fixture unavailable");
        setData(response.fixture);
        setTime(Math.max(...response.fixture.timeline.map((state) => state.t)));
      })
      .catch((caught) => setError(caught instanceof Error ? caught.message : String(caught)));
  }, []);

  const selected = useMemo(
    () => data?.scene.nodes.find((node) => node.id === selectedId) || null,
    [data, selectedId],
  );

  const selectedHash = selected ? fcoHash(selected.id) : "";
  const selectedTerm = selected ? knowledgeTerm(selected.label) : undefined;
  const selectedLinks = useMemo(
    () => data?.scene.links.filter((link) => link.source === selectedId || link.target === selectedId) || [],
    [data, selectedId],
  );
  const selectedSourceRef = typeof selected?.payload.source_ref === "string" ? selected.payload.source_ref : "";
  const selectedSourceNode = selectedSourceRef && data
    ? data.scene.nodes.find((node) => node.id === selectedSourceRef) || null
    : null;

  const matching = useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (!needle || !data) return new Set(data?.scene.nodes.map((node) => node.id) || []);
    return new Set(
      data.scene.nodes
        .filter((node) => JSON.stringify(node).toLowerCase().includes(needle))
        .map((node) => node.id),
    );
  }, [data, query]);

  const activeMetric = useMemo(() => {
    if (selected) {
      const nodeMetric = data?.timeline.find((state) => state.t === selected.t);
      if (nodeMetric) return nodeMetric;
    }
    return data?.timeline.find((state) => state.t === time) || null;
  }, [data, selected, time]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !data) return;
    const context = canvas.getContext("2d");
    if (!context) return;

    const ratio = Math.max(1, window.devicePixelRatio || 1);
    const width = canvas.clientWidth || 900;
    const height = canvas.clientHeight || 560;
    canvas.width = Math.floor(width * ratio);
    canvas.height = Math.floor(height * ratio);
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.clearRect(0, 0, width, height);

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
      projected.set(node.id, {
        id: node.id,
        px: width / 2 + x1 * perspective,
        py: height / 2 + y2 * perspective,
        depth: z2,
      });
    }

    context.lineWidth = 1;
    for (const link of data.scene.links) {
      if (!visibleIds.has(link.source) || !visibleIds.has(link.target)) continue;
      const a = projected.get(link.source);
      const b = projected.get(link.target);
      if (!a || !b) continue;
      context.globalAlpha = 0.32;
      context.strokeStyle = "#82909f";
      context.beginPath();
      context.moveTo(a.px, a.py);
      context.lineTo(b.px, b.py);
      context.stroke();
    }

    const ordered = [...visible].sort(
      (a, b) => (projected.get(a.id)?.depth || 0) - (projected.get(b.id)?.depth || 0),
    );
    const clickTargets: Projected[] = [];
    for (const node of ordered) {
      const point = projected.get(node.id);
      if (!point) continue;
      const isMatch = matching.has(node.id);
      const isSelected = selectedId === node.id;
      const radius = isSelected ? 11 : node.label === "StateSnapshot" ? 9 : 7;

      const nodeMetric = data.timeline.find((state) => state.t === node.t);
      const nodeHeat = nodeMetric
        ? heatMode === "mutation"
          ? nodeMetric.mutation_distance
          : heatMode === "restoration"
            ? nodeMetric.restoration_gain
            : Math.min(1, Math.abs(nodeMetric.delta_g_star))
        : 0;

      const hue = heatMode === "restoration" ? 145 : heatMode === "delta" ? 275 : 18;
      const saturation = Math.round(40 + nodeHeat * 55);
      const lightness = Math.round(65 - nodeHeat * 25);

      context.globalAlpha = isSelected ? 1.0 : isMatch ? 0.90 : 0.20;
      context.fillStyle = isSelected
        ? `hsl(${hue} 95% 55%)`
        : `hsl(${hue} ${saturation}% ${lightness}%)`;
      context.beginPath();
      context.arc(point.px, point.py, radius, 0, Math.PI * 2);
      context.fill();

      if (isSelected) {
        context.strokeStyle = "#ffffff";
        context.lineWidth = 2.5;
        context.stroke();
      }
      if (isMatch && (isSelected || node.label === "StateSnapshot")) {
        context.globalAlpha = 0.95;
        context.fillStyle = "#ffffff";
        context.font = "11px ui-monospace, SFMono-Regular, Menlo, monospace";
        context.fillText(`${node.label} · t${node.t}`, point.px + 12, point.py - 8);
      }
      clickTargets.push(point);
    }
    context.globalAlpha = 1;
    projectedRef.current = clickTargets;
  }, [data, time, yaw, pitch, zoom, matching, selectedId, heatMode]);

  function onPointerDown(event: PointerEvent<HTMLCanvasElement>) {
    event.currentTarget.setPointerCapture(event.pointerId);
    dragRef.current = { active: true, moved: false, x: event.clientX, y: event.clientY };
  }

  function onPointerMove(event: PointerEvent<HTMLCanvasElement>) {
    if (!dragRef.current.active) return;
    const dx = event.clientX - dragRef.current.x;
    const dy = event.clientY - dragRef.current.y;
    if (Math.abs(dx) + Math.abs(dy) > 2) dragRef.current.moved = true;
    dragRef.current.x = event.clientX;
    dragRef.current.y = event.clientY;
    if (reducedMotion) return;
    const yawSens = viewportNarrow ? 0.004 : 0.008;
    const pitchSens = viewportNarrow ? 0.004 : 0.008;
    const pitchMax = viewportNarrow ? 0.55 : 1.3;
    setYaw((value) => value + dx * yawSens);
    setPitch((value) => Math.max(-pitchMax, Math.min(pitchMax, value + dy * pitchSens)));
  }

  function onPointerUp(event: PointerEvent<HTMLCanvasElement>) {
    const moved = dragRef.current.moved;
    dragRef.current.active = false;
    if (moved) return;
    const rect = event.currentTarget.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    const hit = projectedRef.current
      .map((point) => ({ point, distance: Math.hypot(point.px - x, point.py - y) }))
      .filter(({ distance }) => distance <= 16)
      .sort((a, b) => a.distance - b.distance)[0];
    if (hit) {
      setSelectedId(hit.point.id);
      const clicked = data?.scene.nodes.find((node) => node.id === hit.point.id);
      if (clicked && typeof clicked.t === "number") {
        setTime(clicked.t);
      }
    }
  }

  function onWheel(event: WheelEvent<HTMLCanvasElement>) {
    event.preventDefault();
    const maxZoom = viewportNarrow ? 420 : 650;
    setZoom((value) => Math.max(120, Math.min(maxZoom, value - event.deltaY * 0.35)));
  }

  function toggleToyLock() {
    if (!selected) return;
    setUnlocked((previous) => {
      const next = new Set(previous);
      if (next.has(selected.id)) next.delete(selected.id);
      else next.add(selected.id);
      return next;
    });
  }

  function speakSelected() {
    if (!selected || typeof window === "undefined" || !("speechSynthesis" in window)) return;
    const payloadVisible = selected.access === "public" || unlocked.has(selected.id);
    const text = payloadVisible
      ? `${selected.label}. ${String(selected.payload.statement || selected.payload.state_label || selected.id)}`
      : `${selected.label}. This demonstration node is locked.`;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(new SpeechSynthesisUtterance(text));
  }

  const payloadVisible = selected && (selected.access === "public" || unlocked.has(selected.id));

  return (
    <main>
      <Breadcrumbs
        items={[
          { label: "Home", href: "/" },
          { label: "4D FCG Graph Explorer" },
        ]}
        summaryText="Rotate 3D spatial dimensions, scrub time t0..t2, click any FCO node to inspect state calculations (H, G*, ΔG*), and follow graph dependency edges."
      />

      <nav>
        <a href="/">MVP</a>
        <a href="/judge">Judge Lab</a>
        <a href="/graph">4D FCG</a>
        <a href="/knowledge">Knowledge</a>
        <a href="/demo">Demo + video</a>
        <a href="/eligibility">Submission custody</a>
      </nav>

      <header className="hero">
        <div>
          <p className="eyebrow">4D Fractal Custody Graph</p>
          <h1>State field</h1>
          <p className="lede">
            Drag to rotate the three spatial dimensions, scroll or pinch to change scale, move the time
            slider through graph history, and select an FCO to inspect who/what touched it and where it came from.
          </p>
        </div>
      </header>

      {error ? <section className="panel"><strong>Graph unavailable:</strong> {error}</section> : null}

      <section className="panel">
        <p className="eyebrow">Linked terminology</p>
        <div className="actions">
          {KNOWLEDGE_TERMS.map((item) => (
            <a className="secondary" href={`/knowledge#${item.slug}`} key={item.slug}>{item.term}</a>
          ))}
        </div>
      </section>

      <section className="grid twoCol">
        <article className="panel">
          <div className="panelHead">
            <div>
              <p className="eyebrow">FCG navigation</p>
              <h2>x · y · z · time</h2>
            </div>
            <span className="pill pillMuted">HydraDB-backed fixture</span>
          </div>
          <label>
            Search visible FCOs
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="source, atom, seed, state…" />
          </label>
          <div className="actions">
            <button className={heatMode === "mutation" ? "tab active" : "tab"} onClick={() => setHeatMode("mutation")}>mutation</button>
            <button className={heatMode === "restoration" ? "tab active" : "tab"} onClick={() => setHeatMode("restoration")}>restoration</button>
            <button className={heatMode === "delta" ? "tab active" : "tab"} onClick={() => setHeatMode("delta")}>|ΔG*|</button>
            <button className="secondary" type="button" onClick={resetView}>Reset view</button>
          </div>
          <div ref={canvasWrapRef} style={{ width: "100%" }}>
            <canvas
              ref={canvasRef}
              aria-label="Interactive four-dimensional FCG projection"
              style={{ width: "100%", height: canvasHeight, border: "1px solid var(--line)", borderRadius: 12, touchAction: "none", background: "#090c10" }}
              onPointerDown={onPointerDown}
              onPointerMove={onPointerMove}
              onPointerUp={onPointerUp}
              onPointerCancel={() => { dragRef.current.active = false; }}
              onWheel={onWheel}
            />
          </div>
          <label style={{ marginTop: 14 }}>
            Time / graph state: t{time} — {activeMetric?.label || "loading"}
            <input type="range" min={0} max={2} step={1} value={time} onChange={(event) => setTime(Number(event.target.value))} />
          </label>
        </article>

        <article className="panel">
          <p className="eyebrow">Information-state heat layer</p>
          <h2>Mutation → restoration</h2>
          <div className="metrics" style={{ gridTemplateColumns: "repeat(2, minmax(0,1fr))" }}>
            <div className="metric">
              <span className="metricLabel">
                <a href="/knowledge#shannon-h" title="Knowledge Base: Shannon 1948 Citation & Formula">Shannon H ↗</a>
              </span>
              <strong>{activeMetric?.shannon_entropy.toFixed(3) ?? "—"}</strong>
              <span className="small muted"><a href="/graph?q=StateSnapshot" className="mono compact">FCG: StateSnapshot</a></span>
            </div>
            <div className="metric">
              <span className="metricLabel">
                <a href="/knowledge#g-star" title="Knowledge Base: Friston Free Energy Citation">G* ↗</a>
              </span>
              <strong>{activeMetric?.g_star.toFixed(3) ?? "—"}</strong>
              <span className="small muted"><a href="/graph?q=g_star" className="mono compact">FCG: HydraDB G*</a></span>
            </div>
            <div className="metric">
              <span className="metricLabel">
                <a href="/knowledge#delta-g-star" title="Knowledge Base: Lin 1991 Citation & Formula">ΔG* ↗</a>
              </span>
              <strong>{activeMetric?.delta_g_star.toFixed(3) ?? "—"}</strong>
              <span className="small muted"><a href="/graph?q=delta_g_star" className="mono compact">FCG: ΔG* edge</a></span>
            </div>
            <div className="metric">
              <span className="metricLabel">
                <a href="/knowledge#mutation-distance" title="Knowledge Base: JSD Citation & Formula">Mutation ↗</a>
              </span>
              <strong>{activeMetric?.mutation_distance.toFixed(3) ?? "—"}</strong>
              <span className="small muted"><a href="/graph?q=mutation" className="mono compact">FCG: Mutation JSD</a></span>
            </div>
            <div className="metric">
              <span className="metricLabel">
                <a href="/knowledge#restoration-gain" title="Knowledge Base: Antidote Gain Citation">Restoration ↗</a>
              </span>
              <strong>{activeMetric?.restoration_gain.toFixed(3) ?? "—"}</strong>
              <span className="small muted"><a href="/graph?q=restoration" className="mono compact">FCG: Antidote Gain</a></span>
            </div>
            <div className="metric">
              <span className="metricLabel">
                <a href="/knowledge#u-star-burden" title="Knowledge Base: Perturbation Burden Formula">U* burden ↗</a>
              </span>
              <strong>{activeMetric?.burden.toFixed(3) ?? "—"}</strong>
              <span className="small muted"><a href="/graph?q=burden" className="mono compact">FCG: U* Burden</a></span>
            </div>
          </div>
          <p className="small muted note">
            H is Shannon entropy (<a href="/knowledge#shannon-h">Shannon 1948</a>). G* and ΔG* are dimensionless information-state abstractions (<a href="/knowledge#g-star">Friston 2010</a>; <a href="/knowledge#delta-g-star">Lin 1991</a>); they are not physical Gibbs free energy and carry no kcal/mol or joule claim.
          </p>

          <div className="panel" style={{ marginTop: 18 }}>
            <p className="eyebrow">Selected FCO</p>
            <h3>{selected?.label || "Select a node"}</h3>
            {selected ? (
              <>
                <div className="actions">
                  {selectedTerm ? <a className="secondary" href={`/knowledge#${selectedTerm.slug}`}>How to: {selectedTerm.term}</a> : null}
                  <a className="secondary" href={`/graph?node=${encodeURIComponent(selected.id)}`}>Permalink</a>
                  {selectedHash ? <a className="secondary" href={`/evidence?sha=${selectedHash}`}>Evidence by hash</a> : null}
                </div>
                <p className="mono small compact">{selected.id}</p>
                {selectedHash ? <p className="small muted">SHA-256 → <a className="mono compact" href={`/evidence?sha=${selectedHash}`}>{selectedHash}</a></p> : null}
                <p className="small muted">t={selected.t} · access={selected.access} · label={selected.label}</p>

                {/* Node-Level Contextual Information State */}
                <div className="panel" style={{ marginTop: 12, background: "rgba(255,255,255,0.02)", border: "1px solid var(--line)" }}>
                  <p className="eyebrow">Node Contextual Information State (t{selected.t})</p>
                  <div className="metrics" style={{ gridTemplateColumns: "repeat(3, minmax(0,1fr))", marginTop: 8 }}>
                    <div className="metric">
                      <span className="metricLabel">Node G*</span>
                      <strong>{((typeof selected.payload.g_star === "number" ? selected.payload.g_star : activeMetric?.g_star) ?? 0).toFixed(3)}</strong>
                    </div>
                    <div className="metric">
                      <span className="metricLabel">Node Shannon H</span>
                      <strong>{((typeof selected.payload.shannon_entropy_bits === "number" ? selected.payload.shannon_entropy_bits : activeMetric?.shannon_entropy) ?? 0).toFixed(3)}</strong>
                    </div>
                    <div className="metric">
                      <span className="metricLabel">FCG Degree</span>
                      <strong>{selectedLinks.length} edges</strong>
                    </div>
                  </div>
                </div>

                {/* Side-by-Side Node Comparison */}
                <div className="panel" style={{ marginTop: 12, background: "rgba(255,255,255,0.02)", border: "1px solid var(--line)" }}>
                  <p className="eyebrow">Compare Node Context (Delta vs Reference t0)</p>
                  {(() => {
                    const refMetric = data?.timeline[0];
                    const nodeG = (typeof selected.payload.g_star === "number" ? selected.payload.g_star : activeMetric?.g_star) ?? 0;
                    const refG = refMetric?.g_star ?? 0;
                    const dG = nodeG - refG;

                    const nodeH = (typeof selected.payload.shannon_entropy_bits === "number" ? selected.payload.shannon_entropy_bits : activeMetric?.shannon_entropy) ?? 0;
                    const refH = refMetric?.shannon_entropy ?? 0;
                    const dH = nodeH - refH;

                    return (
                      <div className="metrics" style={{ gridTemplateColumns: "repeat(2, minmax(0,1fr))", marginTop: 8 }}>
                        <div className="metric">
                          <span className="metricLabel">ΔG* vs t0</span>
                          <strong style={{ color: dG < 0 ? "#4caf50" : dG > 0 ? "#ff9800" : "#d8e0e8" }}>
                            {dG >= 0 ? "+" : ""}{dG.toFixed(3)}
                          </strong>
                        </div>
                        <div className="metric">
                          <span className="metricLabel">ΔH vs t0</span>
                          <strong>{dH >= 0 ? "+" : ""}{dH.toFixed(3)}</strong>
                        </div>
                      </div>
                    );
                  })()}
                </div>

                {selectedSourceNode ? (
                  <p className="small muted" style={{ marginTop: 12 }}>source_ref → <button className="secondary" onClick={() => { setSelectedId(selectedSourceNode.id); setTime(selectedSourceNode.t); }}>{selectedSourceNode.label}</button></p>
                ) : selectedSourceRef.startsWith("http") ? (
                  <p className="small muted" style={{ marginTop: 12 }}>source_ref → <a href={selectedSourceRef} target="_blank" rel="noreferrer">upstream source ↗</a></p>
                ) : selectedSourceRef ? <p className="mono small compact" style={{ marginTop: 12 }}>source_ref={selectedSourceRef}</p> : null}

                {selected.access === "toy-locked" ? (
                  <button className="secondary" onClick={toggleToyLock}>
                    {unlocked.has(selected.id) ? "Lock toy key" : "Unlock with toy key"}
                  </button>
                ) : null}
                <button className="secondary" onClick={speakSelected} style={{ marginLeft: 8 }}>Speak node</button>
                <pre className="result">
                  {payloadVisible ? JSON.stringify(selected.payload, null, 2) : "TOY_LOCKED — payload hidden in UI only. This is not production cryptography."}
                </pre>
                {selectedLinks.length ? (
                  <div>
                    <p className="eyebrow">Connected FCG edges</p>
                    <ul>
                      {selectedLinks.map((link, index) => {
                        const outgoing = link.source === selected.id;
                        const otherId = outgoing ? link.target : link.source;
                        const other = data?.scene.nodes.find((node) => node.id === otherId);
                        return (
                          <li key={`${link.source}-${link.relation}-${link.target}-${index}`}>
                            <span className="mono small">{outgoing ? "→" : "←"} {link.relation} </span>
                            <button className="secondary" onClick={() => { setSelectedId(otherId); if (other) setTime(other.t); }}>{other?.label || otherId.slice(0, 20)}</button>
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                ) : null}
              </>
            ) : <div className="result empty">Click a node to inspect its FCO payload & contextual information state.</div>}
          </div>
        </article>
      </section>

      <section className="panel architecture">
        <p className="eyebrow">Claim boundary</p>
        <h2>Visualization is evidence-linked, not evidence-generating</h2>
        <p className="muted">
          The heat layer is recomputed from declared state distributions stored on StateSnapshot FCOs. It shows
          graph mutation/restoration under the fixture contract; it does not independently establish truth,
          safety, biological rescue, or physical thermodynamics.
        </p>
      </section>
    </main>
  );
}
