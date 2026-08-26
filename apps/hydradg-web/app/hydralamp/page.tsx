"use client";

import { useEffect, useMemo, useState } from "react";

type HydraEvent = {
  event_index: number;
  event_type: string;
  actor_id: string;
  actor_class: string;
  region: string;
  runtime_model: string;
  msm_state_after: string;
  fcg_root_after: string;
  access_decision: {
    allowed: boolean;
    reason: string;
    connect?: boolean;
    decrypt_private?: boolean;
    promote?: boolean;
  };
  delta_g_star_drift_pointer?: string;
};

const STATE_COLORS: Record<string, string> = {
  UNKNOWN: "#808080",
  AUTHENTICATED: "#0064ff",
  CAPABILITY_GRANTED: "#00c8ff",
  EVIDENCE_ACCESSED: "#00c8ff",
  PROPOSAL_CREATED: "#ffdc00",
  QUARANTINED: "#ff3232",
  VERIFIED: "#00c864",
  PROMOTED: "#a000c8",
  DENIED: "#ff5050",
  REVOKED: "#000000",
};

const ACTOR_POSITIONS: Record<string, { x: number; y: number }> = {
  HUMAN_CONTROLLER: { x: 15, y: 50 },
  RESEARCH_AGENT: { x: 40, y: 25 },
  VERIFIER_AGENT: { x: 65, y: 25 },
  REPAIR_AGENT: { x: 40, y: 75 },
  POISON_AGENT: { x: 65, y: 75 },
};

export default function HydraLampPage() {
  const [events, setEvents] = useState<HydraEvent[]>([]);
  const [status, setStatus] = useState<Record<string, unknown>>({});
  const [cursor, setCursor] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/hydralamp/events")
      .then((r) => r.json())
      .then((data) => {
        setEvents(data.events || []);
        setStatus(data.status || {});
        if (data.error) setError(data.error);
      })
      .catch(() => setError("FETCH_FAILED"));
  }, []);

  const visible = events.slice(0, cursor + 1);
  const actorStates = useMemo(() => {
    const states: Record<string, string> = {};
    for (const ev of visible) states[ev.actor_id] = ev.msm_state_after;
    return states;
  }, [visible]);

  const latest = visible[visible.length - 1];

  return (
    <main style={{ padding: "2rem", fontFamily: "system-ui, sans-serif", maxWidth: "1000px", margin: "0 auto" }}>
      <h1>HydraLamp Prototype</h1>
      <p>
        Passwordless zero-trust multi-agent federation — visualization consumes{" "}
        <code>HYDRALAMP_EVENTS.jsonl</code> only. No fabricated events.
      </p>

      {error && (
        <p style={{ color: "#c00" }}>
          Events not loaded ({error}). Run <code>scripts/run_hydralamp_daisy_chain.py</code> first.
        </p>
      )}

      <section style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem", marginTop: "1.5rem" }}>
        <div>
          <h2>Actor Field</h2>
          <svg viewBox="0 0 100 100" style={{ width: "100%", background: "#14141e", borderRadius: "8px" }}>
            {Object.entries(ACTOR_POSITIONS).map(([actorId, pos]) => {
              const state = actorStates[actorId] || "UNKNOWN";
              const fill = STATE_COLORS[state] || "#808080";
              return (
                <g key={actorId}>
                  <circle cx={pos.x} cy={pos.y} r="6" fill={fill} stroke="#fff" strokeWidth="0.5" />
                  <text x={pos.x} y={pos.y + 10} fill="#ccc" fontSize="3" textAnchor="middle">
                    {actorId.split("_")[0]}
                  </text>
                </g>
              );
            })}
            {latest && ACTOR_POSITIONS[latest.actor_id] && (
              <circle
                cx={ACTOR_POSITIONS[latest.actor_id].x}
                cy={ACTOR_POSITIONS[latest.actor_id].y}
                r="9"
                fill="none"
                stroke="#ff0"
                strokeWidth="0.4"
              />
            )}
          </svg>
          <p style={{ fontSize: "0.85rem", color: "#666" }}>
            gray=disconnected · blue=authenticated · cyan=authorized · yellow=pending · red=quarantine ·
            green=verified · purple=canonical · black=revoked
          </p>
        </div>

        <div>
          <h2>Status Gates</h2>
          <table style={{ width: "100%", fontSize: "0.9rem" }}>
            <tbody>
              {[
                "HYDRALAMP_PROTOTYPE",
                "REAL_CRYPTO_CANARY",
                "WORLD_LEAK_TEST",
                "UNAUTHORIZED_PRIVATE_PLAINTEXT_DISCLOSURE",
                "UNAUTHORIZED_CANONICAL_WRITES",
                "SGLANG_STATE",
              ].map((key) => (
                <tr key={key}>
                  <td style={{ padding: "4px 8px 4px 0" }}>{key}</td>
                  <td style={{ padding: "4px 0", fontFamily: "monospace" }}>{String(status[key] ?? "—")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section style={{ marginTop: "1.5rem" }}>
        <label>
          Event cursor: {cursor + 1} / {Math.max(events.length, 1)}
          <input
            type="range"
            min={0}
            max={Math.max(events.length - 1, 0)}
            value={cursor}
            onChange={(e) => setCursor(Number(e.target.value))}
            style={{ width: "100%", marginTop: "0.5rem" }}
            disabled={events.length === 0}
          />
        </label>
      </section>

      {latest && (
        <section style={{ marginTop: "1.5rem", padding: "1rem", background: "#f4f4f4", borderRadius: "6px" }}>
          <h3>Event #{latest.event_index}: {latest.event_type}</h3>
          <ul style={{ fontSize: "0.9rem" }}>
            <li>Actor: {latest.actor_id} ({latest.actor_class})</li>
            <li>Region: {latest.region} · Model: {latest.runtime_model}</li>
            <li>MSM: {latest.msm_state_after}</li>
            <li>FCG root: <code>{latest.fcg_root_after.slice(0, 32)}…</code></li>
            <li>Access: {latest.access_decision.allowed ? "ALLOWED" : "DENIED"} — {latest.access_decision.reason}</li>
            <li>ΔG*/Drift: {latest.delta_g_star_drift_pointer || "—"}</li>
          </ul>
        </section>
      )}

      <section style={{ marginTop: "2rem" }}>
        <h3>Event Log (deterministic order)</h3>
        <div style={{ maxHeight: "240px", overflow: "auto", fontSize: "0.8rem", fontFamily: "monospace" }}>
          {visible.map((ev) => (
            <div key={ev.event_index} style={{ padding: "2px 0", borderBottom: "1px solid #eee" }}>
              [{ev.event_index}] {ev.event_type} · {ev.actor_id} · {ev.msm_state_after}
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
