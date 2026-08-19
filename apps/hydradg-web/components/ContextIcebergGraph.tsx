"use client";

import Link from "next/link";
import {
  type PointerEvent,
  type WheelEvent,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import {
  PENDING_CONTEXT_ICEBERG,
  contextCloudVisual,
  deltaGDirection,
  type ContextIcebergObservation,
  type ContextIcebergScopeMetric,
} from "@/lib/contextIceberg";
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
  shannon_entropy: number;
  normalized_entropy: number;
  g_star: number;
  delta_g_star: number;
  mutation_distance: number;
  restoration_gain: number;
  burden: number;
};

type Fixture = {
  state_field_contract: string;
  scene: { nodes: SceneNode[]; links: SceneLink[] };
  timeline: Timeline[];
};

type FixtureResponse = { fixture?: Fixture; error?: string };
type Projected = { id: string; px: number; py: number; depth: number };

type NodeVisualMetric = {
  delta_g_star: number | null;
  cloud_drift_0_100: number | null;
  burden_0_1: number | null;
  metric_source: "OBJECT_SPECIFIC" | "STATE_INHERITED" | "DEMO_CONTROL" | "PENDING";
  demo_cloud_magnitude_0_100: number | null;
};

function signed(value: number | null, digits = 3) {
  if (value == null || !Number.isFinite(value)) return "PENDING";
  return `${value > 0 ? "+" : ""}${value.toFixed(digits)}`;
}

function percentDelta(value: number | null) {
  if (value == null || !Number.isFinite(value)) return "—";
  const points = value * 100;
  return `${points > 0 ? "+" : ""}${points.toFixed(1)}%`;
}

function fcoHash(id: string) {
  return id.startsWith("fco:") && /^[0-9a-f]{64}$/i.test(id.slice(4)) ? id.slice(4) : "";
}

function clamp01(value: number | null | undefined) {
  if (value == null || !Number.isFinite(value)) return 0;
  return Math.max(0, Math.min(1, value));
}

function baseRadius(label: string) {
  if (label === "StateSnapshot") return 9;
  if (label === "KnowledgeAtom") return 7.5;
  if (label === "Evidence") return 7;
  if (label === "Source") return 6.5;
  return 6;
}

export default function ContextIcebergGraph() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const projectedRef = useRef<Projected[]>([]);
  const dragRef = useRef({ active: false, moved: false, x: 0, y: 0 });

  const [fixture, setFixture] = useState<Fixture | null>(null);
  const [iceberg, setIceberg] = useState<ContextIcebergObservation>(PENDING_CONTEXT_ICEBERG);
  const [error, setError] = useState("");
  const [time, setTime] = useState(0);
  const [yaw, setYaw] = useState(0.45);
  const [pitch, setPitch] = useState(-0.25);
  const [zoom, setZoom] = useState(260);
  const [selectedId, setSelectedId] = useState("");
  const [query, setQuery] = useState("");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setQuery(params.get("q") || "");
    setSelectedId(params.get("node") || "");

    Promise.all([
      fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "fixture" }),
      }).then((response) => response.json() as Promise<FixtureResponse>),
      fetch("/api/math/current", { cache: "no-store" })
        .then((response) => response.json() as Promise<ContextIcebergObservation>)
        .catch(() => PENDING_CONTEXT_ICEBERG),
    ])
      .then(([fixtureResponse, icebergResponse]) => {
        if (fixtureResponse.error || !fixtureResponse.fixture) {
          throw new Error(fixtureResponse.error || "Fixture unavailable");
        }
        setFixture(fixtureResponse.fixture);
        setIceberg(icebergResponse?.schema === "hydradg.context_iceberg_projection.v1"
          ? icebergResponse
          : PENDING_CONTEXT_ICEBERG);
        setTime(Math.max(0, ...fixtureResponse.fixture.timeline.map((item) => item.t)));
      })
      .catch((caught) => setError(caught instanceof Error ? caught.message : String(caught)));
  }, []);

  const currentTimeline = fixture?.timeline.find((item) => item.t === time) || null;
  const selected = fixture?.scene.nodes.find((node) => node.id === selectedId) || null;
  const selectedHash = selected ? fcoHash(selected.id) : "";
  const selectedKnowledge = selected ? knowledgeTerm(selected.label) : undefined;
  const selectedLinks = useMemo(
    () => fixture?.scene.links.filter((link) => link.source === selectedId || link.target === selectedId) || [],
    [fixture, selectedId],
  );

  const matching = useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (!fixture) return new Set<string>();
    if (!needle) return new Set(fixture.scene.nodes.map((node) => node.id));
    return new Set(
      fixture.scene.nodes
        .filter((node) => JSON.stringify(node).toLowerCase().includes(needle))
        .map((node) => node.id),
    );
  }, [fixture, query]);

  const scopeById = useMemo(() => {
    const map = new Map<string, ContextIcebergScopeMetric>();
    for (const metric of iceberg.scopes || []) map.set(metric.scope_id, metric);
    return map;
  }, [iceberg.scopes]);

  function metricForNode(node: SceneNode): NodeVisualMetric {
    const direct = scopeById.get(node.id);
    if (direct) {
      return {
        delta_g_star: direct.delta_g_star,
        cloud_drift_0_100: direct.cloud_drift_0_100,
        burden_0_1: direct.burden_0_1 ?? null,
        metric_source: direct.metric_source,
        demo_cloud_magnitude_0_100: null,
      };
    }

    const stateMetric = (iceberg.scopes || []).find(
      (item) => item.metric_source === "STATE_INHERITED" && item.t === node.t,
    );
    if (stateMetric) {
      return {
        delta_g_star: stateMetric.delta_g_star,
        cloud_drift_0_100: stateMetric.cloud_drift_0_100,
        burden_0_1: stateMetric.burden_0_1 ?? null,
        metric_source: "STATE_INHERITED",
        demo_cloud_magnitude_0_100: null,
      };
    }

    const demo = fixture?.timeline.find((item) => item.t === node.t) || null;
    if (demo) {
      return {
        delta_g_star: demo.delta_g_star,
        cloud_drift_0_100: null,
        burden_0_1: clamp01(demo.burden),
        metric_source: "DEMO_CONTROL",
        demo_cloud_magnitude_0_100: Math.max(0, Math.min(100, demo.mutation_distance * 100)),
      };
    }

    return {
      delta_g_star: null,
      cloud_drift_0_100: null,
      burden_0_1: null,
      metric_source: "PENDING",
      demo_cloud_magnitude_0_100: null,
    };
  }

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !fixture) return;
    const context = canvas.getContext("2d");
    if (!context) return;

    const ratio = Math.max(1, window.devicePixelRatio || 1);
    const width = canvas.clientWidth || 900;
    const height = canvas.clientHeight || 560;
    canvas.width = Math.floor(width * ratio);
    canvas.height = Math.floor(height * ratio);
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.clearRect(0, 0, width, height);

    const visible = fixture.scene.nodes.filter((node) => node.t <= time);
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

    for (const link of fixture.scene.links) {
      if (!visibleIds.has(link.source) || !visibleIds.has(link.target)) continue;
      const a = projected.get(link.source);
      const b = projected.get(link.target);
      if (!a || !b) continue;
      const selectedEdge = link.source === selectedId || link.target === selectedId;
      context.globalAlpha = selectedEdge ? 0.72 : 0.25;
      context.strokeStyle = selectedEdge ? "#e7e3d9" : "#69727e";
      context.lineWidth = selectedEdge ? 1.8 : 1;
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
      const metric = metricForNode(node);
      const realCloudDrift = metric.cloud_drift_0_100;
      const cloudMagnitude = realCloudDrift ?? metric.demo_cloud_magnitude_0_100 ?? 0;
      const visual = contextCloudVisual({
        delta_g_star: metric.delta_g_star,
        cloud_drift_0_100: cloudMagnitude,
        burden_0_1: metric.burden_0_1,
      });
      const radius = baseRadius(node.label) * visual.radius_scale + (selectedId === node.id ? 2 : 0);
      const haloRadius = radius + visual.halo_px;
      const isMatch = matching.has(node.id);

      context.save();
      context.globalAlpha = isMatch ? visual.halo_alpha : visual.halo_alpha * 0.25;
      context.strokeStyle = visual.fill;
      context.lineWidth = visual.halo_line_width;
      if (realCloudDrift == null) context.setLineDash([3, 4]);
      context.beginPath();
      context.arc(point.px, point.py, haloRadius, 0, Math.PI * 2);
      context.stroke();
      context.restore();

      context.globalAlpha = isMatch ? 0.94 : 0.12;
      context.fillStyle = visual.fill;
      context.beginPath();
      context.arc(point.px, point.py, radius, 0, Math.PI * 2);
      context.fill();

      if (selectedId === node.id) {
        context.globalAlpha = 1;
        context.strokeStyle = "#ffffff";
        context.lineWidth = 2;
        context.beginPath();
        context.arc(point.px, point.py, radius + 2, 0, Math.PI * 2);
        context.stroke();
      }

      if (isMatch && (selectedId === node.id || node.label === "StateSnapshot")) {
        context.globalAlpha = 0.9;
        context.fillStyle = "#d8e0e8";
        context.font = "11px ui-monospace, SFMono-Regular, Menlo, monospace";
        context.fillText(`${node.label} · t${node.t}`, point.px + radius + 7, point.py - 6);
      }
      clickTargets.push(point);
    }

    context.globalAlpha = 1;
    projectedRef.current = clickTargets;
  }, [fixture, iceberg.scopes, matching, pitch, selectedId, time, yaw, zoom]);

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
      .filter(({ distance }) => distance <= 22)
      .sort((a, b) => a.distance - b.distance)[0];
    if (hit) setSelectedId(hit.point.id);
  }

  function onWheel(event: WheelEvent<HTMLCanvasElement>) {
    event.preventDefault();
    setZoom((value) => Math.max(120, Math.min(650, value - event.deltaY * 0.35)));
  }

  const liveScores = iceberg.state === "READY";
  const currentDeltaG = liveScores ? iceberg.scores.delta_g_star : null;
  const currentCloudDrift = liveScores ? iceberg.scores.cloud_drift_0_100 : null;
  const selectedMetric = selected ? metricForNode(selected) : null;

  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">Context Iceberg · 4D Fractal Custody Graph</p>
          <h1>See the delta around every object.</h1>
          <p className="lede">
            Rotate x/y/z, move through time, and inspect the custody object underneath each context cloud.
            Cloud width encodes frozen CloudDrift when a canonical receipt exists; color encodes signed ΔG* direction;
            node size encodes declared normalized burden. The score never substitutes for accuracy or custody.
          </p>
          <div className="actions">
            <Link className="primary" href="/judge">Run the judge path</Link>
            <Link className="secondary" href="/knowledge#context-iceberg">What is the Context Iceberg?</Link>
          </div>
        </div>
        <div className="heroStatus">
          <span className={`pill ${liveScores ? "pillGood" : "pillMuted"}`}>score receipt · {iceberg.state}</span>
          <span className="pill pillMuted">read-only release lane</span>
        </div>
      </header>

      {error ? <section className="panel"><strong>Graph unavailable:</strong> {error}</section> : null}

      <section className="metrics" aria-label="Context Iceberg headline scores">
        <article className="metric">
          <span className="metricLabel">ΔG*</span>
          <strong>{signed(currentDeltaG)}</strong>
          <span className="small muted">{deltaGDirection(currentDeltaG)} · direction only</span>
        </article>
        <article className="metric">
          <span className="metricLabel">Cloud Drift</span>
          <strong>{currentCloudDrift == null ? "PENDING" : `${currentCloudDrift.toFixed(1)} / 100`}</strong>
          <span className="small muted">100 × Jensen-Shannon divergence</span>
        </article>
        <article className="metric">
          <span className="metricLabel">Δ recall@k</span>
          <strong>{percentDelta(iceberg.outcomes.delta_recall_at_k)}</strong>
          <span className="small muted">empirical outcome · separate from ΔG*</span>
        </article>
        <article className="metric">
          <span className="metricLabel">Custody</span>
          <strong className="small">{iceberg.governance.signature_state}</strong>
          <span className="small muted">Merkle: {iceberg.governance.merkle_state}</span>
        </article>
      </section>

      {!liveScores ? (
        <section className="panel">
          <p className="eyebrow">Display contract active · scientific score pending</p>
          <p className="muted">
            No frozen ContextDrift observation is configured. Dashed halos demonstrate the deterministic UI grammar using
            the existing demo-control mutation-distance timeline. They are <strong>not</strong> CloudDrift/JSD measurements.
            Release Watch does not choose G* weights or invent a reference distribution.
          </p>
        </section>
      ) : null}

      <section className="grid twoCol">
        <article className="panel">
          <div className="panelHead">
            <div>
              <p className="eyebrow">Navigable state field</p>
              <h2>x · y · z · time + context cloud</h2>
            </div>
            <span className="pill pillMuted">{fixture?.state_field_contract || "loading"}</span>
          </div>
          <label>
            Search visible FCOs / atoms / objects
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="source, evidence, atom, state…" />
          </label>
          <div className="flow mono" style={{ margin: "14px 0" }}>
            <span>blue = ΔG* LOWER</span>
            <span>gray = STABLE / PENDING</span>
            <span>amber = ΔG* HIGHER</span>
            <span>solid cloud = JSD receipt</span>
            <span>dashed cloud = demo fallback</span>
          </div>
          <canvas
            ref={canvasRef}
            aria-label="Interactive four-dimensional Fractal Custody Graph with context-cloud halos"
            style={{ width: "100%", height: 590, border: "1px solid var(--line)", borderRadius: 4, touchAction: "none", background: "#080b0f" }}
            onPointerDown={onPointerDown}
            onPointerMove={onPointerMove}
            onPointerUp={onPointerUp}
            onPointerCancel={() => { dragRef.current.active = false; }}
            onWheel={onWheel}
          />
          <label style={{ marginTop: 14 }}>
            Time / graph state: t{time} — {currentTimeline?.label || "loading"}
            <input
              type="range"
              min={Math.min(0, ...(fixture?.timeline.map((item) => item.t) || [0]))}
              max={Math.max(0, ...(fixture?.timeline.map((item) => item.t) || [0]))}
              step={1}
              value={time}
              onChange={(event) => setTime(Number(event.target.value))}
            />
          </label>
        </article>

        <article className="panel">
          <p className="eyebrow">Selected custody object</p>
          <h2>{selected?.label || "Select a node"}</h2>
          {selected ? (
            <>
              <p className="mono small compact">{selected.id}</p>
              <div className="metrics" style={{ gridTemplateColumns: "repeat(2,minmax(0,1fr))" }}>
                <div className="metric"><span className="metricLabel">t</span><strong>{selected.t}</strong></div>
                <div className="metric"><span className="metricLabel">Metric source</span><strong className="small">{selectedMetric?.metric_source}</strong></div>
                <div className="metric"><span className="metricLabel">ΔG*</span><strong>{signed(selectedMetric?.delta_g_star ?? null)}</strong></div>
                <div className="metric"><span className="metricLabel">Cloud Drift</span><strong>{selectedMetric?.cloud_drift_0_100 == null ? "PENDING" : selectedMetric.cloud_drift_0_100.toFixed(1)}</strong></div>
              </div>
              {selectedMetric?.cloud_drift_0_100 == null && selectedMetric?.demo_cloud_magnitude_0_100 != null ? (
                <p className="small muted">Demo halo magnitude: {selectedMetric.demo_cloud_magnitude_0_100.toFixed(1)} · mutation-distance control, not JSD.</p>
              ) : null}
              <p className="small muted">Connected edges: {selectedLinks.length}</p>
              <div className="actions">
                {selectedHash ? <Link className="secondary" href={`/fco/${encodeURIComponent(selected.id)}`}>Open FCO custody object</Link> : null}
                {selectedKnowledge ? <Link className="secondary" href={`/knowledge#${selectedKnowledge.slug}`}>Open knowledge definition</Link> : null}
              </div>
              <pre className="result">{JSON.stringify(selected.payload, null, 2)}</pre>
            </>
          ) : (
            <p className="muted">Click a node. Every selected object remains navigable back toward its FCO/FCG/source context when that link exists.</p>
          )}
        </article>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">01 / WATERLINE</span>
        <h2 className="displayTitle">Direction, magnitude, outcome, custody.</h2>
        <div className="grid twoCol">
          <article className="panel">
            <p className="eyebrow">Context distribution</p>
            <p>JSD: <span className="mono">{iceberg.scores.js_divergence == null ? "PENDING" : iceberg.scores.js_divergence.toFixed(4)}</span></p>
            <p>Reference FCG: <span className="mono compact">{iceberg.reference_state_root || "PENDING"}</span></p>
            <p>Current FCG: <span className="mono compact">{iceberg.current_state_root || "PENDING"}</span></p>
          </article>
          <article className="panel">
            <p className="eyebrow">Empirical outcome</p>
            <p>Δ hit@k: <span className="mono">{percentDelta(iceberg.outcomes.delta_hit_at_k)}</span></p>
            <p>Δ recall@k: <span className="mono">{percentDelta(iceberg.outcomes.delta_recall_at_k)}</span></p>
            <p>Mean answer-rank displacement: <span className="mono">{iceberg.outcomes.mean_answer_rank_displacement ?? "—"}</span></p>
          </article>
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">02 / BELOW WATER</span>
        <h2 className="displayTitle">The score opens into the custody graph.</h2>
        <div className="grid twoCol">
          <article className="panel">
            <p className="eyebrow">Governance decomposition</p>
            <ul>
              <li>Provenance completeness: {iceberg.governance.provenance_completeness ?? "PENDING"}</li>
              <li>Orphan FCOs: {iceberg.governance.orphan_fco_count ?? "PENDING"}</li>
              <li>Broken FCG edges: {iceberg.governance.broken_fcg_edge_count ?? "PENDING"}</li>
              <li>Hash mismatches: {iceberg.governance.artifact_hash_mismatch_count ?? "PENDING"}</li>
              <li>Semantic abstention: {iceberg.governance.semantic_abstention_rate ?? "PENDING"}</li>
              <li>Unresolved contradiction: {iceberg.governance.unresolved_contradiction_rate ?? "PENDING"}</li>
            </ul>
          </article>
          <article className="panel">
            <p className="eyebrow">Nulls remain first class</p>
            <ul>{iceberg.null_hypotheses.map((item) => <li key={item}>{item}</li>)}</ul>
            <p className="small muted">Claim ceiling: {iceberg.claim_ceiling}</p>
          </article>
        </div>
      </section>
    </main>
  );
}
