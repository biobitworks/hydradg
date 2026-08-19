"use client";

import { PointerEvent, WheelEvent, useEffect, useMemo, useRef, useState } from "react";

type SceneNode = {
  id: string;
  label: string;
  x: number;
  y: number;
  z: number;
  t: number;
  payload: Record<string, unknown>;
};

type SceneLink = { source: string; target: string; relation: string };

type Fixture = { scene: { nodes: SceneNode[]; links: SceneLink[] } };
type Custody = {
  golden_path: string[];
  golden_path_semantics: string[];
  checkpoint_fco: { id: string; object_sha256: string; type: string; payload: Record<string, unknown> };
  merkle: { root_sha256: string; leaf_count: number; ordering: string; odd_leaf_rule: string };
};

type Props = { fixture: Fixture; custody: Custody };
type Projected = { id: string; px: number; py: number; depth: number };

export default function GoldenGraph({ fixture, custody }: Props) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const projectedRef = useRef<Projected[]>([]);
  const dragRef = useRef({ active: false, moved: false, x: 0, y: 0 });
  const [yaw, setYaw] = useState(0.55);
  const [pitch, setPitch] = useState(-0.22);
  const [zoom, setZoom] = useState(260);
  const [time, setTime] = useState(2);
  const [selectedId, setSelectedId] = useState(custody.golden_path[2] || "");
  const golden = useMemo(() => new Set(custody.golden_path), [custody.golden_path]);

  const nodes = useMemo<SceneNode[]>(() => {
    const checkpoint: SceneNode = {
      id: custody.checkpoint_fco.id,
      label: "MerkleCheckpoint",
      x: 1.55,
      y: -0.85,
      z: 0.7,
      t: 2,
      payload: {
        ...custody.checkpoint_fco.payload,
        object_sha256: custody.checkpoint_fco.object_sha256,
      },
    };
    return [...fixture.scene.nodes, checkpoint];
  }, [fixture.scene.nodes, custody.checkpoint_fco]);

  const selected = useMemo(() => nodes.find((node) => node.id === selectedId) || null, [nodes, selectedId]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const context = canvas.getContext("2d");
    if (!context) return;

    const rootStyle = getComputedStyle(document.documentElement);
    const accent = rootStyle.getPropertyValue("--accent").trim() || "#8dd3c7";
    const text = rootStyle.getPropertyValue("--text").trim() || "#f4f5f7";
    const muted = rootStyle.getPropertyValue("--muted").trim() || "#9aa4b2";
    const line = rootStyle.getPropertyValue("--line").trim() || "#29313a";

    const ratio = Math.max(1, window.devicePixelRatio || 1);
    const width = canvas.clientWidth || 760;
    const height = canvas.clientHeight || 520;
    canvas.width = Math.floor(width * ratio);
    canvas.height = Math.floor(height * ratio);
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.clearRect(0, 0, width, height);

    const visible = nodes.filter((node) => node.t <= time);
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
      });
    }

    context.lineWidth = 1;
    for (const link of fixture.scene.links) {
      if (!visibleIds.has(link.source) || !visibleIds.has(link.target)) continue;
      const a = projected.get(link.source);
      const b = projected.get(link.target);
      if (!a || !b) continue;
      context.globalAlpha = golden.has(link.source) && golden.has(link.target) ? 0.65 : 0.22;
      context.strokeStyle = golden.has(link.source) && golden.has(link.target) ? accent : line;
      context.beginPath();
      context.moveTo(a.px, a.py);
      context.lineTo(b.px, b.py);
      context.stroke();
    }

    context.lineWidth = 3;
    context.globalAlpha = 0.88;
    context.strokeStyle = accent;
    const visibleGolden = custody.golden_path.filter((id) => visibleIds.has(id));
    for (let index = 0; index < visibleGolden.length - 1; index += 1) {
      const a = projected.get(visibleGolden[index]);
      const b = projected.get(visibleGolden[index + 1]);
      if (!a || !b) continue;
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
      const isGolden = golden.has(node.id);
      const isSelected = node.id === selectedId;
      const radius = isSelected ? 10 : isGolden ? 8 : 5;
      context.globalAlpha = isGolden ? 0.98 : 0.36;
      context.fillStyle = isGolden ? accent : muted;
      context.beginPath();
      context.arc(point.px, point.py, radius, 0, Math.PI * 2);
      context.fill();
      if (isSelected) {
        context.globalAlpha = 1;
        context.strokeStyle = text;
        context.lineWidth = 2;
        context.stroke();
      }
      if (isGolden) {
        context.globalAlpha = 0.9;
        context.fillStyle = text;
        context.font = "11px ui-monospace, SFMono-Regular, Menlo, monospace";
        context.fillText(node.label, point.px + 11, point.py - 7);
      }
      clickTargets.push(point);
    }
    context.globalAlpha = 1;
    projectedRef.current = clickTargets;
  }, [nodes, fixture.scene.links, custody.golden_path, golden, yaw, pitch, zoom, time, selectedId]);

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
    if (hit) setSelectedId(hit.point.id);
  }

  function onWheel(event: WheelEvent<HTMLCanvasElement>) {
    event.preventDefault();
    setZoom((value) => Math.max(120, Math.min(620, value - event.deltaY * 0.35)));
  }

  return (
    <div className="grid twoCol">
      <div>
        <canvas
          ref={canvasRef}
          aria-label="Interactive 3D FCO and FCG golden-path projection"
          style={{ width: "100%", height: 520, border: "1px solid var(--line)", borderRadius: 12, background: "#090c10", touchAction: "none" }}
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={onPointerUp}
          onPointerCancel={() => { dragRef.current.active = false; }}
          onWheel={onWheel}
        />
        <label style={{ marginTop: 12 }}>
          Time / graph state: t{time}
          <input type="range" min={0} max={2} step={1} value={time} onChange={(event) => setTime(Number(event.target.value))} />
        </label>
        <p className="small muted">
          Drag to rotate · scroll/pinch to zoom · click a node to inspect it. Thin lines are stored FCG relations;
          the thick line is the curated golden dependency route and may bridge relation direction for explanation.
        </p>
      </div>

      <div className="stack">
        <div className="metric">
          <span className="metricLabel">Fixture Merkle root</span>
          <strong className="mono compact">{custody.merkle.root_sha256}</strong>
          <span className="small muted">{custody.merkle.leaf_count} FCO leaves · {custody.merkle.ordering} · {custody.merkle.odd_leaf_rule}</span>
        </div>
        <div className="panel">
          <p className="eyebrow">Selected custody object</p>
          <h3>{selected?.label || "Select a node"}</h3>
          <p className="mono small compact">{selected?.id || "—"}</p>
          <pre className="result">{selected ? JSON.stringify(selected.payload, null, 2) : "No node selected."}</pre>
        </div>
        <div className="panel">
          <p className="eyebrow">Golden pathway</p>
          <ol>
            {custody.golden_path_semantics.map((label, index) => (
              <li key={`${label}-${index}`}>
                <button className="secondary" type="button" onClick={() => setSelectedId(custody.golden_path[index])}>
                  {index + 1}. {label}
                </button>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </div>
  );
}
