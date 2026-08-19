"use client";

import { PointerEvent, WheelEvent, useEffect, useMemo, useRef, useState } from "react";

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
  const projectedRef = useRef<Projected[]>([]);
  const dragRef = useRef({ active: false, moved: false, x: 0, y: 0 });
  const [data, setData] = useState<FixtureResponse["fixture"] | null>(null);
  const [error, setError] = useState("");
  const [time, setTime] = useState(2);
  const [yaw, setYaw] = useState(0.45);
  const [pitch, setPitch] = useState(-0.25);
  const [zoom, setZoom] = useState(260);
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
    setYaw((value) => value + dx * 0.008);
    setPitch((value) => Math.max(-1.3, Math.min(1.3, value + dy * 0.008)));
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
    setZoom((value) => Math.max(120, Math.min(650, value - event.deltaY * 0.35)));
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
          </div>
          <canvas
            ref={canvasRef}
            aria-label="Interactive four-dimensional FCG projection"
            style={{ width: "100%", height: 560, border: "1px solid var(--line)", borderRadius: 12, touchAction: "none", background: "#090c10" }}
            onPointerDown={onPointerDown}
            onPointerMove={onPointerMove}
            onPointerUp={onPointerUp}
            onPointerCancel={() => { dragRef.current.active = false; }}
            onWheel={onWheel}
          />
          <label style={{ marginTop: 14 }}>
            Time / graph state: t{time} — {activeMetric?.label || "loading"}
            <input type="range" min={0} max={2} step={1} value={time} onChange={(event) => setTime(Number(event.target.value))} />
          </label>
        </article>

        <article className="panel">
          <p className="eyebrow">Information-state heat layer</p>
          <h2>Mutation → restoration</h2>
          <div className="metrics" style={{ gridTemplateColumns: "repeat(2, minmax(0,1fr))" }}>
            <div className="metric"><span className="metricLabel">Shannon H</span><strong>{activeMetric?.shannon_entropy.toFixed(3) ?? "—"}</strong></div>
            <div className="metric"><span className="metricLabel">G*</span><strong>{activeMetric?.g_star.toFixed(3) ?? "—"}</strong></div>
            <div className="metric"><span className="metricLabel">ΔG*</span><strong>{activeMetric?.delta_g_star.toFixed(3) ?? "—"}</strong></div>
            <div className="metric"><span className="metricLabel">Mutation</span><strong>{activeMetric?.mutation_distance.toFixed(3) ?? "—"}</strong></div>
            <div className="metric"><span className="metricLabel">Restoration</span><strong>{activeMetric?.restoration_gain.toFixed(3) ?? "—"}</strong></div>
            <div className="metric"><span className="metricLabel">U* burden</span><strong>{activeMetric?.burden.toFixed(3) ?? "—"}</strong></div>
          </div>
          <p className="small muted note">
            H is Shannon entropy. G* and ΔG* are dimensionless information-state abstractions inspired by
            free-energy inference; they are not physical Gibbs free energy and carry no kcal/mol or joule claim.
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
                <p className="small muted">t={selected.t} · access={selected.access}</p>
                {selectedSourceNode ? (
                  <p className="small muted">source_ref → <button className="secondary" onClick={() => setSelectedId(selectedSourceNode.id)}>{selectedSourceNode.label}</button></p>
                ) : selectedSourceRef.startsWith("http") ? (
                  <p className="small muted">source_ref → <a href={selectedSourceRef} target="_blank" rel="noreferrer">upstream source ↗</a></p>
                ) : selectedSourceRef ? <p className="mono small compact">source_ref={selectedSourceRef}</p> : null}
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
                            <button className="secondary" onClick={() => setSelectedId(otherId)}>{other?.label || otherId.slice(0, 20)}</button>
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                ) : null}
              </>
            ) : <div className="result empty">Click a node to inspect its FCO payload.</div>}
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
