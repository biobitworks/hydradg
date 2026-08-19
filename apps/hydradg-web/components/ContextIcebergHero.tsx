"use client";

import Link from "next/link";
import {
  PointerEvent as ReactPointerEvent,
  WheelEvent as ReactWheelEvent,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import { deltaDirection, deltaHue } from "@/lib/contextIceberg";

type SceneNode = {
  id: string;
  label: string;
  x: number;
  y: number;
  z: number;
  t: number;
  payload?: Record<string, unknown>;
  context_drift?: {
    cloud_drift_0_100?: number;
    delta_g_star?: number;
    scope?: string;
  };
};

type TimelineState = {
  t: number;
  label: string;
  distribution: number[];
  g_star: number;
  delta_g_star: number;
  js_divergence: number;
  cloud_drift_0_100: number;
  shannon_entropy?: number;
  normalized_entropy?: number;
  mutation_distance?: number;
  restoration_gain?: number;
  burden?: number;
  delta_hit_at_k?: number | null;
  delta_recall_at_k?: number | null;
};

type IcebergPayload = {
  schema?: string;
  source_state?: string;
  claim_ceiling?: string;
  project_fcg_root?: string | null;
  hydradb_projection_root?: string | null;
  signature_state?: string;
  merkle_state?: string;
  refreshed_at?: string;
  timeline: TimelineState[];
  scene: {
    nodes: SceneNode[];
    links: Array<{ source: string; target: string; relation: string }>;
  };
  error?: string;
};

type Projected = { id: string; px: number; py: number; depth: number; hitRadius: number };

function signed(value: number | null | undefined, digits = 3) {
  if (value === null || value === undefined || !Number.isFinite(value)) return "PENDING";
  if (Math.abs(value) < 10 ** -(digits + 1)) return (0).toFixed(digits);
  return `${value > 0 ? "+" : ""}${value.toFixed(digits)}`;
}

function percentDelta(value: number | null | undefined) {
  if (value === null || value === undefined || !Number.isFinite(value)) return "PENDING";
  return `${value > 0 ? "+" : ""}${(value * 100).toFixed(1)}%`;
}

function compactRoot(value: string | null | undefined) {
  if (!value) return "PENDING";
  return value.length > 20 ? `${value.slice(0, 10)}…${value.slice(-8)}` : value;
}

export default function ContextIcebergHero() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const projectedRef = useRef<Projected[]>([]);
  const dragRef = useRef({ active: false, moved: false, x: 0, y: 0 });
  const latestTimeRef = useRef<number | null>(null);
  const [data, setData] = useState<IcebergPayload | null>(null);
  const [error, setError] = useState("");
  const [time, setTime] = useState(0);
  const [followLatest, setFollowLatest] = useState(true);
  const [playing, setPlaying] = useState(false);
  const [yaw, setYaw] = useState(0.55);
  const [pitch, setPitch] = useState(-0.3);
  const [zoom, setZoom] = useState(245);
  const [selectedId, setSelectedId] = useState("");

  useEffect(() => {
    let active = true;
    async function refresh() {
      try {
        const response = await fetch("/api/iceberg", { cache: "no-store" });
        const payload = (await response.json()) as IcebergPayload;
        if (!response.ok || payload.error) throw new Error(payload.error || `iceberg state failed (${response.status})`);
        if (!active) return;
        setData(payload);
        setError("");
        const newest = Math.max(...payload.timeline.map((state) => state.t));
        latestTimeRef.current = newest;
        if (followLatest) setTime(newest);
      } catch (caught) {
        if (!active) return;
        setError(caught instanceof Error ? caught.message : String(caught));
      }
    }
    refresh();
    const timer = window.setInterval(refresh, 3500);
    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, [followLatest]);

  const maxTime = useMemo(() => (data?.timeline.length ? Math.max(...data.timeline.map((state) => state.t)) : 0), [data]);
  const current = useMemo(() => data?.timeline.find((state) => state.t === time) || null, [data, time]);
  const selected = useMemo(() => data?.scene.nodes.find((node) => node.id === selectedId) || null, [data, selectedId]);

  useEffect(() => {
    if (!playing || maxTime <= 0) return;
    const timer = window.setInterval(() => {
      setFollowLatest(false);
      setTime((value) => (value >= maxTime ? 0 : value + 1));
    }, 1250);
    return () => window.clearInterval(timer);
  }, [playing, maxTime]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !data || !current) return;
    const context = canvas.getContext("2d");
    if (!context) return;

    const ratio = Math.max(1, window.devicePixelRatio || 1);
    const width = canvas.clientWidth || 720;
    const height = canvas.clientHeight || 500;
    canvas.width = Math.floor(width * ratio);
    canvas.height = Math.floor(height * ratio);
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.clearRect(0, 0, width, height);

    const hue = deltaHue(current.delta_g_star);
    const ambientRadius = Math.max(width, height) * (0.32 + current.cloud_drift_0_100 / 250);
    const ambient = context.createRadialGradient(width / 2, height / 2, 20, width / 2, height / 2, ambientRadius);
    ambient.addColorStop(0, `hsla(${hue}, 68%, 56%, ${0.035 + current.cloud_drift_0_100 / 1800})`);
    ambient.addColorStop(0.55, `hsla(${hue}, 68%, 44%, ${0.018 + current.cloud_drift_0_100 / 3000})`);
    ambient.addColorStop(1, `hsla(${hue}, 68%, 30%, 0)`);
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
      const perspective = zoom / Math.max(1.25, 3.2 - z2);
      projected.set(node.id, {
        id: node.id,
        px: width / 2 + x1 * perspective,
        py: height / 2 + y2 * perspective,
        depth: z2,
        hitRadius: 18,
      });
    }

    for (const link of data.scene.links) {
      if (!visibleIds.has(link.source) || !visibleIds.has(link.target)) continue;
      const a = projected.get(link.source);
      const b = projected.get(link.target);
      if (!a || !b) continue;
      context.globalAlpha = 0.26;
      context.strokeStyle = "#87909b";
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
      const nodeMetric = node.context_drift;
      const cloud = Math.max(0, Math.min(100, nodeMetric?.cloud_drift_0_100 ?? current.cloud_drift_0_100));
      const nodeDelta = nodeMetric?.delta_g_star ?? current.delta_g_star;
      const nodeHue = deltaHue(nodeDelta);
      const haloRadius = 11 + cloud * 0.26;
      const selectedNode = node.id === selectedId;
      const baseRadius = selectedNode ? 8 : node.label === "StateSnapshot" ? 7 : 4.5;

      for (let ring = 2; ring >= 0; ring -= 1) {
        const ringRadius = haloRadius * (0.45 + ring * 0.28);
        context.globalAlpha = (0.035 + cloud / 1300) * (1 - ring * 0.17);
        context.fillStyle = `hsl(${nodeHue} 72% ${50 + ring * 4}%)`;
        context.beginPath();
        context.arc(point.px, point.py, ringRadius, 0, Math.PI * 2);
        context.fill();
      }

      context.globalAlpha = 0.92;
      context.fillStyle = node.label === "StateSnapshot" ? `hsl(${nodeHue} 72% 68%)` : "#e4e8ec";
      context.beginPath();
      context.arc(point.px, point.py, baseRadius, 0, Math.PI * 2);
      context.fill();

      if (selectedNode) {
        context.strokeStyle = "#ffffff";
        context.globalAlpha = 0.92;
        context.lineWidth = 1.5;
        context.beginPath();
        context.arc(point.px, point.py, haloRadius + 4, 0, Math.PI * 2);
        context.stroke();
        context.fillStyle = "#eef2f5";
        context.font = "11px ui-monospace, SFMono-Regular, Menlo, monospace";
        context.fillText(`${node.label} · drift ${cloud.toFixed(1)}`, point.px + 12, point.py - 10);
      }

      hits.push({ ...point, hitRadius: Math.max(18, baseRadius + 8) });
    }

    context.globalAlpha = 1;
    projectedRef.current = hits;
  }, [data, current, time, yaw, pitch, zoom, selectedId]);

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
    setPitch((value) => Math.max(-1.25, Math.min(1.25, value + dy * 0.008)));
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
      .filter(({ point, distance }) => distance <= point.hitRadius)
      .sort((a, b) => a.distance - b.distance)[0];
    if (hit) setSelectedId(hit.point.id);
  }

  function onWheel(event: ReactWheelEvent<HTMLCanvasElement>) {
    event.preventDefault();
    setZoom((value) => Math.max(120, Math.min(620, value - event.deltaY * 0.3)));
  }

  function jumpLive() {
    setPlaying(false);
    setFollowLatest(true);
    const newest = latestTimeRef.current ?? maxTime;
    setTime(newest);
  }

  const sourceState = data?.source_state || "LOADING";
  const isSynthetic = sourceState.includes("SYNTHETIC");
  const direction = current ? deltaDirection(current.delta_g_star) : "STABLE";
  const selectedCloud = selected?.context_drift?.cloud_drift_0_100;
  const selectedDelta = selected?.context_drift?.delta_g_star;
  const selectedClaim = typeof selected?.payload?.claim_ceiling === "string" ? selected.payload.claim_ceiling : data?.claim_ceiling;

  return (
    <div
      style={{
        flex: "1 1 560px",
        width: "100%",
        minWidth: 0,
        border: "1px solid rgba(255,255,255,.12)",
        background: "rgba(8,10,13,.92)",
        padding: 12,
        boxShadow: "0 28px 80px rgba(0,0,0,.34)",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "flex-start", flexWrap: "wrap" }}>
        <div>
          <p className="eyebrow">4D FCG · context iceberg</p>
          <p className="small muted" style={{ margin: "7px 0 0" }}>
            x · y · z · time · halo width = Cloud Drift · hue = signed ΔG*
          </p>
        </div>
        <span className={isSynthetic ? "pill pillWarn" : "pill pillGood"}>{sourceState.replaceAll("_", " ")}</span>
      </div>

      <div className="metrics" style={{ gridTemplateColumns: "repeat(4, minmax(0,1fr))", margin: "12px 0 8px" }}>
        <div className="metric" style={{ minHeight: 82, padding: 12 }}><span className="metricLabel">ΔG*</span><strong style={{ fontSize: 22 }}>{current ? signed(current.delta_g_star) : "—"}</strong><span className="small muted">{direction}</span></div>
        <div className="metric" style={{ minHeight: 82, padding: 12 }}><span className="metricLabel">Cloud Drift</span><strong style={{ fontSize: 22 }}>{current ? current.cloud_drift_0_100.toFixed(1) : "—"}</strong><span className="small muted">0–100 · JSD</span></div>
        <div className="metric" style={{ minHeight: 82, padding: 12 }}><span className="metricLabel">Accuracy Δ</span><strong style={{ fontSize: 22 }}>{percentDelta(current?.delta_hit_at_k)}</strong><span className="small muted">separate outcome</span></div>
        <div className="metric" style={{ minHeight: 82, padding: 12 }}><span className="metricLabel">Recall Δ</span><strong style={{ fontSize: 22 }}>{percentDelta(current?.delta_recall_at_k)}</strong><span className="small muted">separate outcome</span></div>
      </div>

      <canvas
        ref={canvasRef}
        aria-label="Navigable four-dimensional FCG context cloud"
        style={{ width: "100%", height: 410, border: "1px solid rgba(255,255,255,.10)", background: "#07090b", touchAction: "none" }}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerCancel={() => { dragRef.current.active = false; }}
        onWheel={onWheel}
      />

      <div style={{ display: "grid", gridTemplateColumns: "minmax(0,1fr) auto", gap: 10, alignItems: "end", marginTop: 10 }}>
        <label className="small">
          t{time} · {current?.label || "loading"}
          <input
            type="range"
            min={0}
            max={maxTime}
            step={1}
            value={Math.min(time, maxTime)}
            onChange={(event) => {
              setFollowLatest(false);
              setPlaying(false);
              setTime(Number(event.target.value));
            }}
          />
        </label>
        <div className="actions" style={{ margin: 0 }}>
          <button className="tab" onClick={() => setPlaying((value) => !value)}>{playing ? "pause" : "play"}</button>
          <button className={followLatest ? "tab active" : "tab"} onClick={jumpLive}>latest</button>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(2,minmax(0,1fr))", gap: 10, marginTop: 10 }}>
        <div className="small muted">
          <strong style={{ color: "var(--text)" }}>Custody</strong><br />
          FCG {compactRoot(data?.project_fcg_root)} · HydraDB {compactRoot(data?.hydradb_projection_root)}<br />
          {data?.signature_state || "SIGNATURE PENDING"} · {data?.merkle_state || "MERKLE PENDING"}
        </div>
        <div className="small muted">
          <strong style={{ color: "var(--text)" }}>{selected ? selected.label : "Select an FCO"}</strong><br />
          {selected ? `${compactRoot(selected.id)} · drift ${(selectedCloud ?? 0).toFixed(1)} · ΔG* ${signed(selectedDelta)}` : "Click a node to inspect its state-level drift envelope."}<br />
          {selected ? `ceiling ${selectedClaim || "PENDING"}` : "Cloud width is magnitude; hue is direction, not correctness."}
        </div>
      </div>

      {error ? <p className="small" style={{ color: "var(--bad)" }}>Live refresh blocked: {error}</p> : null}
      <div className="actions" style={{ marginBottom: 0 }}>
        <Link className="secondary" href="/graph">Open full 4D FCG</Link>
        <a className="secondary" href="/api/iceberg">Inspect read-only state JSON</a>
      </div>
      <p className="small muted note" style={{ marginBottom: 0 }}>
        {isSynthetic ? "Current hero uses the deterministic demo fixture until HYDRADG_ICEBERG_STATE_PATH points at a validated live custody artifact. " : "Live state is read from a custody artifact; this UI does not mutate the scientific lane. "}
        ΔG* is a dimensionless information-state abstraction, not physical Gibbs free energy. Cloud Drift is distributional magnitude, not an accuracy score.
      </p>
    </div>
  );
}
