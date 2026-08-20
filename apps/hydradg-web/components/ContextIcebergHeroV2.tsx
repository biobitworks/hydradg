"use client";

import { useEffect, useMemo, useRef, useState } from "react";

type TimelineState = {
  t: number;
  label: string;
  distribution: number[];
  g_star: number;
  delta_g_star: number;
  js_divergence: number;
  cloud_drift_0_100: number;
  delta_hit_at_k?: number | null;
  delta_recall_at_k?: number | null;
};

type Node = { id: string; label: string; x: number; y: number; z: number; t: number };
type Payload = {
  source_state?: string;
  project_fcg_root?: string | null;
  hydradb_projection_root?: string | null;
  signature_state?: string;
  merkle_state?: string;
  timeline: TimelineState[];
  scene: { nodes: Node[]; links: Array<{ source: string; target: string; relation: string }> };
  error?: string;
};

const STATE = [
  { label: "Reference / normal", color: "#b69cff" },
  { label: "Poison / mutation", color: "#ff8a3d" },
  { label: "Antidote / restoration", color: "#5aa9ff" },
] as const;

function outcome(value: number | null | undefined) {
  if (value === null || value === undefined || !Number.isFinite(value)) return "N/A";
  return `${value >= 0 ? "+" : ""}${(value * 100).toFixed(1)}%`;
}

function root(value: string | null | undefined) {
  if (!value) return "synthetic control / no hosted root in this fixture";
  return value.length > 22 ? `${value.slice(0, 11)}…${value.slice(-8)}` : value;
}

export default function ContextIcebergHeroV2() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [data, setData] = useState<Payload | null>(null);
  const [error, setError] = useState("");
  const [time, setTime] = useState(2);

  useEffect(() => {
    let active = true;
    fetch("/api/iceberg", { cache: "no-store" })
      .then(async (response) => {
        const payload = (await response.json()) as Payload;
        if (!response.ok || payload.error) throw new Error(payload.error || `iceberg ${response.status}`);
        return payload;
      })
      .then((payload) => {
        if (!active) return;
        setData(payload);
        setTime(Math.max(...payload.timeline.map((state) => state.t)));
        setError("");
      })
      .catch((caught) => active && setError(caught instanceof Error ? caught.message : String(caught)));
    return () => { active = false; };
  }, []);

  const current = useMemo(() => data?.timeline.find((state) => state.t === time) || null, [data, time]);
  const maxTime = data?.timeline.length ? Math.max(...data.timeline.map((state) => state.t)) : 2;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !data || !current) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const ratio = Math.max(1, window.devicePixelRatio || 1);
    const width = canvas.clientWidth || 620;
    const height = canvas.clientHeight || 340;
    canvas.width = Math.floor(width * ratio);
    canvas.height = Math.floor(height * ratio);
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    ctx.clearRect(0, 0, width, height);

    const visible = data.scene.nodes.filter((node) => node.t <= time);
    const byId = new Map(visible.map((node) => [node.id, node]));
    for (const link of data.scene.links) {
      const a = byId.get(link.source);
      const b = byId.get(link.target);
      if (!a || !b) continue;
      ctx.strokeStyle = "rgba(180,190,200,.22)";
      ctx.beginPath();
      ctx.moveTo(width / 2 + a.x * 145, height / 2 + a.y * 125);
      ctx.lineTo(width / 2 + b.x * 145, height / 2 + b.y * 125);
      ctx.stroke();
    }
    for (const node of visible) {
      const state = STATE[node.t] || STATE[0];
      const metric = data.timeline.find((candidate) => candidate.t === node.t) || current;
      const radius = node.label === "StateSnapshot" ? 8 : 5;
      const halo = radius + Math.min(28, metric.cloud_drift_0_100 * 0.35);
      const x = width / 2 + node.x * 145 + node.z * 28;
      const y = height / 2 + node.y * 125 - node.z * 18;
      ctx.globalAlpha = 0.1;
      ctx.fillStyle = state.color;
      ctx.beginPath();
      ctx.arc(x, y, halo, 0, Math.PI * 2);
      ctx.fill();
      ctx.globalAlpha = 0.92;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }, [data, current, time]);

  const visual = STATE[time] || STATE[0];

  return (
    <div className="panel" style={{ minWidth: 0 }}>
      <div className="panelHead">
        <div><p className="eyebrow">Context Iceberg · T0–T2 scientific fixture</p><h2 style={{ color: visual.color }}>{visual.label}</h2></div>
        <span className="pill pillMuted">{data?.source_state?.replaceAll("_", " ") || "LOADING"}</span>
      </div>
      {error ? <p style={{ color: "var(--bad)" }}>{error}</p> : null}
      <div className="metrics" style={{ gridTemplateColumns: "repeat(4,minmax(0,1fr))" }}>
        <div className="metric"><span className="metricLabel">G*</span><strong>{current?.g_star.toFixed(6) ?? "—"}</strong></div>
        <div className="metric"><span className="metricLabel">ΔG*</span><strong>{current ? `${current.delta_g_star >= 0 ? "+" : ""}${current.delta_g_star.toFixed(6)}` : "—"}</strong></div>
        <div className="metric"><span className="metricLabel">Cloud Drift</span><strong>{current?.cloud_drift_0_100.toFixed(4) ?? "—"}</strong></div>
        <div className="metric"><span className="metricLabel">Retrieval Δ</span><strong>{outcome(current?.delta_recall_at_k)}</strong><span className="small muted">N/A for synthetic fixture</span></div>
      </div>
      <canvas ref={canvasRef} aria-label="Context Iceberg mini-view with violet reference, orange poison and blue antidote" style={{ width: "100%", height: 340, background: "#07090b", border: "1px solid var(--line)" }} />
      <label className="small">t{time} · {visual.label}<input type="range" min={0} max={maxTime} step={1} value={time} onChange={(event) => setTime(Number(event.target.value))} /></label>
      <div className="actions">
        {STATE.map((state, index) => <button key={state.label} className={time === index ? "tab active" : "tab"} onClick={() => setTime(index)}><span aria-hidden="true" style={{ color: state.color }}>●</span> {state.label}</button>)}
      </div>
      <p className="small muted">FCG root: {root(data?.project_fcg_root)} · HydraDB root: {root(data?.hydradb_projection_root)}</p>
      <p className="small muted">{data?.signature_state || "NOT_SIGNED"} · {data?.merkle_state || "NOT_MERKLE_COMMITTED"}. T3–T5 release states are shown separately; no scalar context score is fabricated without a declared distribution.</p>
    </div>
  );
}
